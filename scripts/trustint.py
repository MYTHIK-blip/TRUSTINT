import shutil
import sqlite3
import sys
import time
import uuid
from pathlib import Path

import click
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.lattice import validate_all
from core.matrices import export_csv, export_jsonl, export_markdown, write_checksums
from core.substrate import connect, ingest_from_config, init_db
from utils.logger import get_logger
from utils.provenance import append_event, sha256_file

LOG = get_logger("trustint")

DEFAULT_DB_PATH = Path("vault/trustint.db")
POLICY_PATH = Path("config/intake.yaml")
RAW_VAULT_PATH = Path("vault/raw")
QUARANTINE_PATH = Path("vault/quarantine")


class InboxHandler(FileSystemEventHandler):
    def __init__(
        self, db_path: Path, policy: dict, raw_vault_path: Path, quarantine_path: Path
    ):
        self.db_path = db_path
        self.policy = policy
        self.raw_vault_path = raw_vault_path
        self.quarantine_path = quarantine_path
        self.raw_vault_path.mkdir(exist_ok=True)
        self.quarantine_path.mkdir(exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return
        self._process_file(Path(event.src_path))

    def _process_file(self, path: Path):
        if not path.exists():
            return
        LOG.info(f"INBOX_DETECT: New file detected: {path}")
        append_event({"event": "INBOX_DETECT", "src": str(path)})

        try:
            file_hash = sha256_file(path)
            append_event(
                {"event": "INBOX_CHECKSUM", "src": str(path), "sha256": file_hash}
            )

            with connect(self.db_path) as con:
                res = con.execute(
                    "SELECT 1 FROM inbox_log WHERE sha256 = ?", (file_hash,)
                ).fetchone()
                if res:
                    LOG.warning(
                        f"INBOX_DUPLICATE: File {path} with hash {file_hash} is a duplicate."
                    )
                    append_event(
                        {
                            "event": "INBOX_DUPLICATE",
                            "src": str(path),
                            "sha256": file_hash,
                        }
                    )
                    con.execute(
                        """
                        INSERT INTO inbox_log (sha256, src, size_bytes, file_ext, policy_id, decision)
                        VALUES (?, ?, ?, ?, ?, 'DUPLICATE')
                        """,
                        (
                            file_hash,
                            str(path),
                            path.stat().st_size,
                            path.suffix.lower(),
                            "v1.0",
                        ),
                    )
                    return

            size_bytes = path.stat().st_size
            file_ext = path.suffix.lower()

            if file_ext not in self.policy["rules"]["allowed_extensions"]:
                self._reject_file(path, file_hash, "E001", "Disallowed file extension")
                return

            if size_bytes > self.policy["rules"]["max_size_bytes"]:
                self._reject_file(path, file_hash, "E002", "File size exceeds limit")
                return

            self._accept_file(path, file_hash)

        except Exception as e:
            LOG.error(f"Failed to process file {path}: {e}")
            self._reject_file(path, "unknown", "E004", f"Processing error: {e}")

    def _accept_file(self, path: Path, file_hash: str):
        LOG.info(f"INBOX_ACCEPT: File {path} accepted.")
        append_event({"event": "INBOX_ACCEPT", "src": str(path), "sha256": file_hash})

        size_bytes = path.stat().st_size
        target_path = self.raw_vault_path / f"{file_hash}{path.suffix.lower()}"
        shutil.move(str(path), str(target_path))
        LOG.info(f"INBOX_MOVE_RAW: Moved {path} to {target_path}")
        append_event(
            {
                "event": "INBOX_MOVE_RAW",
                "src": str(path),
                "dest": str(target_path),
                "sha256": file_hash,
            }
        )

        with connect(self.db_path) as con:
            con.execute(
                """
                INSERT INTO inbox_log (sha256, src, size_bytes, file_ext, policy_id, decision)
                VALUES (?, ?, ?, ?, ?, 'ACCEPT')
                """,
                (
                    file_hash,
                    str(path),
                    size_bytes,
                    path.suffix.lower(),
                    "v1.0",
                ),
            )

    def _reject_file(
        self, path: Path, file_hash: str, reason_code: str, reason_text: str
    ):
        ticket_id = f"T{uuid.uuid4().hex[:8].upper()}"
        LOG.warning(
            f"INBOX_REJECT: File {path} rejected. Reason: {reason_text}. Ticket: {ticket_id}"
        )
        append_event(
            {
                "event": "INBOX_REJECT",
                "src": str(path),
                "sha256": file_hash,
                "reason_code": reason_code,
                "ticket_id": ticket_id,
            }
        )

        size_bytes = path.stat().st_size
        quarantine_dir = self.quarantine_path / ticket_id
        quarantine_dir.mkdir(exist_ok=True)
        shutil.move(str(path), quarantine_dir / path.name)
        LOG.info(f"INBOX_MOVE_QUAR: Moved {path} to {quarantine_dir}")
        append_event(
            {
                "event": "INBOX_MOVE_QUAR",
                "src": str(path),
                "dest": str(quarantine_dir),
                "sha256": file_hash,
                "ticket_id": ticket_id,
            }
        )

        with connect(self.db_path) as con:
            con.execute(
                """
                INSERT INTO quarantine_ticket (id, reason, sha256)
                VALUES (?, ?, ?)
                """,
                (ticket_id, f"{reason_code}: {reason_text}", file_hash),
            )
            con.execute(
                """
                INSERT INTO inbox_log (sha256, src, size_bytes, file_ext, policy_id, decision, ticket_id)
                VALUES (?, ?, ?, ?, ?, 'REJECT', ?)
                """,
                (
                    file_hash,
                    str(path),
                    size_bytes,
                    path.suffix.lower(),
                    "v1.0",
                    ticket_id,
                ),
            )


@click.group()
@click.option(
    "--db",
    "db_path",
    default=DEFAULT_DB_PATH,
    type=click.Path(path_type=Path),
    help="Path to the database file.",
)
@click.option(
    "--policy",
    "policy_path",
    default=POLICY_PATH,
    type=click.Path(path_type=Path),
    help="Path to the intake policy file.",
)
@click.pass_context
def cli(ctx, db_path, policy_path):
    """TRUSTINT Trust Intelligence Daemon"""
    ctx.obj = {"DB_PATH": db_path, "POLICY_PATH": policy_path}


@cli.command()
def validate():
    """Validate all configuration files."""
    try:
        validate_all()
        LOG.info("Validation successful.")
    except Exception as e:
        LOG.error(f"Validation failed: {e}")
        raise e


@cli.command()
@click.pass_context
def ingest(ctx):
    """Initialize the database and ingest all configuration files."""
    try:
        db_path = ctx.obj["DB_PATH"]
        init_db(db_path)
        ingest_from_config(db_path)
        LOG.info("Ingestion successful.")
    except Exception as e:
        LOG.error(f"Ingestion failed: {e}")
        raise e


@cli.command()
@click.option("--pdf", is_flag=True, help="Export board report as PDF.")
@click.pass_context
def export(ctx, pdf):
    """Export data to all formats."""
    try:
        db_path = ctx.obj["DB_PATH"]
        paths = [export_jsonl(), export_csv(), export_markdown()]
        if pdf:
            from core.matrices import export_pdf

            paths.append(export_pdf())
        write_checksums(paths)
        LOG.info("Export successful.")

        with connect(db_path) as con:
            result = con.execute("PRAGMA wal_checkpoint(NORMAL);").fetchone()
            LOG.info(
                "DB_CHECKPOINT_NORMAL: WAL checkpoint performed. Result: %s", result
            )

    except Exception as e:
        LOG.error(f"Export failed: {e}")
        raise e


@cli.group()
def run():
    """Run daemon processes."""


@run.command()
@click.argument(
    "inbox_dir",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, writable=True
    ),
)
@click.pass_context
def watch(ctx, inbox_dir):
    """Watch the inbox directory for new files and process them."""
    db_path = ctx.obj["DB_PATH"]
    policy_path = ctx.obj["POLICY_PATH"]
    if not policy_path.exists():
        LOG.error(f"Policy file not found at: {policy_path}")
        return

    with open(policy_path, "r") as f:
        policy = yaml.safe_load(f)

    LOG.info(f"Starting inbox watcher on: {inbox_dir}")
    handler = InboxHandler(db_path, policy, RAW_VAULT_PATH, QUARANTINE_PATH)

    for item in Path(inbox_dir).iterdir():
        if item.is_file():
            handler._process_file(item)

    observer = Observer()
    observer.schedule(handler, inbox_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.group()
def quarantine():
    """Manage quarantined files."""


@quarantine.command("list")
@click.pass_context
def list_tickets(ctx):
    """List all open quarantine tickets."""
    with connect(ctx.obj["DB_PATH"]) as con:
        res = con.execute(
            "SELECT id, reason, created_at FROM quarantine_ticket WHERE resolved_at IS NULL ORDER BY created_at ASC"
        ).fetchall()
        if not res:
            click.echo("No open quarantine tickets.")
            return
        for row in res:
            click.echo(
                f"Ticket ID: {row[0]}\n  Reason: {row[1]}\n  Created: {row[2]}\n"
            )


@quarantine.command("show")
@click.argument("ticket_id")
@click.pass_context
def show_ticket(ctx, ticket_id):
    """Show details for a specific quarantine ticket."""
    with connect(ctx.obj["DB_PATH"]) as con:
        res = con.execute(
            "SELECT * FROM quarantine_ticket WHERE id = ?", (ticket_id,)
        ).fetchone()
        if not res:
            click.echo(f"Ticket {ticket_id} not found.")
            return

        res_inbox = con.execute(
            "SELECT * FROM inbox_log WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()

        click.echo(f"Ticket Details ({ticket_id}):")
        click.echo(f"  Reason:     {res['reason']}")
        click.echo(f"  SHA256:     {res['sha256']}")
        click.echo(f"  Created:    {res['created_at']}")
        click.echo(f"  Resolved:   {res['resolved_at'] or 'N/A'}")
        click.echo(f"  Note:       {res['note'] or 'N/A'}")
        if res_inbox:
            click.echo("\n  Original File Info:")
            click.echo(f"    Source:      {res_inbox['src']}")
            click.echo(f"    Size (bytes):{res_inbox['size_bytes']}")
            click.echo(f"    MIME Type:   {res_inbox['mime_type']}")
            click.echo(f"    Extension:   {res_inbox['file_ext']}")


@quarantine.command("resolve")
@click.argument("ticket_id")
@click.option("--note", required=True, help="A note explaining the resolution.")
@click.pass_context
def resolve_ticket(ctx, ticket_id, note):
    """Resolve a quarantine ticket."""
    with connect(ctx.obj["DB_PATH"]) as con:
        res = con.execute(
            "SELECT id FROM quarantine_ticket WHERE id = ? AND resolved_at IS NULL",
            (ticket_id,),
        ).fetchone()
        if not res:
            click.echo(f"Open ticket {ticket_id} not found.")
            return

        resolved_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        con.execute(
            "UPDATE quarantine_ticket SET resolved_at = ?, note = ? WHERE id = ?",
            (resolved_at, note, ticket_id),
        )

        event = {
            "event": "QUARANTINE_RESOLVE",
            "ticket_id": ticket_id,
            "resolved_at": resolved_at,
            "note": note,
        }
        append_event(event)
        click.echo(f"Ticket {ticket_id} resolved.")


@cli.group()
def inbox():
    """Interact with the inbox."""


@inbox.command("status")
@click.pass_context
def inbox_status(ctx):
    """Show the status of the inbox."""
    with connect(ctx.obj["DB_PATH"]) as con:
        counts = con.execute(
            """
            SELECT
                decision,
                COUNT(*)
            FROM inbox_log
            GROUP BY decision
        """
        ).fetchall()

        oldest_ticket = con.execute(
            """
            SELECT id, created_at
            FROM quarantine_ticket
            WHERE resolved_at IS NULL
            ORDER BY created_at ASC
            LIMIT 1
        """
        ).fetchone()

        click.echo("Inbox Status:")
        for decision, count in counts:
            click.echo(f"  {decision:<10}: {count}")

        if oldest_ticket:
            click.echo("\nOldest Unresolved Ticket:")
            click.echo(f"  ID: {oldest_ticket['id']}")
            click.echo(f"  Created: {oldest_ticket['created_at']}")


@cli.command()
@click.option(
    "--scope",
    default="all",
    type=click.Choice(["trusts", "roles", "assets", "obligations", "filings", "all"]),
    help="Scope of the search.",
)
@click.argument("query")
@click.pass_context
def search(ctx, scope, query):
    """Search the database using FTS5."""
    from core.substrate import search_fts

    try:
        results = search_fts(ctx.obj["DB_PATH"], query, scope)
        if not results:
            LOG.info("No results found.")
            return

        w_scope = max(len(r["scope"]) for r in results)
        w_key = max(len(r["key"]) for r in results)

        click.echo(f"{'SCOPE':<{w_scope}} {'KEY':<{w_key}} {'CONTENT'}")
        click.echo(f"{'='*w_scope} {'='*w_key} {'='*40}")

        for r in results:
            content = r["content"].replace("\n", " ").strip()
            if len(content) > 70:
                content = content[:67] + "..."
            click.echo(f"{r['scope']:<{w_scope}} {r['key']:<{w_key}} {content}")

    except Exception as e:
        LOG.error(f"Search failed: {e}")
        raise e


@cli.command()
@click.option("--target", type=int, help="Migrate to a specific version.")
@click.pass_context
def migrate(ctx, target):
    """Run database migrations."""
    from scripts.migrate import run_migrations

    try:
        run_migrations(ctx.obj["DB_PATH"], target_version=target)
    except Exception as e:
        LOG.error(f"Migration failed: {e}")
        raise e


@cli.command()
@click.pass_context
def doctor(ctx):
    """Perform read-only health checks on the system."""
    db_path = ctx.obj["DB_PATH"]
    results = {}
    overall_success = True

    click.echo("Performing system health checks...")

    # 1. DB Pragmas Check
    try:
        with connect(db_path) as con:
            # WAL mode check
            cursor = con.execute("PRAGMA journal_mode;")
            journal_mode = cursor.fetchone()[0].upper()
            wal_success = journal_mode == "WAL"
            results["DB Journal Mode (WAL)"] = (
                "PASS" if wal_success else f"FAIL (Current: {journal_mode})"
            )
            if not wal_success:
                overall_success = False

            # Foreign Keys check
            cursor = con.execute("PRAGMA foreign_keys;")
            foreign_keys_on = cursor.fetchone()[0] == 1
            fk_success = foreign_keys_on
            results["DB Foreign Keys (ON)"] = (
                "PASS" if fk_success else "FAIL (Current: OFF)"
            )
            if not fk_success:
                overall_success = False
    except Exception as e:
        results["DB Pragmas Check"] = f"ERROR ({e})"
        overall_success = False

    # 2. FTS5 Availability Check
    try:
        with connect(db_path) as con:
            con.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS _test_fts USING fts5(content);"
            )
            con.execute("DROP TABLE IF EXISTS _test_fts;")
        results["FTS5 Available"] = "PASS"
    except sqlite3.OperationalError as e:
        if "no such module: fts5" in str(e):
            results["FTS5 Available"] = "FAIL (FTS5 module not found)"
        else:
            results["FTS5 Available"] = f"ERROR ({e})"
        overall_success = False
    except Exception as e:
        results["FTS5 Available"] = f"ERROR ({e})"
        overall_success = False

    # 3. Provenance Verification
    import hashlib
    import hmac
    import json

    from utils.provenance import LEDGER_PATH, load_hmac_key

    try:
        key, status = load_hmac_key()
        status_detail = status.replace("PASS: ", "").replace("FAIL: ", "")

        if not key:
            results["Provenance HMAC Key"] = f"FAIL ({status_detail})"
            results["Provenance Chain Verify"] = "SKIP (no key)"
            overall_success = False
        else:
            results["Provenance HMAC Key"] = f"PASS ({status_detail})"
            if not LEDGER_PATH.exists():
                results["Provenance Chain Verify"] = "PASS (Ledger file not found)"
            else:
                lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
                last_mac = ""
                chain_ok = True
                error_msg = ""
                for i, line in enumerate(lines):
                    try:
                        event = json.loads(line)
                        mac = event.pop("mac")
                        msg = json.dumps(
                            event, sort_keys=True, separators=(",", ":")
                        ).encode()
                        expected_mac = hmac.new(key, msg, hashlib.sha256).hexdigest()

                        if not hmac.compare_digest(mac, expected_mac):
                            error_msg = f"MAC mismatch at line {i+1}"
                            chain_ok = False
                            break

                        prev_mac = event.get("prev", "")
                        if prev_mac != last_mac:
                            error_msg = f"prev MAC mismatch at line {i+1}"
                            chain_ok = False
                            break

                        last_mac = mac
                    except (json.JSONDecodeError, KeyError) as e:
                        error_msg = f"JSON error at line {i+1}: {e}"
                        chain_ok = False
                        break

                if chain_ok:
                    results["Provenance Chain Verify"] = "PASS"
                else:
                    results["Provenance Chain Verify"] = f"FAIL: {error_msg}"
                    overall_success = False

    except Exception as e:
        results["Provenance HMAC Key"] = f"ERROR ({e})"
        results["Provenance Chain Verify"] = "ERROR (check failed)"
        overall_success = False

    click.echo("\n--- Health Check Summary ---")
    for check, status in results.items():
        click.echo(f"{check:<30}: {status}")
    click.echo("----------------------------")

    if overall_success:
        click.echo("\nAll health checks passed successfully.")
        sys.exit(0)
    else:
        click.echo("\nOne or more health checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    cli()
