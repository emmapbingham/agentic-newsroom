#!/usr/bin/env python3
"""Derived instrument: per-registrant income-deflation flags (Senate).

Mirror of derived_registrant_income_integrity (the LOC crank-check, which
flags income implausibly HIGH for scale). This flags the inverse: registrants
whose self-reported income is implausibly LOW for their scale -- heavy
lobbyist teams (>=5 lobbyists ever) reporting income-per-activity far below
the corpus norm (~$26,940/activity across all filings with parseable income).
A real firm running a large lobbying operation on a token reported income
would be under-reporting -- either structuring around disclosure, or another
data-quality artifact worth a manual read, same discipline as the crank-check.

IMPORTANT metric-design note (found the hard way, first build attempt):
income_per_activity MUST divide total_income by activities counted ONLY on
the filings that contributed to that income sum (act_on_income_filings), NOT
by all activities across every filing the registrant ever made. ~65% of this
corpus's filings carry no parseable income (known caveat, docs/*_db.md); a
registrant with many blank-income quarters and a few real ones will show a
mechanically deflated ratio if the denominator includes activities from the
blank quarters -- that is an artifact of sparse reporting, not evidence of
under-reporting. First build used the mismatched denominator and flagged
Kellen Company / Drummond Woodsum / Delta Development Group -- all small
government-relations shops whose clients (counties, townships, small
nonprofits) simply don't get parseable income on most quarters. Re-checked
with the coverage-matched denominator and all three dropped out entirely.

Grain: one row per registrant (registrant-level total income / activities on
income-bearing filings only, not a repeat-cluster like the crank-check --
deflation doesn't need a repeated-exact-amount signal, since consistently low
is itself the signal regardless of whether the amount varies quarter to
quarter).

    python scripts/build_derived_registrant_income_deflation.py
    python scripts/build_derived_registrant_income_deflation.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_registrant_income_deflation"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    registrant_id           INTEGER NOT NULL PRIMARY KEY,
    registrant_name         TEXT,
    n_clients               INTEGER NOT NULL,  -- distinct clients, this registrant, ever
    n_lobbyists             INTEGER NOT NULL,  -- distinct lobbyists, this registrant, ever
    n_filings_income        INTEGER NOT NULL,  -- filings with parseable income > 0
    total_income            REAL NOT NULL,
    act_on_income_filings   INTEGER NOT NULL,  -- activities, but ONLY on the filings summed into total_income
    income_per_activity     REAL,
    flag_reason             TEXT NOT NULL
);
"""

# Signal: registrant with a real lobbying team (>=5 lobbyists ever -- rules
# out solo shops, where a low income figure is unremarkable) and income that
# IS reported (>0, so this is deflation among reporters, not the separate
# missing-income question -- missingness in this corpus doesn't correlate
# with scale in the direction deflation would predict, see docs), but whose
# income-per-activity -- computed only over activities on the SAME filings
# that reported that income, see module docstring -- sits far below the
# corpus norm (~$26,940). Threshold <$3,000/activity is a >9x gap from norm.
# act_on_income_filings > 0 required: a registrant whose income-bearing
# filings link zero activities (e.g. DSD ADVISORS, LLC, first build attempt)
# has no valid ratio, not a deflated one -- excluded via NULLIF/HAVING.
BUILD = f"""
INSERT INTO {TABLE}
WITH registrant_scale AS (
  SELECT r.id AS registrant_id, r.name AS registrant_name,
    count(DISTINCT f.client_id) AS n_clients,
    count(DISTINCT al.lobbyist_id) AS n_lobbyists
  FROM senate_filings f
  JOIN senate_registrants r ON r.id = f.registrant_id
  LEFT JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
  LEFT JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id
  GROUP BY r.id
),
per_filing AS (
  SELECT f.filing_uuid, f.registrant_id, f.income_amt,
    count(DISTINCT a.activity_id) AS n_act
  FROM senate_filings f
  LEFT JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
  GROUP BY f.filing_uuid
),
registrant_income AS (
  SELECT registrant_id, SUM(income_amt) AS total_income, SUM(n_act) AS act_on_income_filings,
    count(*) AS n_filings_income
  FROM per_filing
  WHERE income_amt IS NOT NULL AND income_amt > 0
  GROUP BY registrant_id
  HAVING SUM(n_act) > 0
)
SELECT
  rs.registrant_id, rs.registrant_name, rs.n_clients, rs.n_lobbyists,
  ri.n_filings_income, ri.total_income, ri.act_on_income_filings,
  ROUND(ri.total_income / ri.act_on_income_filings, 2) AS income_per_activity,
  'income-per-activity < $3,000 (corpus norm ~$26,940) on a >=5-lobbyist registrant, ' ||
  'computed over activities on income-reporting filings only'
FROM registrant_scale rs
JOIN registrant_income ri ON ri.registrant_id = rs.registrant_id
WHERE rs.n_lobbyists >= 5
  AND (ri.total_income / ri.act_on_income_filings) < 3000;
"""

INDEXES = [
    f"CREATE INDEX idx_rideflate_ipa ON {TABLE}(income_per_activity);",
]


def build(con):
    con.executescript(DDL)
    con.execute(BUILD)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='registrant_income_deflation'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('registrant_income_deflation','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n} flagged registrants")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")
    rows = con.execute(
        f"SELECT registrant_name, n_clients, n_lobbyists, "
        f"n_filings_income, total_income, act_on_income_filings, income_per_activity FROM {TABLE} "
        f"ORDER BY income_per_activity ASC"
    ).fetchall()
    print(f"  {len(rows)} flagged registrants total")
    for row in rows:
        print(f"    {row}")

    corpus_norm = con.execute(
        "SELECT avg(income_amt / NULLIF(n_act,0)) FROM ("
        "  SELECT f.filing_uuid, f.income_amt, count(DISTINCT a.activity_id) AS n_act"
        "  FROM senate_filings f"
        "  LEFT JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid"
        "  WHERE f.income_amt IS NOT NULL AND f.income_amt > 0"
        "  GROUP BY f.filing_uuid"
        ")"
    ).fetchone()[0]
    print(f"  corpus-wide avg income_per_activity (filing-level) = {corpus_norm:.2f}")

    max_ipa = con.execute(f"SELECT max(income_per_activity) FROM {TABLE}").fetchone()[0]
    if max_ipa is not None and corpus_norm:
        ratio = corpus_norm / max_ipa
        print(f"  weakest flag income_per_activity={max_ipa}, corpus norm/flag ratio={ratio:.1f}x")
        check("every flagged registrant is >=5x below corpus norm", ratio >= 5)

    n_lobbyists_min = con.execute(f"SELECT min(n_lobbyists) FROM {TABLE}").fetchone()[0]
    check("scale floor respected (all flagged rows have >=5 lobbyists)",
          n_lobbyists_min is None or n_lobbyists_min >= 5)

    all_act_covered = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE act_on_income_filings IS NULL OR act_on_income_filings <= 0"
    ).fetchone()[0]
    check("no rows with zero/null activity denominator (mismatched-denominator bug from build 1)",
          all_act_covered == 0)

    known_false_positives = ('KELLEN COMPANY', 'DRUMMOND WOODSUM STRATEGIC CONSULTING LLC',
                              'DELTA DEVELOPMENT GROUP, INC.', 'DSD ADVISORS, LLC')
    fp_still_flagged = con.execute(
        f"SELECT registrant_name FROM {TABLE} WHERE registrant_name IN "
        f"({','.join('?' for _ in known_false_positives)})", known_false_positives
    ).fetchall()
    check("known denominator-mismatch false positives (small gov-relations shops with mostly "
          "blank-income filings) correctly excluded", len(fp_still_flagged) == 0)

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
