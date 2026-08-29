"""Pull cosponsor lists for the 4 bills named in Amazon's LDA lobbying
descriptions (evidence.md E3), cross-reference against the 39 Amazon-money
members from screen 40 (entity_id=125), and write the crosswalk used in E4.

Requires CONGRESS_GOV_API_KEY in .env (repo root). Re-run to refresh; raw API
responses cached under data/congress_bills/ (gitignored).
"""
import json
import sqlite3
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BILLS = {
    "AICOA_S": ("117", "s", "2992"),
    "AICOA_HR": ("117", "hr", "3816"),
    "WWPA_S": ("118", "s", "4260"),
    "WWPA_HR": ("118", "hr", "8639"),
}

RAW_DIR = ROOT / "data" / "congress_bills"


def load_api_key():
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("CONGRESS_GOV_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("CONGRESS_GOV_API_KEY not found in .env")


def fetch(api_key, congress, btype, num, suffix=""):
    url = (f"https://api.congress.gov/v3/bill/{congress}/{btype}/{num}{suffix}"
           f"?format=json&api_key={api_key}&limit=250")
    req = urllib.request.Request(url, headers={"User-Agent": "gain-investigation/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    api_key = load_api_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    sponsors, cosponsor_sets = {}, {}
    for label, (congress, btype, num) in BILLS.items():
        bill = fetch(api_key, congress, btype, num)
        (RAW_DIR / f"bill_{congress}_{btype}_{num}.json").write_text(json.dumps(bill, indent=2))
        sponsors[label] = bill["bill"]["sponsors"][0]["bioguideId"]
        time.sleep(0.3)

        cospon = fetch(api_key, congress, btype, num, "/cosponsors")
        (RAW_DIR / f"cosponsors_{congress}_{btype}_{num}.json").write_text(json.dumps(cospon, indent=2))
        cosponsor_sets[label] = {c["bioguideId"]: c.get("sponsorshipDate") for c in cospon["cosponsors"]}
        time.sleep(0.3)

    conn = sqlite3.connect(ROOT / "db" / "gain.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        WITH ent_reg AS (
          SELECT DISTINCT a.entity_id, r.id AS registrant_id
          FROM derived_client_alias_index a
          JOIN senate_registrants r
            ON UPPER(replace(replace(r.name,'.',''),',','')) = a.alias
          WHERE a.status <> 'rejected_too_generic' AND a.entity_id = 125
        ),
        money AS (
          SELECT entity_id, bioguide, sum(amount_num) AS feca_usd
          FROM (
            SELECT DISTINCT er.entity_id, h.bioguide,
                   ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
            FROM ent_reg er
            JOIN senate_contribution_filings cf ON cf.registrant_id = er.registrant_id
            JOIN senate_contribution_items ci ON ci.filing_uuid = cf.filing_uuid
            JOIN honoree_member_map h
              ON h.honoree_name = ci.honoree_name AND h.confidence >= 0.9
            WHERE ci.contribution_type = 'feca' AND ci.amount_num > 0
          )
          GROUP BY entity_id, bioguide
        ),
        ment AS (
          SELECT entity_id, bioguide_id, count(*) AS n_mentions
          FROM derived_client_press_mentions
          WHERE bioguide_id IS NOT NULL
          GROUP BY entity_id, bioguide_id
        )
        SELECT m.bioguide, m.official_full, m.last_party, m.last_state, m.last_type, mo.feca_usd
        FROM money mo
        JOIN ment me ON me.entity_id = mo.entity_id AND me.bioguide_id = mo.bioguide
        JOIN members m ON m.bioguide = mo.bioguide
        WHERE me.n_mentions >= 2
        ORDER BY mo.feca_usd DESC
    """).fetchall()

    out = []
    for r in rows:
        bg = r["bioguide"]
        entry = dict(bioguide=bg, name=r["official_full"], party=r["last_party"],
                     state=r["last_state"], chamber=r["last_type"], feca_usd=r["feca_usd"])
        for label in BILLS:
            if bg == sponsors[label]:
                entry[label] = "SPONSOR"
            elif bg in cosponsor_sets[label]:
                entry[label] = f"cosponsor:{cosponsor_sets[label][bg]}"
            else:
                entry[label] = "-"
        out.append(entry)

    out_path = Path(__file__).parent.parent / "derived" / "cosponsorship_crosswalk.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"wrote {len(out)} rows to {out_path}")


if __name__ == "__main__":
    main()
