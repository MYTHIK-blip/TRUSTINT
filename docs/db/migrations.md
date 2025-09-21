# Database Migrations

The TRUSTINT database schema evolves through a series of versioned migration scripts. These scripts are applied sequentially to update the database structure and ensure compatibility with the application.

## Migration Overview

-   **V001__initial_schema.sql**: Establishes the foundational database schema, including tables for `jurisdictions`, `trusts`, `roles`, `assets`, `obligations`, and `filings`. It also sets up the `search_idx` FTS5 virtual table for full-text search capabilities.

-   **V002__add_rbac_tables.sql**: Introduces tables for `users` and `role_permissions` to lay the groundwork for Role-Based Access Control (RBAC). This migration also populates initial permission sets for core roles.

-   **V003__add_inbox_and_quarantine.sql**: Adds the `inbox_log` table to record all incoming file processing events and the `quarantine_ticket` table to manage files that fail intake policies. This supports a Write-Once-Read-Many (WORM) intake and review process.

-   **V004__add_schema_version.sql**: Creates a `schema_version` table to track the current version of the database schema. This table is crucial for the migration system to determine which migrations need to be applied.

## Schema Versioning

The `schema_version` table contains a single row with an `id` of `1` and a `version` column. This `version` number is incremented with each successful migration, allowing the system to manage schema updates programmatically.

## Running Migrations

Migrations can be run using the `trustint migrate` CLI command. For example:

```bash
trustint migrate
# or to migrate to a specific version
trustint migrate --target 2
```
