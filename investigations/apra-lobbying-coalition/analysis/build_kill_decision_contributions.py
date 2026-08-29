#!/usr/bin/env python3
"""E13: LD-203 contributions from in-house APRA-lobbying registrants to the
people most directly tied to APRA's fate: the two reported kill-decision-
makers at the June 27, 2024 House markup cancellation, plus both discussion-
draft co-authors (House and Senate) as contrast cases -- NOT "GOP
leadership" in the abstract.

Per a 2026-07-08 web search (non-corpus, see log.md): Speaker Mike Johnson
(J000299) and Majority Leader Steve Scalise (S001176) arranged a leadership
meeting the night before the markup that excluded committee chair Cathy
McMorris Rodgers (M001159) -- APRA's own lead House GOP sponsor and
co-author of the Cantwell-Rodgers discussion draft -- and used it to block
the bill over Rodgers' objection. Rodgers announced her retirement 2024-02-08
(also web-sourced), which -- checked and confirmed 2026-07-08 -- explains
why ALL her recorded contributions, not just APRA-linked ones, stop within
days of that announcement; her contribution pattern is NOT usable as a
clean contrast case for this reason.

Sen. Maria Cantwell (C000127), the discussion draft's Senate co-author, is
a cleaner contrast: not retiring, not up for re-election in this window,
still active. If Johnson/Scalise show a contribution pattern distinct from
BOTH bill co-authors (Rodgers pre-retirement-announcement, and Cantwell
throughout), that would be more informative than comparing against Rodgers
alone, whose data is confounded by her retirement.

Reuses the same in-house/APRA-matched registrant scoping as E11
(build_top4_inhouse_timeline.py) -- same query, different honoree set.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_kill_decision_contributions.py
Requires db/gain.db (read-only). Writes derived/kill_decision_contributions.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
ROSTER = Path(__file__).resolve().parent.parent / "derived" / "roster_corrected_deduplicated.csv"
OUT = Path(__file__).resolve().parent.parent / "derived" / "kill_decision_contributions.csv"

MEMBERS = {
    "J000299": "Johnson (Speaker, reportedly arranged the block)",
    "S001176": "Scalise (Majority Leader, reportedly arranged the block)",
    "M001159": "McMorris Rodgers (bill's own lead GOP sponsor, reportedly excluded)",
    "C000127": "Cantwell (Senate co-author of the discussion draft, not up for re-election, not retiring)",
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
        if out_rows:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            w.writeheader()
            w.writerows(out_rows)
        else:
            f.write("member,bioguide,in_house_registrant_client,contribution_date,amount,"
                     "amount_num,honoree_name_as_filed,filing_year,filing_period,filing_uuid,lda_url\n")

    print(f"{len(in_house_reg_ids)} in-house APRA-lobbying registrants checked")
    print(f"{len(out_rows)} individual contribution items found")
    for bg, label in MEMBERS.items():
        sub = [r for r in out_rows if r["bioguide"] == bg]
        total = sum(r["amount_num"] or 0 for r in sub)
        entities = sorted(set(r["in_house_registrant_client"] for r in sub))
        print(f"  {label}: {len(sub)} items, ${total:,.2f}, entities: {entities}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
