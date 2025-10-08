import base64
import os

import pytest

# Import the function to test
from utils.provenance import load_hmac_key


# Fixture to manage environment variables and temporary file paths for tests
@pytest.fixture(autouse=True)
def manage_env_and_files(monkeypatch, tmp_path):
    """
    This fixture automatically prepares a clean environment for each test.
    - It redirects the default HMAC key path to a temporary directory.
    - It ensures the TRUSTINT_HMAC_KEY environment variable is unset before each test.
    """
    # Create a temporary directory for the vault
    vault_path = tmp_path / "vault"
    vault_path.mkdir()

    # Mock the default key path to use the temporary directory
    monkeypatch.setattr("utils.provenance.DEFAULT_KEY_PATH", vault_path / ".hmac_key")

    # Ensure the environment variable is not set at the start of a test
    monkeypatch.delenv("TRUSTINT_HMAC_KEY", raising=False)
    yield


def test_load_key_from_env_base64url(monkeypatch):
    """
    Case A: Verifies that a valid base64url-encoded key is correctly loaded
    from the TRUSTINT_HMAC_KEY environment variable.
    """
    key_bytes = os.urandom(32)
    b64_key = base64.urlsafe_b64encode(key_bytes).decode("ascii").rstrip("=")
    monkeypatch.setenv("TRUSTINT_HMAC_KEY", b64_key)

    loaded_key, status = load_hmac_key()

    assert loaded_key == key_bytes
    assert "PASS" in status
    assert "env" in status
    assert "base64url" in status


def test_load_key_from_env_hex(monkeypatch):
    """
    Verifies that a valid hex-encoded key is correctly loaded from the
    TRUSTINT_HMAC_KEY environment variable.
    """
    key_bytes = os.urandom(32)
    hex_key = key_bytes.hex()
    monkeypatch.setenv("TRUSTINT_HMAC_KEY", hex_key)

    loaded_key, status = load_hmac_key()

    assert loaded_key == key_bytes
    assert "PASS" in status
    assert "env" in status
    assert "hex" in status


def test_load_key_from_binary_file(tmp_path):
    """
    Case B: Verifies that a raw binary key is correctly loaded from the
    `vault/.hmac_key` file.
    """
    key_path = tmp_path / "vault" / ".hmac_key"
    key_bytes = os.urandom(32)
    key_path.write_bytes(key_bytes)

    loaded_key, status = load_hmac_key()

    assert loaded_key == key_bytes
    assert "PASS" in status
    assert "vault" in status
    assert "binary" in status


def test_load_key_from_base64url_file(tmp_path):
    """
    Case C: Verifies that a base64url-encoded text key is correctly loaded
    from the `vault/.hmac_key` file.
    """
    key_path = tmp_path / "vault" / ".hmac_key"
    key_bytes = os.urandom(32)
    b64_key = base64.urlsafe_b64encode(key_bytes).decode("ascii").rstrip("=")
    key_path.write_text(b64_key)

    loaded_key, status = load_hmac_key()

    assert loaded_key == key_bytes
    assert "PASS" in status
    assert "vault" in status
    assert "base64url" in status


def test_generate_new_key_if_none_exist(tmp_path):
    """
    Verifies that a new key is generated, saved, and loaded correctly when
    no key is found in the environment or the filesystem.
    """
    key_path = tmp_path / "vault" / ".hmac_key"
    assert not key_path.exists()

    loaded_key, status = load_hmac_key()

    assert key_path.exists()
    assert len(loaded_key) == 32
    assert "PASS" in status
    assert "New" in status
    assert "generated" in status


def test_key_too_short_fails(tmp_path):
    """
    Verifies that the key loading fails if the key material is shorter
    than the required minimum length (16 bytes).
    """
    # Test failure from environment variable
    os.environ["TRUSTINT_HMAC_KEY"] = "c2hvcnRfa2V5"  # "short_key" in base64
    loaded_key, status = load_hmac_key()
    assert loaded_key == b""
    assert "FAIL" in status

    # Test failure from file
    key_path = tmp_path / "vault" / ".hmac_key"
    key_path.write_bytes(b"too_short")
    os.environ.pop("TRUSTINT_HMAC_KEY", None)  # Ensure env is not used

    loaded_key, status = load_hmac_key()

    assert loaded_key == b""
    assert "FAIL" in status


def test_non_standard_key_length_warns():
    """
    Verifies that a warning is issued if the key length is valid (>=16)
    but not the recommended 32 bytes.
    """
    key_bytes = os.urandom(24)  # Valid length, but not standard
    b64_key = base64.urlsafe_b64encode(key_bytes).decode("ascii").rstrip("=")
    os.environ["TRUSTINT_HMAC_KEY"] = b64_key

    loaded_key, status = load_hmac_key()

    assert loaded_key == key_bytes
    assert "WARN" in status
    assert "not the recommended" in status
