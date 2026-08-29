#!/usr/bin/env python3
"""Cross-check E4 (committee INS press share) against the M0 ML classifier
instead of BROAD_INS_KEYWORDS (see ins_committee_press_share.py).

Reads db/gain.db only (read-only; derived_press_issue_labels is a
pre-built table from scripts/build_derived_press_issue_labels.py, not
refit here). Produces every number cited in evidence.md E6.

Per docs/press-issue-classifier.md, the
classifier and the keyword map are coexisting, non-authoritative methods --
neither is ground truth. This script exists to see whether the case's core
finding (no INS jurisdiction lift) survives a second, independently-wrong-
in-different-ways measurement of the same thing.

    python investigations/insurance-jurisdiction-no-press-lift/analysis/ins_ml_classifier_crosscheck.py
"""
import sqlite3
from pathlib import Path

DB = Path("db/gain.db")

COMMITTEES = {
    "HSBA04": "House Committee on Financial Services -- Housing and Insurance",
    "SSBK04": "Senate Committee on Banking Housing and Urban Affairs -- Securities Insurance and Investment",
}

NFIP_FLOOD_KEYWORDS = ["nfip", "flood insurance", "property insurance", "casualty insurance"]


def committee_release_ids(con, committee_id):
    return [
        r[0]
        for r in con.execute(
            """
            SELECT p.release_id FROM press_releases p
            JOIN member_committees_history h ON h.bioguide = p.bioguide_id
            WHERE h.committee_id = ?
              AND h.valid_from <= p.date AND (h.valid_to IS NULL OR h.valid_to > p.date)
            """,
            (committee_id,),
        ).fetchall()
    ]


def main():
    con = sqlite3.connect(DB)

    print("=== E6a: classifier vs. keyword-set overlap on INS ===")
    clf_ids = set(
        r[0] for r in con.execute("SELECT release_id FROM derived_press_issue_labels WHERE issue_code='INS'")
    )
    NARROW = ["insurance industry", "insurance regulation", "insurer", "insurance premium"]
    like_narrow = " OR ".join(f"lower(text) LIKE '%{kw.lower()}%'" for kw in NARROW)
    narrow_ids = set(r[0] for r in con.execute(f"SELECT release_id FROM press_releases WHERE {like_narrow}"))
    print(f"classifier INS matches (prob >= 0.3): {len(clf_ids)}")
    print(f"narrow (shared, in-production) keyword matches: {len(narrow_ids)}")
    overlap = clf_ids & narrow_ids
    print(f"overlap: {len(overlap)}")
    print(f"classifier recall of narrow keyword set: {len(overlap)}/{len(narrow_ids)} = {100*len(overlap)/len(narrow_ids):.1f}%")

    print("\n=== E6b: classifier recall on genuine NFIP/flood/property/casualty content ===")
    like_nfip = " OR ".join(f"lower(text) LIKE '%{kw}%'" for kw in NFIP_FLOOD_KEYWORDS)
    nfip_ids = set(r[0] for r in con.execute(f"SELECT release_id FROM press_releases WHERE {like_nfip}"))
    nfip_caught = nfip_ids & clf_ids
    print(f"genuine NFIP/flood/property/casualty releases in corpus: {len(nfip_ids)}")
    print(f"classifier catches: {len(nfip_caught)}/{len(nfip_ids)} = {100*len(nfip_caught)/len(nfip_ids):.1f}%")

    print("\n=== E6c: corpus-wide INS share (classifier) ===")
    total_press = con.execute("SELECT count(*) FROM press_releases").fetchone()[0]
    corpus_pct = 100 * len(clf_ids) / total_press
    print(f"{len(clf_ids)}/{total_press} = {corpus_pct:.2f}%")

    print("\n=== E6d: committee-level INS share (classifier), vs. E4's keyword-based numbers ===")
    for cid, cname in COMMITTEES.items():
        rows = committee_release_ids(con, cid)
        total_c = len(rows)
        matched_c = sum(1 for rid in rows if rid in clf_ids)
        pct_c = 100 * matched_c / total_c if total_c else float("nan")
        print(f"{cid} ({cname})")
        print(f"  total releases: {total_c}")
        print(f"  INS (classifier): {matched_c}/{total_c} = {pct_c:.2f}%  (corpus baseline {corpus_pct:.2f}%)")


if __name__ == "__main__":
    main()
