import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Optional

DEFAULT_KEY_PATH = Path("vault/.hmac_key")
LEDGER_PATH = Path("vault/events.jsonl")


def _read_key() -> bytes:
    env_key = os.environ.get("TRUSTINT_HMAC_KEY")
    if env_key:
        return env_key.encode("utf-8")

    DEFAULT_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DEFAULT_KEY_PATH.exists():
        # deterministic but local—user should rotate/replace securely later
        DEFAULT_KEY_PATH.write_bytes(os.urandom(32))
        os.chmod(DEFAULT_KEY_PATH, 0o600)
    return DEFAULT_KEY_PATH.read_bytes()


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
    key = key or _read_key()

    prev_mac = ""
    if LEDGER_PATH.exists():
        *_, last = LEDGER_PATH.read_text(encoding="utf-8").splitlines() or [""]
        if last:
            prev_mac = json.loads(last).get("mac", "")

    enriched = {
        **event,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "prev": prev_mac,
    }
    msg = json.dumps(enriched, sort_keys=True, separators=(",", ":")).encode()
    mac = hmac.new(key, msg, hashlib.sha256).hexdigest()
    enriched["mac"] = mac

    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(enriched, ensure_ascii=False) + "\n")
    return enriched
