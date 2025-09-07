import hashlib
import hmac
import json
import os

import click

from core.matrices import export_csv, export_jsonl, export_markdown, write_checksums
from utils.logger import get_logger
from utils.provenance import DEFAULT_KEY_PATH, LEDGER_PATH, _read_key

LOG = get_logger("prov_tools")


@click.group()
def cli():
    """Provenance tools for TRUSTINT."""


@cli.command()
def keygen():
    """Generate a new HMAC key."""
    new_key = os.urandom(32)
    DEFAULT_KEY_PATH.write_bytes(new_key)
    os.chmod(DEFAULT_KEY_PATH, 0o600)
    LOG.info(f"New HMAC key generated at: {DEFAULT_KEY_PATH}")


@cli.command()
def chain_verify():
    """Verify the integrity of the event chain."""
    if not LEDGER_PATH.exists():
        LOG.warning("Ledger file not found. Nothing to verify.")
        return

    key = _read_key()
    lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
    last_mac = ""

    for i, line in enumerate(lines):
        try:
            event = json.loads(line)
            mac = event.pop("mac")

            msg = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
            expected_mac = hmac.new(key, msg, hashlib.sha256).hexdigest()

            if not hmac.compare_digest(mac, expected_mac):
                LOG.error(f"Chain broken at line {i+1}: MAC mismatch.")
                raise click.Abort()

            prev_mac = event.get("prev", "")
            if prev_mac != last_mac:
                LOG.error(f"Chain broken at line {i+1}: prev MAC mismatch.")
                raise click.Abort()

            last_mac = mac
        except (json.JSONDecodeError, KeyError) as e:
            LOG.error(f"Error decoding JSON at line {i+1}: {e}")
            raise e

    LOG.info("Chain verification successful.")


@cli.command()
def checksums():
    """Regenerate all checksums for exported files."""
    try:
        paths = [export_jsonl(), export_csv(), export_markdown()]
        write_checksums(paths)
        LOG.info("Checksums regenerated successfully.")
    except Exception as e:
        LOG.error(f"Checksum regeneration failed: {e}")
        raise e


if __name__ == "__main__":
    cli()
