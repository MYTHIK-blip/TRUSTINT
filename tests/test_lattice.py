from core.lattice import validate_all
from core.substrate import ingest_from_config, init_db


def test_pipeline_roundtrip(tmp_path):
    # Create isolated database path under pytest tmp
    db_path = tmp_path / "test_db_dir" / "trustint.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate config and initialize schema
    validate_all()
    init_db(db_path)

    # Ingest data into the temporary DB
    counts = ingest_from_config(db_path)
    assert counts["trusts"] >= 1

    # Sanity: run a simple query to confirm rows are there and readable
    from core.substrate import connect

    with connect(db_path) as con:
        got = con.execute("SELECT COUNT(*) FROM trusts").fetchone()[0]
    assert got >= 1
