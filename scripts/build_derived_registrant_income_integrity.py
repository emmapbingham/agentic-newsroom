#!/usr/bin/env python3
"""Derived instrument: per-registrant income-plausibility flags (Senate + House).

Built to explain a specific artifact: "STATE OF LOC NATION GLOBAL PUBLIC
BENEFIT CORPORATION" (registrant LOC COMMUNITY ASSOCIATION) self-reported a
flat $20,000,000 income on every quarterly LDA filing in 2025 -- one client,
one lobbyist, ~100 low-content activities, filer self-titling "HH Empress
Queen Christina Clement" across amendments. The LDA has no income-plausibility
check at filing time, so nothing stops any registrant from typing an
arbitrary number in. That single filer's $20M distorted the Family/Abortion
(FAM) issue code's 2025 apportioned-income aggregate by roughly two-thirds
(see lead family-abortion-flat-lobbying-through-dobbs, corrected 2026-07-04).

This table flags Senate registrants whose scale (client count, lobbyist
count, activity count) is far too small to plausibly justify their reported
income, using a repeated-flat-income signal (the same income_amt reported on
>=3 filings -- one-off large filings are common and NOT flagged; a crank
signature is a number that never moves quarter to quarter regardless of
activity). Grain: one row per (registrant_id, income_amt) repeat-cluster.

    python scripts/build_derived_registrant_income_integrity.py
    python scripts/build_derived_registrant_income_integrity.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_registrant_income_integrity"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    registrant_id       INTEGER NOT NULL,
    registrant_name     TEXT,
    income_amt          REAL NOT NULL,
    n_filings_same_amt  INTEGER NOT NULL,  -- filings repeating this exact amount
    n_clients           INTEGER NOT NULL,  -- distinct clients, this registrant, ever
    n_lobbyists         INTEGER NOT NULL,  -- distinct lobbyists, this registrant, ever
    n_activities        INTEGER NOT NULL,  -- distinct activities, this registrant, ever
    income_per_activity REAL,
    flag_reason         TEXT NOT NULL,     -- why this row was surfaced
    PRIMARY KEY (registrant_id, income_amt)
);
"""

# Signal: an income figure repeated on >=3 filings (rules out one-off large
# but real contracts), for a registrant with <=2 clients and <=2 lobbyists
# ever (rules out real firms whose scale could justify large income), at
# >=$100k (rules out small legitimate flat-retainer solo shops, which cluster
# at $15k-$100k per the corpus's small-registrant income distribution).
BUILD = f"""
INSERT INTO {TABLE}
WITH registrant_scale AS (
  SELECT r.id AS registrant_id, r.name AS registrant_name,
    count(DISTINCT f.client_id) AS n_clients,
    count(DISTINCT al.lobbyist_id) AS n_lobbyists,
    count(DISTINCT a.activity_id) AS n_activities
  FROM senate_filings f
  JOIN senate_registrants r ON r.id = f.registrant_id
  LEFT JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
  LEFT JOIN senate_activity_lobbyists al ON al.activity_id = a.activity_id
  GROUP BY r.id
),
income_repeat AS (
  SELECT f.registrant_id, f.income_amt, count(*) AS n_filings_same_amt
  FROM senate_filings f
  WHERE f.income_amt IS NOT NULL AND f.income_amt > 0
  GROUP BY f.registrant_id, f.income_amt
  HAVING count(*) >= 3
)
SELECT
  rs.registrant_id, rs.registrant_name, ir.income_amt, ir.n_filings_same_amt,
  rs.n_clients, rs.n_lobbyists, rs.n_activities,
  ROUND(ir.income_amt / NULLIF(rs.n_activities, 0), 2) AS income_per_activity,
  'repeated flat income (n=' || ir.n_filings_same_amt || ') on a <=2-client/<=2-lobbyist registrant'
FROM income_repeat ir
JOIN registrant_scale rs ON rs.registrant_id = ir.registrant_id
WHERE rs.n_lobbyists <= 2 AND rs.n_clients <= 2 AND ir.income_amt >= 100000;
"""

INDEXES = [
    f"CREATE INDEX idx_riint_reg ON {TABLE}(registrant_id);",
    f"CREATE INDEX idx_riint_ipa ON {TABLE}(income_per_activity);",
]


def build(con):
    con.executescript(DDL)
    con.execute(BUILD)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='registrant_income_integrity'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('registrant_income_integrity','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n} flagged registrant-income clusters")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")
    rows = con.execute(
        f"SELECT registrant_name, income_amt, n_filings_same_amt, n_clients, "
        f"n_lobbyists, n_activities, income_per_activity FROM {TABLE} "
        f"ORDER BY income_per_activity DESC"
    ).fetchall()
    print(f"  {len(rows)} flagged registrant-income clusters total")
    for row in rows:
        print(f"    {row}")

    loc = con.execute(
        f"SELECT income_per_activity FROM {TABLE} WHERE registrant_name='LOC COMMUNITY ASSOCIATION'"
    ).fetchone()
    check("known crank (LOC COMMUNITY ASSOCIATION) is flagged", loc is not None)
    if loc:
        next_highest = con.execute(
            f"SELECT max(income_per_activity) FROM {TABLE} WHERE registrant_name != 'LOC COMMUNITY ASSOCIATION'"
        ).fetchone()[0]
        ratio = loc[0] / next_highest if next_highest else None
        print(f"  LOC income_per_activity={loc[0]}, next-highest={next_highest}, ratio={ratio}")
        check("LOC is a clear outlier (>=5x next-highest income_per_activity)",
              ratio is not None and ratio >= 5)

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
