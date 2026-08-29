#!/usr/bin/env python3
"""Derived instrument: registrant x issue x year activity panel (Senate).

For spotting issue-area entry/surge (e.g. the 2025 tariff lead: registrants
newly active on TAR). Built on the SAME canonical (deduped) filing set as the
income panel — one filing per (registrant, client, year, quarter), latest-posted —
so duplicate/amendment filings don't inflate activity counts.

Grain: registrant x general_issue_code x filing_year.

    python scripts/build_derived_registrant_issue.py
    python scripts/build_derived_registrant_issue.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_registrant_issue_panel"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    registrant_id   INTEGER NOT NULL,
    registrant_name TEXT,
    issue_code      TEXT    NOT NULL,
    issue_display   TEXT,
    filing_year     INTEGER NOT NULL,
    n_activities    INTEGER NOT NULL,   -- activity rows on canonical filings
    n_engagements   INTEGER NOT NULL,   -- distinct canonical filings (reg-client-qtr)
    PRIMARY KEY (registrant_id, issue_code, filing_year)
);
"""

BUILD = f"""
INSERT INTO {TABLE}
WITH canon AS (
  SELECT f.filing_uuid, f.registrant_id, f.filing_year,
         row_number() OVER (
           PARTITION BY f.registrant_id, f.client_id, f.filing_year, f.filing_period
           ORDER BY f.dt_posted DESC, f.filing_uuid DESC
         ) AS rn
  FROM senate_filings f
  WHERE f.filing_period IN
        ('first_quarter','second_quarter','third_quarter','fourth_quarter')
)
SELECT
  c.registrant_id,
  r.name,
  a.general_issue_code,
  max(a.general_issue_code_display),
  c.filing_year,
  count(*),
  count(DISTINCT c.filing_uuid)
FROM canon c
JOIN senate_lobbying_activities a ON a.filing_uuid = c.filing_uuid
LEFT JOIN senate_registrants r ON r.id = c.registrant_id
WHERE c.rn = 1 AND a.general_issue_code IS NOT NULL
GROUP BY c.registrant_id, a.general_issue_code, c.filing_year;
"""

INDEXES = [
    f"CREATE INDEX idx_rixp_reg   ON {TABLE}(registrant_id);",
    f"CREATE INDEX idx_rixp_issue ON {TABLE}(issue_code, filing_year);",
]


def build(con):
    con.executescript(DDL)
    con.execute(BUILD)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='registrant_issue'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('registrant_issue','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n:,} registrant-issue-years")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")
    # 1. confirm the tariff code exists and resolve its label
    tar = con.execute(
        f"SELECT issue_display, sum(n_activities) FROM {TABLE} WHERE issue_code='TAR'"
    ).fetchone()
    print(f"  TAR = {tar[0]!r}, {tar[1]:,} total activities")
    check("TAR code present", tar[1] and tar[1] > 0)

    # 2. VERIFY THE TARIFF-SURGE PREMISE (don't assume the scout's numbers).
    #    Activity counts by year, and count of registrants whose FIRST TAR year
    #    is 2025 (the "204 first-time TAR registrants" claim).
    print("  TAR activities by year:")
    for yr, na, nr in con.execute(
        f"SELECT filing_year, sum(n_activities), count(*) FROM {TABLE} "
        "WHERE issue_code='TAR' GROUP BY filing_year ORDER BY filing_year"
    ).fetchall():
        print(f"    {yr}: {na:>6,} activities across {nr:>4} registrants")
    first2025 = con.execute(
        f"""SELECT count(*) FROM (
              SELECT registrant_id, min(filing_year) fy FROM {TABLE}
              WHERE issue_code='TAR' GROUP BY registrant_id) WHERE fy=2025"""
    ).fetchone()[0]
    print(f"  registrants whose FIRST TAR year is 2025: {first2025} "
          f"(sweep scout claimed ~204 first-time)")
    check("first-time-2025 TAR registrants is a substantial cohort (>100)",
          first2025 > 100)

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
