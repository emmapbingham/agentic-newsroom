#!/usr/bin/env python3
"""Historical committee-membership snapshots (Senate + House), built from git
history of unitedstates/congress-legislators' committee-membership-current.yaml.

WHY THIS EXISTS: member_committees (built by ingest_members.py) only carries
the CURRENT roster -- the upstream file is a live snapshot the project
scrapes and overwrites, with no separate historical-membership file. But the
press+lobbying corpus spans 2022-2026 Q1 (117th, 118th, 119th Congresses), so
using "current" committee assignments to attribute pre-2025 data would
misattribute members who changed committees between Congresses. The file's
GIT HISTORY, however, has real point-in-time snapshots going back to 2022 --
this script pulls ~18 of them (roughly every 2-3 months, at commit shas
pinned below) and builds a validity-windowed table.

Grain: one row per (bioguide, committee_id, valid_from). valid_to is the next
snapshot's date for that bioguide+committee (or NULL if still valid as of the
latest pulled snapshot). A member's assignment is treated as continuously
held between consecutive snapshots that both show it -- this is an
approximation (a mid-window swap is invisible) bounded by the ~2-3 month
snapshot spacing.

Source: pinned commit shas (not "main" -- exact reproducibility). Downloaded
to data/congress_legislators/history/<sha>.yaml, gitignored like the rest of
data/. Re-run with --refresh to re-download.

    python scripts/ingest_committee_history.py
    python scripts/ingest_committee_history.py --validate
"""
import argparse
import sqlite3
import sys
import urllib.request
from pathlib import Path

import yaml
try:
    Loader = yaml.CSafeLoader
except AttributeError:
    Loader = yaml.SafeLoader

DB = Path("db/gain.db")
DATA = Path("data/congress_legislators/history")
BASE = "https://raw.githubusercontent.com/unitedstates/congress-legislators"
TABLE = "member_committees_history"
SOURCE = "committee_history"
TIER = "reference"

# (commit sha, date) -- picked at ~2-3 month spacing across the corpus window,
# including snapshots right after both Congress transitions (118th: Jan 2023,
# 119th: Jan 2025). Pin shas for exact reproducibility.
SNAPSHOTS = [
    ("f0facbc3d24692e8c3c649becb0644621f7a6e46", "2022-01-04"),
    ("4744bf0a2522f8ffc0da29b2d422a4b979219469", "2022-06-22"),
    ("878dc077ee10624617a7839a449ca6bad21bd1ed", "2022-09-01"),
    ("5817772bd4aa6556f655de406f13aa7218a73e79", "2022-12-25"),
    ("c3b28a4c5a00c85eb29faf41da6dd04bbea868bd", "2023-02-17"),
    ("98e8dceb1a11f11efec77b616e6bc344d38e2233", "2023-06-06"),
    ("95cd8a7567360353479af71902241e6ed2ddbf2f", "2023-11-14"),
    ("4ce03d29fa876c573f9515a41c2e8c0e41591a38", "2024-03-06"),
    ("c22da268b57fe3a392a142674b78c5e7a21acb49", "2024-06-28"),
    ("ebd89d2a2fad695ee1ae38bc28f933c0b0065913", "2024-09-01"),
    ("ce2c4664703a734bf5f25e3861a9c90f62bd4bb5", "2024-12-28"),
    ("fb3faba275437c913033ff98d96c192290f537c4", "2025-02-02"),
    ("c56f57eba40dfa5b8fd0c15d2f2b7b6f59326191", "2025-04-04"),
    ("65259e46abc0b11f9e643f06a021b1d5dd5dbdc2", "2025-06-17"),
    ("5de69ba81bafaabf91c91adeddee44777ea09817", "2025-09-11"),
    ("c003379a48f8c7ac0b3370c87c0c1c4abaa4d572", "2025-11-14"),
    ("4db6613cb3108303c0fd8ac36e4c217082f2080b", "2026-02-03"),
    ("f1166e1120ec37987b27cf77923e7e113838571c", "2026-03-25"),
]

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    bioguide     TEXT NOT NULL,
    committee_id TEXT NOT NULL,
    side         TEXT,
    rank         INTEGER,
    title        TEXT,
    valid_from   TEXT NOT NULL,   -- snapshot date this assignment first observed
    valid_to     TEXT,            -- next snapshot date it was NOT observed; NULL = still valid as of latest pull
    source_sha   TEXT NOT NULL    -- commit this row's valid_from snapshot came from
);
CREATE INDEX idx_mch_bio  ON {TABLE}(bioguide);
CREATE INDEX idx_mch_com  ON {TABLE}(committee_id);
CREATE INDEX idx_mch_time ON {TABLE}(valid_from, valid_to);
"""


def download(refresh=False):
    DATA.mkdir(parents=True, exist_ok=True)
    for sha, date in SNAPSHOTS:
        dest = DATA / f"{date}_{sha[:10]}.yaml"
        if refresh or not dest.exists():
            url = f"{BASE}/{sha}/committee-membership-current.yaml"
            print(f"  downloading {date} ({sha[:10]}) ...", flush=True)
            urllib.request.urlretrieve(url, dest)


def load_snapshot(sha, date):
    dest = DATA / f"{date}_{sha[:10]}.yaml"
    with dest.open() as f:
        return yaml.load(f, Loader=Loader)


def build(con, refresh=False):
    download(refresh=refresh)

    valid_committee_ids = {r[0] for r in con.execute("SELECT committee_id FROM committees")}

    # membership_by_snapshot[date] = set of (bioguide, committee_id, side, rank, title)
    snapshots = []
    for sha, date in SNAPSHOTS:
        raw = load_snapshot(sha, date)
        rows = set()
        for cid, members in raw.items():
            if cid not in valid_committee_ids:
                continue  # subcommittee/committee renamed or not in our committees table
            for m in members:
                bio = m.get("bioguide")
                if not bio:
                    continue
                rows.add((bio, cid, m.get("party"), m.get("rank"), m.get("title")))
        snapshots.append((date, sha, rows))

    # Build validity windows: for each (bioguide, committee_id) track appears/disappears
    # across consecutive snapshots. A row's valid_from is the first snapshot it appears
    # in (after a gap or at the start); valid_to is the first subsequent snapshot date
    # it's absent, or NULL if present in the latest snapshot.
    out_rows = []
    seen_keys = {}  # (bio, cid) -> (side, rank, title, valid_from, source_sha)
    n_snapshots = len(snapshots)
    for i, (date, sha, rows) in enumerate(snapshots):
        current_keys = {(bio, cid): (side, rank, title) for bio, cid, side, rank, title in rows}
        # close out any open assignment not present this snapshot
        for key in list(seen_keys):
            if key not in current_keys:
                side, rank, title, valid_from, source_sha = seen_keys.pop(key)
                out_rows.append((key[0], key[1], side, rank, title, valid_from, date, source_sha))
        # open new assignments (or continue existing ones -- no-op if already open)
        for key, (side, rank, title) in current_keys.items():
            if key not in seen_keys:
                seen_keys[key] = (side, rank, title, date, sha)
        if i == n_snapshots - 1:
            # final snapshot: close all remaining as still-valid (valid_to=NULL)
            for key, (side, rank, title, valid_from, source_sha) in seen_keys.items():
                out_rows.append((key[0], key[1], side, rank, title, valid_from, None, source_sha))

    con.executescript(DDL)
    con.executemany(
        f"INSERT INTO {TABLE} VALUES (?,?,?,?,?,?,?,?)", out_rows
    )
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]

    con.execute("DELETE FROM ingest_log WHERE source=?", (SOURCE,))
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES (?,?,?,?,?,datetime('now'))",
        (SOURCE, TIER, f"{len(SNAPSHOTS)} pinned commit snapshots", TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n:,} rows from {len(SNAPSHOTS)} snapshots "
          f"({SNAPSHOTS[0][1]} .. {SNAPSHOTS[-1][1]})")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")

    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    check("table non-empty", n > 0)

    # Ways & Means chair at 118th-Congress-era snapshot should be Jason Smith
    # (verified fact used elsewhere in this corpus -- ways-means-chair-money-magnet case)
    row = con.execute(
        f"SELECT bioguide, title FROM {TABLE} WHERE committee_id='HSWM' "
        "AND valid_from <= '2023-06-01' AND (valid_to IS NULL OR valid_to > '2023-06-01') "
        "AND title='Chair'"
    ).fetchone()
    print(f"  HSWM chair as of 2023-06-01: {row}")
    check("HSWM had a recorded chair in 2023 (118th Congress)", row is not None)

    # current snapshot's committee assignment count should roughly match member_committees
    # (the current-only table built by ingest_members.py) -- not identical (different
    # pull dates) but same order of magnitude
    n_current_history = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE valid_to IS NULL"
    ).fetchone()[0]
    n_member_committees = con.execute("SELECT count(*) FROM member_committees").fetchone()[0]
    print(f"  still-valid history rows: {n_current_history}, member_committees (current): {n_member_committees}")
    ratio = n_current_history / n_member_committees if n_member_committees else 0
    check("still-valid history count is same order of magnitude as member_committees",
          0.5 < ratio < 2.0)

    # spot check: a member's committee set changes between 118th and 119th snapshots
    # for SOMEONE (proves this isn't just a static unchanged file)
    changed = con.execute(f"""
        SELECT count(DISTINCT bioguide) FROM (
          SELECT bioguide, committee_id FROM {TABLE} WHERE valid_from='2023-02-17'
          EXCEPT
          SELECT bioguide, committee_id FROM {TABLE} WHERE valid_from='2025-02-02' OR
            (valid_from < '2025-02-02' AND (valid_to IS NULL OR valid_to > '2025-02-02'))
        )
    """).fetchone()[0]
    print(f"  members with a 2023-02 committee assignment absent by 2025-02: {changed}")
    check("committee rosters genuinely differ between 118th and 119th snapshots", changed > 50)

    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="re-download snapshots")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)
    try:
        if args.validate:
            sys.exit(0 if validate(con) else 1)
        build(con, refresh=args.refresh)
    finally:
        con.close()


if __name__ == "__main__":
    main()
