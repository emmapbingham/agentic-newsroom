"""Deep schema discovery for the Senate LDA data.

Walks every record in filings_*.json and contributions_*.json, building a
path-level schema map (types seen, null counts, example values) and resolving
the registrant ID-namespace question (5-digit filing IDs vs 9-digit
contribution IDs) so we can design the SQLite schema with confidence.

Usage: python scripts/discover_senate_schema.py [year ...]
       (defaults to all years found under data/senate/)
"""

import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

DATA = Path("data/senate")


def walk(obj, path, schema):
    """Record type/null/example info for each structural path."""
    info = schema[path]
    info["count"] += 1
    if obj is None:
        info["null"] += 1
        return
    t = type(obj).__name__
    info["types"][t] += 1
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}" if path else k, schema)
    elif isinstance(obj, list):
        info["list_lens"][len(obj)] += 1
        for v in obj:
            walk(v, f"{path}[]", schema)
    else:
        if len(info["examples"]) < 3:
            s = str(obj)
            info["examples"].append(s[:60])


def new_schema():
    return defaultdict(lambda: {
        "count": 0, "null": 0,
        "types": Counter(), "list_lens": Counter(), "examples": [],
    })


def print_schema(title, schema):
    print(f"\n{'='*70}\n{title}\n{'='*70}")
    for path in sorted(schema):
        i = schema[path]
        types = ",".join(f"{t}:{n}" for t, n in i["types"].most_common())
        nullpct = 100 * i["null"] / i["count"] if i["count"] else 0
        line = f"{path:<55} n={i['count']:<8} null={nullpct:4.0f}%  {types}"
        if i["list_lens"]:
            lens = i["list_lens"]
            line += f"  len[min={min(lens)},max={max(lens)}]"
        print(line)
        if i["examples"]:
            print(f"{'':<55}   e.g. {i['examples']}")


def main():
    years = sys.argv[1:] or sorted(
        p.name for p in DATA.iterdir() if p.is_dir() and p.name.isdigit()
    )
    print(f"Years: {years}")

    filing_schema = new_schema()
    contrib_schema = new_schema()

    # ID-namespace investigation
    filing_reg_ids = set()
    contrib_reg_ids = set()
    reg_name_to_ids = defaultdict(set)          # lowered name -> {ids} (both sources)
    reg_id_to_house = defaultdict(set)           # registrant.id -> {house_registrant_id}
    client_id_eq_client_id = Counter()           # does client.id == client.client_id?
    filing_type_counts = Counter()
    contrib_type_counts = Counter()
    filing_total = contrib_total = 0

    for y in years:
        fp = DATA / y / "filings" / f"filings_{y}.json"
        if fp.exists():
            print(f"  loading {fp} ...", flush=True)
            data = json.load(open(fp))
            filing_total += len(data)
            for rec in data:
                walk(rec, "", filing_schema)
                filing_type_counts[rec.get("filing_type")] += 1
                r = rec.get("registrant") or {}
                if r.get("id") is not None:
                    filing_reg_ids.add(r["id"])
                    if r.get("name"):
                        reg_name_to_ids[r["name"].strip().lower()].add(r["id"])
                    reg_id_to_house[r["id"]].add(r.get("house_registrant_id"))
                c = rec.get("client") or {}
                if c:
                    client_id_eq_client_id[c.get("id") == c.get("client_id")] += 1
            del data

        cp = DATA / y / "contributions" / f"contributions_{y}.json"
        if cp.exists():
            print(f"  loading {cp} ...", flush=True)
            data = json.load(open(cp))
            contrib_total += len(data)
            for rec in data:
                walk(rec, "", contrib_schema)
                contrib_type_counts[rec.get("filing_type")] += 1
                r = rec.get("registrant") or {}
                if r.get("id") is not None:
                    contrib_reg_ids.add(r["id"])
                    if r.get("name"):
                        reg_name_to_ids[r["name"].strip().lower()].add(r["id"])
                    reg_id_to_house[r["id"]].add(r.get("house_registrant_id"))
            del data

    print_schema(f"FILINGS schema  (total records={filing_total})", filing_schema)
    print_schema(f"CONTRIBUTIONS schema  (total records={contrib_total})", contrib_schema)

    print(f"\n{'='*70}\nID-NAMESPACE INVESTIGATION\n{'='*70}")
    print(f"filing registrant ids:        {len(filing_reg_ids)}")
    print(f"contribution registrant ids:  {len(contrib_reg_ids)}")
    print(f"intersection:                 {len(filing_reg_ids & contrib_reg_ids)}")

    def lens(ids):
        return Counter(len(str(i)) for i in ids)
    print(f"filing id digit-lengths:      {dict(lens(filing_reg_ids))}")
    print(f"contribution id digit-lengths:{dict(lens(contrib_reg_ids))}")

    # Same registrant NAME appearing under different ids -> namespace bridge
    cross = {n: ids for n, ids in reg_name_to_ids.items() if len(ids) > 1}
    print(f"\nregistrant names mapping to >1 id: {len(cross)} "
          f"(of {len(reg_name_to_ids)} distinct names)")
    for n, ids in list(cross.items())[:8]:
        print(f"   {sorted(ids)}  <- {n!r}")

    print(f"\nclient.id == client.client_id ? {dict(client_id_eq_client_id)}")
    multi_house = {rid: hs for rid, hs in reg_id_to_house.items() if len(hs) > 1}
    print(f"registrant.id mapping to >1 house_registrant_id: {len(multi_house)}")
    for rid, hs in list(multi_house.items())[:5]:
        print(f"   reg {rid} -> house ids {hs}")

    print(f"\nfiling_type distribution (filings):       {filing_type_counts.most_common()}")
    print(f"filing_type distribution (contributions): {contrib_type_counts.most_common()}")


if __name__ == "__main__":
    main()
