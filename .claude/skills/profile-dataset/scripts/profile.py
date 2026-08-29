"""Profile an unknown structured dataset before ingesting it.

Walks JSON / JSONL / XML / CSV records and reports a path-level schema (types,
null/empty rates, list cardinality, examples), flags candidate keys (scalar
fields that are ~unique), and — with --key/--name — runs the key-integrity check
that tells you whether an id is a clean stable key or needs entity resolution.

Stdlib only. Examples:
    python profile.py data/senate/2025/filings/filings_2025.json
    python profile.py 'data/congress_press/2025/*.jsonl' --format jsonl --sample 2000
    python profile.py 'data/house/2025_1stQuarter_XML/*.xml'   # XML: 1 record/file; pass fewer files to sample
    python profile.py data/...json --key registrant.id --name registrant.name
"""

import argparse
import csv
import glob
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path

CAP = 500_000  # max distinct values tracked per path (bounds memory)


# --- record loaders ---------------------------------------------------------
def detect_format(paths):
    ext = Path(paths[0]).suffix.lower()
    return {".json": "json", ".jsonl": "jsonl", ".ndjson": "jsonl",
            ".xml": "xml", ".csv": "csv"}.get(ext, "json")


def xml_to_obj(elem):
    """Element -> JSON-like: leaf->text|None, else dict (repeats become lists)."""
    children = list(elem)
    if not children:
        t = (elem.text or "").strip()
        return t or None
    out = {}
    for c in children:
        v = xml_to_obj(c)
        if c.tag in out:
            if not isinstance(out[c.tag], list):
                out[c.tag] = [out[c.tag]]
            out[c.tag].append(v)
        else:
            out[c.tag] = v
    return out


def records(paths, fmt, sample, skipped):
    """Yield up to `sample` records per file (0 = all; XML is 1 record/file).

    Unparseable files are recorded in `skipped` (list of (path, error)) and
    reported by the caller — never silently dropped.
    """
    for p in paths:
        try:
            if fmt == "json":
                data = json.load(open(p))
                data = data if isinstance(data, list) else [data]
                yield from (data[:sample] if sample else data)
            elif fmt == "jsonl":
                with open(p) as f:
                    for i, line in enumerate(f):
                        if sample and i >= sample:
                            break
                        line = line.strip()
                        if line:
                            yield json.loads(line)
            elif fmt == "xml":
                yield xml_to_obj(ET.parse(p).getroot())
            elif fmt == "csv":
                with open(p, newline="") as f:
                    for i, row in enumerate(csv.DictReader(f)):
                        if sample and i >= sample:
                            break
                        yield dict(row)
        except (json.JSONDecodeError, ET.ParseError, UnicodeDecodeError, OSError) as e:
            skipped.append((p, f"{type(e).__name__}: {e}"))


# --- profiling --------------------------------------------------------------
def walk(obj, path, schema):
    i = schema[path]
    i["count"] += 1
    if obj is None or obj == "":
        i["empty"] += 1
        return
    i["types"][type(obj).__name__] += 1
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}" if path else k, schema)
    elif isinstance(obj, list):
        i["list_lens"][len(obj)] += 1
        for v in obj:
            walk(v, f"{path}[]", schema)
    else:
        if len(i["examples"]) < 3:
            i["examples"].append(str(obj)[:55])
        vals = i["values"]
        if vals is not None:
            vals.add(obj if isinstance(obj, (str, int, float, bool)) else str(obj))
            if len(vals) > CAP:
                i["values"] = None  # stop tracking (too high-cardinality)


def get(obj, dotted):
    cur = obj
    for part in dotted.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return None
    return cur


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+", help="file(s) or glob(s)")
    ap.add_argument("--format", choices=["auto", "json", "jsonl", "xml", "csv"], default="auto")
    ap.add_argument("--sample", type=int, default=0, help="max records per file (0=all)")
    ap.add_argument("--key", help="dotted path of a candidate id field")
    ap.add_argument("--name", help="dotted path of a name field to test --key against")
    args = ap.parse_args()

    paths = [f for pat in args.paths for f in sorted(glob.glob(pat))] or args.paths
    fmt = detect_format(paths) if args.format == "auto" else args.format
    print(f"format={fmt}  files={len(paths)}  sample/file={args.sample or 'all'}", file=sys.stderr)
    if fmt == "xml" and args.sample:
        print("note: XML is one record per file; --sample has no effect (pass fewer files instead)",
              file=sys.stderr)
    if bool(args.key) != bool(args.name):
        print("warning: --key and --name must be given together; key-integrity check skipped",
              file=sys.stderr)

    schema = defaultdict(lambda: {"count": 0, "empty": 0, "types": Counter(),
                                  "list_lens": Counter(), "examples": [], "values": set()})
    # key check compares normalized names (case/whitespace) but shows raw variants
    key2names, key2raw, name2keys = defaultdict(set), defaultdict(set), defaultdict(set)
    n, skipped = 0, []
    for rec in records(paths, fmt, args.sample, skipped):
        n += 1
        walk(rec, "", schema)
        if args.key and args.name:
            k, nm = get(rec, args.key), get(rec, args.name)
            if k is not None and nm is not None:
                norm = str(nm).strip().lower()
                key2names[k].add(norm)
                key2raw[k].add(str(nm)[:40])
                name2keys[norm].add(k)

    if skipped:
        print(f"WARNING: skipped {len(skipped)} of {len(paths)} files (unparseable):",
              file=sys.stderr)
        for p, err in skipped[:5]:
            print(f"  {p}: {err}", file=sys.stderr)
        if len(skipped) > 5:
            print(f"  ... and {len(skipped) - 5} more", file=sys.stderr)

    print(f"\n{'='*70}\nSCHEMA  ({n:,} records)\n{'='*70}")
    for path in sorted(schema):
        i: dict = schema[path]
        types = ",".join(f"{t}:{c}" for t, c in i["types"].most_common())
        emptypct = 100 * i["empty"] / i["count"] if i["count"] else 0
        line = f"{path:<46} n={i['count']:<7} empty={emptypct:4.1f}%  {types}"
        if i["list_lens"]:
            line += f"  len[max={max(i['list_lens'])}]"
        print(line)
        if i["examples"]:
            print(f"{'':<46}   e.g. {i['examples']}")

    print(f"\n{'='*70}\nCANDIDATE KEYS (scalar fields that are ~unique)\n{'='*70}")
    found = False
    for path in sorted(schema):
        i: dict = schema[path]
        vals, nonnull = i["values"], i["count"] - i["empty"]
        if vals is None:
            print(f"  {path:<44} high-cardinality (>{CAP:,} distinct) — likely a key/free text")
            found = True
        elif nonnull and len(vals) / nonnull > 0.999 and nonnull > 1:
            print(f"  {path:<44} UNIQUE  ({len(vals):,}/{nonnull:,} distinct) — candidate primary key")
            found = True
    if not found:
        print("  (none — no scalar field is ~unique in this sample)")

    if args.key and args.name:
        print(f"\n{'='*70}\nKEY INTEGRITY: {args.key}  vs  {args.name}"
              f"  (names compared case/whitespace-insensitively)\n{'='*70}")
        multi_name = {k: v for k, v in key2names.items() if len(v) > 1}
        multi_key = {k: v for k, v in name2keys.items() if len(v) > 1}
        print(f"  distinct {args.key}: {len(key2names):,}; distinct {args.name}: {len(name2keys):,}")
        print(f"  {args.key} values mapping to >1 {args.name}: {len(multi_name):,}"
              f"  ->  {'CLEAN key' if not multi_name else 'AMBIGUOUS'}")
        for k in list(multi_name)[:5]:
            print(f"      {k!r}: {sorted(key2raw[k])[:4]}")
        print(f"  {args.name} values mapping to >1 {args.key}: {len(multi_key):,}"
              f"  ->  {'1:1' if not multi_key else 'name reused across ids (dedupe/ER needed)'}")
        for k, v in list(multi_key.items())[:5]:
            print(f"      {k!r}: {sorted(v)[:6]}")


if __name__ == "__main__":
    main()
