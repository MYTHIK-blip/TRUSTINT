import base64

import pytest
from click.testing import CliRunner

from scripts.prov_tools import cli as prov_cli
from utils.provenance import append_event, load_hmac_key

# A known 32-byte key, base64url-encoded (no padding)
TEST_KEY_B64 = "A" * 43
TEST_KEY_BYTES = base64.urlsafe_b64decode(TEST_KEY_B64 + "=")


@pytest.fixture
def isolated_vault(tmp_path, monkeypatch):
    """Ensure each test has a clean vault and paths are monkeypatched."""
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    key_path = vault_path / ".hmac_key"
    ledger_path = vault_path / "events.jsonl"

    monkeypatch.setattr("utils.provenance.DEFAULT_KEY_PATH", key_path)
    monkeypatch.setattr("utils.provenance.LEDGER_PATH", ledger_path)
    monkeypatch.setattr("scripts.prov_tools.LEDGER_PATH", ledger_path)

    yield vault_path


def test_load_key_from_env(monkeypatch, isolated_vault):
    """Test that the key is correctly loaded from the environment variable."""
    monkeypatch.setenv("TRUSTINT_HMAC_KEY", TEST_KEY_B64)
    key, status = load_hmac_key()
    assert key == TEST_KEY_BYTES
    assert (
        "from TRUSTINT_HMAC_KEY (env, base64url)" in status
        or "PASS: Loaded key from TRUSTINT_HMAC_KEY (env, base64url)" in status
    )


def test_load_key_from_binary_file(isolated_vault):
    """Test loading a raw binary key from a file."""
    key_file = isolated_vault / ".hmac_key"
    key_file.write_bytes(TEST_KEY_BYTES)

    key, status = load_hmac_key()
    assert key == TEST_KEY_BYTES
    assert "(binary)" in status


def test_load_key_from_b64_file(isolated_vault):
    """Test loading a base64url text key from a file."""
    key_file = isolated_vault / ".hmac_key"
    key_file.write_text(TEST_KEY_B64, encoding="utf-8")

    key, status = load_hmac_key()
    assert key == TEST_KEY_BYTES
    assert "(base64url text)" in status


def test_key_generation(isolated_vault):
    """Test that a new key is generated if none is found."""
    key, status = load_hmac_key()
    assert len(key) == 32
    assert "New 32-byte HMAC key generated" in status

    key_file = isolated_vault / ".hmac_key"
    assert key_file.exists()
    try:
        padded_key = key_file.read_text(encoding="utf-8") + "=="
        decoded = base64.urlsafe_b64decode(padded_key)
        assert len(decoded) == 32
    except Exception:
        pytest.fail("Generated key file is not valid base64url text")


def test_invalid_env_key_fails(monkeypatch, isolated_vault):
    """Test that a short env key fails gracefully."""
    monkeypatch.setenv("TRUSTINT_HMAC_KEY", "c2hvcnQ=")  # "short" in base64
    key, status = load_hmac_key()
    assert not key
    assert "too short" in status


def test_invalid_file_key_fails(isolated_vault):
    """Test that an invalid file key fails gracefully."""
    key_file = isolated_vault / ".hmac_key"
    key_file.write_text("short-key", encoding="utf-8")
    key, status = load_hmac_key()
    assert not key
    assert "Invalid" in status


def test_wrong_size_binary_key_fails(isolated_vault):
    """Test that a binary key of the wrong size fails."""
    key_file = isolated_vault / ".hmac_key"
    key_file.write_bytes(b"12345")
    key, status = load_hmac_key()
    assert not key
    assert "FAIL" in status


def test_keygen_outputs_b64():
    """Test that `prov_tools keygen` outputs a valid base64url key."""
    runner = CliRunner()
    result = runner.invoke(prov_cli, ["keygen"])
    assert result.exit_code == 0
    output = result.output.strip()
    assert len(output) == 43
    try:
        decoded = base64.urlsafe_b64decode(output + "=")
        assert len(decoded) == 32
    except Exception:
        pytest.fail(f"keygen output '{output}' is not valid base64url")


def test_chain_verification_with_different_key_sources(monkeypatch, isolated_vault):
    """
    Tests that event appending and chain verification work interchangeably
    with keys from env, binary file, and b64 text file.
    """
    # 1. Create a ledger with an ENV key
    monkeypatch.setenv("TRUSTINT_HMAC_KEY", TEST_KEY_B64)
    append_event({"event": "test1"})
    assert (isolated_vault / "events.jsonl").exists()

    # 2. Unset env and verify with a binary file key
    monkeypatch.delenv("TRUSTINT_HMAC_KEY")
    key_file = isolated_vault / ".hmac_key"
    key_file.write_bytes(TEST_KEY_BYTES)

    runner = CliRunner()
    result = runner.invoke(prov_cli, ["chain-verify"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "Chain verification successful" in result.output
    assert "(binary)" in result.output

    # 3. Append another event (will use the binary key from the file)
    append_event({"event": "test2"})

    # 4. Overwrite key file with b64 text and verify the whole chain
    key_file.write_text(TEST_KEY_B64, encoding="utf-8")
    result = runner.invoke(prov_cli, ["chain-verify"], catch_exceptions=False)
    assert result.exit_code == 0, result.output
    assert "Chain verification successful" in result.output
    assert "(base64url text)" in result.output
