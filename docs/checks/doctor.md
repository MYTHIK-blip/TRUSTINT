# System Health Checks (`doctor`)

The `trustint doctor` command performs a series of read-only health checks to ensure the system is configured correctly and its state is consistent. It verifies critical database settings, essential module availability, and the integrity of the provenance chain.

## Checks Performed

### 1. Database Pragmas Check

-   **Purpose:** Verifies that the SQLite database is configured with optimal settings for performance and data integrity.
-   **Details:**
    -   **Journal Mode (WAL):** Checks if `PRAGMA journal_mode` is set to `WAL` (Write-Ahead Logging), which improves concurrency and durability.
    -   **Foreign Keys (ON):** Ensures `PRAGMA foreign_keys` is enabled, enforcing referential integrity within the database.
-   **Failure Impact:** Incorrect database pragmas can lead to data corruption, performance issues, or bypassed integrity constraints.

### 2. FTS5 Availability Check

-   **Purpose:** Confirms that the FTS5 (Full-Text Search) module is available and functional within the SQLite environment.
-   **Details:** Attempts to create and drop a temporary FTS5 virtual table.
-   **Failure Impact:** The `trustint search` command will not function correctly without FTS5.

### 3. Provenance Chain Verification

-   **Purpose:** Validates the cryptographic integrity of the provenance ledger (`vault/events.jsonl`).
-   **Details:** Executes `scripts/prov_tools.py chain-verify` to re-calculate and compare HMAC-SHA256 signatures for each event in the ledger, ensuring no tampering has occurred. It also attempts a fallback verification using `vault/.hmac_key` if the environment variable key fails.
-   **Failure Impact:** A broken provenance chain indicates potential data tampering or configuration issues with the HMAC key, compromising the audit trail.

## Sample Output

```
Performing system health checks...
Initial provenance check failed with ENV key. Retrying with vault/.hmac_key...

--- Health Check Summary ---
DB Journal Mode (WAL)         : PASS
DB Foreign Keys (ON)          : PASS
FTS5 Available                : PASS
Provenance Chain Verify       : PASS (used VAULT key; ENV key mismatched)
----------------------------

All health checks passed successfully.
```

*Note: The sample output above shows a scenario where the `TRUSTINT_HMAC_KEY` environment variable did not match the key used to sign the provenance chain, but a successful fallback to the key stored in `vault/.hmac_key` allowed the check to pass.*
