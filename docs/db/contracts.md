# Database Contracts for TRUSTINT

This document defines the foundational contracts governing the TRUSTINT database, ensuring data integrity, operational predictability, and auditability. Operators must adhere to these principles for stable system performance and reliable data provenance.

## 1. SQLite Journaling and Checkpointing Policy

The TRUSTINT database (`vault/trustint.db`) operates in **Write-Ahead Logging (WAL) mode** by default. This mode enhances concurrency and durability by writing changes to a separate WAL file before committing them to the main database file.

*   **Default Journal Mode:** WAL.
*   **Checkpointing Policy:** Checkpointing is performed with a `NORMAL` strategy. This process flushes the contents of the WAL file back into the main database file. Checkpointing is explicitly triggered as part of the `export` command, ensuring that all ingested and processed data is durably written to the primary database file before external reports or artifacts are generated. This guarantees that exported data reflects a fully committed state.

## 2. Database Vacuum Policy

The database employs a **maintenance-only vacuum policy**. Automatic or frequent `VACUUM` operations are not performed.

*   **Rationale:** While `VACUUM` can reclaim disk space and defragment the database, it is a blocking operation that can impact performance. For TRUSTINT's operational profile, space reclamation is managed on an as-needed basis.
*   **Operator Action:** Operators should initiate `VACUUM` manually during scheduled maintenance windows if significant disk space reclamation is required or if performance degradation due to fragmentation is observed.

## 3. FTS5 Configuration and Trade-offs

The Full-Text Search (FTS5) virtual table (`search_idx`) is configured as **contentless** and uses a specific tokenizer for efficient and precise search capabilities.

*   **Contentless FTS5:** The `search_idx` table stores only references (`scope`, `key`) and the searchable `content`, without duplicating the full row data. This minimizes storage overhead.
*   **Tokenizer Choice (Bronze Gate):** For the Bronze Gate release, the `unicode61` tokenizer with `remove_diacritics=2` is selected.
    *   **`unicode61` with `remove_diacritics=2`:** This tokenizer provides robust support for international characters and normalizes diacritics (e.g., 'é' becomes 'e'). This is crucial for precise matching of names, jurisdictions, and descriptors that may contain accented characters, ensuring that searches for "résumé" correctly match "resume". It prioritizes accuracy and standard linguistic processing.
    *   **Trade-off vs. `trigram`:** While a `trigram` tokenizer offers superior fuzzy matching and resilience to typos, it can generate more false positives and is less precise for structured data where exact or normalized matches are preferred. For the Bronze Gate's focus on deterministic and auditable data, the precision offered by `unicode61` is paramount. `trigram` may be considered for future Silver or Gold Gate releases where broader, less precise search capabilities are required.

## 4. Deterministic Row ID Discipline and Collision Assertion

TRUSTINT enforces a **deterministic ingestion discipline** to ensure idempotency. While SQLite assigns an internal `rowid` by default, the system's idempotency and collision assertion rely on **explicit `UNIQUE` constraints** defined in the `schema.sql`.

*   **Idempotency:** The ingestion process (`trustint ingest`) is designed to be idempotent. Re-running the ingestion with the same configuration data will result in the same database state, without creating duplicate records or altering existing valid data.
*   **Collision Assertion:** Collisions are asserted via `UNIQUE` constraints on natural keys within the schema. For example, the `slug` column in the `trusts` table is `UNIQUE NOT NULL`. If an ingestion attempt tries to insert a trust with an already existing slug, the database will prevent the duplicate entry, ensuring data integrity. The ingestion logic handles these assertions gracefully, typically by ignoring or replacing existing records based on these unique identifiers.

## 5. Schema Drift Control

To manage database schema evolution and prevent ad-hoc modifications, TRUSTINT adheres to a strict **schema drift control policy**.

*   **Migration Directory:** All schema changes will be managed through a dedicated `migrations/` directory. This directory will contain SQL scripts or migration tools with **monotonic filenames** (e.g., `V001__initial_schema.sql`, `V002__add_new_column.sql`) to ensure a clear, ordered, and auditable history of schema evolution.
*   **No Ad-Hoc DDL:** Direct Data Definition Language (DDL) statements (e.g., `ALTER TABLE`, `CREATE TABLE`) are strictly forbidden at runtime or outside the controlled migration process. All schema modifications must be part of a versioned migration script.
*   **Policy Enforcement:** Any deviation from this policy will be considered a critical operational violation, potentially leading to data corruption or system instability.

## 6. Operational Invariants

The following operational invariants can be verified from system logs and outputs, confirming adherence to database contracts:

*   **Validation Success:** Confirms that configuration data adheres to defined schemas and business rules before ingestion.
    *   `[YYYY-MM-DDTHH:MM:SSZ] INFO lattice: Validation passed: %d trusts, %d roles, %d assets, %d obligations`
*   **Ingestion Success:** Confirms that data has been successfully processed and committed to the database.
    *   `[YYYY-MM-DDTHH:MM:SSZ] INFO trustint: Ingestion successful.`
*   **Provenance Chain Verification Success:** Confirms the integrity of the event ledger, which records all significant database-related operations.
    *   `[YYYY-MM-DDTHH:MM:SSZ] INFO prov_tools: Chain verification successful.`

## Operator Checklist

1.  **Verify WAL Mode:** Confirm `vault/trustint.db-wal` and `vault/trustint.db-shm` files exist after database activity, indicating WAL mode is active.
2.  **Trigger Checkpointing:** Always run `trustint export` after any `trustint ingest` operation to ensure data is flushed from the WAL file to the main database.
3.  **Manual Vacuum:** Execute `sqlite3 vault/trustint.db "VACUUM;"` only during scheduled maintenance if disk space reclamation is necessary.
4.  **Schema Updates:** For any schema changes, consult the `migrations/` directory and follow the defined migration process. Never apply ad-hoc DDL.
5.  **Monitor Logs:** Regularly review system logs for "Validation passed", "Ingestion successful", and "Chain verification successful" messages to confirm operational invariants.
6.  **Verify Provenance:** Periodically run `python scripts/prov_tools.py chain-verify` to assert the integrity of the database's event ledger.
