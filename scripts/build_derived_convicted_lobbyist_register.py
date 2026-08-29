#!/usr/bin/env python3
"""Build derived_convicted_lobbyist_register in db/gain.db.

One row per Senate lobbyist (stable lobbyist_id) who has at least one
conviction disclosure row in senate_filing_conviction_disclosures, with their
post-conviction filing/disclosure record:

- conviction_date / conviction_desc: earliest disclosure row's date/description
  (the LDA disclosure carries the conviction date as filed).
- n_filings_disclosed: distinct filings carrying a disclosure row for them.
- n_post_quarterlies: distinct ORIGINAL quarterly reports (filing_type Q1-Q4,
  the $118M-episode discipline: no amendments, no terminations) that list the
  lobbyist on an activity AND whose quarter starts strictly after
  conviction_date. The screen's baseline mandates the post-conviction filter
  (Burkman/Wohl 2022 disclosure gaps predate their convictions).
- n_post_missing: those post-conviction quarterlies with NO disclosure row for
  this lobbyist on that filing. missing_uuids: up to 5 example filing_uuids
  (verifiability: https://lda.gov/filings/public/filing/{uuid}/print/).
- n_post_disclosed: post-conviction quarterlies WITH the disclosure
  (awareness evidence: they know the obligation exists).

Senate-only by design: house_convictions is name-keyed (no stable id); House
corroboration stays case-side. Rows with NULL conviction date keep the
register row but NULL post-conviction columns (can't order against filings).
"""

import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")

QUARTER_START = {
    "first_quarter": "-01-01",
    "second_quarter": "-04-01",
    "third_quarter": "-07-01",
    "fourth_quarter": "-10-01",
}

DDL = """
DROP TABLE IF EXISTS derived_convicted_lobbyist_register;
CREATE TABLE derived_convicted_lobbyist_register (
    lobbyist_id          INTEGER PRIMARY KEY REFERENCES senate_lobbyists(id),
    lobbyist_name        TEXT,
    conviction_date      TEXT,     -- earliest disclosure row's date, as filed
    conviction_desc      TEXT,     -- earliest disclosure row's description
    n_filings_disclosed  INTEGER,  -- distinct filings with a disclosure row
    n_post_quarterlies   INTEGER,  -- original Q1-Q4 listing them, quarter start > conviction_date
    n_post_disclosed     INTEGER,  -- of those, carrying the disclosure
    n_post_missing       INTEGER,  -- of those, lacking it
    missing_uuids        TEXT      -- up to 5 example filing_uuids, comma-separated
);
"""


def main() -> None:
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)
    con.executescript(DDL)

    case_expr = " ".join(
        f"WHEN '{p}' THEN f.filing_year || '{s}'" for p, s in QUARTER_START.items()
    )

    con.executescript(f"""
    -- earliest disclosure row per lobbyist (date may be NULL/junk; keep as filed)
    CREATE TEMP TABLE conv AS
    SELECT lobbyist_id,
           min(date)                              AS conviction_date,
           (SELECT description FROM senate_filing_conviction_disclosures c2
             WHERE c2.lobbyist_id = c.lobbyist_id
             ORDER BY c2.date IS NULL, c2.date, c2.id LIMIT 1) AS conviction_desc,
           count(DISTINCT filing_uuid)            AS n_filings_disclosed
    FROM senate_filing_conviction_disclosures c
    WHERE lobbyist_id IS NOT NULL
    GROUP BY lobbyist_id;

    -- post-conviction original quarterlies listing each convicted lobbyist
    CREATE TEMP TABLE postq AS
    SELECT DISTINCT conv.lobbyist_id, f.filing_uuid,
           EXISTS (SELECT 1 FROM senate_filing_conviction_disclosures d
                    WHERE d.filing_uuid = f.filing_uuid
                      AND d.lobbyist_id = conv.lobbyist_id) AS has_disclosure
    FROM conv
    JOIN senate_activity_lobbyists al ON al.lobbyist_id = conv.lobbyist_id
    JOIN senate_lobbying_activities a ON a.activity_id = al.activity_id
    JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
    WHERE f.filing_type IN ('Q1','Q2','Q3','Q4')
      AND conv.conviction_date IS NOT NULL
      AND (CASE f.filing_period {case_expr} END) > conv.conviction_date;

    INSERT INTO derived_convicted_lobbyist_register
    SELECT conv.lobbyist_id,
           trim(coalesce(l.last_name,'') || ', ' || coalesce(l.first_name,''), ', '),
           conv.conviction_date,
           conv.conviction_desc,
           conv.n_filings_disclosed,
           (SELECT count(*) FROM postq p WHERE p.lobbyist_id = conv.lobbyist_id),
           (SELECT count(*) FROM postq p WHERE p.lobbyist_id = conv.lobbyist_id AND p.has_disclosure),
           (SELECT count(*) FROM postq p WHERE p.lobbyist_id = conv.lobbyist_id AND NOT p.has_disclosure),
           (SELECT group_concat(filing_uuid) FROM (
                SELECT filing_uuid FROM postq p
                WHERE p.lobbyist_id = conv.lobbyist_id AND NOT p.has_disclosure
                ORDER BY filing_uuid LIMIT 5))
    FROM conv JOIN senate_lobbyists l ON l.id = conv.lobbyist_id;
    """)

    # sanity checks
    n, = con.execute("SELECT count(*) FROM derived_convicted_lobbyist_register").fetchone()
    people, = con.execute(
        "SELECT count(DISTINCT lobbyist_id) FROM senate_filing_conviction_disclosures"
        " WHERE lobbyist_id IS NOT NULL").fetchone()
    assert n == people, f"register rows {n} != distinct convicted lobbyists {people}"
    bad, = con.execute(
        "SELECT count(*) FROM derived_convicted_lobbyist_register"
        " WHERE n_post_disclosed + n_post_missing != n_post_quarterlies").fetchone()
    assert bad == 0, f"{bad} rows where disclosed+missing != total"

    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at)"
        " VALUES ('convicted_lobbyist_register','derived','db/gain.db',"
        " 'derived_convicted_lobbyist_register',?,datetime('now'))", (n,))
    con.commit()
    print(f"derived_convicted_lobbyist_register: {n} lobbyists")
    for row in con.execute(
        "SELECT lobbyist_name, conviction_date, n_post_quarterlies, n_post_missing"
        " FROM derived_convicted_lobbyist_register"
        " WHERE n_post_quarterlies > 0 ORDER BY n_post_missing DESC LIMIT 8"):
        print("  ", row)
    con.close()


if __name__ == "__main__":
    main()
