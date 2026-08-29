"""Ingest the House LDA XML data into the combined GAIN SQLite database.

Writes the `house_*` tables into db/gain.db by parsing every LD-1 (registration)
and LD-2 (quarterly) XML filing under data/house/. Source-scoped and idempotent:
drops and recreates only the House tables and its own ingest_log rows, leaving
senate_*/press_* and shared state intact.

LD-1 and LD-2 are flattened into one filing table (doc_type discriminator).
Lobbyists are normalized to the filing level (LD-2 nests them per ali_info; we
take the deduped union). The House senateID is parsed into senate_registrant_id
for a clean join to the Senate data.

Usage:
    python scripts/ingest_house.py                  # all dirs -> db/gain.db
    python scripts/ingest_house.py --dirs data/house/2025_1stQuarter_XML
    python scripts/ingest_house.py --db /tmp/x.db
"""

import argparse
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

HOUSE = Path("data/house")
SHARED_SCHEMA = Path("scripts/schema_shared.sql")
HOUSE_SCHEMA = Path("scripts/schema_house.sql")
ISSUE_CODES = Path("data/senate/constants/lobbying_activity_issues.json")
SOURCE = "house"
TIER = "raw"

# house_filings column order (must match the INSERT below)
FILING_COLS = [
    "house_filing_id", "doc_type", "filing_year", "filing_period", "report_year",
    "report_type", "reg_type", "organization_name", "contact_prefix",
    "contact_first_name", "contact_last_name", "address_1", "address_2", "city",
    "state", "zip", "country", "principal_city", "principal_state",
    "principal_zip", "principal_country", "registrant_general_description",
    "self_select", "client_name", "client_govt_entity", "client_address",
    "client_city", "client_state", "client_zip", "client_country",
    "client_general_description", "senate_id", "senate_registrant_id",
    "senate_client_suffix", "house_id", "income", "income_amt", "expenses",
    "expenses_amt", "expenses_method", "no_lobbying", "termination_date",
    "effective_date", "printed_name", "signed_date", "imported", "pages",
    "source_file",
]


_NUMREF = re.compile(r"&#(x?)([0-9a-fA-F]+);")


def _strip_invalid_refs(match):
    """Drop XML numeric character references that are illegal in XML 1.0
    (a handful of House filings embed control chars like &#1; / &#11;)."""
    try:
        code = int(match.group(2), 16 if match.group(1) else 10)
    except ValueError:
        return ""
    if (code in (0x9, 0xA, 0xD) or 0x20 <= code <= 0xD7FF
            or 0xE000 <= code <= 0xFFFD or 0x10000 <= code <= 0x10FFFF):
        return match.group(0)
    return ""


def parse_root(fp):
    """Parse an XML filing, recovering from invalid character references.
    Returns (root, recovered_bool) or (None, False) if truly unparseable."""
    try:
        return ET.parse(fp).getroot(), False
    except ET.ParseError:
        raw = fp.read_bytes().decode("utf-8", errors="replace")
        try:
            return ET.fromstring(_NUMREF.sub(_strip_invalid_refs, raw)), True
        except ET.ParseError:
            return None, False


def s(v):
    if v is None:
        return None
    v = v.strip()
    return v or None


def money(v):
    if v is None:
        return None
    txt = v.strip().replace("$", "").replace(",", "")
    if not txt:
        return None
    try:
        return float(txt)
    except ValueError:
        return None


def dir_year_period(name):
    year = int(name.split("_")[0])
    if "Registrations" in name:
        return year, "REG"
    for q, p in (("1stQuarter", "Q1"), ("2ndQuarter", "Q2"),
                 ("3rdQuarter", "Q3"), ("4thQuarter", "Q4")):
        if q in name:
            return year, p
    return year, None


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class HouseIngester:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.con.execute("PRAGMA foreign_keys = OFF")
        self.con.execute("PRAGMA journal_mode = OFF")
        self.con.execute("PRAGMA synchronous = OFF")
        self.con.execute("PRAGMA temp_store = MEMORY")
        self.seen = set()
        self.dups = 0
        self.recovered = 0
        self.failed = 0
        self._activity_id = 0
        self._foreign_id = 0
        self._affil_id = 0
        self._conv_id = 0

    def create_schema(self):
        self.con.executescript(SHARED_SCHEMA.read_text())
        self.con.executescript(HOUSE_SCHEMA.read_text())
        self.con.execute("PRAGMA foreign_keys = OFF")
        self.con.execute("DELETE FROM ingest_log WHERE source = ?", (SOURCE,))
        # ensure issue-code names exist even if Senate hasn't been ingested
        codes = json.load(open(ISSUE_CODES))
        self.con.executemany("INSERT OR IGNORE INTO ref_issue_codes(value,name) VALUES(?,?)",
                             [(r["value"], r["name"]) for r in codes])
        self.con.commit()

    def _parse_senate_id(self, sid):
        if not sid:
            return None, None
        prefix, _, suffix = sid.partition("-")
        reg_id = int(prefix) if prefix.isdigit() else None
        return reg_id, (suffix or None)

    def ingest_dir(self, d):
        year, period = dir_year_period(d.name)
        filings, activities, lobbyists = [], [], []
        foreigns, affils, convs = [], [], []
        n = 0
        for fp in d.glob("*.xml"):
            root, recovered = parse_root(fp)
            if root is None:
                self.failed += 1
                print(f"    !! unparseable: {fp}", flush=True)
                continue
            if recovered:
                self.recovered += 1
            fid = fp.stem
            if fid in self.seen:
                self.dups += 1
                continue
            self.seen.add(fid)
            n += 1
            is_ld1 = root.tag == "LOBBYINGDISCLOSURE1"
            g = lambda tag, _r=root: s(_r.findtext(tag))
            reg_id, suffix = self._parse_senate_id(g("senateID"))
            ry = g("reportYear")
            d_row: dict = {c: None for c in FILING_COLS}
            d_row.update(
                house_filing_id=fid,
                doc_type="LD1" if is_ld1 else "LD2",
                filing_year=year, filing_period=period,
                report_year=int(ry) if ry and ry.isdigit() else None,
                report_type=g("reportType"), reg_type=g("regType"),
                organization_name=g("organizationName"),
                contact_prefix=g("prefix"), contact_first_name=g("firstName"),
                contact_last_name=g("lastName"),
                address_1=g("address1"), address_2=g("address2"), city=g("city"),
                state=g("state"), zip=g("zip"), country=g("country"),
                principal_city=g("principal_city"), principal_state=g("principal_state"),
                principal_zip=g("principal_zip"), principal_country=g("principal_country"),
                registrant_general_description=g("registrantGeneralDescription"),
                self_select=g("selfSelect"),
                client_name=g("clientName"), client_govt_entity=g("clientGovtEntity"),
                client_address=g("clientAddress"), client_city=g("clientCity"),
                client_state=g("clientState"), client_zip=g("clientZip"),
                client_country=g("clientCountry"),
                client_general_description=g("clientGeneralDescription"),
                senate_id=g("senateID"), senate_registrant_id=reg_id,
                senate_client_suffix=suffix, house_id=g("houseID"),
                income=g("income"), income_amt=money(g("income")),
                expenses=g("expenses"), expenses_amt=money(g("expenses")),
                expenses_method=g("expensesMethod"),
                no_lobbying=g("noLobbying"), termination_date=g("terminationDate"),
                effective_date=g("effectiveDate"),
                printed_name=g("printedName"), signed_date=g("signedDate"),
                imported=g("imported"), pages=g("pages"),
                source_file=str(fp),
            )
            filings.append(tuple(d_row[c] for c in FILING_COLS))

            lob_set = set()
            if is_ld1:
                # bare ali_Code list + filing-level lobbyists
                for seq, code_el in enumerate(root.findall("alis/ali_Code")):
                    code = s(code_el.text)
                    if code:
                        self._activity_id += 1
                        activities.append((self._activity_id, fid, seq, code, None, None, None))
                for lob in root.findall("lobbyists/lobbyist"):
                    lob_set.add((
                        s(lob.findtext("lobbyistFirstName")), s(lob.findtext("lobbyistLastName")),
                        s(lob.findtext("lobbyistSuffix")), s(lob.findtext("coveredPosition")),
                        s(lob.findtext("lobbyistNew")),
                    ))
                for fe in root.findall("foreignEntities/foreignEntity"):
                    self._foreign_id += 1
                    foreigns.append((
                        self._foreign_id, fid, s(fe.findtext("name")),
                        s(fe.findtext("country")), s(fe.findtext("contribution")),
                        money(s(fe.findtext("contribution"))),
                        s(fe.findtext("ownership_Percentage")),
                        s(fe.findtext("city")), s(fe.findtext("address")),
                    ))
                for ao in root.findall("affiliatedOrgs/affiliatedOrg"):
                    self._affil_id += 1
                    affils.append((
                        self._affil_id, fid, s(ao.findtext("affiliatedOrgName")),
                        s(ao.findtext("affiliatedOrgCity")), s(ao.findtext("affiliatedOrgState")),
                        s(ao.findtext("affiliatedOrgCountry")), s(ao.findtext("affiliatedOrgZip")),
                    ))
            else:
                # LD2: one activity per ali_info; lobbyists nested per ali_info
                for seq, ali in enumerate(root.findall("alis/ali_info")):
                    self._activity_id += 1
                    activities.append((
                        self._activity_id, fid, seq,
                        s(ali.findtext("issueAreaCode")),
                        s(ali.findtext("specific_issues/description")),
                        s(ali.findtext("federal_agencies")),
                        s(ali.findtext("foreign_entity_issues")),
                    ))
                    for lob in ali.findall("lobbyists/lobbyist"):
                        lob_set.add((
                            s(lob.findtext("lobbyistFirstName")), s(lob.findtext("lobbyistLastName")),
                            s(lob.findtext("lobbyistSuffix")), s(lob.findtext("coveredPosition")),
                            s(lob.findtext("lobbyistNew")),
                        ))

            for (fn, ln, sf, cp, nw) in lob_set:
                lobbyists.append((fid, fn, ln, sf, cp, nw))
            for cv in root.findall("convictionDisclosure/convictions/convictionDetail"):
                self._conv_id += 1
                convs.append((
                    self._conv_id, fid, s(cv.findtext("lobbyistName")),
                    s(cv.findtext("convictionDate")), s(cv.findtext("convictionDescription")),
                ))

        c = self.con
        c.executemany(
            "INSERT INTO house_filings (%s) VALUES (%s)"
            % (",".join(FILING_COLS), ",".join("?" * len(FILING_COLS))), filings)
        c.executemany("INSERT INTO house_activities VALUES(?,?,?,?,?,?,?)", activities)
        c.executemany("INSERT INTO house_filing_lobbyists VALUES(?,?,?,?,?,?)", lobbyists)
        c.executemany("INSERT INTO house_foreign_entities VALUES(?,?,?,?,?,?,?,?,?)", foreigns)
        c.executemany("INSERT INTO house_affiliated_orgs VALUES(?,?,?,?,?,?,?)", affils)
        c.executemany("INSERT INTO house_convictions VALUES(?,?,?,?,?)", convs)
        self.con.execute(
            "INSERT INTO ingest_log(source,tier,source_file,record_kind,n_records,ingested_at) "
            "VALUES(?,?,?,?,?,?)", (SOURCE, TIER, d.name, "house_filings", n, now_iso()))
        c.commit()
        print(f"  [{d.name}] filings={n} activities={len(activities)} "
              f"lobbyists={len(lobbyists)} foreign={len(foreigns)} "
              f"affil={len(affils)} conv={len(convs)}", flush=True)

    def build_fts(self):
        c = self.con
        c.execute("DROP TABLE IF EXISTS house_activities_fts")
        c.execute("CREATE VIRTUAL TABLE house_activities_fts USING fts5("
                  "description, federal_agencies, foreign_entity_issues, activity_id UNINDEXED)")
        c.execute("INSERT INTO house_activities_fts(rowid, description, federal_agencies, "
                  "foreign_entity_issues, activity_id) SELECT activity_id, description, "
                  "federal_agencies, foreign_entity_issues, activity_id FROM house_activities")
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
    ap.add_argument("--dirs", nargs="*", default=None)
    args = ap.parse_args()

    if args.dirs:
        dirs = [Path(d) for d in args.dirs]
    else:
        dirs = sorted(p for p in HOUSE.iterdir() if p.is_dir())

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    ing = HouseIngester(str(db_path))
    ing.create_schema()
    for d in dirs:
        ing.ingest_dir(d)
    print("Building FTS index ...", flush=True)
    ing.build_fts()
    ing.finalize()
    print(f"Done -> {db_path}  ({db_path.stat().st_size/1e6:.0f} MB)")
    print(f"  duplicate house_filing_ids skipped: {ing.dups}")
    print(f"  recovered (sanitized bad char refs): {ing.recovered}; unparseable: {ing.failed}")


if __name__ == "__main__":
    main()
