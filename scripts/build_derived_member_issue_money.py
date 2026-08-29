#!/usr/bin/env python3
"""Derived table: per-member per-issue-code per-year FECA contributions from sector-active registrants.

For say-vs-pay screens: committee-funded-silence, high-money-zero-press,
rising-money-falling-voice. Answers: how much did registrants active in
issue code X give to member M in year Y?

Join logic:
  1. Dedup registrant-year-issue (one row per registrant that lobbied on
     that code in that calendar year, using Q1-Q4 originals only).
  2. Per registrant-year-bioguide: sum FECA contributions from LD-203.
  3. Cross-join (2) to (1) to attribute dollars to issue codes.

This means one registrant's $5k FECA gift is counted under *each* issue
code that registrant lobbied on that year — correct for the question
"how much did health-sector money flow to this member?"

Caveats:
- FECA only (political contributions). Other contribution_types excluded.
- Confidence >= 0.9 on honoree_member_map.
- Lobbying year = calendar year of senate_filings.filing_year (not
  contribution filing year); contribution year = scf.filing_year.
  We match them on the same integer year.
- filing_type filter ('Q1','Q2','Q3','Q4') keeps originals; skips
  amendments and LD-1/LD-2 registrations to avoid double-counting.

    python scripts/build_derived_member_issue_money.py
    python scripts/build_derived_member_issue_money.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_member_issue_money_panel"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    bioguide              TEXT NOT NULL,
    member_name           TEXT,
    party                 TEXT,
    state                 TEXT,
    issue_code            TEXT NOT NULL,
    issue_name            TEXT,
    year                  INTEGER NOT NULL,
    feca_total            REAL NOT NULL DEFAULT 0,
    n_giving_registrants  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (bioguide, issue_code, year)
);
CREATE INDEX IF NOT EXISTS idx_mimp_bioguide   ON {TABLE}(bioguide);
CREATE INDEX IF NOT EXISTS idx_mimp_issue_year ON {TABLE}(issue_code, year);
"""

BUILD = f"""
INSERT INTO {TABLE}
WITH registrant_issue_years AS (
  -- one row per (registrant, issue_code, year) — deduplicated
  SELECT DISTINCT
    sf.registrant_id,
    sf.filing_year    AS lobby_year,
    sla.general_issue_code AS issue_code
  FROM senate_filings sf
  JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
  WHERE sla.general_issue_code IS NOT NULL
    AND sf.filing_type IN ('Q1','Q2','Q3','Q4')
    AND sf.filing_year BETWEEN 2022 AND 2026
),
contrib_by_registrant_member_year AS (
  -- total FECA per (registrant, member bioguide, contribution year)
  SELECT
    scf.registrant_id,
    scf.filing_year     AS contrib_year,
    hmm.bioguide,
    SUM(sci.amount_num) AS feca_amt
  FROM senate_contribution_items sci
  JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
  JOIN honoree_member_map hmm ON hmm.honoree_name = sci.honoree_name
  WHERE hmm.confidence >= 0.9
    AND sci.contribution_type = 'feca'
    AND sci.amount_num > 0
    AND scf.filing_year BETWEEN 2022 AND 2026
  GROUP BY scf.registrant_id, scf.filing_year, hmm.bioguide
),
attributed AS (
  -- attribute each dollar to each issue code the registrant lobbied on that year
  SELECT
    cb.bioguide,
    riy.issue_code,
    cb.contrib_year AS year,
    cb.feca_amt
  FROM contrib_by_registrant_member_year cb
  JOIN registrant_issue_years riy
    ON riy.registrant_id = cb.registrant_id
    AND riy.lobby_year   = cb.contrib_year
)
SELECT
  a.bioguide,
  coalesce(mem.official_full, mem.first || ' ' || mem.last) AS member_name,
  mem.last_party AS party,
  mem.last_state AS state,
  a.issue_code,
  ri.name AS issue_name,
  a.year,
  SUM(a.feca_amt)             AS feca_total,
  COUNT(*)                    AS n_giving_registrants
FROM attributed a
JOIN members mem ON mem.bioguide = a.bioguide
JOIN ref_issue_codes ri ON ri.value = a.issue_code
GROUP BY a.bioguide, a.issue_code, a.year;
"""

VALIDATE = """
SELECT
  'rows'              AS metric, count(*)           AS value FROM derived_member_issue_money_panel UNION ALL
SELECT 'members',      count(DISTINCT bioguide)                FROM derived_member_issue_money_panel UNION ALL
SELECT 'issue_codes',  count(DISTINCT issue_code)              FROM derived_member_issue_money_panel UNION ALL
SELECT 'years',        count(DISTINCT year)                    FROM derived_member_issue_money_panel UNION ALL
SELECT 'total_feca_B', round(sum(feca_total)/1e9,3)            FROM derived_member_issue_money_panel;
"""

SPOT_CHECK = """
SELECT bioguide, member_name, issue_code, year, round(feca_total/1e3) as feca_k, n_giving_registrants
FROM derived_member_issue_money_panel
WHERE issue_code='HCR' AND year=2024
ORDER BY feca_total DESC LIMIT 10;
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA cache_size=-131072")  # 128 MB

    print(f"Building {TABLE}...")
    for stmt in DDL.strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)
    con.executescript(BUILD)
    con.commit()
    print("Done.")

    if args.validate:
        print("\n--- validation ---")
        for row in con.execute(VALIDATE):
            print(f"  {row[0]:<20} {row[1]}")
        print("\n--- spot check: HCR top recipients 2024 ---")
        for row in con.execute(SPOT_CHECK):
            print(f"  {row[0]} {row[1]:<30} {row[2]} {row[3]}  ${row[4]}k  ({row[5]} registrants)")

    con.close()


if __name__ == "__main__":
    main()
