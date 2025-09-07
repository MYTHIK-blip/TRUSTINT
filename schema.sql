-- Core entities
CREATE TABLE IF NOT EXISTS jurisdictions(
  id INTEGER PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,         -- e.g., NZ, BVI
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trusts(
  id INTEGER PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  purpose TEXT,
  jurisdiction_id INTEGER REFERENCES jurisdictions(id),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS roles(
  id INTEGER PRIMARY KEY,
  trust_id INTEGER NOT NULL REFERENCES trusts(id) ON DELETE CASCADE,
  role_type TEXT NOT NULL,           -- trustee, protector, beneficiary, advisor
  party TEXT NOT NULL,               -- "Kerehama Mcleod", "PTC Ltd"
  powers TEXT,
  UNIQUE(trust_id, role_type, party)
);

CREATE TABLE IF NOT EXISTS assets(
  id INTEGER PRIMARY KEY,
  trust_id INTEGER NOT NULL REFERENCES trusts(id) ON DELETE CASCADE,
  class TEXT NOT NULL,               -- land | water | air
  descriptor TEXT NOT NULL,          -- e.g., "Lot 12 DP 34567", "Riparian rights", "Airspace above Lot 12 (0-120m AGL)"
  jurisdiction_id INTEGER REFERENCES jurisdictions(id),
  metadata TEXT,
  UNIQUE(trust_id, class, descriptor)
);

CREATE TABLE IF NOT EXISTS obligations(
  id INTEGER PRIMARY KEY,
  trust_id INTEGER NOT NULL REFERENCES trusts(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                -- filing or covenant
  kind TEXT NOT NULL,                -- compliance | covenant
  schedule TEXT,
  authority TEXT,
  details TEXT,
  UNIQUE(trust_id, name, kind)
);

-- Optional filings log
CREATE TABLE IF NOT EXISTS filings(
  id INTEGER PRIMARY KEY,
  trust_id INTEGER NOT NULL REFERENCES trusts(id) ON DELETE CASCADE,
  obligation_id INTEGER REFERENCES obligations(id) ON DELETE SET NULL,
  filing_date TEXT NOT NULL,
  status TEXT NOT NULL,              -- filed | pending | overdue
  reference TEXT,                    -- e.g., receipt number
  evidence_path TEXT                 -- path into vault/refs/
);

-- Free-text search index for quick discovery
CREATE VIRTUAL TABLE IF NOT EXISTS search_idx USING fts5(
  scope,                             -- trusts|roles|assets|obligations|filings
  key,                               -- slug, party, descriptor, name, reference
  content,                           -- textual body
  tokenize='unicode61 remove_diacritics 2'
);
