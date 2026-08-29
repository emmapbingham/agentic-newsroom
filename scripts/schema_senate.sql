-- ============================================================================
-- Senate LDA tables for the combined GAIN database (db/gain.db)
-- ----------------------------------------------------------------------------
-- Owns the `senate_*` namespace only. Idempotent: drops and recreates just the
-- Senate tables, leaving shared ref_*/ingest_log and other sources' tables
-- (house_*, press_*) untouched. Run scripts/schema_shared.sql first.
--
-- Design (mapped to the rubric — see also docs/senate_db.md):
--   * Verifiability — every fact row carries the source filing_uuid:
--       lobbying filings:     https://lda.gov/filings/public/filing/{filing_uuid}/print/
--       contribution filings: https://lda.gov/filings/public/contribution/{filing_uuid}/print/
--     (different path segment and UUID namespace per record type; both need
--     the trailing /print/ or the URL 404s. LDA is migrating
--     lda.senate.gov -> lda.gov, same paths -- use lda.gov going forward.)
--     Dimensions keep the Senate API's exact numeric IDs.
--   * Efficiency — controlled vocabularies are shared ref tables; money is
--     stored raw (auditable) + parsed (aggregatable).
--   * Capability — nested LDA structure flattened into composable fact tables.
--
-- Verified key facts (scripts/discover_senate_schema.py):
--   registrant.id / client.id / lobbyist.id are clean stable global keys.
--   registrant.house_registrant_id bridges to the House data.
--   client.id (API-addressable, 1:1 with name) is the client key; client_id is
--   a coarser grouping kept only for later entity resolution.
-- ============================================================================

DROP TABLE IF EXISTS senate_activities_fts;
DROP TABLE IF EXISTS senate_contribution_pacs;
DROP TABLE IF EXISTS senate_contribution_items;
DROP TABLE IF EXISTS senate_contribution_filings;
DROP TABLE IF EXISTS senate_filing_conviction_disclosures;
DROP TABLE IF EXISTS senate_filing_affiliated_orgs;
DROP TABLE IF EXISTS senate_filing_foreign_entities;
DROP TABLE IF EXISTS senate_activity_government_entities;
DROP TABLE IF EXISTS senate_activity_lobbyists;
DROP TABLE IF EXISTS senate_lobbying_activities;
DROP TABLE IF EXISTS senate_filings;
DROP TABLE IF EXISTS senate_lobbyists;
DROP TABLE IF EXISTS senate_clients;
DROP TABLE IF EXISTS senate_registrants;

-- ----------------------------------------------------------------------------
-- Dimensions (PKs are the Senate API's own IDs)
-- ----------------------------------------------------------------------------
CREATE TABLE senate_registrants (
    id                  INTEGER PRIMARY KEY,   -- registrant.id (global)
    name                TEXT NOT NULL,
    description         TEXT,
    house_registrant_id INTEGER,               -- bridge to House LDA data
    address_1           TEXT,
    address_2           TEXT,
    city                TEXT,
    state               TEXT,
    state_display       TEXT,
    zip                 TEXT,
    country             TEXT,
    contact_name        TEXT,
    contact_telephone   TEXT,
    dt_updated          TEXT
);
CREATE INDEX idx_senate_registrants_house ON senate_registrants(house_registrant_id);
CREATE INDEX idx_senate_registrants_name  ON senate_registrants(name);

CREATE TABLE senate_clients (
    id                      INTEGER PRIMARY KEY, -- client.id (API-addressable)
    client_id               INTEGER,             -- coarser grouping (kept for ER)
    name                    TEXT NOT NULL,
    general_description     TEXT,
    client_government_entity INTEGER,            -- bool 0/1, nullable
    client_self_select      INTEGER,             -- bool 0/1, nullable
    state                   TEXT,
    state_display           TEXT,
    country                 TEXT,
    ppb_state               TEXT,
    ppb_country             TEXT
);
CREATE INDEX idx_senate_clients_client_id ON senate_clients(client_id);
CREATE INDEX idx_senate_clients_name      ON senate_clients(name);

CREATE TABLE senate_lobbyists (
    id          INTEGER PRIMARY KEY,            -- lobbyist.id (global)
    first_name  TEXT,
    middle_name TEXT,
    last_name   TEXT,
    nickname    TEXT,
    prefix      TEXT,
    suffix      TEXT
);
CREATE INDEX idx_senate_lobbyists_last ON senate_lobbyists(last_name);

-- ----------------------------------------------------------------------------
-- Facts — LDA filings (LD-1 registrations, LD-2 quarterly activity)
-- ----------------------------------------------------------------------------
CREATE TABLE senate_filings (
    filing_uuid           TEXT PRIMARY KEY,
    filing_type           TEXT REFERENCES ref_filing_types(value),
    filing_type_display   TEXT,
    filing_year           INTEGER,
    filing_period         TEXT,
    filing_period_display TEXT,
    registrant_id         INTEGER REFERENCES senate_registrants(id),
    client_id             INTEGER REFERENCES senate_clients(id),  -- = client.id
    income                TEXT,
    income_amt            REAL,
    expenses              TEXT,
    expenses_amt          REAL,
    expenses_method       TEXT,
    expenses_method_display TEXT,
    client_effective_date TEXT,
    posted_by_name        TEXT,
    dt_posted             TEXT,
    termination_date      TEXT,
    url                   TEXT,
    filing_document_url   TEXT
);
CREATE INDEX idx_senate_filings_registrant   ON senate_filings(registrant_id);
CREATE INDEX idx_senate_filings_client       ON senate_filings(client_id);
CREATE INDEX idx_senate_filings_year_period  ON senate_filings(filing_year, filing_period);
CREATE INDEX idx_senate_filings_type         ON senate_filings(filing_type);

CREATE TABLE senate_lobbying_activities (
    activity_id                INTEGER PRIMARY KEY,
    filing_uuid                TEXT NOT NULL REFERENCES senate_filings(filing_uuid),
    seq                        INTEGER,
    general_issue_code         TEXT REFERENCES ref_issue_codes(value),
    general_issue_code_display TEXT,
    description                TEXT,
    foreign_entity_issues      TEXT
);
CREATE INDEX idx_senate_activities_filing ON senate_lobbying_activities(filing_uuid);
CREATE INDEX idx_senate_activities_issue  ON senate_lobbying_activities(general_issue_code);

CREATE TABLE senate_activity_lobbyists (
    activity_id      INTEGER NOT NULL REFERENCES senate_lobbying_activities(activity_id),
    lobbyist_id      INTEGER NOT NULL REFERENCES senate_lobbyists(id),
    covered_position TEXT,        -- prior gov role (revolving-door signal)
    is_new           INTEGER
);
CREATE INDEX idx_senate_actlob_activity ON senate_activity_lobbyists(activity_id);
CREATE INDEX idx_senate_actlob_lobbyist ON senate_activity_lobbyists(lobbyist_id);
CREATE INDEX idx_senate_actlob_covered  ON senate_activity_lobbyists(covered_position)
    WHERE covered_position IS NOT NULL;

CREATE TABLE senate_activity_government_entities (
    activity_id          INTEGER NOT NULL REFERENCES senate_lobbying_activities(activity_id),
    government_entity_id  INTEGER NOT NULL REFERENCES ref_government_entities(id)
);
CREATE INDEX idx_senate_actge_activity ON senate_activity_government_entities(activity_id);
CREATE INDEX idx_senate_actge_entity   ON senate_activity_government_entities(government_entity_id);

CREATE TABLE senate_filing_foreign_entities (
    id                   INTEGER PRIMARY KEY,
    filing_uuid          TEXT NOT NULL REFERENCES senate_filings(filing_uuid),
    name                 TEXT,
    country              TEXT,
    country_display      TEXT,
    ownership_percentage TEXT,
    contribution         TEXT,
    contribution_amt     REAL,
    city                 TEXT,
    address              TEXT,
    ppb_country          TEXT
);
CREATE INDEX idx_senate_foreign_filing ON senate_filing_foreign_entities(filing_uuid);
CREATE INDEX idx_senate_foreign_name   ON senate_filing_foreign_entities(name);

CREATE TABLE senate_filing_affiliated_orgs (
    id          INTEGER PRIMARY KEY,
    filing_uuid TEXT NOT NULL REFERENCES senate_filings(filing_uuid),
    name        TEXT,
    city        TEXT,
    state       TEXT,
    country     TEXT,
    url         TEXT
);
CREATE INDEX idx_senate_affil_filing ON senate_filing_affiliated_orgs(filing_uuid);
CREATE INDEX idx_senate_affil_name   ON senate_filing_affiliated_orgs(name);

CREATE TABLE senate_filing_conviction_disclosures (
    id          INTEGER PRIMARY KEY,
    filing_uuid TEXT NOT NULL REFERENCES senate_filings(filing_uuid),
    lobbyist_id INTEGER REFERENCES senate_lobbyists(id),
    date        TEXT,
    description TEXT
);
CREATE INDEX idx_senate_conv_filing   ON senate_filing_conviction_disclosures(filing_uuid);
CREATE INDEX idx_senate_conv_lobbyist ON senate_filing_conviction_disclosures(lobbyist_id);

-- ----------------------------------------------------------------------------
-- Facts — LD-203 contribution reports
-- ----------------------------------------------------------------------------
CREATE TABLE senate_contribution_filings (
    filing_uuid         TEXT PRIMARY KEY,
    filing_type         TEXT REFERENCES ref_filing_types(value),
    filing_type_display TEXT,
    filing_year         INTEGER,
    filing_period       TEXT,
    filing_period_display TEXT,
    registrant_id       INTEGER REFERENCES senate_registrants(id),
    lobbyist_id         INTEGER REFERENCES senate_lobbyists(id),
    filer_type          TEXT,
    no_contributions    INTEGER,
    comments            TEXT,
    dt_posted           TEXT,
    url                 TEXT,
    filing_document_url TEXT
);
CREATE INDEX idx_senate_contribfilings_reg  ON senate_contribution_filings(registrant_id);
CREATE INDEX idx_senate_contribfilings_lob  ON senate_contribution_filings(lobbyist_id);
CREATE INDEX idx_senate_contribfilings_year ON senate_contribution_filings(filing_year);

CREATE TABLE senate_contribution_items (
    item_id            INTEGER PRIMARY KEY,
    filing_uuid        TEXT NOT NULL REFERENCES senate_contribution_filings(filing_uuid),
    contribution_type  TEXT REFERENCES ref_contribution_item_types(value),
    contributor_name   TEXT,
    payee_name         TEXT,
    honoree_name       TEXT,    -- the member/official honored (-> bioguide later)
    amount             TEXT,
    amount_num         REAL,
    date               TEXT
);
CREATE INDEX idx_senate_contribitems_filing  ON senate_contribution_items(filing_uuid);
CREATE INDEX idx_senate_contribitems_honoree ON senate_contribution_items(honoree_name);
CREATE INDEX idx_senate_contribitems_payee   ON senate_contribution_items(payee_name);
CREATE INDEX idx_senate_contribitems_date    ON senate_contribution_items(date);

CREATE TABLE senate_contribution_pacs (
    filing_uuid TEXT NOT NULL REFERENCES senate_contribution_filings(filing_uuid),
    pac_name    TEXT
);
CREATE INDEX idx_senate_contribpacs_filing ON senate_contribution_pacs(filing_uuid);
CREATE INDEX idx_senate_contribpacs_name   ON senate_contribution_pacs(pac_name);
