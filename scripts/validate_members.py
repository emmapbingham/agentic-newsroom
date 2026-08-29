"""Validate the member crosswalk slice of db/gain.db and demonstrate the
now-closed money <-> member <-> press loop.

Usage: python scripts/validate_members.py [--db db/gain.db]
"""

import argparse
import sqlite3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    con.execute("PRAGMA foreign_keys = ON")
    q = lambda s: con.execute(s).fetchall()
    one = lambda s: con.execute(s).fetchone()[0]

    print(f"=== {args.db} (member crosswalk) ===\n")
    print("ROW COUNTS")
    for t in ("members", "member_terms", "committees", "member_committees",
              "honoree_member_map"):
        print(f"  {t:<22} {one(f'SELECT count(*) FROM {t}'):>10,}")
    print(f"  ... current members:  {one('SELECT count(*) FROM members WHERE is_current=1'):,}")

    print("\nREFERENTIAL INTEGRITY")
    fk = q("PRAGMA foreign_key_check")
    print(f"  !! {len(fk)} violations e.g. {fk[:3]}" if fk else "  OK — no orphan foreign keys")

    print("\nPRESS <-> CROSSWALK coverage")
    press_bio = one("SELECT count(DISTINCT bioguide_id) FROM press_releases WHERE bioguide_id IS NOT NULL")
    press_in_members = one("""SELECT count(DISTINCT p.bioguide_id) FROM press_releases p
                              JOIN members m ON m.bioguide=p.bioguide_id""")
    print(f"  press bioguides: {press_bio}; found in members: {press_in_members}")

    print("\nHONOREE RESOLUTION")
    tot = one("SELECT count(*) FROM honoree_member_map")
    matched = one("SELECT count(*) FROM honoree_member_map WHERE bioguide IS NOT NULL")
    print(f"  distinct honorees: {tot:,}; matched: {matched:,} ({100*matched/tot:.0f}%)")
    dollars = one("SELECT sum(amount_num) FROM senate_contribution_items WHERE honoree_name IS NOT NULL")
    dmatch = one("""SELECT sum(i.amount_num) FROM senate_contribution_items i
                    JOIN honoree_member_map m ON m.honoree_name=i.honoree_name
                    WHERE m.bioguide IS NOT NULL""")
    print(f"  $ to matched honorees: {100*dmatch/dollars:.0f}% (rest -> PACs/committees/non-members)")
    print("  methods:", dict(q("SELECT method, count(*) FROM honoree_member_map WHERE bioguide IS NOT NULL GROUP BY method")))

    print("\nCLOSED LOOP: top members by lobbyist/PAC contributions, with press volume + a committee")
    print("  (money via honoree_member_map -> bioguide -> press_releases / committees)")
    rows = q("""
        SELECT mem.official_full, mem.last_party, mem.last_state,
               round(sum(i.amount_num)) total_received,
               (SELECT count(*) FROM press_releases p WHERE p.bioguide_id=mem.bioguide) releases,
               (SELECT c.name FROM member_committees mc JOIN committees c ON c.committee_id=mc.committee_id
                WHERE mc.bioguide=mem.bioguide AND c.parent_committee_id IS NULL
                ORDER BY mc.rank LIMIT 1) a_committee
        FROM senate_contribution_items i
        JOIN honoree_member_map hm ON hm.honoree_name=i.honoree_name
        JOIN members mem ON mem.bioguide=hm.bioguide
        WHERE hm.confidence >= 0.9
        GROUP BY mem.bioguide ORDER BY total_received DESC LIMIT 12""")
    for full, party, st, total, rel, com in rows:
        print(f"  ${total:>10,.0f}  {full} ({party[:1]}-{st})  press={rel}  {com or ''}")
    con.close()


if __name__ == "__main__":
    main()
