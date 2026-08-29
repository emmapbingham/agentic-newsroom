#!/usr/bin/env python3
"""Timeline data, part 1/3: item-level (exact-date) LD-203 contributions from
ACU (registrant_id=11322, the merged-entity registrant used throughout E0-E9;
see evidence.md E0 for why the alias-variant entity 645 doesn't separately
resolve) honoring each of the 11 bench members (Barr + the 9 drilled in
E1-E9, + Peters added 2026-07-09 per E13), restricted to confidence>=0.9
honoree matches per case convention.

One row per contribution item (not aggregated), so it can sit on a timeline
next to press releases and lobbying filing dates.

Re-run: python3 investigations/acu-legislative-bench/analysis/build_bench_contributions.py
Requires db/gain.db (read-only). Writes derived/bench_contributions.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "bench_contributions.csv"

ACU_REGISTRANT_ID = 11322

MEMBERS = {
    "B001282": "Barr",
    "C001096": "Cramer",
    "S001184": "Scott",
    "B001319": "Britt",
    "E000294": "Emmer",
    "F000471": "Fitzgerald",
    "B001305": "Budd",
    "B001281": "Beatty",
    "V000130": "Vargas",
    "G000581": "Gonzalez",
    "P000595": "Peters",
}

QUERY = """
SELECT DISTINCT hm.bioguide, sci.contributor_name, sci.payee_name, sci.date, sci.amount,
       sci.amount_num, sci.contribution_type, sci.honoree_name, sci.filing_uuid,
       scf.filing_year, scf.filing_period_display
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
JOIN honoree_member_map hm ON hm.honoree_name = sci.honoree_name
WHERE scf.registrant_id = ?
  AND hm.bioguide IN ({placeholders})
  AND hm.confidence >= 0.9
  AND sci.contribution_type = 'feca'
  AND sci.amount_num > 0
ORDER BY hm.bioguide, sci.date
"""


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    placeholders = ",".join("?" * len(MEMBERS))
    rows = con.execute(
        QUERY.format(placeholders=placeholders),
        [ACU_REGISTRANT_ID] + list(MEMBERS.keys()),
    ).fetchall()
    con.close()

    # Case convention (queries.sql q-*1 templates): dedup on
    # (contributor_name, payee_name, date, amount_num), NOT on filing_uuid --
    # the same real-world contribution is sometimes re-reported byte-identical
    # across filer copies with a different filing_uuid and/or honoree_name
    # spelling variant (e.g. "Sen. Tim Scott" vs "Tim Scott", both mapping to
    # S001184). Keep the first-seen filing_uuid/honoree_name for citation.
    seen = set()
    out_rows = []
    for (bioguide, contributor_name, payee_name, date, amount, amount_num,
         ctype, honoree_name, filing_uuid, fy, fp) in rows:
        key = (bioguide, contributor_name, payee_name, date, amount_num)
        if key in seen:
            continue
        seen.add(key)
        out_rows.append({
            "member": MEMBERS[bioguide],
            "bioguide": bioguide,
            "contribution_date": date,
            "amount": amount,
            "amount_num": amount_num,
            "contribution_type": ctype,
            "contributor_name": contributor_name,
            "payee_name": payee_name,
            "honoree_name_as_filed": honoree_name,
            "filing_year": fy,
            "filing_period": fp,
            "filing_uuid": filing_uuid,
            "lda_url": f"https://lda.gov/filings/public/contribution/{filing_uuid}/print/",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f"{len(out_rows)} contribution items across {len(MEMBERS)} members")
    for m in MEMBERS.values():
        sub = [r for r in out_rows if r["member"] == m]
        total = sum(r["amount_num"] or 0 for r in sub)
        print(f"  {m}: {len(sub)} items, ${total:,.2f}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
