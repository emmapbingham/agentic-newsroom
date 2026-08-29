# Evidence — tariff-2025-stealth-surge

Each block: the claim, the query/script that produces it, source records, caveats,
verdict. All figures from the deduped derived panels (rebuildable via
`scripts/build_derived_registrant_{income,issue}.py`).

## E1 — TAR lobbying roughly tripled in 2025
- **query/script:** `queries.sql#q1`
- **result:** activities by year — 2022:485, 2023:395, 2024:381, **2025:1,248**,
  2026:309 (partial). Distinct registrants 2024:112 → 2025:310.
- **source records:** aggregates over `derived_registrant_issue_panel`
  (issue_code='TAR'); drill to `senate_lobbying_activities` → `filing_uuid`.
- **caveats:** activity-count metric (issue-code rows), not dollars; 2026 partial.
- **verdict:** supports

## E2 — 211 registrants lobbied TAR for the first time in 2025 (~126 genuinely new)
- **query/script:** `queries.sql#q2`, refined by the TRD cross-check (E7)
- **result:** 211 registrants whose earliest TAR year (in the 2022– corpus) is
  2025. Of these, **85 (40%) had lobbied TRD (Trade) before 2025** — existing
  trade lobbyists newly coding tariff — leaving **~126 (60%) with no prior
  trade/tariff footprint at all** (genuinely new). Headline should say "~126
  genuinely new + 85 trade lobbyists adding the tariff code."
- **source records:** `derived_registrant_issue_panel`; named examples in E5.
- **caveats:** the 60/40 split is a within-corpus proxy; "genuinely new" still
  means "no TAR/TRD in 2022–", so a pre-2022 spot-check on lda.senate.gov for a
  sample of the 126 is still owed.
- **verdict:** supports (qualified — magnitude of novelty reduced from 211 to ~126)

## E3 — The 2025 entrant rush is tariff-SPECIFIC, a singular outlier
- **query/script:** `queries.sql#q3` (screen `issue-new-entrant-rush`, run 7)
- **result:** TAR excess new entrants vs its own 2022-24 baseline = **+152**; the
  next-highest issue (DOC) = +4; all others ≤ +4 or negative. ~38× the runner-up.
- **source records:** `derived_registrant_issue_panel` across all issue codes;
  shortlist `investigations/screens/issue-new-entrant-rush/run-7/shortlist.csv`.
- **caveats:** left-censoring inflates every issue's 2022 baseline equally, so the
  ranking is fair and TAR's excess is conservative.
- **verdict:** supports (this is the strongest single piece)

## E4 — Income surged for the named GOP-aligned firms, Q4-24 → Q1-25
- **query/script:** `queries.sql#q4` (screen `registrant-transition-income-surge`, run 6)
- **result:** Ballard $6.13M→$13.87M (+126%), Miller $4.01M→$8.74M (+118%),
  Continental +303%. New names the sweep missed: A10 +124%, Clark Hill +124%,
  Stonington +112%, Artemis +102% (all on a ≥$200k Q4-24 base).
- **source records:** `derived_registrant_income_panel` (deduped); drill to
  `senate_filings.filing_uuid`.
- **caveats:** registrant-total income, not tariff-specific income (a firm's TAR
  work is part of a larger book). Scout's Continental +1309% was wrong; verified +303%.
- **verdict:** supports (income context; not by itself tariff-attributable)

## E5 — Top first-time-2025 TAR entrants (named, sourced)
- **query/script:** `queries.sql#q5`
- **result (registrant — 2025 TAR activities — sample filing_uuid):**
  - HANCE SCARBOROUGH — 31 — `b5038d0b-ffde-402f-b22c-f5bbfeb15550`
  - CLARK HILL PUBLIC STRATEGIES LLC — 23 — `20357dfd-3f25-4c28-b09f-973711775d29`
  - FORBES-TATE — 18 — `63ad2853-1e21-4a46-bbfb-c279810d0ff6`
  - BGR GOVERNMENT AFFAIRS — 17 — `2913ab0a-9479-4748-9dab-52212644462f`
  - CHECKMATE GOVERNMENT RELATIONS — 16 — `0e80b9c4-c323-4c2b-95d9-0648b24ad1ec`
- **source records:** UUIDs resolve at
  `https://lda.gov/filings/public/filing/{uuid}/print/`.
- **caveats:** verify each firm wasn't TAR-active pre-2022; BGR being a "first-timer"
  on TAR despite its size is worth a manual look.
- **verdict:** supports

## E6 — Incumbents scaled up too (the other driver)
- **query/script:** `queries.sql#q6`
- **result:** Ballard Partners TAR activities 2022:4, 2023:4, 2024:11, **2025:82**,
  2026:19 — a ~7× jump, so Ballard is a scale-up, NOT a first-timer.
- **source records:** `derived_registrant_issue_panel`; drill to filing_uuids.
- **caveats:** distinguishes the two surge drivers (new entrants E2/E5 vs
  incumbent scale-up); refine the headline to credit both.
- **verdict:** supports (and corrects the "Ballard is a new TAR entrant" framing)

## E7 — The surge is NOT reclassification from Trade (TRD) — both rose
- **query/script:** `queries.sql#q7`
- **result:** TRD activities did not fall as TAR rose; both increased 2024→2025
  (TRD 5,705→8,108, +42%; TAR 381→1,248, +227%). TRD is the larger code and also
  surged, but its rise is driven by incumbents (TRD did not appear in the
  new-entrant-rush top, E3), whereas TAR's rise is driven by new entrants.
- **source records:** `derived_registrant_issue_panel` (issue_code in TAR, TRD).
- **caveats:** refines the framing to "a 2025 trade-and-tariff lobbying surge,
  with the dedicated tariff code drawing the distinctive *new-entrant* rush."
- **verdict:** supports (refutes the reclassification innocent explanation)

## E8 — The new entrants' clients are import-exposed / foreign-linked manufacturers + pharma
- **query/script:** `queries.sql#q8` (cohort = 126 genuinely-new, q2/E7 definition)
- **result:** top TAR clients of the genuinely-new entrants (2025), by activity:
  Westwin Elements (critical-mineral refining), Schaeffler Group USA (German auto
  parts), United Natural Products Alliance, Teva/Amgen/Takeda/Dompé/West Pharma
  (pharma + supply chain), Tetra Pak (Swedish packaging), Alpek Polyester
  (Mexican petrochem), Wacker Polysilicon (German chemical), Hanesbrands
  (apparel), TerraPower (nuclear), Mid-Continent Steel & Wire, DigitalEurope (BE).
- **source records:** `senate_clients` joined via 2025 TAR activities; drill to
  `filing_uuid`.
- **caveats:** the client `country` field reads "US" for most because they file as
  US subsidiaries — beneficial ownership (Schaeffler/Tetra Pak/Wacker/Alpek =
  foreign parents) is hidden, per the beat-book caveat. A rigorous foreign-share
  count needs name-level ownership resolution (follow-up). Top-18 by volume; not
  a census.
- **verdict:** supports (characterizes the cohort: importers + foreign-linked
  manufacturers + pharma supply chains, plus a domestic-protection minority)

## E9 — They are reacting to specific 2025 tariff actions; some are foreign trade bodies
- **query/script:** `queries.sql#q9` (sampled `description` text, 2025 TAR, cohort)
- **result (illustrative, longest descriptions):**
  - Port of Portland — "Monitor and evaluate impacts of global tariffs Reciprocal
    Tariff (IEEPA)…"
  - Apotex Corp (Canadian pharma) — "America First Trade Policy Presidential
    Memorandum…"
  - PLP Inc — Commerce/BIS request to include aluminum (Section 232).
  - Seaman Corp — SPEED Act + Berry Amendment (domestic textile sourcing — the
    *protection* side).
  - **Foreign trade associations lobbying US Congress directly:** UNICA (Brazilian
    sugarcane/bioenergy), IBA (Brazilian tree industry), Orica (Australia),
    DigitalEurope (Belgium).
- **source records:** `senate_lobbying_activities.description` + `filing_uuid`.
- **caveats:** sampled (10 longest), illustrative not representative — a full
  relief-vs-protection split needs classifying all cohort descriptions (a
  candidate Haiku enrichment job). Description text is free-form.
- **verdict:** supports (answers "what for": mostly relief/monitoring of the 2025
  tariff actions, a protection minority, and notable direct foreign-industry lobbying)

## E10 — The split is quantified: relief dominates the WHOLE market, ~9–21:1
- **query/script:** `analysis/build_stance.py` over `derived/final_map.json`
  (LLM classification of all 1,156 distinct all-years TAR descriptions:
  Haiku+Sonnet, Opus-adjudicated; rubric `analysis/classifier_prompt_v2.md` v3).
  Full write-up: `derived/stance_results.md`.
- **result (canonical activities, directional = relief+protection+mixed):**
  all-years conf≥0.8 — **relief 92% / protection 4% / mixed 4%** (n=539);
  all-conf — 86% / 8% / 7% (n=683); 2025 conf≥0.8 — 90% / 5% / 5%. **Relief
  outnumbers protection ~9:1 to ~21:1.**
- **the baseline contrast (2025):** genuine-new 84% relief, incumbent-adding-TAR
  90%, established 86% — protection a steady ~8% in every cohort. **The relief
  skew is market-wide, not a newcomer trait;** the entrant story is entry/volume
  (E2/E3/E5), not a distinctive stance.
- **source records:** per-row labels in `derived/tariff_stance_activities.csv`
  (each carries `filing_uuid` + `stance_confidence` + `source`); aggregates in
  `derived/stance_summary.json`.
- **caveats:** labels are LLM-produced (reference tier — confidence-filtered).
  Only ~23% of TAR activity discloses a determinable direction (the rest is
  topic-only `unclear`/`monitoring`) — the "% relief" is among that classifiable
  minority. Cohort directional n is small (genuine-new=37) → cohort %s noisy;
  the market-wide split is the robust number.
- **red-team (2026-06-15, `derived/redteam_report.md`):** independent **blind**
  verifier, strict on protection — finding holds, all corrections conservative.
  Protection **52→42** canonical (6/21 calls refuted under a strict blind pass;
  name protection examples from the 15+2 confirmed only), id 78 → protection,
  relief a **lower bound** (the `unclear` bucket hides MTB/GSP relief). Red-teamed
  split: **relief 90% / protection 6% / mixed 3%, ~14:1**.
- **verdict:** supports + sharpens, **red-teamed** (replaces E9's 10-anecdote read;
  baseline reframes the cohort claim; protection measured even rarer)

## E11 — Foreign-ownership share: ~36% inferred vs 6.5% declared
- **query/script:** deterministic floors over `senate_clients` +
  `senate_filing_foreign_entities`; inference pass `derived/client_foreign.json`
  (Sonnet, name + filed country → ultimate parent). Detail:
  `derived/owed_items_results.md`.
- **result:** of the cohort's **155 distinct 2025 TAR clients**, only **6.5%
  declare** a non-US country (17 carry a foreign-entity disclosure), but **~36%
  (56/155) are inferred foreign-linked**, **39% activity-weighted** (173/443).
  Named: Schaeffler[DE], Alpek[MX], Takeda[JP], Tetra Pak[SE], Teva[IL],
  Wacker[DE], Dompé[IT], DigitalEurope[BE], bioMérieux[FR], Apotex[CA],
  Anheuser-Busch[BE].
- **source records:** `senate_clients` (country/ppb_country) + per-client basis
  in `derived/client_foreign.json`.
- **caveats:** the 36/39% is LLM-inferred (reference tier, name-based); verifiable
  lower bound = 6.5% declared + the named examples. Not corporate-registry grade.
- **verdict:** supports (the cohort is heavily foreign-linked and the LDA country
  field hides it — the 6.5% → 36% gap is itself reportable)

## E12 — Pre-2022 spot-check: no left-censoring found (4/6 confirmed)
- **query/script:** public LDA API (`lda.senate.gov/api/v1/filings`), tariff-text
  filter, oldest-first, 6 genuine-new firms. Detail: `derived/owed_items_results.md`.
- **result:** confirmed **no pre-2022 tariff** for Clark Hill (earliest LDA filing
  2022), Westwin (earliest tariff 2025), A10 Associates (all 2025), Teva (earliest
  2025); **inconclusive** for Checkmate + Amgen (text filter blind — their
  descriptions omit the word "tariff"). **Method validated:** the same query
  surfaces Ballard's tariff lobbying back to **2018**.
- **source records:** LDA filing API URLs in `derived/owed_items_results.md`.
- **caveats:** sample of 6; 2 inconclusive via text filter (a code-level API query
  would close them).
- **verdict:** supports (no left-censoring in the confirmable cases)

## E13 — Congressional press-release volume grew faster than TAR lobbying volume through the surge (minor, supplementary)
- **query/script:** `investigations/screens/issue-lobby-press-lead-lag/screen.sql`
  + `scripts/screen_issue_lobby_press_lead_lag.py`, run 2026-07-02
  (`screen_runs.id=19`); source `derived_issue_quarter_volume_press`.
- **result:** 2024 Q4 → 2025 Q1: TAR lobbying activities 87→251 (2.9x), member
  press releases mentioning tariffs 25→388 (15.5x). 2025 Q1→Q2: lobbying
  251→357 (1.4x), press 388→749 (1.9x). Press volume grew faster than lobbying
  volume at every step of the ramp.
- **source records:** `derived_issue_quarter_volume_press` (issue_code='TAR');
  drills to `senate_lobbying_activities`/`press_releases` underlying it.
- **caveats:** this is a *within-corpus* comparison (member press releases vs.
  LDA filings, both primary records) — distinct from the retired "lead-lag vs
  press" check below, which was about *outside media* coverage timing (a
  novelty question). Not causal: press releases can be issued same-day while
  LDA filings have a quarterly cadence and disclosure lag, so a chamber-vs-filing
  mechanical reporting-speed difference is the strongest innocent account, not
  members "leading" the lobbying wave. Doesn't change the case verdict — logged
  as a minor supplementary data point, not a headline claim.
- **verdict:** supports (context only — not load-bearing for the case)

## Open / refutation checks
- **Relief-vs-protection split:** DONE + RED-TEAMED — E10 + `derived/redteam_report.md`.
- **Foreign-ownership resolution:** DONE — E11 (`derived/owed_items_results.md`).
- **Left-censoring spot-check:** DONE — E12 (`derived/owed_items_results.md`).
- **Lead-lag vs outside media coverage:** retired — the novelty-scan (case.md
  Prior coverage) shows coverage is contemporaneous, so no lead-time claim vs.
  outside press is available.
- **Lead-lag vs corpus press releases (internal):** DONE, minor — E13. Press
  volume outgrew lobbying volume through the surge; mechanical reporting-cadence
  difference is the likely explanation, not a real leadership signal.
