#!/usr/bin/env python3
"""Interactive companion to bench_timeline_chart.png: reads the same 4
derived CSVs (bench_contributions.csv, bench_press_releases.csv,
bench_lobbying_filings.csv, bench_bill_dates.csv) and writes a self-
contained static HTML file with a D3 timeline -- hover any marker
(contribution, press mention, lobbying filing, bill-introduction) for its
full detail: bill purpose, press headline+url, lobbying excerpt+LDA link,
contribution amount+payee+LDA link.

This script owns DATA ONLY -- reshaping the 4 CSVs into one JSON blob and
injecting it into an HTML shell. The rendering logic lives in the static,
hand-written analysis/bench_timeline_d3.js, loaded by the HTML shell
unchanged; re-running this script never touches that file.

The PNG (build_bench_timeline_chart.py) stays the archival/print artifact
for the PDF report; this HTML is the interactive review companion -- same
underlying data, same 4-layer design (contributions/press/lobbying/bill-
intro), not a replacement.

BILL_PURPOSES below is a short plain-English gloss per bill_label, hand-
written from evidence.md's own descriptions (E1-E9) plus the web search
that resolved bench_bill_dates.csv (see log.md 2026-07-08) -- official
titles are frequently uninformative ("TABS Act of 2023"), so this exists
to make the tooltip useful without clicking through to congress.gov.

Re-run: python3 investigations/acu-legislative-bench/analysis/build_bench_timeline_d3.py
Writes derived/bench_timeline_data.json and derived/bench_timeline_chart.html.
"""
import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "derived"
ANALYSIS = Path(__file__).resolve().parent
CONTRIB_CSV = BASE / "bench_contributions.csv"
PRESS_CSV = BASE / "bench_press_releases.csv"
LOBBYING_CSV = BASE / "bench_lobbying_filings.csv"
BILL_DATES_CSV = BASE / "bench_bill_dates.csv"
JS_SRC = ANALYSIS / "bench_timeline_d3.js"
OUT_JSON = BASE / "bench_timeline_data.json"
OUT_HTML = BASE / "bench_timeline_chart.html"

MEMBERS = ["Barr", "Britt", "Emmer", "Cramer", "Scott", "Beatty",
           "Fitzgerald", "Gonzalez", "Vargas", "Budd", "Peters"]
COLORS = {
    "Barr": "#e41a1c", "Britt": "#377eb8", "Emmer": "#4daf4a", "Cramer": "#984ea3",
    "Scott": "#ff7f00", "Beatty": "#a65628", "Fitzgerald": "#f781bf",
    "Gonzalez": "#999999", "Vargas": "#66c2a5", "Budd": "#1b9e77", "Peters": "#e6ab02",
}

BILL_PURPOSES = {
    "TABS Act": "Would strip the CFPB of Federal Reserve funding and put it "
                "on congressional appropriations instead.",
    "Rectifying UDAAP Act": "Narrows the CFPB's authority to declare a "
                "financial practice \"abusive\" without a specific rule.",
    "Protecting Access to Credit for Small Businesses Act": "Blocks/delays "
                "a CFPB small-business lending data rule.",
    "Community Bank Relief Act": "Raises the asset threshold that caps "
                "debit-card interchange fees, indexed to inflation.",
    "Anti-CBDC Surveillance State Act": "Bars the Federal Reserve from "
                "issuing a central bank digital currency to individuals.",
    "Making the CFPB Accountable to Small Businesses Act": "Requires the "
                "CFPB to presume small entities need tailored regulation in "
                "SBREFA panel reviews.",
    "HUMPS Act": "Halting Uncertain Methods and Practices in Supervision -- "
                "adds transparency/process requirements to bank exams.",
    "Expanding Access to Lending Options Act": "Raises the NCUA's maximum "
                "federal credit union loan maturity from 15 to 20+ years.",
    "Fair Hiring in Banking Act": "Loosens the ban on hiring people with "
                "old/minor financial-crime convictions at banks and credit "
                "unions. Enacted via NDAA, Dec 2022.",
    "Advancing the Mentor-Protege Program for Small Financial Institutions Act":
                "Codifies a Treasury mentor-protege program pairing small/"
                "minority depository institutions with larger banks and "
                "credit unions. Beatty's SECOND bill, added 2026-07-09 -- "
                "unlike Fair Hiring in Banking Act, ACU DOES name this one "
                "in lobbying text (1 filing) and gives it a named press "
                "quote -- her record is a split, not a clean absence.",
    "Secure Payments Act": "Requires the Federal Reserve to pause its debit-"
                "card interchange-fee rule pending an economic impact study. "
                "Budd's SECOND bill, added 2026-07-09 (E16) -- found via a "
                "systematic press-release-vs-bill pass, sole-sponsored, "
                "same-day press/bill/lobbying-text pattern like most of the "
                "bench.",
    "Expanding Access to Lending Options Act (shared w/ Fitzgerald)":
                "Gives credit unions flexibility to offer longer loan terms/"
                "lower payments. Fitzgerald's bill (see his own entry above) "
                "-- Vargas is an ORIGINAL COSPONSOR, credited here under his "
                "own name after a systematic press-release-vs-bill pass "
                "(E16) found his 2024-01-10 announcement release had never "
                "been matched to a bill.",
    "Credit Union Board Modernization Act": "Lets some credit unions meet "
                "less often than monthly, easing a board-meeting mandate.",
    "Veterans Member Business Loan Act": "Excludes veteran business loans "
                "from the credit union member-business-lending cap.",
    "STREAMLINE Act": "Raises Bank Secrecy Act currency/suspicious-activity "
                "reporting thresholds (e.g. $10k to $30k), first update since "
                "the 1970s. Not in the original bench bill list -- added "
                "2026-07-08 while checking press-release hooks.",
    "MORE Opportunities for Homeownership Act": "Expands credit union access "
                "to Federal Home Loan Bank liquidity/advances for affordable "
                "housing. Not in the original bench bill list -- added "
                "2026-07-08 while checking press-release hooks.",
    "Housing Financial Literacy Act": "Directs HUD to include financial "
                "literacy/homebuyer counseling info with mortgage-related "
                "notices. Peters added 2026-07-09 (E13) -- ACU's lobbying "
                "text names this bill only in 117th-Congress filings "
                "(2022-2023 Q1, S.1490); Peters' actual press release is "
                "for the 118th-Congress reintroduction (S.4542, 2024), "
                "which ACU's filings never name -- a lobbying-text gap "
                "during the exact Congress the release covers.",
}


def load_csv(path):
    return list(csv.DictReader(path.open()))


def build_contributions():
    rows = load_csv(CONTRIB_CSV)
    return [{
        "member": r["member"],
        "date": r["contribution_date"],
        "amount": float(r["amount_num"]),
        "payer": r["contributor_name"],
        "payee": r["payee_name"],
        "lda_url": r["lda_url"],
    } for r in rows]


def build_press():
    rows = load_csv(PRESS_CSV)
    return [{
        "member": r["member"],
        "date": r["date"],
        "title": r["title"],
        "url": r["url"],
        "chamber": r["chamber"],
    } for r in rows if r["date"]]


# LDA filing_period strings -> (start month/day, end month/day). Filings are
# quarterly (H1/H2 "Mid-Year"/"Year-End" only appear pre-2008, not in this
# corpus's 2022+ window) -- see docs/senate_db.md for the full vocabulary.
QUARTER_BOUNDS = {
    "1st Quarter (Jan 1 - Mar 31)": ((1, 1), (3, 31)),
    "2nd Quarter (Apr 1 - June 30)": ((4, 1), (6, 30)),
    "3rd Quarter (July 1 - Sep 30)": ((7, 1), (9, 30)),
    "4th Quarter (Oct 1 - Dec 31)": ((10, 1), (12, 31)),
}


def quarter_span(filing_year, filing_period):
    bounds = QUARTER_BOUNDS.get(filing_period)
    if not bounds:
        return None, None
    (sm, sd), (em, ed) = bounds
    y = int(filing_year)
    return f"{y}-{sm:02d}-{sd:02d}", f"{y}-{em:02d}-{ed:02d}"


def build_lobbying():
    """One row per (member, quarter) BAND, not per filing -- a filing covers
    a full quarter, and members with >1 tracked bill (e.g. Barr: TABS +
    UDAAP; Fitzgerald: 3 bills) can have multiple filings landing in the
    same quarter, which would otherwise draw overlapping ticks/bands for a
    single quarter. Bills matched in that quarter are merged into one row
    (bill_labels: list) so the band tooltip can show all of them."""
    rows = load_csv(LOBBYING_CSV)
    by_quarter = {}
    for r in rows:
        if r["description_excerpt"] == "NO MATCHES" or not r["dt_posted"]:
            continue
        q_start, q_end = quarter_span(r["filing_year"], r["filing_period"])
        if not q_start:
            continue
        key = (r["member"], r["filing_year"], r["filing_period"])
        entry = by_quarter.setdefault(key, {
            "member": r["member"],
            "quarter_start": q_start,
            "quarter_end": q_end,
            "filing_period": r["filing_period"],
            "filing_year": r["filing_year"],
            "bills": [],
        })
        entry["bills"].append({
            "bill_label": r["bill_label"],
            "excerpt": r["description_excerpt"],
            "lda_url": r["lda_url"],
        })
    return list(by_quarter.values())


def build_bill_dates():
    rows = load_csv(BILL_DATES_CSV)
    out = []
    for r in rows:
        if not r["introduced_date"]:
            continue
        out.append({
            "member": r["member"],
            "date": r["introduced_date"],
            "bill_label": r["bill_label"],
            "bill_number": f"{r['bill_type']}.{r['number']} ({r['congress']}th Congress)",
            "official_title": r["official_title"],
            "purpose": BILL_PURPOSES.get(r["bill_label"], ""),
            "sponsor": r["sponsor_name"],
            "latest_action_date": r["latest_action_date"],
            "latest_action_text": r["latest_action_text"],
            "url": r["congress_gov_url"],
        })
    return out


def main():
    data = {
        "members": MEMBERS,
        "colors": COLORS,
        "contributions": build_contributions(),
        "press": build_press(),
        "lobbying": build_lobbying(),
        "billDates": build_bill_dates(),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(data, indent=2))

    js_code = JS_SRC.read_text()
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ACU legislative bench: say-pay-lobby timeline (interactive)</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
  body {{ font-family: -apple-system, Helvetica, Arial, sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 16px; font-weight: 600; margin-bottom: 2px; }}
  .subtitle {{ font-size: 12px; color: #666; margin-bottom: 14px; }}
  .caption {{ font-size: 11px; color: #666; max-width: 1400px; margin-top: 10px; line-height: 1.5; }}
  .tooltip {{
    position: absolute; pointer-events: auto; background: white;
    border: 1px solid #ccc; border-radius: 4px; padding: 8px 10px;
    font-size: 12px; max-width: 340px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    line-height: 1.4;
  }}
  .tooltip b {{ display: block; margin-bottom: 3px; }}
  .tooltip a {{ color: #1a5fb4; }}
  .lane-label {{ font-size: 12px; font-weight: 600; }}
  .legend text {{ font-size: 11px; }}
  .axis text {{ font-size: 11px; }}
  .contrib-dot, .press-mark, .lobbying-tick, .bill-star, .lane-bg, .lane-label {{
    transition: opacity 0.15s ease;
  }}
</style>
</head>
<body>
<h1>ACU legislative bench: contributions vs. press mentions vs. lobbying filings vs. bill introductions</h1>
<div class="subtitle">Interactive companion to bench_timeline_chart.png -- hover any marker for source detail. Click a legend swatch to show/hide that marker type; hover or click a member's lane to highlight it (click again to release). Same 4 derived CSVs, same 10 members.</div>
<div id="chart"></div>
<div class="caption">
  Contributions: ACU registrant_id=11322 LD-203 FECA items, derived/bench_contributions.csv.
  Press mentions: derived_client_press_mentions join (entity 644/645, deduped), derived/bench_press_releases.csv.
  Lobbying: ACU Senate filings matching each member's bill title, derived/bench_lobbying_filings.csv.
  Bill-introduction dates: Congress.gov API, derived/bench_bill_dates.csv, web-sourced 2026-07-08 -- NOT corpus evidence, see log.md.
  Beatty's lane has contributions + a press mention but zero lobbying filings -- the documented E7 triple break (evidence.md).
</div>
<script>
const DATA = {json.dumps(data)};
</script>
<script>
{js_code}
</script>
</body>
</html>
"""
    OUT_HTML.write_text(html)

    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
