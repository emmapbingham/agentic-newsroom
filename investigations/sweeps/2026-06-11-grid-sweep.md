# Grid sweep — 2026-06-11 — editorial report

The first full-grid instrument/screen/lead proposal sweep over `db/gain.db`.
This document is the human-readable editorial record; the machine-canonical
synthesis is `2026-06-11-grid-sweep.json` (all 18 instruments, 33 screens),
and the proposals are filed in `investigations/newsroom.db` (provenance
`workflow:grid-sweep 2026-06-11`).

> **Status of every number below: scout-reported, editor-unverified.** Scouts
> ran read-only probes against the real DB and the synthesis stage deduped and
> sanity-checked across cells, but nothing here has passed the memo→verifier
> gate. Re-derive every figure before it enters a memo, case, or publication.

## Run metadata

| | |
|---|---|
| Workflow | `grid-sweep`, run `wf_e88d37dd-5f1` |
| Design | 26 scouts (Sonnet), one per contrast-type × grain cell → 1 synthesis (Fable) → 1 clerk (Haiku) |
| Cost | 2.21M subagent tokens, 28 agents, 2,568 tool calls, ~2h0m wall clock |
| Yield | 125 instrument proposals → **18 merged/ranked**; 144 screens → **33**; 73 lead ideas → **20 new leads** |
| Estimate vs actual | tokens on estimate (1.5–3M predicted); wall clock 4× over (scouts probed far deeper than briefed) |

The grid: contrast types {outlier-vs-peers, self-over-time, source-vs-source,
absence, data-vs-law, population-structure} × grains {member, registrant,
client, lobbyist, issue, committee}, pruned from 36 to 26 viable cells.

## The three story engines (synthesis verdict)

1. **Say-vs-pay at the member/committee grain.** A dozen cells independently
   proposed the same money-side panel (LD-203 dollars from issue-active
   registrants per member, via `honoree_member_map` ≥ 0.9) and the same
   press-side panel (FTS topic counts per member-month). Both are gated on two
   small *static config tables* nearly every cell flagged as its missing
   dependency: an issue-code → FTS-keyword map and a committee → issue-code
   jurisdiction map. Building those four unblocks `say-vs-pay-chairs`,
   `pbm-guthrie`, `lead-lag-timing`, and most silence/premium screens at once.
2. **The cross-chamber engagement bridge** — the disclosure system auditing
   itself. Probing already surfaced apparently-new facts: **970 Senate
   quarterly reports filed twice under different UUIDs (~$35M double-counted)**
   and a **3,255-vs-~50 asymmetry** of House-only vs Senate-only client-period
   filings by dual-chamber registrants. Where engagements match, income agrees
   (34 of 56,882 pairs differ >10%) — so the cross-chamber story is *missing
   clients, not misreported dollars*, which resolves the old
   `house-senate-discrepancy` lead's methodology.
3. **The 2025 transition/tariff shock.** Republican-aligned firms surging
   simultaneously in income, practice areas, and rightward contributions
   (Ballard +140% QoQ vs next peer +47%; Continental +1309%); TAR lobbying
   tripling with 204 first-time tariff registrants. The timeliest material.

Plus a **data-vs-law compliance vein** producing near-publishable named leads
almost for free (Hunter, RR-disclosure dropoff, BGR placeholder flip,
retroactive income-zeroing — see leads below).

## Build slate (top 10 of 18; full list in newsroom.db / JSON)

| # | Instrument | Grain | Cells | Consumers | Note |
|---|---|---|---|---|---|
| 1 | `member-issue-money-panel` | member × issue × year | 9 | 11 | most-demanded artifact; chain probe-verified |
| 2 | `issue-press-keyword-map` | issue_code × FTS expr (static, 79 rows) | 9 | 8 | pure config; load-bearing for every press-side build |
| 3 | `member-press-topic-panel` | member × topic × month | 6 | 9 | the "say" half; MUST carry per-member coverage flags |
| 4 | `cross-chamber-engagement-bridge` | registrant × client × year × qtr | 10 | 7 | one blocking probe first (client_suffix dispute) |
| 5 | `committee-issue-jurisdiction-map` | committee × issue (static, ~20–40 rows) | 7 | 8 | gate on every committee-grain screen |
| 6 | `issue-quarter-volume-press-panel` | issue × quarter ⋈ issue × month | 6 | 7 | enabler of lead-lag-timing |
| 7 | `registrant-issue-panel` | registrant × issue × year | 5 | 8 | serves tariff-surge + GOV-miscoding leads |
| 8 | `member-contribution-profile-panel` | member × year | 3 | 6 | scouts found a type-separation correctness fix the slate inherits |
| 9 | `lobbyist-revolving-door-profile` | senate lobbyist_id | 5 | 10 | build via Python script (pure SQL hit temp-space limits) |
| 10 | `registrant-income-panel` | registrant × year × qtr | 3 | 4 | anchors the transition-surge lead |

Recommended build order: 1–3 + 5 (the say-vs-pay gate, two of which are
afternoon-sized config tables), then 4 after its adjudication probe, then 6–10
as their consumer leads get promoted.

## The 20 new leads

Grouped; each lead's full claim/why/caveats and originating cells are in the
JSON. Statuses to be assigned at editor triage — none are in `LEADS.md` yet.

### Transition / tariff (timely)
- **`trump-transition-access-surge`** — Republican-aligned firms (Ballard,
  Miller Strategies, Continental, Mercury, Checkmate) simultaneously surged in
  income (+140%/+117%/+1309% QoQ vs +47% next peer), pivoted into new issue
  codes, churned 150+ clients, and shifted contributions rightward, all in the
  post-election quarters. *Caveats:* post-election growth is expected — the
  story is scale-vs-peers and client composition; one scout confused
  Ballard/Miller principals (synthesis caught it) — verify all identities.
- **`tariff-2025-stealth-surge`** — TAR lobbying tripled (444→1,506 activities)
  on 204 first-time TAR registrants; the members receiving most from TAR-active
  registrants issued near-zero tariff press. *Caveats:* lead-lag direction
  disputed between cells; press-silence claims inherit the coverage-gap caveat;
  check pre-2025 tariff work filed under TRD.

### System integrity (the disclosure regime auditing itself)
- **`senate-duplicate-disclosure-inflation`** — ≥970 identical quarterlies
  filed twice under different UUIDs (437 registrants, ~$35M double-counted);
  invisible within Senate data alone. *Caveats:* many are same-minute clerical
  re-submissions — separate accident from pattern via dt_posted/posted_by_name;
  frame as systemic data-integrity failure.
  **→ VERIFIED 2026-06-13 — the scout figure was right; an over-correction was
  wrong.** An intermediate "correction" to ~1,554/$118M (counting same-`filing_type`
  pairs) was REFUTED by an independent verifier: amendments *are* filing types
  (1A/2A/…), so that filter swept in amendment-pairs (70% of the inflated $) plus
  one $60M junk record. Restricted to original quarterlies (`filing_type ∈
  Q1..Q4`): **970 groups / $35.1M**, base rate 0.39%, **~90% same-day clerical
  double-submissions** — matching the original sweep number. Modest, mostly
  clerical; demote to a sidebar. See `memos/senate-duplicate-disclosure-inflation.md`.
- **`house-senate-client-disclosure-asymmetry`** — dual-chamber registrants
  disclose systematically more clients to the House (3,255 house-only
  client-periods vs ~50 senate-only), including foreign-linked clients; income
  agrees where engagements match. Supersedes `house-senate-discrepancy`.
  *Caveats:* client matching is the hard part (suffix-bridge dispute; ~7.4%
  FKA/DBA misses); some house-only filings are legitimate.
  **→ VERIFIED & corrected 2026-06-13 (cross-chamber bridge build):** the
  adjudicated id-join collapses the magnitude — dual-chamber registrants
  2022–2025 show **2,095 house-only vs 612 senate-only (3.4×)**, not 3,255 vs 50
  (65×). The scout's UPPER-name join inflated house-only (name variants counted
  as house-only) and missed real senate-only engagements. **Direction survives,
  magnitude does not** — reframe the lead around a modest, real asymmetry.

### Say-vs-pay & silence
- **`silent-gatekeepers`** — health-committee members receiving six-figure-plus
  sums from health-sector registrants while publishing far below committee
  peers on health topics — anchored on verified full-coverage members (Adrian
  Smith, Hern, LaHood, Bentz, Houchin, Griffith). *Caveats:* THE central
  caveat — press coverage gaps; restrict to ~247 full-coverage members;
  registrant-level money ≠ "pharma money" without single-issue subtotals.
- **`chair-power-premium`** — chairs receive 2–7× the contributions of
  rank-and-file on the same committees; premium largest where jurisdiction
  money is largest; gavel transitions show ~2× same-year spikes while outgoing
  chairs flatten — money tracks the gavel, not the person. Absorbs the
  population-level half of `say-vs-pay-chairs`. *Caveats:* member_committees is
  current-Congress only; seniority and election-cycle confounds.
- **`critic-takes-money`** — ≥20 members with 10+ press releases attacking drug
  pricing also took $100k+ from pharma/health registrants (clearest: Neal).
  *Caveats:* verify the releases actually target the industry (Neal's largely
  attack Republican inaction); audit industry classification.
- **`copyright-quiet-money`** — CPT is the quietest big-money issue (~$234M,
  4.4 activities per press mention); IP-subcommittee members with $0.5–0.9M
  from CPT-active registrants and near-zero IP press, vs Issa as the loud
  counterexample. *Caveats:* exclude Jordan (coverage artifact); widen keyword
  set; filing-weighted income only.
- **`gun-lobby-vacuum`** — FIR is the most extreme reverse-absence: most press,
  among the least registered lobbying. A methodological counterpoint showing
  the metric detects both directions. *Caveats:* NRA-style influence flows
  through FEC vehicles, not LDA — frame strictly as registered-lobbying
  footprint.

### Revolving door, quantified
- **`revolving-door-contribution-premium`** — revolvers out-contribute
  non-revolvers 2.4× and target their former committees at ~2× the base rate
  (Finance 30.9% vs 16.6%); all-revolver boutiques monetize at $1.7–5.9M
  income/lobbyist. *Caveats:* firm fixed effects; covered_position is
  self-reported free text; Senate-side only.
- **`defense-revolving-door-surge`** — ex-government share in Defense lobbying
  rose 41.9%→54.2% (Intelligence 52.8%→65.0%) while the population rate held
  flat ~28–30%. *Caveats:* 2026 partial year; per-issue disclosure-habit drift
  could mimic the trend.

### Compliance / named accountability
- **`hunter-conviction-disclosure-gaps`** — Duncan Hunter filed 6/6 Senate and
  9/10 House post-conviction reports without the mandatory conviction
  disclosure; one earlier filing WITH it forecloses the ignorance defense.
  *Caveats:* verify VALOON is Hunter's firm against source XML; confirm pardon
  doesn't alter the obligation.
- **`rr-disclosure-dropoff`** — 478 lobbyists disclosed their covered position
  at registration then omitted it from every quarterly (sector rate 62%→25–27%);
  each one's own LD-1 is the smoking gun. *Caveats:* whether quarterly
  re-disclosure is legally required needs external LDA guidance text.
- **`bgr-see-prior-flip`** — BGR used 'See prior filing' on 89.6% of 2022 rows
  (96% of all corpus usage, incl. 733 logically-impossible Q1 uses), then
  dropped to 0.7% by 2025. What triggered the cleanup? *Caveats:* legality
  unresolved; historical-pattern story.
- **`retroactive-income-zeroing`** — 652 Senate amendments filed 2+ years
  late; ISEMAN bulk-replaced 2022–2024 income figures with NULL in one May
  2025 session (also Primacy 78, Kimbell 62). *Caveats:* retroactive amendments
  are legal; manual review of UUIDs before characterizing intent.
- **`burkman-wohl-access-factory`** — the convicted robocall fraudsters at 90+
  clients (Burkman 43.9× peer average), 68.5% coded under catch-all GOV, plus
  the phone-numbers-in-client-names pattern unique to their filings. *Caveats:*
  Ohio state conviction may not trigger LDA consequences; phone-number names
  may be sole-proprietor artifacts.
- **`gov-catch-all-miscoding`** — $119M of income on filings coded exclusively
  GOV; 30.8% of GOV rows keyword-map to specific codes; firms code Raytheon and
  Tencent work as GOV while using specific codes elsewhere. *Caveats:*
  selective miscoding is arguable, not bright-line; keyword inference is
  probabilistic.

### Foreign influence
- **`foreign-client-fe-omission`** — 1,311 of 1,315 non-US Senate clients have
  zero foreign-entity disclosure rows ever (incl. EN+ Group, Alibaba, Ant,
  KNDS); 66% of House LD-1s for non-US clients carry only empty placeholder FE
  records. *Caveats:* the 20%-ownership trigger legitimately exempts many; the
  systemic rate is the story until FARA cross-referencing (external ingest).
- **`flash-lobbying-foreign-clients`** — ZTE, Nord Stream 2 AG, Hikvision ran
  single-year ~$1.2M bursts and went dark, against a 3+-year domestic norm.
  *Caveats:* country field misses beneficial ownership; timing ≠ causation;
  watch for rebrand exits.

### Inverse / strategic absence
- **`ld203-contribution-blackout`** — seven $5–10M firms certified 'no
  contributions' on all eight semi-annual LD-203s; 218 clients ($322M spend)
  are served exclusively by always-no registrants. *Caveats:* nothing illegal —
  the story is the strategy; filter state/tribal clients who cannot give;
  related-entity splits create false positives.

## What the sweep did to our priors

- **`pbm-guthrie`:** money side strengthened (Guthrie +267% on gaining the
  gavel, within a population-wide chair premium), but the say side is
  **compromised for Guthrie specifically** — 16 press releases in the corpus is
  a scraper coverage gap, not silence. The lead largely dissolves into
  `chair-power-premium` + `silent-gatekeepers`, which is the better story.
- **`house-senate-discrepancy`:** superseded with a directional methodology
  (missing clients, not income mismatch).
- **`revolving-door-commerce`:** revived in quantified form
  (`revolving-door-contribution-premium`) despite our earlier editorial
  deprioritization — the contribution-targeting angle is new.

## Adjudications required before building

1. **`senate_client_suffix` dispute — RESOLVED 2026-06-13.** The suffix is a
   numeric ref to `senate_clients.client_id` (coarser grouping), 99.5%
   coverage, 91.6% exact name agreement; the dispute was scouts testing `.id`
   (31.9%) vs `.client_id` (99.5%). Use the id-join; name-join only for the ~5%
   residual. **Instrument #4 unblocked.** (Beat book updated.)
2. **Tariff lead-lag direction** — cells disagree; needs the monthly panel
   (instrument #6), claim no direction until then.
3. **Scout prose is unverified** — the Ballard/Miller principal mix-up was
   caught, but assume others weren't. Names, titles, firm attributions all
   re-verify at memo stage.

## Cell coverage notes

- **Thin cells (re-sweep candidates):** `self-over-time × member` (leads
  rested on coverage artifacts), `source-vs-source × issue` (honest null
  result — cross-chamber issue-code divergence ≈ 0 once matching is done
  right), `absence × registrant` (mostly dead ends, salvage merged elsewhere).
- **Pruned cells the synthesis missed:** by design, 10 cells were never
  assigned (e.g. `data-vs-law × member`, `population-structure × client`,
  the `× lobbyist` cells for self/source/absence). The synthesis independently
  flagged two of them as gaps worth having — evidence those prunes were wrong.
  Add to any re-sweep.

## Run economics & process lessons

- **Sweeps are capital expenditure.** 2.2M tokens / ~2h bought a backlog that
  will take weeks to consume. Do not re-run until this slate is digested;
  future sweeps should be targeted (thin/pruned cells only).
- **Wall clock 4× over estimate** because scouts averaged ~100 tool calls each
  (2,568 total). Future scout briefs should carry an explicit probe budget
  ("verify with at most ~10 probes") — thoroughness was the right failure
  mode, but it should be a dial, not a surprise.
- **`args` plumbing failed silently** (DATE fell back to 'undated'; fixed
  deskside, renamed + provenance UPDATEd). Verify args reach the script next
  run before launching the fleet.
- **Schema-forced output worked**: 26/26 scouts returned valid structured
  proposals; the consumer-gate and baseline requirements held (125 proposals
  all named consumers; screens all stated baselines).
- **Haiku clerk did fine** (18+33 rows, 0 errors) — but per the calibration
  rule agreed deskside: tier by fleet size, not task dignity.
