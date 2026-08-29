# Derived tables (`derived_*`) — the instrument catalog

Shared, rebuildable derived tables promoted into `gain.db` because they serve
≥1 named consumer (a lead or a screen). The **derived** tier of the build DAG
(`scripts/build_gain_db.py`): each is produced by a `build_*.py` reading only
`gain.db`, is source-scoped + idempotent, and logs to `ingest_log` at
`tier='derived'`. Refresh one in place with
`python scripts/build_gain_db.py --only <stage>`.

This file is how an agent discovers an instrument instead of recomputing it —
**check here before computing anything from raw tables.** Each entry gives the
grain, the builder, the questions it answers, and any caveats baked in.

---

## `derived_cross_chamber_engagements`

The cross-chamber engagement bridge — pairs House and Senate LDA filings so the
two parallel disclosure systems can be checked against each other.

- **Grain:** one row per `(registrant_id, client_group_id, filing_year, quarter)`
  engagement-quarter. 382,809 rows (370,013 `both`, 10,552 `senate_only`,
  2,244 `house_only`).
- **Builder / stage:** `scripts/build_derived_cross_chamber.py` (stage
  `cross_chamber`); validate `scripts/validate_cross_chamber.py`.
- **Keys.** `registrant_id` = `senate_registrants.id` (= the verified 100%
  Senate↔House registrant bridge). `client_group_id` = `senate_clients.client_id`
  (coarse grouping), reached from the House side by the **adjudicated** join
  `CAST(house_filings.senate_client_suffix AS INTEGER) = senate_clients.client_id`
  (99.5% coverage — **not** `senate_clients.id`, 31.9%; see the
  `docs/beat_book.md` beat book). Quarters Q1–Q4 aligned across
  chambers; House `REG`/LD-1 registrations excluded.
- **Columns:** `presence` (`both`/`senate_only`/`house_only`), `senate_n`,
  `senate_income_sum`, `senate_filing_uuids`, `house_n`, `house_income_sum`,
  `house_filing_ids`, display `registrant_name`/`client_name`.
- **Questions it answers:**
  - Which engagements appear in one chamber but not the other? (`presence`)
  - Client-disclosure asymmetry for dual-chamber registrants.
  - Income (dis)agreement where an engagement is filed in both chambers.
  - A navigation layer to the duplicate-inflation screen (drills to filings).
- **Consumers:** `house-senate-client-disclosure-asymmetry`,
  `senate-duplicate-disclosure-inflation`, `house-senate-discrepancy` (backlog),
  `foreign-client-fe-omission` (cross-check).
- **Provenance:** aggregates carry the source keys (`*_filing_uuids`,
  `house_filing_ids`) — always verify a claim back to the filing
  (`lda.gov/filings/public/filing/{uuid}/print/` for lobbying filings,
  `lda.gov/filings/public/contribution/{uuid}/print/` for contribution
  filings — different path per record type, trailing `/print/` required —
  or `house_filing_id`).
- **Caveats / facts established at build (these CORRECT the 2026-06-11 sweep):**
  - **Client-disclosure asymmetry is ~3×, not 65×.** Dual-chamber registrants
    2022–2025: **2,095 house-only vs 612 senate-only** engagement-quarters.
    The sweep's scout (UPPER-name join) reported 3,255 vs ~50; the name join
    inflated house-only (un-unified name variants) and missed real senate-only
    engagements. Direction (House discloses more) holds; magnitude does not.
  - **Senate "duplicates" = ORIGINAL quarterlies only (`filing_type ∈
    Q1..Q4`).** A true duplicate is one original quarterly report filed twice
    (identical >0 income, ≥2 distinct UUIDs): **970 groups / $35.1M**, base rate
    0.39%, **~90% same-day clerical** double-submissions. Amendments (1A/2A/…)
    and year-end (Y) are separate filing types and are NOT duplicates — an
    independent verifier (2026-06-13) showed that an earlier same-`filing_type`
    definition wrongly counted amendment-pairs + a $60M junk record, inflating
    this to a since-retired ~1,554/$118M. Detection is filing-grain (query
    `senate_filings`); this table's `senate_n` only flags candidates.
  - **Do NOT use `senate_income_sum`/`house_income_sum` for cross-chamber
    income *comparison*.** They sum across all filings in an
    engagement-quarter, so Senate duplicates and multi-filing (amendments,
    multiple LD-2s) inflate one side: 707/707 of >10% "mismatches" were
    multi-filing artifacts, not real discrepancies (true-income-mismatch
    screen run 3, quarantined). Income agrees at the true per-filing grain.
  - `senate_income_sum` is sparse (~65% of Senate filings carry parsed income);
    sums skip NULLs. `house_only` includes a tiny known residual (≤~14 rows
    across ~7 placeholder House registrant ids that resolve to no Senate
    registrant — `registrant_name` is NULL there).

---

## `derived_registrant_income_panel`

Senate registrant income time-series — for income-surge detection (the 2025
transition lead).

- **Grain:** `(registrant_id, filing_year, quarter)`. 83,242 rows.
- **Builder / stage:** `scripts/build_derived_registrant_income.py`
  (stage `registrant_income`); validate `scripts/validate_registrant_income.py`.
- **Dedup discipline (important):** income is reduced to ONE canonical filing per
  `(registrant, client, year, quarter)` = latest-posted (`max(dt_posted)`), which
  supersedes duplicates and adopts amendment values, *then* summed across clients.
  Removed 4.2% of raw income ($446M) as dupes/amendments. Latest-posted means a
  retroactive amendment that NULLs income (the retroactive-income-zeroing lead)
  correctly drops it.
- **Columns:** `n_clients`, `n_with_income`, `income_sum`. Senate-only (House
  income is sparse/differently reported).
- **Consumers:** `trump-transition-access-surge`, registrant outlier/surge screens.
- **Verified at build:** Ballard Partners $6.13M→$13.87M (+126%), Miller
  Strategies $4.01M→$8.74M (+118%), Continental Strategy +303%, Q4-2024→Q1-2025 —
  the transition premise holds (scout magnitudes were close for Ballard/Miller,
  wildly high for Continental at +1309%).
- **Caveats:** ~65% income coverage; aggregate the parsed column, quote the raw
  filing; verify any firm back to its `filing_uuid`s.

## `derived_registrant_issue_panel`

Senate registrant × issue × year activity panel — for issue-entry/surge
detection (the 2025 tariff lead).

- **Grain:** `(registrant_id, issue_code, filing_year)`. 123,085 rows.
- **Builder / stage:** `scripts/build_derived_registrant_issue.py`
  (stage `registrant_issue`); validate `scripts/validate_registrant_issue.py`.
- **Dedup:** built on the SAME canonical filing set as the income panel, so
  duplicate/amendment filings don't inflate activity counts.
- **Columns:** `issue_display`, `n_activities`, `n_engagements`.
- **Consumers:** `tariff-2025-stealth-surge`, `gov-catch-all-miscoding`,
  registrant issue-mix screens.
- **Verified at build:** TAR (Tariff) activities 381→1,248 (2024→2025); **211
  registrants whose first TAR year is 2025** (scout said ~204 — accurate). The
  tariff-surge premise holds and the scout numbers were robust here, unlike the
  cross-chamber leads.
- **Caveats:** activity counts, not dollars; an "activity" is one issue-code row
  on a filing; GOV is a catch-all (see `gov-catch-all-miscoding`).

## `derived_registrant_income_integrity`

Flags Senate registrants whose self-reported income is implausible relative
to their own scale — surfaced from a single confirmed crank filing (see below)
that distorted a Family/Abortion issue-code income aggregate by ~two-thirds
for 2025.

- **Grain:** `(registrant_id, income_amt)` — one row per repeated-flat-income
  cluster. 16 rows total.
- **Builder / stage:** `scripts/build_derived_registrant_income_integrity.py`
  (stage `registrant_income_integrity`).
- **Signal:** the same `income_amt` reported on ≥3 filings (rules out one-off
  large but real contracts — a genuine crank signature is a number that never
  moves quarter to quarter regardless of activity), for a registrant with ≤2
  clients and ≤2 lobbyists ever, at ≥$100k (small legitimate flat-retainer
  solo shops cluster $15k–$100k in this corpus; the LOC case is 18.9× above
  the next-highest `income_per_activity` in the flagged set).
- **Confirmed crank (2026-07-04):** "STATE OF LOC NATION GLOBAL PUBLIC BENEFIT
  CORPORATION" (registrant `LOC COMMUNITY ASSOCIATION`, filer self-titling
  "HH Empress Queen Christina Clement" across amendments) self-reported a flat
  **$20,000,000** on every 2025 quarterly Senate filing (9 filings, 106
  low-content activities, 1 client, 1 lobbyist ever) — confirmed on the House
  side too (same $20M flat figure, 15 filings, starting the same quarter). The
  LDA has no income-plausibility check at filing time; nothing stops a
  registrant from entering an arbitrary number. **This is the only such filer
  found corpus-wide** — checked independently via `posted_by_name` for
  self-titles (Empress/Queen/Prophet/Divine/HH), zero other matches in Senate
  or House. The other 15 rows in this table are small real firms (real
  clients, plausible flat-retainer contracts, `income_per_activity` in the
  $560–$10,000 range) — **flagged, not confirmed cranks**; a genuine finding
  requires the same manual read (activity-description coherence, filer
  self-titling, dollar-figure repetition pattern) that caught LOC, not just
  the numeric threshold alone.
- **Consumers:** none yet (built ad hoc from the FAM-income investigation);
  candidate screen for future sweeps — "registrant income implausible for
  scale."
- **Caveats:** Senate-only (House lacks the same `registrant_id`/lobbyist
  linkage needed for the scale computation, though the LOC filer was verified
  there manually). A registrant below the ≥$100k / ≥3-repeats / ≤2-client
  thresholds could still be a crank at smaller scale — this table is a
  high-precision, not high-recall, detector.

## `derived_registrant_income_deflation`

Mirror-image companion to `derived_registrant_income_integrity` above: flags
Senate registrants whose self-reported income is implausibly **low** for
their scale, rather than high. Built 2026-07-06; **result is a negative
finding, not a lead** — see the trap this build taught in
`docs/beat_book.md`, the beat book.

- **Grain:** one row per `registrant_id`. 4 rows.
- **Builder / stage:** `scripts/build_derived_registrant_income_deflation.py`
  (stage `registrant_income_deflation`); validation baked into the same
  script's `--validate` flag (matches the crank-check's convention).
- **Signal:** registrants with ≥5 lobbyists ever, income-per-activity <
  $3,000 (corpus norm ~$26,940/activity). **Critical metric detail**: the
  denominator (`act_on_income_filings`) counts activities only on the
  filings that contributed to the income sum — not all activities the
  registrant ever logged. Dividing by all activities (the first build's
  mistake) mechanically deflates the ratio for any registrant with mostly
  blank-income quarters, which is ~65% of this corpus's filings corpus-wide
  — that is a sparse-reporting artifact, not evidence of under-reporting.
- **Verdict (hand-checked all 4 rows, 2026-07-06):** no deflation story here.
  3 of 4 are self-lobbying nonprofits/trade associations (Food & Water
  Watch, SUNY Buffalo, American Apparel & Footwear Association — client ==
  registrant, so "client income" isn't the right frame). The 4th, Capitol
  Advocacy Partners, is a legitimate small-municipality government-relations
  shop with real flat retainers ($5k–$20k/quarter) spread across 18 small
  clients (cities, school districts, charter-school nonprofits) and a
  10-lobbyist team — low income-per-activity because the client base is
  genuinely small-dollar, not because income is concealed.
- **Consumers:** none — built to close out the deflation-screen line of
  inquiry from the crank-check follow-up; kept as a documented negative
  result so the signature isn't re-swept.
- **Caveats:** Senate-only (same linkage limitation as the crank-check).
  High-precision by construction (tight threshold, hand-verified), but the
  verdict is "screen doesn't find deflation," not "these 4 are clean" in an
  absolute sense — a different deflation signature (structuring across
  registrants, chamber-shopping; signatures #4/#5 from the original screen
  proposal) was not tested here and remains open.

## `derived_client_alias_index`

First stage of the entity-tracing pipeline (`data_manual.md`'s "entity
graph" lead, `PressNER → registrants/clients → members` — built as
alias-match-outward instead of NER-inward, see beat book for why). Alias
strings for the Senate clients with ≥$1M total 2022–2026Q1 income, collapsed
by normalized name.

- **Grain:** many rows per entity (one per alias). `entity_id` groups an
  entity's rows. **2,263 entities, 5,313 rows** (3,010 `raw` + 1,156
  `suffix_strip` + 345 `fka_split` + 802 net-new `llm_suggested`). 3,757 rows
  `candidate`, 1,556 rows `rejected_too_generic` (884 entities have *all*
  their aliases rejected). Counts current as of the 2026-07-07 rebuild.
- **Builder:** `scripts/build_derived_client_alias_index.py`, three
  deterministic stages, then two apply steps:
  1. **suffix-strip** (fixed list) + `"X (FKA/DBA Y)"` splitting;
  2. **cluster on the fully suffix-stripped core key** (so `"X CORPORATION"`
     and `"X"` land together — the Norfolk Southern split fix, 2026-07-06);
  3. **stage-2 cluster merge** (2026-07-07): collapses variants the core key
     leaves split — punctuation/apostrophe spelling (`"AMERICA'S"` vs
     `"AMERICAS"`, `"BRISTOL MYERS"` vs `"BRISTOL-MYERS"`), acronym
     parentheticals (`"… (AHIP)"`), `"(AND SUBSIDIARIES)"`, and
     non-parenthetical formerly/dba markers (`"CVS PREVIOUSLY AETNA"`,
     `"… INC DBA AMERICAS CREDIT UNIONS"`). Merges on a
     punctuation/apostrophe-normalized token set: **equal-token** clusters
     merge unconditionally (they differed only in punctuation/paren/marker,
     else the core key would already have unified them); a **strict token
     subset** merges only when it is a *marker-shortened* variant (a paren /
     subsidiary / formerly marker actually dropped tokens). Deliberately
     conservative — only *noise* parentheticals are stripped (acronyms +
     subsidiary/FKA markers); an identity-bearing one like
     `"(ON BEHALF OF GENENTECH INC)"` is **kept**, so consultant filings for
     different clients (Tiber Creek OBO Genentech vs OBO Novartis) do **not**
     collapse, and no subset merge crosses an `"on behalf of"` (OBO)
     coalition/consultant filing. Every merge is logged to stdout
     (absorbed → target, with names). The build **asserts** its acceptance
     tests: CVS HEALTH INC + CVS HEALTH (AND SUBSIDIARIES) + CVS PREVIOUSLY
     AETNA → one entity; the two America's/Americas Credit Unions variants →
     one entity; and the count only drops modestly (**2,297 → 2,263**, 34
     merges) with a hard **≥1,800 floor** that STOPs the build if the key is
     ever loosened into over-merging.
  Then `scripts/apply_client_alias_llm_review.py <review_file>` (agent review,
  matched by `canonical_name` with a raw-alias fallback so the merge's
  canonical re-selection doesn't drop rows — 0 review rows failed to match
  post-merge) and `investigations/derived/client_alias_review/manual_alias_rejects_2026-07-06.sql`
  (9 alias-level bare-token rejects: VISA, Miller, Goldman, Schneider, …).
  Neither apply step is part of the idempotent rebuild — re-running the
  builder wipes back to deterministic candidates; re-apply both by hand, in
  that order (the rebuild chain is documented in `REPRODUCING.md`).
- **Review methodology:** batched **Agent tool** launches (general-purpose
  subagents inheriting the Claude Code session, not raw API calls — no extra
  billing), each given ~90 canonical names, returning (a) confident
  additional aliases a suffix-strip can't produce (abbreviations, legacy
  brand names — "IBM," "Conrail" for Consolidated Rail, "Anthem" for
  Elevance Health) and (b) a genericness flag where the name/alias risks
  heavy FTS false-positive collision. Consolidated review file:
  `investigations/derived/client_alias_review/consolidated_review_2026-07-06.txt`.
- **`status` column is the gate**: `candidate` = safe to FTS-match;
  `rejected_too_generic` = flagged by review or a manual reject. Consumers
  must filter `status='candidate'` (or `status <> 'rejected_too_generic'`).
- **Collision-risk companion:** `derived_alias_collision_flags` (below) scores
  every alias for surname / short-word / press-disproportion collision risk —
  informational, does **not** change `status`. Screens that want a
  precision-first slate can additionally exclude `risk_tier='high'` aliases.
- **Consumers:** `derived_client_press_mentions`, `derived_alias_collision_flags`,
  `client-mention-honoree-triangle` screen.
- **Coverage bound (stated, not fixed):** this is a **mention-driven**
  pipeline — a downstream mention/triangle screen only ever surfaces an entity
  that a member actually *name-checks* in a press release (and, for the
  triangle, that is an in-house registrant matchable to LD-203 money). An
  entity with real money but no member press-mention is invisible: e.g. the
  American Bankers Association gave Rep. Andy Barr more than America's Credit
  Unions did, yet does not appear in the triangle because it was not
  press-name-checked at the ≥2-mention threshold (tribunal, 2026-07-07).
  Absence from a mention-based screen is **not** evidence of absence of ties.
- **Caveats:** Senate-only (same `client_id` scale-computation limitation as
  the income-integrity tables). The confirmed crank filer STATE OF LOC
  NATION GLOBAL PUBLIC BENEFIT CORPORATION (fabricated $180M,
  `derived_registrant_income_integrity`) is present but independently flagged
  `rejected_too_generic` — exclude it from any income-based ranking regardless
  of status; the real reason is the fabrication, not the name.

## `derived_client_press_mentions`

Second/final stage of the entity-tracing pipeline: every FTS5 phrase-match
hit between `derived_client_alias_index`'s candidate aliases and `press_fts`.

- **Grain:** `(entity_id, release_id)`, deduped — an entity with multiple
  aliases hitting the same release counts once. **25,998 rows, 989 of 1,379
  candidate entities** have ≥1 mention (2022–2026 Q1; current as of the
  2026-07-07 rebuild). The stage-2 alias merge (above) de-fragments an
  entity's mentions onto one `entity_id` **and** de-duplicates across former
  fragments that shared an alias: e.g. the three former CVS entities each
  matched the shared `"CVS"` alias, so their merged total (94) equals the
  *union* of their releases, **not** the arithmetic sum of the three
  per-fragment counts (which triple-counts the shared `"CVS"` hits). Total
  moved 26,412 → 25,998 (−1.6%) across the rebuild — the net drop is exactly
  this cross-fragment de-duplication from the 34 merges.
- **Builder:** `scripts/build_derived_client_press_mentions.py` (rebuild it
  **after** the alias index + review + manual rejects + collision flags).
- **Columns:** `canonical_name`, `matched_alias` (which alias fired),
  `bioguide_id`, `member_name`, `chamber`, `date`, `url`, `title`.
- **Consumers:** `client-press-mention-gap` and `client-mention-honoree-triangle`
  screens (say-vs-pay at the individual-company level, complementing
  `critic-takes-money` and `quiet-issue-quadrant`'s industry/issue-code level).
- **Caveats:** mention volume is an **upper bound on salience, not a clean
  lobbying-specific signal** — entities newsy for unrelated reasons
  (universities, sports leagues, large consumer brands) will show high
  counts regardless of their lobbying footprint; a member could also discuss
  a company's issue without naming it (e.g. "Big Tech"), which this can't
  see. First look (2026-07-06, not yet hand-verified): quiet-money
  candidates at ≥$1M income include Samsung Semiconductor ($3.0M/0
  mentions), Korea Zinc ($4.5M/3), Tencent America ($3.9M/8).

## `derived_alias_collision_flags`

Per-alias collision-risk scoring for `derived_client_alias_index` — the
deterministic hardening that generalizes the ad-hoc manual bare-token rejects
(VISA / Miller / Goldman / Schneider) into a re-runnable, auditable flag set.
**Informational only: it never writes `status`.** Flags inform; humans/sessions
decide; the existing manual rejects stay as-is.

- **Grain:** one row per alias-index row, keyed `alias_id` → `derived_client_alias_index.id`.
  5,313 rows (2026-07-07).
- **Builder:** `scripts/build_derived_alias_collision_flags.py` (deterministic,
  drops/recreates its own table; run after the index + review + rejects, before
  or independent of the mentions rebuild).
- **Flags (per alias):**
  - `is_member_surname` — single-token alias equal (case-insensitive) to any
    `members.last`; `is_current_member_surname` narrows to *sitting* members
    (the ones who actually appear in the 2022–2026 press corpus — the real
    collision, e.g. Miller/Goldman/Schneider).
  - `is_short_common` — single token AND (`len ≤ 5` OR in an English wordlist:
    `/usr/share/dict/words` if present, else a small builtin offender list).
  - `press_rate_outlier` — the alias's `press_fts` phrase-hit count exceeds
    **20×** the entity's total Senate lobbying-activity count (a disproportion
    heuristic: a company alias hitting press far more than the company lobbies
    is probably a common word). `entity_activity_count` and `press_hits` are
    stored so the ratio is auditable.
  - `risk_tier` ∈ {high, medium, low}: **high** = sitting-member surname, or a
    member-surname/short-common alias that is *also* a press outlier;
    **medium** = any single flag; **low** = none.
- **Distribution:** 13 high / 551 medium / 4,749 low across all rows. Among
  **currently-active** aliases (`status <> 'rejected_too_generic'`): 0 high,
  456 medium — the high-risk ones are already the manual rejects, a sign the
  ad-hoc rejects covered the worst offenders. The medium-active set is the
  methods exhibit "Congress is full of people named after companies": single-
  token company aliases that collide with (mostly historical) member surnames
  — Sands, Dow, Lilly, Corning, Disney, Koch, Baxter, Wynn, Coke, Kellogg….
- **Consumers:** morning-brief risk report; any screen wanting a precision-first
  alias slate can exclude `risk_tier='high'` (or down-weight `medium`).

## `derived_issue_quarter_volume_press`

Per-issue-code per-quarter lobbying volume (Senate + House, kept **separate**,
not summed into one pre-deduped figure) and congressional press-release
volume, 2022–2026 Q1.

- **Grain:** `(issue_code, year, quarter)`. 75 of 79 codes have press keyword
  coverage (MIA/SCI/GOV/CON excluded — too generic to disambiguate by keyword
  match; see the script's header comment for why).
- **Builder / stage:** `scripts/build_derived_issue_quarter_volume_press.py`
  (stage `issue_quarter_volume_press`); validate
  `scripts/validate_issue_quarter_volume_press.py`.
- **Columns:** `senate_activities`, `house_activities`, `total_activities`,
  `senate_income_apportioned`, `house_income_apportioned`,
  `total_income_apportioned`, `n_press_releases`, `lobby_per_press`.
- **Income apportionment:** filing income divided evenly across all issue
  codes active on that filing (avoids the 2.17x overcount from summing raw
  income across codes on multi-issue filings).
- **Senate + House deliberately kept separate, not deduplicated into one
  count:** ~97% of dual-chamber engagements file the *same* issue-code set in
  both chambers (verified 2026-07-02, 286/300 sampled `presence='both'`
  engagements had identical Senate/House issue-code sets) — summing
  `senate_activities + house_activities` would roughly double-count real
  lobbying volume for the vast majority of engagements. A screen that wants a
  single deduped volume figure should count `derived_cross_chamber_engagements`
  rows instead of summing this table's two chamber columns; a screen that
  wants "total disclosed activity regardless of duplication across the two
  legally-separate filing regimes" can sum them. **Don't silently do either
  without naming the choice.**
- **Consumers:** `quiet-issue-quadrant`, `issue-quarterly-surge`,
  `issue-lobby-press-lead-lag`, `derived_committee_quarter_press` (via
  `committee_issue_jurisdiction` join, see below).
- **Caveats:** press volume uses `ISSUE_KEYWORDS` (recall-oriented LIKE
  matching, not exact classification) — see the script for the excluded
  codes and known false-positive risks per keyword set.

## `derived_press_issue_labels`

Press-release-to-issue-code labels from the ML classifier (`M0`,
`scripts/press_topic_classifier.py` — multinomial logistic regression
trained on ~1.5M Senate/House LDA activity descriptions), scored against
every press release. An independent, non-keyword alternative to
`ISSUE_KEYWORDS`; the two methods coexist and neither is authoritative —
see `docs/press-issue-classifier.md`.

- **Grain:** `(release_id, issue_code)`, one row per release-code pair with
  `predict_proba >= 0.3` (global threshold, validated by sweep — see plan
  doc). 100,541 rows.
- **Builder:** `scripts/build_derived_press_issue_labels.py` (not yet
  registered as a `build_gain_db.py` stage — run manually). Validate:
  `scripts/validate_press_issue_labels.py`.
- **Columns:** `probability` (predict_proba, comparable across codes),
  `is_primary` (argmax code per release), `low_confidence` (code has <1,000
  LDA training examples — see `PressTopicClassifier.LOW_TRAIN_VOLUME`).
- **Excluded codes:** GOV, MIA, SCI, CON — same exclusion list as
  `ISSUE_KEYWORDS`, too generic to disambiguate under either method.
- **Consumers:** `derived_issue_quarter_volume_press_ml`.
- **Caveats — empirically confirmed, not theoretical:** low recall
  relative to keyword matching. On INS specifically (see
  `investigations/insurance-jurisdiction-no-press-lift/evidence.md` E6),
  `M0` recalls only 16.2% of the narrow `ISSUE_KEYWORDS['INS']` match set
  and 25.6% of unambiguous NFIP/flood/property/casualty content, while
  independently introducing an ACA/health-insurance false-positive mode
  (LDA filing language and press-release narrative prose are different
  registers — see the plan doc's "domain-mismatch" section). Spot-checked
  as high-precision where it does match (0.3 threshold validated by hand
  on INS/TAX/ENV/VET/CPT/PHA), but this is a **precision-oriented,
  recall-weak** instrument, not a strictly-better replacement for keyword
  matching. **Hard rule: no count from this table may be cited as a
  standalone quantitative finding without a human read-through of the
  underlying flagged releases** (same rule as the keyword-based tables,
  restated because it's easy to assume "trained model" implies more
  authority than "keyword regex," which is not true here).

## `derived_issue_quarter_volume_press_ml`

ML-classifier sibling of `derived_issue_quarter_volume_press` — identical
grain, shape, and activities/income computation; press volume sourced from
`derived_press_issue_labels` instead of an `ISSUE_KEYWORDS` LIKE sweep. The
`_ml` suffix means METHOD, not VERSION — not a migration path, not expected
to ever replace the unsuffixed table (see plan doc's coexistence
architecture). A release counts once per issue code it was labeled with
(multi-label; same multi-count semantics as the keyword version).

- **Grain:** `(issue_code, year, quarter)`. All 79 codes minus the same 4
  excluded (GOV/MIA/SCI/CON).
- **Builder:** `scripts/build_derived_issue_quarter_volume_press_ml.py`
  (not yet a `build_gain_db.py` stage — run manually, after
  `derived_press_issue_labels` exists).
- **Columns:** identical to `derived_issue_quarter_volume_press`.
- **Consumers:** `quiet-issue-quadrant-ml` screen.
- **Caveats:** inherits every caveat from `derived_press_issue_labels`
  above. Spearman rank correlation between this table's `lobby_per_press`
  ratio and the keyword-based table's, per issue code (2023–2024,
  ≥20 press releases, 65 codes compared): **0.44** — real shared signal,
  but substantial reordering, consistent with the two methods having
  different (not simply "one is noisier") failure modes. Ratios in this
  table run systematically higher than the keyword version (M0 is
  recall-weak nearly everywhere, not just on INS) — read this table's
  rankings as "quiet by M0's more conservative standard," not as a
  directly comparable absolute scale to the keyword table.

## `derived_committee_quarter_press`

Committee-level companion to `derived_issue_quarter_volume_press` — per
committee, per issue code the committee has jurisdiction over, per quarter:
how many press releases did *that committee's own members* (using the
roster **actually seated at the time**, not today's roster) put out on that
topic. Built 2026-07-02 to give a lobbying-vs-press lead-lag comparison a
real institutional anchor, after the flat 79-issue-code version
(`issue-lobby-press-lead-lag` screen) turned out to be mostly noise at
n=17 quarters × 79 codes with no jurisdiction anchor.

- **Grain:** `(committee_id, issue_code, year, quarter)`. 2,057 rows (121
  committee-issue jurisdiction pairs with keyword coverage × ~17 quarters).
- **Builder / stage:** `scripts/build_derived_committee_quarter_press.py`
  (stage `committee_quarter_press`); validate
  `scripts/validate_committee_quarter_press.py`.
- **Roster resolution:** uses `member_committees_history` (not
  `member_committees`) — the roster valid as of each quarter's start date,
  clamped to the earliest available snapshot (2022-01-04) for the first
  quarter of the corpus. This is the whole point of the table: a naive join
  against the current roster would misattribute years of press releases to
  members who weren't on the committee at the time.
- **Columns:** `n_committee_members` (roster size that quarter),
  `n_total_releases` (all releases from those members, any topic),
  `n_topic_releases` (topic-matched via the same `ISSUE_KEYWORDS` map as
  `derived_issue_quarter_volume_press` — imported, not copied, so the two
  stay in sync by construction), `topic_share`, **`organizing_gap`**.
- **`organizing_gap` (read this before using the table):** 1 when no roster
  existed for a committee_id that quarter. Two legitimate causes: the whole
  chamber hadn't organized committees yet at the start of a new Congress
  (2023 Q1, 2025 Q1 — every committee gaps here), or a specific subcommittee
  didn't exist yet (e.g. `SSBK13` Digital Assets, created 2025). **Filter
  `organizing_gap=0` before any volume/lag comparison** — these are real
  institutional facts, not zero-activity data points, and would corrupt a
  correlation if treated as legitimate zeros.
- **Verified at build:** Jason Smith / Ways & Means (`HSWM`) resolves 42-45
  members across the window (growing over time, a real fact); TAX-topic
  press share for that committee runs ~45–60% of their total output,
  2022–2026.
- **Consumers:** none yet — built as groundwork for a committee-level
  lobbying-volume-vs-press lead-lag screen (not yet designed/run). Join to
  `derived_issue_quarter_volume_press` via `committee_issue_jurisdiction`
  (`committee_id` → `issue_code`) to compare this table's press volume
  against that table's Senate/House lobbying-activity volume for the same
  `(issue_code, year, quarter)`.
- **Caveats:** press topic-matching inherits `ISSUE_KEYWORDS`' recall-oriented
  LIKE-match limitations (see `derived_issue_quarter_volume_press` above). A
  release from a committee member is topic-matched independent of whether it
  actually concerns that member's committee work (e.g. a Ways & Means member's
  press release about veterans' issues won't count toward TAX, correctly, but
  also won't be excluded from the *denominator* `n_total_releases` just
  because it's off-topic for the committee — that's intentional, `topic_share`
  is meant to show what fraction of a committee's messaging touches its own
  jurisdiction).

## `derived_member_contribution_panel`

LD-203 contributions resolved to members — the say-vs-pay money side (objective;
no issue/industry attribution, which awaits the subjective committee→issue map).

- **Grain:** `(bioguide, filing_year, contribution_type)`. 3,316 rows, 752 members.
- **Builder / stage:** `scripts/build_derived_member_contributions.py`
  (stage `member_contributions`); validate `scripts/validate_member_contributions.py`.
- **Provenance:** contributions resolve via `honoree_member_map` at **confidence
  ≥ 0.9** only (~$851M of $1.71B; FECA portion $830M). Year from
  `senate_contribution_filings.filing_year`.
- **Columns:** `member_name`, `party`, `state`, `total_amount`, `n_items`.
- **contribution_type is kept SEPARATE (correctness fix):** `feca` = political
  contributions ($1.48B corpus-wide; $830M matched); `he`/`me`/`ple`/`pic` =
  honorary/meeting/other. **Never sum across types** as "money to the member" —
  filter to the relevant type (usually `feca`).
- **Consumers:** `chair-power-premium`, `silent-gatekeepers` (money side),
  `critic-takes-money`, `committee-role-contribution-premium` screen.
- **Verified at build (chair-power-premium holds):** full-committee chairs raise
  **1.9× the FECA money of their committee's rank-and-file** ($2.53M vs $1.53M
  avg, 48/49 committees) — closely matching the sweep's $2.75M vs $1.43M; the
  "2–7×" is the *across-committee range*. NB: pooling subcommittee chairs in
  dilutes this to 1.4× — use full committees (`length(committee_id) ≤ 4`).
- **Caveats:** built against `member_committees` (current-Congress only —
  temporal mismatch with 2022–26 contributions); honoree match ≥0.9 (~50% of
  dollars); this is *total* contributions, not industry-attributed. **A fix
  exists but is not yet wired into this panel:** `member_committees_history`
  (added 2026-07-02, see `docs/members_db.md`) has point-in-time committee
  rosters across 2022–2026 from pinned git-history snapshots of the source
  file — a chair-power-premium rebuild using it instead of `member_committees`
  would correctly attribute pre-2025 contributions to the committee a member
  actually sat on at the time, not their current seat. Re-running this
  verification is a good follow-up, not yet done.

## `derived_lobbyist_year_profile` / `derived_lobbyist_issue_year` / `derived_lobbyist_rr_disclosure`

Three related tables (one builder) profiling individual Senate lobbyists —
client/registrant footprint and revolving-door (prior government post)
disclosure. Built for the `lobbyist-revolving-door-profile` screen backlog.

- **Builder / stage:** `scripts/build_derived_lobbyist_revolving_door.py`
  (stage `lobbyist_revolving_door`).
- **`derived_lobbyist_year_profile`** — grain `(lobbyist_id, filing_year)`.
  66,836 rows. `n_registrants`, `n_clients`, `n_issue_codes`, `n_activities`,
  `has_covered_position`. Powers `within-firm-rainmaker` (client-count outlier
  among lobbyists at the same firm).
- **`derived_lobbyist_issue_year`** — grain `(lobbyist_id, issue_code,
  filing_year)`. 376,851 rows. `n_clients`, `n_activities`,
  `has_covered_position`. Powers `issue-specialist-gatekeepers` (client
  concentration by issue) and `revolving-door-surge-by-issue` (yearly
  revolving-door share per issue).
- **`derived_lobbyist_rr_disclosure`** — grain `(lobbyist_id, registrant_id)`,
  one row per lobbyist-registrant pair that disclosed a non-junk covered
  position on the initial registration (RR) filing. 4,070 rows.
  `rr_covered_position`, `n_subsequent_quarterlies`,
  `n_subsequent_with_disclosure`, `redisclosed_ever`. Powers
  `rr-only-disclosers`.
- **Dedup:** year-profile and issue-year tables are built on the same
  canonical-filing dedup as the income/issue panels (one row per
  `(registrant, client, year, quarter)`, latest-posted). The RR-disclosure
  table compares one RR filing per pair (earliest-posted) against all later
  filings of any type for that pair.
- **Junk filter (applied everywhere):** `covered_position` values `'N/A'`,
  `'See prior filing'`, `'Legislative Consultant'`, `'Self'`, `'None'`, `''`,
  and `'Partner'` (a firm title, not a government post) are excluded before
  computing `has_covered_position`. Keep in sync with the
  beat book's revolving-door recipe
  (`docs/beat_book_recipes.md`).
- **Verified at build — corrects a stale scout baseline:** the
  `rr-only-disclosers` screen's baseline (written before this table existed)
  claimed "sector RR disclosure rate is 62.1% vs 25-27% on quarterlies,"
  implying disclosure decay after registration. The actual, verified rate at
  the lobbyist×registrant grain is **81.8% redisclosed** (3,328 / 4,070 pairs)
  — persistence, not decay, and in the opposite direction from the old claim.
  **Do not use the 62.1%/25-27% figures; they do not reconcile with this
  table and their original grain/derivation is unknown.**
- **Caveats:** Senate-only (House `covered_position` is name-only, no stable
  lobbyist id — not included). "Redisclosed" means the position text appears
  again on *any* later filing type for the pair, not necessarily every
  quarterly (LDA guidance requires it on each quarterly; a lobbyist who
  redisclosed on 1 of 4 quarterlies still counts as `redisclosed_ever=1`) —
  a stricter "redisclosed on every subsequent quarterly" cut is a follow-up,
  not yet built.

## derived_convicted_lobbyist_register

Built by `scripts/build_derived_convicted_lobbyist_register.py` (2026-07-06).
One row per Senate lobbyist with ≥1 row in
`senate_filing_conviction_disclosures`: conviction date/description as filed
(earliest row), `n_filings_disclosed`, and the post-conviction record over
**original quarterlies only** (`filing_type IN ('Q1','Q2','Q3','Q4')`, quarter
start strictly after conviction date): `n_post_quarterlies`,
`n_post_disclosed`, `n_post_missing`, plus up to 5 example `missing_uuids`
for citation. Senate-only by design — `house_convictions` is name-keyed;
House corroboration stays case-side. 18 rows. Consumer:
`conviction-quarterly-gaps` screen. Caveat: `conviction_date` is
self-reported on the disclosure; NULL dates get NULL post-conviction columns.
