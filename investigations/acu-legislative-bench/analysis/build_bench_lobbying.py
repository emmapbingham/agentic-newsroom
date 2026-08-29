#!/usr/bin/env python3
"""Timeline data, part 3/3: ACU's own sworn Senate lobbying-activity text
(registrant_id=11322) that names each bench member's flagship bill by
title/number, one row per quarterly filing. Search fragments are the exact
strings verified per member in evidence.md (E1/EBarr6/E2-E9) -- reused, not
re-derived, so this table stays consistent with the case's cited quotes.

Members/bills with more than one confirmed bill get multiple fragments
(e.g. Fitzgerald has 3, Budd's SBA-bill leg reuses the Cramer/Scott fragment
since it's a shared bill). Beatty's FIRST bill (Fair Hiring in Banking Act)
is INCLUDED with a negative/zero-row result on purpose -- evidence.md E7
found zero matches for that bill despite an unambiguous title. Beatty has a
SECOND bill (Mentor-Protege Program for Small Financial Institutions Act,
added 2026-07-09) that DOES have a lobbying-text match (1 filing) -- her
overall record is a split, not a clean absence; see E7's revision.

Peters (added 2026-07-09 per E13) is a PARTIAL/LAGGED case, not a clean
match like the others: ACU's lobbying text names "Housing Financial
Literacy Act" only in 2022 - 2023 Q1 filings, which is the 117th-Congress
bill (S.1490, Peters' original 2021 sponsorship). His actual press release
("Reintroduces", 2024-06-13) is for a DIFFERENT bill number in the 118th
Congress (S.4542) -- ACU never names that one; the lobbying-text mentions
stop over a year before his reintroduction. Kept as one fragment (title text
is identical across both bills' short titles) but flagged with its own
evidence_ref so the gap is visible in the CSV, not just in evidence.md.

Re-run: python3 investigations/acu-legislative-bench/analysis/build_bench_lobbying.py
Requires db/gain.db (read-only). Writes derived/bench_lobbying_filings.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "bench_lobbying_filings.csv"

ACU_REGISTRANT_ID = 11322

# member, bill_label, search fragment (LIKE, case-insensitive), evidence.md ref
BILL_FRAGMENTS = [
    ("Barr", "Taking Account of Bureaucrats Spending Act (TABS)", "%Taking Account of Bureaucrats Spending%", "EBarr6"),
    ("Barr", "Rectifying UDAAP Act", "%Rectifying UDAAP%", "EBarr6"),
    ("Cramer", "Protecting Access to Credit for Small Businesses Act", "%Protecting Access to Credit for Small Businesses%", "E1"),
    ("Scott", "Protecting Access to Credit for Small Businesses Act", "%Protecting Access to Credit for Small Businesses%", "E2"),
    ("Britt", "Community Bank Relief Act", "%Community Bank Relief%", "E3"),
    ("Emmer", "Anti-CBDC Surveillance State Act", "%Anti-CBDC Surveillance State%", "E4"),
    ("Fitzgerald", "CFPB Accountable to Small Businesses Act", "%CFPB Accountable%", "E5"),
    ("Fitzgerald", "HUMPS Act (Uncertain Methods and Practices)", "%Uncertain Methods and Practices%", "E5"),
    ("Fitzgerald", "Expanding Access to Lending Options Act", "%Expanding Access to Lending Options%", "E5"),
    ("Budd", "Protecting Access to Credit for Small Businesses Act (shared w/ Cramer/Scott)", "%Protecting Access to Credit for Small Businesses%", "E6"),
    ("Beatty", "Fair Hiring in Banking Act (NEGATIVE RESULT -- zero matches, see E7)", "%Fair Hiring%", "E7"),
    # added 2026-07-09: second Beatty bill, editor-identified. ACU's lobbying
    # text names it once (2026 Q1). This is the bill her 2025-06-05 press
    # release is actually about -- see E7's revision.
    ("Beatty", "Advancing the Mentor-Protege Program for Small Financial Institutions Act", "%Mentor-Protege Program for Small Financial%", "E7-correction"),
    ("Vargas", "Credit Union Board Modernization Act", "%Credit Union Board Modernization%", "E8"),
    ("Gonzalez", "Veterans Members Business Loans Act", "%Veterans Member%Business Loan%", "E9"),
    ("Peters", "Housing Financial Literacy Act (117th-Congress text only -- see E13, gap through his actual 118th reintroduction)", "%housing financial literacy%", "E13"),
    # added 2026-07-09 (E16): systematic press-release-vs-bill pass.
    # Budd: genuinely new bill, never tracked before. Vargas: real
    # cosponsorship of a bill already tracked under Fitzgerald (E5) --
    # added again under Vargas so his own press-release/lobbying rows show
    # it (same shared-bill pattern as Cramer/Scott/Budd's SBA-lending bill).
    ("Budd", "Secure Payments Act", "%Secure Payments Act%", "E16"),
    ("Vargas", "Expanding Access to Lending Options Act (shared w/ Fitzgerald)", "%Expanding Access to Lending Options%", "E16"),
]

QUERY = """
SELECT a.filing_uuid, a.description, f.filing_year, f.filing_period_display, f.dt_posted
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE f.registrant_id = ?
  AND a.description LIKE ?
ORDER BY f.filing_year, f.filing_period_display
"""


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    out_rows = []
    for member, bill_label, fragment, ev_ref in BILL_FRAGMENTS:
        rows = con.execute(QUERY, (ACU_REGISTRANT_ID, fragment)).fetchall()
        if not rows:
            out_rows.append({
                "member": member,
                "bill_label": bill_label,
                "evidence_ref": ev_ref,
                "filing_uuid": "",
                "filing_year": "",
                "filing_period": "",
                "dt_posted": "",
                "description_excerpt": "NO MATCHES",
                "lda_url": "",
            })
            continue
        for filing_uuid, description, fy, fp, dt_posted in rows:
            out_rows.append({
                "member": member,
                "bill_label": bill_label,
                "evidence_ref": ev_ref,
                "filing_uuid": filing_uuid,
                "filing_year": fy,
                "filing_period": fp,
                "dt_posted": dt_posted,
                "description_excerpt": (description or "")[:400],
                "lda_url": f"https://lda.gov/filings/public/filing/{filing_uuid}/print/",
            })

    con.close()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f"{len(out_rows)} lobbying-filing rows across {len(BILL_FRAGMENTS)} member-bill pairs")
    for member, bill_label, fragment, ev_ref in BILL_FRAGMENTS:
        n = sum(1 for r in out_rows if r["member"] == member and r["bill_label"] == bill_label
                and r["description_excerpt"] != "NO MATCHES")
        print(f"  {member} / {bill_label[:40]}: {n} filings")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
