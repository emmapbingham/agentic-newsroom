#!/usr/bin/env python3
"""E11: item-level (exact-date) LD-203 contributions to the top 4
press-release members, restricted to IN-HOUSE registrants only (editor
instruction 2026-07-08: third-party firm rows in E10/
top4_member_contributions.csv can't be attributed to a specific client's
motive, since an LD-203 filing has no client field -- see log.md for the
mechanics discussion). In-house means the registrant IS the roster client
(the company lobbies for itself), so "this entity lobbied on APRA" and
"this entity gave this contribution" are the same legal person.

Reuses the same registrant-scoping query as build_top4_contributions.py
(APRA-matched Senate filings, length<600, bill-name keyword, for a roster
client) rather than re-deriving it. Unlike E10's aggregate CSV, this keeps
one row per contribution ITEM (exact date), not per (member, registrant)
aggregate, so it can be laid next to derived/apra_press_releases.csv's
press-release dates for a timing comparison.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_top4_inhouse_timeline.py
Requires db/gain.db (read-only). Writes derived/top4_inhouse_contribution_timeline.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
ROSTER = Path(__file__).resolve().parent.parent / "derived" / "roster_corrected_deduplicated.csv"
OUT = Path(__file__).resolve().parent.parent / "derived" / "top4_inhouse_contribution_timeline.csv"

MEMBERS = {
    "S001145": "Schakowsky",
    "T000482": "Trahan",
    "M000934": "Moran",
    "D000617": "DelBene",
}

REGISTRANT_QUERY = """
SELECT DISTINCT r.id, r.name, c.name
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
JOIN senate_registrants r ON r.id = sf.registrant_id
WHERE length(sla.description) < 600
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
"""


def main() -> None:
    roster = list(csv.DictReader(ROSTER.open()))
    roster_names_upper = set()
    for r in roster:
        for n in r["raw_names_merged"].split("; "):
            roster_names_upper.add(n.strip().upper())

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    reg_rows = con.execute(REGISTRANT_QUERY).fetchall()
    in_house_reg_ids = {
        rid for rid, rname, cname in reg_rows
        if cname.upper() in roster_names_upper and rname.upper() in roster_names_upper
    }

    reg_placeholders = ",".join("?" * len(in_house_reg_ids))
    bg_placeholders = ",".join("?" * len(MEMBERS))

    q = f"""
    SELECT hm.bioguide, r.name, sci.honoree_name, sci.date, sci.amount, sci.amount_num,
           sci.filing_uuid, scf.filing_year, scf.filing_period_display
    FROM senate_contribution_items sci
    JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
    JOIN senate_registrants r ON r.id = scf.registrant_id
    JOIN honoree_member_map hm ON hm.honoree_name = sci.honoree_name
    WHERE scf.registrant_id IN ({reg_placeholders})
      AND hm.bioguide IN ({bg_placeholders})
      AND hm.confidence >= 0.9
    ORDER BY hm.bioguide, sci.date
    """
    rows = con.execute(q, list(in_house_reg_ids) + list(MEMBERS.keys())).fetchall()
    con.close()

    out_rows = []
    for bioguide, registrant, honoree_name, date, amount, amount_num, filing_uuid, filing_year, filing_period in rows:
        out_rows.append({
            "member": MEMBERS[bioguide],
            "bioguide": bioguide,
            "in_house_registrant_client": registrant,
            "contribution_date": date,
            "amount": amount,
            "amount_num": amount_num,
            "honoree_name_as_filed": honoree_name,
            "filing_year": filing_year,
            "filing_period": filing_period,
            "filing_uuid": filing_uuid,
            "lda_url": f"https://lda.gov/filings/public/contribution/{filing_uuid}/print/",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f"{len(in_house_reg_ids)} in-house registrants matched")
    print(f"{len(out_rows)} individual contribution items")
    for m in MEMBERS.values():
        sub = [r for r in out_rows if r["member"] == m]
        total = sum(r["amount_num"] or 0 for r in sub)
        print(f"  {m}: {len(sub)} items, ${total:,.2f}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
