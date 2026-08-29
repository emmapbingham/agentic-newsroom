#!/usr/bin/env python3
"""Build the deduplicated APRA/ADPPA Senate client roster (E5).

senate_clients.id is not a stable entity key on its own -- the same company
files under multiple client_ids across periods, sometimes with slightly
different name strings (e.g. "RELX INC." / "RELX INC"). This script pulls
the raw per-name activity counts from gain.db, manually collapses the known
name variants for entities in this roster (found by eyeballing the raw
84-name list), and writes investigations/apra-lobbying-coalition/derived/
roster_deduplicated.csv.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_roster.py
Requires db/gain.db (read-only).
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "roster_deduplicated.csv"

QUERY = """
SELECT c.name,
       count(*) n_activities,
       count(DISTINCT sf.filing_uuid) n_filings,
       count(DISTINCT c.id) n_client_ids,
       min(sf.filing_year) first_year,
       max(sf.filing_year) last_year
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE sla.general_issue_code = 'CPI'
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
GROUP BY c.name
ORDER BY n_activities DESC;
"""

# Manually identified name variants for the same entity (raw 84-name list
# had exact-duplicate senate_clients.id rows AND near-duplicate name strings
# for the same company). Found by reading the full name list once.
NAME_GROUPS = {
    "RELX": ["RELX INC.", "RELX INC"],
    "BLOCK": ["BLOCK, INC.", "BLOCK INC."],
    "MATCH GROUP": ["MATCH GROUP", "MATCH GROUP, LLC", "MATCH GROUP, INC."],
    "BSA / SOFTWARE ALLIANCE": [
        "BSA, THE SOFTWARE ALLIANCE",
        "BUSINESS SOFTWARE ALLIANCE",
        "BSA THE SOFTWARE ALLIANCE (FORMERLY BSA BUSINESS SOFTWARE ALLIANCE INC)",
    ],
    "TECHNET": ["TECHNET", "TECHNOLOGY NETWORK AKA TECHNET"],
    "INTUIT": [
        "INTUIT, INC. AND AFFILIATES (FORMERLY INTUIT, INC.)",
        "INTUIT, INC. AND AFFILIATES",
    ],
    "META PLATFORMS": [
        "META PLATFORMS, INC.",
        "META PLATFORMS, INC. AND VARIOUS SUBSIDIARIES",
    ],
    "YAHOO": [
        'YAHOO INC, AND VAR. SUBS/AFFILIATES (FKA COLLEGE PARENT, L.P. DBA "YAHOO")',
        "YAHOO INC. AND VAR. SUBS/AFFILIATES",
    ],
    "LIVERAMP": ["LIVERAMP, INC.", "LIVERAMP HOLDINGS INC."],
    "SIIA": [
        "SOFTWARE & INFORMATION INDUSTRY ASSOCIATION",
        "SOFTWARE & INFORMATION INDUSTRY ASSOCIATION (SIIA)",
    ],
    "IBM": ["INTERNATIONAL BUSINESS MACHINES CORPORATION (IBM)", "IBM"],
}
NAME_TO_GROUP = {name: g for g, names in NAME_GROUPS.items() for name in names}


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    rows = con.execute(QUERY).fetchall()
    con.close()

    merged: dict[str, dict] = {}
    for name, n_activities, n_filings, n_client_ids, first_year, last_year in rows:
        key = NAME_TO_GROUP.get(name, name)
        m = merged.setdefault(
            key,
            {"n_activities": 0, "n_filings": 0, "n_client_ids": 0,
             "first_year": 9999, "last_year": 0, "names": []},
        )
        m["n_activities"] += n_activities
        m["n_filings"] += n_filings
        m["n_client_ids"] += n_client_ids
        m["first_year"] = min(m["first_year"], first_year)
        m["last_year"] = max(m["last_year"], last_year)
        m["names"].append(name)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "entity", "n_activities", "n_filings", "n_client_ids",
            "first_year", "last_year", "n_years_span", "raw_names_merged",
        ])
        for k, m in sorted(merged.items(), key=lambda kv: -kv[1]["n_activities"]):
            w.writerow([
                k, m["n_activities"], m["n_filings"], m["n_client_ids"],
                m["first_year"], m["last_year"],
                m["last_year"] - m["first_year"] + 1,
                "; ".join(m["names"]),
            ])

    print(f"{len(rows)} raw name-rows -> {len(merged)} deduplicated entities")
    print(f"total activities: {sum(m['n_activities'] for m in merged.values())}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
