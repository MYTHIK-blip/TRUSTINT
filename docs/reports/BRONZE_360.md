# Bronze 360° Snapshot

**Date:** 2025-09-06 15:10:31 UTC

## 1) Repo State

### Git Status
```
## No commits yet on main
?? .github/
?? .gitignore
?? .pre-commit-config.yaml
?? .ruff.toml
?? ADDENDUM.md
?? LICENSE
?? LICENSE-DOCS
?? Makefile
?? README.md
?? config/
?? core/
?? docs/
?? inbox/
?? migrations/
?? mypy.ini
?? pyproject.toml
?? requirements.txt
Schema is governed by versioned files under migrations/ (see migrations/README.md).
?? scripts/
?? tests/
?? trustint.egg-info/
?? utils/
```

### Python Version
```
Python 3.12.3
```

## 2) Lint/Type/Test Results

### Ruff Check
```
(No issues found)
```

### MyPy
```
Success: no issues found in 20 source files
```

### Pytest
```
9 passed in 0.76s
```

## 3) DB Health (default DB)

### DB Status
```
DB_READY True JOURNAL wal COUNTS {'jurisdictions': 2, 'trusts': 1, 'roles': 2, 'assets': 3, 'obligations': 2} CHK <sqlite3.Row object at 0x724d43a42770>
```

### DB Files
```
-rw-r--r-- 1 mythik mythik 77824 Sep  7 03:09 vault/trustint.db
-rw-rw-r-- 1 mythik mythik    48 Sep  6 18:03 vault/trustint.db.bak
-rw-rw-r-- 1 mythik mythik    48 Sep  6 18:03 vault/trustint.db.corrupt
```

## 4) ADR Inventory (Bronze scope)

### ADR Files and Sizes
- docs/adr/ADR-0001 Bronze Gate.md (387 bytes)
- docs/adr/ADR-0002 Inbox Model.md (371 bytes)
- docs/adr/ADR-0003 DB Contracts.md (484 bytes)
- docs/adr/ADR-0004 Logging & Audit.md (427 bytes)
- docs/adr/ADR-0005 Provenance Head.md (454 bytes)

### ADR Titles
- Bronze Gate
- Inbox Model
- DB Contracts
- Logging & Audit
- Provenance Head

## 5) Notable Bronze Corrections

- Repo-root anchoring of schema/config paths
- Explicit `db_path` in substrate APIs; no global DB_PATH/monkeypatch
- WAL + foreign_keys on init; NORMAL checkpoint on export
- FTS5 `unicode61 remove_diacritics 2`
- Idempotent ingest (UNIQUE + INSERT OR IGNORE)
- Tests use tmp_path + explicit db_path; removed freezegun; migrations parked (Silver)
