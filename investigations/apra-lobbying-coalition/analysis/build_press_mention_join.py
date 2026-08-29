#!/usr/bin/env python3
"""E9: join the 345-entity APRA/ADPPA roster against derived_client_alias_index
/ derived_client_press_mentions -- reused infrastructure from the
client-press-mention-gap screen (screens/client-press-mention-gap/screen.sql),
NOT rebuilt from scratch. Covers only the roster's raw client names that
already have Senate-client alias review (>=$1M total disclosed income,
2022-2026Q1) -- roughly a third of the roster. The remaining ~256 raw names
(smaller filers, never reviewed) are explicitly out of scope for this script;
per editor instruction (2026-07-08) do not hand-roll alias review for them
without further direction.

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_press_mention_join.py
Requires db/gain.db (read-only). Writes derived/press_mention_join.csv.
"""
import csv
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[3] / "db" / "gain.db"
ROSTER = Path(__file__).resolve().parent.parent / "derived" / "roster_corrected_deduplicated.csv"
OUT = Path(__file__).resolve().parent.parent / "derived" / "press_mention_join.csv"


def main() -> None:
    roster = list(csv.DictReader(ROSTER.open()))
    name_to_entity = {}
    for r in roster:
        for n in r["raw_names_merged"].split("; "):
            name_to_entity[n.strip()] = r["entity"]
    roster_names = set(name_to_entity)

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    alias_rows = con.execute(
        "SELECT DISTINCT canonical_name, status FROM derived_client_alias_index"
    ).fetchall()
    alias_status = {}
    for canonical_name, status in alias_rows:
        # a canonical_name can have both candidate and rejected rows across
        # different aliases; treat as reviewed-usable if ANY row is 'candidate'
        if canonical_name not in alias_status or status == "candidate":
            alias_status[canonical_name] = status

    mention_counts = con.execute(
        "SELECT canonical_name, count(*) n, count(DISTINCT bioguide_id) n_members, "
        "max(date) most_recent FROM derived_client_press_mentions GROUP BY canonical_name"
    ).fetchall()
    mentions_by_name = {r[0]: (r[1], r[2], r[3]) for r in mention_counts}

    con.close()

    raw_rows = []
    for raw_name in sorted(roster_names):
        entity = name_to_entity[raw_name]
        if raw_name not in alias_status:
            coverage = "not_reviewed"
        elif alias_status[raw_name] == "rejected_too_generic":
            coverage = "rejected_too_generic"
        else:
            coverage = "reviewed"
        n_mentions, n_members, most_recent = mentions_by_name.get(raw_name, (0, 0, None))
        raw_rows.append({
            "roster_entity": entity,
            "raw_client_name": raw_name,
            "alias_coverage": coverage,
            "n_press_mentions": n_mentions,
            "n_distinct_members_mentioning": n_members,
            "most_recent_mention_date": most_recent or "",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(raw_rows[0].keys()))
        w.writeheader()
        w.writerows(raw_rows)

    # entity-level rollup: an entity counts as covered/reviewed if ANY of its
    # raw name variants was reviewed, and mentions sum across variants (the
    # roster's own dedup, e.g. AMAZON.COM SERVICES LLC / INC., can otherwise
    # split one company's real mentions across a zero-mention "twin" row).
    by_entity = {}
    for r in raw_rows:
        e = by_entity.setdefault(r["roster_entity"], {
            "roster_entity": r["roster_entity"], "coverage_statuses": set(),
            "n_press_mentions": 0, "n_distinct_members_mentioning": 0,
            "most_recent_mention_date": "",
        })
        e["coverage_statuses"].add(r["alias_coverage"])
        e["n_press_mentions"] += r["n_press_mentions"]
        e["n_distinct_members_mentioning"] = max(
            e["n_distinct_members_mentioning"], r["n_distinct_members_mentioning"])
        if r["most_recent_mention_date"] > e["most_recent_mention_date"]:
            e["most_recent_mention_date"] = r["most_recent_mention_date"]

    entity_rows = []
    for e in by_entity.values():
        statuses = e.pop("coverage_statuses")
        if "reviewed" in statuses:
            coverage = "reviewed"
        elif "rejected_too_generic" in statuses:
            coverage = "rejected_too_generic"
        else:
            coverage = "not_reviewed"
        e["alias_coverage"] = coverage
        entity_rows.append(e)
    entity_rows.sort(key=lambda e: -e["n_press_mentions"])

    entity_out = OUT.parent / "press_mention_join_by_entity.csv"
    with entity_out.open("w", newline="") as f:
        fieldnames = ["roster_entity", "alias_coverage", "n_press_mentions",
                      "n_distinct_members_mentioning", "most_recent_mention_date"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for e in entity_rows:
            w.writerow({k: e[k] for k in fieldnames})

    n_reviewed = sum(1 for r in raw_rows if r["alias_coverage"] == "reviewed")
    n_rejected = sum(1 for r in raw_rows if r["alias_coverage"] == "rejected_too_generic")
    n_not_reviewed = sum(1 for r in raw_rows if r["alias_coverage"] == "not_reviewed")
    n_with_mentions = sum(1 for e in entity_rows if e["n_press_mentions"] > 0)
    n_entities_reviewed = sum(1 for e in entity_rows if e["alias_coverage"] == "reviewed")
    print(f"{len(raw_rows)} roster raw client names / {len(entity_rows)} deduplicated entities")
    print(f"  raw names reviewed (usable alias): {n_reviewed}")
    print(f"  raw names rejected_too_generic: {n_rejected}")
    print(f"  raw names not_reviewed (below $1M threshold, out of scope this pass): {n_not_reviewed}")
    print(f"  entities with >=1 raw name reviewed: {n_entities_reviewed}")
    print(f"  entities with >=1 press mention: {n_with_mentions}")
    print(f"wrote {OUT}")
    print(f"wrote {entity_out}")


if __name__ == "__main__":
    main()
