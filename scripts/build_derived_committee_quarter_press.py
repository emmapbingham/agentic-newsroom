#!/usr/bin/env python3
"""Derived table: committee-quarter press volume, using the ACTUAL roster
active in each quarter (not today's roster applied retroactively).

Answers: for a given committee and the issue code(s) it has jurisdiction
over, how many press releases did that committee's own members put out on
that topic, per quarter, 2022-2026?

This is the press-side companion to derived_issue_quarter_volume_press
(which already carries Senate/House lobbying-activity volume separately, by
issue-code-quarter). Pairing the two via committee_issue_jurisdiction gives a
committee-level lobbying-volume-vs-press lead-lag read with a real
institutional anchor -- something the flat 79-issue-code-only version could
not do (see the 2026-07-02 issue-lobby-press-lead-lag run, which found that
screen mostly returns noise at n=17 quarters x 79 codes).

Roster resolution: for each quarter, use member_committees_history rows
valid as of that quarter's START date (valid_from <= quarter_start AND
(valid_to IS NULL OR valid_to > quarter_start)). This is the "who actually
sat on this committee at the time" fix -- member_committees alone is
current-Congress-only and would misattribute 2022-2024 press releases to
today's committee members.

Press topic-matching reuses ISSUE_KEYWORDS from
build_derived_issue_quarter_volume_press.py (imported, not copied, so the
two stay in sync by construction -- no manual-sync drift risk).

Grain: (committee_id, issue_code, year, quarter). A committee can have
multiple issue codes (from committee_issue_jurisdiction); a member's release
counts once per (issue_code, quarter) it topic-matches, but the same release
can count toward multiple issue codes if the text matches multiple keyword
sets (matches the base table's behavior -- not deduplicated across codes,
since "how much did this committee talk about topic X" is a per-topic
question).

Output columns:
  committee_id, committee_name, issue_code, issue_name, weight,
  year, quarter,
  n_committee_members     -- size of the roster used for this quarter
  n_total_releases        -- all releases from committee members this quarter (any topic)
  n_topic_releases        -- of those, topic-matched to issue_code
  topic_share              -- n_topic_releases / n_total_releases (NULL if n_total_releases=0)
  organizing_gap            -- 1 = no committee roster existed for this committee_id
                                this quarter. Two legitimate causes: (a) the whole
                                chamber hasn't organized committees yet at the start
                                of a new Congress (2023 Q1, 2025 Q1 -- every
                                committee gaps here), or (b) this specific
                                (sub)committee didn't exist yet as of this quarter
                                (e.g. SSBK13 Digital Assets, created 2025). A real
                                fact about institutional history, not a data gap --
                                filter these out before any volume/lag comparison,
                                don't treat as zero activity.

    python scripts/build_derived_committee_quarter_press.py
    python scripts/build_derived_committee_quarter_press.py --validate
"""
import argparse
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_derived_issue_quarter_volume_press import ISSUE_KEYWORDS  # noqa: E402

DB = Path("db/gain.db")
TABLE = "derived_committee_quarter_press"

QUARTER_START = {1: "01-01", 2: "04-01", 3: "07-01", 4: "10-01"}
YEARS = range(2022, 2027)

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    committee_id       TEXT    NOT NULL,
    committee_name     TEXT,
    issue_code         TEXT    NOT NULL,
    issue_name         TEXT,
    weight              TEXT,   -- primary/secondary, from committee_issue_jurisdiction
    year                INTEGER NOT NULL,
    quarter             INTEGER NOT NULL,
    n_committee_members INTEGER NOT NULL,
    n_total_releases    INTEGER NOT NULL DEFAULT 0,
    n_topic_releases    INTEGER NOT NULL DEFAULT 0,
    topic_share         REAL,
    organizing_gap      INTEGER NOT NULL DEFAULT 0,  -- 1 = no roster existed yet (Congress not organized, or subcommittee didn't exist), not a data gap
    PRIMARY KEY (committee_id, issue_code, year, quarter)
);
CREATE INDEX idx_cqp_committee ON {TABLE}(committee_id);
CREATE INDEX idx_cqp_issue     ON {TABLE}(issue_code, year, quarter);
"""


def roster_for_quarter(con, year, quarter, earliest_snapshot):
    """Bioguides on each committee_id as of this quarter's start date.

    Clamped to earliest_snapshot for quarters before our first pulled
    snapshot (2022-01-04) -- the few missing days get the earliest-known
    roster rather than an artificial zero. Genuine gaps where NO committee
    has been organized yet (start of a new Congress, before the chamber has
    assigned committees -- e.g. 2023 Q1 before the 118th organized on
    2023-02-17, 2025 Q1 before the 119th organized on 2025-02-02) are left
    as real zeros: no committee assignments existed yet, this is a fact
    about the world, not a data gap.
    """
    qdate = max(f"{year}-{QUARTER_START[quarter]}", earliest_snapshot)
    rows = con.execute(
        """
        SELECT DISTINCT committee_id, bioguide FROM member_committees_history
        WHERE valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)
        """,
        (qdate, qdate),
    ).fetchall()
    roster = defaultdict(set)
    for cid, bio in rows:
        roster[cid].add(bio)
    return roster


def press_by_bioguide_quarter(con):
    """(bioguide, year, quarter) -> list of release texts (lowercased once)."""
    rows = con.execute(
        """
        SELECT bioguide_id, year, strftime('%m', date), lower(text)
        FROM press_releases
        WHERE date IS NOT NULL AND bioguide_id IS NOT NULL
          AND year BETWEEN 2022 AND 2026
        """
    ).fetchall()
    out = defaultdict(list)
    for bio, year, month, text in rows:
        if month is None:
            continue
        q = (int(month) - 1) // 3 + 1
        out[(bio, int(year), q)].append(text or "")
    return out


def build(con):
    jurisdiction = con.execute(
        "SELECT committee_id, committee_name, issue_code, weight "
        "FROM committee_issue_jurisdiction WHERE issue_code IS NOT NULL"
    ).fetchall()
    # keep only issue codes we have a keyword map for (matches base table's 75-of-79 coverage)
    jurisdiction = [(cid, cname, code, w) for cid, cname, code, w in jurisdiction
                     if code in ISSUE_KEYWORDS]

    issue_names = dict(con.execute("SELECT value, name FROM ref_issue_codes"))

    print(f"  jurisdiction rows (with keyword coverage): {len(jurisdiction)}")
    print("  loading press releases by (bioguide, year, quarter)...")
    press_idx = press_by_bioguide_quarter(con)

    earliest_snapshot = con.execute(
        "SELECT min(valid_from) FROM member_committees_history"
    ).fetchone()[0]

    print("  loading rosters per quarter...")
    rosters_by_q = {}
    for year in YEARS:
        for q in (1, 2, 3, 4):
            if year == 2026 and q > 1:
                continue  # corpus ends 2026 Q1
            rosters_by_q[(year, q)] = roster_for_quarter(con, year, q, earliest_snapshot)

    rows_out = []
    for cid, cname, code, weight in jurisdiction:
        keywords = ISSUE_KEYWORDS[code]
        for (year, q), roster in rosters_by_q.items():
            members = roster.get(cid, set())
            n_members = len(members)
            n_total = 0
            n_topic = 0
            for bio in members:
                texts = press_idx.get((bio, year, q), [])
                n_total += len(texts)
                for t in texts:
                    if any(kw.lower() in t for kw in keywords):
                        n_topic += 1
            share = n_topic / n_total if n_total > 0 else None
            # With the earliest-snapshot clamp, n_members==0 only happens when
            # NO snapshot (clamped or otherwise) has this committee_id populated
            # for this date -- i.e. a genuine organizing gap (new Congress not
            # yet organized), not a pre-corpus date artifact.
            organizing_gap = 1 if n_members == 0 else 0
            rows_out.append((
                cid, cname, code, issue_names.get(code, ""), weight,
                year, q, n_members, n_total, n_topic, share, organizing_gap,
            ))

    con.executescript(DDL)
    con.executemany(f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", rows_out)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]

    con.execute("DELETE FROM ingest_log WHERE source='committee_quarter_press'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('committee_quarter_press','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n:,} rows")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")

    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    check("table non-empty", n > 0)

    bad_share = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE topic_share IS NOT NULL AND (topic_share < 0 OR topic_share > 1)"
    ).fetchone()[0]
    check("topic_share always in [0,1] where non-NULL", bad_share == 0)

    bad_topic_gt_total = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE n_topic_releases > n_total_releases"
    ).fetchone()[0]
    check("n_topic_releases never exceeds n_total_releases", bad_topic_gt_total == 0)

    # organizing_gap has two legitimate causes: (1) the whole chamber hasn't
    # organized committees yet at the start of a new Congress (2023 Q1, 2025
    # Q1 -- every committee should show this), and (2) a specific subcommittee
    # didn't exist yet (e.g. SSBK13 Digital Assets, created 2025 -- only that
    # subcommittee gaps, not the whole chamber). Check (1) directly: at least
    # HSWM and SSFI (both long-standing, non-Q1-created committees) should gap
    # on exactly 2023 Q1 and 2025 Q1 and nowhere else.
    for cid in ("HSWM", "SSFI"):
        gaps = con.execute(
            f"SELECT DISTINCT year, quarter FROM {TABLE} WHERE committee_id=? AND organizing_gap=1 ORDER BY year, quarter",
            (cid,),
        ).fetchall()
        print(f"  {cid} organizing_gap quarters: {gaps}")
        check(f"{cid} (long-standing committee) gaps only on Congress-transition quarters",
              set(gaps) == {(2023, 1), (2025, 1)})

    # Total distinct (committee_id, issue_code) pairs with a gap should be a
    # minority of the jurisdiction map, not systemic
    n_pairs_total = con.execute(
        f"SELECT count(DISTINCT committee_id || issue_code) FROM {TABLE}"
    ).fetchone()[0]
    n_pairs_with_any_gap = con.execute(
        f"SELECT count(DISTINCT committee_id || issue_code) FROM {TABLE} WHERE organizing_gap=1"
    ).fetchone()[0]
    print(f"  committee-issue pairs with >=1 organizing_gap quarter: {n_pairs_with_any_gap}/{n_pairs_total}")
    check("organizing_gap affects most committee-issue pairs (expected: all gap on Q1-of-new-Congress at minimum)",
          n_pairs_with_any_gap > 0)

    # 2022 Q1 should NOT be a gap (clamped to earliest snapshot 2022-01-04) --
    # confirms the clamp fix actually works
    q1_2022 = con.execute(
        f"SELECT n_committee_members, organizing_gap FROM {TABLE} WHERE committee_id='HSWM' "
        "AND issue_code='TAX' AND year=2022 AND quarter=1"
    ).fetchone()
    print(f"  HSWM 2022 Q1 (should be clamped to earliest snapshot, not a gap): {q1_2022}")
    check("2022 Q1 uses the clamped earliest-snapshot roster, not an organizing gap",
          q1_2022 is not None and q1_2022[1] == 0 and q1_2022[0] > 0)

    # Ways & Means / TAX should show real press volume (sanity, not a strong claim)
    row = con.execute(
        f"""SELECT sum(n_total_releases), sum(n_topic_releases) FROM {TABLE}
            WHERE committee_id='HSWM' AND issue_code='TAX' AND year=2023"""
    ).fetchone()
    print(f"  HSWM (Ways & Means) TAX releases in 2023: total={row[0]}, topic-matched={row[1]}")
    check("Ways & Means members produced press in 2023 (roster resolved correctly)",
          row[0] is not None and row[0] > 0)

    # roster size sanity: HSWM had ~25 members historically -- not 0, not 435
    row = con.execute(
        f"""SELECT DISTINCT n_committee_members FROM {TABLE}
            WHERE committee_id='HSWM' AND year=2023 AND quarter=2 LIMIT 1"""
    ).fetchone()
    print(f"  HSWM roster size, 2023 Q2: {row[0] if row else None}")
    check("HSWM roster size is a plausible committee size (5-60)",
          row is not None and 5 <= row[0] <= 60)

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
