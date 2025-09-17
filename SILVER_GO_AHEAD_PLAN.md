# TRUSTINT Go-Ahead Plan: Bronze to Silver

**Preamble:** This plan outlines the strategic and technical path from TRUSTINT's current state as a deterministic proof-of-concept (Bronze) to a mature, persistent, and intelligent governance service (Silver). This evolution is designed to deepen its utility for real-world trusts, reinforcing their sovereignty and operational resilience.

---

### 1. Executive Snapshot

*   **TRUSTINT Today (Bronze Gate):** TRUSTINT is a functional, command-line-driven system that proves trust data can be managed with absolute integrity. It transforms human-readable YAML configurations into a verifiable database, produces auditable reports, and records every action in a tamper-evident HMAC ledger. It is a powerful, passive archive—a perfect digital snapshot.

*   **TRUSTINT at Silver:** At Silver, TRUSTINT evolves from a passive archive into an **active guardian**. It becomes a persistent daemon that automatically watches for, verifies, and ingests new information. It introduces role-based access control (RBAC), formalizes data attestations, and begins to provide governance intelligence through compliance and cultural rubrics. It moves from being a tool you *run* to a service that *serves*.

*   **Why This Matters:** For a Māori land trust or a rūnanga, this transition is critical. It means moving from periodic, manual record-keeping to a continuous, automated system that reduces administrative burden, enforces internal policies, and provides real-time insights into the trust's health and obligations. It empowers trusts to operate with the efficiency of a modern corporation while preserving their unique identity and tikanga.

---

### 2. Real-World Applications (Current Bronze State)

Even at Bronze, TRUSTINT offers immediate, practical value to various entities:

*   **For a Standalone Māori Land Trust:**
    *   **Succession Planning:** Codifies the trust's structure, assets (including specific whenua boundaries and airspace), and trustee roles in simple, version-controlled files. This creates a permanent, understandable record for future generations, independent of any single person's knowledge.
    *   **Hui-Ready Reporting:** Generates a clean, verifiable `board_report.md` at any time, providing a single source of truth for trustee meetings and decisions.
    *   **Sovereignty Assertion:** Formally documents stewardship over Land, Water, and Air (LAW), creating a clear record of the trust's domain and its rules (e.g., privacy corridors against drones).

*   **For an Incorporation (e.g., Ahu Whenua Trust):**
    *   **Audit & Compliance:** Provides auditors with a perfect, time-stamped data export and a cryptographically secure ledger. This dramatically simplifies annual reviews and proves compliance with reporting standards.
    *   **Role Clarity:** Clearly defines the powers and limitations of different roles (governors, shareholders, advisors), ensuring operational integrity.
    *   **Deterministic Record-Keeping:** The idempotent nature of data ingestion means that financial or administrative records can be re-submitted without fear of creating duplicates or corrupting the database.

*   **For a Rūnanga or Central Iwi Body:**
    *   **Collective Governance:** Can run separate TRUSTINT instances for subsidiary trusts (e.g., for different hapū or specific whenua blocks) while using the core principles to aggregate high-level reports.
    *   **Obligation Tracking:** The `laws.yaml` file can codify obligations that apply across the entire collective, such as treaty settlement commitments or environmental policy adherence.
    *   **Resilience:** By promoting a decentralized "mesh" of strong, independent trusts, the Rūnanga fosters resilience. The failure of one system does not impact the others, preventing systemic collapse.

---

### 3. Silver Path Enhancements

To achieve Silver maturity, we will implement the following capabilities in a structured manner:

*   **Attestations & Forensic Integrity:**
    *   **Goal:** To make provenance absolute and verifiable by anyone.
    *   **Enhancements:**
        1.  **Formalize `PROVENANCE_HEAD`:** On every export, generate a signed file containing the latest ledger hash and a manifest of all exported artifact checksums. This creates a self-contained, verifiable "release."
        2.  **Implement Forensic Replay:** Create a script (`prov_tools.py replay-ledger`) that can rebuild the entire database state purely from the `events.jsonl` ledger, proving the ledger is a complete and sufficient record of history.
        3.  **SLSA-Style Badging:** The `chain-verify` tool will be enhanced to output a simple "pass/fail" attestation, similar to a SLSA level 1 badge, confirming the integrity of the ledger.

*   **RBAC and Separation of Duties:**
    *   **Goal:** To enforce who can do what within the system.
    *   **Enhancements:**
        1.  **User/Role Schema:** Introduce `users` and `permissions` tables to the database.
        2.  **Role Definitions:** Formally define roles (e.g., `secretariat`, `trustee`, `auditor`, `beneficiary`) with specific permissions (`can_ingest`, `can_read_reports`, `can_verify_ledger`).
        3.  **Middleware Enforcement:** The core `trustint` CLI will be modified to check a user's permissions before executing any action, especially state-changing ones like `ingest`. An `auditor` role, for example, would be able to run `export` and `chain-verify` but not `ingest`.

*   **Inbox/WORM Daemon:**
    *   **Goal:** To make the system "live" and automated.
    *   **Enhancements:**
        1.  **Watcher Daemon:** Implement the `trustint run --watch` command. This will be a persistent process that monitors the `inbox/` directory.
        2.  **Sidecar Verification:** When a new file (e.g., `filing.pdf`) appears, the daemon looks for its sidecar (`filing.pdf.sha256`). It verifies the hash to ensure the file is intact.
        3.  **Quarantine Flow:** If verification fails, the file is moved to the `quarantine/` directory and a `INBOX_QUARANTINE` event is logged. If it succeeds, it's passed to the ingest pipeline and moved to a `vault/` archive.

*   **Compliance & Cultural Rubrics:**
    *   **Goal:** To provide actionable governance intelligence.
    *   **Enhancements:**
        1.  **Scoring Engine:** Create a new module (`core/rubrics.py`) that reads from the database.
        2.  **Metric Calculation:** It will calculate scores (0-5) for:
            *   **CH (Compliance Health):** Based on the status of `obligations` in the (to be enhanced) `filings` table.
            *   **RH (Rūnanga Health):** Based on role distribution, meeting frequency, and decision records.
            *   **FI (Financial Integrity):** Based on asset records and financial report attestations.
        3.  **GRS (Governance Readiness Score):** A weighted average of CH, RH, and FI, included in the `board_report.md` to provide an at-a-glance health check.

*   **Asset & Resource Management:**
    *   **Goal:** To deepen the modeling of real-world assets.
    *   **Enhancements:**
        1.  **Richer Metadata:** The `assets` table schema will be expanded to include structured metadata for valuation, condition, and associated documents.
        2.  **Vault Linking:** Assets will be able to link to evidence files (e.g., titles, valuations, photos) stored securely in the `vault/` directory.

*   **Migrations & Schema Versioning:**
    *   **Goal:** To manage database evolution safely and transparently.
    *   **Enhancements:**
        1.  **Migration Tooling:** Integrate a simple, robust migration handler (e.g., a custom script or a lightweight library).
        2.  **Versioned Scripts:** All future schema changes must be made via versioned SQL scripts in the `migrations/` directory (e.g., `V002__add_asset_valuation.sql`). The system will track the current schema version in the database and apply new migrations automatically on startup.

*   **Policy Documentation:**
    *   **Goal:** To improve project governance and security posture.
    *   **Enhancements:**
        1.  `SECURITY.md`: A document outlining the process for reporting security vulnerabilities.
        2.  `CODEOWNERS`: A file defining which individuals or teams are responsible for reviewing changes to different parts of the codebase.
        3.  `CONTRIBUTING.md`: A guide for new developers on how to set up the environment, run tests, and contribute code that meets project standards.

---

### 4. Intelligence Architecture: Reinforcing Trust Sovereignty

TRUSTINT is more than a tool; it's an "intelligence architecture" designed to counter trends that weaken trust identity and autonomy.

*   **From Fragmented Trusts → Resilient Mesh:** Today, many trusts exist as fragmented paper trails, vulnerable to knowledge loss and administrative failure. By giving each trust a self-contained, sovereign TRUSTINT instance, we create a **resilient mesh**. Each trust is a strong, independent node.
*   **From Meshes → Sovereign Lattice:** At Silver, these independent nodes can begin to interact. A Rūnanga could act as a trusted auditor for its constituent trusts, verifying their ledgers without controlling their data. This creates a **sovereign lattice**—a network of collaboration built on verifiable trust, not centralized control.
*   **Counter to Incorporation Pressure:** Trusts often face pressure to incorporate to achieve administrative efficiency, sometimes at the cost of their unique tikanga. TRUSTINT offers another path. It provides the tools for modern, efficient governance *within* the trust structure, allowing trusts to scale their operations and collaborate effectively without sacrificing their identity.

---

### 5. Definition of Done (Silver Promotion)

TRUSTINT will be promoted from Bronze to Silver when all the following criteria are met and verified:

1.  [ ] **Daemon is Live:** The `trustint run --watch` command is implemented, documented, and has integration tests demonstrating the full inbox-verify-quarantine-ingest flow.
2.  [ ] **RBAC is Enforced:** A user with an "auditor" role is demonstrably blocked by CLI middleware from performing an `ingest` operation.
3.  [ ] **GRS is Calculated:** The Governance Readiness Score (GRS) is calculated and appears in the exported `board_report.md`.
4.  [ ] **Schema Migration Works:** At least one new, non-trivial schema change has been successfully applied via the `migrations/` directory mechanism.
5.  [ ] **Forensic Replay is Possible:** A script exists and successfully rebuilds the database from the event ledger.
6.  [ ] **Policy Docs Exist:** `SECURITY.md`, `CODEOWNERS`, and `CONTRIBUTING.md` are present in the repository root and contain meaningful content.

---

### 6. Future Trajectory (Gold and Beyond)

Silver establishes a mature, active foundation. The path to Gold and Diamond will build upon this with advanced intelligence features:

*   **UI/UX Command Centre (Gold):** A web-based interface for trust administrators, making the system accessible to non-technical users.
*   **Simulation Matrices (Gold):** "What-if" analysis tools to model the impact of events (e.g., a change in law, a climate event affecting land assets) on the trust's compliance and financial health.
*   **Foresight Agents (Diamond):** Autonomous agents that monitor external data sources (e.g., legislative websites, environmental data feeds) and automatically create attestations or trigger compliance workflows within the system.

---

## Sprint Progress Log

### End of Silver Sprint 1: Formalized Database Migration System

As of this iteration, TRUSTINT has matured beyond its initial Bronze state by incorporating a foundational architectural enhancement: a formal, auditable database migration system.

While retaining all its Bronze-level guarantees (determinism, idempotency, tamper-evidence), the system now includes:

1.  **Managed Schema Evolution:** All database schema changes are now managed through versioned SQL files located in the `migrations/` directory. This replaces the prior reliance on a single, static `schema.sql` file.
2.  **Auditable Migrations:** Every migration applied to the database is now recorded as a `MIGRATION_APPLY` event in the core `vault/events.jsonl` provenance ledger. This ensures that the evolution of the data's structure is as tamper-evident as the data itself.
3.  **CLI-Driven Process:** The new `trustint migrate` command provides administrators with a safe, idempotent way to apply pending schema changes.
4.  **Foundation for RBAC:** The initial migration (`V002`) has evolved the database schema to version 2, creating the `users` and `role_permissions` tables. This lays the essential groundwork for the upcoming Role-Based Access Control (RBAC) feature, which is a core goal of the Silver milestone.

In essence, TRUSTINT is now a system that not only tracks the history of its data but also the history of its own structure, significantly hardening its claim as a true provenance-first architecture.
