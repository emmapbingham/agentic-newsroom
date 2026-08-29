#!/usr/bin/env python3
"""Diagnostic: for each ISSUE_KEYWORDS code with a single obvious bare anchor
word (the code's name/first keyword lowercased), compare the keyword-matched
press-release count to the bare-word count. A ratio far below other codes'
ratios signals likely undercounting (narrow/over-specific keywords), not a
genuinely quiet topic -- the INS code was caught this way 2026-07-02 (23%
recall vs BAN/RET's >170%). This script does NOT auto-fix anything -- it
only flags codes worth a manual look, the way INS was manually checked.

Only meaningful for codes with a natural single bare-word anchor (most
industry/topic codes have one -- "insurance", "bank", "housing"). Skips
codes with no clean single-word anchor (acronym-heavy or multi-word-only
by nature, e.g. TAR/Tariff already IS a bare word, ADV/Advertising has one).

    python scripts/audit_issue_keyword_recall.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_derived_issue_quarter_volume_press import ISSUE_KEYWORDS  # noqa: E402

DB = Path("db/gain.db")

# Manually curated bare-anchor word per code, where one obviously exists.
# Not every code has a clean single-word anchor -- only codes present here
# get audited.
BARE_ANCHORS = {
    "INS": "insurance", "BAN": "bank", "RET": "retirement", "HOU": "housing",
    "FIN": "financial", "TAX": "tax", "DEF": "defense", "ENG": "energy",
    "ENV": "environment", "EDU": "education", "IMM": "immigrant",
    "AGR": "agriculture", "HCR": "health", "TRA": "transportation",
    "VET": "veteran", "FIR": "gun", "TEC": "telecommunication",
    "AVI": "aviation", "AUT": "automotive", "MMM": "medicare",
    "PHA": "pharma", "TRD": "trade", "LBR": "labor", "BUD": "budget",
    "HOM": "homeland security", "ALC": "alcohol",
}


def main():
    if not DB.exists():
        sys.exit(f"{DB} not found")
    con = sqlite3.connect(DB)

    rows = []
    for code, anchor in BARE_ANCHORS.items():
        keywords = ISSUE_KEYWORDS.get(code)
        if not keywords:
            continue
        bare_n = con.execute(
            "SELECT count(*) FROM press_releases WHERE lower(text) LIKE ?",
            (f"%{anchor}%",),
        ).fetchone()[0]
        like_parts = " OR ".join(f"lower(text) LIKE '%{kw.lower()}%'" for kw in keywords)
        matched_n = con.execute(
            f"SELECT count(*) FROM press_releases WHERE {like_parts}"
        ).fetchone()[0]
        ratio = matched_n / bare_n if bare_n else float("nan")
        rows.append((code, anchor, len(keywords), bare_n, matched_n, ratio))

    rows.sort(key=lambda r: r[5])
    print(f"{'code':4s} {'anchor':20s} {'n_kw':>5s} {'bare_n':>8s} {'matched_n':>10s} {'ratio':>8s}")
    for code, anchor, n_kw, bare_n, matched_n, ratio in rows:
        flag = "  <-- LOW RECALL, check manually" if ratio < 0.5 else ""
        print(f"{code:4s} {anchor:20s} {n_kw:5d} {bare_n:8d} {matched_n:10d} {ratio:8.2f}{flag}")

    con.close()


if __name__ == "__main__":
    main()
