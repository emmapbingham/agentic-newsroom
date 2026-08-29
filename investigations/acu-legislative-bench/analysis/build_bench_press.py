#!/usr/bin/env python3
"""Timeline data, part 2/3: ACU press-release mentions for the 11 bench
members (Barr + E1-E9 + Peters, added 2026-07-09 per E13), from
derived_client_press_mentions (entity_id 644/645, ACU's two canonical-name
variants -- see evidence.md E0 on why they're two rows in the alias index
but one registrant for money/lobbying).

Deduped on (bioguide, url) -- ACU has two canonical-name variants in the alias
index (entity_id 644/645, see evidence.md E0) that can both match the same
release. After dedup, per-member counts match evidence.md's hand-verified
E1-E9 mention counts exactly. This is still the raw mention join, not
evidence.md's "roster-only vs. named-quote" characterization of each mention
-- use the `title`/`url` columns to cross-check which releases carry a named
ACU quote vs. a roster-only listing.

Re-run: python3 investigations/acu-legislative-bench/analysis/build_bench_press.py
Requires db/gain.db (read-only). Writes derived/bench_press_releases.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
OUT = Path(__file__).resolve().parent.parent / "derived" / "bench_press_releases.csv"

ACU_ENTITY_IDS = (644, 645)

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
SELECT bioguide_id, member_name, chamber, date, url, title, canonical_name
FROM derived_client_press_mentions
WHERE entity_id IN (644, 645)
  AND bioguide_id IN ({placeholders})
ORDER BY bioguide_id, date
"""


def main() -> None:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    placeholders = ",".join("?" * len(MEMBERS))
    rows = con.execute(QUERY.format(placeholders=placeholders), list(MEMBERS.keys())).fetchall()
    con.close()

    # ACU has two canonical-name variants in the alias index (entity_id 644
    # and 645, see evidence.md E0) that can both match the same release --
    # dedup on (bioguide, url) so one real release isn't double-counted.
    seen = set()
    out_rows = []
    for bioguide, member_name, chamber, date, url, title, canonical_name in rows:
        key = (bioguide, url)
        if key in seen:
            continue
        seen.add(key)
        out_rows.append({
            "member": MEMBERS[bioguide],
            "bioguide": bioguide,
            "member_name_as_filed": member_name,
            "chamber": chamber,
            "date": date,
            "title": title,
            "url": url,
            "acu_canonical_name_matched": canonical_name,
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f"{len(out_rows)} press mentions across {len(MEMBERS)} members")
    for m in MEMBERS.values():
        sub = [r for r in out_rows if r["member"] == m]
        print(f"  {m}: {len(sub)} mentions")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
