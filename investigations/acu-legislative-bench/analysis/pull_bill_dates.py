"""Pull authoritative introduced/latest-action dates for the bench's named
bills (evidence.md E1-E9, EBarr6) from the Congress.gov API, for the
introduced-date milestones on the bench timeline chart.

Bill numbers were NOT assumed to carry across Congresses (evidence.md already
flags S.3992->S.2486 renumbering for the SBA-lending bill) -- each was
independently confirmed via web search against congress.gov before being
hardcoded here (see log.md 2026-07-08 entry for source links). Congress.gov's
v3 API has no working free-text bill search, so this list can't be built by
querying the API alone.

Requires CONGRESS_GOV_API_KEY in .env (repo root). Re-run to refresh; raw API
responses cached under data/congress_bills/ (gitignored).
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "congress_bills"
OUT = Path(__file__).resolve().parent.parent / "derived" / "bench_bill_dates.csv"

# (member, bill_label, congress, bill_type, number, evidence_ref)
# multiple rows per member/bill_label = reintroduction across Congresses
BILLS = [
    ("Barr", "TABS Act", "118", "hr", "1382", "EBarr6"),
    ("Barr", "TABS Act", "119", "hr", "654", "EBarr6"),
    ("Barr", "Rectifying UDAAP Act", "118", "hr", "6789", "EBarr6"),
    ("Barr", "Rectifying UDAAP Act", "119", "hr", "1652", "EBarr6"),
    ("Cramer", "Protecting Access to Credit for Small Businesses Act", "118", "s", "3992", "E1"),
    ("Cramer", "Protecting Access to Credit for Small Businesses Act", "119", "s", "2486", "E1"),
    ("Scott", "Protecting Access to Credit for Small Businesses Act", "118", "s", "3992", "E2"),
    ("Scott", "Protecting Access to Credit for Small Businesses Act", "119", "s", "2486", "E2"),
    ("Budd", "Protecting Access to Credit for Small Businesses Act", "118", "s", "3992", "E6"),
    ("Budd", "Protecting Access to Credit for Small Businesses Act", "119", "s", "2486", "E6"),
    ("Britt", "Community Bank Relief Act", "119", "s", "3849", "E3"),
    ("Britt", "Community Bank Relief Act", "119", "hr", "7484", "E3"),
    ("Emmer", "Anti-CBDC Surveillance State Act", "118", "hr", "5403", "E4"),
    ("Emmer", "Anti-CBDC Surveillance State Act", "119", "hr", "1919", "E4"),
    ("Fitzgerald", "Making the CFPB Accountable to Small Businesses Act", "117", "hr", "8443", "E5"),
    ("Fitzgerald", "Making the CFPB Accountable to Small Businesses Act", "118", "hr", "1749", "E5"),
    ("Fitzgerald", "Making the CFPB Accountable to Small Businesses Act", "119", "hr", "1606", "E5"),
    ("Fitzgerald", "HUMPS Act", "119", "hr", "3379", "E5"),
    ("Fitzgerald", "Expanding Access to Lending Options Act", "118", "hr", "6933", "E5"),
    ("Fitzgerald", "Expanding Access to Lending Options Act", "119", "hr", "4167", "E5"),
    ("Beatty", "Fair Hiring in Banking Act", "117", "hr", "5911", "E7"),
    # added 2026-07-09: editor found a second Beatty bill this case had
    # missed -- her 2025-06-05 press release is actually about THIS bill,
    # not Fair Hiring in Banking Act. ACU's lobbying text DOES name it
    # (1 filing, 2026 Q1) -- see E7's revision.
    ("Beatty", "Advancing the Mentor-Protege Program for Small Financial Institutions Act", "119", "hr", "3709", "E7-correction"),
    ("Vargas", "Credit Union Board Modernization Act", "118", "hr", "582", "E8"),
    ("Vargas", "Credit Union Board Modernization Act", "119", "hr", "975", "E8"),
    ("Gonzalez", "Veterans Member Business Loan Act", "118", "hr", "4867", "E9"),
    ("Gonzalez", "Veterans Member Business Loan Act", "119", "hr", "507", "E9"),
    # added 2026-07-08 while checking the "press mentions always have a bill
    # or contribution nearby" observation -- these two press releases
    # (Britt 2025-10-22, Gonzalez 2026-02-24) looked like exceptions only
    # because their bills weren't in the original E1-E9 inventory; both
    # turned out to be same-day/next-day bill-intro announcements. See
    # log.md 2026-07-08 (press-hook completeness check).
    ("Britt", "STREAMLINE Act", "119", "s", "3017", "press-hook-check"),
    ("Gonzalez", "MORE Opportunities for Homeownership Act", "119", "hr", "7647", "press-hook-check"),
    # added 2026-07-09 (E13): Peters, added to the bench per editor's call.
    # S.1490 (117th) is the ACU-lobbying-confirmed bill (Peters' original
    # 2021 sponsorship, identical to Beatty's H.R.1395); S.4542 (118th) is
    # the bill his actual 2024-06-13 "Reintroduces" press release covers --
    # ACU's lobbying text does NOT name S.4542 (see E13/build_bench_lobbying
    # note). Both rows kept so the chart shows the full lineage + the gap.
    ("Peters", "Housing Financial Literacy Act", "117", "s", "1490", "E13"),
    ("Peters", "Housing Financial Literacy Act", "118", "s", "4542", "E13"),
    # added 2026-07-09 (E16): systematic press-release-vs-bill pass found 2
    # more gaps. Budd's is a genuinely new, previously untracked bill;
    # Vargas's is a real cosponsorship of a bill already in this list under
    # Fitzgerald (H.R.6933) -- added again here under Vargas's own name so
    # his bill_dates rows/chart lane show it too (same underlying bill,
    # shared by two bench members, same pattern as Cramer/Scott/Budd's
    # shared SBA-lending bill above).
    ("Budd", "Secure Payments Act", "118", "s", "4570", "E16"),
    ("Vargas", "Expanding Access to Lending Options Act (shared w/ Fitzgerald)", "118", "hr", "6933", "E16"),
]


def load_api_key():
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("CONGRESS_GOV_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("CONGRESS_GOV_API_KEY not found in .env")


def fetch(api_key, congress, btype, num):
    url = (f"https://api.congress.gov/v3/bill/{congress}/{btype}/{num}"
           f"?format=json&api_key={api_key}")
    req = urllib.request.Request(url, headers={"User-Agent": "gain-investigation/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def main():
    api_key = load_api_key()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for member, bill_label, congress, btype, num, ev_ref in BILLS:
        cache_path = RAW_DIR / f"bill_{congress}_{btype}_{num}.json"
        if cache_path.exists():
            bill = json.loads(cache_path.read_text())
        else:
            bill = fetch(api_key, congress, btype, num)
            cache_path.write_text(json.dumps(bill, indent=2))
            time.sleep(0.3)

        b = bill["bill"]
        sponsor = b.get("sponsors", [{}])[0]
        rows.append({
            "member": member,
            "bill_label": bill_label,
            "evidence_ref": ev_ref,
            "congress": congress,
            "bill_type": btype.upper(),
            "number": num,
            "official_title": b.get("title", ""),
            "sponsor_bioguide": sponsor.get("bioguideId", ""),
            "sponsor_name": sponsor.get("fullName", ""),
            "introduced_date": b.get("introducedDate", ""),
            "latest_action_date": b.get("latestAction", {}).get("actionDate", ""),
            "latest_action_text": b.get("latestAction", {}).get("text", ""),
            "congress_gov_url": b.get("legislationUrl", ""),
        })
        print(f"{member} / {bill_label} ({congress}th {btype.upper()}.{num}): "
              f"introduced {rows[-1]['introduced_date']}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\nwrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
