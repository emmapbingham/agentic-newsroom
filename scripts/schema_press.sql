-- ============================================================================
-- Congressional press-release tables for the combined GAIN database (db/gain.db)
-- ----------------------------------------------------------------------------
-- Owns the `press_*` namespace only. Idempotent: drops + recreates just the
-- press tables, leaving shared ref_*/ingest_log and senate_*/house_* untouched.
-- Run scripts/schema_shared.sql first.
--
-- Press releases scraped from *.house.gov / *.senate.gov member sites. Light,
-- clean metadata wrapping a free-text body. The body is what matters, so the
-- table is thin and the value is the FTS5 index over title + text.
--
-- Verified (scripts/discover_press_schema.py): url is 100% unique (natural key);
-- member.bioguide_id present on 99.9% of records (536 distinct members — the
-- join key to the lobbying/contribution data via a future bioguide crosswalk).
-- ============================================================================

DROP TABLE IF EXISTS press_fts;
DROP TABLE IF EXISTS press_members;
DROP TABLE IF EXISTS press_releases;

CREATE TABLE press_releases (
    release_id   INTEGER PRIMARY KEY,      -- surrogate (= FTS rowid)
    url          TEXT UNIQUE NOT NULL,     -- natural key / public source link
    title        TEXT,
    date         TEXT,                     -- 'YYYY-MM-DD' (nullable: 14 records)
    year         INTEGER,                  -- derived from date, for fast grouping
    date_source  TEXT,                     -- 'scraper' | 'page_html'
    source       TEXT,                     -- member press-release index page
    domain       TEXT,                     -- e.g. 'costa.house.gov'
    scraper      TEXT,
    bioguide_id  TEXT,                     -- member key (nullable: 0.1%)
    member_name  TEXT,
    party        TEXT,
    state        TEXT,
    chamber      TEXT,                     -- 'House' | 'Senate'
    text         TEXT,                     -- full body, newline-preserved
    collected_at TEXT,
    updated_at   TEXT,
    source_file  TEXT
);
CREATE INDEX idx_press_bioguide ON press_releases(bioguide_id);
CREATE INDEX idx_press_date     ON press_releases(date);
CREATE INDEX idx_press_year     ON press_releases(year);
CREATE INDEX idx_press_domain   ON press_releases(domain);
CREATE INDEX idx_press_chamber  ON press_releases(chamber);
CREATE INDEX idx_press_party    ON press_releases(party);

-- Roster derived from the corpus: one row per member, with representative
-- (most-recent) metadata and activity span. Convenience + the bridge target for
-- the future member<->bioguide crosswalk.
CREATE TABLE press_members (
    bioguide_id TEXT PRIMARY KEY,
    name        TEXT,
    party       TEXT,
    state       TEXT,
    chamber     TEXT,
    n_releases  INTEGER,
    first_date  TEXT,
    last_date   TEXT
);
CREATE INDEX idx_press_members_state ON press_members(state);
