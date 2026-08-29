#!/usr/bin/env python3
"""Derived instrument: press-release mentions of high-spend Senate clients.

Second/final stage of the press-mining entity-tracing pipeline (see
build_derived_client_alias_index.py for stage one). For every 'candidate'
alias in derived_client_alias_index (deterministic + agent-reviewed, generic
names already excluded via status='rejected_too_generic'), phrase-matches the
alias against press_fts and records every hit. This is the "say vs. pay"
entity-level bridge: for a given company, which members mentioned it in a
press release, when, and how that compares to its lobbying footprint.

Uses FTS5 phrase queries (quoted), which requires escaping literal double
quotes in the alias (rare, e.g. an alias containing a quote character) by
doubling them per FTS5 syntax. Matches are deduped per (entity_id,
release_id) -- an entity with multiple aliases hitting the same release
counts once, but matched_alias records which alias(es) fired.

CAVEAT: the LOC COMMUNITY ASSOCIATION crank filer's aliases are already
status='rejected_too_generic' (agent review, see docstring note in the alias
builder) and so are excluded here too -- but exclude it from any income-based
ranking regardless, since its $180M is fabricated
(derived_registrant_income_integrity).

    python scripts/build_derived_client_press_mentions.py
    python scripts/build_derived_client_press_mentions.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_client_press_mentions"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    id             INTEGER PRIMARY KEY,
    entity_id      INTEGER NOT NULL,
    canonical_name TEXT NOT NULL,
    matched_alias  TEXT NOT NULL,
    release_id     INTEGER NOT NULL,
    bioguide_id    TEXT,
    member_name    TEXT,
    chamber        TEXT,
    date           TEXT,
    url            TEXT NOT NULL,
    title          TEXT
);
"""

INDEXES = [
    f"CREATE INDEX idx_{TABLE}_entity ON {TABLE}(entity_id);",
    f"CREATE INDEX idx_{TABLE}_release ON {TABLE}(release_id);",
    f"CREATE UNIQUE INDEX idx_{TABLE}_entity_release ON {TABLE}(entity_id, release_id);",
]


def fts_phrase(alias: str) -> str:
    return '"' + alias.replace('"', '""') + '"'


def build(con):
    con.executescript(DDL)

    aliases = con.execute(
        f"SELECT entity_id, canonical_name, alias FROM derived_client_alias_index "
        f"WHERE status='candidate' ORDER BY entity_id"
    ).fetchall()

    seen_entity_release = set()
    n_matches = 0

    for entity_id, canonical_name, alias in aliases:
        query = fts_phrase(alias)
        rows = con.execute(
            "SELECT p.release_id, p.bioguide_id, p.member_name, p.chamber, p.date, p.url, p.title "
            "FROM press_fts f JOIN press_releases p ON p.release_id = f.release_id "
            "WHERE press_fts MATCH ?",
            (query,),
        ).fetchall()
        for release_id, bioguide_id, member_name, chamber, date, url, title in rows:
            key = (entity_id, release_id)
            if key in seen_entity_release:
                continue
            seen_entity_release.add(key)
            n_matches += 1
            con.execute(
                f"INSERT INTO {TABLE} (entity_id, canonical_name, matched_alias, release_id, "
                f"bioguide_id, member_name, chamber, date, url, title) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (entity_id, canonical_name, alias, release_id, bioguide_id, member_name,
                 chamber, date, url, title),
            )

    for ix in INDEXES:
        con.execute(ix)

    n_entities_matched = con.execute(f"SELECT count(DISTINCT entity_id) FROM {TABLE}").fetchone()[0]
    con.execute("DELETE FROM ingest_log WHERE source='client_press_mentions'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('client_press_mentions','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n_matches),
    )
    con.commit()
    print(f"built {TABLE}: {n_matches} (entity, release) mentions across "
          f"{n_entities_matched} of {len(set(r[0] for r in aliases))} candidate entities")


def validate(con):
    ok = True

    def check(label, cond):
        nonlocal ok
        ok = ok and cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {label}")

    n_rows = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    n_entities = con.execute(f"SELECT count(DISTINCT entity_id) FROM {TABLE}").fetchone()[0]
    print(f"  {n_rows} mention rows, {n_entities} distinct entities with >=1 mention")

    dupe = con.execute(
        f"SELECT count(*) FROM (SELECT entity_id, release_id, count(*) c FROM {TABLE} "
        f"GROUP BY entity_id, release_id HAVING c > 1)"
    ).fetchone()[0]
    check("no duplicate (entity_id, release_id) rows", dupe == 0)

    rejected_present = con.execute(
        f"SELECT count(*) FROM {TABLE} m JOIN derived_client_alias_index a "
        f"ON a.entity_id = m.entity_id AND a.alias = m.matched_alias "
        f"WHERE a.status = 'rejected_too_generic'"
    ).fetchone()[0]
    check("no mentions sourced from a rejected_too_generic alias", rejected_present == 0)

    loc_present = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE canonical_name LIKE '%LOC NATION%'"
    ).fetchone()[0]
    check("LOC NATION crank filer excluded (rejected_too_generic upstream)", loc_present == 0)

    sample = con.execute(
        f"SELECT canonical_name, matched_alias, member_name, date, title FROM {TABLE} "
        f"ORDER BY date DESC LIMIT 5"
    ).fetchall()
    print("  sample recent mentions:")
    for row in sample:
        print(f"    {row}")

    top = con.execute(
        f"SELECT canonical_name, count(*) c FROM {TABLE} GROUP BY entity_id "
        f"ORDER BY c DESC LIMIT 10"
    ).fetchall()
    print("  top 10 entities by mention count:")
    for row in top:
        print(f"    {row}")

    print("PASS" if ok else "FAIL")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)
    try:
        if args.validate:
            sys.exit(0 if validate(con) else 1)
        build(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
