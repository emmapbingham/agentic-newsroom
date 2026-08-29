#!/usr/bin/env python3
"""E10: LD-203 contributions to the top 4 press-release members
(Schakowsky S001145, Trahan T000482, Moran M000934, DelBene D000617 -- the
top 4 by count in derived/apra_press_releases.csv after excluding
UNVERIFIED/reproductive-rights rows, per editor request 2026-07-08) from
registrants tied to APRA-matched lobbying filings for a roster client.

Method, following E4's RELX precedent: LD-203 filings are filed by
REGISTRANTS (lobbying firms / in-house lobbying shops), not CLIENTS
directly. Scope registrants to those with at least one APRA-matched Senate
filing (length<600, bill-name keyword match) for a roster client -- same
scoping as build_corrected_roster.py -- then pull that registrant's own
LD-203 contribution items to the 4 members (honoree_member_map,
confidence>=0.9).

Distinguishes in-house lobbying (registrant name == roster client name,
i.e. company lobbies for itself) from third-party firms (a law/lobbying
firm hired by a roster client) -- a third-party firm's LD-203 contribution
is that FIRM's own giving, not directly attributable to any one client's
interest in APRA specifically (the firm may represent many other clients
too). Report both, clearly separated.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_top4_contributions.py
Requires db/gain.db (read-only). Writes derived/top4_member_contributions.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
ROSTER = Path(__file__).resolve().parent.parent / "derived" / "roster_corrected_deduplicated.csv"
OUT = Path(__file__).resolve().parent.parent / "derived" / "top4_member_contributions.csv"

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
    # keep only registrants tied to an APRA-matched filing for a roster client
    reg_to_clients = {}
    for rid, rname, cname in reg_rows:
        if cname.upper() in roster_names_upper:
            reg_to_clients.setdefault(rid, {"name": rname, "clients": set()})
            reg_to_clients[rid]["clients"].add(cname)

    reg_ids = list(reg_to_clients.keys())
    reg_placeholders = ",".join("?" * len(reg_ids))
    bg_placeholders = ",".join("?" * len(MEMBERS))

    q = f"""
    SELECT hm.bioguide, scf.registrant_id, sci.honoree_name, sci.date,
           sci.amount_num, sci.filing_uuid
    FROM senate_contribution_items sci
    JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
    JOIN honoree_member_map hm ON hm.honoree_name = sci.honoree_name
    WHERE scf.registrant_id IN ({reg_placeholders})
      AND hm.bioguide IN ({bg_placeholders})
      AND hm.confidence >= 0.9
    """
    contrib_rows = con.execute(q, reg_ids + list(MEMBERS.keys())).fetchall()
    con.close()

    # aggregate by (bioguide, registrant) then attribute to client(s)
    agg = {}
    for bioguide, registrant_id, honoree_name, date, amount, filing_uuid in contrib_rows:
        key = (bioguide, registrant_id)
        a = agg.setdefault(key, {"n_items": 0, "total": 0.0, "min_date": date, "max_date": date})
        a["n_items"] += 1
        a["total"] += amount or 0.0
        a["min_date"] = min(a["min_date"], date) if date else a["min_date"]
        a["max_date"] = max(a["max_date"], date) if date else a["max_date"]

    rows = []
    for (bioguide, registrant_id), a in agg.items():
        reg_info = reg_to_clients[registrant_id]
        registrant_name = reg_info["name"]
        clients = sorted(reg_info["clients"])
        relationship = "in_house" if registrant_name.upper() in roster_names_upper else "third_party_firm"
        rows.append({
            "member": MEMBERS[bioguide],
            "bioguide": bioguide,
            "registrant": registrant_name,
            "relationship": relationship,
            "roster_clients_represented": "; ".join(clients),
            "n_contribution_items": a["n_items"],
            "total_amount": round(a["total"], 2),
            "first_date": a["min_date"],
            "last_date": a["max_date"],
        })

    rows.sort(key=lambda r: (r["member"], -r["total_amount"]))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{len(rows)} (member, registrant) rows")
    print(f"  in_house: {sum(1 for r in rows if r['relationship']=='in_house')}")
    print(f"  third_party_firm: {sum(1 for r in rows if r['relationship']=='third_party_firm')}")
    for m in MEMBERS.values():
        sub = [r for r in rows if r["member"] == m]
        total = sum(r["total_amount"] for r in sub)
        print(f"  {m}: {len(sub)} registrants, ${total:,.2f} total")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
