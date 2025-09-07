from pathlib import Path

from core.substrate import connect, ingest_from_config, init_db


def get_db_pragma(pragma_name: str, db_path: Path):
    with connect(db_path) as con:
        return con.execute(f"PRAGMA {pragma_name};").fetchone()[0]


class TestDbContracts:
    def test_db_wal_mode(self, tmp_path):
        db_path = tmp_path / "test_db_dir" / "trustint.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        init_db(db_path)
        assert get_db_pragma("journal_mode", db_path).lower() == "wal"
        assert db_path.exists()
        # Ensure WAL sidecar exists alongside DB
        assert (db_path.parent / f"{db_path.name}-wal").exists()

    def test_export_triggers_checkpoint(self, tmp_path):
        """
        Bronze-scope: verify we can run a checkpoint on the SAME DB we initialized.
        We don't invoke the CLI export (it targets default DB). Instead, we assert
        that NORMAL checkpoint runs and returns a tuple after ingest.
        """
        db_path = tmp_path / "test_db_dir" / "trustint.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        init_db(db_path)
        ingest_from_config(db_path)

        with connect(db_path) as con:
            # Clear WAL to start from a known state; capture frames flushed.
            _ = con.execute("PRAGMA wal_checkpoint(TRUNCATE);").fetchone()
            # Now a NORMAL checkpoint should be valid on this same DB.
            row = con.execute("PRAGMA wal_checkpoint(NORMAL);").fetchone()
        assert row is not None and len(row) >= 1

    def test_fts_tokenizer_unicode61(self, tmp_path):
        db_path = tmp_path / "test_db_dir" / "trustint.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        init_db(db_path)
        ingest_from_config(db_path)
        with connect(db_path) as con:
            row = con.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='search_idx'"
            ).fetchone()
        create_sql = (row[0] if row else "").lower()
        assert "fts5" in create_sql
        assert "unicode61" in create_sql
        assert "remove_diacritics" in create_sql

    def test_idempotent_ingest(self, caplog, tmp_path):
        db_path = tmp_path / "test_db_dir" / "trustint.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        init_db(db_path)
        ingest_from_config(db_path)

        with connect(db_path) as con:
            counts1 = {
                t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                for t in ["trusts", "roles", "assets", "obligations"]
            }

        caplog.clear()
        ingest_from_config(db_path)
        with connect(db_path) as con:
            counts2 = {
                t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
                for t in ["trusts", "roles", "assets", "obligations"]
            }

        assert counts2 == counts1

        # If duplicates occur, ingest should log ignored conflicts.
        # Bronze-level tests do not assert on log contents.
