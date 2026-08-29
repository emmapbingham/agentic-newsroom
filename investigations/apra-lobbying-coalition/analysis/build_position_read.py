#!/usr/bin/env python3
"""E8: re-run E5's position-language keyword scan against the FULL corrected
345-entity roster (any issue code, length(description) < 600 — E6/E7's
method), not the superseded 71-entity CPI-only roster E5 used.

Pulls every activity description matching both the bill-name filter and a
position-signal keyword (oppose/support/preemption/private right of
action/concern/favor), for manual read-through classification into genuine
bill-specific position language vs. false-positive boilerplate (e.g.
"support" used for an unrelated bill in the same laundry-list description).

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_position_read.py
Requires db/gain.db (read-only). Writes derived/position_read_candidates.csv
for manual read-through; the classification itself is recorded in evidence.md
E8, not derived mechanically.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "position_read_candidates.csv"

QUERY = """
SELECT c.name, sf.filing_year, sla.general_issue_code, sla.description
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE length(sla.description) < 600
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
  AND (
    lower(sla.description) LIKE '%oppose%'
    OR lower(sla.description) LIKE '%support%'
    OR lower(sla.description) LIKE '%private right of action%'
    OR lower(sla.description) LIKE '%preemption%'
    OR lower(sla.description) LIKE '%preempt%'
    OR lower(sla.description) LIKE '%concern%'
    OR lower(sla.description) LIKE '%favor %'
  )
ORDER BY c.name, sf.filing_year;
"""


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute(QUERY).fetchall()
    con.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["client_name", "filing_year", "issue_code", "description"])
        w.writerows(rows)

    names = sorted(set(r[0] for r in rows))
    print(f"{len(rows)} rows / {len(names)} distinct raw client names")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
