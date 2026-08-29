-- ============================================================================
-- House LDA tables for the combined GAIN database (db/gain.db)
-- ----------------------------------------------------------------------------
-- Owns the `house_*` namespace only. Idempotent: drops + recreates just the
-- House tables, leaving shared ref_*/ingest_log and senate_*/press_* untouched.
-- Run scripts/schema_shared.sql first.
--
-- The House Clerk's LD-1 (registration) and LD-2 (quarterly) filings — the same
-- disclosure regime as the Senate data, filed separately with a different XML
-- shape. Kept in their OWN tables (not merged into senate_*) on purpose:
-- schemas differ, the same engagement is often filed in BOTH chambers, and
-- House-vs-Senate discrepancies for one engagement are themselves reportable.
--
-- Bridge to the Senate data (verified, scripts/discover_house_schema.py):
--   senateID = "{senate_registrant_id}-{client_suffix}"; the prefix matches
--   senate_registrants.id in 99.95% of sampled filings. Stored parsed as
--   `senate_registrant_id` for a clean join. houseID's first 5-6 digits match
--   senate_registrants.house_registrant_id ~62% of the time (secondary link).
--
-- Notable differences from the Senate data:
--   * House lobbyists have NO stable id — name + coveredPosition only (fuzzy to
--     the Senate lobbyist dimension). Stored inline, not as a keyed dimension.
--   * `federal_agencies` (the entity lobbied) is FREE TEXT, not a controlled
--     vocabulary like the Senate government_entities.
--   * Issue codes are the same 3-letter ALI codes -> shared ref_issue_codes.
--   * The filename is the unique House filing id (numeric, globally distinct).
--   * LD-1: filing-level lobbyists, bare ali_Code list, foreign/affiliated orgs.
--     LD-2: lobbyists nested per ali_info, no foreign/affiliated orgs, has
--     income/expenses. Lobbyists are normalized to the filing level uniformly.
-- ============================================================================

DROP TABLE IF EXISTS house_activities_fts;
DROP TABLE IF EXISTS house_convictions;
DROP TABLE IF EXISTS house_affiliated_orgs;
DROP TABLE IF EXISTS house_foreign_entities;
DROP TABLE IF EXISTS house_filing_lobbyists;
DROP TABLE IF EXISTS house_activities;
DROP TABLE IF EXISTS house_filings;

CREATE TABLE house_filings (
    house_filing_id      TEXT PRIMARY KEY,      -- numeric filing id (= filename)
    doc_type             TEXT,                  -- 'LD1' (registration) | 'LD2' (quarterly)
    filing_year          INTEGER,               -- from source directory
    filing_period        TEXT,                  -- 'Q1'..'Q4' | 'REG' (from directory)
    report_year          INTEGER,               -- in-file reportYear (LD2)
    report_type          TEXT,                  -- e.g. '1T'
    reg_type             TEXT,                  -- LD1 regType
    organization_name    TEXT,                  -- the registrant (lobbying firm/org)
    contact_prefix       TEXT,
    contact_first_name   TEXT,
    contact_last_name    TEXT,
    address_1            TEXT,
    address_2            TEXT,
    city                 TEXT,
    state                TEXT,
    zip                  TEXT,
    country              TEXT,
    principal_city       TEXT,
    principal_state      TEXT,
    principal_zip        TEXT,
    principal_country    TEXT,
    registrant_general_description TEXT,         -- LD1
    self_select          TEXT,
    client_name          TEXT,
    client_govt_entity   TEXT,                   -- Y/N
    client_address       TEXT,                   -- LD1
    client_city          TEXT,
    client_state         TEXT,
    client_zip           TEXT,
    client_country       TEXT,
    client_general_description TEXT,             -- LD1
    senate_id            TEXT,                   -- raw senateID
    senate_registrant_id INTEGER,               -- parsed prefix -> senate_registrants.id
    senate_client_suffix TEXT,                  -- parsed suffix
    house_id             TEXT,                   -- raw houseID
    income               TEXT,
    income_amt           REAL,
    expenses             TEXT,
    expenses_amt         REAL,
    expenses_method      TEXT,
    no_lobbying          TEXT,                   -- Y/N (LD2)
    termination_date     TEXT,
    effective_date       TEXT,                   -- LD1
    printed_name         TEXT,
    signed_date          TEXT,
    imported             TEXT,
    pages                TEXT,
    source_file          TEXT
);
CREATE INDEX idx_house_filings_senatereg ON house_filings(senate_registrant_id);
CREATE INDEX idx_house_filings_houseid   ON house_filings(house_id);
CREATE INDEX idx_house_filings_org       ON house_filings(organization_name);
CREATE INDEX idx_house_filings_client    ON house_filings(client_name);
CREATE INDEX idx_house_filings_yp        ON house_filings(filing_year, filing_period);
CREATE INDEX idx_house_filings_doctype   ON house_filings(doc_type);

CREATE TABLE house_activities (
    activity_id           INTEGER PRIMARY KEY,
    house_filing_id       TEXT NOT NULL REFERENCES house_filings(house_filing_id),
    seq                   INTEGER,
    issue_area_code       TEXT REFERENCES ref_issue_codes(value),
    description           TEXT,                  -- LD2 specific_issues/description
    federal_agencies      TEXT,                  -- LD2 free-text entities lobbied
    foreign_entity_issues TEXT
);
CREATE INDEX idx_house_act_filing ON house_activities(house_filing_id);
CREATE INDEX idx_house_act_issue  ON house_activities(issue_area_code);

-- Filing-level lobbyists (name-only; no stable id). For LD2 this is the union
-- of lobbyists across all ali_info on the filing, deduped.
CREATE TABLE house_filing_lobbyists (
    house_filing_id  TEXT NOT NULL REFERENCES house_filings(house_filing_id),
    first_name       TEXT,
    last_name        TEXT,
    suffix           TEXT,
    covered_position TEXT,                       -- revolving-door signal (free text)
    is_new           TEXT                        -- Y/N
);
CREATE INDEX idx_house_lob_filing  ON house_filing_lobbyists(house_filing_id);
CREATE INDEX idx_house_lob_last    ON house_filing_lobbyists(last_name);
CREATE INDEX idx_house_lob_covered ON house_filing_lobbyists(covered_position)
    WHERE covered_position IS NOT NULL;

CREATE TABLE house_foreign_entities (
    id                   INTEGER PRIMARY KEY,
    house_filing_id      TEXT NOT NULL REFERENCES house_filings(house_filing_id),
    name                 TEXT,
    country              TEXT,
    contribution         TEXT,
    contribution_amt     REAL,
    ownership_percentage TEXT,
    city                 TEXT,
    address              TEXT
);
CREATE INDEX idx_house_foreign_filing ON house_foreign_entities(house_filing_id);
CREATE INDEX idx_house_foreign_name   ON house_foreign_entities(name);

CREATE TABLE house_affiliated_orgs (
    id              INTEGER PRIMARY KEY,
    house_filing_id TEXT NOT NULL REFERENCES house_filings(house_filing_id),
    name            TEXT,
    city            TEXT,
    state           TEXT,
    country         TEXT,
    zip             TEXT
);
CREATE INDEX idx_house_affil_filing ON house_affiliated_orgs(house_filing_id);
CREATE INDEX idx_house_affil_name   ON house_affiliated_orgs(name);

CREATE TABLE house_convictions (
    id              INTEGER PRIMARY KEY,
    house_filing_id TEXT NOT NULL REFERENCES house_filings(house_filing_id),
    lobbyist_name   TEXT,
    date            TEXT,
    description     TEXT
);
CREATE INDEX idx_house_conv_filing ON house_convictions(house_filing_id);
