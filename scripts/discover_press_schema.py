"""Schema discovery for the congressional press-release JSONL.

Walks every record under data/congress_press/, building a field-level inventory
(types, null rates, examples) and answering the questions that drive the schema:
bioguide_id coverage, url uniqueness (the natural dedup key), date format/range,
member-metadata distributions, text length, and cross-file duplicate urls.

Usage: python scripts/discover_press_schema.py
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path("data/congress_press")


def files():
    yield from sorted(ROOT.glob("20[0-9][0-9]/*.jsonl"))
    yield from sorted(ROOT.glob("*.jsonl"))


def walk(obj, path, schema):
    info = schema[path]
    info["count"] += 1
    if obj is None:
        info["null"] += 1
        return
    info["types"][type(obj).__name__] += 1
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}" if path else k, schema)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, f"{path}[]", schema)
    elif len(info["examples"]) < 3:
        info["examples"].append(str(obj)[:60])


def main():
    schema = defaultdict(lambda: {"count": 0, "null": 0, "types": Counter(), "examples": []})
    n = 0
    urls = set()
    dup_urls = 0
    bio_null = 0
    bioguides = set()
    parties, chambers = Counter(), Counter()
    states = Counter()
    scrapers = Counter()
    date_sources = Counter()
    dates = []
    textlens = []
    title_null = 0

    for fp in files():
        with open(fp) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                n += 1
                walk(rec, "", schema)
                u = rec.get("url")
                if u in urls:
                    dup_urls += 1
                else:
                    urls.add(u)
                m = rec.get("member") or {}
                if m.get("bioguide_id"):
                    bioguides.add(m["bioguide_id"])
                else:
                    bio_null += 1
                parties[m.get("party")] += 1
                chambers[m.get("chamber")] += 1
                states[m.get("state")] += 1
                scrapers[rec.get("scraper")] += 1
                date_sources[rec.get("date_source")] += 1
                d = rec.get("date")
                if d:
                    dates.append(d)
                if not rec.get("title"):
                    title_null += 1
                t = rec.get("text") or ""
                textlens.append(len(t))

    print(f"total records: {n:,}\n")
    print("FIELD INVENTORY")
    for path in sorted(schema):
        i: dict = schema[path]
        types = ",".join(f"{t}:{c}" for t, c in i["types"].most_common())
        nullpct = 100 * i["null"] / i["count"] if i["count"] else 0
        print(f"  {path:<26} n={i['count']:<8} null={nullpct:4.1f}%  {types}")
        if i["examples"]:
            print(f"  {'':<26}   e.g. {i['examples']}")

    print(f"\nURL uniqueness: {len(urls):,} distinct / {n:,} records  (dup urls: {dup_urls:,})")
    print(f"bioguide_id missing: {bio_null:,} ({100*bio_null/n:.1f}%)")
    print(f"title missing: {title_null:,} ({100*title_null/n:.1f}%)")
    dates.sort()
    print(f"date range: {dates[0]} .. {dates[-1]}  (n with date={len(dates):,})")
    print(f"date_source: {date_sources.most_common()}")
    import statistics
    print(f"text length: min={min(textlens)} max={max(textlens):,} "
          f"mean={statistics.mean(textlens):.0f} median={statistics.median(textlens):.0f}")
    print(f"parties: {parties.most_common()}")
    print(f"chambers: {chambers.most_common()}")
    print(f"distinct states: {len(states)}; distinct scrapers: {len(scrapers)}")
    print(f"distinct bioguide_ids (members): {len(bioguides):,}")


if __name__ == "__main__":
    main()
