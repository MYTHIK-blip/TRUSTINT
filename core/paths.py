from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path("vault/trustint.db")


def resolve_db_path(db_path: Optional[Path]) -> Path:
    """
    Resolves the database path, defaulting to DEFAULT_DB_PATH if None.
    """
    return db_path if db_path is not None else DEFAULT_DB_PATH
