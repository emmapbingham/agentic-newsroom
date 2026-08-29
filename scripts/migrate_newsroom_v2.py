"""
One-shot migration: newsroom.db v1 → v2.

Schema changes:
  - screens.instrument  → screens.derived_table
  - screens adds: status (live/backlog), needs_table
  - memos     → DROP (after migrating 2 rows into leads)
  - instruments → DROP (4 built rows → derived_tables; 14 proposed → drop)
  - leads     → CREATE (append-only run-record; 20 LEADS.md entries + 2 memo rows)
  - derived_tables → CREATE (4 rows from built instruments)
  - sweeps    → CREATE (1 row from 2026-06-11 sweep)
"""

import sqlite3
import sys
from pathlib import Path

DB = Path("investigations/newsroom.db")
if not DB.exists():
    sys.exit(f"DB not found: {DB}")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = OFF")

# ── helpers ──────────────────────────────────────────────────────────────────

def run(sql, params=()):
    cur.execute(sql, params)

def rows(sql, params=()):
    return cur.execute(sql, params).fetchall()


# ── Phase 1: read old state before touching anything ─────────────────────────

old_screens = rows("SELECT id, name, contrast_type, instrument, baseline, sql_path, created_at, notes FROM screens")
old_screen_runs = rows("SELECT id, screen_id, run_at, params, n_candidates, shortlist_path, figures_path, notes FROM screen_runs")
old_instruments_built = rows("SELECT name, description, builder_script, table_name FROM instruments WHERE status='built'")
old_memos = rows("SELECT id, slug, path, lead_slug, screen_run_id, status, notes FROM memos")

# Which screen ids have at least one run?
run_screen_ids = {r["screen_id"] for r in old_screen_runs}

print(f"Old screens: {len(old_screens)}")
print(f"  with runs (→live): {len([s for s in old_screens if s['id'] in run_screen_ids])}")
print(f"  no runs  (→backlog): {len([s for s in old_screens if s['id'] not in run_screen_ids])}")
print(f"Built instruments: {len(old_instruments_built)}")
print(f"Memos: {len(old_memos)}")


# ── Phase 2: drop old tables, recreate screens ────────────────────────────────

run("DROP TABLE IF EXISTS memos")
run("DROP TABLE IF EXISTS instruments")

# Recreate screens with new columns
run("DROP TABLE IF EXISTS screens_new")
run("""
CREATE TABLE screens_new (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    contrast_type TEXT CHECK (contrast_type IN
                  ('outlier-vs-peers','self-over-time','source-vs-source',
                   'absence','data-vs-law','population-structure')),
    derived_table TEXT,
    baseline      TEXT NOT NULL,
    sql_path      TEXT,
    status        TEXT NOT NULL DEFAULT 'live'
                  CHECK (status IN ('live','backlog')),
    needs_table   TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    notes         TEXT
)
""")

for s in old_screens:
    is_live = s["id"] in run_screen_ids
    status = "live" if is_live else "backlog"
    needs_table = None if is_live else s["instrument"]
    run("""
        INSERT INTO screens_new
        (id, name, contrast_type, derived_table, baseline, sql_path, status, needs_table, created_at, notes)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (s["id"], s["name"], s["contrast_type"], s["instrument"],
          s["baseline"], s["sql_path"], status, needs_table,
          s["created_at"], s["notes"]))

run("DROP TABLE IF EXISTS screens")
run("ALTER TABLE screens_new RENAME TO screens")
print(f"screens migrated: {cur.execute('SELECT count(*) FROM screens').fetchone()[0]}")


# ── Phase 3: restore screen_runs (foreign key now points at new screens) ──────

run("DROP TABLE IF EXISTS screen_runs_new")
run("""
CREATE TABLE screen_runs_new (
    id            INTEGER PRIMARY KEY,
    screen_id     INTEGER NOT NULL REFERENCES screens(id),
    run_at        TEXT NOT NULL DEFAULT (datetime('now')),
    params        TEXT,
    n_candidates  INTEGER,
    shortlist_path TEXT,
    figures_path  TEXT,
    notes         TEXT
)
""")
for r in old_screen_runs:
    run("""
        INSERT INTO screen_runs_new
        (id, screen_id, run_at, params, n_candidates, shortlist_path, figures_path, notes)
        VALUES (?,?,?,?,?,?,?,?)
    """, (r["id"], r["screen_id"], r["run_at"], r["params"],
          r["n_candidates"], r["shortlist_path"], r["figures_path"], r["notes"]))

run("DROP TABLE IF EXISTS screen_runs")
run("ALTER TABLE screen_runs_new RENAME TO screen_runs")
print(f"screen_runs migrated: {cur.execute('SELECT count(*) FROM screen_runs').fetchone()[0]}")


# ── Phase 4: create derived_tables (4 built instruments only) ─────────────────

run("DROP TABLE IF EXISTS derived_tables")
run("""
CREATE TABLE derived_tables (
    id            INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    answers       TEXT NOT NULL,
    builder_script TEXT
)
""")

for inst in old_instruments_built:
    # answers = first sentence of description
    desc = inst["description"] or ""
    answers = desc.split(".")[0].strip() + "." if "." in desc else desc[:200]
    run("INSERT INTO derived_tables (name, answers, builder_script) VALUES (?,?,?)",
        (inst["table_name"] or inst["name"], answers, inst["builder_script"]))

print(f"derived_tables created: {cur.execute('SELECT count(*) FROM derived_tables').fetchone()[0]}")


# ── Phase 5: create sweeps (1 row) ────────────────────────────────────────────

run("DROP TABLE IF EXISTS sweeps")
run("""
CREATE TABLE sweeps (
    id              INTEGER PRIMARY KEY,
    run_at          TEXT NOT NULL,
    grid            TEXT,
    tokens          INTEGER,
    agents          INTEGER,
    n_screens_added INTEGER,
    report_path     TEXT,
    notes           TEXT
)
""")
run("""
INSERT INTO sweeps (run_at, grid, tokens, agents, n_screens_added, report_path, notes)
VALUES (?,?,?,?,?,?,?)
""", ("2026-06-11",
      "contrast×grain 6×6",
      2200000,
      28,
      33,
      "investigations/sweeps/2026-06-11-grid-sweep.json",
      "First grid sweep. 26 Sonnet scouts + Fable synthesis + Haiku clerk. "
      "125 instrument proposals → 18 merged/ranked, 144 screens → 33, 73 lead ideas → 20 new leads."))

print(f"sweeps created: {cur.execute('SELECT count(*) FROM sweeps').fetchone()[0]}")


# ── Phase 6: create leads table and populate ─────────────────────────────────

run("DROP TABLE IF EXISTS leads")
run("""
CREATE TABLE leads (
    id              INTEGER PRIMARY KEY,
    slug            TEXT NOT NULL UNIQUE,
    screen_run_id   INTEGER REFERENCES screen_runs(id),
    story           TEXT NOT NULL,
    claim           TEXT,
    probe_sql       TEXT,
    scout_number    TEXT,
    boring_explanation TEXT,
    surfaced_at     TEXT NOT NULL DEFAULT (datetime('now')),
    promoted_at     TEXT,
    case_slug       TEXT
)
""")

# LEADS.md entries — 20 leads from the file (sweep-derived + originals).
# surfaced_at='2026-06-11' for sweep-derived; '2026-06-13' for desk-verified;
# '2026-06-16' for ways-means (promoted from LEADS.md that date).
# screen_run_id set where the entry cites a specific run.

leads_data = [
    # slug, screen_run_id, story, claim, scout_number, boring_explanation, surfaced_at, promoted_at, case_slug
    (
        "senate-duplicate-disclosure-inflation",
        4,  # screen run 4
        "970 original Senate quarterly reports were filed twice under different UUIDs with identical income — $35.1M double-counted, about 90% of it same-day clerical re-submissions. Top offenders are major lobbying firms: Brownstein Hyatt, Bracewell, BGR. The duplicate rate is 0.39% of qualifying quarterly filings.",
        "970 original Senate quarterly filings (Q1–Q4 only) have byte-identical income duplicates, totalling $35.1M at a 0.39% rate, ~90% same-day.",
        "$35.1M / 970 dupes (scout said 970/$35M — confirmed)",
        "Same-day duplicates are overwhelmingly clerical re-submissions (corrected filing, same day). The 10% different-day group may include intentional re-filings after a data correction window. Neither class implies fraud.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "hunter-conviction-disclosure-gaps",
        None,
        "Duncan Hunter filed 6 out of 6 Senate and 9 out of 10 House quarterly reports after his federal conviction without the mandatory conviction disclosure. One earlier filing that does include the disclosure forecloses any ignorance defense — he knew the requirement and stopped complying.",
        "Duncan Hunter filed 15/16 post-conviction LDA reports with the mandatory conviction disclosure omitted; one prior disclosure forecloses an ignorance defense.",
        "6/6 Senate + 9/10 House post-conviction reports missing disclosure (scout-reported, unverified)",
        "Some convictions may not trigger mandatory LDA disclosure depending on charge type and timing. The prior disclosure, if confirmed, is the key record.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "chair-power-premium",
        8,  # screen run 8
        "Full-committee chairs raise 1.9 times the lobbying-reported FECA money of their committee's rank-and-file on average — $2.53M vs $1.53M — across 48 of 49 committees. The across-committee range is 2–7×: Homeland Security 6.8×, Ways & Means 4.7×, Energy & Commerce 3.9×. This is the structural say-vs-pay finding: the gavel itself is the money magnet.",
        "Full-committee chairs raise 1.9× their committee's rank-and-file FECA on average (48/49 committees); the across-committee range is 2–7×.",
        "1.9× average, 2–7× range (screen run 8, verified)",
        "Chairs run more expensive reelection campaigns and are sought-after for party fundraising events regardless of committee jurisdiction — the premium may reflect general seniority/visibility, not committee-specific cultivation.",
        "2026-06-13",
        None,
        None,
    ),
    (
        "rr-disclosure-dropoff",
        None,
        "478 lobbyists disclosed their covered government position at registration then omitted it from every subsequent quarterly filing — a sector-wide compliance rate that falls from 62% on LD-1s to 25–27% on quarterly reports. Each individual's own LD-1 is the proof that the disclosure was once made.",
        "478 lobbyists disclosed covered_position at LD-1 registration then omitted it from all subsequent quarterlies; sector rate drops 62%→25–27%.",
        "478 lobbyists, 62%→25-27% rate (scout-reported, unverified)",
        "Quarterly re-disclosure may not be legally required under the LDA — the obligation may apply only at registration. The legal requirement needs confirmation from LDA guidance before any 'violation' framing.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "silent-gatekeepers",
        None,
        "Several health-committee members took six-figure-plus lobbying-reported contributions from health-sector registrants while publishing far below their committee peers on health topics — but only for the ~247 members with full press-scraper coverage. Named members in the full-coverage set: Adrian Smith, Hern, LaHood, Bentz, Houchin, Griffith.",
        "Health-committee members taking large health-sector contributions publish significantly less health-topic press than full-coverage committee peers.",
        "6 named members (scout-reported, unverified — coverage flags required)",
        "The press coverage gap is the primary confound: Guthrie has 16 releases, Jason Smith 10, Jordan 0 — these are scraper gaps, not silence. Any absence claim must be restricted to ~247 full-coverage members.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "trump-transition-access-surge",
        9,  # screen run 9 (registrant-transition-income-surge)
        "A cluster of GOP-aligned lobbying firms — Ballard Partners, Miller Strategies, Continental Strategy, Mercury, Checkmate — surged simultaneously in income, new issue codes, client churn, and rightward LD-203 giving across the post-election quarters. Ballard rose +140% QoQ vs +47% for the next peer. Three simultaneous signals timed to the transition make this more than a routine post-election bump.",
        "5 GOP-aligned firms show simultaneous income surge, new-issue expansion, client churn, and contribution shift in Q4 2024–Q1 2025; Ballard +126%, Miller +118%.",
        "Ballard +126%, Miller +118% (deduped, confirmed); Continental +303% (scout said +1309% — corrected)",
        "Post-election income growth for access-focused firms is structurally expected when the party they are aligned with wins the White House. The story is scale-vs-peers and simultaneous multi-signal break, not growth per se.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "tariff-2025-stealth-surge",
        7,  # screen run 7 (issue-new-entrant-rush)
        "Tariff (TAR) lobbying tripled in 2025, driven by 211 first-time TAR registrants — of whom ~126 are genuinely new to lobbying. TAR is a ~38× outlier in new-entrant count vs the next-most-rushed issue. The newly mobilized cohort is ~36% foreign-linked and ~90% seeking relief from the 2025 tariff actions. The headline surge is well-covered; the foreign-cohort and quantified relief split are under-reported.",
        "TAR lobbying activities rose 381→1,248 in 2025; 211 first-time TAR registrants (~126 genuinely new); TAR is a ~38× new-entrant outlier vs all other issues.",
        "+152 excess new TAR entrants vs +4 for next issue (screen run 7, verified); Ballard 11→82 TAR activities",
        "Post-election issue-code surges are common for trade topics when a new administration brings a new trade agenda. The story is the singularity (38× vs next issue) and the foreign-cohort composition, not growth per se.",
        "2026-06-13",
        "2026-06-13",
        "tariff-2025-stealth-surge",
    ),
    (
        "house-senate-client-disclosure-asymmetry",
        None,
        "Dual-chamber registrants disclose modestly more clients to the House than the Senate — 2,095 house-only vs 612 senate-only client engagements, a 3.4× asymmetry. This direction survived verification but the magnitude collapsed from the sweep's 65× (a scout name-join artifact). The gap is real but modest.",
        "Dual-chamber registrants show 3.4× more house-only vs senate-only client engagements (2,095 vs 612, 2022–25, verified).",
        "65× scout (REFUTED); verified 3.4× (2,095 vs 612) by building derived_cross_chamber_engagements",
        "Disclosure rules differ between chambers; the House LD-2 form may capture a different client-relationship grain than the Senate form, producing apparent asymmetry from a reporting-convention difference rather than strategic selective disclosure.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "revolving-door-contribution-premium",
        None,
        "Revolving-door lobbyists out-contribute non-revolvers 2.4× in LD-203 FECA and target their former committees at ~2× the base rate. All-revolver boutique firms monetize at $1.7–5.9M per lobbyist. This is a contribution-targeting angle that extends beyond the well-covered raw revolving-door count.",
        "Revolvers contribute 2.4× non-revolvers in LD-203 FECA and target former committees at ~2× base rate.",
        "2.4× / ~2× (scout-reported, unverified)",
        "Revolving-door lobbyists are typically more senior and experienced, which both increases their client revenue and increases their personal contributions independent of any committee-targeting strategy.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "gov-catch-all-miscoding",
        None,
        "Roughly $119M of Senate income is on filings coded exclusively with the 'GOV' (Government Issues) catch-all — the vaguest issue code — while ~31% of GOV-coded description text names specific policy topics. Some firms code Raytheon and Tencent client work as GOV while using specific codes elsewhere on the same filing.",
        "~$119M Senate income on exclusively-GOV-coded filings; ~31% of GOV descriptions name specific topics — selective catch-all use may obscure issue footprints.",
        "$119M exclusively-GOV income (scout-reported, unverified)",
        "GOV is the correct code for genuinely cross-agency government-management work (appropriations, procurement reform, interagency coordination). The rate of selective use vs legitimate use is difficult to distinguish without manual review.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "foreign-client-fe-omission",
        None,
        "1,311 of 1,315 non-US Senate clients have zero foreign-entity disclosure rows ever, and 66% of House LD-1s for non-US clients carry only empty placeholders. The 20%-ownership FARA trigger legitimately exempts many — but the systemic omission rate suggests either widespread exemptions or widespread non-disclosure.",
        "1,311/1,315 non-US Senate clients have zero foreign-entity disclosures; 66% of House LD-1s for non-US clients carry empty placeholders.",
        "1,311/1,315 zero FE disclosure (scout-reported, unverified)",
        "The 20%-ownership threshold for foreign-principal disclosure exempts majority-US-owned subsidiaries of foreign companies and foreign-headquartered firms with US ownership structures. Most non-US clients may legitimately fall below this threshold.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "critic-takes-money",
        None,
        "At least 20 members with 10 or more drug-pricing-critical press releases also took $100k+ from pharma and health registrants in lobbying-reported contributions. The clearest case is Richard Neal, though his releases largely attack GOP inaction rather than the industry itself — the industry classification needs careful auditing.",
        "≥20 members with 10+ drug-pricing-critical releases took $100k+ from pharma/health registrants in LD-203 FECA.",
        "≥20 members (scout-reported, unverified)",
        "Public criticism of drug pricing may attract pharma contributions as a defensive measure (they cultivate critics to have a seat at the table) or the criticism may be purely partisan (targeting the opposing party's legislative inaction, not the industry). Neal's releases target GOP inaction, which weakens the say-vs-pay framing.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "copyright-quiet-money",
        None,
        "Copyright (CPT) is the quietest big-money issue by press coverage relative to lobbying spend — ~$234M in lobbying income, 4.4 activities per press mention. IP subcommittee members hold $0.5–0.9M from CPT registrants with near-zero IP press, while Issa is the loud counterexample. Exclude Jordan (coverage gap).",
        "CPT: ~$234M lobbying income / 4.4 activities per press mention — quietest big-money ratio; IP subcommittee members show $0.5–0.9M CPT money with near-zero IP press.",
        "$234M CPT lobbying (scout-reported, unverified)",
        "Copyright issues are technical, bipartisan, and rarely generate newsworthy legislative moments — low press coverage may simply reflect low public salience, not a deliberate silence by contribution-taking members.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "retroactive-income-zeroing",
        None,
        "652 Senate amendments were filed 2+ years late, and one firm (ISEMAN) bulk-replaced 2022–24 income figures with NULL across an entire May 2025 filing session. Primacy (78 amendments) and Kimbell (62) show similar patterns. Retroactive amendments are legal, but bulk income nullification is notable.",
        "652 Senate amendments filed 2+ years late; ISEMAN bulk-replaced 2022–24 income with NULL in May 2025 (78 amendments in one session).",
        "652 late amendments; ISEMAN 78-amendment NULL session (scout-reported, unverified)",
        "Retroactive income amendment is legal and sometimes required for corrections. A firm that discovers a multi-year reporting error in a compliance review might legitimately file a batch of amendments. Manual UUID review of the ISEMAN filings is needed before any intent framing.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "bgr-see-prior-flip",
        None,
        "BGR Group used 'See prior filing' on 89.6% of 2022 covered-position rows — accounting for 96% of the entire corpus's usage of that phrase — then dropped to 0.7% by 2025. The shift tracks a possible change in compliance posture or firm policy. This dominates the covered_position field for any corpus-wide analysis involving BGR.",
        "BGR used 'See prior filing' on 89.6% of 2022 covered_position rows (96% of corpus total) then dropped to 0.7% by 2025.",
        "89.6% / 96% corpus share (scout-reported, unverified)",
        "'See prior filing' is a disclosure convention that may have been legitimate if the LD-1 registration disclosed the positions in full and the quarterly filing is referencing that. A policy change or legal review in 2023 may explain the shift without implying prior non-compliance.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "burkman-wohl-access-factory",
        None,
        "Jack Burkman and Jacob Wohl — convicted robocall fraudsters who ran a voter suppression scheme targeting Black voters in 2020 — appear across 90+ lobbying clients at 43.9× the peer average. 68.5% of their activities are coded GOV. Their filings also contain phone numbers embedded in client name fields — a sloppy-filing artifact unique to their firm.",
        "Burkman/Wohl firm: 90+ clients, 43.9× peer avg, 68.5% GOV-coded, phone numbers in client_name field; both convicted of federal voter suppression charges.",
        "90+ clients, 43.9× peer avg (scout-reported, unverified)",
        "Ohio state conviction vs federal conviction distinction matters for LDA consequences. High client counts with GOV coding and vague descriptions may reflect a legitimate government-relations business model, not fraud. The phone-number artifact is a data-quality curiosity, not an illegal act.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "defense-revolving-door-surge",
        None,
        "The share of ex-government lobbyists in Defense (DEF) lobbying rose from 41.9% to 54.2% (2022–2025), and Intelligence (INT) from 52.8% to 65.0%, while the overall corpus rate held flat at ~28–30%. Defense and Intelligence are systematically over-represented in revolving-door lobbying and trending upward.",
        "Ex-government share in DEF lobbying: 41.9%→54.2%; INT: 52.8%→65.0% (2022–2025); corpus baseline held flat ~28–30%.",
        "41.9%→54.2% DEF, 52.8%→65.0% INT (scout-reported, unverified)",
        "Defense and intelligence lobbying requires deep domain expertise that is concentrated in the ex-government population — a high revolver share is structurally expected in these issue areas and may reflect necessary specialization rather than improper influence.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "ld203-contribution-blackout",
        None,
        "Seven large lobbying firms ($5–10M in client revenue) certified 'no contributions' on all 8 of their LD-203 filings in the corpus window. Together they serve 218 clients with $322M in combined lobbying spend. The pattern may reflect a deliberate firm policy to avoid the disclosure obligation.",
        "7 firms ($5–10M revenue) certified 'no contributions' across all 8 LD-203 filings; serve 218 clients / $322M combined spend.",
        "7 firms, 218 clients, $322M spend (scout-reported, unverified)",
        "A firm-level 'no contributions' certification is legally valid if principals and employees made no qualifying political contributions during the period. Some large firms adopt such a policy deliberately. State and tribal client exemptions may further reduce the contribution universe. FEC verification is the completion step.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "flash-lobbying-foreign-clients",
        None,
        "ZTE, Nord Stream 2 AG, and Hikvision each ran single-year lobbying bursts of ~$1.2M then went dark, versus a 3+-year domestic lobbying norm. These are foreign entities that activated US lobbying for specific crises then exited — a pattern visible in the filings.",
        "ZTE, Nord Stream 2, Hikvision: single-year ~$1.2M lobbying bursts then zero activity; domestic norm is 3+ years.",
        "~$1.2M single-year bursts (scout-reported, unverified)",
        "Single-year lobbying by foreign entities may reflect legitimate crisis management (sanctions, export controls, regulatory review) that resolved, eliminating the need for ongoing lobbying. Country field misses beneficial ownership, and rebranding exits can make entities appear to go dark while continuing under a different registration.",
        "2026-06-11",
        None,
        None,
    ),
    (
        "gun-lobby-vacuum",
        None,
        "The Firearms (FIR) issue code has among the highest press coverage per lobbying activity — 2.7 press mentions per registered activity — while having comparatively little registered lobbying spend. This is the inverse of the usual pattern where heavy lobbying accompanies heavy press coverage.",
        "FIR: 2.7:1 press-to-lobby ratio — highest direction; most lobbying influence flows through FEC and NRA membership, not LDA filings.",
        "2.7:1 press-to-lobby (scout-reported, unverified)",
        "NRA-style gun-lobby influence flows primarily through FEC donations, membership mobilization, and state-level channels — not LDA lobbying filings. The LDA captures a small slice of the actual influence footprint for this issue. Framing strictly as 'what LDA filings show' is essential.",
        "2026-06-11",
        None,
        None,
    ),
]

# ways-means was promoted from LEADS.md on 2026-06-16 — also add as a lead row
leads_data.append((
    "ways-means-chair-money-magnet",
    9,  # screen run 9 (member-contribution-peer-outlier)
    "Jason Smith (R-MO), chair of the House Ways and Means Committee, is the single largest FECA outlier among House Republicans in LD-203 contribution data — $9.16M, z=6.45, 8.8× the GOP-House peer mean — and out-raises the Speaker (Mike Johnson, $6.38M) despite holding no party leadership post. The gavel-year spike (2022 $1.35M → 2023 $2.67M) is the sharpest in the full 24-chair cohort; Neal's mirror drop when he lost the same gavel confirms the mechanism. Verified SUPPORTED.",
    "Jason Smith is the #1 FECA outlier among House Republicans in LD-203 data ($9.16M, z=6.45), driven by a gavel-year spike not explained by leadership roles; the W&M gavel functions as an exceptional money magnet.",
    "$9.16M z=6.45 (screen run 9, VERIFIED — all numbers re-derive exactly)",
    "Chairs run more expensive reelection campaigns and serve as party fundraising vehicles independent of committee jurisdiction. Smith's 'LEADERSHIP PAC' honoree variant is in the corpus. The peer mean is depressed by the long tail. LD-203 captures lobbying-world money only, not FEC total.",
    "2026-06-16",
    "2026-06-16",
    "ways-means-chair-money-magnet",
))

for (slug, screen_run_id, story, claim, scout_number, boring_explanation,
     surfaced_at, promoted_at, case_slug) in leads_data:
    run("""
        INSERT INTO leads
        (slug, screen_run_id, story, claim, scout_number, boring_explanation,
         surfaced_at, promoted_at, case_slug)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (slug, screen_run_id, story, claim, scout_number, boring_explanation,
          surfaced_at, promoted_at, case_slug))

print(f"leads created: {cur.execute('SELECT count(*) FROM leads').fetchone()[0]}")
print(f"  promoted: {cur.execute('SELECT count(*) FROM leads WHERE promoted_at IS NOT NULL').fetchone()[0]}")

# ── Commit and verify ─────────────────────────────────────────────────────────

con.commit()
cur.execute("PRAGMA foreign_keys = ON")

print("\n── Final counts ──────────────────────────────────────────────────────")
for table in ["screens", "screen_runs", "leads", "derived_tables", "sweeps"]:
    n = cur.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {n}")

print("\n── Screens by status ─────────────────────────────────────────────────")
for row in cur.execute("SELECT status, count(*) FROM screens GROUP BY status"):
    print(f"  {row[0]}: {row[1]}")

print("\n── Promoted leads ────────────────────────────────────────────────────")
for row in cur.execute("SELECT slug, case_slug, promoted_at FROM leads WHERE promoted_at IS NOT NULL"):
    print(f"  {row['slug']} → {row['case_slug']} ({row['promoted_at']})")

print("\n── Tables present ────────────────────────────────────────────────────")
for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    print(f"  {row[0]}")

print("\nmemos table gone?", not bool(cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='memos'").fetchone()))
print("instruments table gone?", not bool(cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='instruments'").fetchone()))

con.close()
print("\nMigration complete.")
