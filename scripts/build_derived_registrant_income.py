#!/usr/bin/env python3
"""Derived instrument: registrant income panel (Senate).

registrant x filing_year x quarter income time-series, for spotting income
surges (e.g. the 2025 transition lead). Senate-only: Senate income is the clean
column; House income is sparse and reported differently.

THE DEDUP DISCIPLINE (learned at cost — see the $118M duplicate episode):
income is reported per filing (registrant-client-period). The same client-period
can carry an original quarterly, an amendment, and accidental duplicates. Summing
them double-counts. So we first reduce to ONE canonical filing per
(registrant, client, year, quarter) = the latest-posted (max dt_posted, then max
uuid) — which supersedes duplicates AND adopts amendment values — then sum across
clients per registrant-quarter.

Caveats baked in: latest-posted means a retroactive amendment that NULLs income
(cf. the retroactive-income-zeroing lead) correctly removes it from the series.
~65% of filings carry parsed income; quarters are the 4 Senate filing_periods.

    python scripts/build_derived_registrant_income.py
    python scripts/build_derived_registrant_income.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_registrant_income_panel"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    registrant_id   INTEGER NOT NULL,
    registrant_name TEXT,
    filing_year     INTEGER NOT NULL,
    quarter         TEXT    NOT NULL,        -- Q1..Q4
    n_clients       INTEGER NOT NULL,        -- distinct canonical client engagements
    n_with_income   INTEGER NOT NULL,        -- of those, how many carry parsed income
    income_sum      REAL,                    -- deduped: latest-posted per engagement
    PRIMARY KEY (registrant_id, filing_year, quarter)
);
"""

# One canonical filing per (registrant, client, year, quarter): latest-posted.
BUILD = f"""
INSERT INTO {TABLE}
WITH canon AS (
  SELECT f.registrant_id, f.client_id, f.filing_year, f.filing_period,
         f.income_amt,
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
  c.filing_year,
  CASE c.filing_period
    WHEN 'first_quarter' THEN 'Q1' WHEN 'second_quarter' THEN 'Q2'
    WHEN 'third_quarter' THEN 'Q3' WHEN 'fourth_quarter' THEN 'Q4' END,
  count(*),
  sum(c.income_amt IS NOT NULL),
  sum(c.income_amt)
FROM canon c
LEFT JOIN senate_registrants r ON r.id = c.registrant_id
WHERE c.rn = 1
GROUP BY c.registrant_id, c.filing_year, c.filing_period;
"""

INDEXES = [
    f"CREATE INDEX idx_rip_reg  ON {TABLE}(registrant_id);",
    f"CREATE INDEX idx_rip_time ON {TABLE}(filing_year, quarter);",
]


def build(con):
    con.executescript(DDL)
    con.execute(BUILD)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='registrant_income'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('registrant_income','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n:,} registrant-quarters")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")
    # 1. deduped income must be <= raw income sum (dedup only removes rows)
    panel = con.execute(f"SELECT sum(income_sum) FROM {TABLE}").fetchone()[0] or 0
    raw = con.execute(
        "SELECT sum(income_amt) FROM senate_filings WHERE filing_period IN "
        "('first_quarter','second_quarter','third_quarter','fourth_quarter')"
    ).fetchone()[0] or 0
    print(f"  panel income ${panel:,.0f} vs raw (incl dupes/amends) ${raw:,.0f} "
          f"-> removed ${raw-panel:,.0f} ({100*(raw-panel)/raw:.1f}%)")
    check("deduped income <= raw", panel <= raw)
    check("dedup removed something but not most (<25%)", 0 < (raw - panel) < 0.25 * raw)

    # 2. VERIFY THE TRANSITION-LEAD PREMISE (do not assume the scout's numbers).
    #    Report each named firm's Q4-2024 -> Q1-2025 income change.
    print("  transition-surge premise (Q4-2024 -> Q1-2025 income):")
    for like in ("BALLARD PARTNERS%", "MILLER STRATEGIES%", "CONTINENTAL STRATEGY%"):
        rows = dict(con.execute(
            f"SELECT filing_year||quarter, income_sum FROM {TABLE} t "
            "JOIN senate_registrants r ON r.id=t.registrant_id "
            "WHERE r.name LIKE ? AND ((filing_year=2024 AND quarter='Q4') OR "
            "(filing_year=2025 AND quarter='Q1'))", (like,)).fetchall())
        q4, q1 = rows.get("2024Q4"), rows.get("2025Q1")
        if q4 and q1:
            pct = 100 * (q1 - q4) / q4
            print(f"    {like[:24]:24s} ${q4:>11,.0f} -> ${q1:>11,.0f}  ({pct:+.0f}%)")
        else:
            print(f"    {like[:24]:24s} insufficient data (q4={q4}, q1={q1})")

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
