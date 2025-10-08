import base64
import hashlib
import hmac
import json
import os
import re
import time
from pathlib import Path
from typing import Optional, Tuple

# Constants
KEY_LEN_BYTES = 32
MIN_KEY_LEN_BYTES = 16
DEFAULT_KEY_PATH = Path("vault/.hmac_key")
LEDGER_PATH = Path("vault/events.jsonl")

# Regex for base64url detection (allowing for missing padding)
_B64URL_RE = re.compile(r"^[A-Za-z0-9\-_]+$")
_HEX_RE = re.compile(r"^[a-fA-F0-9]+$")


def load_hmac_key() -> Tuple[bytes, str]:
    """
    Loads the HMAC key from environment, file, or generates a new one.

    The key can be sourced in the following order of precedence:
    1.  `TRUSTINT_HMAC_KEY` env var (base64url or hex-encoded).
    2.  `TRUSTINT_HMAC_KEY_FILE` env var pointing to a file.
    3.  `vault/.hmac_key` file (binary, base64url, or hex).
    4.  Auto-generation of a new key if none of the above are found.

    Returns:
        A tuple containing:
        - The key as bytes.
        - A status string describing how the key was loaded.
    """
    env_key = os.getenv("TRUSTINT_HMAC_KEY")
    if env_key:
        key_str = env_key.strip()
        try:
            # Try decoding as hex first
            if len(key_str) == KEY_LEN_BYTES * 2 and _HEX_RE.match(key_str):
                key = bytes.fromhex(key_str)
                return key, "PASS: Loaded 32-byte key from TRUSTINT_HMAC_KEY (env, hex)"
            # Fallback to base64url
            key = base64.urlsafe_b64decode(key_str + "=" * (-len(key_str) % 4))
            if len(key) < MIN_KEY_LEN_BYTES:
                return (
                    b"",
                    f"FAIL: Key from TRUSTINT_HMAC_KEY is too short ({len(key)} bytes)",
                )
            if len(key) != KEY_LEN_BYTES:
                return (
                    key,
                    f"WARN: Key from TRUSTINT_HMAC_KEY is {len(key)} bytes, not the recommended 32",
                )
            return key, "PASS: Loaded key from TRUSTINT_HMAC_KEY (env, base64url)"
        except (ValueError, TypeError):
            return (
                b"",
                "FAIL: Invalid format for TRUSTINT_HMAC_KEY (expected base64url or hex)",
            )

    key_path = Path(os.getenv("TRUSTINT_HMAC_KEY_FILE") or DEFAULT_KEY_PATH)

    if key_path.exists():
        try:
            content = key_path.read_text("utf-8").strip()
            if _B64URL_RE.match(content):
                key = base64.urlsafe_b64decode(content + "=" * (-len(content) % 4))
                source = f"{key_path} (base64url text)"
            elif _HEX_RE.match(content):
                key = bytes.fromhex(content)
                source = f"{key_path} (hex text)"
            else:  # Fallback to binary read
                key = key_path.read_bytes()
                source = f"{key_path} (binary)"

            if len(key) < MIN_KEY_LEN_BYTES:
                return b"", f"FAIL: Key from {source} is too short ({len(key)} bytes)"
            if len(key) != KEY_LEN_BYTES:
                return (
                    key,
                    f"WARN: Key from {source} is {len(key)} bytes, not the recommended 32",
                )
            return key, f"PASS: Loaded {len(key)}-byte key from {source}"
        except UnicodeDecodeError:  # It's a binary file
            key = key_path.read_bytes()
            source = f"{key_path} (binary)"
            if len(key) < MIN_KEY_LEN_BYTES:
                return b"", f"FAIL: Key from {source} is too short ({len(key)} bytes)"
            if len(key) != KEY_LEN_BYTES:
                return (
                    key,
                    f"WARN: Key from {source} is {len(key)} bytes, not the recommended 32",
                )
            return key, f"PASS: Loaded {len(key)}-byte key from {source}"
        except Exception as e:
            return b"", f"FAIL: Could not load key from {key_path}: {e}"

    # If no key is found, generate, save, and return a new one
    key_path.parent.mkdir(parents=True, exist_ok=True)
    new_key = os.urandom(KEY_LEN_BYTES)
    # Save as base64url text for readability
    b64_key = base64.urlsafe_b64encode(new_key).decode("ascii").rstrip("=")
    key_path.write_text(b64_key, encoding="utf-8")
    return new_key, f"PASS: New 32-byte HMAC key generated and saved to {key_path}"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def append_event(event: dict, key: Optional[bytes] = None) -> dict:
    """
    Append an event to the append-only ledger with an HMAC chain.
    Returns the enriched event (with ts, prev, mac).
    """
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    if key is None:
        key, _ = load_hmac_key()  # Discard status message

    prev_mac = ""
    if LEDGER_PATH.exists():
        try:
            with LEDGER_PATH.open("r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        prev_mac = json.loads(last_line).get("mac", "")
        except (IOError, json.JSONDecodeError):
            # Handle case where file is empty or corrupt
            pass

    enriched = {
        **event,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prev": prev_mac,
    }
    msg = json.dumps(enriched, sort_keys=True, separators=(",", ":")).encode("utf-8")
    mac = hmac.new(key, msg, hashlib.sha256).hexdigest()
    enriched["mac"] = mac

    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(enriched, ensure_ascii=False) + "\n")
    return enriched


def get_provenance_tail() -> list[str]:
    """Returns the last 5 lines of the provenance ledger."""
    if not LEDGER_PATH.exists():
        return []
    return LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()[-5:]
