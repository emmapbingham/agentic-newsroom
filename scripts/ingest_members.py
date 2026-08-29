"""Build the member<->bioguide crosswalk in db/gain.db.

Ingests the public-domain `unitedstates/congress-legislators` dataset (current +
historical legislators, committees, committee membership) into member_* tables,
then resolves the free-text `senate_contribution_items.honoree_name` to a
bioguide id (honoree_member_map, with method + confidence). This is the bridge
that ties lobbying/contribution money to the press corpus' bioguide_id.

Source-scoped + idempotent. Downloads the source files to
data/congress_legislators/ if missing (see sources/congress-legislators.md).

Usage:
    python scripts/ingest_members.py            # -> db/gain.db
    python scripts/ingest_members.py --refresh  # re-download source files
"""

import argparse
import re
import sqlite3
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml
try:
    Loader = yaml.CSafeLoader
except AttributeError:
    Loader = yaml.SafeLoader

DATA = Path("data/congress_legislators")
SHARED_SCHEMA = Path("scripts/schema_shared.sql")
MEMBERS_SCHEMA = Path("scripts/schema_members.sql")
SOURCE = "members"
TIER = "reference"
BASE = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main"
FILES = ["legislators-current.yaml", "legislators-historical.yaml",
         "committees-current.yaml", "committee-membership-current.yaml"]
# historical members whose last term ended on/after this are eligible for
# honoree name-matching (bounds last-name ambiguity to plausibly-honored people)
MATCH_CUTOFF = "2015-01-01"

HONORIFICS = {"the", "honorable", "hon", "senator", "sen", "representative",
              "rep", "congressman", "congresswoman", "congressmember", "cong",
              "governor", "gov", "president", "vice", "dr", "mr", "mrs", "ms",
              "us", "u.s", "u.s.", "american"}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def download(refresh=False):
    DATA.mkdir(parents=True, exist_ok=True)
    for fn in FILES:
        dest = DATA / fn
        if refresh or not dest.exists():
            print(f"  downloading {fn} ...", flush=True)
            urllib.request.urlretrieve(f"{BASE}/{fn}", dest)


def load(fn):
    return yaml.load(open(DATA / fn), Loader=Loader)


def norm(text):
    """Lowercase, drop parenthetical, strip honorifics + punctuation."""
    if not text:
        return ""
    t = re.sub(r"\([^)]*\)", " ", text.lower())
    t = t.replace(".", "")
    t = re.sub(r"[^a-z0-9'\- ]", " ", t)
    toks = [w for w in t.split() if w]
    while toks and toks[0] in HONORIFICS:
        toks.pop(0)
    # drop trailing generational suffixes
    while toks and toks[-1] in {"jr", "sr", "ii", "iii", "iv"}:
        toks.pop()
    return " ".join(toks)


class MembersIngester:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = OFF")
        self.con.execute("PRAGMA journal_mode = OFF")
        self.con.execute("PRAGMA synchronous = OFF")

    def create_schema(self):
        self.con.executescript(SHARED_SCHEMA.read_text())
        self.con.executescript(MEMBERS_SCHEMA.read_text())
        self.con.execute("PRAGMA foreign_keys = OFF")
        self.con.execute("DELETE FROM ingest_log WHERE source = ?", (SOURCE,))
        self.con.commit()

    def _member_row(self, r, is_current):
        nm, ids, terms = r["name"], r.get("id", {}), r.get("terms", [])
        last = terms[-1] if terms else {}
        fec = ids.get("fec") or []
        return (
            ids["bioguide"], nm.get("first"), nm.get("middle"), nm.get("last"),
            nm.get("nickname"), nm.get("official_full"), 1 if is_current else 0,
            last.get("type"), last.get("state"), last.get("party"),
            terms[0].get("start") if terms else None,
            last.get("end"),
            ",".join(fec), ids.get("opensecrets"), ids.get("govtrack"), ids.get("icpsr"),
        )

    def ingest_legislators(self):
        members, terms = [], []
        for fn, cur in (("legislators-current.yaml", True),
                        ("legislators-historical.yaml", False)):
            for r in load(fn):
                members.append(self._member_row(r, cur))
                bio = r["id"]["bioguide"]
                for i, t in enumerate(r.get("terms", [])):
                    terms.append((bio, i, t.get("type"), t.get("state"),
                                  t.get("district"), t.get("party"),
                                  t.get("start"), t.get("end")))
        c = self.con
        c.executemany("INSERT OR IGNORE INTO members VALUES(%s)" % ",".join("?"*16), members)
        c.executemany("INSERT INTO member_terms VALUES(?,?,?,?,?,?,?,?)", terms)
        c.commit()
        self._log("legislators", len(members))
        print(f"  members={len(members)} terms={len(terms)}", flush=True)

    def ingest_committees(self):
        com = load("committees-current.yaml")
        committees, ids = [], set()
        for c in com:
            tid = c.get("thomas_id")
            if not tid:
                continue
            committees.append((tid, c.get("type"), c.get("name"), None))
            ids.add(tid)
            for s in c.get("subcommittees", []):
                sid = tid + s["thomas_id"]
                committees.append((sid, c.get("type"),
                                   f"{c.get('name')} — {s['name']}", tid))
                ids.add(sid)
        mem = load("committee-membership-current.yaml")
        rows = []
        for cid, members in mem.items():
            if cid not in ids:
                continue
            for m in members:
                rows.append((m["bioguide"], cid, m.get("party"),
                             m.get("rank"), m.get("title")))
        c = self.con
        c.executemany("INSERT INTO committees VALUES(?,?,?,?)", committees)
        c.executemany("INSERT INTO member_committees VALUES(?,?,?,?,?)", rows)
        c.commit()
        self._log("committees", len(committees))
        print(f"  committees={len(committees)} memberships={len(rows)}", flush=True)

    # -- honoree resolution --------------------------------------------------
    def build_honoree_map(self):
        c = self.con
        # matching pool: current + recent historical
        pool = c.execute(
            "SELECT bioguide, first, middle, last, nickname, official_full, "
            "is_current, last_term_end FROM members "
            "WHERE is_current=1 OR last_term_end >= ?", (MATCH_CUTOFF,)).fetchall()
        full_index, last_index = {}, {}
        for bio, first, mid, last, nick, full, cur, end in pool:
            meta = (bio, cur, end or "")
            variants = set()
            if full:
                variants.add(norm(full))
            if first and last:
                variants.add(norm(f"{first} {last}"))
                if mid:
                    variants.add(norm(f"{first} {mid} {last}"))
            if nick and last:
                variants.add(norm(f"{nick} {last}"))
            for v in variants:
                if v:
                    full_index.setdefault(v, []).append(meta)
            if last:
                last_index.setdefault(norm(last), []).append((meta, norm(first or ""), norm(nick or "")))

        def best(cands):
            # prefer current, then most recent term end
            return sorted(cands, key=lambda m: (m[1], m[2]), reverse=True)[0][0]

        honorees = [r[0] for r in c.execute(
            "SELECT DISTINCT honoree_name FROM senate_contribution_items "
            "WHERE honoree_name IS NOT NULL")]
        rows = []
        for raw in honorees:
            h = norm(raw)
            bio, method, conf = None, None, None
            if h in full_index:
                cands = full_index[h]
                bio = best(cands)
                method, conf = "full_name", (1.0 if len(cands) == 1 else 0.9)
            else:
                toks = h.split()
                if len(toks) >= 2 and norm(toks[-1]) in last_index:
                    entries = last_index[norm(toks[-1])]
                    first = toks[0]
                    fmatch = [e for e in entries
                              if e[1] == first or e[2] == first
                              or (len(first) == 1 and e[1].startswith(first))]
                    if len(fmatch) == 1:
                        bio, method, conf = fmatch[0][0][0], "first_last", 0.9
                    elif len(entries) == 1:
                        bio, method, conf = entries[0][0][0], "last_unique", 0.6
            rows.append((raw, h, bio, method, conf))
        c.executemany("INSERT INTO honoree_member_map VALUES(?,?,?,?,?)", rows)
        c.commit()
        matched = sum(1 for r in rows if r[2])
        self._log("honoree_map", len(rows))
        print(f"  honorees={len(rows)} matched={matched} ({100*matched/max(len(rows),1):.0f}%)",
              flush=True)

    def _log(self, kind, n):
        self.con.execute(
            "INSERT INTO ingest_log(source,tier,source_file,record_kind,n_records,ingested_at) "
            "VALUES(?,?,?,?,?,?)", (SOURCE, TIER, kind, kind, n, now_iso()))

    def finalize(self):
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.execute("ANALYZE")
        self.con.commit()
        self.con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    ap.add_argument("--refresh", action="store_true", help="re-download source files")
    args = ap.parse_args()

    download(args.refresh)
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    ing = MembersIngester(str(db_path))
    ing.create_schema()
    print("Legislators ...", flush=True)
    ing.ingest_legislators()
    print("Committees ...", flush=True)
    ing.ingest_committees()
    print("Resolving honoree names ...", flush=True)
    ing.build_honoree_map()
    ing.finalize()
    print(f"Done -> {db_path}")


if __name__ == "__main__":
    main()
