# DB Contracts
**Status:** Accepted (Bronze)
**Date:** 2025-09-07

## Context
- Integrity, idempotency, reproducibility

## Decision
- WAL mode
- foreign_keys ON at init
- checkpoint NORMAL on export
- manual VACUUM
- UNIQUE keys + INSERT OR IGNORE
- FTS5 `unicode61 remove_diacritics=2`
- schema drift via versioned migrations (runner deferred)

## Consequences
- Reliable ingest
- Precise search
- No runtime DDL

## Notes
- Related to [Bronze Gate](./ADR-0001%20Bronze%20Gate.md)
