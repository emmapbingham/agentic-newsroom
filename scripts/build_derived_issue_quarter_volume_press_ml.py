#!/usr/bin/env python3
"""Derived table: per-issue-code per-quarter lobbying volume and press release
volume, press volume sourced from the ML classifier instead of ISSUE_KEYWORDS.

Same grain/shape as derived_issue_quarter_volume_press (the `_ml` suffix
means METHOD, not VERSION -- see
docs/press-issue-classifier.md's "Naming /
coexistence architecture" section). Both tables coexist; neither replaces
the other. Activities/income computation is copied verbatim from
build_derived_issue_quarter_volume_press.py -- only the press-volume source
differs (derived_press_issue_labels, scored by
scripts/press_topic_classifier.py's M0 model, threshold 0.3, instead of a
LIKE-based ISSUE_KEYWORDS sweep).

KNOWN LIMITATION, confirmed empirically (see
investigations/insurance-jurisdiction-no-press-lift/evidence.md E6): on INS,
M0 recalls only 16.2% of the narrow ISSUE_KEYWORDS match set and 25.6% of
unambiguous industry-specific content, while independently introducing an
ACA/health-insurance false-positive mode. This is not assumed to be INS-
specific -- treat every code's M0-based press count in this table as a
DIFFERENT, not necessarily BETTER, measurement than the keyword-based one.
Per the hard rule in the plan doc, no count from this table may be cited as
a standalone quantitative finding without a human read-through of the
underlying flagged releases.

Used by screens:
  - quiet-issue-quadrant-ml (ML-classifier sibling of quiet-issue-quadrant)

    python scripts/build_derived_issue_quarter_volume_press_ml.py
    python scripts/build_derived_issue_quarter_volume_press_ml.py --validate
"""
import argparse
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

DB = Path("db/gain.db")
TABLE = "derived_issue_quarter_volume_press_ml"

SENATE_QUARTERLY = ("Q1", "Q2", "Q3", "Q4", "1", "2", "3", "4")
HOUSE_QUARTERLY = ("Q1", "Q2", "Q3", "Q4")


def build_ddl(table: str) -> str:
    return f"""
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
    issue_code                  TEXT    NOT NULL,
    issue_name                  TEXT,
    year                        INTEGER NOT NULL,
    quarter                     INTEGER NOT NULL,
    senate_activities           INTEGER NOT NULL DEFAULT 0,
    house_activities            INTEGER NOT NULL DEFAULT 0,
    total_activities            INTEGER NOT NULL DEFAULT 0,
    senate_income_apportioned   REAL    NOT NULL DEFAULT 0.0,
    house_income_apportioned    REAL    NOT NULL DEFAULT 0.0,
    total_income_apportioned    REAL    NOT NULL DEFAULT 0.0,
    n_press_releases            INTEGER NOT NULL DEFAULT 0,
    lobby_per_press             REAL,
    PRIMARY KEY (issue_code, year, quarter)
);
CREATE INDEX IF NOT EXISTS idx_iqvpml_code ON {table}(issue_code);
CREATE INDEX IF NOT EXISTS idx_iqvpml_year_qtr ON {table}(year, quarter);
"""


def period_to_quarter(period: str) -> Optional[int]:
    p = (period or "").strip().upper()
    mapping = {"1": 1, "2": 2, "3": 3, "4": 4,
               "Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4,
               "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
               "FIRST_QUARTER": 1, "SECOND_QUARTER": 2,
               "THIRD_QUARTER": 3, "FOURTH_QUARTER": 4}
    return mapping.get(p)


def month_to_quarter(month_str: str) -> int:
    m = int(month_str)
    return (m - 1) // 3 + 1


def compute_senate(con: sqlite3.Connection) -> tuple[dict[tuple, int], dict[tuple, float]]:
    activity_counts: dict[tuple, int] = defaultdict(int)
    apportioned_income: dict[tuple, float] = defaultdict(float)

    filing_code_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    filing_meta: dict[str, tuple[int, int, float]] = {}

    rows = con.execute("""
        SELECT sf.filing_uuid, sf.filing_year, sf.filing_period,
               sf.income_amt,
               sla.general_issue_code
        FROM senate_filings sf
        JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
        WHERE sf.filing_year BETWEEN 2022 AND 2026
          AND sf.filing_period IN (
            'first_quarter','second_quarter','third_quarter','fourth_quarter',
            'Q1','Q2','Q3','Q4','1','2','3','4'
          )
          AND sf.income_amt > 0
          AND sla.general_issue_code IS NOT NULL
    """)
    for uuid, year, period, income, code in rows:
        q = period_to_quarter(period)
        if q is None:
            continue
        filing_code_counts[uuid][code] += 1
        filing_meta[uuid] = (int(year), q, float(income))

    for uuid, code_counts in filing_code_counts.items():
        if uuid not in filing_meta:
            continue
        year, quarter, income = filing_meta[uuid]
        n_codes = len(code_counts)
        share = income / n_codes if n_codes > 0 else 0.0
        for code, n_acts in code_counts.items():
            key = (code, year, quarter)
            activity_counts[key] += n_acts
            apportioned_income[key] += share

    return dict(activity_counts), dict(apportioned_income)


def compute_house(con: sqlite3.Connection) -> tuple[dict[tuple, int], dict[tuple, float]]:
    activity_counts: dict[tuple, int] = defaultdict(int)
    apportioned_income: dict[tuple, float] = defaultdict(float)

    filing_code_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    filing_meta: dict[str, tuple[int, int, float]] = {}

    rows = con.execute("""
        SELECT hf.house_filing_id, hf.filing_year, hf.report_type,
               hf.income_amt,
               ha.issue_area_code
        FROM house_filings hf
        JOIN house_activities ha ON ha.house_filing_id = hf.house_filing_id
        WHERE hf.filing_year BETWEEN 2022 AND 2026
          AND hf.report_type IN ('Q1','Q2','Q3','Q4')
          AND hf.income_amt > 0
          AND ha.issue_area_code IS NOT NULL
    """)
    for fid, year, period, income, code in rows:
        q = period_to_quarter(period)
        if q is None:
            continue
        filing_code_counts[fid][code] += 1
        filing_meta[fid] = (int(year), q, float(income))

    for fid, code_counts in filing_code_counts.items():
        if fid not in filing_meta:
            continue
        year, quarter, income = filing_meta[fid]
        n_codes = len(code_counts)
        share = income / n_codes if n_codes > 0 else 0.0
        for code, n_acts in code_counts.items():
            key = (code, year, quarter)
            activity_counts[key] += n_acts
            apportioned_income[key] += share

    return dict(activity_counts), dict(apportioned_income)


def compute_press_ml(con: sqlite3.Connection) -> dict[tuple, int]:
    """Press release counts per issue-code-quarter, from the ML classifier's
    derived_press_issue_labels (probability >= 0.3, threshold set at build
    time -- see scripts/build_derived_press_issue_labels.py) instead of
    ISSUE_KEYWORDS. A release counts once per issue_code it was labeled
    with (multi-label; a release can count toward more than one code, same
    multi-count semantics as the keyword version)."""
    press: dict[tuple, int] = defaultdict(int)

    rows = con.execute("""
        SELECT l.issue_code, p.year, strftime('%m', p.date) AS month, count(*)
        FROM derived_press_issue_labels l
        JOIN press_releases p ON p.release_id = l.release_id
        WHERE p.date IS NOT NULL AND p.year BETWEEN 2022 AND 2026
        GROUP BY l.issue_code, p.year, month
    """)
    for issue_code, year, month, n in rows:
        if month is None:
            continue
        q = month_to_quarter(month)
        press[(issue_code, int(year), q)] += n

    return dict(press)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")

    if con.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='derived_press_issue_labels'"
    ).fetchone()[0] == 0:
        print(
            "ERROR: derived_press_issue_labels not found -- run "
            "scripts/build_derived_press_issue_labels.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    issue_names: dict[str, str] = {}
    for code, name in con.execute("SELECT value, name FROM ref_issue_codes"):
        issue_names[code] = name

    print(f"Building {TABLE}...")
    for stmt in build_ddl(TABLE).strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)
    con.commit()

    print("  Computing Senate activities and apportioned income...")
    s_acts, s_income = compute_senate(con)

    print("  Computing House activities and apportioned income...")
    h_acts, h_income = compute_house(con)

    print("  Computing press volume from derived_press_issue_labels (M0 classifier)...")
    press_counts = compute_press_ml(con)

    all_keys: set[tuple] = set(s_acts) | set(s_income) | set(h_acts) | set(h_income) | set(press_counts)

    rows = []
    for key in sorted(all_keys):
        code, year, quarter = key
        s_a = s_acts.get(key, 0)
        h_a = h_acts.get(key, 0)
        s_i = s_income.get(key, 0.0)
        h_i = h_income.get(key, 0.0)
        total_a = s_a + h_a
        total_i = s_i + h_i
        n_press = press_counts.get(key, 0)
        lpp = total_a / n_press if n_press > 0 else None
        rows.append((
            code, issue_names.get(code, ""),
            year, quarter,
            s_a, h_a, total_a,
            s_i, h_i, total_i,
            n_press, lpp,
        ))

    con.executemany(f"""
        INSERT INTO {TABLE}
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, rows)
    con.commit()
    print(f"  Inserted {len(rows):,} rows.")

    if args.validate:
        print("\n--- validation ---")
        for row in con.execute(f"""
            SELECT 'rows' AS m, count(*) FROM {TABLE} UNION ALL
            SELECT 'codes',   count(DISTINCT issue_code) FROM {TABLE} UNION ALL
            SELECT 'years',   count(DISTINCT year) FROM {TABLE} UNION ALL
            SELECT 'quarters',count(DISTINCT quarter) FROM {TABLE}
        """):
            print(f"  {row[0]:<12} {row[1]}")

        print("\n--- lobby_per_press top 10, ML-based (2023-2024, >=50 press) ---")
        for row in con.execute(f"""
            SELECT issue_code, issue_name,
                   sum(total_activities) as acts,
                   sum(n_press_releases) as press,
                   round(cast(sum(total_activities) as real)/sum(n_press_releases),1) as ratio
            FROM {TABLE}
            WHERE year BETWEEN 2023 AND 2024 AND n_press_releases > 0
            GROUP BY issue_code
            HAVING sum(n_press_releases) >= 50
            ORDER BY ratio DESC LIMIT 10
        """):
            print(f"  {row[0]} {row[1]:<35} {row[2]:>6} acts / {row[3]:>5} press = {row[4]:.1f}x")

        print("\n--- comparison: same code's keyword-based ratio (from derived_issue_quarter_volume_press) ---")
        if con.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='derived_issue_quarter_volume_press'"
        ).fetchone()[0] > 0:
            for row in con.execute(f"""
                SELECT ml.issue_code,
                       round(cast(sum(ml.total_activities) as real)/sum(ml.n_press_releases),1) as ml_ratio,
                       (SELECT round(cast(sum(kw.total_activities) as real)/sum(kw.n_press_releases),1)
                        FROM derived_issue_quarter_volume_press kw
                        WHERE kw.issue_code = ml.issue_code
                          AND kw.year BETWEEN 2023 AND 2024 AND kw.n_press_releases > 0) as kw_ratio
                FROM {TABLE} ml
                WHERE ml.year BETWEEN 2023 AND 2024 AND ml.n_press_releases > 0
                GROUP BY ml.issue_code
                HAVING sum(ml.n_press_releases) >= 50
                ORDER BY ml_ratio DESC LIMIT 10
            """):
                print(f"  {row[0]}: ML={row[1]}x  keyword={row[2]}x")

    con.close()


if __name__ == "__main__":
    main()
