# 🕸 TRUSTINT — Trust Intelligence Daemon (TID)

[![Gate: 🟤 Bronze v0.1](https://img.shields.io/badge/Gate-🟤%20Bronze%20v0.1-%23cd7f32)](https://github.com/MYTHIK-blip/TRUSTINT/releases/tag/bronze-gate-v0.1)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE)
[![Docs License: CC BY-SA 4.0](https://img.shields.io/badge/Docs-CC--BY--SA%204.0-green)](LICENSE-DOCS)
[![Status: Embryo](https://img.shields.io/badge/Status-Embryo-lightgrey)]()

---

## ✍️ Author & Stewardship
- **Author:** Kerehama Mcleod (aka _MYTHIK_)
- **Role:** Architect of Trust Intelligence Systems
- **Stewardship model:** Operators are **stewards, not owners**. Provenance is mandatory.

---

## 📜 Citation
If referencing TRUSTINT in research or governance work, please cite as:

> Mcleod, Kerehama (_MYTHIK_). **TRUSTINT — Trust Intelligence Daemon (TID).**
> A covenantal system for provenance, LAW sovereignty, and collapse-aware continuity.
> AGPLv3 + CC BY-SA 4.0. GitHub, 2025.

---

## 🌐 Vision
TRUSTINT is a **Trust Intelligence Architecture** — a covenantal system that models, manages, and preserves **assets, roles, laws, and compliance** across generations.
It is not a trust itself, but a **Trust Intelligence Daemon (TID)**:

- 🏛 **Substrate (TIS)** — database + schema layer for codified trusts.
- 🕸 **Lattice (TIL)** — governance validation and rule enforcement.
- 🔢 **Matrices (TIM)** — exports, simulations, and board-ready reports.

Anchored in **NZ + Pacific jurisdictions** (extensible globally), TRUSTINT addresses:
- Land & water sovereignty under compulsory acquisition.
- Air sovereignty amid drones, surveillance, and intrusive reconnaissance.
- Continuity of civic, cultural, and digital assets under collapse scenarios.

---

## 🎯 Purpose
- Codify trust logic into **deterministic, auditable pipelines**.
- Preserve **provenance** across every artifact, deed, and decision.
- Validate roles, assets, and obligations against explicit **schemas + rule checks**.
- Provide **tamper-evident vaults** and **exportable board reports**.
- Enable **continuity under disruption** (public-domain fallback on systemic failure).

---

## 🧬 Ethos
- ✅ Integrity first — licenses + covenant before operations.
- ✅ Provenance mandatory — signed commits, checksums, append-only ledger.
- ✅ Idempotency — reproducible outputs; no silent black-boxing.
- ✅ Continuity under collapse — defaults to public-domain accessibility.
- ✅ Stewardship — multi-party, accountable governance.
- ✅ Agents bound by covenant — AI derivatives must preserve attribution + context.

---

## 🌍 Sovereignty Layers (LAW)
TRUSTINT encodes **Land · Water · Air** domains:

- **Land** — estates, whenua, tangible infrastructures.
- **Water** — freshwater, coastal zones, rights of use & stewardship.
- **Air** — privacy corridors, airspace easements, drone boundaries (0–120m AGL).

Future (Silver → Gold → Diamond): simulation matrices, drone telemetry ingestion, jurisdictional overlays.

---

## 📂 Repository Structure
    TRUSTINT/
    ├── config/           # trusts.yaml, roles.yaml, assets.yaml, laws.yaml
    ├── core/             # substrate.py (DB ingest), lattice.py (validation), matrices.py (exports)
    ├── scripts/          # run_lattice.py, run_matrix.py
    ├── utils/            # logger.py, provenance.py
    ├── vault/            # tamper-evident storage (db, events, artifacts)
    ├── docs/             # ontology, playbook, governance
    ├── tests/            # pytest modules
    ├── dist/             # packaged exports + checksums
    ├── LICENSE           # AGPLv3
    ├── ADDENDUM.md       # provenance & collapse covenant
    ├── LICENSE-DOCS      # CC-BY-SA 4.0
    ├── requirements.txt  # pinned dependencies
    # Schema is now governed by versioned files under migrations/ (see migrations/README.md).
    └── README.md

---

## ⚙️ Quickstart (Bronze MVP, deterministic — no LLMs)
    # 0) Create/activate venv and install deps
    pip install -r requirements.txt

    # 1) Validate + Ingest (YAML → SQLite + FTS + ledger)
    python scripts/run_lattice.py

    # 2) Export (JSONL/CSV/Markdown) + checksums
    python scripts/run_matrix.py

    # 3) Tests (roundtrip sanity)
    pytest -q

    # 4) Package (Bronze artifact + rollback integrity)
    cd dist
    tar -czf trustint-bronze-v0.1.tar.gz *.md *.csv *.jsonl SHA256SUMS
    sha256sum trustint-bronze-v0.1.tar.gz > trustint-bronze-v0.1.sha256

---

##  CLI Entrypoint
As an alternative to the individual `run_*.py` scripts, you can use the main `trustint.py` entrypoint:

    # Validate, ingest, and export
    python scripts/trustint.py validate
    python scripts/trustint.py ingest
    python scripts/trustint.py export

    # Search for assets containing "airspace"
    python scripts/trustint.py search --scope assets "airspace"

---

## 🛠 Pipeline Details

### Validate + Ingest
- JSONSchema validation for: `trusts.yaml`, `roles.yaml`, `assets.yaml`, `laws.yaml`.
- Rule checks:
  - Each trust must have **≥1 trustee**.
  - **Air** assets must specify `jurisdiction` and bounded descriptor (e.g., “0–120m AGL”).
- DB initialization is now governed by versioned files under `migrations/` (see `migrations/README.md`). The legacy `schema.sql` can be found at `docs/legacy/schema.sql` for historical reference.
- Ingest normalized entities into `vault/trustint.db`.
- Append HMAC-chained event to `vault/events.jsonl`.

### Export
- `dist/trustint_export.jsonl` — machine-friendly summary per trust.
- `dist/trustint_export.csv` — flat view (trusts, roles, assets).
- `dist/board_report.md` — board-readable report (roles, LAW assets).
- `dist/SHA256SUMS` — integrity across exports.

---

## 💻 CLI Usage

All core operations are available via the `trustint` command-line interface. Ensure you have installed the project in editable mode (`pip install -e .`) for the `trustint` command to be available in your shell.

```bash
# Validate configuration files
trustint validate

# Initialize database and ingest data from config files
trustint ingest

# Export data to various formats (JSONL, CSV, Markdown)
trustint export

# Export data to various formats, including PDF
trustint export --pdf

# Search the database using Full-Text Search (FTS5)
# Example: Search for assets containing "airspace"
trustint search --scope assets "airspace"

# Run the daemon to watch for changes in a directory and trigger pipeline commands
# Example: Watch the 'inbox/' directory and run validate, ingest, and export on changes
trustint run --watch inbox/ --on-change "validate,ingest,export"
```

---

## 🚀 Commands List

Here's a comprehensive list of all commands and their functionalities implemented in TRUSTINT:

### Core Pipeline Commands (via `trustint` CLI)
- `trustint validate`: Validates all configuration files against defined schemas and business rules.
- `trustint ingest`: Initializes the database and ingests data from `config/*.yaml` files. This process is idempotent.
- `trustint export [--pdf]`: Exports processed data into machine-readable (JSONL, CSV) and human-readable (Markdown) formats. The `--pdf` flag generates an additional PDF report.

### Utility Commands (via `trustint` CLI)
- `trustint search --scope [scope] "query"`: Performs a full-text search across the database. Supported scopes include `trusts`, `roles`, `assets`, `obligations`, `filings`, or `all`.
- `trustint run --watch [directory] --on-change [commands]`: Activates daemon mode, monitoring a specified directory for changes and automatically triggering a sequence of commands (e.g., `validate,ingest,export`).
- `trustint doctor`: Performs read-only health checks on the database (WAL mode, foreign keys, FTS5 availability) and provenance chain integrity.

### Provenance Tools (via `scripts/prov_tools.py`)
- `python scripts/prov_tools.py keygen`: Generates a new HMAC key for securing the provenance ledger.
- `python scripts/prov_tools.py chain-verify`: Verifies the integrity of the `vault/events.jsonl` append-only ledger, ensuring no tampering has occurred.
- `python scripts/prov_tools.py checksums`: Regenerates SHA256 checksums for all exported artifacts in the `dist/` directory, ensuring data integrity.

### Development & Build Commands (via `Makefile`)
- `make setup`: Installs all project dependencies and sets up the editable installation.
- `make lint`: Runs code quality checks using Ruff and Mypy.
- `make test`: Executes all unit and integration tests using Pytest.
- `make ingest`: Runs the `trustint ingest` command.
- `make export`: Runs the `trustint export` command.
- `make package`: Creates a distributable tarball of the project exports with checksums.

### Original Runner Scripts (for backward compatibility)
- `python scripts/run_lattice.py`: Executes validation and ingestion (equivalent to `trustint validate` and `trustint ingest`).
- `python scripts/run_matrix.py`: Executes data export (equivalent to `trustint export`).

---

## 🧑‍⚖️ Real-World Use (Chairman’s View)
- **Clarity & Oversight** — single source of truth for instruments; cross-jurisdiction visibility.
- **Defensive Posture** — tamper-evident vault; air/water clauses; legislative hooks (Silver via TenderBot).
- **Operational Efficiency** — deterministic validation; board exports; reproducible packaging.
- **Strategic Leverage** — covenantal enforcement; multi-party stewardship; collapse continuity.

---

## 🧩 Config Schema (Bronze)
**trusts.yaml**
    - slug: <kebab-case-id>
      name: <string>
      purpose: <string>
      jurisdiction: <ISO-like code, e.g., NZ>

**roles.yaml**
    - trust: <trust.slug>
      role: trustee | protector | beneficiary | advisor
      party: <string>
      powers: { signing_threshold?: int, veto?: [strings...] }

**assets.yaml**
    - trust: <trust.slug>
      class: land | water | air
      descriptor: <human-readable bounds/identity>
      jurisdiction: <code>
      metadata: { titles?: [..], coordinates?: [lat,lon], ... }

**laws.yaml**
    jurisdictions:
      - { code: NZ, name: New Zealand }
      - { code: BVI, name: British Virgin Islands }
    obligations:
      - trust: <trust.slug>
        name: <e.g., IRD Annual Return>
        kind: compliance | covenant
        schedule: annual | on change-of-law | ...
        authority: <regulator/org>
        details: { statute?: <...>, link?: <...>, notes?: <...> }

---

## 🔐 Provenance & Integrity
- **Ledger:** `vault/events.jsonl` — append-only HMAC chain (prev → mac).
- **Checksums:** `dist/SHA256SUMS` — SHA256 for exported artifacts.
- **Vault:** content-addressed paths for evidence and references.
- **Keys:** local seed at `vault/.hmac_key` (rotate for production; prefer GPG/HSM).

---

## 🧪 Tooling & Policy
- **Pre-commit:** Black, Ruff (auto-fix), Mypy, YAML checks.
- **Testing:** Pytest with golden-file snapshots encouraged.
- **Style:** Python 3.12, Ruff line-length 100, strict-lean types. (All Ruff errors are now addressed directly in code, no ignores needed).

---

## 🧭 Troubleshooting
- `ModuleNotFoundError: core`
  - Ensure `tests/conftest.py` adds repo root to `sys.path` **or** run with `PYTHONPATH=. ...`.
  - Add `__init__.py` to `utils/`, `scripts/`, `tests/`.

- Exports missing or empty
  - Verify `config/*.yaml` exist and pass validation.
  - Run `python scripts/run_lattice.py` before `run_matrix.py`.

- Checksum mismatch
  - Re-generate `dist/SHA256SUMS` after modifying any exports.

---

## 🪜 Bronze → Silver → Gold → Diamond
- **Bronze (current):** Working daemon — ingest, validate, export, provenance; LAW seeded (land, water, air).
- **Silver:** Multi-trust lattice, jurisdiction overlays, TenderBotNZ integration (legislation scraping), richer obligations.
- **Gold:** Simulation matrices (PvP/PvE/systemic shocks), multi-lattice governance, incident evidence vault flows.
- **Diamond:** Adaptive AI-driven compliance/resilience matrices; autonomous provenance vaulting; cross-chain attestations.

---

## 🗺 Roadmap (Mermaid source)
    %% paste into a mermaid renderer if desired
    graph TD
      A[Bronze Gate] --> B[Silver Gate]
      B --> C[Gold Gate]
      C --> D[Diamond Gate]

      A:::bronze
      B:::silver
      C:::gold
      D:::diamond

    classDef bronze fill:#cd7f32,stroke:#333,stroke-width:2px,color:#fff
    classDef silver fill:#c0c0c0,stroke:#333,stroke-width:2px,color:#000
    classDef gold fill:#ffd700,stroke:#333,stroke-width:2px,color:#000
    classDef diamond fill:#b9f2ff,stroke:#333,stroke-width:2px,color:#000

---

## 📂 Artifact Provenance (Release Ritual)
- Tag gate: `bronze-gate-v0.1`
- Build tarball in `dist/` with exports + `SHA256SUMS`
- Emit `.sha256` and (optional) `.sha512`
- Signed tag/commit if GPG available
- Freeze `bronze` branch as rollback line

---

## 📜 Licenses & Covenant
- **Code → AGPLv3** (`LICENSE`) — ensures openness; prevents SaaS enclosure.
- **Docs → CC BY-SA 4.0** (`LICENSE-DOCS`) — ontology + cultural artifacts remain libre with attribution.
- **Covenant → `ADDENDUM.md`** — provenance, collapse continuity, exportability, AI obligations.

---

## ⚔️ Synthesis
TRUSTINT at Bronze is a **living covenant + working daemon**:
- Deterministic pipeline (no LLMs).
- Legally shielded (AGPL, CC, covenant).
- Provenance enforced (ledger + checksums).
- Real-world applicable (board reports, compliance exports, LAW sovereignty).
- Positioned for Silver without code churn: add multi-trust, jurisdiction overlays, and scraping integration.

### Current Status: All Systems Go
Comprehensive checks confirm the robust functionality of all components:
- **Core Pipeline:** `make setup`, `lint`, `test`, `ingest`, `export`, and `package` targets all execute successfully.
- **CLI:** The `trustint` command and its subcommands (`validate`, `ingest`, `export`, `search`, `run`) are fully operational.
- **Daemon Mode:** The `trustint run` command effectively monitors directories and triggers the pipeline on changes, with proper debouncing.
- **Database:** The `vault/trustint.db` is correctly populated, queried, and maintained, with idempotency verified.
- **Provenance:** The `vault/events.jsonl` ledger's integrity is verifiable via `prov_tools.py chain-verify`, demonstrating tamper detection.
- **Backward Compatibility:** Original runner scripts (`scripts/run_lattice.py`, `scripts/run_matrix.py`) still function as expected.
- **Utility Tools:** `prov_tools.py keygen` and `checksums` commands perform their intended operations.

## 🗓 Release Notes

### `v0.2.0-silver.1` - Pipeline Overview & Roadmap (2025-09-20T12-38-13Z)

A comprehensive pipeline overview and enhancement roadmap has been generated, detailing the current system architecture, resolved issues (schema version idempotency), remaining gaps, and a strategic plan for future development. This report is available at `docs/reports/PIPELINE_OVERVIEW_2025-09-20T12-38-13Z.md`.
