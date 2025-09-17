
# TRUSTINT System Health Checks (`doctor`)

The `doctor` command runs a series of checks to ensure the system is configured correctly and that its state is consistent.

## 1. Inbox Checks

### C001: Inbox Directory Permissions

- **Check:** Verifies that the specified inbox directory exists and that the application has read and write permissions.
- **Rationale:** The watcher needs to be able to read new files and move them after processing. Without these permissions, it cannot function.
- **Remediation:**
  - Ensure the directory path is correct.
  - Use `chmod` to grant the necessary permissions to the user running the `trustint` process.

## 2. Migration Coherence

### C002: Migration Hash Check

- **Check:** Compares the SHA256 hash of each applied migration script (e.g., `V001__initial_schema.sql`) with the hash recorded in the database's `schema_migrations` table.
- **Rationale:** Detects if a migration script was altered after it was applied, which could lead to a critical state inconsistency between the code and the database schema.
- **Remediation:**
  - **NEVER** modify a migration script after it has been run.
  - If a change is needed, create a new migration script.
  - If an inconsistency is found, you may need to restore the database from a backup or manually align the schema.
