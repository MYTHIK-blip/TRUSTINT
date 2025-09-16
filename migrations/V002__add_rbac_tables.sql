-- Silver Sprint 1: Prefigure RBAC by adding users and permissions.

-- A table to hold users who can interact with the system.
-- In the future, this will store credentials. For now, it links a user to a party.
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    party TEXT UNIQUE NOT NULL, -- Corresponds to the 'party' field in the existing 'roles' table
    created_at TEXT NOT NULL
);

-- A table to define the permissions for each role type.
-- This makes the permissions part of the auditable schema.
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY,
    role_type TEXT NOT NULL, -- e.g., 'trustee', 'auditor', 'secretariat'
    permission TEXT NOT NULL, -- e.g., 'can_read_reports', 'can_ingest_data'
    UNIQUE(role_type, permission)
);

-- Example permissions for core roles.
INSERT OR IGNORE INTO role_permissions (role_type, permission) VALUES
    ('trustee', 'can_read_reports'),
    ('protector', 'can_read_reports'),
    ('auditor', 'can_read_reports'),
    ('auditor', 'can_verify_ledger');
