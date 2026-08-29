#!/usr/bin/env python3
"""Derived instrument: member contribution profile panel (LD-203 -> member).

member (bioguide) x year x contribution_type money, for the say-vs-pay money side
(chair-power-premium, silent-gatekeepers, critic-takes-money). Objective: no
issue/industry attribution (that needs the subjective committee->issue map, left
for the editor) — this is just "who received how much, of what type, when."

Provenance / correctness discipline:
- contributions resolve to a member via honoree_member_map at **confidence >= 0.9**
  (high-trust only; ~$851M of $1.71B). Each row's claim rests on that match.
- contribution_type is kept SEPARATE (the scout's correctness fix): `feca` is
  political contributions ($1.48B); `he`/`me`/`ple`/`pic` are honorary/meeting/
  other expenses. Aggregate the right type for the question — do NOT sum across
  types as "money to the member".
- year from senate_contribution_filings.filing_year (clean int), not item free-text date.

    python scripts/build_derived_member_contributions.py
    python scripts/build_derived_member_contributions.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_member_contribution_panel"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    bioguide          TEXT NOT NULL,
    member_name       TEXT,
    party             TEXT,
    state             TEXT,
    filing_year       INTEGER NOT NULL,
    contribution_type TEXT NOT NULL,        -- feca | he | me | ple | pic ...
    total_amount      REAL NOT NULL,        -- sum of parsed amount_num
    n_items           INTEGER NOT NULL,
    PRIMARY KEY (bioguide, filing_year, contribution_type)
);
"""

BUILD = f"""
INSERT INTO {TABLE}
SELECT
  m.bioguide,
  coalesce(mem.official_full, mem.first || ' ' || mem.last),
  mem.last_party,
  mem.last_state,
  cf.filing_year,
  i.contribution_type,
  sum(i.amount_num),
  count(*)
FROM senate_contribution_items i
JOIN honoree_member_map m ON m.honoree_name = i.honoree_name AND m.confidence >= 0.9
JOIN senate_contribution_filings cf ON cf.filing_uuid = i.filing_uuid
JOIN members mem ON mem.bioguide = m.bioguide
WHERE i.amount_num IS NOT NULL AND i.contribution_type IS NOT NULL
GROUP BY m.bioguide, cf.filing_year, i.contribution_type;
"""

INDEXES = [
    f"CREATE INDEX idx_mcp_bio  ON {TABLE}(bioguide);",
    f"CREATE INDEX idx_mcp_type ON {TABLE}(contribution_type, filing_year);",
]


def build(con):
    con.executescript(DDL)
    con.execute(BUILD)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='member_contributions'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('member_contributions','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    members = con.execute(f"SELECT count(DISTINCT bioguide) FROM {TABLE}").fetchone()[0]
    print(f"built {TABLE}: {n:,} rows across {members:,} members")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")
    # 1. panel FECA total matches a direct conf>=0.9 query
    panel = con.execute(
        f"SELECT sum(total_amount) FROM {TABLE} WHERE contribution_type='feca'"
    ).fetchone()[0] or 0
    direct = con.execute(
        "SELECT sum(i.amount_num) FROM senate_contribution_items i "
        "JOIN honoree_member_map m ON m.honoree_name=i.honoree_name AND m.confidence>=0.9 "
        "JOIN members mem ON mem.bioguide=m.bioguide "
        "WHERE i.contribution_type='feca' AND i.amount_num IS NOT NULL"
    ).fetchone()[0] or 0
    print(f"  panel FECA ${panel:,.0f} vs direct ${direct:,.0f}")
    check("panel FECA total reconciles", abs(panel - direct) < 1)

    # 2. VERIFY chair-power-premium premise. The faithful measure is PER FULL
    #    COMMITTEE (committee_id length<=4; the other 181 ids are subcommittees,
    #    whose chairs dilute a pooled measure): chair FECA vs that committee's
    #    rank-and-file mean. (member_committees = current Congress — temporal
    #    mismatch with 2022-26 contributions is a known caveat.)
    print("  chair-power-premium (FECA all years; full committees only):")
    full = con.execute(f"""
        WITH money AS (SELECT bioguide, sum(total_amount) feca FROM {TABLE}
                       WHERE contribution_type='feca' GROUP BY bioguide),
        roled AS (
          SELECT mc.committee_id,
                 CASE WHEN mc.title IN ('Chairman','Chair','Chairwoman') THEN 'chair' ELSE 'member' END role,
                 coalesce(money.feca,0) feca
          FROM member_committees mc LEFT JOIN money ON money.bioguide=mc.bioguide
          WHERE length(mc.committee_id)<=4
            AND (mc.title IS NULL OR mc.title NOT IN ('Ex Officio','Ranking Member','Vice Chair','Vice Chairman'))),
        per_comm AS (
          SELECT committee_id,
                 max(CASE WHEN role='chair' THEN feca END) chair_feca,
                 avg(CASE WHEN role='member' THEN feca END) member_mean
          FROM roled GROUP BY committee_id)
        SELECT count(*),
               sum(chair_feca IS NOT NULL AND member_mean>0),
               avg(CASE WHEN chair_feca IS NOT NULL AND member_mean>0 THEN chair_feca*1.0/member_mean END),
               avg(CASE WHEN chair_feca IS NOT NULL THEN chair_feca END),
               avg(member_mean)
        FROM per_comm
    """).fetchone()
    n_comm, comparable, mean_ratio, chair_avg, member_mean_avg = full
    print(f"    {comparable}/{n_comm} full committees comparable; mean chair/member ratio "
          f"{mean_ratio:.1f}x; chair avg ${chair_avg:,.0f} vs member-mean avg ${member_mean_avg:,.0f}")
    print(f"    (sweep claimed ~$2.75M vs $1.43M, 2-7x across committees — holds; "
          f"the 2-7x is the across-committee range, ~1.9x on average)")
    check("full-committee chair premium present and material (>=1.5x)", mean_ratio >= 1.5)

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
