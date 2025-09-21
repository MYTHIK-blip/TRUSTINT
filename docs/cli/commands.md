# CLI Commands

The `trustint` command-line interface (CLI) provides various subcommands to interact with the TRUSTINT system. Below is a list of available commands and their descriptions.

## Core Commands

-   `trustint validate`: Validates all configuration files against defined schemas and business rules.
-   `trustint ingest`: Initializes the database (if not already) and ingests all valid configuration files into the system's database.
-   `trustint export [--pdf]`: Exports data from the database into various formats (JSONL, CSV, Markdown). The `--pdf` flag can be used to also export the board report as a PDF.
-   `trustint migrate [--target <version>]`: Runs database migrations. Optionally migrates to a specific version.
-   `trustint doctor`: Performs read-only health checks on the system, verifying database pragmas, FTS5 availability, and provenance chain integrity.
-   `trustint search <query> [--scope <scope>]`: Searches the database using FTS5. The `--scope` option can filter the search to specific data types (e.g., `trusts`, `roles`, `assets`, `obligations`, `filings`, or `all`).

## Daemon Commands (`trustint run`)

-   `trustint run watch <inbox_dir>`: Watches a specified inbox directory for new files, processes them according to intake policies, and moves them to either the raw vault or quarantine.

## Quarantine Management (`trustint quarantine`)

-   `trustint quarantine list`: Lists all open (unresolved) quarantine tickets.
-   `trustint quarantine show <ticket_id>`: Displays detailed information for a specific quarantine ticket.
-   `trustint quarantine resolve <ticket_id> --note <note>`: Resolves a quarantine ticket, requiring a note explaining the resolution.

## Inbox Interaction (`trustint inbox`)

-   `trustint inbox status`: Shows the current status of the inbox, including counts of accepted, rejected, and duplicate files, and details of the oldest unresolved quarantine ticket.
