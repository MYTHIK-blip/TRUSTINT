# scripts/migrate.py

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import List

from utils.logger import get_logger
from utils.provenance import append_event, sha256_file

LOG = get_logger("migrate")
MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations"

# Canonical migration filename pattern: V###__name.sql
_MIGRATION_RE = re.compile(r"^V(\d+)__([A-Za-z0-9_]+)\.sql$")


def _parse_version_from_name(fname: str) -> int:
    """Return the integer version from a canonical migration filename.

    Raises:
        ValueError: if the filename does not match the canonical pattern.
    """
    m = _MIGRATION_RE.match(fname)
    if m is None:
        raise ValueError(
            f"Invalid migration filename (expected 'V###__name.sql'): {fname!r}"
        )
    return int(m.group(1))


def _discover_migrations() -> List[Path]:
    """Return a sorted list of valid migration files by version."""
    if not MIGRATIONS_DIR.is_dir():
        return []
    candidates = list(MIGRATIONS_DIR.glob("V*.sql"))
    # Keep only files that match the canonical pattern
    valid = [p for p in candidates if _MIGRATION_RE.match(p.name) is not None]
    # Sort by parsed version
    valid.sort(key=lambda p: _parse_version_from_name(p.name))
    return valid


def get_db_version(con: sqlite3.Connection) -> int:
    """Get the current schema version from the database."""
    try:
        cur = con.execute("SELECT version FROM schema_version")
        row = cur.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        # schema_version table doesn't exist yet
        return 0


def set_db_version(con: sqlite3.Connection, version: int) -> None:
    """Set the schema version in the database."""
    con.execute("UPDATE schema_version SET version = ?", (version,))


def run_migrations(db_path: Path, target_version: int | None = None) -> None:
    """Scan migrations directory and apply pending migrations."""
    LOG.info("Starting database migration process...")

    migration_files = _discover_migrations()
    if not migration_files:
        LOG.warning("No migration files found at %s. Nothing to do.", MIGRATIONS_DIR)
        return

    with sqlite3.connect(db_path) as con:
        current_version = get_db_version(con)
        LOG.info("Current DB version: %d", current_version)

        # Determine effective target version
        if target_version is None:
            # Default to the latest version found among valid files
            effective_target = _parse_version_from_name(migration_files[-1].name)
        else:
            effective_target = target_version

        LOG.info("Target DB version: %d", effective_target)

        if current_version >= effective_target:
            LOG.info(
                "Database is already at or beyond the target version. No migration needed."
            )
            return

        applied_count = 0
        for migration_file in migration_files:
            version = _parse_version_from_name(migration_file.name)
            if current_version < version <= effective_target:
                LOG.info("Applying migration %s...", migration_file.name)

                # Execute the migration script
                sql_script = migration_file.read_text(encoding="utf-8")
                con.executescript(sql_script)

                # Update the schema version
                set_db_version(con, version)

                # Log provenance
                event = {
                    "type": "MIGRATION_APPLY",
                    "version": version,
                    "script": migration_file.name,
                    "sha256": sha256_file(migration_file),
                }
                append_event(event)

                LOG.info(
                    "Successfully applied version %d and logged provenance event.",
                    version,
                )
                current_version = version
                applied_count += 1

        con.commit()

    if applied_count > 0:
        LOG.info("Migration process complete. Applied %d migration(s).", applied_count)
    else:
        LOG.info("No new migrations to apply.")
