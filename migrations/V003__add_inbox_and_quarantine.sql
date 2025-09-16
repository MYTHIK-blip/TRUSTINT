-- Silver Sprint-2a: Inbox/WORM + Quarantine
--
-- Create inbox_log for tracking all incoming files, their metadata,
-- and the policy decisions made. This table acts as a Write-Once-Read-Many
-- (WORM) log for intake events. The UNIQUE constraint on (sha256, decision)
-- prevents processing the same file for the same outcome multiple times,
-- supporting idempotency.
--
-- Create quarantine_ticket for managing rejected files. Each ticket
-- corresponds to a file that failed intake policies and requires manual
-- review.
BEGIN;

CREATE TABLE IF NOT EXISTS inbox_log (
    id INTEGER PRIMARY KEY,
    sha256 TEXT NOT NULL,
    src TEXT,
    size_bytes INTEGER,
    mime_type TEXT,
    file_ext TEXT,
    policy_id TEXT,
    decision TEXT NOT NULL CHECK(decision IN ('ACCEPT', 'REJECT', 'DUPLICATE')),
    ticket_id TEXT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sha256, decision)
) STRICT;

CREATE TABLE IF NOT EXISTS quarantine_ticket (
    id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT NULL,
    note TEXT NULL
) STRICT;

COMMIT;
