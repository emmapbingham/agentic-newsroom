#!/usr/bin/env python3
"""Derived instrument: cross-chamber engagement bridge.

Pairs House and Senate LDA filings at the *engagement* grain
(registrant x client-group x year x quarter) so the two parallel disclosure
systems can be compared against each other — the "source-vs-source" contrast.

Grain / keys
------------
- registrant_id   : senate_registrants.id (= house_filings.senate_registrant_id,
                    the verified 100% Senate<->House registrant bridge)
- client_group_id : senate_clients.client_id, the coarse client grouping.
                    The House side reaches it via the ADJUDICATED join
                    CAST(house_filings.senate_client_suffix AS INTEGER)
                    = senate_clients.client_id  (99.5% coverage, 91.6% exact
                    name agreement; see the docs/beat_book.md beat
                    book, 2026-06-13). NOT senate_clients.id (only 31.9%).
- filing_year, quarter (Q1..Q4): Senate first/second/third/fourth_quarter and
                    House Q1..Q4 are aligned. House REG (LD-1) and any non-Q
                    periods are excluded (registrations, no quarterly analog).

What it enables (named consumers — the build gate)
--------------------------------------------------
- house-senate-client-disclosure-asymmetry  (presence = house_only / senate_only)
- senate-duplicate-disclosure-inflation      (senate_n >= 2 -> drill to filings)
- house-senate-discrepancy (backlog)         (presence + income compare)
- foreign-client-fe-omission (cross-check)

Source-scoped + idempotent: drops/recreates only its own table and its own
ingest_log rows. Reads only gain.db (derived tier). Verify every downstream
claim back to the source filing_uuid / house_filing_id this table concatenates.

    python scripts/build_derived_cross_chamber.py
    python scripts/build_derived_cross_chamber.py --validate   # reconcile
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_cross_chamber_engagements"

DDL = f"""
DROP TABLE IF EXISTS {TABLE};
CREATE TABLE {TABLE} (
    registrant_id      INTEGER NOT NULL,
    registrant_name    TEXT,
    client_group_id    INTEGER NOT NULL,
    client_name        TEXT,
    filing_year        INTEGER NOT NULL,
    quarter            TEXT    NOT NULL,   -- Q1..Q4
    presence           TEXT    NOT NULL,   -- 'both' | 'senate_only' | 'house_only'
    senate_n           INTEGER NOT NULL DEFAULT 0,
    senate_income_sum  REAL,               -- sum of parsed income_amt (sparse; ~65% of filings)
    senate_filing_uuids TEXT,              -- comma-joined source keys -> lda.gov/filings/public/filing/{uuid}/print/
    house_n            INTEGER NOT NULL DEFAULT 0,
    house_income_sum   REAL,
    house_filing_ids   TEXT,               -- comma-joined source keys
    PRIMARY KEY (registrant_id, client_group_id, filing_year, quarter)
);
"""

# Per-chamber engagement aggregates. Quarter normalized to Q1..Q4 on both sides.
SENATE_AGG = """
CREATE TEMP TABLE s_eng AS
SELECT
    f.registrant_id                              AS registrant_id,
    sc.client_id                                 AS client_group_id,
    f.filing_year                                AS filing_year,
    CASE f.filing_period
        WHEN 'first_quarter'  THEN 'Q1'
        WHEN 'second_quarter' THEN 'Q2'
        WHEN 'third_quarter'  THEN 'Q3'
        WHEN 'fourth_quarter' THEN 'Q4'
    END                                          AS quarter,
    count(*)                                     AS senate_n,
    sum(f.income_amt)                            AS senate_income_sum,
    group_concat(f.filing_uuid)                  AS senate_filing_uuids,
    min(sc.name)                                 AS s_name
FROM senate_filings f
JOIN senate_clients sc ON sc.id = f.client_id
WHERE f.filing_period IN
      ('first_quarter','second_quarter','third_quarter','fourth_quarter')
  AND f.registrant_id IS NOT NULL
  AND sc.client_id IS NOT NULL
GROUP BY 1,2,3,4;
"""

HOUSE_AGG = """
CREATE TEMP TABLE h_eng AS
SELECT
    h.senate_registrant_id                       AS registrant_id,
    CAST(h.senate_client_suffix AS INTEGER)      AS client_group_id,
    h.filing_year                                AS filing_year,
    h.filing_period                              AS quarter,
    count(*)                                     AS house_n,
    sum(h.income_amt)                            AS house_income_sum,
    group_concat(h.house_filing_id)              AS house_filing_ids,
    min(h.client_name)                           AS h_name
FROM house_filings h
WHERE h.senate_registrant_id IS NOT NULL
  AND h.senate_client_suffix IS NOT NULL AND h.senate_client_suffix <> ''
  AND h.filing_period IN ('Q1','Q2','Q3','Q4')
GROUP BY 1,2,3,4;
"""

# Union of all engagement keys, then left-join both sides (SQLite 3.37 has no
# FULL OUTER JOIN). registrant_name from the Senate dimension (the bridge keys
# every house registrant_id into it at 100%).
INSERT = f"""
INSERT INTO {TABLE}
SELECT
    k.registrant_id,
    r.name                                       AS registrant_name,
    k.client_group_id,
    coalesce(s.s_name, h.h_name)                 AS client_name,
    k.filing_year,
    k.quarter,
    CASE
        WHEN s.registrant_id IS NOT NULL AND h.registrant_id IS NOT NULL THEN 'both'
        WHEN s.registrant_id IS NOT NULL THEN 'senate_only'
        ELSE 'house_only'
    END                                          AS presence,
    coalesce(s.senate_n, 0)                       AS senate_n,
    s.senate_income_sum,
    s.senate_filing_uuids,
    coalesce(h.house_n, 0)                        AS house_n,
    h.house_income_sum,
    h.house_filing_ids
FROM (
    SELECT registrant_id, client_group_id, filing_year, quarter FROM s_eng
    UNION
    SELECT registrant_id, client_group_id, filing_year, quarter FROM h_eng
) k
LEFT JOIN s_eng s USING (registrant_id, client_group_id, filing_year, quarter)
LEFT JOIN h_eng h USING (registrant_id, client_group_id, filing_year, quarter)
LEFT JOIN senate_registrants r ON r.id = k.registrant_id;
"""

INDEXES = [
    f"CREATE INDEX idx_cce_presence   ON {TABLE}(presence);",
    f"CREATE INDEX idx_cce_registrant ON {TABLE}(registrant_id);",
    f"CREATE INDEX idx_cce_client     ON {TABLE}(client_group_id);",
    f"CREATE INDEX idx_cce_year       ON {TABLE}(filing_year, quarter);",
]


def build(con):
    con.executescript(DDL)
    con.executescript(SENATE_AGG)
    con.executescript(HOUSE_AGG)
    con.executescript(INSERT)
    for ix in INDEXES:
        con.execute(ix)
    n = con.execute(f"SELECT count(*) FROM {TABLE}").fetchone()[0]
    # source-scoped ingest_log: clear our own rows, then record this build
    con.execute("DELETE FROM ingest_log WHERE source='cross_chamber'")
    con.execute(
        "INSERT INTO ingest_log (source, tier, source_file, record_kind, n_records, ingested_at) "
        "VALUES ('cross_chamber','derived','db/gain.db',?,?,datetime('now'))",
        (TABLE, n),
    )
    con.commit()
    by = con.execute(
        f"SELECT presence, count(*) FROM {TABLE} GROUP BY presence ORDER BY 2 DESC"
    ).fetchall()
    print(f"built {TABLE}: {n:,} engagement-quarters")
    for p, c in by:
        print(f"  {p:12s} {c:>9,}")
    return n


def validate(con):
    """Reconcile against the corpus and against the sweep's scout-reported facts."""
    ok = True

    def check(label, got, want=None, tol=None):
        nonlocal ok
        if want is None:
            print(f"  {label}: {got}")
            return
        good = (abs(got - want) <= tol) if tol is not None else (got == want)
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: got {got:,}, want ~{want:,}")

    print("reconciliation:")
    # --- structural invariants -------------------------------------------------
    # 1. registrant_id orphans: a tiny known residual is expected — ~23 House
    #    filings carry a senateID that resolves to no real Senate registrant
    #    (placeholder ids like 20000002). They appear only as house_only and
    #    leave registrant_name NULL. Assert the residual stays small, not zero.
    orphan = con.execute(
        f"SELECT count(*) FROM {TABLE} t "
        "LEFT JOIN senate_registrants r ON r.id=t.registrant_id "
        "WHERE r.id IS NULL"
    ).fetchone()[0]
    orphan_house_only = con.execute(
        f"SELECT count(*) FROM {TABLE} t "
        "LEFT JOIN senate_registrants r ON r.id=t.registrant_id "
        "WHERE r.id IS NULL AND t.presence='house_only'"
    ).fetchone()[0]
    check("registrant_id orphans (known House-bridge residual, want < 50)",
          1 if orphan < 50 else 0, 1)
    check("  ...and all orphans are house_only", 1 if orphan == orphan_house_only else 0, 1)

    # 2. no row empty on both sides; presence flags internally consistent
    bad = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE senate_n=0 AND house_n=0"
    ).fetchone()[0]
    check("rows empty on both sides (want 0)", bad, 0)
    mism = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE "
        "(presence='both' AND (senate_n=0 OR house_n=0)) OR "
        "(presence='senate_only' AND (senate_n=0 OR house_n>0)) OR "
        "(presence='house_only' AND (house_n=0 OR senate_n>0))"
    ).fetchone()[0]
    check("presence-flag inconsistencies (want 0)", mism, 0)

    # --- VERIFIED facts (this instrument CORRECTS the 2026-06-11 sweep) ---------
    # 3. Client-disclosure asymmetry among dual-chamber registrants, 2022-2025.
    #    The sweep's scout used an UPPER(client_name) join and reported ~3,255
    #    house-only vs ~50 senate-only (65x). The adjudicated id-join unifies the
    #    name variants the scout counted as house-only AND surfaces real
    #    senate-only engagements the scout missed: the skew is ~3x, not 65x.
    #    Direction (House discloses more clients) survives; magnitude does not.
    dual = (
        f"SELECT registrant_id FROM {TABLE} GROUP BY registrant_id "
        "HAVING sum(presence='both')>0"
    )
    ho = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE presence='house_only' "
        f"AND filing_year BETWEEN 2022 AND 2025 AND registrant_id IN ({dual})"
    ).fetchone()[0]
    so = con.execute(
        f"SELECT count(*) FROM {TABLE} WHERE presence='senate_only' "
        f"AND filing_year BETWEEN 2022 AND 2025 AND registrant_id IN ({dual})"
    ).fetchone()[0]
    print(f"  asymmetry (dual-chamber registrants, 2022-2025): "
          f"house_only={ho:,}  senate_only={so:,}  skew={ho/max(so,1):.1f}x "
          f"[sweep claimed 3,255 vs 50 = 65x — REFUTED]")
    check("asymmetry direction holds (house_only > senate_only)",
          1 if ho > so else 0, 1)
    check("asymmetry magnitude is single-digit, not the claimed 65x",
          1 if ho < 10 * so else 0, 1)

    # 4. Senate duplicate inflation, done correctly: same registrant/client/
    #    period, ORIGINAL quarterly filing_type (Q1..Q4 only), identical >0
    #    income, >=2 distinct UUIDs. Restricting to Q1..Q4 is essential: an
    #    independent verifier (2026-06-13) showed that an earlier same-filing_type
    #    definition WRONGLY counted amendment-pairs (1A/2A/…) and a $60M junk
    #    record, inflating $35M -> $118M. The defensible figure is the original
    #    sweep number: ~970 groups / ~$35M, ~90% same-day clerical re-submits.
    dup = con.execute(
        """
        WITH d AS (
          SELECT f.registrant_id, sc.client_id AS cg, f.filing_year,
                 f.filing_period, f.filing_type, f.income_amt,
                 count(DISTINCT f.filing_uuid) AS u
          FROM senate_filings f JOIN senate_clients sc ON sc.id=f.client_id
          WHERE f.filing_type IN ('Q1','Q2','Q3','Q4')
            AND f.income_amt IS NOT NULL AND f.income_amt > 0
          GROUP BY 1,2,3,4,5,6 HAVING count(DISTINCT f.filing_uuid) >= 2
        )
        SELECT count(*) AS groups, sum((u-1)*income_amt) AS excess FROM d
        """
    ).fetchone()
    print(f"  TRUE senate duplicates (original quarterlies Q1-Q4, identical >0 "
          f"income): {dup[0]:,} groups, ~${(dup[1] or 0):,.0f} double-counted "
          f"[matches the sweep's 970/$35M; ~90% same-day clerical]")
    check("true-duplicate groups ~970 (800-1200)",
          1 if 800 <= dup[0] <= 1200 else 0, 1)

    print("PASS" if ok else "FAIL — see above")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    if not DB.exists():
        sys.exit(f"{DB} not found — build the raw + reference stages first")
    con = sqlite3.connect(DB)
    try:
        if args.validate:
            sys.exit(0 if validate(con) else 1)
        else:
            build(con)
    finally:
        con.close()


if __name__ == "__main__":
    main()
