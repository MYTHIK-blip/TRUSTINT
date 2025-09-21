# Architecture Overview

TRUSTINT is a deterministic, CLI-driven system for managing trust and entity data through a configuration-as-code approach. It ingests YAML files, validates them against strict rules, and populates a local, tamper-evident SQLite database.

## Core Principles

The architecture is founded on **provenance** and **idempotency**. All significant actions are recorded in a cryptographically chained ledger, ensuring a verifiable, immutable audit trail. The system guarantees that repeated operations with the same inputs produce the identical state.

## Key Components

-   **TIS (TRUSTINT Substrate):** The data persistence layer, primarily managing the SQLite database schema and data ingestion.
-   **TIL (TRUSTINT Lattice):** The validation and business logic layer, enforcing schema validation and semantic rules.
-   **TIM (TRUSTINT Matrices):** The reporting and export layer, generating various reports and compliance artifacts.
-   **Provenance Ledger:** An append-only event ledger (`vault/events.jsonl`) that records all significant system actions with HMAC-SHA256 signed entries, ensuring an immutable audit trail.

## Operational Flow

The typical operational flow involves linting and testing, ingesting configuration data into the database, appending events to the provenance ledger, exporting reports, and verifying the integrity of the ledger and exports.

For a full 360° overview, refer to the `TRUSTINT_Full_Architecture_Overview.md` document in the project root.
