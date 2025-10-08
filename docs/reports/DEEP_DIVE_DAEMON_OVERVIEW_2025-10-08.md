### TRUSTINT: A Deep Dive into the Trust Intelligence Daemon

**Timestamp:** ⬡ 2025-10-08

---

### 🌍 1. Why TRUSTINT Exists: The Philosophy

At its core, TRUSTINT exists to combat **institutional decay** and **data entropy**. In any long-term organization—be it a family trust, a non-profit, a corporation, or even a small community—the original intent, rules, and records of ownership can become lost, corrupted, or misinterpreted over time. This leads to disputes, mismanagement, and a loss of integrity.

TRUSTINT was created to be a **digital covenant**, a system that acts as a tireless, incorruptible steward. Its purpose is to preserve the **truth** of an organization—what it owns, who is in charge, what its rules are, and the history of every significant decision—in a way that is **verifiable, tamper-evident, and designed to outlive its creators.**

It is not just a database; it is a **Trust Intelligence Daemon (TID)**, an active agent designed to enforce consistency and maintain a perfect, unbroken chain of provenance.

---

### 🏗️ 2. How It Works: The Architectural Flow

TRUSTINT operates as a clear, deterministic pipeline. Think of it as a digital factory for organizational truth.

```
[🧑‍⚖️ The Steward: You]
     |
     | Defines the "source of truth" in plain text...
     v
[📝 CONFIGURATION: /config/*.yaml]
  - assets.yaml   (What the trust owns 🏡)
  - roles.yaml    (Who is in charge 👨‍💼)
  - trusts.yaml   (The trust itself 🏛️)
  - laws.yaml     (The rules it must follow 📜)
     |
     | The Steward initiates an action...
     v
[⚙️ THE DAEMON: `trustint` CLI]
     |
     | 1. VALIDATE (`trustint validate`)
     |    - The Lattice (TIL) checks the YAML files for errors.
     |    - Is there a trustee? Is every asset owned by a real trust?
     |    - 🛑 If invalid, the process stops here.
     |
     | 2. INGEST (`trustint ingest`)
     |    - The Substrate (TIS) takes the valid YAML...
     |    - ...and loads it into the secure database.
     |    - This becomes the new "canonical state".
     |
     | 3. RECORD PROVENANCE (`utils/provenance.py`)
     |    - An entry is written to the ledger: "Event 'ingest' occurred at <time>."
     |    - This entry is cryptographically signed with the HMAC key,
     |      linking it forever to the previous event. ⛓️
     |
     v
[🔐 THE VAULT: /vault/]
  (The tamper-evident heart of the system)
  |
  |---[🗄️ trustint.db]   (The SQLite Database: The canonical state-at-rest)
  |---[🧾 events.jsonl]  (The Provenance Ledger: An unbroken, signed history of all actions)
  |---[🔑 .hmac_key]     (The Secret Key: Signs the ledger. Auto-generated on first run.)
     |
     | The Steward needs a report...
     v
[📤 EXPORT & REPORTING (`trustint export`)]
     |
     | - The Matrices (TIM) reads from the secure database...
     | - ...and generates human-readable and machine-readable reports.
     |
     v
[📦 DISTRIBUTED ARTIFACTS: /dist/]
  - board_report.md      (📄 For board meetings)
  - trustint_export.csv  (📊 For spreadsheets)
  - trustint_export.jsonl(💻 For other systems)
  - SHA256SUMS           (✅ Checksums to prove the reports haven't been altered)
```

---

### 🌍 3. Real-World Applications

TRUSTINT is designed for any scenario where long-term, verifiable control over assets and rules is critical.

*   **Family Trusts & Estates**: Manage family assets across generations. When a new trustee takes over, there is a perfect, indisputable record of every asset, role, and decision, preventing family disputes.
*   **Non-Profit & Charity Governance**: Provide absolute transparency to donors and regulators. The daemon can prove how funds (assets) were managed and that the organization's actions complied with its founding charter (laws).
*   **Shared Asset Management**: For community land, shared infrastructure (like a water well), or cultural artifacts (taonga). TRUSTINT can manage ownership and usage rights for multiple parties in a way that is fair and transparent.
*   **Corporate Governance & Compliance**: Create a tamper-evident audit trail for regulatory compliance. The system can prove that specific compliance checks were made and that data integrity has been maintained, which is invaluable during audits.
*   **Decentralized Autonomous Organizations (DAOs)**: While not a blockchain itself, TRUSTINT provides a robust, off-chain governance and record-keeping backbone. It can manage the "source of truth" for assets and rules that a DAO's smart contracts might then act upon.

---

### ✅ 4. The 25 Tests: A Foundation of Trust

The test suite is the ultimate guarantee that the daemon works as promised. It is divided into modules, each testing a specific part of the system's integrity.

#### **`tests/test_db_contracts.py` (4 tests)**
*Focus: Is the database itself trustworthy?*
*   `test_db_journal_mode_is_wal`: 🚀 Checks for high-performance mode.
*   `test_db_foreign_keys_are_on`: 🔗 Ensures data relationships can't be broken.
*   `test_fts5_is_available`: 🔍 Confirms the search engine is ready.
*   `test_schema_version_is_present`: 🏷️ Verifies the database version for migrations.

#### **`tests/test_idempotent.py` (1 test)**
*Focus: Is the system stable and predictable?*
*   `test_ingest_is_idempotent`: 🔁 Ensures running `ingest` twice doesn't create messy duplicates.

#### **`tests/test_lattice.py` (1 test)**
*Focus: Does the rule-checker work?*
*   `test_validate_finds_orphaned_assets`: 🧐 Catches configuration mistakes, like assets without a valid owner.

#### **`tests/test_provenance.py` (9 tests)**
*Focus: Is the audit trail secure and reliable?*
*   `test_load_key_from_env`: 🔑 Can we load the secret key from an environment variable?
*   `test_load_key_from_binary_file`: 🔑 Can we load it from a raw binary file?
*   `test_load_key_from_b64_file`: 🔑 Can we load it from a text-based (Base64) file?
*   `test_key_generation`: ✨ Does the system auto-generate a key if one is missing?
*   `test_invalid_env_key_fails`: 🛡️ Does it reject a bad key from the environment?
*   `test_invalid_file_key_fails`: 🛡️ Does it reject a malformed key file?
*   `test_wrong_size_binary_key_fails`: 🛡️ Does it reject a key of the wrong size?
*   `test_keygen_outputs_b64`: 🛠️ Does the key generation tool work correctly?
*   `test_chain_verification_with_different_key_sources`: ⛓️ The "master test". Can we create a history and verify it, even if we change how we load the key?

#### **`tests/test_provenance_key_formats.py` (7 tests)**
*Focus: A deep check on the flexibility of key loading.*
*   `test_load_key_from_env_base64url`: flexibility check for base64url keys.
*   `test_load_key_from_env_hex`: flexibility check for hex keys.
*   `test_load_key_from_binary_file`: flexibility check for binary files.
*   `test_load_key_from_base64url_file`: flexibility check for base64url files.
*   `test_generate_new_key_if_none_exist`: Confirms auto-generation in a clean environment.
*   `test_key_too_short_fails`: 📏 Rejects keys that are too short to be secure.
*   `test_non_standard_key_length_warns`: ⚠️ Accepts but warns about keys that aren't the recommended length.

#### **`tests/test_rules.py` (3 tests)**
*Focus: Does the system enforce core governance rules?*
*   `test_rule_has_trustee`: 👨‍💼 Ensures a trust isn't created without a trustee.
*   `test_rule_has_settlor`: ✍️ Ensures a trust has a founder/settlor.
*   `test_rule_has_jurisdiction`: ⚖️ Ensures a trust is governed by the laws of a specific place.
