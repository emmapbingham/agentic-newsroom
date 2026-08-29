# Log — apra-lobbying-coalition

## 2026-07-03
- did: promoted from `leads` (slug=cpi-federal-privacy-bill-quiet-coalition,
  screen_run_id=23 — surfaced from a manual drilldown into the CPI/Computer
  Industry issue code's activity descriptions, following a run of the
  `quiet-issue-quadrant-ml` screen; the ML-screen ranking itself was not the
  direct source of this lead, the drilldown into CPI's raw content was).
- did: before opening this case, ran a preliminary (non-evidentiary) web
  search to sanity-check the lead's "quiet" framing:
  - Query 1: "American Privacy Rights Act 2024 news coverage federal data
    privacy bill" — found real trade/policy press coverage (Washington
    Post called it a "major breakthrough," IAPP, WilmerHale, IBM Think,
    Senate Commerce Committee's own "what others are saying" roundup).
    Also found: the June 27, 2024 markup was canceled amid GOP opposition
    signals, and the bill expired unremarked at the end of the 118th
    Congress in January 2025 — no dramatic floor defeat, it just lapsed.
  - Query 2: "Kids Online Safety Act KOSA news coverage opposition tech
    industry" — found KOSA/KIDS Act is a DIFFERENT bill, currently and
    heavily covered (Axios, NBC, The Hill, Roll Call, all dated within
    days of 2026-07-03), with active House-Senate conflict and on-record
    industry opposition (NetChoice). This is the opposite of quiet and
    must not be conflated with APRA in this case.
  - Decision: dropped the "invisible"/"quiet" framing per editor
    instruction — opened this case agnostic about the eventual angle. See
    case.md's Hypothesis section for the explicit non-commitment.
- did: set up case.md, evidence.md, log.md, queries.sql per templates.
- did: re-derived E1 (lobbying volume, 1,008 activities / 101 clients) and
  E2 (press volume, 19/40) directly against `db/gain.db` — both matched
  the scout numbers from `newsroom.db` exactly. No longer unverified scout
  figures.
- did: ran E3 — read the full, un-keyword-filtered activity text for the 8
  advocacy/nonprofit organizations in CPI's client roster (identified in
  the prior session's name-pattern search: EFF, Fight for the Future,
  Center for Humane Technology, Due Process Institute, Avaaz, David's
  Legacy Foundation, Children and Screens, Sandy Hook Promise Action
  Fund).
- found: see E1-E3 in evidence.md. Headline: none of the 8 advocacy orgs
  mention APRA/ADPPA anywhere in their activity text — each is engaged on
  a different specific bill (KOSA family, RESTRICT Act, antitrust bills,
  generic AI, platform-transparency bills). The APRA-specific coalition in
  this corpus appears to be entirely industry-side so far, though only 8
  orgs were checked and the search that found them (name-pattern matching
  on "foundation"/"institute"/"coalition"/etc.) could have missed others.
- dead ends: none yet — this is the first drilldown session.
- open questions: (1) is the coalition unified or does it split into
  sub-factions with different/opposing positions on specific provisions
  (state preemption, private right of action, data minimization) — not
  yet checked, the client list alone doesn't show position; (2) is
  1,008 activities/101 clients actually unusual in scale, or normal for
  any major unpassed tech bill — no baseline comparison run yet; (3) why
  no organized public-interest voice engaged specifically on APRA — not
  yet investigated, several plausible explanations untested (resource
  constraints, strategic deprioritization vs. KOSA, or genuine lack of
  opposition to the bill's substance).
- NEXT: pull the full 101-client list (not just top-15) and start reading
  individual filings/available public statements for position (support/
  oppose/amend on specific provisions like state-law preemption or private
  right of action) — that's the piece needed before any framing can be
  chosen. Do not pick an angle before this read is done.

## 2026-07-06
- did: a separate session had independently drilled into RELX Inc. via the
  `client-press-mention-gap` screen (newsroom.db screen id 39, unrelated to
  this case originally) — checked RELX's own lobbying-activity descriptions
  and found 28 filings, 2022Q2-2024Q4, naming APRA/ADPPA/American Privacy
  Rights Act/American Data Privacy and Protection Act by name. RELX is
  directly one of this case's 101 coalition clients (E1), so folded that
  session's findings in here as a worked single-entity example rather than
  letting it sit in an unrelated screen's lead record.
- found: RELX Inc. ($6.64M disclosed income, 2022-2026Q1) is never named in
  any congressional press release under any RELX name/brand (Elsevier,
  ThreatMetrix, Reed Exhibitions all checked, zero). A separate small filer
  in the same corporate family, LexisNexis Risk Solutions FL Inc. ($150K,
  not one of the 101 E1 clients — below entity/case threshold), IS named,
  always critically, in 5 press releases (data-broker driver-data sales,
  disaster-benefit fraud, ICE detainee data access) — see E4 for citations.
- found: RELX Inc. also discloses $428,609.16 in LD-203 contributions (163
  items, 2022-03-21 to 2025-12-04) to a bipartisan mix of party committees,
  leadership PACs, and ~90 named individual members. Cross-referencing
  those honorees against `member_committees` shows concentration on
  committees with direct jurisdiction over RELX's own lobbying topics:
  Judiciary's IP and Privacy/Technology/Law subcommittees (both chambers),
  Energy & Commerce's Communications/Technology and Health subcommittees,
  and Finance/Ways & Means including their Health Care subcommittees —
  matching RELX's two disclosed lobbying tracks (Elsevier copyright/AI;
  LexisNexis-adjacent privacy/data-broker/Medicaid-eligibility policy).
- found: checked for overlap between RELX's honorees and the 5 members who
  criticized LexisNexis by name in press — zero overlap at any confidence
  level. Clean negative result: rules out both a "buying off critics" and
  a "avoiding critics" reading; the two groups are simply unconnected here.
- dead ends: none — this raises a question rather than closing one.
- open questions: does RELX's pattern (heavy lobbying on APRA-family bills,
  zero press visibility for the lobbying entity itself, contribution money
  concentrated on committees-of-jurisdiction) hold across the other ~100
  coalition clients, or is RELX unusual within the coalition? Not yet
  known — would need the same registrant+LD-203+committee pull repeated
  for each client, a real scope of work (see evidence.md's new Open item).
- NEXT: still the same priority as 2026-07-03 — full 101-client roster read
  for position/sub-faction structure. RELX (E4) is now a template for what
  a per-client deep-dive looks like (lobbying topic + press visibility +
  contribution/committee pattern) if that becomes the case's method for
  characterizing the coalition once the roster read is done.

## 2026-07-06 (second session)
- did: ran the full roster read and scale baseline, at the editor's
  request. Along the way found that the roster's client count needed
  correcting twice: E1's 101 was a raw `senate_clients.id` count, and the
  first-pass dedup was scoped to `general_issue_code = 'CPI'` only, which
  undercounts because APRA/ADPPA is disclosed under 15+ issue codes
  (Consumer Issues alone has more matching activity than Computer
  Industry). Corrected by matching on any issue code, filtering to
  sub-600-character "focused mention" descriptions to exclude omnibus
  filings that list 50+ unrelated bills in one field, then manually
  deduplicating name variants the same way as a careful roster read (not
  just mechanical regex normalization). Full method and result in
  evidence.md E5 (position read) and E6 (entity count + scale baseline).
- found: **345 distinct entities, 2,545 Senate lobbying activities**
  (2022–2026) — the largest of four compared bills (KOSA ~149/1,292,
  AICOA ~104/902, RESTRICT Act ~24/99). Position-language read (E5): only
  2 entities (SIIA, American Advertising Federation) disclose any real
  ADPPA-specific stance, both pointing the same direction — not a
  coalition split, but too thin to characterize the rest. That read
  predates the 345-entity roster and hasn't been re-run on the ~274
  entities added since.
- did: updated case.md (Hypothesis, scale confirm/kill criterion, Verdict,
  Sources) to cite 345 as the headline entity count. Regenerable scripts:
  `analysis/build_roster.py` (superseded, kept for E5's position-read
  provenance) and `analysis/build_corrected_roster.py` →
  `derived/roster_corrected_deduplicated.csv` (current roster).
- dead ends: none.
- open questions: (1) does the position-language read change once the
  ~274 newly-added entities are read (Zillow, State Farm, Yahoo-ad-side,
  Interpublic, Iron Mountain, Carvana, etc.)?; (2) KOSA/AICOA/RESTRICT's
  entity counts are still mechanical-normalization estimates, not manually
  verified the way APRA's is; (3) House-side roster (87 raw client names)
  still not reconciled against the Senate 345.
- NEXT: re-run the position read on the ~274 new entities. Then decide
  with editor whether to (a) invest in LD-203/committee scope-of-work
  (RELX's E4 method) across the coalition to test if E4's pattern
  generalizes, now against a coalition ~5x bigger than when E4 was first
  drilled into, or (b) pivot toward the press-visibility gap (E2) once it
  has its own baseline.

## 2026-07-08

- did: re-ran E5's position-language read at the editor's request, this
  time against the full corrected 345-entity roster (any issue code,
  `length(description) < 600` — E6/E7's filter) instead of the superseded
  71-entity CPI-only roster. New evidence block: E8 (evidence.md). Script:
  `analysis/build_position_read.py` → `derived/position_read_candidates.csv`.
- found: two things, one substantive, one methodological.
  Substantive — the coalition has real fault lines, not just alignment:
  a private-right-of-action fight (American Association for Justice
  supports it; SIIA/American Transaction Processors Coalition oppose it)
  and a state-preemption fight (California's state senate lobbied to
  strip preemption from HR 8818; the industry coalition wants it). Also:
  **E3's "no organized public-interest voice on APRA" finding is wrong** —
  Electronic Frontier Foundation files substantively on ADPPA/APRA
  (preemption, private right of action, biometric data on minors) but
  under the `CIV` issue code, not `CPI`, so E3's CPI-scoped search missed
  it entirely. Methodological — the `<600` character cutoff, built in E6
  to exclude omnibus 50-bill laundry-list filings, also silently excludes
  verbose single-bill position statements: American Advertising Federation's
  actual ADPPA position statement is 780-1,038 characters in every filing
  year, over the cutoff every time — AAF drops out of this corrected-roster
  method entirely despite being one of E5's two original findings. SIIA
  survived only by luck (one shorter cross-posted row under a different
  issue code).
- did: dropped the length cutoff entirely as a check (`q8b`) — surfaces
  103 raw client names with a position-keyword/bill-name co-occurrence,
  but most are large multi-bill omnibus filings (some 20,000+ characters)
  where the keyword very likely attaches to a different bill in the same
  list. Read through the 600-2,500-char band as a first pass (41 names);
  found one more genuine hit (Insights Association, explicit ADPPA
  support) and confirmed the rest in that band are boilerplate false
  positives. ~64 names in the full 103-name list still unread.
- did: updated case.md (Verdict, Hypothesis's confirm/kill criteria,
  Sources/legal-risk notes — now lists 11 entities with genuine position
  language, up from 2) and evidence.md (new E8 block).
- dead ends: none — this sharpens rather than closes the coalition-shape
  question.
- open questions: (1) does reading the remaining ~64 names in the
  no-cutoff list change the fault-line picture further?; (2) should the
  `<600` character cutoff be replaced (e.g. matching only the
  sentence/clause containing the bill name, not the whole description)
  rather than just re-tuned, given it hides real position language?; (3)
  E8 covers only the position-keyword subset of the 345-entity roster —
  the ~274 E6 added were not systematically re-confirmed as silent beyond
  what a keyword scan catches.
- NEXT: editor is turning to the press-release data (E2's press-visibility
  gap) next session. When resumed on this case's coalition-shape thread:
  finish reading the 103-name no-cutoff list, and decide whether to fix the
  length-cutoff method before any further position-language work on this
  or other rosters in this corpus.

## 2026-07-08 (second session)

- did: editor asked directly whether E2's "quiet press" claim had actually
  been tested for, or only tested against a narrow keyword set (exact bill
  names + three broad phrases: "federal data privacy," "comprehensive
  privacy," "national privacy"). Ran the strongest available stress test:
  queried every `press_releases` row containing the bare substring "data
  privacy" (327 total, no other filter), isolated the 290 outside E2's
  original net, and forked an agent to read all 290 in full text (not
  titles — titles mislead, e.g. subcommittee names literally containing
  "Data" and "Privacy") and classify on-topic (about the comprehensive
  federal consumer-privacy-standard bill fight specifically — ADPPA/APRA/
  Cantwell-Rodgers draft/direct successor bills) vs. off-topic.
- found: **13 of 290 are genuinely on-topic** — real misses, e.g. Sen.
  Moran's statement on the Cantwell/McMorris Rodgers discussion draft
  (`release_id` 59350, 2024-04-09) and DelBene urging Congress to act on
  data privacy alongside the Biden AI executive order (`release_id` 44878,
  2023-10-30). Full list with dates/bioguides/rationale now in
  `derived/e2_revision_ontopic.csv`. **Revised E2 total: 53** (up from 40).
- found: the other 277 confirm the "quiet" framing rather than undermine
  it — they're a *different*, much louder set of controversies that happen
  to share the vocabulary "data privacy": the 2025 DOGE/Musk federal-data-
  access fight (~30, zero overlap with the 2022-2024 APRA window), the
  My Body My Data / reproductive-health privacy family (~35), TikTok/
  foreign-adversary data concerns (~25), the COPPA/KOSA family (~25 —
  already correctly excluded from this case's scope per the 2026-07-03
  KOSA-is-a-different-bill decision), committee/subcommittee-name
  boilerplate (~20), AI-governance passing mentions (~20), and ~90
  miscellaneous one-offs (student/FERPA, Olympic-athlete surveillance,
  FISA, immigration data, voter rolls, 23andMe, auto-data, insurance).
  **An 85% (277/327) false-positive rate on a bare policy-domain substring
  search** — a real finding in its own right about this press corpus:
  several distinct, differently-sized legislative fights share vocabulary
  in the same multi-year window, and any future keyword-only press-corpus
  measurement in this corpus needs to budget for that.
- did: updated evidence.md (E2 revised with the full method, result, and
  caveats), case.md (press-thinness confirm/kill criterion, Verdict),
  queries.sql (`q2c`), added `derived/e2_revision_ontopic.csv`.
- dead ends: none — this was a direct test of whether E2 was measuring
  what it claimed to measure, and it substantially was, just undercounting
  by ~13.
- open questions: (1) the borderline-case judgment calls (TikTok/Meta/COPPA
  statements that pivot to explicitly demand the comprehensive bill,
  counted on-topic) were made by a single agent pass, not independently
  cross-checked; (2) E2 still has no comparison-bill baseline — is 53 low
  for a bill of this scale, or just low in absolute terms with no
  reference point; (3) the 90-item "miscellaneous" off-topic bucket was
  characterized by theme, not individually verified against a checklist.
- NEXT: continuing into the press-release data more broadly at the
  editor's direction (separate from the specific E2 keyword-net question
  just closed out) — awaiting editor's next specific angle.

## 2026-07-08 (third session)

- did: editor asked whether roster entities show up in press by name.
  Proposed a fresh bulk substring match, but editor pointed out prior work
  existed: `client-press-mention-gap` screen already built
  `derived_client_alias_index` (LLM-reviewed alias/generic-flag table,
  ≥$1M-income Senate clients, 5,336 rows) and
  `derived_client_press_mentions` (precomputed FTS hits, 35,425 mentions/
  1,010 entities). Editor authorized reuse steps only (join existing data +
  mechanical FTS extension for names with a reviewed alias but no
  precomputed mentions yet) and explicitly withheld authorization for
  hand-rolling alias review on the unreviewed remainder, citing token cost
  from a prior over-broad pass.
- did: joined the 345-entity roster (399 raw names) against both tables.
  92 entities (99 raw names) have a usable reviewed alias; 233 entities
  (256 raw names) were never reviewed (below $1M threshold) — left
  entirely out of scope per instruction. For 14 raw names with a candidate
  alias but no precomputed mentions, re-ran
  `build_derived_client_press_mentions.py` (mechanical FTS rebuild, no LLM
  calls) — confirmed idempotent (35,425/1,010 unchanged) before trusting
  the result; all 14 came back genuinely zero-mention. Script:
  `analysis/build_press_mention_join.py` → `derived/press_mention_join.csv`
  (raw-name grain) + `derived/press_mention_join_by_entity.csv` (entity
  grain). New evidence block: E9.
- found: **VISA is the #1 entity by mention count (1,149) and it's a
  collision false positive** — sampled 15 matched releases, all 15 are
  about immigration visas, zero about Visa Inc. The alias index's own
  prior review is inconsistent: `VISA, U.S.A., INC.` was correctly flagged
  `rejected_too_generic`, but `VISA, INC.` (the raw name this roster
  actually uses) was left as a bare-word `candidate` alias and slipped
  through. **This bug lives in shared infrastructure** — it also
  contaminates the `client-press-mention-gap` screen's own ranking, not
  just this case's join. TikTok/Amazon/Intel/Microsoft/GM/American Heart
  Association's top hits were spot-checked and look clean.
- found: 14 reviewed entities have zero press mentions (American Property
  Casualty Insurance Association, LiveRamp, Twilio, Aflac, Swiss Re,
  OneMain Financial, Dapper Labs, American Transaction Processors
  Coalition, Medtronic, JM Family Enterprises, Acxiom, Deutsche Bank USA,
  plus an Amazon raw-name-variant artifact that isn't a real zero once
  rolled up to entity level) — a smaller, cleaner RELX-style candidate
  list than trying to eyeball the full noisy ranking.
- did: updated evidence.md (new E9 block, with the VISA bug flagged
  explicitly as a shared-infrastructure issue, not case-specific).
- dead ends: none — partial coverage by design (editor-scoped), not a
  failure.
- open questions: (1) does the say-vs-pay pattern hold for the 233
  never-reviewed (smaller) entities — unknown, out of scope until
  authorized; (2) should the VISA alias bug be fixed at the shared-table
  level (affects `client-press-mention-gap` too) — flagged in evidence.md's
  Open section but not this case's call alone to make; (3) is TikTok's
  high mention count actually APRA-relevant or driven by the unrelated
  foreign-adversary-ownership fight — not determined, would need reading
  a sample of TikTok's 544 matched releases the way VISA's were sampled.
- NEXT: awaiting editor direction — whether to (a) authorize extending
  alias review to the 233 unreviewed entities, (b) fix the VISA bug first
  (small, high-value, affects another case), or (c) move to something else
  entirely.

## 2026-07-08 (fourth session)

- did: editor asked to rank the top 4 press-active members (Schakowsky,
  Trahan, Moran, DelBene) against LD-203 contributions from APRA-lobbying
  registrants. First pass joined all registrants (in-house + third-party
  firms); editor questioned the mechanics ("only the lobbyist and their
  employer are listed on LD-203, not the client — did you join with the
  other LDA data to get the clients?") and I confirmed: yes, via a
  two-step inference (registrant lobbied on APRA for a roster client, same
  registrant's own LD-203 giving pulled separately) — NOT a client field
  on the LD-203 itself, which doesn't exist. Editor directed: filter to
  in-house only (registrant IS the client) going forward, since a
  third-party firm's giving can't be attributed to one of its many
  clients' motive. New evidence: E10 (all-registrant version) and E11
  (in-house-only re-cut, 513 items). Same inverted pattern holds in both:
  DelBene/Moran (fewer press releases) get more money than Schakowsky/
  Trahan (more press releases).
- did: built a timeline chart (E12,
  `analysis/build_top4_timeline_chart.py` → `derived/top4_timeline_chart.png`)
  — contributions (circles sized by amount) and press releases (triangles)
  per member, plus 5 bill-milestone reference lines (web-sourced
  2026-07-08: ADPPA introduced 2022-06-21, APRA discussion draft
  2024-04-08, APRA formally introduced 2024-06-25, markup canceled
  2024-06-27, 118th Congress ends 2025-01-03). Several matplotlib bugs
  fixed along the way (a negative refund amount broke `s=size**0.5` via a
  complex-number result; y-axis inversion made milestone-label positioning
  non-obvious; jitter added to de-blob dense lanes).
- found: editor's own read of the chart — no visible timing correlation.
  Confirmed by a proper check: contribution counts in +/-14-day windows
  around each milestone were all within a normal range EXCEPT the
  118th-Congress-ends window (1 vs ~10 expected) — investigated further
  and found this is a **routine holiday-season giving lull, present every
  year 2022-2025** (2/5/1/3 contributions in Dec20-Jan17 windows across
  four different years), not APRA-specific. Logged as a checked-and-
  rejected near-miss, not a finding — exactly the kind of multiple-
  comparisons trap this case's own doctrine warns about.
- did: editor asked to check specific ENTITIES' contribution timing, not
  just the 4 members in aggregate. Ran a pre-screen (ratio of observed to
  expected contribution count in a window around each milestone, per
  entity, using each entity's own baseline rate) before building any
  chart, per editor's explicit "don't build a per-entity chart" steer.
  Found only 3 apparent "clusters," all traced to Primerica Life
  Insurance's routine same-date batch PAC giving (identical amounts,
  identical dates, repeating quarterly-ish) — a scheduled-giving artifact,
  not a reaction to APRA news. No real per-entity timing signal survives
  scrutiny. Reported this cleanly as a negative result rather than
  building the chart.
- did: editor asked directly: "what is the point of all that lobbying if
  the bill was killed by partisan politics?" — reframed the case's
  central open question around 3 possibilities (shaping bill content
  independent of final passage; insurance/optionality lobbying for
  successor bills; defensive lobbying where "died in gridlock" is the
  cover story for industry preference). Editor chose to test #3: pull
  contributions to whoever specifically killed the bill.
- did: before pulling any data, checked who actually killed it (editor
  asked "do we know?"). Prior corpus notes only said "GOP opposition
  signals" — vague. Web search (The Hill, IAPP, Foley & Lardner) found
  specifics: Speaker Mike Johnson and Majority Leader Steve Scalise
  arranged a leadership meeting the night before the June 27 markup that
  EXCLUDED committee chair Cathy McMorris Rodgers — APRA's own lead House
  GOP sponsor — and used it to block the bill over her objection. This
  reframed the whole check: Johnson/Scalise are the reported blockers,
  Rodgers is a natural contrast case (the sponsor), not a co-conspirator.
- did: built E13 (`analysis/build_kill_decision_contributions.py` →
  `derived/kill_decision_contributions.csv`) — in-house APRA-lobbying-
  registrant contributions to Johnson, Scalise, and Rodgers.
- found: no clean separation — all three get 66-84% of their in-house
  giving from APRA-lobbying entities, Rodgers included. Then found a
  sharper-looking signal: Rodgers' APRA-linked contributions (and her
  ENTIRE recorded contribution history, any registrant) stop dead on
  2024-02-09, while Johnson/Scalise continue through Dec 2025. Almost
  reported this as a real finding — checked first whether it was
  APRA-specific or something else, and found (web search) Rodgers
  announced her retirement 2024-02-08, one day before her last recorded
  contribution. Retiring members' PAC pipelines dry up on announcement,
  routinely, for reasons unconnected to any specific bill. **This would
  have been a false "smoking gun" if not checked against her full (not
  just APRA-linked) contribution record and outside context.**
- did: editor asked about Cantwell (APRA's Senate co-author, not
  retiring, not up for re-election in this window) as a cleaner contrast
  case than the confounded Rodgers data. Added her to E13. Found: her
  APRA-linked share (46%) is lower than the House trio's (66-84%), but
  explained by senators generally receiving less concentrated corporate-
  PAC giving than House leadership (her ALL-registrant total is also
  proportionally smaller, $100K vs Johnson's $992K) — not by her position
  on the bill. Her timing shows NO gap around the markup cancellation
  (steady giving straight through 2024-06-18 into 2025), the opposite
  pattern from Rodgers — confirms the retirement explanation rather than
  undermining it.
- did: user supplied a Wired article URL (Dell Cameron, "Surprise! The
  Latest 'Comprehensive' US Privacy Bill Is Doomed",
  wired.com/story/apra-privacy-bill-doomed/) and asked how it compares to
  this case's analysis. Direct WebFetch failed (domain not fetchable by
  this session's tools); read via WebSearch + a Wikipedia citation of the
  same Wired piece instead — flagged in case.md's Prior coverage as
  provisional pending a direct re-read. Cameron's framing: bill was
  "engineered to appease conservative lobbyists representing the
  interests of big business," Scalise/leadership blocked it regardless of
  committee decisions, private right of action was a persistent sticking
  point. This matches E13's independently-sourced Johnson/Scalise/Rodgers
  account and E8's private-right-of-action fault line closely — but
  Cameron's framing implies industry capture broadly, while this case's
  money-side legs (E10-E13) found no contribution signal supporting that
  specific mechanism.
- did: editor asked the sharp follow-up — if lobbying shaped the bill's
  language (Cameron's framing) rather than bought the kill vote, shouldn't
  lobbying ACTIVITY (not money) spike when the bill's text was actually
  being drafted? Tested directly: E14
  (`analysis/build_drafting_stage_spike.py` →
  `derived/drafting_stage_spike.csv` + `_composition.csv`).
- found: real, corpus-baseline-checked spikes at both drafting moments —
  22x jump (Q1→Q2 2022, ADPPA's introduction) and 2.2x jump (Q1→Q2 2024,
  APRA's discussion draft/introduction/markup-cancellation all landing in
  one quarter — the highest single quarter in the whole 2022-2026 series)
  — against a corpus-wide baseline that's flat within ~13% every quarter
  for four straight years, ruling out a general Q2 filing-season artifact.
- did: editor pushed further — did the query actually scope to
  APRA/ADPPA-specific language (confirmed: yes, same 5-phrase bill-name/
  ADPPA filter as E1/E6/E8, not a broader "data privacy" search), and who
  dominated the spike quarters (not yet checked — this was the right
  question, since "activity spiked" alone doesn't establish "industry
  shaped it" without knowing WHO was doing the spiking).
- found: both spike quarters (and their pre-spike baseline quarters) are
  ~98-100% industry-composed by manual classification (corporations +
  trade associations) — Q1 2022: 5/5, Q2 2022: 148/148, Q1 2024: 103/104,
  Q2 2024: 223/228. No single entity dominates either spike (max 4-5
  activities out of 199-304, spread across 148-228 distinct filers) — a
  breadth phenomenon, not a few big players. The handful of non-industry
  names found (Public Knowledge, Brennan Center, Planned Parenthood,
  Susan B. Anthony List, David's Legacy Foundation) are mostly
  reproductive-rights/general-civil-liberties groups likely on a
  different angle, not confirmed APRA-specific advocacy — only Public
  Knowledge reads as core privacy-advocacy.
- did: updated evidence.md (E10-E14, full write-up), case.md (Verdict
  rewritten around the drafting-stage-lobbying-not-money-bought-the-kill
  synthesis; Prior coverage section restructured to include Wired,
  flagged as provisional pending direct read; coverage frontmatter field
  updated).
- dead ends: the money-side hypothesis (E10, E13) and the aggregate/
  per-entity contribution-timing hypothesis (E12, entity pre-screen) —
  both tested directly and both came back negative, logged as real
  negative results, not abandoned mid-check.
- open questions: (1) does E14's spike/composition pattern hold on the
  House side (Senate-only so far); (2) E14's manual industry/non-industry
  classification (~230 names x 4 quarters) not independently cross-
  checked; (3) the Wired account needs a direct re-read, not just a
  search-engine-mediated summary, before its framing is trusted for the
  case's Prior coverage verdict; (4) E2 still has no comparison-bill press
  baseline.
- NEXT: (a) direct-read the Wired article if a fetchable mirror/method is
  found; (b) House-side replication of E14; (c) decide with editor whether
  this synthesis (drafting-stage lobbying shaped text; money did not buy
  the kill decision) is strong enough to move toward closing this case
  out for the findings report, or whether more verification (builder →
  skeptic → judge per the track-investigation skill) should run first.

## 2026-07-08 (fifth session)

- did: user supplied the Wired article's full text; cited at `wired_source.md`
  (full text not redistributed here)
  (direct fetch of wired.com had failed earlier this session). Read the
  full piece — corrected my earlier search-engine-mediated summary, which
  had overstated "engineered to appease conservative lobbyists" as the
  article's throughline. The actual account: the bill's final-week
  revisions stripped civil-rights/algorithmic-decision-audit language to
  court conservative Republicans, and THAT stripping is what caused a wave
  of privacy/civil-rights orgs (named: ACLU, Center for Democracy &
  Technology, NAACP, Japanese American Citizens League, Autistic Self
  Advocacy Network, Asian Americans Advancing Justice, Access Now, Demand
  Progress, Free Press Action) to withdraw support and lobby E&C Democrats
  against the bill in its final days. Also new: Pallone's post-cancellation
  statement praising Rodgers; Rep. Barragán quoted on California-preemption
  concerns (independently corroborates E8's California State Senate
  finding, from a member's own stated reasoning rather than lobbying text).
- did: checked each of the 9 named organizations against this corpus's
  Senate LDA data (E15) — is it a registered filer, and did it lobby on
  APRA by name. Result: only 2 of 9 show up (ACLU, Demand Progress
  Action); of those, only Demand Progress's language is substantive
  ("Establishes a federal privacy baseline for treatment of covered
  data"), ACLU's is six quarters of near-identical disclosure-minimum
  boilerplate inside 10,600-18,200-character omnibus filings, missing the
  specific civil-rights objection Wired reports. The other 7 either aren't
  registered Senate filers at all (CDT, ASAN, AAAJ, JACL, Access Now — one
  false-positive name collision checked and ruled out, "Coalition for
  Access Now" is an unrelated CBD-industry group) or are registered but
  show no APRA-specific filing (NAACP, Free Press Action Fund).
- did: user drew a direct parallel to `maha-gras-capture` — a separate
  case that found industry outnumbers/outspends public-interest advocacy
  ~940:1 in registered GRAS-reform lobbying, with zero MAHA-branded
  presence, and explicitly noted "public pressure that never becomes
  registered lobbying is invisible to LDA data by construction." Agreed
  the underlying mechanism is the same. Proposed writing this up as a
  finding about lobbying-disclosure law's scope/adequacy — user pushed
  back hard and correctly: LDA is a paid-influence disclosure regime by
  design, not a general influence registry, and arguing the data/law is
  inadequate for not capturing unpaid advocacy is out of scope for this
  project and not something two lobbying-corpus case studies give us
  standing to claim. Retracted the reframe.
- did: wrote up E15 as a plain fact-check of what this case's coalition
  characterization (E3, E8) can and cannot corroborate against Wired's
  named organizations — no claim about LDA's design or adequacy attached.
  Updated case.md's Verdict and Prior coverage sections to match: replaced
  the "essentially no organized opposing voice" framing in the E14
  synthesis (that claim is only true of registered LDA activity, not of
  opposition generally, per E15) and corrected the Prior coverage entry
  now that the full article text is available (no longer "provisional
  pending direct read").
- dead ends: the "this reveals something about lobbying-disclosure law"
  framing — proposed, corrected by the editor, not used. Worth remembering
  for this case and others: a real, checkable data-coverage limitation
  (E15's table) is citable as exactly that; it is not license to draw a
  broader normative conclusion about the law or system that produced the
  data.
- open questions: (1) cross-check E15's list against maha-gras-capture's
  curated 16-org public-interest registrant list, in case it catches
  something the Wired-seeded search missed; (2) E14's House-side
  replication still open; (3) E2 still has no comparison-bill baseline.
- NEXT: awaiting editor direction on whether to close this case out for
  the findings report now, run the maha-gras cross-check first, or pursue
  something else.

## 2026-07-08 (sixth session — builder/skeptic/judge verification)

- did: editor asked for a full builder → skeptic → judge verification pass,
  specifically to cut through the sprawl (15 evidence blocks, 6 prior
  sessions) and land on clear headline findings for the report.
- did (builder): read all of evidence.md (E1-E15) and case.md, ranked
  candidate headline findings by strength. Strongest: E14 (drafting-stage
  activity spike) + E8 (fault lines) + Wired corroboration. Second:
  E10-E13 (money didn't buy the kill). Scale (E6) as necessary context,
  not itself surprising. E15 as a limiting clause on E14's "no organized
  opposition" language. Flagged E9/E4/E6's comparison-bill counts as not
  report-ready.
- did (skeptic, independent agent, re-derived directly against `gain.db`,
  did not just read the case's narrative): re-ran E14's spike query,
  E13's contribution totals, E15's org-by-org table, and E6's scale count
  from scratch.
- found (skeptic): a **real, previously uncaught bug** — the shared
  5-phrase bill-name filter (`queries.sql`, reused by E1/E6/E8/E10-E14)
  matches an unrelated bill via the bare "Data Privacy Act" phrase (H.R.
  5807/S. 3065, "the DATA Privacy Act," plus several pre-2022 discussion
  drafts), usually inside long omnibus multi-bill description fields.
  Verified directly against `gain.db` by the judge, not just taken on the
  skeptic's word (see below).
- found (skeptic): with contamination stripped, E14's "22x"/"2.2x
  single-highest-quarter" spike figures do not survive — Q1 2022 has zero
  genuine matches (bill didn't exist, not a valid baseline), and clean
  Q2 2024 (272) is exceeded by clean Q3/Q4 2022 (287/282). Real pattern:
  a sustained ~3-4x-elevated plateau across two multi-quarter windows, not
  a single-event spike.
- found (skeptic, a genuine strengthening the builder's pass missed):
  independently replicated E14's pattern on the House side (previously
  flagged as an open gap, never run) — 3.86x Q1→Q2 2024, almost identical
  to Senate's clean 3.83x. Real, unflagged cross-chamber corroboration.
- found (skeptic): E6's "2,545/345" scale figure is ~25% inflated by the
  same filter bug (clean estimate ~1,918/~367) — the *ranking* (APRA
  largest of 4 bills) likely survives given the margin over KOSA, but the
  exact figure needs re-deriving with a fixed filter before publication.
- found (skeptic): spot-checked E14's manual industry/non-industry
  classification (25-row sample) — 2 small misclassifications (American
  Heart Association, American Association for Justice), moves ~98% to
  ~97%, not verdict-changing.
- found (skeptic): the "Wired corroboration" of E8's two fault lines
  (private right of action, preemption) is less distinctive than framed —
  American Association for Justice takes the identical position on KOSA,
  verbatim, in the same filings. These are generic federal-preemption
  fault lines, not APRA-specific discoveries. Reframe as background, not
  "independent corroboration."
- found (skeptic): E13's Rodgers wording ("stops abruptly") overstates a
  taper (Feb 2024 still $93,500/35 items, declining through March) — small
  wording fix, doesn't change the verdict.
- did (judge): independently re-ran the contamination check directly
  against `gain.db` (not just trusting the skeptic's report) — confirmed
  the bare `%data privacy act%` clause matches H.R. 5807/S. 3065 and
  pre-2022 drafts inside omnibus fields. Weighed builder vs. skeptic,
  rendered verdict: **case's core thesis holds, confidence raised from low
  to medium, but the two most quotable numbers (22x spike, 2,545/345
  scale) must be corrected via a filter fix before publication** — this is
  a "fix and ship" verdict, not a refutation. Rewrote case.md's Verdict
  section around 4 ranked headline findings, a Corrections-required
  section, a killed-hypotheses section, and a not-report-ready section.
  Confidence: low → medium.
- NEXT: (1) fix the shared bill-name filter in `queries.sql` (tighten
  `%data privacy act%` or exclude known contaminants), re-run E1/E6/E8/
  E10-E14 with the corrected filter, replace the inflated headline numbers
  with clean ones; (2) fold the skeptic's House-side replication into
  evidence.md as a proper E16; (3) decide with editor whether to close the
  case out for the findings report now that a clear headline synthesis
  exists, or run the remaining "still open" items first (E2 baseline,
  maha-gras cross-check, second-reader spot-check of the rest of E14's
  classification).

## 2026-07-08 (seventh session — filter fix applied, evidence re-run)

- did: editor confirmed the judge's verdict from the sixth session and
  asked to fix the evidence blocks affected by the shared filter bug
  found in E16.
- did: identified the exact contaminant before writing any fix — pulled
  all 810 Senate rows matching bare `%data privacy act%` but none of the
  4 APRA-specific phrases, and classified them. **97% (789/810) are
  explained by H.R. 1165, "Data Privacy Act of 2023"** (an unrelated
  financial-sector/GLBA bill) — not H.R. 5807/S. 3065 as the skeptic's
  report had named as primary; H.R. 5807/S.3065/S.583/S.3337/a Wyden
  draft explain the remaining 21 rows. This correction to the skeptic's
  own attribution is logged in E16.
- did: confirmed by direct query that the bare clause adds ZERO genuine
  APRA/ADPPA rows (checked: no row matches bare "data privacy act" +
  HR8818/HR8152 bill numbers without also matching one of the 4 existing
  phrases) — the fix is a clean removal, not a partial exclusion list.
- did: removed the `OR lower(...) LIKE '%data privacy act%'` clause from
  `queries.sql` (6 occurrences) and all 7 analysis scripts that embedded
  the identical inline filter (`build_roster.py`, `build_position_read.py`,
  `build_drafting_stage_spike.py`, `build_kill_decision_contributions.py`,
  `build_corrected_roster.py`, `build_top4_inhouse_timeline.py`,
  `build_top4_contributions.py`) — fixed once at the source, mechanically
  (sed), not patched per-finding. Left `queries.sql#q2c`'s press-release
  bare-phrase clause alone — checked separately, zero contamination there
  (press release text doesn't carry the same omnibus-multi-bill-list
  pattern LDA filings do).
- did: re-ran every affected script/query and recorded clean numbers:
  - E1: Senate CPI-only 509→416, House CPI-only 499→407, combined
    1,008→823, distinct Senate clients 101→79.
  - E6/roster: 2,545 activities/399 raw names/345 entities →
    **1,950/371/319**. Top clients unchanged in identity.
  - E8/position-read: 222 rows/36 names → 114 rows/30 names; all
    previously-named entities with genuine position language (SIIA, AAF,
    Alabama Farmers Federation, AAJ, ATPC, California State Senate,
    Chamber of Progress, Center for Freedom and Prosperity, EFF, National
    Fusion Center Association, Insights Association) confirmed to survive.
  - E14/spike: full clean quarterly series pulled (17 quarters). Confirmed
    the skeptic's finding exactly — clean Q2 2024 (273) is NOT the highest
    quarter; Q3/Q4 2022 (293/288) exceed it. Real pattern: sustained
    ~3-4x-elevated plateau across 2022 H2 and 2024 Q2-Q3, not a single
    spike. Added the skeptic's 2 classification fixes (American Heart
    Association, American Association for Justice → non-industry) to
    `NON_INDUSTRY_MARKERS` and re-ran composition: ~97-99% industry,
    consistent with before.
  - House-side replication (new, not in original E14): clean House
    Q1→Q2 2024 = 70→267 (3.81x), essentially identical to clean Senate
    (72→273 = 3.79x). Confirms the skeptic's finding was not a fluke.
  - E10/E11/E13 (contributions): re-ran all three scripts. Same
    qualitative patterns hold (press-inverts-money for E10/E11; no
    blocker/sponsor separation for E13) with lower dollar totals
    (H.R. 1165-linked registrants correctly dropped from the in-house
    sets). E13's Rodgers wording corrected from "abrupt stop" to "tapers."
- did: updated `evidence.md` in place — E1, E6, E8, E14, E10, E11, E13 all
  got "corrected" sub-blocks (originals kept, marked superseded, for the
  record); E16 corrected its own H.R. 5807 attribution and added a
  RESOLVED note; the "Open" list marked the House-replication and
  classification-spot-check items done, added a new open item (check
  KOSA/AICOA/RESTRICT's own filters for equivalent contamination).
- did: rewrote `case.md`'s Verdict to present the corrected numbers
  directly (no longer "corrections required," now "corrections applied")
  — headline findings 1-4 all restated with clean figures; Hypothesis and
  confirm/kill sections' 345/2,545 references updated to 319/1,950;
  Sources/legal-risk roster figure updated.
- NEXT: (1) check KOSA/AICOA/RESTRICT's own bill-name filters for the same
  contamination pattern, to firm up E6's exact margin claim; (2) decide
  with editor whether the case is now ready to close for the findings
  report, or whether remaining "still open" items (E2 baseline,
  maha-gras cross-check) should run first.

## 2026-07-08 (eighth session — SECURE Data Act check)

- did: editor asked whether E14's revised plateau methodology shows a
  Q1 2026 signal for a new bill, the "SECURE Data Act," which the editor
  recalled being checked for "no spike" in a prior session.
- did: searched this case's own files, the newsroom ledger, and `gain.db`
  directly for any trace of a "SECURE Data Act" evidence block or lead —
  found none. Zero rows in `senate_lobbying_activities` for the bill name.
  Flagged this to the editor before proceeding rather than assuming the
  prior-session claim was accurate.
- did: editor clarified — the bill was not expected to be in the DB by
  name because it was introduced in April 2026; asked for a web search.
- did: web search found H.R. 8413, "Securing and Establishing Consumer
  Uniform Rights and Enforcement over Data Act" ("SECURE Data Act"),
  introduced by House Republicans **April 22, 2026 — Q2 2026, not Q1** as
  the editor had said (corrected this in evidence.md E17's Prior coverage
  note). A comprehensive federal privacy bill, no private right of action,
  FTC/state-AG enforcement with a 45-day cure period.
- did: checked `gain.db`'s actual date coverage before running anything
  else — confirmed the corpus's most recent quarter is **2026 Q1 only**
  (24,347 Senate filings). Q2 2026 LDA filings aren't due until ~July 20,
  2026 and aren't ingested yet. This meant a "Q1 2026 plateau check" for
  a bill introduced in Q2 2026 could not, structurally, show anything —
  flagged this before writing up a verdict, to avoid the same kind of
  "checked the wrong quarter, called it a finding" mistake E13's
  Rodgers-retirement near-miss illustrated earlier in this case.
- did: ran three checks anyway to be thorough: (1) bill-name search
  (H.R. 8413, "secure data act") — zero hits, as expected; (2) E14's
  clean APRA/ADPPA-family filter's tail through Q1 2026 — continues a
  declining trend (40→26→26→19→16 since Q1 2025), no uptick; (3) a
  broader "comprehensive/national/federal privacy" any-bill-name search —
  flat at 43-54 per quarter since Q1 2025, no uptick; (4) a targeted
  "secure"+"privacy" short-filing search for discussion-draft-style
  anticipation language (the same pattern Moran's April 2024 APRA
  statement showed ahead of formal introduction) — 7 rows, all name
  collisions with unrelated bills (SECURE Notarization Act, Secure Rural
  Schools, SAFE Banking Act), zero genuine signal.
- found: no finding can honestly be made either way. The "no spike in
  Q1 2026" result is real but uninformative — it's checking a quarter
  that predates the bill's existence by three weeks, not testing whether
  the bill generates the kind of lobbying-activity plateau APRA showed.
  Wrote this up as E17: an explicit "we cannot answer this yet, here is
  why, and here is the correct re-run date" entry, not a disguised
  negative finding.
- dead ends: none — this wasn't a hypothesis that failed, it was a
  premature check flagged before it could produce a misleading null
  result.
- NEXT: re-run E17's checks once Q2 2026 Senate LDA data is ingested
  (expected available ~2026-07-20 per LDA's ~20-day filing deadline)
  and Q3 2026 (~2026-10-20) — compare SECURE Data Act's own
  introduction-quarter lobbying pattern against APRA's Q2 2022/Q2 2024
  plateau windows using the same corrected methodology. This is a
  genuinely interesting comparison (same corpus, same methodology, a
  bill introduced right as this case's own methodology matured) but
  cannot be run until the data exists.

## 2026-07-08 (ninth session — closeout, findings report entry written)

- did: editor decided to close this case out — judged it unlikely to
  surface further significant findings in the time remaining before
  submission, and asked for a findings.md write-up. Read findings.md's
  two existing entries first to match style/conventions (story/evidence/
  methodology/caveats structure, cited filing_uuids and LDA URLs
  throughout, GAO-report/Wired-style external citations kept separate from
  corpus evidence).
- did: wrote a new findings.md entry, explicitly framed as a set of
  takeaways rather than one headline claim (unlike the other two entries)
  — the editor flagged up front this case doesn't have a single dramatic
  story the way JACK Act/Sunland Park do, and the write-up should be
  honest about that shape rather than force a false headline. Pulled
  concrete citable filing_uuids for each takeaway (drafting-stage spike
  entities, AAJ/SIIA/California State Senate position filings, a Cantwell
  contribution item) rather than citing only aggregates.
- did: closed out the case per the track-investigation skill's Path 2
  checklist (`reference/closeout.md`): condensed case.md's Verdict section
  from ~130 lines of accreted per-evidence-update prose down to a single
  current-state summary (~5 paragraphs) that states the claim, confidence,
  and remaining open items once, without re-narrating the correction
  history (that stays in log.md, which is append-only by design).
  Frontmatter updated: status open→closed, coverage line clarified as
  "not systematically scanned, do not treat as a novelty claim,"
  `**opened**/**last updated**` line replaced with `**opened**/**closed**`.
- did: recorded the closeout in the `actions` journal (priority 5, per the
  skill's doctrine that kills/closes are provisional agent actions pending
  editor acknowledgment).
- found: nothing new — this was a wrap-up session, not a data session.
- NEXT: none — case closed, see Verdict in case.md. The findings.md entry
  is the report-facing artifact; the only live thread (SECURE Data Act
  follow-up, E17) is explicitly logged as future work outside this case's
  remaining scope, not a reason to keep it open.
