"""Validate the House LDA slice of db/gain.db.

Reconciles house_filings against the XML files on disk (flagging any that failed
to parse), checks referential integrity, characterizes the Senate<->House bridge
built from the parsed senateID, and runs representative cross-source joins.

Usage: python scripts/validate_house.py [--db db/gain.db]
"""

import argparse
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

HOUSE = Path("data/house")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    ap.add_argument("--find-unparsed", action="store_true",
                    help="scan disk to list XML files missing from the DB")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    q = lambda sql: con.execute(sql).fetchall()
    one = lambda sql: con.execute(sql).fetchone()[0]

    print(f"=== {args.db} (House slice) ===\n")

    print("ROW COUNTS")
    for t in [r[0] for r in q("SELECT name FROM sqlite_master WHERE type='table' "
                              "AND name LIKE 'house_%' ORDER BY name")]:
        print(f"  {t:<32} {one(f'SELECT count(*) FROM {t}'):>12,}")

    print("\nREFERENTIAL INTEGRITY (foreign_key_check — expect empty)")
    fk = q("PRAGMA foreign_key_check")
    print(f"  !! {len(fk)} violations, e.g. {fk[:5]}" if fk else "  OK — no orphan foreign keys")

    print("\nRECONCILIATION vs files on disk")
    n_files = sum(1 for _ in HOUSE.glob("*/*.xml"))
    n_db = one("SELECT count(*) FROM house_filings")
    print(f"  .xml files on disk: {n_files:,}")
    print(f"  house_filings rows: {n_db:,}")
    print(f"  unparsed/missing:   {n_files - n_db:,}")

    print("\nDOC TYPE / PERIOD")
    for dt, n in q("SELECT doc_type, count(*) FROM house_filings GROUP BY doc_type"):
        print(f"  {dt}: {n:,}")
    print("  by year/period:", dict(q("SELECT filing_year||'-'||filing_period, count(*) "
                                       "FROM house_filings GROUP BY 1 ORDER BY 1")))

    print("\nSENATE<->HOUSE BRIDGE (via parsed senateID prefix)")
    with_sid = one("SELECT count(*) FROM house_filings WHERE senate_registrant_id IS NOT NULL")
    matched = one("""SELECT count(*) FROM house_filings h
                     WHERE EXISTS (SELECT 1 FROM senate_registrants r
                                   WHERE r.id = h.senate_registrant_id)""")
    print(f"  house_filings with parsed senate_registrant_id: {with_sid:,}")
    print(f"  ... that match a senate_registrants.id:         {matched:,} "
          f"({100*matched/max(with_sid,1):.1f}%)")
    bridged_regs = one("""SELECT count(DISTINCT h.senate_registrant_id) FROM house_filings h
                          JOIN senate_registrants r ON r.id = h.senate_registrant_id""")
    print(f"  distinct registrants present in BOTH chambers:  {bridged_regs:,}")

    print("\nSPOT-CHECK: registrants filing in both chambers (by House filing count)")
    for name, n in q("""SELECT r.name, count(*) n FROM house_filings h
                        JOIN senate_registrants r ON r.id = h.senate_registrant_id
                        GROUP BY r.id ORDER BY n DESC LIMIT 5"""):
        print(f"  {n:>6,}  {name}")

    print("\nSPOT-CHECK: House revolving-door covered positions")
    for pos, n in q("""SELECT covered_position, count(*) n FROM house_filing_lobbyists
                       WHERE covered_position IS NOT NULL
                       GROUP BY covered_position ORDER BY n DESC LIMIT 5"""):
        print(f"  {n:>6,}  {pos[:68]}")

    print("\nSPOT-CHECK: House FTS — activities mentioning 'cryptocurrency'")
    n = one("""SELECT count(*) FROM house_activities_fts
               WHERE house_activities_fts MATCH 'cryptocurrency'""")
    print(f"  matches: {n:,}")

    if args.find_unparsed:
        print("\nUNPARSED FILES (scanning disk; this is slow)")
        db_ids = {r[0] for r in q("SELECT house_filing_id FROM house_filings")}
        for fp in HOUSE.glob("*/*.xml"):
            if fp.stem not in db_ids:
                try:
                    ET.parse(fp)
                    reason = "MISSING (parses OK!)"
                except ET.ParseError as e:
                    reason = f"ParseError: {e}"
                print(f"  {fp}  -> {reason}")

    con.close()


if __name__ == "__main__":
    main()
