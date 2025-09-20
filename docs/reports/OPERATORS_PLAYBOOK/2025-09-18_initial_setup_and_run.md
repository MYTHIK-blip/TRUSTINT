# Operator's Playbook: Initial Setup & Full System Run

- **Date:** 2025-09-18
- **Operator:** Gemini Agent
- **Status:** Success

## 1. Introduction

This document serves as a log and operational guide for the TRUSTINT system. It details the steps taken during the initial setup and a full run of all system components on the date specified. It is intended for both human operators and automated agents to understand the system's state and operational procedures.

**A reminder to all operators:** All manual and automated changes, interventions, and significant operational events **must be logged**. This system's integrity relies on complete and auditable provenance. Where autonomous logging is not available, manual entries are mandatory.

## 2. Session Log: Initial Setup & Run (2025-09-18)

### 2.1. Objective

The goal of this session was to perform a comprehensive check of the TRUSTINT system by:
1.  Reading all documentation (`README.md` files).
2.  Installing all dependencies.
3.  Running all tests, scripts, and pipelines.
4.  Creating a distributable package.
5.  Starting the system's background agent.

### 2.2. Execution Log & Commands

*Timestamp: 2025-09-18T11:54:00Z*

**Action:** Read all `README.md` files to understand the project.
**Result:** Success. Gained understanding of project structure, commands, and purpose.

**Action:** Install project dependencies.
**Command:**
```bash
source .venv/bin/activate && pip install -r requirements.txt
```
**Result:** Success. All dependencies were already satisfied.

**Action:** Run the test suite.
**Command:**
```bash
source .venv/bin/activate && pytest -q
```
**Result:** Success. All 9 tests passed.

**Action:** Run the data validation and ingestion pipeline.
**Command:**
```bash
source .venv/bin/activate && python scripts/run_lattice.py
```
**Result:** **Failure.**
**Issue:** The script failed with `TypeError: init_db() missing 1 required positional argument: 'db_path'`.
**Resolution:**
1.  Inspected `scripts/run_lattice.py` and `core/substrate.py`.
2.  Confirmed that `init_db()` and `ingest_from_config()` required a `db_path` argument.
3.  Modified `scripts/run_lattice.py` to define the database path and pass it to the functions.
**Status:** Issue resolved.

**Action:** Re-run the data validation and ingestion pipeline.
**Command:**
```bash
source .venv/bin/activate && python scripts/run_lattice.py
```
**Result:** Success. The pipeline ran correctly, noting that the data was already present from a previous run.

**Action:** Run the data export pipeline.
**Command:**
```bash
source .venv/bin/activate && python scripts/run_matrix.py
```
**Result:** Success. Exported `trustint_export.jsonl`, `trustint_export.csv`, and `board_report.md`.

**Action:** Install the project in editable mode for CLI access.
**Command:**
```bash
source .venv/bin/activate && pip install -e .
```
**Result:** Success.

**Action:** Verify CLI commands (`validate`, `ingest`, `export`, `search`).
**Commands:**
```bash
source .venv/bin/activate && python scripts/trustint.py validate
source .venv/bin/activate && python scripts/trustint.py ingest
source .venv/bin/activate && python scripts/trustint.py export
source .venv/bin/activate && python scripts/trustint.py search --scope assets "airspace"
```
**Result:** Success. All commands executed correctly.

**Action:** Start the background file-watching daemon.
**Command:**
```bash
source .venv/bin/activate && python scripts/trustint.py run --watch inbox/ --on-change "validate,ingest,export" &
```
**Result:** Success. The daemon started as a background process.

**Action:** Run linter checks.
**Command:**
```bash
source .venv/bin/activate && make lint
```
**Result:** Success. `ruff` and `mypy` reported no issues.

**Action:** Verify the provenance chain integrity.
**Command:**
```bash
source .venv/bin/activate && make chain-verify
```
**Result:** Success. The event ledger in `vault/events.jsonl` is intact.

**Action:** Regenerate checksums for exported files.
**Command:**
```bash
source .venv/bin/activate && make checksums
```
**Result:** Success. `dist/SHA256SUMS` was updated.

**Action:** Create a distributable package.
**Command:**
```bash
source .venv/bin/activate && make package
```
**Result:** Success. Created `dist/trustint-bronze-v0.1.tar.gz`.

### 2.3. Summary

The system is fully operational. All tests pass, pipelines run as expected, and the provenance mechanisms are functional. The initial setup and run were successful, with one minor script issue that was identified and resolved.

## 3. Operator's Quick Reference Guide

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
# Install in editable mode for CLI
pip install -e .
```

### Core Pipeline
```bash
# Run all steps via the main CLI
trustint validate
trustint ingest
trustint export

# Or use the Makefile
make ingest
make export
```

### Testing & Verification
```bash
# Run tests
make test

# Run linters
make lint

# Verify provenance chain
make chain-verify
```

### Daemon
```bash
# Watch 'inbox/' and run pipeline on changes
trustint run --watch inbox/ --on-change "validate,ingest,export" &
```

### Packaging
```bash
# Create a new distributable package
make package
```
