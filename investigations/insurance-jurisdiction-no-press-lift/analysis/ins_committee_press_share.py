#!/usr/bin/env python3
"""Case-local re-derivation for insurance-jurisdiction-no-press-lift.

Reads db/gain.db only (read-only); writes nothing back to gain.db. Produces
every number cited in evidence.md. Re-run this to reproduce or re-verify any
figure in the case rather than trusting a number copied into prose.

Uses the BROAD_INS_KEYWORDS override (see case.md "Methodology: the INS
keyword-recall bug and its fix" section) instead of the shared
ISSUE_KEYWORDS['INS'] in scripts/build_derived_issue_quarter_volume_press.py,
which is known-broken (23% recall vs the bare word "insurance" -- see
scripts/audit_issue_keyword_recall.py). This override is case-local until
someone promotes it into the shared table (not yet done -- see case.md open
items).

    python investigations/insurance-jurisdiction-no-press-lift/analysis/ins_committee_press_share.py
"""
import sqlite3
from pathlib import Path

DB = Path("db/gain.db")

# Broadened, industry-disambiguated INS keyword set (case-local override).
# Built by hand-checking a sample of bare-word "insurance" mentions in the
# corpus: most bare mentions are HEALTH insurance (HCR territory) or
# UNEMPLOYMENT insurance (UNM territory), not insurance-as-a-regulated-
# industry -- so a naive "just match bare insurance" fix would wrongly sweep
# in those. This set targets insurance-industry language specifically:
# insurer/insurance-company language, and the named insurance product lines
# (property/casualty/auto/home/life/disability/title) that are the LDA INS
# code's actual subject matter.
BROAD_INS_KEYWORDS = [
    "insurance industry", "insurance regulation", "insurer", "insurance premium",
    "insurance compan", "insurance market", "insurance rate",
    "homeowners insurance", "property insurance", "auto insurance", "flood insurance",
    "life insurance", "disability insurance", "title insurance", "casualty insurance",
]

# The narrow, shared (currently in-production) keyword set, for comparison --
# copied from scripts/build_derived_issue_quarter_volume_press.py ISSUE_KEYWORDS['INS'].
# Must stay in sync with that file if it changes; not imported directly because
# this script needs to show BOTH old and new counts side by side as evidence.
NARROW_INS_KEYWORDS = [
    "insurance industry", "insurance regulation", "insurer", "insurance premium",
]

COMMITTEES = {
    "HSBA04": "House Committee on Financial Services -- Housing and Insurance",
    "SSBK04": "Senate Committee on Banking Housing and Urban Affairs -- Securities Insurance and Investment",
}

# The committee's OTHER primary jurisdiction issue code, for the within-committee
# contrast (from committee_issue_jurisdiction, weight='primary').
OTHER_JURISDICTION = {"HSBA04": "HOU", "SSBK04": "FIN"}


def like_or(keywords):
    return " OR ".join(f"lower(text) LIKE '%{kw.lower()}%'" for kw in keywords)


def bare_word_count(con, word):
    return con.execute(
        "SELECT count(*) FROM press_releases WHERE lower(text) LIKE ?", (f"%{word}%",)
    ).fetchone()[0]


def keyword_match_count(con, keywords):
    return con.execute(
        f"SELECT count(*) FROM press_releases WHERE {like_or(keywords)}"
    ).fetchone()[0]


def committee_releases(con, committee_id):
    """All press releases from members while seated on committee_id, using
    member_committees_history (point-in-time roster), not member_committees
    (current-Congress-only, would misattribute pre-2025 releases)."""
    return con.execute(
        """
        SELECT p.text FROM press_releases p
        JOIN member_committees_history h ON h.bioguide = p.bioguide_id
        WHERE h.committee_id = ?
          AND h.valid_from <= p.date AND (h.valid_to IS NULL OR h.valid_to > p.date)
        """,
        (committee_id,),
    ).fetchall()


def issue_code_corpus_wide_share(con, keywords):
    total = con.execute("SELECT count(*) FROM press_releases").fetchone()[0]
    matched = keyword_match_count(con, keywords)
    return matched, total, 100 * matched / total


def issue_code_lobby_income(con, issue_code):
    row = con.execute(
        "SELECT sum(total_income_apportioned), sum(total_activities) "
        "FROM derived_issue_quarter_volume_press WHERE issue_code=?",
        (issue_code,),
    ).fetchone()
    return row[0] or 0.0, row[1] or 0


def issue_keywords_for_code(code):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
    from build_derived_issue_quarter_volume_press import ISSUE_KEYWORDS  # noqa: E402

    return ISSUE_KEYWORDS.get(code, [])


def main():
    con = sqlite3.connect(DB)

    print("=== E-recall-bug: narrow vs broad INS keyword recall ===")
    bare_n = bare_word_count(con, "insurance")
    narrow_n = keyword_match_count(con, NARROW_INS_KEYWORDS)
    broad_n = keyword_match_count(con, BROAD_INS_KEYWORDS)
    print(f"bare word 'insurance': {bare_n}")
    print(f"narrow (shared, in-production) keyword match: {narrow_n} ({100*narrow_n/bare_n:.1f}% of bare)")
    print(f"broad (case-local override) keyword match: {broad_n} ({100*broad_n/bare_n:.1f}% of bare)")

    print("\n=== E-corpus-baseline: corpus-wide INS topic share (broad keywords) ===")
    matched, total, pct = issue_code_corpus_wide_share(con, BROAD_INS_KEYWORDS)
    print(f"{matched}/{total} = {pct:.2f}%")

    print("\n=== E-committee-topic-share: HSBA04 / SSBK04, INS vs other jurisdiction ===")
    for cid, cname in COMMITTEES.items():
        rows = committee_releases(con, cid)
        total_c = len(rows)
        matched_c = sum(1 for (t,) in rows if t and any(kw in t.lower() for kw in BROAD_INS_KEYWORDS))
        pct_c = 100 * matched_c / total_c if total_c else float("nan")
        other_code = OTHER_JURISDICTION[cid]
        other_kws = issue_keywords_for_code(other_code)
        matched_other = sum(1 for (t,) in rows if t and any(kw in t.lower() for kw in other_kws))
        pct_other = 100 * matched_other / total_c if total_c else float("nan")
        _, _, other_baseline_pct = issue_code_corpus_wide_share(con, other_kws)
        print(f"{cid} ({cname})")
        print(f"  total releases (roster-at-time members): {total_c}")
        print(f"  INS: {matched_c}/{total_c} = {pct_c:.2f}%  (corpus baseline {pct:.2f}%)")
        print(f"  {other_code}: {matched_other}/{total_c} = {pct_other:.2f}%  (corpus baseline {other_baseline_pct:.2f}%)")

    print("\n=== E-lobby-money: INS lobbying scale ===")
    income, acts = issue_code_lobby_income(con, "INS")
    print(f"INS apportioned income (Senate, 2022-2026): ${income:,.0f}")
    print(f"INS total activities: {acts}")

    print("\n=== E-dollar-normalized: press per $1M lobbied, INS vs comparable industries ===")
    rows = con.execute(
        """
        SELECT issue_code, issue_name, sum(total_income_apportioned) as income
        FROM derived_issue_quarter_volume_press
        WHERE issue_code NOT IN ('GOV','SCI')
        GROUP BY issue_code
        HAVING income > 50000000
        ORDER BY income DESC
        """
    ).fetchall()
    print(f"{'code':4s} {'name':40s} {'income_M':>10s} {'press/$1M':>10s}")
    for code, name, income_val in rows:
        if code == "INS":
            press_n = broad_n
        else:
            kws = issue_keywords_for_code(code)
            press_n = keyword_match_count(con, kws)
        ppm = press_n / (income_val / 1e6)
        flag = "  <-- INS" if code == "INS" else ""
        print(f"{code:4s} {name[:40]:40s} {income_val/1e6:10.1f} {ppm:10.2f}{flag}")

    con.close()


if __name__ == "__main__":
    main()
