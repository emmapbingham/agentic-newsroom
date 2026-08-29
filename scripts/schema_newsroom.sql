-- Newsroom editorial ledgers (investigations/newsroom.db).
--
-- Durable editorial state — the record of what was proposed, run, and decided.
-- Tracked in git (see .gitignore exception). Shortlists live as files; these
-- tables are the index/board over them.
--
-- Init / reset:  sqlite3 investigations/newsroom.db < scripts/schema_newsroom.sql

PRAGMA foreign_keys = ON;

-- Derived tables: the shared derived_* tables in gain.db that screens run on top of.
-- A discoverability index agents read before recomputing anything from raw.
CREATE TABLE IF NOT EXISTS derived_tables (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,    -- kebab-case slug (matches derived_* table in gain.db)
    answers       TEXT NOT NULL,           -- what question this makes cheap, in one sentence
    builder_script TEXT                    -- scripts/build_*.py that creates it
);

-- Screens: registered deterministic queries that emit ranked shortlists.
-- The system's accumulated fishing capability. A screen can only run once its
-- derived_table is built; backlog screens are honest about that dependency.
CREATE TABLE IF NOT EXISTS screens (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    contrast_type TEXT CHECK (contrast_type IN
                  ('outlier-vs-peers','self-over-time','source-vs-source',
                   'absence','data-vs-law','population-structure')),
    derived_table TEXT,                    -- derived_tables.name it reads (NULL = raw tables)
    baseline      TEXT NOT NULL,           -- what 'expected' means, in one line
    sql_path      TEXT,                    -- investigations/screens/<name>/screen.sql
    status        TEXT NOT NULL DEFAULT 'live'
                  CHECK (status IN ('live','backlog')),
    priority      TEXT CHECK (priority IN ('high','medium','low')),
    grain         TEXT CHECK (grain IN ('actor','structure')),
                                           -- actor: shortlist rows name someone who did something
                                           --   (registrant/member/client/lobbyist) → surface as leads.
                                           -- structure: rows are issue/committee/code-level patterns
                                           --   → drill to actors before surfacing (see fish-for-leads
                                           --   reference/lead-gates.md).
    needs_table   TEXT,                    -- for backlog rows: the derived_table not yet built
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    notes         TEXT
);

-- Screen runs: the multiple-comparisons ledger. Every execution is logged so
-- the skeptic can always answer "this lead surfaced out of how many screens?".
CREATE TABLE IF NOT EXISTS screen_runs (
    id            INTEGER PRIMARY KEY,
    screen_id     INTEGER NOT NULL REFERENCES screens(id),
    run_at        TEXT NOT NULL DEFAULT (datetime('now')),
    params        TEXT,                    -- JSON: thresholds/filters used
    n_candidates  INTEGER,                 -- shortlist size emitted
    shortlist_path TEXT,                   -- investigations/screens/<name>/run-<id>/shortlist.csv
    figures_path  TEXT,                    -- distribution plot(s) saved by the runner
    notes         TEXT
);

-- Leads: append-only run-record of candidates surfaced by screen runs.
-- Ephemeral but logged — every surfaced candidate is a row, carrying its story
-- and the probe SQL that produced it. Rows are never deleted or edited after
-- surfacing, but each carries a `disposition`: the editorial fate (or a
-- surfacing-gate suppression, kept so the run-record stays complete). The
-- disposition ledger is how the editor's taste accumulates as data — the
-- go-fish loop reads recent dispositions before surfacing new leads.
-- Promotion sets promoted_at + case_slug; the case owns the verdict after.
CREATE TABLE IF NOT EXISTS leads (
    id              INTEGER PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    screen_run_id   INTEGER REFERENCES screen_runs(id),  -- NULL for sweep-derived or desk leads
    story           TEXT NOT NULL,         -- 2-3 plain-language sentences; the front door
    claim           TEXT,                  -- one line, falsifiable
    probe_sql       TEXT,                  -- the exact query that produced this candidate
    scout_number    TEXT,                  -- flagged unverified until re-derived
    boring_explanation TEXT,               -- strongest innocent account of the same rows
    surfaced_at     TEXT NOT NULL DEFAULT (datetime('now')),
    promoted_at     TEXT,                  -- set when promoted to a case
    case_slug       TEXT,                  -- investigations/<slug>/; NULL until promoted
    disposition     TEXT CHECK (disposition IN
                    ('promoted',           -- editor promoted to a case
                     'pass-boring',        -- editor: boring explanation wins / no story
                     'pass-covered',       -- editor: already reported
                     'duplicate-of',       -- same candidate as an earlier lead (name it in reason)
                     'artifact',           -- data-quality artifact, not a real-world pattern
                     'suppressed-covered', -- surfacing gate: novelty-lite found a decisive hit
                     'suppressed-boring',  -- surfacing gate: boring explanation beat the story
                     'suppressed-below-cut')), -- unattended run: passed gates but fell below the K-cap
                                           -- NULL = surfaced, awaiting editor triage
    disposition_reason TEXT,               -- one line: the editor's why, or the gate's citation
    disposition_at  TEXT
);

-- Sweeps: the rare, expensive fleet operation that designs new screens and
-- proposes derived tables. Its output is screens + table proposals, not leads.
CREATE TABLE IF NOT EXISTS sweeps (
    id              INTEGER PRIMARY KEY,
    run_at          TEXT NOT NULL,
    grid            TEXT,                  -- e.g. 'contrast×grain 6×6'
    tokens          INTEGER,               -- approximate total tokens consumed
    agents          INTEGER,               -- number of agents in the fleet
    n_screens_added INTEGER,               -- screens registered from this sweep
    report_path     TEXT,                  -- investigations/sweeps/<date>-*.json
    notes           TEXT
);

-- Actions: append-only journal of every newsroom state change, with actor and
-- review state. The editor's review queue reads unreviewed rows ranked by
-- priority, grouped by object; acknowledging an object's latest action
-- acknowledges its chain (record in review_note). Overturns never edit
-- history: append an action='overturn' row (editor-attributed) and set the
-- target row's review_state='overturned'. Editor-directed actions are born
-- acknowledged. Hard gate: nothing crosses the system boundary (findings
-- report, comment requests, publication) unless its chain is acknowledged.
CREATE TABLE IF NOT EXISTS actions (
    id           INTEGER PRIMARY KEY,
    at           TEXT NOT NULL DEFAULT (datetime('now')),
    actor        TEXT NOT NULL CHECK (actor IN ('editor','agent-live','agent-auto')),
                                            -- editor: human made the call (born acknowledged)
                                            -- agent-live: agent acted, human present in session
                                            -- agent-auto: unattended run
    object_type  TEXT NOT NULL CHECK (object_type IN
                 ('lead','case','screen','derived_table','sweep')),
    object_ref   TEXT NOT NULL,             -- slug / name
    action       TEXT NOT NULL,             -- surface|suppress|pass|promote|open-case|verdict|
                                            -- kill|close|novelty-scan|build|register|run|overturn|...
    basis        TEXT,                      -- one line: why + pointers (run ids, evidence ids)
    priority     INTEGER CHECK (priority BETWEEN 1 AND 5),
                                            -- review rank: 5 kill/promote/verdict on report-bound work,
                                            -- 3 builds/registrations, 1 routine suppressions
    review_state TEXT NOT NULL DEFAULT 'unreviewed'
                 CHECK (review_state IN ('unreviewed','acknowledged','overturned')),
    reviewed_at  TEXT,
    reviewed_by  TEXT,                      -- who signed off: 'emma' | 'ian' (required when
                                            -- review_state leaves 'unreviewed')
    review_note  TEXT
);
CREATE INDEX IF NOT EXISTS idx_actions_review ON actions(review_state, priority DESC);
CREATE INDEX IF NOT EXISTS idx_actions_object ON actions(object_type, object_ref);
