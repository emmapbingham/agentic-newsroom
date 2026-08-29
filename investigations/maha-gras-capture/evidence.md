# Evidence — maha-gras-capture

## E7 — Registered lobbying on GRAS is almost entirely industry; no organized "MAHA lobby" exists in the LDA data
- **query/script:** `queries.sql#q7`
- **result:** Across all years (2022-2026 Q1), 28 distinct Senate clients have
  FOO-code filings explicitly citing "GRAS" or "generally recognized as safe."
  Of these, only 3 read as consumer/health-advocacy rather than food/chemical
  industry: Center for Science in the Public Interest (CSPI, pre-existing food
  safety nonprofit, not MAHA-branded), Alliance for Natural Health USA, and The
  Good Food Institute (plant-based/alt-protein advocacy, not a MAHA
  organization either). **No RFK-affiliated, "Make America Healthy Again"
  branded, or MAHA-coalition entity appears as a registered LDA client or
  registrant anywhere in the GRAS-lobbying data.** This directly answers "is
  there an organized MAHA lobby": no, not in the federal registered-lobbying
  sense. MAHA's influence on this fight (per prior coverage, see case.md) runs
  through public pressure/backlash campaigns and HHS/FDA administrative action
  (Kennedy directing FDA to explore GRAS reform), not K Street.
  Escalation over time (q7b): distinct clients citing GRAS per quarter rose
  cleanly from 11 (2025 Q1) to 22 (2025 Q4), holding at 22 in 2026 Q1 — a real
  doubling, roughly consistent with NOTUS's reported "12 to 35 orgs" tripling
  (their count is evidently broader than Senate FOO-code GRAS mentions alone).
  **Spend comparison (q7c):** using COALESCE(income_amt, expenses_amt) per
  filing, the 25 industry clients' GRAS-adjacent filings report $70.58M in
  total quarterly lobbying spend across 86 filings; the 3 advocacy clients
  report $75,000 across 6 filings (CSPI runs $10-15K/quarter). A ~940:1 ratio
  at face value.
- **source records:** `senate_filings` × `senate_clients` × `senate_lobbying_activities`,
  FOO issue code, GRAS keyword match, all years.
- **caveats:** THE SPEND NUMBER IS NOT ISSUE-SPECIFIC AND SHOULD NOT BE
  HEADLINED AS "$70.58M spent lobbying on GRAS." LDA filings report income/
  expenses at the FILING level (typically covering all issues a registrant
  lobbies on that quarter for that client), not broken out per issue code.
  Checked directly: ADM's $2.05M filing (e1e5ecbc-3758-46d6-ab77-c738dcdf3f6d)
  covers 10 distinct issue codes, of which GRAS/FOO is one — the $2.05M is
  ADM's entire quarterly lobbying spend, not GRAS-specific. CSPI's filing
  (86f4ff7c-7055-4ab1-96b8-74d2c7fbbb8c) covers exactly 1 issue code, so its
  $10-15K/quarter genuinely is close to single-issue. The asymmetry in
  ORGANIZATIONAL PRESENCE (25 industry clients vs. 3 advocacy clients, and zero
  MAHA-branded registrants) is a clean, directly supportable finding. The raw
  dollar comparison is directionally suggestive (industry's multi-issue
  lobbying operations dwarf CSPI's single-issue one by any reasonable
  apportionment) but the precise ratio is an artifact of LDA's filing-level (not
  issue-level) expense reporting and should be presented with that caveat if
  used at all.
- **verdict:** supports (organizational asymmetry is solid; dollar ratio needs
  the issue-level caveat spelled out, or an apportioned estimate, before citing
  a number)

## E8 — The GRAS pattern generalizes: many issue codes have heavy industry lobbying and near-zero public-interest advocacy presence
- **query/script:** `queries.sql#q8` (curated advocacy-org list + issue-code census)
- **result:** Built a manually-curated list of 16 confirmed public-interest/
  consumer/environmental advocacy registrants that appear in the corpus (ACLU,
  Public Citizen, Consumer Federation of America, Consumer Reports, Sierra
  Club, Earthjustice, NRDC, EDF, EWG, Common Cause, Center for Responsible
  Lending, American Public Health Association, Union of Concerned Scientists,
  CSPI, Good Food Institute). NOT a name-pattern/keyword heuristic — tried that
  first (matching "coalition"/"foundation"/"center for") and it failed
  immediately: it caught industry-funded groups with advocacy-sounding names
  ("Data Center Coalition," "Coalition of Manufacturers of Smoking
  Alternatives") at least as often as genuine public-interest orgs.
  Among issue codes with 200+ distinct 2025 clients AND a plausible
  public-interest counter-lobby (i.e., excluding codes like Defense/Aerospace/
  Veterans/Tariffs where "public advocacy" isn't a natural opposing force):
  Environment (1,556 clients, 6 advocacy = 0.4%), Agriculture (1,519, 6 =
  0.4%), Consumer Safety/Products (646, 3 = 0.5%), Food Industry (402, 5 =
  1.2%), Computer Industry (566, 1), Pharmacy (405, 1) all show heavy
  imbalance. Insurance (400 clients), Medical/Disease Research (418), Real
  Estate (276), and Utilities (245) show ZERO of the 16 curated orgs present.
  Sanity-checked Insurance's zero result: found 3 clients with
  consumer/patient-sounding names (Consumer Credit Industry Association,
  Diabetes Patient Advocacy Coalition, Federation of Americans for Consumer
  Choice) that are actually industry-funded trade/advocacy groups on closer
  look — reinforcing why name-pattern matching is unreliable and why this
  needs to stay a curated, verified list.
- **source records:** `senate_filings` × `senate_clients` × `senate_lobbying_activities`
  × `ref_issue_codes`, filing_year=2025, grouped by issue code.
- **caveats:** This is a SCREEN, not a finding — it identifies WHERE to look,
  not proof of capture in any of these areas. The 16-org advocacy list is
  necessarily incomplete (built from well-known national orgs; misses smaller/
  regional/single-issue advocacy groups that may lobby under names not
  obviously "advocacy"). Zero advocacy presence does not mean zero public
  pushback — as E7 shows for GRAS, MAHA won a real fight (S.3122 preemption)
  with NO registered lobbying presence at all, via public/political pressure
  instead. This screen can only see the K Street side; the public-pressure
  side is structurally invisible to LDA data by definition. Each of these
  issue codes would need its own case-style drilldown (bill-level, like GRAS)
  before any capture claim could be made — this is a lead-generation result,
  not a verified pattern.
- **verdict:** needs-follow-up (real, reusable pattern; worth formalizing as a
  named screen via generate-query-ideas rather than a one-off case query —
  each candidate issue code needs its own outcome research before it's a story)

## E1 — FOO lobbying activity ran above baseline in 2025, issue-specific not a volume artifact (VERIFIED)
- **query/script:** `queries.sql#q1`, `queries.sql#q1b`
- **result:** Re-derived cleanly. z=6.14 (population sd) / 5.88 (sample sd) for
  FOO in both 2025 Q3 and Q4 (386 activities vs 2022-24 baseline mean ~304,
  sd~13.3). Income apportioned: ~$7.6M/quarter in 2025 Q3-Q4 vs ~$5.3M baseline
  mean. Base-rate check (q1b): overall Senate lobbying activity volume across
  *all* issue codes rose only ~8-13% in 2025 vs the 2022-24 baseline
  (~45-46k/quarter → ~50-52k/quarter) — FOO's +27% (304→386) rise is
  disproportionate, not just riding a global 2025 lobbying-volume wave.
  2026 Q1 drops sharply back to 257 (z=-3.55) — a post-surge falloff worth
  noting (could mean the legislative window closed, or seasonal Q1 dip —
  2022 Q1 was also the lowest quarter of that year, so partly seasonal).
- **source records:** derived_issue_quarter_volume_press (gain.db);
  senate_lobbying_activities × senate_filings for base rate
- **caveats:** FOO n_press_releases=0 by construction (no keywords mapped in
  ISSUE_KEYWORDS); cannot use press column as signal. 2026 Q1 seasonal dip
  means the 2025 Q3/Q4 peak could be a temporary spike, not a sustained shift —
  don't overclaim durability without 2026 Q2+ data.
- **verdict:** supported (surge confirmed, issue-specific, not base-rate noise)

## E2 — Industry lobbying on GRAS/S.3122 is broad (25 clients); direct S.2341-vs-S.3122 contrast is thinner than first pass suggested
- **query/script:** `queries.sql#q2` (dedup by client + filing count), plus
  targeted stance checks below
- **result:** 25 distinct clients cite GRAS reform, "generally recognized as
  safe," or S.3122/Better FDA Act language in 2025 FOO filings (up from the 7
  named in the original scout pass). Top by filing count: Consumer Brands
  Association (8), International Dairy Foods Association (7), ADM (5), United
  Natural Products Alliance (4), PepsiCo (4), Mondelez (4), Conagra (4), Bunge
  (4), American Bakers Association (4).
  **Strongest single data point:** American Beverage Association names S.3122
  by bill number explicitly and only S.3122 — "H.R.4958 Grocery and Safety
  Reform Act S.3122 The Better FDA Act - Issues related to ingredient
  transparency" (filing e6f80865-fc70-49c8-b2c3-cc9c7eb60433) — no mention of
  S.2341 anywhere in its 2025 filings.
  **Complication found on drilldown:** only CSPI names S.2341 explicitly among
  pro-reform-side filers. But International Dairy Foods Association (filing
  c6bb1ba6-4b4c-4ae4-aa49-3b27d5ce2952) and Pharmavite LLC BOTH name S.2341 AND
  S.3122 in the same filing, neutrally, alongside a long list of other bills —
  this reads as "monitor everything relevant to our issue," not "support the
  weak bill, oppose the strong one." Environmental Defense Action Fund (a
  pro-reform environmental group) also names S.3122 — plausibly tracking it to
  oppose/amend it, not endorsing it. A same-titled 2023 predecessor bill
  (S.3387, 118th Congress) shows up in Abbott Laboratories and Apeel Sciences
  filings under near-identical title language ("Ensuring Safe and Toxic-Free
  Foods Act") — this is NOT the current S.2341 and should not be counted as
  either side lobbying the current bill.
- **source records:** Full client list + filing UUIDs in
  `queries.sql#q2`/`#q2b`/`#q2c` re-run output. Key UUIDs: American Beverage
  Assoc e6f80865-fc70-49c8-b2c3-cc9c7eb60433; ADM
  e4b0fbd4-3c16-4e87-b38f-de1ddb671933; IDFA (both bills)
  c6bb1ba6-4b4c-4ae4-aa49-3b27d5ce2952; CSPI (S.2341 only)
  86f4ff7c-7055-4ab1-96b8-74d2c7fbbb8c.
- **caveats:** Most industry descriptions (ADM, Bunge, Cargill, Conagra,
  Consumer Brands) cite "GRAS reform"/"GRAS regulatory process" generically —
  topic-level lobbying, not a stated position on either bill. Only American
  Beverage Association is an unambiguous single-bill (S.3122-only) citation.
  The "industry lobbies FOR S.3122 AGAINST S.2341" framing is not well
  supported by description text alone — LDA descriptions record subject matter
  lobbied, not position taken. This is a structural limitation of the LDA
  disclosure form itself, not a data-quality issue in this corpus — worth
  noting explicitly if this becomes a finding.
- **verdict:** needs-follow-up (topic-level lobbying confirmed broadly; the
  clean "pro-weak-bill vs. pro-strong-bill" contrast is real only for American
  Beverage Association on current evidence — everyone else needs a different
  signal, e.g. cosponsorship/contributions, to establish position)

## E3 — Two competing bills: S. 2341 (close loophole) vs S. 3122 (disclose only)
- **query/script:** `queries.sql#q3` (press release texts)
- **result:** S. 2341 (Booker/Markey, Ensuring Safe and Toxic-Free Foods Act):
  requires FDA pre-market review of all new food chemicals, prohibits
  self-affirmation, bans GRAS for carcinogens/endocrine disruptors.
  S. 3122 (Britt/Marshall/Scott, Better Food Disclosure Act / "Better FDA Act"):
  requires companies to report GRAS determinations to FDA; allows state officials
  to petition FDA for review; framed as "response to state-led efforts" — 
  implies federal floor that could preempt state bans.
  Industry lobbying descriptions cite S. 3122 neutrally/positively; no
  descriptions found citing S. 2341 by name.
- **source records:** Press release URLs:
  https://www.booker.senate.gov/news/press/booker-markey-introduce-legislation-to-get-dangerous-chemicals-out-of-food
  https://www.britt.senate.gov/news/press-releases/u-s-senators-katie-britt-roger-marshall-rick-scott-introduce-bill-to-ensure-safer-food-for-american-families/
- **caveats:** Bill texts not yet retrieved — preemption claim is inference from
  "response to state-led efforts" language, not confirmed statutory text.
  Neither bill has passed. Legislative inaction could reflect ordinary gridlock,
  not active industry blocking.
- **verdict:** supports (partial — bill text verification needed)

## E4 — Hyde-Smith press release: 258 food/ag groups demand seat at MAHA table
- **query/script:** `queries.sql#q4`
- **result:** June 24 2025 Hyde-Smith release (republished farm publication piece)
  describes 258 food and agriculture groups sending letter to MAHA Commission
  demanding transparency and stakeholder inclusion, citing "errors and
  distortions" in inaugural MAHA report, warning against "hidden agenda."
  A prior March letter from 300+ orgs called for "sound science" on crop
  protection and food ingredients.
- **source records:** https://www.hydesmith.senate.gov/food-and-ag-groups-seek-more-input-maha-activities
- **caveats:** This shows industry pushback against MAHA, not lobbying against
  specific legislation. Hyde-Smith is an agriculture-committee senator from MS —
  her role as industry mouthpiece is expected and disclosed.
- **verdict:** supports (industry-MAHA tension is real and documented)

## E6 — Say-vs-pay: food-industry PAC money concentrates on Marshall/Britt/Cammack, near-zero on Booker/Markey
- **query/script:** `queries.sql#q6`
- **result:** Via `honoree_member_map` (confidence >= 0.9 only), food-industry-named
  PACs gave: Marshall (R-KS, S.3122 lead sponsor) ~$53,500 across 8 distinct
  food/ag PACs (ADM PAC, Cargill PAC, Tyson PAC, IDFA PAC, Dairy Farmers of
  America PAC, Bunge PAC, American Beverage PAC, American Bakers PAC, Pet Food
  Institute PAC, PepsiCo Concerned Citizens Fund, FMI FoodPAC); Britt (R-AL,
  S.3122 cosponsor) ~$16,500 across 6 PACs; Cammack (R-FL, sponsor of the
  narrower House GRAS bill industry has rallied around) ~$7,500 across 5 PACs;
  Rick Scott (R-FL, S.3122 cosponsor) $1,000. Booker (D-NJ, S.2341 lead
  sponsor) received $5,260 total, and only from "Food Solutions Action PAC" —
  not one of the major processed-food/ag names that gave to Marshall. Markey
  (D-MA, S.2341 cosponsor) received **zero** dollars from any food-industry PAC
  in his top 15 LD-203 contributors (his largest are self-funding, unions,
  and trial lawyers).
- **source records:** `senate_contribution_items` × `honoree_member_map`
  (bioguide M001198=Marshall, B001319=Britt, C001039=Cammack, S001217=Rick
  Scott, B001288=Booker, M000133=Markey). Example filing_uuids for Marshall/ADM
  PAC: 93d16eea-c302-442d-afc5-8fbf4ae0161d (2023-09-26, $2,000),
  57e39c8a-4765-466c-aea1-257673cea976 (2025-02-18, $1,000),
  a05b9c13-163b-46ea-9371-e89732615365 (2025-09-17, $2,000).
- **caveats:** LD-203 covers only lobbyist/registrant-affiliated contributions
  (PAC and event-related giving disclosed by lobbying registrants), not full
  FEC campaign totals — this is a slice of money, not the whole picture, and
  actual industry giving to these members via non-lobbyist-registered PACs or
  direct FEC channels is NOT captured here. Time window spans 2022-2026,  not
  isolated to the S.3122/S.2341 introduction period, so this shows a standing
  relationship, not necessarily bill-triggered giving. Booker's $5,260 and
  Markey's $0 could also reflect that food-industry PACs simply don't donate to
  Democrats/reform-sponsors as a matter of course, independent of this
  specific bill fight — a base-rate check against other Democrats' food-PAC
  receipts would strengthen this.
- **verdict:** supports (clear say-vs-pay asymmetry: the S.3122/Cammack-bill
  sponsors are the industry's PAC recipients; the S.2341 sponsors are not)

## E5 — MAHA press releases: sponsor-only GRAS coverage, corrected count (2026-07-15)
- **BUG, caught 2026-07-15:** the original version of this block (query
  `queries.sql#q5`, preserved below for the record) used bare, unescaped
  substring matching — `lower(text) LIKE '%maha%'` and `LIKE '%gras%'` — which
  collides with ordinary words. `%maha%` matches Omaha, Mahalo, Taj Mahal,
  Tomahawk, and Mayor Mahan; `%gras%` matches Grassley (by far the largest
  single source — 1,139 of 1,499 raw hits), grassroots, grasp, grasslands,
  Ingrassia, and Mardi Gras. The original count ("198 R + 105 D... GRAS:
  effectively zero, 1 release each from Booker and Markey") is **not
  reliable** — re-derive from `queries.sql#q5b/q5c/q5d` before citing any
  number from this block.
- **query/script:** `queries.sql#q5b` (corrected MAHA count, title-anchored),
  `queries.sql#q5c` (corrected GRAS/food-chemical-reform count, FTS5
  tokenized + broadened phrase set + manually verified exclusions),
  `queries.sql#q5d` (whole milk count, same word-boundary-safe approach).
- **result — corrected MAHA-branded release count:** 134 releases in 2025
  from 69 distinct members (not 303/198R+105D). Word-boundary-safe: matches
  `title LIKE '%MAHA%'` or `text LIKE '%Make America Healthy Again%'`, no
  bare lowercase substring.
- **result — corrected GRAS/food-chemical-reform count:** 4 substantive,
  on-topic releases in all of 2025, from 4 distinct members — and every one
  of them is the bill's own sponsor talking about their own bill, not a
  rank-and-file member picking up the fight:
  - **Rep. Jan Schakowsky + Rep. Rosa DeLauro** (D), 2025-07-10, "Schakowsky,
    DeLauro Introduce Legislation to Help Ensure the Food We Eat is Safe" —
    the Food Chemical Reassessment Act of 2025, a *different* GRAS-reform
    bill not previously counted in this case (
    https://schakowsky.house.gov/media/press-releases/schakowsky-delauro-introduce-legislation-help-ensure-food-we-eat-safe
    ).
  - **Sen. Cory Booker + Sen. Ed Markey** (D), 2025-07-17, "Booker, Markey
    Introduce Legislation to Get Dangerous Chemicals Out of Food" — S.2341
    (already known, E3) (
    https://www.booker.senate.gov/news/press/booker-markey-introduce-legislation-to-get-dangerous-chemicals-out-of-food
    ).
  - **Rep. Frank Pallone** (D), 2025-08-14, "Pallone Unveils Food Safety
    Bill as Kids Prepare to Head Back to School" — a separate House bill on
    the same food-ingredient loophole, tied to a Rutgers University
    roundtable, not previously counted (
    https://pallone.house.gov/media/press-releases/pallone-unveils-food-safety-bill-kids-prepare-head-back-school
    ).
  - **Sen. Katie Britt + Sen. Roger Marshall + Sen. Rick Scott** (R),
    2025-11-10, announcing S.3122 (already known, E3) (
    https://www.britt.senate.gov/news/press-releases/u-s-senators-katie-britt-roger-marshall-rick-scott-introduce-bill-to-ensure-safer-food-for-american-families/
    ).
  Rep. Hyde-Smith's June 2025 release (E4) is industry-pushback framing, not
  a bill announcement, and is counted separately. **Markey does not appear
  as an independent confirming case under this corrected keyword set** — his
  only hit is the joint Booker/Markey announcement; the original
  "1 release each from Booker and Markey" implied he generated his own
  press separately, which this correction does not support. Two genuinely
  new on-topic releases surfaced by this correction (Schakowsky/DeLauro,
  Pallone) that the original pass missed entirely.
- **result — whole milk comparison, CORRECTED AGAIN 2026-07-15 (same day):**
  33 releases in 2025 from 18 distinct members mention whole milk
  (`title LIKE '%whole milk%'` or `text LIKE '%Whole Milk for Healthy Kids%'`)
  — but **only 2 of those 33 also mention MAHA or "Make America Healthy
  Again"**: Tuberville (2025-04-01, "Tuberville Calls for Healthier Options
  for Students at Ag Hearing") and Thompson (2025-12-15, "House Overwhelmingly
  Passes Thompson's Whole Milk for Healthy Kids Act"). The other 31 —
  Schrier, Thompson's earlier releases, Fetterman, McCormick, Schumer,
  Hyde-Smith, Welch, Heinrich, Feenstra, Mannion, Stefanik, Kelly, Ryan,
  Riley, Van Orden, Vasquez, Durbin — frame the bill entirely in
  dairy-farmer/school-nutrition/bipartisan-committee-win terms, with no MAHA
  language at all. **Whole Milk for Healthy Kids Act is, for all but two
  sponsors, not being sold as a MAHA win — it is ordinary bipartisan
  agriculture-committee legislation that happens to also satisfy a MAHA
  talking point RFK Jr.'s office separately claims credit for.** This
  materially weakens the "MAHA takes the easy win" framing as originally
  drafted (this file's own text, written earlier the same day, called this
  "no MAHA-branding filter needed," treating the raw whole-milk count as
  interchangeable with a MAHA-branded count — that framing is retracted
  here). The MAHA-branded comparison that is actually defensible: **2
  MAHA-branded whole-milk releases vs. 4 MAHA-branded/sponsor GRAS
  releases** — GRAS reform gets as much or slightly more MAHA-branded press
  attention than whole milk does, not less.
- **source records:** press_releases + press_fts, gain.db. All release URLs
  listed above.
- **caveats:** Keyword mapping is still not exhaustive — a member could
  discuss GRAS reform using neither "GRAS" nor any phrase in the q5c set.
  The corrected picture is now narrower than either prior draft of this
  block claimed: the real, defensible finding is not "MAHA talks milk
  instead of GRAS" (retracted — most milk coverage isn't MAHA-branded) nor
  simply "sponsor-only GRAS coverage vs. bigger whole-milk volume"
  (misleading without the MAHA-mention breakdown) but specifically: **of
  134 MAHA-branded releases from 69 members in 2025, only 6 total (2 on
  whole milk, 4 on GRAS) engage with either specific food-policy fight by
  name — the other 128 MAHA-branded releases are about other topics
  entirely** (not yet broken down — see open question below). Whatever
  the real MAHA-press-attention story is, "milk beats GRAS" is not it as
  currently evidenced.
- **verdict:** needs-follow-up, downgraded from "supports" — the
  sponsor-only-coverage fact for GRAS still holds (4 releases, all
  sponsors, zero rank-and-file), but the comparison to whole milk as a
  contrasting "MAHA easy win" does NOT hold once whole-milk releases are
  checked for actual MAHA branding. Before this proceeds to any writeup: (1)
  determine what the 128 non-milk, non-GRAS MAHA-branded releases actually
  are about (seed oil, dietary guidelines, food dye, general RFK Jr.
  messaging?) — this is the real comparison set, not whole milk by raw
  volume; (2) decide whether "sponsor-only GRAS coverage" is newsworthy on
  its own, without a "vs. the easy win" contrast, since that contrast as
  drafted twice today has now failed verification twice.

<details>
<summary>Original E5 (2026-06-25/07-02, superseded — kept for the record, do not cite)</summary>

- **query/script:** `queries.sql#q5`
- **result:** 198 Republican + 105 Democrat press releases mention MAHA or
  "Make America Healthy Again" in 2025. The dominant legislative outcome is the
  Whole Milk for Healthy Kids Act (passed Congress, signed into law). Seed oil:
  4 press releases. Dietary guidelines: 27. GRAS/food chemicals: effectively
  zero (Booker/Markey bill = 1 press release from each sponsor).
- **source records:** press_releases table, gain.db
- **caveats:** Keyword mapping is incomplete — may undercount GRAS mentions if
  members used different terminology. Press release corpus covers member offices
  only, not committee statements or floor speeches.
- **verdict:** supports (MAHA legislative output visible in press ≠ what industry
  was lobbying about; gap is real) — **superseded, see corrected block above.**

</details>
