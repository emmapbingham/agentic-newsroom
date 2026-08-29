"""Deep schema discovery for the House LDA XML data.

Samples files from every House directory, builds a path-level tag inventory
(split by root type: LOBBYINGDISCLOSURE1 registrations vs LOBBYINGDISCLOSURE2
quarterly reports), records repeating-element cardinality and empty rates, and
RESOLVES the Senate<->House linking by testing senateID/houseID against the IDs
already loaded in db/gain.db.

Usage: python scripts/discover_house_schema.py [--sample N] [--db db/gain.db]
"""

import argparse
import sqlite3
import xml.etree.ElementTree as ET
from collections import defaultdict, Counter
from pathlib import Path

HOUSE = Path("data/house")


def text(elem):
    t = (elem.text or "").strip()
    return t or None


def walk(elem, path, schema):
    """Record path stats. Leaf = no child elements."""
    children = list(elem)
    info = schema[path]
    info["count"] += 1
    if not children:
        v = text(elem)
        if v is None:
            info["empty"] += 1
        elif len(info["examples"]) < 3:
            info["examples"].append(v[:55])
        return
    # container: record child-tag cardinality (max repeats under this parent)
    tag_counts = Counter(c.tag for c in children)
    for tag, n in tag_counts.items():
        info["child_max"][tag] = max(info["child_max"].get(tag, 0), n)
    for c in children:
        walk(c, f"{path}/{c.tag}", schema)


def new_schema():
    return defaultdict(lambda: {
        "count": 0, "empty": 0, "examples": [], "child_max": {},
    })


def print_schema(title, schema, n_files):
    print(f"\n{'='*72}\n{title}  (sampled {n_files} files)\n{'='*72}")
    for path in sorted(schema):
        i = schema[path]
        emptypct = 100 * i["empty"] / i["count"] if i["count"] else 0
        depth = path.count("/")
        short = path.split("/")[-1]
        line = f"{'  '*depth}{short:<28} n={i['count']:<6} empty={emptypct:3.0f}%"
        if i["child_max"]:
            reps = {t: m for t, m in i["child_max"].items() if m > 1}
            if reps:
                line += f"  repeats={reps}"
        print(line)
        if i["examples"]:
            print(f"{'  '*depth}{'':<28}   e.g. {i['examples']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=1500,
                    help="max files sampled per directory")
    ap.add_argument("--db", default="db/gain.db")
    args = ap.parse_args()

    reg_schema = new_schema()
    qtr_schema = new_schema()
    reg_files = qtr_files = 0
    report_types = Counter()         # LD2 reportType
    reg_types = Counter()            # LD1 regType
    senate_ids, house_ids = [], []   # raw samples for format analysis

    dirs = sorted(p for p in HOUSE.iterdir() if p.is_dir())
    for d in dirs:
        files = sorted(d.glob("*.xml"))[: args.sample]
        for fp in files:
            try:
                root = ET.parse(fp).getroot()
            except ET.ParseError:
                continue
            if root.tag == "LOBBYINGDISCLOSURE1":
                walk(root, root.tag, reg_schema); reg_files += 1
                rt = root.findtext("regType")
                if rt and rt.strip():
                    reg_types[rt.strip()] += 1
            else:
                walk(root, root.tag, qtr_schema); qtr_files += 1
                rt = root.findtext("reportType")
                if rt and rt.strip():
                    report_types[rt.strip()] += 1
            sid = (root.findtext("senateID") or "").strip()
            hid = (root.findtext("houseID") or "").strip()
            if sid and len(senate_ids) < 4000:
                senate_ids.append(sid)
            if hid and len(house_ids) < 4000:
                house_ids.append(hid)

    print_schema("LOBBYINGDISCLOSURE1 (registrations)", reg_schema, reg_files)
    print_schema("LOBBYINGDISCLOSURE2 (quarterly)", qtr_schema, qtr_files)
    print(f"\nregType distribution (LD1): {reg_types.most_common()}")
    print(f"reportType distribution (LD2): {report_types.most_common()}")

    # ---- Senate <-> House linking resolution -----------------------------
    print(f"\n{'='*72}\nSENATE<->HOUSE LINKING\n{'='*72}")
    print(f"senateID samples: {senate_ids[:6]}")
    print(f"houseID samples:  {house_ids[:6]}")
    print(f"senateID has '-' suffix: "
          f"{sum('-' in x for x in senate_ids)}/{len(senate_ids)}")

    sid_prefix = [x.split("-")[0] for x in senate_ids]
    con = sqlite3.connect(args.db)
    reg_ids = {str(r[0]) for r in con.execute("SELECT id FROM senate_registrants")}
    house_reg_ids = {str(r[0]) for r in con.execute(
        "SELECT house_registrant_id FROM senate_registrants WHERE house_registrant_id IS NOT NULL")}
    print(f"\nsenate_registrants: {len(reg_ids)} ids, "
          f"{len(house_reg_ids)} with house_registrant_id")

    pre_in_regid = sum(p in reg_ids for p in sid_prefix)
    print(f"senateID-prefix matches senate_registrants.id:        "
          f"{pre_in_regid}/{len(sid_prefix)}")
    hid_in_housereg = sum(h in house_reg_ids for h in house_ids)
    print(f"houseID matches senate_registrants.house_registrant_id:"
          f" {hid_in_housereg}/{len(house_ids)}")
    # also test: does houseID (or a prefix of it) match house_registrant_id?
    hid_prefix6 = sum(h[:6] in house_reg_ids or h[:5] in house_reg_ids for h in house_ids)
    print(f"houseID[:5/6]-prefix matches house_registrant_id:     "
          f"{hid_prefix6}/{len(house_ids)}")
    con.close()


if __name__ == "__main__":
    main()
