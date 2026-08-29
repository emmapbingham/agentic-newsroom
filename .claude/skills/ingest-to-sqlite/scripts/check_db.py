"""Verify a freshly-built SQLite database — the validation half of a verifiable
ingestion. Runs integrity + referential-integrity checks, prints every table's
row count, and (with --expect) reconciles counts against the numbers you got
from the raw source, so "it loaded" becomes "it loaded correctly and completely".

Stdlib only. Examples:
    python check_db.py db/gain.db
    python check_db.py db/gain.db --expect senate_filings=418098 press_releases=141332
"""

import argparse
import sqlite3
import sys


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("db")
    ap.add_argument("--expect", nargs="*", default=[],
                    help="table=count assertions, e.g. senate_filings=418098")
    ap.add_argument("--like", default="%", help="only show tables matching this LIKE pattern")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    ok = True

    print(f"=== {args.db} ===\n")

    print("INTEGRITY")
    quick = con.execute("PRAGMA quick_check").fetchone()[0]
    print(f"  quick_check: {quick}")
    ok &= quick == "ok"
    fk = con.execute("PRAGMA foreign_key_check").fetchall()
    print(f"  foreign_key_check: {'OK — no orphans' if not fk else f'{len(fk)} VIOLATIONS e.g. {fk[:5]}'}")
    ok &= not fk

    print("\nROW COUNTS")
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' "
        "AND name LIKE ? ORDER BY name", (args.like,))]
    for t in tables:
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"  {t:<36} {n:>12,}")

    if args.expect:
        print("\nRECONCILIATION (db vs expected)")
        for pair in args.expect:
            table, _, want = pair.partition("=")
            if not table or not want.isdigit():
                ok = False
                print(f"  {pair:<36} MALFORMED (use table=count, e.g. filings=418098)")
                continue
            exists = con.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ).fetchone()
            if not exists:
                ok = False
                print(f"  {table:<36} NO SUCH TABLE (have: {', '.join(tables[:8])}"
                      f"{', ...' if len(tables) > 8 else ''})")
                continue
            got = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            match = got == int(want)
            ok &= match
            print(f"  {table:<36} db={got:,} expected={int(want):,}  "
                  f"{'OK' if match else 'MISMATCH'}")

    con.close()
    print(f"\n{'ALL CHECKS PASSED' if ok else 'CHECKS FAILED'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
