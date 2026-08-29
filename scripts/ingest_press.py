"""Ingest the congressional press releases into the combined GAIN database.

Writes the `press_*` tables into db/gain.db from the JSONL under
data/congress_press/, plus an FTS5 index over title + text and a member roster
derived from the corpus. Source-scoped and idempotent: rebuilds only press_*.

Usage:
    python scripts/ingest_press.py                  # all files -> db/gain.db
    python scripts/ingest_press.py --db /tmp/x.db
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("data/congress_press")
SHARED_SCHEMA = Path("scripts/schema_shared.sql")
PRESS_SCHEMA = Path("scripts/schema_press.sql")
SOURCE = "press"
TIER = "raw"


def s(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def files():
    yield from sorted(ROOT.glob("20[0-9][0-9]/*.jsonl"))
    yield from sorted(ROOT.glob("*.jsonl"))


class PressIngester:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = OFF")
        self.con.execute("PRAGMA journal_mode = OFF")
        self.con.execute("PRAGMA synchronous = OFF")
        self.con.execute("PRAGMA temp_store = MEMORY")
        self.seen = set()
        self.dups = 0
        self._rid = 0

    def create_schema(self):
        self.con.executescript(SHARED_SCHEMA.read_text())
        self.con.executescript(PRESS_SCHEMA.read_text())
        self.con.execute("DELETE FROM ingest_log WHERE source = ?", (SOURCE,))
        self.con.commit()

    def ingest_file(self, path):
        rows = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                url = rec.get("url")
                if url in self.seen:
                    self.dups += 1
                    continue
                self.seen.add(url)
                self._rid += 1
                m = rec.get("member") or {}
                date = s(rec.get("date"))
                year = int(date[:4]) if date and date[:4].isdigit() else None
                rows.append((
                    self._rid, url, s(rec.get("title")), date, year,
                    s(rec.get("date_source")), s(rec.get("source")),
                    s(rec.get("domain")), s(rec.get("scraper")),
                    s(m.get("bioguide_id")), s(m.get("name")), s(m.get("party")),
                    s(m.get("state")), s(m.get("chamber")),
                    rec.get("text"),  # keep body verbatim (do not strip)
                    s(rec.get("collected_at")), s(rec.get("updated_at")),
                    str(path),
                ))
        self.con.executemany(
            "INSERT INTO press_releases VALUES(%s)" % ",".join("?" * 18), rows)
        self.con.execute(
            "INSERT INTO ingest_log(source,tier,source_file,record_kind,n_records,ingested_at) "
            "VALUES(?,?,?,?,?,?)", (SOURCE, TIER, str(path), "press_releases", len(rows), now_iso()))
        self.con.commit()
        print(f"  [{path.name}] releases={len(rows)}", flush=True)

    def build_members(self):
        # one row per member: representative (most-recent) metadata + span
        self.con.execute("DELETE FROM press_members")
        self.con.execute("""
            INSERT INTO press_members
            SELECT bioguide_id, name, party, state, chamber, n, first_date, last_date
            FROM (
                SELECT bioguide_id, member_name AS name, party, state, chamber,
                       count(*)  OVER (PARTITION BY bioguide_id) n,
                       min(date) OVER (PARTITION BY bioguide_id) first_date,
                       max(date) OVER (PARTITION BY bioguide_id) last_date,
                       row_number() OVER (PARTITION BY bioguide_id
                                          ORDER BY date DESC) rn
                FROM press_releases WHERE bioguide_id IS NOT NULL
            ) WHERE rn = 1
        """)
        self.con.commit()

    def build_fts(self):
        c = self.con
        c.execute("DROP TABLE IF EXISTS press_fts")
        c.execute("CREATE VIRTUAL TABLE press_fts USING fts5("
                  "title, text, release_id UNINDEXED)")
        c.execute("INSERT INTO press_fts(rowid, title, text, release_id) "
                  "SELECT release_id, title, text, release_id FROM press_releases")
        c.commit()

    def finalize(self):
        print("Optimizing ...", flush=True)
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.execute("ANALYZE")
        self.con.commit()
        self.con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    args = ap.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    ing = PressIngester(str(db_path))
    ing.create_schema()
    for fp in files():
        ing.ingest_file(fp)
    print("Building member roster ...", flush=True)
    ing.build_members()
    print("Building FTS index ...", flush=True)
    ing.build_fts()
    ing.finalize()
    n_members = sqlite3.connect(str(db_path)).execute(
        "SELECT count(*) FROM press_members").fetchone()[0]
    print(f"Done -> {db_path}  ({db_path.stat().st_size/1e6:.0f} MB)")
    print(f"  duplicate urls skipped: {ing.dups}; members: {n_members}")


if __name__ == "__main__":
    main()
