
# TRUSTINT Operations Runbook

This document provides instructions for common operational tasks.

## Inbox Watch Mode

The Inbox Watch Mode is a continuous process that monitors a specified directory for new files, validates them against intake policies, and moves them to the appropriate location (raw vault or quarantine).

**Starting the Watcher:**

To start the watcher, use the `run --watch` command, specifying the path to the inbox directory.

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the watcher on the 'inbox/' directory
trustint run --watch inbox/
```

The watcher will log its activities to the console and record provenance events in `vault/events.jsonl`.

## Quarantine Workflow

Files that fail the intake policy are moved to a quarantine area for manual review. Each quarantined file is associated with a ticket.

**1. List Open Tickets:**

To see all unresolved quarantine tickets:

```bash
trustint quarantine list
```

**2. Show Ticket Details:**

To view the details of a specific ticket, use its ID:

```bash
trustint quarantine show <ticket_id>
```

**3. Resolve a Ticket:**

After reviewing a quarantined file, you can resolve its ticket. This marks the ticket as resolved and records the action.

```bash
trustint quarantine resolve <ticket_id> --note "User verified the file is safe and has been manually processed."
```

This action emits a `QUARANTINE_RESOLVE` event, ensuring the entire lifecycle is captured in the provenance chain.
