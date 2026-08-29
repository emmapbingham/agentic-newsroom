#!/usr/bin/env python3
"""E14: does APRA/ADPPA-matched Senate lobbying activity spike in the exact
quarters the bill text became live (introduction, discussion draft, markup),
and is that spike industry-dominated?

Two things checked, both editor-directed (2026-07-08 follow-up to the
kill-decision-contribution work, E13, which found no money signal):

1. Quarterly activity volume, same bill-name/ADPPA keyword filter as
   E1/E6/E8 (length<600, same 5 phrase patterns) -- compared against the
   corpus-wide quarterly baseline (ALL Senate lobbying activities, no
   filter) to rule out a general Q2 filing-season artifact before treating
   any spike as APRA-specific.
2. For the two spike quarters (Q2 2022: ADPPA introduced 2022-06-21; Q2
   2024: APRA discussion draft 2024-04-08, formal introduction 2024-06-25,
   markup canceled 2024-06-27 -- all three land in one quarter) and their
   immediately preceding baseline quarters (Q1 2022, Q1 2024), classify
   every distinct client name as industry (corporation/trade association)
   vs. non-industry (advocacy/public-interest/other) -- reusing E3/E8's
   already-identified advocacy-org name list, not re-deriving it from
   scratch.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_drafting_stage_spike.py
Requires db/gain.db (read-only). Writes derived/drafting_stage_spike.csv
(quarterly counts) and derived/drafting_stage_spike_composition.csv
(per-quarter client list with industry/non-industry classification).
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT_QUARTERLY = Path(__file__).resolve().parent.parent / "derived" / "drafting_stage_spike.csv"
OUT_COMPOSITION = Path(__file__).resolve().parent.parent / "derived" / "drafting_stage_spike_composition.csv"

BILL_FILTER = """
  length(sla.description) < 600
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
"""

# Reused from E3 (evidence.md) -- the 8 advocacy orgs identified by name-
# pattern search in the CPI client roster -- plus a small number of other
# obviously non-industry names spotted by inspection when this spike's
# client lists were read (Public Knowledge, Brennan Center, reproductive-
# rights groups). NOT a mechanically-derived list -- a manual read-through,
# same convention as E3/E5/E8's position-language classification.
NON_INDUSTRY_MARKERS = [
    "ELECTRONIC FRONTIER", "FIGHT FOR THE FUTURE", "CENTER FOR HUMANE TECHNOLOGY",
    "DUE PROCESS INSTITUTE", "AVAAZ", "DAVID'S LEGACY", "CHILDREN AND SCREENS",
    "SANDY HOOK PROMISE", "CONSUMER FEDERATION", "PUBLIC KNOWLEDGE",
    "PUBLIC INTEREST RESEARCH", "CONSUMER REPORTS", "AMERICAN CIVIL LIBERTIES",
    "COMMON SENSE", "CENTER FOR DEMOCRACY", "FREE PRESS", "ACCESS NOW",
    "NATIONAL CONSUMERS LEAGUE", "ELECTRONIC PRIVACY INFORMATION",
    "PLANNED PARENTHOOD", "SUSAN B ANTHONY", "BRENNAN CENTER",
    "AMERICAN HEART ASSOCIATION", "AMERICAN ASSOCIATION FOR JUSTICE",
]

QUARTER_ORDER = {"first_quarter": 1, "second_quarter": 2, "third_quarter": 3, "fourth_quarter": 4}

SPIKE_QUARTERS = [
    (2022, "first_quarter", "Q1 2022 (pre-ADPPA baseline)"),
    (2022, "second_quarter", "Q2 2022 (ADPPA H.R.8152 introduced 2022-06-21)"),
    (2024, "first_quarter", "Q1 2024 (pre-APRA baseline)"),
    (2024, "second_quarter", "Q2 2024 (APRA draft 04-08, introduced 06-25, markup canceled 06-27)"),
]


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    # part 1: quarterly volume, APRA-matched vs. corpus-wide baseline
    apra_q = con.execute(f"""
        SELECT sf.filing_year, sf.filing_period, count(*) n_activities,
               count(DISTINCT c.id) n_clients
        FROM senate_lobbying_activities sla
        JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
        JOIN senate_clients c ON c.id = sf.client_id
        WHERE {BILL_FILTER}
        GROUP BY sf.filing_year, sf.filing_period
    """).fetchall()
    baseline_q = con.execute("""
        SELECT sf.filing_year, sf.filing_period, count(*) n_all_activities
        FROM senate_lobbying_activities sla
        JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
        GROUP BY sf.filing_year, sf.filing_period
    """).fetchall()
    baseline_map = {(y, p): n for y, p, n in baseline_q}

    quarterly_rows = []
    for y, p, n_act, n_cli in apra_q:
        quarterly_rows.append({
            "filing_year": y, "filing_period": p,
            "apra_matched_activities": n_act, "apra_matched_clients": n_cli,
            "corpus_wide_activities": baseline_map.get((y, p), 0),
        })
    quarterly_rows.sort(key=lambda r: (r["filing_year"], QUARTER_ORDER[r["filing_period"]]))

    OUT_QUARTERLY.parent.mkdir(parents=True, exist_ok=True)
    with OUT_QUARTERLY.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(quarterly_rows[0].keys()))
        w.writeheader()
        w.writerows(quarterly_rows)

    # part 2: composition of the two spike quarters + their baselines
    comp_rows = []
    for year, period, label in SPIKE_QUARTERS:
        names = con.execute(f"""
            SELECT DISTINCT c.name
            FROM senate_lobbying_activities sla
            JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
            JOIN senate_clients c ON c.id = sf.client_id
            WHERE {BILL_FILTER}
              AND sf.filing_year = ? AND sf.filing_period = ?
        """, (year, period)).fetchall()
        for (name,) in names:
            is_non_industry = any(m.upper() in name.upper() for m in NON_INDUSTRY_MARKERS)
            comp_rows.append({
                "quarter_label": label, "filing_year": year, "filing_period": period,
                "client_name": name, "classification": "non_industry" if is_non_industry else "industry",
            })

    con.close()

    with OUT_COMPOSITION.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(comp_rows[0].keys()))
        w.writeheader()
        w.writerows(comp_rows)

    print("Quarterly APRA-matched activity vs. corpus-wide baseline:")
    for r in quarterly_rows:
        print(f"  {r['filing_year']} {r['filing_period']:15s} "
              f"apra={r['apra_matched_activities']:4d}  clients={r['apra_matched_clients']:4d}  "
              f"corpus_baseline={r['corpus_wide_activities']}")
    print()
    print("Composition of spike quarters vs. their baselines:")
    for year, period, label in SPIKE_QUARTERS:
        sub = [r for r in comp_rows if r["filing_year"] == year and r["filing_period"] == period]
        n_industry = sum(1 for r in sub if r["classification"] == "industry")
        n_non = len(sub) - n_industry
        print(f"  {label}: {len(sub)} clients, {n_industry} industry ({n_industry/len(sub)*100:.0f}%), "
              f"{n_non} non-industry {[r['client_name'] for r in sub if r['classification']=='non_industry']}")
    print(f"\nwrote {OUT_QUARTERLY}")
    print(f"wrote {OUT_COMPOSITION}")


if __name__ == "__main__":
    main()
