import argparse
import sqlite3
import time
from pathlib import Path

from utils.logger import get_logger

LOG = get_logger("migrate")

DB_PATH = Path("vault/trustint.db")
MIGRATIONS_DIR = Path("migrations")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con


def _init_migrations_table(con: sqlite3.Connection):
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_ts TEXT NOT NULL
        );
        """
    )
    con.commit()


def get_applied_migrations(con: sqlite3.Connection) -> set[str]:
    cursor = con.execute("SELECT version FROM schema_migrations")
    return {row["version"] for row in cursor.fetchall()}


def get_pending_migrations() -> list[Path]:
    if not MIGRATIONS_DIR.exists():
        return []
    # Get all SQL files in the migrations directory, sorted lexically
    return sorted(MIGRATIONS_DIR.glob("V*.sql"))


def apply_migration(con: sqlite3.Connection, migration_file: Path):
    version = migration_file.stem  # e.g., V001__initial_schema
    applied_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    LOG.info("Applying migration: %s", version)
    with open(migration_file, "r", encoding="utf-8") as f:
        con.executescript(f.read())

    con.execute(
        "INSERT INTO schema_migrations (version, applied_ts) VALUES (?, ?)",
        (version, applied_ts),
    )
    con.commit()
    LOG.info("DB_MIGRATION_APPLIED: Migration %s applied successfully.", version)


def main():
    parser = argparse.ArgumentParser(description="TRUSTINT Database Migration Tool")
    parser.add_argument(
        "--plan", action="store_true", help="Show migration plan without applying."
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply pending migrations."
    )
    args = parser.parse_args()

    if not args.plan and not args.apply:
        parser.print_help()
        return

    with connect() as con:
        _init_migrations_table(con)
        applied_migrations = get_applied_migrations(con)
        pending_migrations = get_pending_migrations()

        migrations_to_run = []
        for migration_file in pending_migrations:
            version = migration_file.stem
            if version not in applied_migrations:
                migrations_to_run.append(migration_file)
            else:
                LOG.info("DB_MIGRATION_SKIPPED: Migration %s already applied.", version)

        if not migrations_to_run:
            LOG.info("No pending migrations.")
            return

        LOG.info(
            "DB_MIGRATION_PLAN: Found %d pending migrations.", len(migrations_to_run)
        )
        for migration_file in migrations_to_run:
            LOG.info("  - %s", migration_file.name)

        if args.apply:
            for migration_file in migrations_to_run:
                apply_migration(con, migration_file)
            LOG.info("All pending migrations applied.")
        elif args.plan:
            LOG.info("Run with --apply to apply these migrations.")


if __name__ == "__main__":
    main()
