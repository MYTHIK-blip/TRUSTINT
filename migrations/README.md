# Database Migrations for TRUSTINT

This directory contains SQL scripts for managing the evolution of the TRUSTINT database schema. All schema changes must be applied through this migration system to ensure consistency, auditability, and prevent schema drift.

## Principles

*   **Monotonic Versioning:** Migration files are named using a monotonic versioning scheme (e.g., `V001__initial_schema.sql`, `V002__add_new_feature.sql`). The `V` prefix followed by a zero-padded number ensures lexical ordering.
*   **Single Responsibility:** Each migration file should ideally address a single, logical schema change.
*   **Idempotency (within a migration):** While the migration runner ensures a script is applied only once, individual migration scripts should be written to be idempotent where possible (e.g., using `CREATE TABLE IF NOT EXISTS`).
*   **No Ad-Hoc DDL:** Direct Data Definition Language (DDL) statements (e.g., `ALTER TABLE`, `CREATE TABLE`, `DROP TABLE`) are strictly forbidden at runtime or outside the controlled `scripts/migrate.py` process. This tool is the *only* authorized mechanism for applying schema changes. Any DDL applied outside this system will be considered an untracked change and may lead to system instability or data loss.

## Usage

Use the `scripts/migrate.py` tool to manage and apply migrations.

*   **Dry Run:** To see which migrations would be applied without actually modifying the database:
    ```bash
    python scripts/migrate.py --plan
    ```
*   **Apply Migrations:** To apply pending migrations to the database:
    ```bash
    python scripts/migrate.py --apply
    ```

## Migration File Naming Convention

`V<version_number>__<description>.sql`

*   `<version_number>`: A zero-padded, monotonically increasing integer (e.g., `001`, `002`).
*   `<description>`: A short, descriptive name for the migration, using underscores instead of spaces.

**Example:**

```
migrations/
├── README.md
├── V001__initial_schema.sql
└── V002__add_new_column_to_assets.sql
```
