# Logging & Audit
**Status:** Accepted (Bronze)
**Date:** 2025-09-07

## Context
- Need traceable, low-noise logs for Bronze

## Decision
- Structured log fields for key events (VALIDATION_OK, DB_INIT_OK, INGEST_OK, DB_INGEST_CONFLICT_IGNORED, EXPORT_OK, PROV_CHAIN_OK placeholder)

## Consequences
- Auditability improves
- Deeper taxonomy deferred to Silver

## Notes
- Supports [Inbox Model](./ADR-0002%20Inbox%20Model.md)
