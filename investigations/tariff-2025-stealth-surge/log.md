# Log — tariff-2025-stealth-surge

## 2026-06-13 (case opened)
- did: promoted from newsroom leads run-record (sweep lead, previously tracked as promising). Built on the
  deduped registrant income + issue panels (engine #2). Seeded `case.md`,
  `evidence.md` (E1–E6), `queries.sql` (q1–q7).
- found: the quantitative core is verified and strong —
  - E1: TAR activities 381→1,248 (2024→2025); registrants 112→310.
  - E2: 211 first-time-2025 TAR registrants (scout said ~204 — accurate).
  - E3 (strongest): TAR is a singular outlier — +152 excess new entrants vs the
    next issue's +4 (~38×). The rush is tariff-specific, not a generic post-
    election bump.
  - E4: income surge for named firms (Ballard +126%, Miller +118%, Continental
    +303%) + new names (A10, Clark Hill, Stonington, Artemis).
  - E6: incumbents scaled up too — Ballard TAR 11→82, so it's a scale-up not a
    first-timer; surge has two drivers.
- dead ends / corrections: scout's Continental +1309% was wrong (verified +303%);
  scout framing of Ballard as a new TAR entrant is wrong (it's a scale-up).
- open questions: who are the new clients and what are they lobbying FOR? Is part
  of the surge TRD→TAR reclassification? Does press lead or lag?
- then did: ran `queries.sql#q7` (TRD vs TAR) + a within-corpus left-censoring
  proxy. Results (E7, and E2 refined):
  - TRD did NOT shrink as TAR rose (TRD 5,705→8,108; TAR 381→1,248) → the surge
    is NOT reclassification. Refutation cleared; confidence trending up.
  - Of 211 first-time-TAR registrants, 85 had prior TRD → ~126 genuinely new.
    Qualified E2's "211 brand-new" down to "~126 genuinely new + 85 adding TAR."
- then did: client-composition drilldown for the ~126 genuinely-new (q8/q9 →
  E8, E9).
- found: the cohort's clients are import-exposed + foreign-linked manufacturers
  (Schaeffler/Tetra Pak/Wacker/Alpek), pharma supply chains (Teva/Amgen/Takeda),
  and DIRECT foreign trade associations (UNICA/IBA Brazil, Orica Australia,
  DigitalEurope) — descriptions show them reacting to the 2025 reciprocal/IEEPA
  tariffs, America-First Trade Policy memo, and Section 232, mostly seeking
  relief/monitoring; a protection minority (Berry Amendment, steel). The
  narrative the case needed is now in place; defensible story written into
  case.md verdict.
- caveats logged: client country field reads "US" for foreign-owned subsidiaries
  (beneficial ownership hidden); E9 descriptions are illustrative (10 longest),
  not a representative relief-vs-protection census.
- NEXT: quantify the relief-vs-protection split by classifying ALL cohort TAR
  descriptions — a good first **Haiku enrichment** job (→ a `derived_*` reference
  table with method/confidence per row). Then independent builder→red-team→
  verification (reference/verification.md, builder→skeptic→judge) before report-grade. (Lower priority:
  foreign-ownership name resolution; lead-lag vs press once the press panel exists.)

## 2026-06-14 (novelty-scan: well-covered)
- did: ran the new newsroom `novelty-scan` step on this case (dogfooding it).
- found: **`well-covered` core** — OpenSecrets/LegiStorm published the same
  LDA-filings analysis (firms 59→231; orgs 120→382; **Ballard ~$3.8M, >¼ of all
  tariff lobbying revenue**); BGov/Reason covered the relief/exemption fight at
  the outcome level. We independently reproduced their numbers → a **precision
  exhibit**, not a scoop. Verdict + citations written into `case.md` (Prior
  coverage); `coverage:` added to frontmatter.
- consequence: reframed the case — keep as a precision exhibit + work the
  **`under-reported` seam** (foreign-cohort; the quantified relief-vs-protection
  split). Coverage is contemporaneous → **lead-lag owed-item retired** (no
  lead-time claim available).

## 2026-06-15 (enrichment spec locked)
- did: with editor, scoped + specified the Haiku stance-classification job.
  Decisions: **5 labels** (relief / protection / monitoring / mixed / unclear —
  mixed split from unclear: one is a position, one is disclosure-quality);
  **scope = all Senate TAR activity, all years, whole market** (not just the
  cohort — the baseline contrast is the finding; all-years buys a before/after
  baseline). Classification unit = **distinct normalized description** (~1,156
  all-years; ~650 in 2025), joined back to activities. Central rule: classify the
  **direction of the ask, not the instrument** (232/301/AD-CVD/de-minimis are
  direction-neutral — verified in the data: "301 exclusion letters" = relief vs a
  domestic AD/CVD petition = protection).
- wrote: `analysis/stance-classification-spec.md` — the full rubric, table schema
  (`derived_tariff_stance`, reference tier, per-row method/confidence + cohort
  tag), classifier prompt skeleton, and the run plan (gold set → pilot →
  threshold → fan-out → build → independent verify). Cost ~0.12–0.15M tokens
  (~5–7% of one grid sweep).
- NEXT (at desk): hand-label the ~40-row gold set, pilot one Haiku agent against
  it, set the confidence threshold, then fan out. Held for the desk — the run
  itself is the only remaining step.

## 2026-06-15 (enrichment EXECUTED → E10)
- pilot: 40-row Opus-gold set; Haiku v1 = 72% raw / 88% collapsed, 2 systematic
  errors (monitoring-overreach, rhetoric→mixed). Rubric v2/v3 fixes; re-pilot
  Haiku+Sonnet both 85% raw, **16/16 high-trust directional calls = 100%**, 0
  false-protection. Chose dual+Opus-adjudication (~$2). Detail: `analysis/pilot_report.md`.
- run: dual-classify all 1,156 distinct TAR descriptions (16 agents, 370K tok;
  87% exact / 89% collapsed agreement) → 173 contested → Opus adjudication
  (3 agents, 98K tok) → `analysis/build_stance.py` (canonical dedup, cohort tag).
- **found (E10):** among directional activity, **relief 92% / protection 4% (all-years,
  conf≥0.8); ~9:1 to ~21:1 relief:protection.** **Baseline reframe:** relief skew is
  *market-wide* (new 84% / incumbent 90% / established 86%) — the entrant story is
  entry/volume, NOT a distinctive stance. Only ~23% of TAR activity discloses a
  direction (disclosure-quality finding). E8/E9 "mostly relief" confirmed + quantified.
- NEXT: independent red-team of the LLM labels (all 52 protection calls + sample
  agreed-relief; fix self-contradictory id 78), then foreign-ownership share +
  pre-2022 spot-check before report-grade.
- then did: **red-team** — independent Opus verifier re-classified a 94-item
  worklist BLIND + strict-on-protection (all 21 protection + all 12 mixed + 30
  relief + 30 unclear + id78). `derived/redteam_report.md`.
- found: **finding holds; all corrections conservative.** Protection 15/21
  confirmed → 6 refuted (Auxin petition / "inclusion" named w/o verb; 2 disputed
  299/300) → canonical protection **52→42**. relief sample 29/31 (94%) confirmed.
  unclear sample: 6/30 actually relief (MTB/GSP) → **relief is a lower bound**.
  mixed corrected (251/305→relief — the "extend exclusions≠tariffs" trap;
  757/758→protection). id 78 → protection. **Red-teamed split: relief 90% /
  protection 6% / mixed 3%, ~14:1.** E10 stance finding is now verified.
- NEXT: foreign-ownership share + pre-2022 spot-check; then report-grade.

## 2026-06-15 (owed items closed → report-ready)
- **E11 foreign-ownership:** cohort = 126 regs / 155 distinct TAR clients. Declared
  non-US only 6.5%; foreign-entity disclosures 17/155. Sonnet inference pass
  (`client_foreign.json`) → **~36% foreign-linked (56/155), 39% activity-weighted**
  — the 6.5%→36% gap is the finding (country field hides it). Named: Schaeffler/
  Alpek/Takeda/Tetra Pak/Teva/Wacker/Dompé/DigitalEurope/bioMérieux/Apotex.
- **E12 pre-2022 spot-check (web, LDA API):** 4/6 confirmed no pre-2022 tariff
  (Clark Hill earliest-filing-2022; Westwin/A10/Teva earliest-tariff-2025);
  Checkmate+Amgen inconclusive (text-filter blind — descriptions omit "tariff").
  Method validated: catches Ballard's tariff work to 2018. No left-censoring found.
- detail: `derived/owed_items_results.md`. Confidence → medium-high; **report-ready**
  modulo named-protection-from-confirmed-set + foreign-share-is-inferred caveats.
