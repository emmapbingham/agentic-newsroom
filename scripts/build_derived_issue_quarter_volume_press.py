#!/usr/bin/env python3
"""Derived table: per-issue-code per-quarter lobbying volume and press release volume.

Answers:
  - How many LDA lobbying activities per issue code per quarter? (Senate + House)
  - What is the filing-weighted income attributable to each issue-code-quarter?
  - How many congressional press releases mention each issue code per quarter?
  - What is the lobby-to-press ratio per issue code?

Used by screens:
  - quiet-issue-quadrant  (79 codes ranked by lobby/press divergence)
  - issue-quarterly-surge (z-score per issue-code-quarter vs own 2022-24 baseline)
  - issue-lobby-press-lead-lag (monthly/quarterly lead-lag correlation)

Income apportionment:
  Filing income is divided evenly across all issue codes active in that filing.
  This avoids the 2.17x overcount that comes from summing raw income across codes.
  Quarterly originals only (filing_type IN ('Q1','Q2','Q3','Q4') for Senate;
  report_type IN ('Q1','Q2','Q3','Q4') for House), income_amt > 0.

Press volume:
  Reuses the same ISSUE_KEYWORDS map as derived_member_press_topic_panel.
  A release counts for an issue-quarter if any keyword matches (lower(text) LIKE).
  'quarter' is derived from strftime('%m', date): 1-3=Q1, 4-6=Q2, 7-9=Q3, 10-12=Q4.

Output columns:
  issue_code TEXT, issue_name TEXT, year INTEGER, quarter INTEGER,
  senate_activities INTEGER, house_activities INTEGER, total_activities INTEGER,
  senate_income_apportioned REAL, house_income_apportioned REAL,
  total_income_apportioned REAL,
  n_press_releases INTEGER,
  lobby_per_press REAL  (NULL when n_press_releases = 0)

    python scripts/build_derived_issue_quarter_volume_press.py
    python scripts/build_derived_issue_quarter_volume_press.py --validate
"""
import argparse
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

DB = Path("db/gain.db")
TABLE = "derived_issue_quarter_volume_press"

# Same keyword map as derived_member_press_topic_panel — must stay in sync.
#
# Coverage: 75 of 79 ref_issue_codes. TOR (Torts) is included but sparse
# (~36 raw hits pre-quarter-split for "tort reform"/"medical malpractice") —
# treat any TOR ranking as low-confidence due to small absolute N, not as a
# reason it was excluded. Deliberately EXCLUDED (too generic to
# disambiguate with LIKE matching — the keyword would catch unrelated releases
# in massive volume and swamp the signal; see skeptic finding E14,
# investigations/invisible-provisions):
#   MIA (Media) — "media" alone is ~22.7k hits, mostly generic press-cycle
#     language, not the lobbying sense (information/publishing industry).
#   SCI (Science/Technology) — "science"/"technology" together are ~17.7k hits,
#     overwhelmingly generic usage, not the LDA topic sense.
#   GOV (Government Issues) — "government" is ~42.1k hits, almost entirely
#     generic references to "the government," not a specific policy area.
#   CON (Constitution) — "constitution" is heavily used in generic rhetorical
#     framing ("constitutional duty," etc.), not the LDA topic sense.
# If a keyword set is later found for these, it needs a validation step
# (manual eyeball of a sample of matches) before being trusted, since a bad
# match here doesn't just miscount — it silently pollutes a "quiet" ranking.
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

SENATE_QUARTERLY = ("Q1", "Q2", "Q3", "Q4", "1", "2", "3", "4")
HOUSE_QUARTERLY = ("Q1", "Q2", "Q3", "Q4")


def build_ddl(table: str) -> str:
    return f"""
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
    issue_code                  TEXT    NOT NULL,
    issue_name                  TEXT,
    year                        INTEGER NOT NULL,
    quarter                     INTEGER NOT NULL,
    senate_activities           INTEGER NOT NULL DEFAULT 0,
    house_activities            INTEGER NOT NULL DEFAULT 0,
    total_activities            INTEGER NOT NULL DEFAULT 0,
    senate_income_apportioned   REAL    NOT NULL DEFAULT 0.0,
    house_income_apportioned    REAL    NOT NULL DEFAULT 0.0,
    total_income_apportioned    REAL    NOT NULL DEFAULT 0.0,
    n_press_releases            INTEGER NOT NULL DEFAULT 0,
    lobby_per_press             REAL,
    PRIMARY KEY (issue_code, year, quarter)
);
CREATE INDEX IF NOT EXISTS idx_iqvp_code ON {table}(issue_code);
CREATE INDEX IF NOT EXISTS idx_iqvp_year_qtr ON {table}(year, quarter);
"""


def period_to_quarter(period: str) -> Optional[int]:
    """Map Senate filing_period to 1-4. Returns None for non-quarterly."""
    p = (period or "").strip().upper()
    mapping = {"1": 1, "2": 2, "3": 3, "4": 4,
               "Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4,
               "FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4,
               "FIRST_QUARTER": 1, "SECOND_QUARTER": 2,
               "THIRD_QUARTER": 3, "FOURTH_QUARTER": 4}
    return mapping.get(p)


def month_to_quarter(month_str: str) -> int:
    m = int(month_str)
    return (m - 1) // 3 + 1


def compute_senate(con: sqlite3.Connection) -> tuple[
    dict[tuple, int],          # (code, year, quarter) -> activity_count
    dict[tuple, float],        # (code, year, quarter) -> apportioned_income
]:
    """Activities and apportioned income per issue-code-quarter from Senate filings."""
    activity_counts: dict[tuple, int] = defaultdict(int)
    apportioned_income: dict[tuple, float] = defaultdict(float)

    # Step 1: per-filing activity counts by code
    filing_code_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    filing_meta: dict[str, tuple[int, int, float]] = {}  # uuid -> (year, quarter, income_amt)

    rows = con.execute("""
        SELECT sf.filing_uuid, sf.filing_year, sf.filing_period,
               sf.income_amt,
               sla.general_issue_code
        FROM senate_filings sf
        JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
        WHERE sf.filing_year BETWEEN 2022 AND 2026
          AND sf.filing_period IN (
            'first_quarter','second_quarter','third_quarter','fourth_quarter',
            'Q1','Q2','Q3','Q4','1','2','3','4'
          )
          AND sf.income_amt > 0
          AND sla.general_issue_code IS NOT NULL
    """)
    for uuid, year, period, income, code in rows:
        q = period_to_quarter(period)
        if q is None:
            continue
        filing_code_counts[uuid][code] += 1
        filing_meta[uuid] = (int(year), q, float(income))

    # Step 2: apportion income evenly across codes per filing
    for uuid, code_counts in filing_code_counts.items():
        if uuid not in filing_meta:
            continue
        year, quarter, income = filing_meta[uuid]
        n_codes = len(code_counts)
        share = income / n_codes if n_codes > 0 else 0.0
        for code, n_acts in code_counts.items():
            key = (code, year, quarter)
            activity_counts[key] += n_acts
            apportioned_income[key] += share

    return dict(activity_counts), dict(apportioned_income)


def compute_house(con: sqlite3.Connection) -> tuple[
    dict[tuple, int],
    dict[tuple, float],
]:
    """Activities and apportioned income per issue-code-quarter from House filings."""
    activity_counts: dict[tuple, int] = defaultdict(int)
    apportioned_income: dict[tuple, float] = defaultdict(float)

    filing_code_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    filing_meta: dict[str, tuple[int, int, float]] = {}

    rows = con.execute("""
        SELECT hf.house_filing_id, hf.filing_year, hf.report_type,
               hf.income_amt,
               ha.issue_area_code
        FROM house_filings hf
        JOIN house_activities ha ON ha.house_filing_id = hf.house_filing_id
        WHERE hf.filing_year BETWEEN 2022 AND 2026
          AND hf.report_type IN ('Q1','Q2','Q3','Q4')
          AND hf.income_amt > 0
          AND ha.issue_area_code IS NOT NULL
    """)
    for fid, year, period, income, code in rows:
        q = period_to_quarter(period)
        if q is None:
            continue
        filing_code_counts[fid][code] += 1
        filing_meta[fid] = (int(year), q, float(income))

    for fid, code_counts in filing_code_counts.items():
        if fid not in filing_meta:
            continue
        year, quarter, income = filing_meta[fid]
        n_codes = len(code_counts)
        share = income / n_codes if n_codes > 0 else 0.0
        for code, n_acts in code_counts.items():
            key = (code, year, quarter)
            activity_counts[key] += n_acts
            apportioned_income[key] += share

    return dict(activity_counts), dict(apportioned_income)


def compute_press(con: sqlite3.Connection) -> dict[tuple, int]:
    """Press release counts per mapped issue-code-quarter."""
    press: dict[tuple, int] = defaultdict(int)

    for issue_code, keywords in ISSUE_KEYWORDS.items():
        like_parts = " OR ".join(
            f"lower(text) LIKE '%{kw.lower()}%'" for kw in keywords
        )
        sql = f"""
            SELECT year,
                   strftime('%m', date) AS month,
                   count(*)
            FROM press_releases
            WHERE date IS NOT NULL
              AND year BETWEEN 2022 AND 2026
              AND ({like_parts})
            GROUP BY year, month
        """
        for year, month, n in con.execute(sql):
            if month is None:
                continue
            q = month_to_quarter(month)
            press[(issue_code, int(year), q)] += n

    return dict(press)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"ERROR: {DB} not found", file=sys.stderr)
        sys.exit(1)

    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")

    # Issue code names
    issue_names: dict[str, str] = {}
    for code, name in con.execute("SELECT value, name FROM ref_issue_codes"):
        issue_names[code] = name

    print(f"Building {TABLE}...")
    for stmt in build_ddl(TABLE).strip().split(";"):
        stmt = stmt.strip()
        if stmt:
            con.execute(stmt)
    con.commit()

    print("  Computing Senate activities and apportioned income...")
    s_acts, s_income = compute_senate(con)

    print("  Computing House activities and apportioned income...")
    h_acts, h_income = compute_house(con)

    print(f"  Computing press volume ({len(ISSUE_KEYWORDS)} codes × 2022–2026)...")
    press_counts = compute_press(con)

    # Union all (code, year, quarter) keys
    all_keys: set[tuple] = set(s_acts) | set(s_income) | set(h_acts) | set(h_income) | set(press_counts)

    rows = []
    for key in sorted(all_keys):
        code, year, quarter = key
        s_a = s_acts.get(key, 0)
        h_a = h_acts.get(key, 0)
        s_i = s_income.get(key, 0.0)
        h_i = h_income.get(key, 0.0)
        total_a = s_a + h_a
        total_i = s_i + h_i
        n_press = press_counts.get(key, 0)
        lpp = total_a / n_press if n_press > 0 else None
        rows.append((
            code, issue_names.get(code, ""),
            year, quarter,
            s_a, h_a, total_a,
            s_i, h_i, total_i,
            n_press, lpp,
        ))

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
            SELECT 'codes',   count(DISTINCT issue_code) FROM {TABLE} UNION ALL
            SELECT 'years',   count(DISTINCT year) FROM {TABLE} UNION ALL
            SELECT 'quarters',count(DISTINCT quarter) FROM {TABLE}
        """):
            print(f"  {row[0]:<12} {row[1]}")

        print("\n--- lobby_per_press top 10 (2023-2024, ≥100 press) ---")
        for row in con.execute(f"""
            SELECT issue_code, issue_name,
                   sum(total_activities) as acts,
                   sum(n_press_releases) as press,
                   round(cast(sum(total_activities) as real)/sum(n_press_releases),1) as ratio
            FROM {TABLE}
            WHERE year BETWEEN 2023 AND 2024 AND n_press_releases > 0
            GROUP BY issue_code
            HAVING sum(n_press_releases) >= 100
            ORDER BY ratio DESC LIMIT 10
        """):
            print(f"  {row[0]} {row[1]:<35} {row[2]:>6} acts / {row[3]:>5} press = {row[4]:.1f}x")

        print("\n--- lobby_per_press bottom 10 (loud issues) ---")
        for row in con.execute(f"""
            SELECT issue_code, issue_name,
                   sum(total_activities) as acts,
                   sum(n_press_releases) as press,
                   round(cast(sum(total_activities) as real)/sum(n_press_releases),1) as ratio
            FROM {TABLE}
            WHERE year BETWEEN 2023 AND 2024 AND n_press_releases > 0
            GROUP BY issue_code
            HAVING sum(n_press_releases) >= 100
            ORDER BY ratio ASC LIMIT 10
        """):
            print(f"  {row[0]} {row[1]:<35} {row[2]:>6} acts / {row[3]:>5} press = {row[4]:.1f}x")

    con.close()


if __name__ == "__main__":
    main()
