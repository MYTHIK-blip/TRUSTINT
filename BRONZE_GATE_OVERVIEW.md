# TRUSTINT Architecture: Bronze Gate 360° Overview

This document provides a concise overview of the TRUSTINT system as it exists in its current "Bronze Gate" implementation.

## 1. Executive Snapshot

TRUSTINT (Bronze) is a deterministic, command-line-driven system designed for the high-integrity management of trust and entity data. It transforms human-readable configuration files (YAML) into a structured, auditable database. Its primary function is to provide trustees, administrators, and auditors with a verifiable, point-in-time snapshot of a trust's structure and obligations, backed by a cryptographically secure ledger of all system activities. It is a tool for creating truth, not for real-time management.

## 2. Core Architecture

The system is composed of four primary layers that work in concert:

-   **TIS (TRUSTINT Substrate):** The data persistence layer, implemented in `core/substrate.py`. It manages the SQLite database (`vault/trustint.db`), which operates in Write-Ahead Logging (WAL) mode for durability. All data ingestion is idempotent, using `INSERT OR IGNORE` logic to prevent data duplication.

-   **TIL (TRUSTINT Lattice):** The validation layer, implemented in `core/lattice.py`. Before any data is ingested, the Lattice validates the source YAML files against both a formal JSON Schema and a set of semantic business rules (e.g., "every trust must have a trustee"). This prevents corrupt or invalid data from entering the system.

-   **TIM (TRUSTINT Matrices):** The reporting and export layer, implemented in `core/matrices.py`. The Matrices layer reads directly from the database to generate verifiable reports in multiple formats (CSV, JSONL, and Markdown). These exports are the primary output of the system for human consumption.

-   **Provenance & Covenant Layer:**
    -   **Provenance:** Implemented in `utils/provenance.py`, this is the system's auditable heart. It maintains an append-only ledger (`vault/events.jsonl`) where every significant action (ingest, export) is recorded as an event. Each event is cryptographically chained to the last using an HMAC-SHA256 signature, making the ledger tamper-evident.
    -   **Covenants:** The system models obligations (both legal `compliance` and internal `covenant`) in its schema (`schema.sql`) and configuration (`config/laws.yaml`), allowing a trust to formally track its duties.

## 3. Data Flow

The operational flow is manual and driven by explicit commands from the `scripts/` directory:

1.  **Ingest:** An operator defines the trust's structure, roles, and assets in YAML files within the `config/` directory. They run `python scripts/trustint.py ingest`.
2.  **Ledger (Append):** The Substrate (TIS) ingests the data into the SQLite database. Simultaneously, the Provenance layer appends an `ingest` event to the `events.jsonl` ledger, cryptographically signing a record of the transaction.
3.  **Export:** The operator runs `python scripts/trustint.py export`. The Matrices (TIM) layer queries the database and generates report files in the `dist/` directory.
4.  **Provenance Proof:** As part of the export, two final proofs are created:
    -   An `export` event is written to the ledger.
    -   A `SHA256SUMS` manifest file is created, containing checksums of all generated reports. This manifest, combined with the ledger, provides auditors with a complete, verifiable "provenance pack".

## 4. Non-Functional Guarantees

The Bronze Gate architecture makes the following guarantees:

-   **Determinism:** Given the same set of input YAML files, the system will always produce the exact same database state and exported reports.
-   **Idempotency:** Running the `ingest` command multiple times with the same data will not create duplicate records or alter the system state.
-   **Tamper-Evidence:** Any modification to the `events.jsonl` ledger will break the HMAC signature chain. This can be verified at any time by running `python scripts/prov_tools.py chain-verify`.
-   **Recovery Policy:** In case of database corruption, the file is renamed to `.corrupt` and never deleted. The entire database state can be deterministically rebuilt by re-running ingestion from the source YAML files.

## 5. Real-World Applications (Bronze Gate)

A trust can use the Bronze implementation today to:

-   **Establish a Single Source of Truth:** Codify the trust's complete structure—including entities, roles, assets, and legal jurisdiction—in version-controllable YAML files.
-   **Generate Verifiable Board Reports:** Create point-in-time reports (`dist/board_report.md`) that are guaranteed to reflect the state of the underlying data, suitable for board meetings and official records.
-   **Satisfy Audit Requirements:** Provide auditors with a time-capsule of trust data, complete with a manifest of file checksums and an immutable, cryptographically-signed ledger of every action taken by the system.
-   **Track Key Obligations:** Formally list and categorize all compliance and covenant obligations tied to the trust, providing a clear reference for trustees and administrators.
