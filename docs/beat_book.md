# The GAIN corpus beat book

Project notes on the corpus in `db/gain.db`: the schema map, the verified
cross-source bridges, the data-quality traps, and a library of ready
cross-source SQL recipes.

This is the **beat book** the `sweep-for-screens` and `fish-for-leads` skills
ask you to supply for your own corpus — the doc holding a corpus's schema,
bridges, and data traps. It is corpus-specific project documentation, not a
reusable skill, so it lives in `docs/` rather than `.claude/skills/`. Update it
when a sweep or case teaches a new trap.

A deterministic query layer over federal lobbying + congressional messaging.
Everything resolves to a source record, so leads are defensible.

## Build the database first

`db/gain.db` is a ~3.9 GB build artifact (not committed). If it's missing:

```bash
python scripts/ingest_senate.py      # senate_*  (~80s)
python scripts/ingest_house.py       # house_*   (~3 min)
python scripts/ingest_press.py       # press_*   (~25s)
python scripts/ingest_members.py     # member_*  (~40s; congress-legislators crosswalk)
```

Confirm it's healthy: `python scripts/validate_senate.py --reconcile` (and the
`house`/`press` validators). Full column-level manuals: `docs/*_db.md`.

## The mental model: one corpus, three sources, two bridges

- **`senate_*`** — Senate LDA filings (who lobbies whom, on what, for how much),
  LD-203 contributions (lobbyist/PAC money to members). Clean stable ids.
- **`house_*`** — House LDA filings. Same regime, separate filing, kept separate
  so House-vs-Senate discrepancies stay visible.
- **`press_*`** — member press releases (rhetoric), keyed by `bioguide_id`.

Bridges that make it one corpus (both verified):
1. **Senate ↔ House:** `house_filings.senate_registrant_id = senate_registrants.id`
   (100% of House filings; 6,630 registrants in both chambers).
2. **Press ↔ money (say vs. pay), via the crosswalk:**
   `press_releases.bioguide_id = members.bioguide`, and contribution
   `honoree_name → honoree_member_map.bioguide → members`. `member_committees`
   adds committee context. Honoree matches carry `method`/`confidence` — filter
   `confidence >= 0.9` for high-trust analysis, treat `0.6` (last-name-only) as a
   lead to confirm. ~45% of distinct honorees are non-members (PACs/committees)
   and stay unmatched by design.

Full table/column map: [beat_book_schema.md](beat_book_schema.md).

## Use the recipes

A library of ready, correct cross-source queries is in
[beat_book_recipes.md](beat_book_recipes.md): topic footprint across all three
corpora, a firm's both-chamber footprint, revolving door, contributions by
honoree, foreign influence, convictions, a member's press over time, and the
say-vs-pay scaffold. Start from a recipe and specialize it.

## Verify every claim before reporting it

- Senate lobbying rows → `filing_uuid` →
  `https://lda.gov/filings/public/filing/{filing_uuid}/print/`
- Senate contribution (LD-203) rows → `filing_uuid` →
  `https://lda.gov/filings/public/contribution/{filing_uuid}/print/`
  (different path segment and UUID namespace from lobbying filings; both
  need the trailing `/print/` or the URL 404s)
- House rows → `house_filing_id` + `source_file`
- Press rows → `url`
- Money: aggregate the parsed `*_amt` column, **quote the raw string** as filed.

## Watch the data-quality traps (filter these when aggregating)

- `covered_position` and `honoree_name` contain junk: `"N/A"`, `"See prior
  filing"`, `"Legislative Consultant"`. `honoree_name` mixes party PACs
  (NRSC/DSCC/NRCC) with individual members and has no standard name format.
  (`"See prior filing"` is 96% one firm — BGR — so it skews any firm-level
  covered-position stat.)
- House lobbyists are name-only (no stable id); House `federal_agencies` is free
  text, not a controlled vocabulary.
- Sparse money: only ~65% of Senate filings carry a parseable income/expense.
- A registrant filing in both chambers means the *same* engagement appears in
  `senate_*` and `house_*` — don't double-count; use one side or compare them.

Additional traps from the 2026-06-11 grid sweep (scout-verified at probe
level; re-derive before publication — full report:
`investigations/sweeps/2026-06-11-grid-sweep.md`):

- **Press coverage gaps — the critical one.** Per-member press-release counts
  reflect *scraper coverage*, not only behavior: some prominent members have
  near-empty corpora (Guthrie 16 releases, Jason Smith 10, Jim Jordan 0).
  **Never make a silence/absence claim without checking the member's coverage
  first** (releases per year vs. chamber norms); restrict absence claims to
  full-coverage members.
- **Duplicate Senate quarterlies**: ~970 cases of the same report filed twice
  under different `filing_uuid`s (~$35M) — invisible within Senate data alone;
  detectable via the House bridge or content comparison. Dedupe before income
  aggregation; many pairs are same-minute clerical re-files (`dt_posted`,
  `posted_by_name`).
- **Contribution types are not interchangeable**: separate LD-203 item types
  (`ref_contribution_item_types` — FECA vs honorary vs meeting expenses etc.)
  before aggregating per-member "money"; mixing types misstates totals. Honoree→
  member matches at `confidence >= 0.9` cover ~50% of dollars ($851M of $1.71B).
- **`member_committees` mixes full committees and subcommittees**: 181 of 230
  rows are subcommittees (longer `committee_id`; full committees have
  `length(committee_id) <= 4`). For chair/role analysis, filter to full
  committees — pooling subcommittee chairs dilutes the chair-power-premium from
  ~1.9× to ~1.4×. `title` ∈ {Chairman, Chair, Chairwoman} for chairs;
  Ranking Member / Vice Chair / Ex Officio are distinct roles.
  **`member_committees` itself is current-Congress only** (temporal mismatch
  with 2022–26 data) — **use `member_committees_history` instead** (added
  2026-07-02) for any analysis spanning multiple Congresses: point-in-time
  rosters from 18 pinned git-history snapshots of the source file
  (2022-01 .. 2026-03, ~2-3 month spacing, both Congress transitions
  captured), with `valid_from`/`valid_to` windows. `member_committees` is
  still fine for "who sits where right now" questions.
- **`ISSUE_KEYWORDS` (`scripts/build_derived_issue_quarter_volume_press.py`)
  has uneven recall across codes — check before trusting a "silent on topic
  X" claim.** `INS` (Insurance, 4 keywords, all narrow compound phrases —
  "insurance industry/regulation/premium," "insurer") recalls only **23%**
  of press releases containing the bare word "insurance," vs. `BAN` (Banking,
  9 broader keywords) and `RET` (Retirement, 4 keywords incl. "pension,"
  "401(k)") each recalling **>170%** of their own bare anchor word (their
  keyword sets deliberately widen beyond the single word). Diagnostic method:
  compare `count(LIKE '%<bare word>%')` to the keyword-matched count — a
  ratio far below other codes' ratios signals undercounting, not real
  silence. **Caught 2026-07-02** chasing a committee-press-silence lead
  (House Financial Services–Housing/Insurance subcommittee, Senate
  Banking–Securities/Insurance/Investment subcommittee both showed ~35x more
  press on their non-insurance jurisdiction) — the finding **survived**
  re-checking with a broader, industry-disambiguated keyword set (1.6%/2.7%
  vs. a 1.7% corpus baseline for insurance topic-share, essentially zero
  jurisdiction lift, vs. real lift on the same committees' other topics —
  logged as lead `insurance-jurisdiction-no-press-lift`). The shared
  `ISSUE_KEYWORDS['INS']` itself is **still not fixed** (would require
  rebuilding `derived_issue_quarter_volume_press` +
  `derived_committee_quarter_press` and re-verifying `quiet-issue-quadrant`'s
  existing INS ranking, which also rests on the narrow keyword set). A
  partial recall audit (`scripts/audit_issue_keyword_recall.py`, 26 of 75
  codes with a clean single-word bare anchor) confirms **INS is an isolated
  outlier, not a systemic problem**: every other audited code scores
  0.23 (INS) vs. 1.29–13.74 for the rest (HCR/FIR/VET/BAN/RET/ENG/AVI/EDU/
  MMM/FIN/DEF/AGR/HOM/TAX/TRA/BUD/LBR/PHA/TEC/ENV/ALC/HOU/AUT/TRD/IMM all
  clear 1.0). Most `ISSUE_KEYWORDS`-based findings in this corpus are
  probably fine; INS specifically is not, and the shared table still has
  not been fixed.
- **`GOV` is a catch-all sink**: ~$119M of Senate income sits on
  exclusively-GOV-coded filings, and ~31% of GOV rows describe specific topics.
  Issue-code analyses must handle GOV explicitly or they undercount the real
  issue.
- **LDA `income_amt`/`expenses_amt` are self-reported with zero plausibility
  checking at filing time — a single crank filer can distort an issue code's
  entire aggregate.** Confirmed 2026-07-04: "STATE OF LOC NATION GLOBAL PUBLIC
  BENEFIT CORPORATION" (registrant `LOC COMMUNITY ASSOCIATION`, 1 client, 1
  lobbyist, ~106 low-content activities, filer self-titling "HH Empress Queen
  Christina Clement" across amendments) reported a flat **$20,000,000** on
  every 2025 quarterly filing, Senate and House both — alone accounting for
  ~two-thirds of the Family/Abortion (FAM) issue code's apparent 2025 income
  total. Caught while re-deriving a scout number before publication (never
  trust the raw derived-table aggregate without a scale sanity-check on its
  top contributors). A systematic screen (`derived_registrant_income_integrity`
  / `registrant-income-crank-check`: flat income repeated on ≥3 filings, ≤2
  clients, ≤2 lobbyists ever, ≥$100k) found this is the **only** such case
  corpus-wide (cross-checked independently via unusual filer self-titling in
  `posted_by_name` — zero other matches) — high-precision, not high-recall;
  a different fabrication style (varying the number slightly, adding a second
  lobbyist) would not be caught by this exact signature. **Any income-based
  aggregate — not just FAM — should sanity-check its top contributors'
  income-per-activity against registrant scale before publication.**
- **The mirror-image "deflation" screen (income anomalously LOW for scale)
  found no story — but taught a real metric-design trap.** Built 2026-07-06
  as the deflation-side companion to the crank-check above
  (`derived_registrant_income_deflation`: Senate registrants with ≥5
  lobbyists ever whose income-per-activity sits far below the corpus norm,
  ~$26,940). **First build divided total reported income by *all* activities
  across every filing the registrant ever made** — but ~65% of this corpus's
  filings carry no parseable income (known caveat above), so any registrant
  with mostly-blank-income quarters and a few real ones gets a mechanically
  deflated ratio regardless of actual under-reporting. That version flagged
  Kellen Company, Drummond Woodsum, and Delta Development Group — all small
  government-relations shops billing counties/townships/small nonprofits,
  not deflators. **Fix: divide by activities counted only on the filings that
  contributed to the income sum** (coverage-matched numerator/denominator).
  After the fix, those three dropped out entirely; the 4 that survived were
  hand-checked and are all benign — 3 self-lobbying nonprofits/associations
  (client == registrant; "client income" isn't the right frame for in-house
  lobbying) and 1 legitimate small-municipality retainer shop (Capitol
  Advocacy Partners: real $5k–$20k flat contracts with 18 small clients,
  spread across a 10-lobbyist team). **Verdict: no deflation finding in this
  corpus via this signature** — low income-per-activity here tracks who the
  clients are (small towns/nonprofits/self-lobbying orgs paying small real
  retainers), not concealment. Any future income-per-activity metric in this
  corpus must use the coverage-matched denominator, and must screen out
  self-lobbying (`registrant_id`'s client set consisting only of itself)
  before treating a low ratio as a signal.
- **Entity-tracing into press text: alias-match outward, don't NER inward.**
  `data_manual.md`'s "entity graph" lead (Press-release NER → companies/orgs
  → LDA registrants/clients → government entities → committees → members)
  had zero infrastructure as of 2026-07-06. Full NER over 141k press releases
  would need to entity-resolve its output against a fragmented client
  namespace (Comcast alone spans 52 `client_id`s in `senate_clients` —
  same-chamber name fragmentation, a much harder problem than the *already
  solved* cross-chamber bridges below). Built the cheaper direction instead:
  start from clean canonical client names (top ~525 Senate clients by total
  income, ≥$1M 2022–2026Q1) and FTS5-match generated alias strings *outward*
  against `press_fts`, rather than extracting entities *inward* from free
  text. Pipeline: `derived_client_alias_index` (deterministic suffix-strip +
  FKA/DBA-split, then a genericness/abbreviation review pass) →
  `derived_client_press_mentions` (FTS phrase-match hits) →
  `client-press-mention-gap` screen (say-vs-pay at the individual-company
  level, not just industry/issue-code level like `critic-takes-money` /
  `quiet-issue-quadrant`). The review pass was run as **6 batched Agent tool
  launches** (general-purpose subagents, no raw API billing), each reviewing
  ~90 canonical names and returning confident additional aliases (brand
  names/abbreviations a suffix-strip can't produce, e.g. "IBM," "Anthem" for
  Elevance Health, "Conrail" for Consolidated Rail) plus a genericness flag.
  159 of 525 entities got flagged too-generic to safely FTS-match at all
  (Apple, Target, Oracle, Delta Air Lines, ARM Holdings, Micron alone,
  U.S. Chamber of Commerce, City of Atlanta — common-word or heavily-collided
  names) and their alias rows were marked `rejected_too_generic`, not deleted
  (kept for audit). Do not skip this review step if rebuilding: the
  deterministic pass alone would let those collision-prone names into the
  match set and silently inflate false-positive mention counts. Read
  `derived_client_press_mentions` counts as an upper bound on salience, not a
  clean lobbying-specific signal — entities newsy for unrelated reasons
  (universities, sports leagues) will show high counts regardless of their
  lobbying footprint.
- **Cross-chamber client join — ADJUDICATED 2026-06-13**: match on
  `CAST(house_filings.senate_client_suffix AS INTEGER) = senate_clients.client_id`
  (the *coarser* grouping, **not** `senate_clients.id`). Coverage 99.5% of
  suffix-bearing House filings (94.9% carry a suffix); 91.6% exact name
  agreement, 95.6% first-12-char. The scout dispute was an artifact of testing
  the wrong column — `.id` matches only 31.9%. This id-join beats the
  `UPPER(client_name)` fallback (~92.6%) and correctly unifies FKA/DBA name
  variants a string join misses; keep the name join only for the ~5% of
  suffix-bearing rows with no `client_id` hit.

## This corpus's best findings may already be news — scan before claiming novelty

The outlets that own this beat (OpenSecrets, LegiStorm, Bloomberg Government) run
the **same primary-records analysis we do**, so a strong, true finding here can
still be old news. Worked example: the 2025 **tariff lobbying surge** — they
published the firm-count explosion and Ballard's revenue dominance, matching our
own numbers (case `tariff-2025-stealth-surge`, `coverage: well-covered`). Before
any *discovery* claim, run the **novelty-scan** (`track-investigation` skill,
`reference/prior-art.md`). Two disciplines: (1) reporting may **nominate a beat**
(point the corpus at a live fight, see `sweep-for-screens`
`reference/beat-nomination.md`) but is **never cited as evidence** — direction
in, novelty out; (2) on a covered topic, aim at the layer reporting can't reach
(the influence plumbing — who filed, who paid, who went quiet) → an
`under-reported` angle. A `well-covered` verdict still earns its keep as a
*precision exhibit* (we rediscovered a real story from filings alone).

## Before computing anything from raw tables

Check the derived-table catalog (`docs/derived_db.md`, when present) and the
newsroom ledgers (`investigations/newsroom.db`: proposed/built instruments,
registered screens) — an instrument may already answer your question with its
junk-filters audited once. The newsroom operating loop is the
`sweep-for-screens` (sweep) and `fish-for-leads` (go-fish) skills. This file
is the corpus's **beat book**: when a sweep or case teaches a new trap or
verified join, add it here.

License: MIT (see repo `LICENSE`).
