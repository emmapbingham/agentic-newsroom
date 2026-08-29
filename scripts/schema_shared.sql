-- ============================================================================
-- Shared schema for the combined GAIN investigation database (db/gain.db)
-- ----------------------------------------------------------------------------
-- Tables here are NOT owned by any single source — they are reference
-- vocabularies and the cross-source ingestion audit log. Every ingester
-- (Senate, House, press, ...) runs this file first with CREATE ... IF NOT
-- EXISTS so it can populate/refresh its own slice without dropping shared
-- state owned by the others.
-- ============================================================================

-- Lobbying Disclosure Act controlled vocabularies (shared by Senate + House).
CREATE TABLE IF NOT EXISTS ref_filing_types (
    value TEXT PRIMARY KEY,          -- e.g. 'RR', 'Q1', 'MM'
    name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_issue_codes (
    value TEXT PRIMARY KEY,          -- 3-letter ALI code, e.g. 'BUD'
    name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_government_entities (
    id   INTEGER PRIMARY KEY,        -- stable id, e.g. 1=SENATE, 2=HOUSE
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_contribution_item_types (
    value TEXT PRIMARY KEY,
    name  TEXT NOT NULL
);

-- Cross-source provenance. `source` namespaces rows so each ingester can
-- delete + rewrite only its own entries on rebuild.
CREATE TABLE IF NOT EXISTS ingest_log (
    id          INTEGER PRIMARY KEY,
    source      TEXT,                -- 'senate' | 'house' | 'press' | 'members' | ...
    tier        TEXT,                -- lineage: 'raw' | 'reference' | 'derived'
    source_file TEXT,
    record_kind TEXT,                -- 'filings' | 'contributions' | 'constants' | ...
    n_records   INTEGER,
    ingested_at TEXT
);
