#!/usr/bin/env python3
"""Derived instrument: lobbyist revolving-door profile (Senate).

Three related tables, one builder, because they share the same junk-filtered
covered_position cleaning and canonical-filing dedup:

1. derived_lobbyist_year_profile      -- lobbyist x filing_year
   Distinct registrants/clients/issue codes worked, activity volume, and
   whether a covered position (prior government post) was disclosed that
   year. Powers within-firm-rainmaker (client-count outlier within a firm).

2. derived_lobbyist_issue_year        -- lobbyist x issue_code x filing_year
   Distinct clients per lobbyist per issue, and covered-position flag.
   Powers issue-specialist-gatekeepers (client concentration by issue) and
   revolving-door-surge-by-issue (yearly revolving-door share per issue).

3. derived_lobbyist_rr_disclosure     -- lobbyist x registrant engagement
   Whether a covered position was disclosed on the INITIAL REGISTRATION (RR)
   for a lobbyist-registrant pair, and whether it was later redisclosed on
   ANY subsequent quarterly filing for that same pair. Powers
   rr-only-disclosers (does a disclosed revolving-door credential persist
   past the initial filing, as LDA guidance expects, or vanish?).

COVERED_POSITION CLEANING: covered_position is free text on
senate_activity_lobbyists, one row per (activity, lobbyist). Known junk
values (self-reported, not a real government post) are excluded everywhere:
'N/A', 'See prior filing', 'Legislative Consultant', 'Self', 'None', '',
'Partner' (a firm title, not a government post). This list is the same one
used in the beat book's revolving-door recipe (docs/beat_book_recipes.md); keep
them in sync if either changes.

DEDUP: filings are reduced to one canonical row per
(registrant_id, client_id, filing_year, filing_period) -- latest-posted --
before counting distinct clients/activities, so amendments and duplicate
filings don't inflate counts. RR filings are registration events, not
period-keyed the same way; they are taken as-is (one row per filing_uuid,
already deduped at the source -- see docs/senate_db.md dedup note).

    python scripts/build_derived_lobbyist_revolving_door.py
    python scripts/build_derived_lobbyist_revolving_door.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")

JUNK_POSITIONS = (
    "N/A", "See prior filing", "Legislative Consultant", "Self", "None", "", "Partner",
)
JUNK_SQL = ",".join("?" for _ in JUNK_POSITIONS)

DDL = f"""
DROP TABLE IF EXISTS derived_lobbyist_year_profile;
CREATE TABLE derived_lobbyist_year_profile (
    lobbyist_id       INTEGER NOT NULL,
    lobbyist_name     TEXT,
    filing_year       INTEGER NOT NULL,
    n_registrants     INTEGER NOT NULL,   -- distinct firms lobbyist worked for
    n_clients         INTEGER NOT NULL,   -- distinct clients across those firms
    n_issue_codes     INTEGER NOT NULL,
    n_activities      INTEGER NOT NULL,   -- activity-lobbyist rows on canonical filings
    has_covered_position INTEGER NOT NULL, -- 1 if a non-junk covered_position appears this year
    PRIMARY KEY (lobbyist_id, filing_year)
);
CREATE INDEX idx_lyp_year ON derived_lobbyist_year_profile(filing_year);

DROP TABLE IF EXISTS derived_lobbyist_issue_year;
CREATE TABLE derived_lobbyist_issue_year (
    lobbyist_id       INTEGER NOT NULL,
    lobbyist_name     TEXT,
    issue_code        TEXT    NOT NULL,
    filing_year       INTEGER NOT NULL,
    n_clients         INTEGER NOT NULL,
    n_activities      INTEGER NOT NULL,
    has_covered_position INTEGER NOT NULL,
    PRIMARY KEY (lobbyist_id, issue_code, filing_year)
);
CREATE INDEX idx_liy_issue_year ON derived_lobbyist_issue_year(issue_code, filing_year);

DROP TABLE IF EXISTS derived_lobbyist_rr_disclosure;
CREATE TABLE derived_lobbyist_rr_disclosure (
    lobbyist_id         INTEGER NOT NULL,
    lobbyist_name       TEXT,
    registrant_id       INTEGER NOT NULL,
    registrant_name     TEXT,
    rr_filing_uuid      TEXT,
    rr_covered_position TEXT,             -- cleaned (non-junk) position text disclosed on RR
    rr_filing_year      INTEGER,
    n_subsequent_quarterlies      INTEGER NOT NULL, -- any filing type for this pair, after RR
    n_subsequent_with_disclosure  INTEGER NOT NULL, -- of those, how many redisclose the position
    redisclosed_ever    INTEGER NOT NULL, -- 1 if n_subsequent_with_disclosure > 0
    PRIMARY KEY (lobbyist_id, registrant_id)
);
CREATE INDEX idx_lrr_registrant ON derived_lobbyist_rr_disclosure(registrant_id);
"""

BUILD_YEAR_PROFILE = f"""
INSERT INTO derived_lobbyist_year_profile
WITH ranked AS (
  SELECT f.filing_uuid, f.registrant_id, f.client_id, f.filing_year,
         row_number() OVER (
           PARTITION BY f.registrant_id, f.client_id, f.filing_year, f.filing_period
           ORDER BY f.dt_posted DESC, f.filing_uuid DESC
         ) AS rn
  FROM senate_filings f
  WHERE f.filing_period IN
        ('first_quarter','second_quarter','third_quarter','fourth_quarter')
),
canon AS (
  SELECT filing_uuid, registrant_id, client_id, filing_year FROM ranked WHERE rn = 1
),
rows AS (
  SELECT al.lobbyist_id, c.filing_year, c.registrant_id, c.client_id,
         a.general_issue_code,
         CASE WHEN al.covered_position IS NOT NULL
                   AND trim(al.covered_position) NOT IN ({JUNK_SQL})
              THEN 1 ELSE 0 END AS has_cp
  FROM canon c
  JOIN senate_lobbying_activities a ON a.filing_uuid = c.filing_uuid
  JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id
)
SELECT
  r.lobbyist_id,
  max(l.first_name || ' ' || l.last_name),
  r.filing_year,
  count(DISTINCT r.registrant_id),
  count(DISTINCT r.client_id),
  count(DISTINCT r.general_issue_code),
  count(*),
  max(r.has_cp)
FROM rows r
LEFT JOIN senate_lobbyists l ON l.id = r.lobbyist_id
GROUP BY r.lobbyist_id, r.filing_year;
"""

BUILD_ISSUE_YEAR = f"""
INSERT INTO derived_lobbyist_issue_year
WITH ranked AS (
  SELECT f.filing_uuid, f.registrant_id, f.client_id, f.filing_year,
         row_number() OVER (
           PARTITION BY f.registrant_id, f.client_id, f.filing_year, f.filing_period
           ORDER BY f.dt_posted DESC, f.filing_uuid DESC
         ) AS rn
  FROM senate_filings f
  WHERE f.filing_period IN
        ('first_quarter','second_quarter','third_quarter','fourth_quarter')
),
canon AS (
  SELECT filing_uuid, registrant_id, client_id, filing_year FROM ranked WHERE rn = 1
),
rows AS (
  SELECT al.lobbyist_id, c.filing_year, c.client_id, a.general_issue_code,
         CASE WHEN al.covered_position IS NOT NULL
                   AND trim(al.covered_position) NOT IN ({JUNK_SQL})
              THEN 1 ELSE 0 END AS has_cp
  FROM canon c
  JOIN senate_lobbying_activities a ON a.filing_uuid = c.filing_uuid
  JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id
  WHERE a.general_issue_code IS NOT NULL
)
SELECT
  r.lobbyist_id,
  max(l.first_name || ' ' || l.last_name),
  r.general_issue_code,
  r.filing_year,
  count(DISTINCT r.client_id),
  count(*),
  max(r.has_cp)
FROM rows r
LEFT JOIN senate_lobbyists l ON l.id = r.lobbyist_id
GROUP BY r.lobbyist_id, r.general_issue_code, r.filing_year;
"""

BUILD_RR_DISCLOSURE = f"""
INSERT INTO derived_lobbyist_rr_disclosure
WITH rr_positions AS (
  -- one row per (lobbyist, registrant) with a non-junk covered_position disclosed on an RR
  SELECT al.lobbyist_id, f.registrant_id, f.filing_uuid AS rr_filing_uuid,
         f.filing_year AS rr_filing_year,
         al.covered_position AS rr_covered_position,
         row_number() OVER (
           PARTITION BY al.lobbyist_id, f.registrant_id
           ORDER BY f.dt_posted ASC, f.filing_uuid ASC
         ) AS rn
  FROM senate_filings f
  JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
  JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id
  WHERE f.filing_type = 'RR'
    AND al.covered_position IS NOT NULL
    AND trim(al.covered_position) NOT IN ({JUNK_SQL})
),
first_rr AS (
  SELECT lobbyist_id, registrant_id, rr_filing_uuid, rr_filing_year, rr_covered_position
  FROM rr_positions WHERE rn = 1
),
subsequent AS (
  -- any filing (any type) for the same lobbyist-registrant pair, dated after the RR
  SELECT fr.lobbyist_id, fr.registrant_id, f.filing_uuid,
         CASE WHEN al.covered_position IS NOT NULL
                   AND trim(al.covered_position) NOT IN ({JUNK_SQL})
              THEN 1 ELSE 0 END AS has_cp
  FROM first_rr fr
  JOIN senate_filings f ON f.registrant_id = fr.registrant_id AND f.filing_type != 'RR'
  JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
  JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id AND al.lobbyist_id = fr.lobbyist_id
  WHERE f.filing_year > fr.rr_filing_year
     OR (f.filing_year = fr.rr_filing_year AND f.filing_uuid != fr.rr_filing_uuid)
)
SELECT
  fr.lobbyist_id,
  max(l.first_name || ' ' || l.last_name),
  fr.registrant_id,
  max(r.name),
  fr.rr_filing_uuid,
  fr.rr_covered_position,
  fr.rr_filing_year,
  count(DISTINCT s.filing_uuid),
  count(DISTINCT CASE WHEN s.has_cp = 1 THEN s.filing_uuid END),
  CASE WHEN count(DISTINCT CASE WHEN s.has_cp = 1 THEN s.filing_uuid END) > 0 THEN 1 ELSE 0 END
FROM first_rr fr
LEFT JOIN subsequent s ON s.lobbyist_id = fr.lobbyist_id AND s.registrant_id = fr.registrant_id
LEFT JOIN senate_lobbyists l ON l.id = fr.lobbyist_id
LEFT JOIN senate_registrants r ON r.id = fr.registrant_id
GROUP BY fr.lobbyist_id, fr.registrant_id;
"""


def build(con):
    con.executescript(DDL)
    con.execute(BUILD_YEAR_PROFILE, JUNK_POSITIONS)
    con.execute(BUILD_ISSUE_YEAR, JUNK_POSITIONS)
    con.execute(BUILD_RR_DISCLOSURE, JUNK_POSITIONS * 2)

    counts = {}
    for t in ("derived_lobbyist_year_profile", "derived_lobbyist_issue_year", "derived_lobbyist_rr_disclosure"):
        counts[t] = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]

    con.execute("DELETE FROM ingest_log WHERE source='lobbyist_revolving_door'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('lobbyist_revolving_door','derived','db/gain.db',?,?,datetime('now'))",
        ("derived_lobbyist_year_profile+issue_year+rr_disclosure", sum(counts.values())),
    )
    con.commit()
    for t, n in counts.items():
        print(f"built {t}: {n:,} rows")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")

    # 1. year profile: no lobbyist-year should have more clients than activities
    bad = con.execute(
        "SELECT count(*) FROM derived_lobbyist_year_profile WHERE n_clients > n_activities"
    ).fetchone()[0]
    check("n_clients <= n_activities in every lobbyist-year row", bad == 0)

    # 2. issue-year table sums of n_activities per lobbyist-year <= year-profile n_activities
    #    (an activity can carry multiple issue codes only if the source has multiple rows
    #    per activity per issue -- here it's one issue code per activity, so this should hold
    #    with equality when a lobbyist works exactly one issue per client-activity)
    mismatch = con.execute(
        """
        SELECT count(*) FROM (
          SELECT y.lobbyist_id, y.filing_year, y.n_activities AS ya, sum(i.n_activities) AS ia
          FROM derived_lobbyist_year_profile y
          JOIN derived_lobbyist_issue_year i
            ON i.lobbyist_id = y.lobbyist_id AND i.filing_year = y.filing_year
          GROUP BY y.lobbyist_id, y.filing_year
          HAVING ia > ya
        )
        """
    ).fetchone()[0]
    check("issue-year activity sum never exceeds year-profile activity count", mismatch == 0)

    # 3. RR-disclosure table: report the actual redisclosure rate (do NOT assume the
    #    screen's cited "62.1% vs 25-27%" baseline -- that number's grain is unverified
    #    and a prior ad hoc check at the lobbyist x registrant grain found ~80%, the
    #    opposite direction).
    n_pairs, n_redisc = con.execute(
        "SELECT count(*), sum(redisclosed_ever) FROM derived_lobbyist_rr_disclosure"
    ).fetchone()
    rate = 100 * n_redisc / n_pairs if n_pairs else 0
    print(f"  RR-disclosed lobbyist-registrant pairs: {n_pairs:,}; "
          f"redisclosed on >=1 later filing: {n_redisc:,} ({rate:.1f}%)")
    check("RR-disclosure table is non-empty", n_pairs > 0)

    # 4. spot-check a known revolving-door name resolves sensibly (Former Member of
    #    Congress is real signal, not junk -- confirm it survives the filter)
    fmoc = con.execute(
        "SELECT count(*) FROM derived_lobbyist_rr_disclosure WHERE rr_covered_position LIKE '%Former Member of Congress%'"
    ).fetchone()[0]
    print(f"  RR disclosures citing 'Former Member of Congress': {fmoc}")
    check("Former Member of Congress survives the junk filter", fmoc > 0)

    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)
    try:
        if args.validate:
            sys.exit(0 if validate(con) else 1)
        build(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
