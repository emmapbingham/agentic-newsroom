#!/usr/bin/env python3
"""Committee -> LDA issue-code jurisdiction map.

Hand-curated editorial judgment, NOT derived from congress-legislators or any
raw source. Source of truth is the checked-in CSV
investigations/reference/committee_issue_jurisdiction.csv; this script loads
it into db/gain.db as committee_issue_jurisdiction, validating every row
against the live committees and ref_issue_codes tables so a typo or a stale
committee_id fails loudly instead of silently dropping a row.

Depends on the `members` stage (committees, ref_issue_codes must exist first)
but is its own reference-tier stage -- re-running scripts/ingest_members.py
does NOT touch this table; re-run this script explicitly after editing the
CSV.

Coverage: all 42 top-level House + Senate committees are represented (either
mapped to issue code(s), or explicit weight='none' rows documenting why a
committee has no legislative-issue jurisdiction -- Ethics, Rules, House
Administration, investigative-only select committees). Subcommittee-level
rows exist only for the handful of committees spanning genuinely distinct
issue areas (Energy & Commerce, Financial Services/Banking, Finance,
Commerce/Science/Transportation, Energy & Natural Resources). Appropriations
subcommittees are spending-category, not issue-code aligned, and are
deliberately out of scope -- Appropriations maps to BUD at the full-committee
level only.

    python scripts/ingest_committee_jurisdiction.py
    python scripts/ingest_committee_jurisdiction.py --validate
"""
import argparse
import csv
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
CSV_PATH = Path("investigations/reference/committee_issue_jurisdiction.csv")
TABLE = "committee_issue_jurisdiction"
SOURCE = "committee_jurisdiction"
TIER = "reference"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    committee_id   TEXT NOT NULL REFERENCES committees(committee_id),
    committee_name TEXT,
    issue_code     TEXT REFERENCES ref_issue_codes(value),  -- NULL when weight='none'
    weight         TEXT NOT NULL CHECK (weight IN ('primary','secondary','none')),
    notes          TEXT
);
CREATE INDEX idx_cij_committee ON {TABLE}(committee_id);
CREATE INDEX idx_cij_issue     ON {TABLE}(issue_code);
"""


def load_rows():
    if not CSV_PATH.exists():
        sys.exit(f"{CSV_PATH} not found")
    with CSV_PATH.open() as f:
        return list(csv.DictReader(f))


def build(con):
    rows = load_rows()

    valid_committees = {r[0] for r in con.execute(
        "SELECT committee_id FROM committees WHERE type IN ('house','senate')")}
    valid_codes = {r[0] for r in con.execute("SELECT value FROM ref_issue_codes")}

    bad = []
    for i, row in enumerate(rows, start=2):  # +2: header row + 1-index
        cid, code = row["committee_id"].strip(), row["issue_code"].strip()
        if cid not in valid_committees:
            bad.append(f"line {i}: unknown committee_id {cid!r}")
        if code and code not in valid_codes:
            bad.append(f"line {i}: unknown issue_code {code!r}")
        if not code and row["weight"].strip() != "none":
            bad.append(f"line {i}: empty issue_code but weight != 'none' ({cid!r})")
    if bad:
        sys.exit("CSV validation failed:\n  " + "\n  ".join(bad))

    con.executescript(DDL)
    con.executemany(
        f"INSERT INTO {TABLE} (committee_id, committee_name, issue_code, weight, notes) "
        "VALUES (?,?,?,?,?)",
        [(r["committee_id"].strip(), r["committee_name"].strip(),
          r["issue_code"].strip() or None, r["weight"].strip(),
          r["notes"].strip() or None) for r in rows],
    )
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]

    con.execute("DELETE FROM ingest_log WHERE source=?", (SOURCE,))
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES (?,?,?,?,?,datetime('now'))",
        (SOURCE, TIER, str(CSV_PATH), TABLE, n),
    )
    con.commit()
    print(f"built {TABLE}: {n:,} rows from {CSV_PATH}")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    print("reconciliation:")

    n_full = con.execute(
        "SELECT count(*) FROM committees WHERE type IN ('house','senate') AND parent_committee_id IS NULL"
    ).fetchone()[0]
    n_mapped_full = con.execute(
        f"""SELECT count(DISTINCT c.committee_id) FROM committees c
            JOIN {TABLE} j ON j.committee_id = c.committee_id
            WHERE c.type IN ('house','senate') AND c.parent_committee_id IS NULL"""
    ).fetchone()[0]
    print(f"  full committees: {n_full}, represented in jurisdiction map: {n_mapped_full}")
    check("every full committee has at least one row (mapped or weight='none')", n_full == n_mapped_full)

    n_none = con.execute(f"SELECT count(*) FROM {TABLE} WHERE weight='none'").fetchone()[0]
    n_null_code_not_none = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE issue_code IS NULL AND weight != 'none'"
    ).fetchone()[0]
    print(f"  weight='none' (no legislative jurisdiction) rows: {n_none}")
    check("no row has a NULL issue_code without weight='none'", n_null_code_not_none == 0)

    dupes = con.execute(
        f"""SELECT committee_id, issue_code, count(*) c FROM {TABLE}
            WHERE issue_code IS NOT NULL GROUP BY committee_id, issue_code HAVING c > 1"""
    ).fetchall()
    print(f"  duplicate (committee, issue_code) pairs: {len(dupes)}")
    check("no duplicate (committee_id, issue_code) rows", len(dupes) == 0)

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
