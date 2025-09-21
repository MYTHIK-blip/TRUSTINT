# Inbox and Quarantine Lifecycle

The TRUSTINT system includes an inbox processing mechanism to handle incoming files, validate them against defined policies, and either accept them into the raw vault or move them to a quarantine area for manual review.

## Inbox Processing (`trustint run watch`)

The `trustint run watch <inbox_dir>` command starts a daemon that monitors a specified directory (`inbox_dir`) for new files. When a new file is detected, the system performs the following steps:

1.  **Detection & Logging:** The file's arrival is logged, and a SHA256 hash is computed.
2.  **Duplicate Check:** The system checks if a file with the same hash and decision (ACCEPT/REJECT) has been processed before. Duplicates are logged and ignored.
3.  **Policy Validation:** The file is validated against the intake policy defined in `config/intake.yaml`. This policy typically includes checks for:
    -   Allowed file extensions.
    -   Maximum file size.
4.  **Decision:**
    -   **Accept:** If the file passes all policy checks, it is moved to the `vault/raw` directory (the raw vault). An `INBOX_ACCEPT` event is logged.
    -   **Reject:** If the file fails any policy check, it is moved to a unique subdirectory within `vault/quarantine`. A `quarantine_ticket` is created in the database, and an `INBOX_REJECT` event is logged.

All actions and decisions are recorded in the `inbox_log` database table, providing a Write-Once-Read-Many (WORM) audit trail for all intake events.

## Quarantine Management (`trustint quarantine`)

Files that are rejected by the inbox policy are moved to the quarantine area and associated with a `quarantine_ticket`. These tickets require manual intervention.

-   **`trustint quarantine list`**: Displays all currently open (unresolved) quarantine tickets.
-   **`trustint quarantine show <ticket_id>`**: Provides detailed information about a specific quarantined file and the reason for its rejection.
-   **`trustint quarantine resolve <ticket_id> --note "Reason for resolution"`**: Allows an operator to mark a ticket as resolved, requiring a note to explain the action taken. This action is also recorded in the provenance ledger.

## Inbox Status (`trustint inbox status`)

The `trustint inbox status` command provides an overview of the inbox's activity, including counts of accepted, rejected, and duplicate files, and highlights the oldest unresolved quarantine ticket, if any.

## Policy Configuration

The intake policy is configured in `config/intake.yaml`. Operators can modify this file to adjust allowed file types, size limits, and other intake rules.
