-- ============================================================================
-- Member crosswalk tables for the combined GAIN database (db/gain.db)
-- ----------------------------------------------------------------------------
-- Owns the `member_*` + `committees` + `honoree_member_map` namespace. Built
-- from the public-domain `unitedstates/congress-legislators` dataset (see
-- sources/congress-legislators.md). Idempotent + source-scoped. Run
-- scripts/schema_shared.sql first.
--
-- Purpose: the missing bridge between the lobbying/contribution money and the
-- press corpus. `bioguide` ties to press_releases.bioguide_id; honoree_member_map
-- resolves the free-text senate_contribution_items.honoree_name to a bioguide;
-- committees give the "which member sits where" context for influence analysis.
-- ============================================================================

DROP TABLE IF EXISTS honoree_member_map;
DROP TABLE IF EXISTS member_committees;
DROP TABLE IF EXISTS committees;
DROP TABLE IF EXISTS member_terms;
DROP TABLE IF EXISTS members;

CREATE TABLE members (
    bioguide         TEXT PRIMARY KEY,
    first            TEXT,
    middle           TEXT,
    last             TEXT,
    nickname         TEXT,
    official_full    TEXT,
    is_current       INTEGER,            -- 1 = in legislators-current
    last_type        TEXT,               -- 'rep' | 'sen' (most recent term)
    last_state       TEXT,
    last_party       TEXT,
    first_term_start TEXT,
    last_term_end    TEXT,
    fec_ids          TEXT,               -- comma-separated FEC candidate ids
    opensecrets_id   TEXT,
    govtrack_id      INTEGER,
    icpsr_id         INTEGER
);
CREATE INDEX idx_members_last    ON members(last);
CREATE INDEX idx_members_current ON members(is_current);

CREATE TABLE member_terms (
    bioguide TEXT NOT NULL REFERENCES members(bioguide),
    seq      INTEGER,
    type     TEXT,       -- 'rep' | 'sen'
    state    TEXT,
    district INTEGER,
    party    TEXT,
    start    TEXT,
    end      TEXT
);
CREATE INDEX idx_member_terms_bio ON member_terms(bioguide);

CREATE TABLE committees (
    committee_id        TEXT PRIMARY KEY,  -- thomas_id (top) or parent+sub (subcommittee)
    type                TEXT,              -- 'house' | 'senate' | 'joint'
    name                TEXT,
    parent_committee_id TEXT               -- NULL for top-level committees
);

CREATE TABLE member_committees (
    bioguide     TEXT NOT NULL REFERENCES members(bioguide),
    committee_id TEXT NOT NULL REFERENCES committees(committee_id),
    side         TEXT,        -- 'majority' | 'minority'
    rank         INTEGER,
    title        TEXT         -- e.g. 'Chairman', 'Ranking Member'
);
CREATE INDEX idx_member_committees_bio ON member_committees(bioguide);
CREATE INDEX idx_member_committees_com ON member_committees(committee_id);

-- Resolution of the free-text contribution honoree to a member (best-effort;
-- carries the method + confidence so every match is auditable). Non-member
-- honorees (e.g. challengers) stay unmatched by design.
CREATE TABLE honoree_member_map (
    honoree_name TEXT PRIMARY KEY,   -- raw senate_contribution_items.honoree_name
    normalized   TEXT,               -- honorifics/titles stripped
    bioguide     TEXT REFERENCES members(bioguide),
    method       TEXT,               -- 'official_full' | 'first_last' | 'nickname_last' | 'last_unique' | NULL
    confidence   REAL                -- 1.0 exact full name ... lower for looser matches
);
CREATE INDEX idx_honoree_bioguide ON honoree_member_map(bioguide);
