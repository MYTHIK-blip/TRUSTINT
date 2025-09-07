from core.substrate import connect, ingest_from_config, init_db


def test_ingest_idempotent(tmp_path):
    # Create isolated database path under pytest tmp
    db_path = tmp_path / "test_db_dir" / "trustint.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize schema
    init_db(db_path)

    # First ingest
    ingest_from_config(db_path)
    with connect(db_path) as con:
        counts1 = {
            table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ["trusts", "roles", "assets", "obligations"]
        }

    # Second ingest (should be idempotent)
    ingest_from_config(db_path)
    with connect(db_path) as con:
        counts2 = {
            table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ["trusts", "roles", "assets", "obligations"]
        }

    # Ensure counts unchanged → idempotency confirmed
    assert counts2 == counts1
