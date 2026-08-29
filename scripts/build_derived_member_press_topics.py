#!/usr/bin/env python3
"""Derived table: per-member per-issue-code per-year press-release topic share.

For say-vs-pay screens: critic-takes-money, committee-funded-silence,
high-money-zero-press, rising-money-falling-voice. Answers: how much does
member M talk about topic X in year Y?

Method: keyword search over press_releases.text via SQLite LIKE (or FTS
for larger queries). Each issue code maps to a curated keyword set. A
release is counted as "on topic" if any keyword matches. This is a recall-
oriented proxy — noisy for broad codes (HCR), tight for narrow ones (PHA).

The keyword map (expanded 2026-06-30, see investigations/invisible-provisions
log.md and skeptic finding E14) covers 75 of 79 ref_issue_codes. Deliberately
excluded: MIA, SCI, GOV, CON — generic single/double words that would swamp
the signal with false positives (see the exclusion note in
build_derived_issue_quarter_volume_press.py, the canonical copy of this map).
Unmapped codes are excluded from the panel — screens should filter to
`WHERE issue_code IN (SELECT DISTINCT issue_code ...)`.

Output columns:
  bioguide, member_name, party, state, issue_code, issue_name, year,
  n_total_releases, n_topic_releases, topic_share (0.0-1.0),
  first_release_year (coverage flag — exclude members with no 2022 data)

    python scripts/build_derived_member_press_topics.py
    python scripts/build_derived_member_press_topics.py --validate
"""
import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path("db/gain.db")
TABLE = "derived_member_press_topic_panel"

# Issue code → FTS/LIKE keyword list (OR logic — any match = on topic).
# Prefer short discriminating roots; avoid overly generic words.
# FTS special chars (+, -, *, ") are NOT used here — we build LIKE patterns.
ISSUE_KEYWORDS: dict[str, list[str]] = {
    "HCR": ["health", "hospital", "patient", "clinic", "medicaid", "medicare",
            "insurance", "aca", "affordable care", "obamacare", "prescription"],
    "PHA": ["pharma", "pharmaceutical", "drug price", "drug cost", "drug compan",
            "pill", "medication", "fda", "prescription drug"],
    "MMM": ["medicare", "medicaid", "cms ", "center for medicare", "social security",
            "entitlement"],
    "TAX": ["tax", "irs", "revenue", "tariff", "deduction", "tax cut", "tax credit",
            "tax reform", "tax code", "tax break"],
    "TRD": ["trade", "import", "export", "tariff", "wto", "usmca", "nafta",
            "free trade", "trade deal", "trade agreement", "trade war"],
    "DEF": ["defense", "military", "pentagon", "armed forces", "army", "navy",
            "air force", "marines", "national security", "ndaa", "weapon"],
    "ENG": ["energy", "nuclear", "oil", "gas", "coal", "renewable", "solar",
            "wind power", "grid", "power plant", "electricity", "natural gas"],
    "ENV": ["environment", "climate", "epa", "clean air", "clean water",
            "emissions", "pollution", "superfund", "carbon"],
    "FIN": ["financial", "wall street", "securities", "investment", "stock market",
            "sec ", "cftc", "dodd-frank", "banking regulation", "hedge fund"],
    "BAN": ["bank", "fdic", "federal reserve", "lending", "credit union",
            "mortgage", "loan", "interest rate", "financial institution"],
    "TEC": ["broadband", "spectrum", "fcc", "telecommunication", "wireless",
            "internet access", "5g", "telecom"],
    "TRA": ["transportation", "infrastructure", "highway", "transit", "rail",
            "aviation", "faa", "dot ", "federal highway"],
    "LBR": ["labor", "worker", "wage", "union", "nlrb", "osha", "workforce",
            "employment", "job", "minimum wage", "collective bargaining"],
    "IMM": ["immigr", "visa", "border", "asylum", "refugee", "daca",
            "undocumented", "deportation", "ice ", "customs"],
    "AGR": ["agriculture", "farm", "crop", "usda", "rural", "livestock",
            "drought", "food supply", "commodity"],
    "EDU": ["education", "school", "student", "college", "university", "pell",
            "title iv", "teacher", "higher education", "k-12"],
    "HOM": ["homeland security", "dhs", "tsa", "fema", "cyber", "cybersecurity",
            "terror", "counterterror"],
    "VET": ["veteran", "va ", "v.a.", "military service", "service member",
            "wounded warrior", "gi bill", "veteran benefit"],
    "HOU": ["housing", "hud", "affordable housing", "rent", "mortgage",
            "eviction", "homeless", "low-income housing"],
    "FIR": ["gun", "firearm", "second amendment", "nra", "background check",
            "gun control", "assault weapon", "mass shooting"],
    "BUD": ["budget", "appropriation", "deficit", "national debt", "spending",
            "fiscal", "government shutdown", "continuing resolution",
            "debt ceiling"],
    "ACC": ["accounting", "audit standard", "gaap", "financial reporting",
            "public company accounting"],
    "ADV": ["advertising", "ad industry", "marketing regulation"],
    "AER": ["aerospace", "space launch", "satellite industry", "space exploration"],
    "ALC": ["alcohol", "distiller", "brewer", "winer", "liquor", "drug abuse",
            "substance abuse", "opioid"],
    "ANI": ["animal welfare", "endangered species", "animal cruelty",
            "wildlife conservation"],
    "APP": ["apparel", "textile", "clothing industry", "garment"],
    "ART": ["national endowment for the arts", "entertainment industry",
            "film industry", "music industry", "arts fund"],
    "AUT": ["automotive", "automobile", "auto industry", "auto manufactur",
            "vehicle emissions", "electric vehicle"],
    "AVI": ["aviation", "airline", "airport", "faa", "air traffic control",
            "pilot shortage"],
    "BEV": ["beverage industry", "soft drink", "soda tax"],
    "BNK": ["bankrupt", "chapter 11", "chapter 7", "insolvency"],
    "CAW": ["clean air", "clean water", "water quality", "air quality standard"],
    "CDT": ["commodit", "futures market", "grain market", "livestock market"],
    "CHM": ["chemical industry", "chemical safety", "toxic substance",
            "pesticide", "pfas"],
    "CIV": ["civil rights", "civil libert", "voting rights act",
            "discrimination law"],
    "COM": ["broadcast", "radio station", "television", "streaming",
            "cable tv", "media ownership"],
    "CPI": ["computer industry", "semiconductor", "chips act", "software industry",
            "artificial intelligence regulation", "data privacy"],
    "CPT": ["copyright", "patent", "trademark", "intellectual property"],
    "CSP": ["consumer protect", "consumer safety", "product recall",
            "product safety", "cpsc"],
    "DIS": ["disaster relief", "disaster declaration", "emergency declaration",
            "fema disaster"],
    "DOC": ["district of columbia", "d.c. statehood", "washington d.c. budget"],
    "ECN": ["economic develop", "economic growth", "economic recovery",
            "small business development"],
    "FAM": ["abortion", "adoption", "reproductive right", "family planning",
            "child welfare"],
    "FOO": ["food safety", "food label", "food industry", "food and drug",
            "nutrition label"],
    "FOR": ["foreign polic", "foreign relation", "state department",
            "foreign aid", "diplomatic"],
    "FUE": ["fuel", "gasoline", "diesel", "renewable fuel standard"],
    "GAM": ["gambling", "casino", "sports betting", "gaming industry"],
    "IND": ["tribal", "native american", "indian affairs", "indian country",
            "indian gaming"],
    "INS": ["insurance industry", "insurance regulation", "insurer",
            "insurance premium"],
    "INT": ["intelligence communit", "cia ", "nsa ", "director of national intelligence",
            "fisa"],
    "LAW": ["law enforcement", "criminal justice", "police reform",
            "sentencing reform", "prison reform"],
    "MAN": ["manufactur"],
    "MAR": ["maritime", "fisheries", "fishing industry", "coast guard",
            "shipbuilding"],
    "MED": ["clinical trial", "medical research", "disease research",
            "national institutes of health", "nih funding"],
    "MON": ["u.s. mint", "digital currency", "currency manipulation",
            "gold standard", "coin production"],
    "NAT": ["natural resource", "public land", "national forest", "national monument"],
    "POS": ["postal service", "usps", "postal reform", "post office"],
    "REL": ["religious freedom", "faith-based", "religious liberty"],
    "RES": ["real estate", "land use", "conservation easement", "zoning"],
    "RET": ["retirement", "pension", "401(k)", "erisa"],
    "ROD": ["highway", "federal-aid road", "road funding", "bridge funding"],
    "RRR": ["railroad", "rail industry", "amtrak", "freight rail"],
    "SMB": ["small business", "sba loan", "small business administration"],
    "SPO": ["professional sport", "ncaa", "athlete compensation", "sports league"],
    "TAR": ["tariff"],
    "TOB": ["tobacco", "vaping", "e-cigarette", "cigarette"],
    "TOR": ["tort reform", "medical malpractice", "liability lawsuit"],
    "TOU": ["tourism", "travel industry", "hospitality industry"],
    "TRU": ["trucking", "freight", "commercial driver", "motor carrier"],
    "UNM": ["unemployment insurance", "unemployment benefit", "jobless claim"],
    "URB": ["urban develop", "municipalit", "community development block grant"],
    "UTI": ["utility bill", "utilities", "electric utility", "water utility",
            "public utility"],
    "WAS": ["hazardous waste", "nuclear waste", "solid waste", "waste disposal"],
    "WEL": ["welfare", "snap benefit", "tanf", "food stamp"],
}


def build_ddl(table: str) -> str:
    return f"""
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
    bioguide            TEXT    NOT NULL,
    member_name         TEXT,
    party               TEXT,
    state               TEXT,
    chamber             TEXT,
    issue_code          TEXT    NOT NULL,
    issue_name          TEXT,
    year                INTEGER NOT NULL,
    n_total_releases    INTEGER NOT NULL DEFAULT 0,
    n_topic_releases    INTEGER NOT NULL DEFAULT 0,
    topic_share         REAL    NOT NULL DEFAULT 0.0,
    first_press_year    INTEGER,
    PRIMARY KEY (bioguide, issue_code, year)
);
CREATE INDEX IF NOT EXISTS idx_mptp_bioguide   ON {table}(bioguide);
CREATE INDEX IF NOT EXISTS idx_mptp_issue_year ON {table}(issue_code, year);
"""


def build_rows(con: sqlite3.Connection) -> list[tuple]:
    """Compute per-member x issue x year topic hits using LIKE on text."""

    # Step 1: per-member-year release counts and first_press_year
    totals: dict[tuple, int] = {}     # (bioguide, year) -> n_total
    first_year: dict[str, int] = {}   # bioguide -> first year with data
    for bioguide, year, n in con.execute("""
        SELECT bioguide_id, year, count(*)
        FROM press_releases
        WHERE bioguide_id IS NOT NULL AND year BETWEEN 2022 AND 2026
        GROUP BY bioguide_id, year
    """):
        totals[(bioguide, year)] = n
        if bioguide not in first_year or year < first_year[bioguide]:
            first_year[bioguide] = year

    # Step 2: member metadata
    member_meta: dict[str, tuple] = {}
    for row in con.execute("""
        SELECT m.bioguide,
               coalesce(m.official_full, m.first || ' ' || m.last),
               m.last_party, m.last_state
        FROM members m
    """):
        member_meta[row[0]] = (row[1], row[2], row[3])

    # Step 3: issue code names
    issue_names: dict[str, str] = dict(con.execute("SELECT value, name FROM ref_issue_codes"))

    rows = []
    for issue_code, keywords in ISSUE_KEYWORDS.items():
        issue_name = issue_names.get(issue_code, "")
        # Build LIKE clause: lower(text) LIKE '%kw%'
        like_parts = " OR ".join(f"lower(text) LIKE '%{kw.lower()}%'" for kw in keywords)
        sql = f"""
            SELECT bioguide_id, year, count(*)
            FROM press_releases
            WHERE bioguide_id IS NOT NULL
              AND year BETWEEN 2022 AND 2026
              AND ({like_parts})
            GROUP BY bioguide_id, year
        """
        topic_hits: dict[tuple, int] = {}
        for bioguide, year, n in con.execute(sql):
            topic_hits[(bioguide, year)] = n

        # Union: all member-years in totals
        seen_pairs: set[tuple] = set()
        for (bioguide, year) in totals:
            seen_pairs.add((bioguide, year))
        # Also include pairs that appear only in topic_hits (shouldn't happen, but be safe)
        for (bioguide, year) in topic_hits:
            seen_pairs.add((bioguide, year))

        for (bioguide, year) in seen_pairs:
            n_total = totals.get((bioguide, year), 0)
            n_topic = topic_hits.get((bioguide, year), 0)
            share = n_topic / n_total if n_total > 0 else 0.0
            meta = member_meta.get(bioguide, (None, None, None))
            fy = first_year.get(bioguide)
            rows.append((
                bioguide, meta[0], meta[1], meta[2], None,
                issue_code, issue_name,
                year,
                n_total, n_topic, share, fy,
            ))

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")

    print(f"Building {TABLE}...")
    for stmt in build_ddl(TABLE).strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)
    con.commit()

    print("  Computing topic hits per issue code (21 codes × member × year)...")
    rows = build_rows(con)
    con.executemany(f"""
        INSERT INTO {TABLE}
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, rows)
    con.commit()
    print(f"  Inserted {len(rows):,} rows.")

    if args.validate:
        print("\n--- validation ---")
        for row in con.execute(f"""
            SELECT 'rows' AS m, count(*) FROM {TABLE} UNION ALL
            SELECT 'members',  count(DISTINCT bioguide) FROM {TABLE} UNION ALL
            SELECT 'issues',   count(DISTINCT issue_code) FROM {TABLE} UNION ALL
            SELECT 'years',    count(DISTINCT year) FROM {TABLE}
        """):
            print(f"  {row[0]:<15} {row[1]}")

        print("\n--- spot check: HCR 2024 top-share members (≥50 releases) ---")
        for row in con.execute(f"""
            SELECT bioguide, member_name, n_total_releases, n_topic_releases,
                   round(topic_share*100,1) as pct
            FROM {TABLE}
            WHERE issue_code='HCR' AND year=2024 AND n_total_releases >= 50
            ORDER BY topic_share DESC LIMIT 10
        """):
            print(f"  {row[0]} {row[1]:<30} {row[2]} releases, {row[3]} HCR, {row[4]}%")

    con.close()


if __name__ == "__main__":
    main()
