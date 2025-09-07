import time
from pathlib import Path

import click
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from core.lattice import validate_all
from core.matrices import export_csv, export_jsonl, export_markdown, write_checksums
from core.substrate import connect, ingest_from_config, init_db
from utils.logger import get_logger

LOG = get_logger("trustint")

DEFAULT_DB_PATH = Path("vault/trustint.db")


@click.group()
def cli():
    """TRUSTINT Trust Intelligence Daemon"""


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
def ingest():
    """Initialize the database and ingest all configuration files."""
    try:
        init_db(DEFAULT_DB_PATH)
        ingest_from_config(DEFAULT_DB_PATH)
        LOG.info("Ingestion successful.")
    except Exception as e:
        LOG.error(f"Ingestion failed: {e}")
        raise e


@cli.command()
@click.option("--pdf", is_flag=True, help="Export board report as PDF.")
def export(pdf):
    """Export data to all formats."""
    try:
        paths = [export_jsonl(), export_csv(), export_markdown()]
        if pdf:
            from core.matrices import export_pdf

            paths.append(export_pdf())
        write_checksums(paths)
        LOG.info("Export successful.")

        # Perform WAL checkpoint
        with connect(DEFAULT_DB_PATH) as con:
            # (log_size, checkpointed_size) = con.execute("PRAGMA wal_checkpoint(NORMAL);").fetchone()
            # SQLite 3.11.0+ returns (log_size, checkpointed_size, frames_checkpointed, frames_wal)
            # We'll just log the result of the pragma call.
            result = con.execute("PRAGMA wal_checkpoint(NORMAL);").fetchone()
            LOG.info(
                "DB_CHECKPOINT_NORMAL: WAL checkpoint performed. Result: %s", result
            )

    except Exception as e:
        LOG.error(f"Export failed: {e}")
        raise e


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, commands, debounce_seconds=2):
        self.commands = commands
        self.debounce_seconds = debounce_seconds
        self.last_triggered = 0

    def on_any_event(self, event):
        if event.is_directory:
            return
        if time.time() - self.last_triggered > self.debounce_seconds:
            self.last_triggered = time.time()
            LOG.info(
                f"Detected change: {event.src_path}. Triggering commands: {self.commands}"
            )
            try:
                if "validate" in self.commands:
                    validate.callback()
                if "ingest" in self.commands:
                    ingest.callback()
                if "export" in self.commands:
                    export.callback()
                LOG.info("Commands executed successfully.")
            except Exception as e:
                LOG.error(f"Command execution failed: {e}")
                raise e


@cli.command()
@click.option(
    "--watch",
    "watch_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory to watch for changes.",
)
@click.option(
    "--on-change",
    "commands",
    required=True,
    help="Comma-separated list of commands to run on change (e.g., 'validate,ingest,export').",
)
def run(watch_dir, commands):
    """Run the TRUSTINT daemon in watch mode."""
    command_list = [c.strip() for c in commands.split(",")]
    event_handler = ChangeHandler(command_list)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.start()
    LOG.info(f"Watching directory: {watch_dir} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


@cli.command()
@click.option(
    "--scope",
    default="all",
    type=click.Choice(["trusts", "roles", "assets", "obligations", "filings", "all"]),
    help="Scope of the search.",
)
@click.argument("query")
def search(scope: str, query: str):
    """Search the database using FTS5."""
    from core.substrate import search_fts

    try:
        results = search_fts(DEFAULT_DB_PATH, query, scope)
        if not results:
            LOG.info("No results found.")
            return

        # Simple table output
        # Determine column widths
        w_scope = max(len(r["scope"]) for r in results)
        w_key = max(len(r["key"]) for r in results)

        # Header
        click.echo(f"{'SCOPE':<{w_scope}} {'KEY':<{w_key}} {'CONTENT'}")
        click.echo(f"{ '='*w_scope} {'='*w_key} {'='*40}")

        # Rows
        for r in results:
            content = r["content"].replace("\n", " ").strip()
            if len(content) > 70:
                content = content[:67] + "..."
            click.echo(f"{r['scope']:<{w_scope}} {r['key']:<{w_key}} {content}")

    except Exception as e:
        LOG.error(f"Search failed: {e}")
        raise e


if __name__ == "__main__":
    cli()
