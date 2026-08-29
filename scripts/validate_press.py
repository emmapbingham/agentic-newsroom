"""Validate the press-release slice of db/gain.db.

Reconciles press_releases against the raw JSONL record count, checks integrity,
and runs representative metadata + full-text queries.

Usage: python scripts/validate_press.py [--db db/gain.db] [--reconcile]
"""

import argparse
import sqlite3
from pathlib import Path

ROOT = Path("data/congress_press")


def raw_count():
    n = 0
    for fp in list(ROOT.glob("20[0-9][0-9]/*.jsonl")) + list(ROOT.glob("*.jsonl")):
        with open(fp) as f:
            n += sum(1 for line in f if line.strip())
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    ap.add_argument("--reconcile", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    q = lambda sql: con.execute(sql).fetchall()
    one = lambda sql: con.execute(sql).fetchone()[0]

    print(f"=== {args.db} (press slice) ===\n")
    print("ROW COUNTS")
    for t in [r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table' "
                              "AND name LIKE 'press_%' ORDER BY name")]:
        print(f"  {t:<28} {one(f'SELECT count(*) FROM {t}'):>10,}")

    print("\nREFERENTIAL INTEGRITY")
    fk = q("PRAGMA foreign_key_check")
    print(f"  !! {len(fk)} violations" if fk else "  OK — no orphan foreign keys")

    print("\nKEY SANITY")
    print(f"  distinct urls:        {one('SELECT count(DISTINCT url) FROM press_releases'):,}")
    print(f"  releases w/o bioguide:{one('SELECT count(*) FROM press_releases WHERE bioguide_id IS NULL'):>6,}")
    print(f"  releases w/o date:    {one('SELECT count(*) FROM press_releases WHERE date IS NULL'):>6,}")
    print(f"  date range:           {one('SELECT min(date) FROM press_releases')} .. {one('SELECT max(date) FROM press_releases')}")

    if args.reconcile:
        db_n = one("SELECT count(*) FROM press_releases")
        raw_n = raw_count()
        print(f"\nRECONCILIATION: db={db_n:,}  raw_lines={raw_n:,}  "
              f"{'OK' if db_n == raw_n else 'MISMATCH'}")

    print("\nBY CHAMBER / PARTY / YEAR")
    print("  chamber:", dict(q("SELECT chamber, count(*) FROM press_releases GROUP BY chamber")))
    print("  party:  ", dict(q("SELECT party, count(*) FROM press_releases GROUP BY party")))
    print("  year:   ", dict(q("SELECT year, count(*) FROM press_releases GROUP BY year ORDER BY year")))

    print("\nSPOT-CHECK: most prolific members (press roster)")
    for name, party, st, n in q("""SELECT name, party, state, n_releases FROM press_members
                                   ORDER BY n_releases DESC LIMIT 5"""):
        print(f"  {n:>5,}  {name} ({party}-{st})")

    print("\nSPOT-CHECK: FTS — releases mentioning 'pharmaceutical'")
    n = one("SELECT count(*) FROM press_fts WHERE press_fts MATCH 'pharmaceutical'")
    print(f"  matches: {n:,}")
    for title, dom in q("""SELECT p.title, p.domain FROM press_fts f
                           JOIN press_releases p ON p.release_id=f.release_id
                           WHERE press_fts MATCH 'pharmaceutical' LIMIT 3"""):
        print(f"    {dom}: {title[:70]}")

    con.close()


if __name__ == "__main__":
    main()
