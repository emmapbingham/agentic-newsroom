"""Ingest the Senate LDA data into the combined GAIN SQLite database.

Writes the `senate_*` tables (and the shared `ref_*` / `ingest_log` tables) into
db/gain.db, flattening the nested JSON defined in scripts/schema_senate.sql. The
build is idempotent and source-scoped: it drops and recreates only the Senate
tables, so rebuilding Senate never touches house_*/press_* or another source's
rows. Other ingesters do the same for their own namespaces.

Entity dimensions (registrants, clients, lobbyists) are deduped in memory on the
Senate API's own IDs and written once at the end. A full-text index over
lobbying-activity descriptions is built last.

Usage:
    python scripts/ingest_senate.py                 # all years -> db/gain.db
    python scripts/ingest_senate.py --years 2025 2026
    python scripts/ingest_senate.py --db /tmp/x.db
"""

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DATA = Path("data/senate")
SHARED_SCHEMA = Path("scripts/schema_shared.sql")
SENATE_SCHEMA = Path("scripts/schema_senate.sql")
SOURCE = "senate"
TIER = "raw"


# --- value coercion helpers -------------------------------------------------
def s(v):
    """Strip strings; map blank/whitespace-only to None."""
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def b(v):
    """Bool -> 0/1, preserving None."""
    return None if v is None else (1 if v else 0)


def money(v):
    """Parse a filed money string to float, else None."""
    if v is None:
        return None
    txt = str(v).strip().replace("$", "").replace(",", "")
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        return None


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ingester:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = OFF")   # bulk load; validated after
        self.con.execute("PRAGMA journal_mode = OFF")   # rebuildable artifact
        self.con.execute("PRAGMA synchronous = OFF")
        self.con.execute("PRAGMA temp_store = MEMORY")
        # deduped dimensions, accumulated across all files
        self.registrants = {}
        self.clients = {}
        self.lobbyists = {}
        # dedupe: source files contain exact-duplicate filing_uuids
        self.seen_filings = set()
        self.seen_contribs = set()
        self.dup_filings = 0
        self.dup_contribs = 0
        # surrogate key counters
        self._activity_id = 0
        self._foreign_id = 0
        self._affil_id = 0
        self._conv_id = 0
        self._item_id = 0
        # controlled-vocab values seen in data (to backfill shared ref tables)
        self.filing_types = {}
        self.issue_codes = {}
        self.gov_entities = {}
        self.contrib_types = {}

    # -- schema / constants --------------------------------------------------
    def create_schema(self):
        self.con.executescript(SHARED_SCHEMA.read_text())   # CREATE IF NOT EXISTS
        self.con.executescript(SENATE_SCHEMA.read_text())   # DROP + CREATE senate_*
        self.con.execute("PRAGMA foreign_keys = OFF")        # re-assert for bulk load
        self.con.execute("DELETE FROM ingest_log WHERE source = ?", (SOURCE,))
        self.con.commit()

    def load_constants(self):
        c = self.con
        const = DATA / "constants"
        def rows(fn):
            return json.load(open(const / fn))
        c.executemany("INSERT OR IGNORE INTO ref_filing_types(value,name) VALUES(?,?)",
                      [(r["value"], r["name"]) for r in rows("filing_types.json")])
        c.executemany("INSERT OR IGNORE INTO ref_issue_codes(value,name) VALUES(?,?)",
                      [(r["value"], r["name"]) for r in rows("lobbying_activity_issues.json")])
        c.executemany("INSERT OR IGNORE INTO ref_government_entities(id,name) VALUES(?,?)",
                      [(r["id"], r["name"]) for r in rows("government_entities.json")])
        c.executemany("INSERT OR IGNORE INTO ref_contribution_item_types(value,name) VALUES(?,?)",
                      [(r["value"], r["name"]) for r in rows("contribution_item_types.json")])
        self._log("constants", "constants", 4)

    # -- dimension capture ---------------------------------------------------
    def _reg(self, r):
        if not r or r.get("id") is None:
            return None
        rid = r["id"]
        self.registrants[rid] = (
            rid, s(r.get("name")), s(r.get("description")),
            r.get("house_registrant_id"),
            s(r.get("address_1")), s(r.get("address_2")),
            s(r.get("city")), s(r.get("state")), s(r.get("state_display")),
            s(r.get("zip")), s(r.get("country")),
            s(r.get("contact_name")), s(r.get("contact_telephone")),
            s(r.get("dt_updated")),
        )
        return rid

    def _client(self, c):
        if not c or c.get("id") is None:
            return None
        cid = c["id"]
        self.clients[cid] = (
            cid, c.get("client_id"), s(c.get("name")),
            s(c.get("general_description")),
            b(c.get("client_government_entity")), b(c.get("client_self_select")),
            s(c.get("state")), s(c.get("state_display")), s(c.get("country")),
            s(c.get("ppb_state")), s(c.get("ppb_country")),
        )
        return cid

    def _lob(self, l):
        if not l or l.get("id") is None:
            return None
        lid = l["id"]
        self.lobbyists[lid] = (
            lid, s(l.get("first_name")), s(l.get("middle_name")),
            s(l.get("last_name")), s(l.get("nickname")),
            s(l.get("prefix")), s(l.get("suffix")),
        )
        return lid

    # -- filings -------------------------------------------------------------
    def ingest_filings(self, path):
        data = json.load(open(path))
        filings, activities, act_lob, act_ge = [], [], [], []
        foreigns, affils, convs = [], [], []
        for rec in data:
            uuid = rec["filing_uuid"]
            if uuid in self.seen_filings:
                self.dup_filings += 1
                continue
            self.seen_filings.add(uuid)
            rid = self._reg(rec.get("registrant"))
            cid = self._client(rec.get("client"))
            ft, ftd = s(rec.get("filing_type")), s(rec.get("filing_type_display"))
            if ft:
                self.filing_types.setdefault(ft, ftd)
            client = rec.get("client") or {}
            filings.append((
                uuid, ft, ftd, rec.get("filing_year"),
                s(rec.get("filing_period")), s(rec.get("filing_period_display")),
                rid, cid,
                s(rec.get("income")), money(rec.get("income")),
                s(rec.get("expenses")), money(rec.get("expenses")),
                s(rec.get("expenses_method")), s(rec.get("expenses_method_display")),
                s(client.get("effective_date")),
                s(rec.get("posted_by_name")), s(rec.get("dt_posted")),
                s(rec.get("termination_date")),
                s(rec.get("url")), s(rec.get("filing_document_url")),
            ))
            for seq, act in enumerate(rec.get("lobbying_activities") or []):
                self._activity_id += 1
                aid = self._activity_id
                code, cdisp = s(act.get("general_issue_code")), s(act.get("general_issue_code_display"))
                if code:
                    self.issue_codes.setdefault(code, cdisp)
                activities.append((
                    aid, uuid, seq, code, cdisp,
                    s(act.get("description")), s(act.get("foreign_entity_issues")),
                ))
                for al in act.get("lobbyists") or []:
                    lid = self._lob(al.get("lobbyist"))
                    if lid is not None:
                        act_lob.append((aid, lid, s(al.get("covered_position")), b(al.get("new"))))
                for ge in act.get("government_entities") or []:
                    geid = ge.get("id")
                    if geid is not None:
                        self.gov_entities.setdefault(geid, s(ge.get("name")))
                        act_ge.append((aid, geid))
            for fe in rec.get("foreign_entities") or []:
                self._foreign_id += 1
                foreigns.append((
                    self._foreign_id, uuid, s(fe.get("name")),
                    s(fe.get("country")), s(fe.get("country_display")),
                    s(fe.get("ownership_percentage")),
                    s(fe.get("contribution")), money(fe.get("contribution")),
                    s(fe.get("city")), s(fe.get("address")), s(fe.get("ppb_country")),
                ))
            for ao in rec.get("affiliated_organizations") or []:
                self._affil_id += 1
                affils.append((
                    self._affil_id, uuid, s(ao.get("name")), s(ao.get("city")),
                    s(ao.get("state")), s(ao.get("country")), s(ao.get("url")),
                ))
            for cv in rec.get("conviction_disclosures") or []:
                self._conv_id += 1
                lid = self._lob(cv.get("lobbyist"))
                convs.append((
                    self._conv_id, uuid, lid, s(cv.get("date")), s(cv.get("description")),
                ))

        c = self.con
        c.executemany("INSERT INTO senate_filings VALUES(%s)" % ",".join("?"*20), filings)
        c.executemany("INSERT INTO senate_lobbying_activities VALUES(?,?,?,?,?,?,?)", activities)
        c.executemany("INSERT INTO senate_activity_lobbyists VALUES(?,?,?,?)", act_lob)
        c.executemany("INSERT INTO senate_activity_government_entities VALUES(?,?)", act_ge)
        c.executemany("INSERT INTO senate_filing_foreign_entities VALUES(?,?,?,?,?,?,?,?,?,?,?)", foreigns)
        c.executemany("INSERT INTO senate_filing_affiliated_orgs VALUES(?,?,?,?,?,?,?)", affils)
        c.executemany("INSERT INTO senate_filing_conviction_disclosures VALUES(?,?,?,?,?)", convs)
        c.commit()
        n = len(filings)
        self._log(str(path), "filings", n)
        print(f"  filings={n}  activities={len(activities)}  act_lob={len(act_lob)} "
              f"act_ge={len(act_ge)}  foreign={len(foreigns)}  conv={len(convs)}", flush=True)
        del data

    # -- contributions -------------------------------------------------------
    def ingest_contributions(self, path):
        data = json.load(open(path))
        cfilings, items, pacs = [], [], []
        for rec in data:
            uuid = rec["filing_uuid"]
            if uuid in self.seen_contribs:
                self.dup_contribs += 1
                continue
            self.seen_contribs.add(uuid)
            rid = self._reg(rec.get("registrant"))
            lid = self._lob(rec.get("lobbyist"))
            ft, ftd = s(rec.get("filing_type")), s(rec.get("filing_type_display"))
            if ft:
                self.filing_types.setdefault(ft, ftd)
            cfilings.append((
                uuid, ft, ftd, rec.get("filing_year"),
                s(rec.get("filing_period")), s(rec.get("filing_period_display")),
                rid, lid, s(rec.get("filer_type")), b(rec.get("no_contributions")),
                s(rec.get("comments")), s(rec.get("dt_posted")),
                s(rec.get("url")), s(rec.get("filing_document_url")),
            ))
            for it in rec.get("contribution_items") or []:
                self._item_id += 1
                ct = s(it.get("contribution_type"))
                if ct:
                    self.contrib_types.setdefault(ct, s(it.get("contribution_type_display")))
                items.append((
                    self._item_id, uuid, ct,
                    s(it.get("contributor_name")), s(it.get("payee_name")),
                    s(it.get("honoree_name")),
                    s(it.get("amount")), money(it.get("amount")), s(it.get("date")),
                ))
            for pac in rec.get("pacs") or []:
                pacs.append((uuid, s(pac)))

        c = self.con
        c.executemany("INSERT INTO senate_contribution_filings VALUES(%s)" % ",".join("?"*14), cfilings)
        c.executemany("INSERT INTO senate_contribution_items VALUES(?,?,?,?,?,?,?,?,?)", items)
        c.executemany("INSERT INTO senate_contribution_pacs VALUES(?,?)", pacs)
        c.commit()
        n = len(cfilings)
        self._log(str(path), "contributions", n)
        print(f"  contrib_filings={n}  items={len(items)}  pacs={len(pacs)}", flush=True)
        del data

    # -- finalize ------------------------------------------------------------
    def write_dimensions(self):
        c = self.con
        c.executemany("INSERT OR REPLACE INTO senate_registrants VALUES(%s)" % ",".join("?"*14),
                      self.registrants.values())
        c.executemany("INSERT OR REPLACE INTO senate_clients VALUES(%s)" % ",".join("?"*11),
                      self.clients.values())
        c.executemany("INSERT OR REPLACE INTO senate_lobbyists VALUES(?,?,?,?,?,?,?)",
                      self.lobbyists.values())
        # backfill any controlled-vocab values present in data but not constants
        c.executemany("INSERT OR IGNORE INTO ref_filing_types(value,name) VALUES(?,?)",
                      [(k, v or k) for k, v in self.filing_types.items()])
        c.executemany("INSERT OR IGNORE INTO ref_issue_codes(value,name) VALUES(?,?)",
                      [(k, v or k) for k, v in self.issue_codes.items()])
        c.executemany("INSERT OR IGNORE INTO ref_government_entities(id,name) VALUES(?,?)",
                      [(k, v) for k, v in self.gov_entities.items()])
        c.executemany("INSERT OR IGNORE INTO ref_contribution_item_types(value,name) VALUES(?,?)",
                      [(k, v or k) for k, v in self.contrib_types.items()])
        c.commit()
        print(f"  registrants={len(self.registrants)} clients={len(self.clients)} "
              f"lobbyists={len(self.lobbyists)}", flush=True)

    def build_fts(self):
        c = self.con
        c.execute("DROP TABLE IF EXISTS senate_activities_fts")
        c.execute(
            "CREATE VIRTUAL TABLE senate_activities_fts USING fts5("
            "description, foreign_entity_issues, activity_id UNINDEXED)"
        )
        c.execute(
            "INSERT INTO senate_activities_fts(rowid, description, foreign_entity_issues, activity_id) "
            "SELECT activity_id, description, foreign_entity_issues, activity_id "
            "FROM senate_lobbying_activities"
        )
        c.commit()

    def _log(self, source_file, kind, n):
        self.con.execute(
            "INSERT INTO ingest_log(source,tier,source_file,record_kind,n_records,ingested_at) "
            "VALUES(?,?,?,?,?,?)",
            (SOURCE, TIER, source_file, kind, n, now_iso()),
        )

    def finalize(self):
        print("Optimizing ...", flush=True)
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.execute("ANALYZE")
        self.con.commit()
        self.con.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/gain.db")
    ap.add_argument("--years", nargs="*", default=None)
    args = ap.parse_args()

    years = args.years or sorted(
        p.name for p in DATA.iterdir() if p.is_dir() and p.name.isdigit()
    )
    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    ing = Ingester(str(db_path))
    ing.create_schema()
    ing.load_constants()
    for y in years:
        fp = DATA / y / "filings" / f"filings_{y}.json"
        if fp.exists():
            print(f"[{y}] filings", flush=True)
            ing.ingest_filings(fp)
        cp = DATA / y / "contributions" / f"contributions_{y}.json"
        if cp.exists():
            print(f"[{y}] contributions", flush=True)
            ing.ingest_contributions(cp)
    print("Writing dimensions ...", flush=True)
    ing.write_dimensions()
    print("Building FTS index ...", flush=True)
    ing.build_fts()
    ing.finalize()
    print(f"Done -> {db_path}  ({db_path.stat().st_size/1e6:.0f} MB)")
    print(f"  exact-duplicate filing_uuids skipped: "
          f"filings={ing.dup_filings} contributions={ing.dup_contribs}")


if __name__ == "__main__":
    main()
