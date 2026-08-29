"""Validate a built Senate SQLite database.

Checks referential integrity (no orphan FKs), reconciles row counts against the
raw JSON record counts, and runs representative investigative joins to confirm
the data is queryable end-to-end.

Usage: python scripts/validate_senate.py [--db db/senate.db]
"""

import argparse
import json
import sqlite3
from pathlib import Path

DATA = Path("data/senate")


def raw_counts():
    """Distinct-uuid counts straight from the JSON, for reconciliation."""
    f = c = 0
    for y in sorted(p.name for p in DATA.iterdir() if p.is_dir() and p.name.isdigit()):
        fp = DATA / y / "filings" / f"filings_{y}.json"
        if fp.exists():
            f += len({r["filing_uuid"] for r in json.load(open(fp))})
        cp = DATA / y / "contributions" / f"contributions_{y}.json"
        if cp.exists():
            c += len({r["filing_uuid"] for r in json.load(open(cp))})
    return f, c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    ap.add_argument("--reconcile", action="store_true",
                    help="re-read raw JSON to reconcile counts (slow)")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    q = lambda sql: con.execute(sql).fetchall()
    one = lambda sql: con.execute(sql).fetchone()[0]

    print(f"=== {args.db} ===\n")

    print("ROW COUNTS (senate_* and shared ref_*/ingest_log)")
    tables = [r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table' "
                              "AND name NOT LIKE 'sqlite_%' "
                              "AND (name LIKE 'senate_%' OR name LIKE 'ref_%' "
                              "     OR name='ingest_log') ORDER BY name")]
    for t in tables:
        print(f"  {t:<36} {one(f'SELECT count(*) FROM {t}'):>12,}")

    print("\nREFERENTIAL INTEGRITY (foreign_key_check — expect empty)")
    fk = q("PRAGMA foreign_key_check")
    if fk:
        print(f"  !! {len(fk)} FK violations, e.g. {fk[:5]}")
    else:
        print("  OK — no orphan foreign keys")

    print("\nNULL/KEY SANITY")
    print(f"  filings w/o registrant: {one('SELECT count(*) FROM senate_filings WHERE registrant_id IS NULL')}")
    print(f"  filings w/o client:     {one('SELECT count(*) FROM senate_filings WHERE client_id IS NULL')}")
    print(f"  activities w/o issue:   {one('SELECT count(*) FROM senate_lobbying_activities WHERE general_issue_code IS NULL')}")
    print(f"  filings w/ income_amt:  {one('SELECT count(*) FROM senate_filings WHERE income_amt IS NOT NULL')}")

    if args.reconcile:
        print("\nRECONCILIATION vs raw JSON (distinct uuids)")
        rf, rc = raw_counts()
        df = one("SELECT count(*) FROM senate_filings")
        dc = one("SELECT count(*) FROM senate_contribution_filings")
        print(f"  filings:       db={df:,}  raw_distinct={rf:,}  {'OK' if df==rf else 'MISMATCH'}")
        print(f"  contributions: db={dc:,}  raw_distinct={rc:,}  {'OK' if dc==rc else 'MISMATCH'}")

    print("\nSPOT-CHECK: top 5 registrants by filing count")
    for name, n in q("""SELECT r.name, count(*) n FROM senate_filings f
                        JOIN senate_registrants r ON r.id=f.registrant_id
                        GROUP BY f.registrant_id ORDER BY n DESC LIMIT 5"""):
        print(f"  {n:>6,}  {name}")

    print("\nSPOT-CHECK: revolving door — most common covered positions")
    for pos, n in q("""SELECT covered_position, count(*) n FROM senate_activity_lobbyists
                       WHERE covered_position IS NOT NULL
                       GROUP BY covered_position ORDER BY n DESC LIMIT 5"""):
        print(f"  {n:>6,}  {pos[:70]}")

    print("\nSPOT-CHECK: top contribution honorees by total $")
    for honoree, total in q("""SELECT honoree_name, sum(amount_num) t FROM senate_contribution_items
                               WHERE honoree_name IS NOT NULL
                               GROUP BY honoree_name ORDER BY t DESC LIMIT 5"""):
        print(f"  ${total:>14,.0f}  {honoree}")

    print("\nSPOT-CHECK: FTS — activities mentioning 'artificial intelligence'")
    rows = q("""SELECT count(*) FROM senate_activities_fts
                WHERE senate_activities_fts MATCH '\"artificial intelligence\"'""")
    print(f"  matches: {rows[0][0]:,}")
    sample = q("""SELECT a.description FROM senate_activities_fts fts
                  JOIN senate_lobbying_activities a ON a.activity_id=fts.activity_id
                  WHERE senate_activities_fts MATCH '\"artificial intelligence\"' LIMIT 2""")
    for (d,) in sample:
        print(f"    e.g. {d[:90]}")

    con.close()


if __name__ == "__main__":
    main()
