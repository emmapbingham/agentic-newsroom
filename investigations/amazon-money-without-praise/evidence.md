# Evidence — amazon-money-without-praise

## E1 — Amazon ranks 4th in client-mention-honoree-triangle screen; press sample shows zero endorsements
- **query/script:** screen 40 / run 36 (`newsroom.db`, `derived_client_press_mentions` /
  `senate_contribution_items` honoree join) — see original lead, `leads.id=73`
- **result:** entity_id=125 (AMAZON.COM SERVICES, INC.), 39 distinct members,
  $396,150 total reported honoree contributions, $250-$38,200/member, both
  parties. Spot-check of ~15-20 substantive (non-collision) press mentions from
  money-taking members found zero clearly favorable/endorsement mentions:
  Wyden ("Demand Amazon Improve its Treatment of its Delivery Drivers"),
  Baldwin ("Calling Out Amazon's Mistreatment of Delivery Drivers"),
  Blackburn/Blumenthal ("Probe Amazon & Google After... Child Sexual Abuse
  Material"), Hoyer/Pallone/Van Hollen on Amazon-adjacent ICE warehouse siting,
  Pallone on recalled-product removal, Warren (CEO pay-to-play, mass layoffs).
- **source records:** press_releases (urls not yet re-pulled into this case —
  TODO re-derive list with press_id/url per mention); senate_contribution_items
  honoree_name='AMAZON.COM SERVICES, INC.' joined via honoree_member_map.
- **caveats:** sample, not full population (~15-20 of 39 members' mentions
  checked); honoree_member_map confidence not yet re-verified per row at
  `>=0.9` threshold for this specific entity; press mention could still contain
  incidental/neutral (non-critical, non-favorable) text not captured by the
  "collision" filter — worth re-checking the collision/non-collision split.
- **verdict:** supports (money/praise disconnect) — carried over from lead,
  not yet re-derived in this case; **TODO: re-run and re-cite before this
  becomes a report claim.**

## E2 — Amazon's top lobbying issue codes, correct in-house filer, 2022–2026 Q1
- **query/script:** `queries.sql#q1`
- **CORRECTION (2026-07-08):** the original pull of this evidence block used
  `senate_clients.id IN (184204, 210237)` ("AMAZON.COM SERVICES, INC." as a
  *client* of outside registrants AVOQ LLC / Endgame Strategies LLC) — a
  different filer than the one the money/press screen (E1/E4) actually
  reaches. Screen 40 only reaches **in-house filers** via exact
  entity↔registrant name match (documented bound in `screens.baseline`);
  entity_id=125 resolves to registrant_id=54494, "AMAZON.COM SERVICES LLC",
  filing **as its own registrant** (18 filings, one per quarter 2022–2026 Q1).
  That is the correct entity for this case. Numbers below replace the
  original (wrong-entity) table.
- **result:** registrant_id=54494 files a near-identical comprehensive
  activity list every quarter (18/18 filings touch each of ~20 issue codes —
  this is one large omnibus filing per quarter, not topic-specific filings).
  Confirmed present in every quarter: Labor Issues/Antitrust/Workplace (18),
  Consumer Issues/Safety/Products (18), Computer Industry (18), Taxation (18),
  Small Business (18), Telecommunications (18), and 14 more codes at 18 or
  16/18. This is a different filing pattern than the outside-firm filings
  (AVOQ/Endgame, which file narrower, more topic-specific quarterly
  activities) — in-house filings read as one omnibus issue list repeated each
  quarter with the "including [bill list]" clause updated as bills change.
- **source records:** `senate_registrants.id`=54494 ("AMAZON.COM SERVICES
  LLC"); `senate_filings.client_id` also 158902 (self-filed, client=self).
- **caveats:** this is Amazon's in-house registration only — it excludes the
  33 filings via AVOQ/Endgame Strategies (client_ids 184204, 210237, still a
  real Amazon lobbying channel, just not the one the money screen reaches)
  and other Amazon-family entities (AWS, Amazon Corporate — ~40 client rows
  total in senate_clients). Total Amazon lobbying footprint is larger than
  what's captured here; this case's claim is scoped to the entity actually
  tied to the honoree money and press mentions in E1.
- **verdict:** neutral (context, corrected) — establishes what the money-
  linked Amazon entity lobbies on; E3 ties specific bills to the criticism
  topics.

## E3 — Amazon's in-house filings name the antitrust and warehouse-worker bills in every relevant quarter, 2022–2026 Q1
- **query/script:** `queries.sql#q2` (corrected to registrant_id=54494)
- **result:** Labor Issues/Antitrust/Workplace activity descriptions, all from
  registrant_id=54494 (self-filed), one activity per quarter, each combining
  labor/workplace/competition issues in a single running list:
  - 2022 Q1–Q4 (filing_uuids 14dc5304-6a3b-470c-a46a-da8366ca2046,
    1e2c937c-44df-4173-b8f1-1761e568b69f, 0445d82f-0734-481e-a3ac-14e6077eb171,
    2046deaf-bd5d-42dd-b10f-fbedbe06e99a): "...competition...including the
    American Choice and Innovation Online Act of 2021 (H.R. 3816)...the
    Competition and Antitrust Law Enforcement Reform Act of 2021 (S. 225)...
    the American Innovation and Choice Online Act (S. 2992)."
  - 2024 Q2–Q4 (filing_uuids 7aa7ca99-9c14-4fc7-ad20-45caa738ca87,
    f3f53731-47d1-42fa-b09d-e2339702497d, 2d06ab44-9b9e-4a24-888b-4bc6b431bfba):
    "...competition, contracting...including the AMERICA Act (S. 1073), the
    Warehouse Worker Protection Act (H.R. 8639 / S. 4260)..." (2024 Q2–Q3 also
    name a successor antitrust bill, S. 2033, "a bill to provide that certain
    discriminatory conduct by covered platforms shall be unlawful")
  - 2025 Q3–Q4, 2026 Q1 (filing_uuids f6449d57-3dc3-459c-93f0-e93210053421,
    ea7b9ed1-5e08-4c31-a04b-fe04480d73d2, eb88d053-1e97-4089-8e38-d2234c9bb80e):
    continuing to name the **119th-Congress successor bill, S. 2613**,
    "Warehouse Worker Protection Act" (sponsor: Sen. Markey, same as S.4260 —
    confirmed via congress.gov, `data/congress_bills/bill_119_s_2613.json`;
    also stalled in committee).
  Consumer Issues/Safety/Products descriptions (not re-verified for the
  corrected entity in this pass, carried from original pull — **TODO
  re-confirm against registrant_id=54494**): SHOP SAFE Act, INFORM Consumers
  Act, kids online safety legislation.
- **source records:** all filing_uuids resolve to
  `https://lda.gov/filings/public/filing/{filing_uuid}/print/`
- **caveats:** LDA activity descriptions disclose subject and relevant bills,
  not the position taken — LDA filings don't record stance. "Opposing" is an
  inference from bill content (pro-regulation/pro-enforcement bills) plus
  Amazon's publicly reported positions on them (outside this corpus) —
  **flag as inference, not directly sourced, until corroborated** by a
  non-LDA source (e.g. a public statement or news account of Amazon's
  position). The persistence across 4+ years and two Congresses (same bill
  renamed/renumbered, same sponsor) is the strongest part of this evidence
  block — this is not a one-off mention.
- **verdict:** supports — ties the money-linked entity's lobbying subject
  matter directly to the criticism topics in E1, with the correct filer this
  time, and shows the antitrust/warehouse-worker fight is sustained, not
  incidental. "Opposing" framing still needs a non-LDA source before it's
  stated as fact in the report.

## E4 — cosponsorship check: money-taking members mostly did NOT cosponsor the bills Amazon lobbies against
- **query/script:** `investigations/amazon-money-without-praise/analysis/pull_cosponsors.py`
  (source: `sources/congress-gov-bills.md`)
- **result:** None of the 4 bills received a floor vote (all died in
  committee/calendar — confirmed via each bill's `latestAction`), so
  cosponsorship is the only available legislative-behavior signal. Of the 39
  Amazon-money members (screen 40, entity_id=125), split by chamber-eligible
  count:
  | bill | cosponsored/sponsored | eligible (right chamber) |
  |---|---|---|
  | S.2992, AICOA (antitrust, Senate) | 2 | 21 |
  | H.R.3816, AICOA (antitrust, House) | 1 | 18 |
  | S.4260, WWPA (warehouse worker, Senate) | 1 | 21 |
  | H.R.8639, WWPA (warehouse worker, House) | 5 | 18 |

  Cosponsors: Mark Warner ($38,200, largest recipient in the whole 39-member
  set) and Jack Reed ($25,750) on S.2992; Angie Craig ($6,200) on H.R.3816;
  Tina Smith ($250) on S.4260; Frank Pallone ($15,000), Bennie Thompson
  ($6,000), Jimmy Gomez ($5,000), Melanie Stansbury ($1,000) on H.R.8639, plus
  **Donald Norcross ($1,000) — who is H.R.8639's primary sponsor**, not just a
  cosponsor.
- **source records:** bioguide ids join directly to `members.bioguide` (no
  fuzzy matching — congress.gov's `bioguideId` is the same id space). Raw API
  responses: `data/congress_bills/cosponsors_{congress}_{type}_{num}.json`.
  Full crosswalk: `investigations/amazon-money-without-praise/derived/cosponsorship_crosswalk.json`.
- **caveats:** cosponsorship as of retrieval (2026-07-08); withdrawals were
  zero at that time per the API's pagination counts (see sources manifest).
  Small base rates (1-5 out of ~18-21) make percentage framing fragile — state
  counts, not rates, in any report language. This is cosponsorship, a cheap
  / low-cost signal itself (weaker than a floor vote, which none of these
  bills got) — so a "no" here is weaker evidence of capture than a "no" on an
  actual vote would be; frame accordingly.
- **verdict:** supports, and the apparent "mixed" pattern resolves cleanly
  once cross-checked against E5 — see below. Once Warner/Reed are correctly
  reclassified as non-critical (collision matches, not genuine Amazon
  criticism), the remaining money-taking, *genuinely critical* members show
  **zero** cosponsorship of the bills addressing their own criticism, with
  one informative exception (Norcross) that strengthens rather than weakens
  the case — see E5.

## E5 — Warner and Reed's Amazon mentions are collision matches, not criticism; Norcross is the real (and sharply critical) case
- **query/script:** direct pull of `press_releases.text` for the release_ids
  behind Warner's and Reed's E4-flagged mentions, plus Norcross's full mention
  list, all via `entity_id=125` in `derived_client_press_mentions`.
- **result:**
  - **Warner (4 mentions, $38,200):** all 4 are incidental. Two are AI-safety
    oversight letters sent to a *list* of ~7 companies including Amazon,
    Anthropic, Google, Meta, Microsoft, OpenAI (release_id 39075, 71776) —
    not Amazon-specific. One (46051) is Warner **praising** Amazon by name as
    a Virginia economic-development recruiting win ("we know from our
    experience recruiting Hilton, Capital One, Northrop Grumman, Amazon..."),
    which if anything cuts the *opposite* direction from "criticism." One
    (94426) doesn't mention Amazon in the retrieved text at all (likely an
    FTS/matched-alias false positive on a general intelligence-hearing
    transcript). **None of these are criticism.**
  - **Reed (2 mentions, $25,750):** release_id 103786 is a DOGE-conflict-of-
    interest letter (with Warren and Wyden) about a Treasury DOGE staffer's
    stock holdings — Amazon appears only as one of three tech stocks
    ("Google, Oracle, and Amazon") the staffer personally owns; not
    Amazon-directed criticism, Amazon is incidental collateral in a story
    about someone else's ethics. Release_id 139454 is a tariff-refund bill
    announcement where **Sen. Heinrich** (not Reed) is quoted naming Amazon
    generically alongside Walmart as a "big corporation" example — not Reed's
    words, not Amazon-specific. **Neither is Reed criticizing Amazon.**
  - **Norcross (10 mentions, $1,000 — smallest amount in the 39-member set):**
    unambiguously and repeatedly critical: "Rep. Norcross Calls for OSHA
    Investigation into Amazon Warehouses After Reports of Skyrocketing
    Injuries" (2022-04-29), "...Slams Amazon After Another Report Reveals the
    Company is Responsible for More Than Half of All Serious Injuries..."
    (2023-04-13), a press conference held *in front of an Amazon warehouse*
    (2022-06-01), a reaction to a worker's death (2022-07-20) — 8 releases of
    sustained, Amazon-specific criticism on warehouse safety over 2022-2023,
    then in 2024 he **introduces** H.R.8639, the Warehouse Worker Protection
    Act, followed by a 2025 bicameral reintroduction (S.2613/successor).
- **source records:** `press_releases.release_id` 39075, 46051, 63356, 71776,
  94426 (Warner); 103786, 139454 (Reed); Norcross release_ids listed in
  `derived_client_press_mentions` for bioguide_id N000188, entity_id=125
  (full list of 10 in that table). All resolve via `press_releases.url`.
- **caveats:** this is a full check of all of Warner's and Reed's Amazon
  mentions (2 and 4 respectively — small enough to read in full, not a
  sample), so the "collision, not criticism" call for them is high-
  confidence, not a spot-check. Norcross's classification as genuinely
  critical is based on titles for 8 of 10 releases (highly unambiguous
  wording) plus the sponsor action itself; the 2 remaining (2023-01-20,
  2022-11-17) also read as critical from title alone but weren't pulled in
  full text here.
- **verdict:** supports — resolves E4's "mixed" reading. Warner and Reed were
  never critical of Amazon in the first place; they don't belong in the
  money/criticism-disconnect framing at all, and their cosponsorship isn't a
  counterexample to anything (a member who never criticized a company
  cosponsoring or not cosponsoring its opposed bill is not informative about
  hypocrisy). That leaves Norcross as the one clearly-critical, money-taking
  member in the cosponsorship-outlier set — and he's the *strongest possible
  confirming case for legislative independence from the money*: sustained,
  specific, repeated criticism (not press-release collision) followed by
  sponsoring the actual fix, on the smallest PAC-adjacent dollar amount
  in the entire 39-member set ($1,000). If a dollar-amount pattern exists at
  all in this data, it points the opposite direction from capture: the
  member who criticized loudest and legislated hardest against Amazon took
  the least money.

## E6 — press-declared bill support beyond formal cosponsorship: Gallego backs WWPA verbally but never cosponsors; Tina Smith's cosponsorship confirmed genuine
- **query/script:** FTS-style `LIKE` search of all 39 members' own
  `press_releases.text` for the bill names/numbers directly (not just
  "Amazon" — the bill itself), across both spellings and all three bill
  numbers (S.4260/H.R.8639/S.2613 for WWPA; S.2992/H.R.3816 for AICOA). This
  is a lower-cost, earlier signal than cosponsorship — a member can state a
  position in a press release without taking the formal step (or before
  taking it), which cosponsorship/vote data alone would miss.
- **result:** AICOA — zero mentions by name/number in any of the 39 members'
  own press releases (the antitrust bill fight is not something these members
  chose to publicize, even the two, Warner/Reed, who turned out to be
  false-positive "critics"). WWPA — 5 releases from 3 members:
  - **Ruben Gallego ($11,000, Senate)** — 2025-12-11, "Gallego Backs Bills to
    Protect Worker Safety and Rights" (release_id=127923): explicit personal
    quote, "I'm proud to support this bill and fight for workers' rights and
    safety" — but **the crosswalk (E4) shows `-` for WWPA_S: Gallego has NOT
    formally cosponsored S.4260/S.2613 as of the 2026-07-08 API pull.** Same
    release also lists "Called on Amazon to explain its mass corporate
    layoffs amid the company's strong financial performance" among his 2025
    labor actions — direct, specific Amazon criticism, not a collision match.
    This is a real instance of the pattern the case is testing: public
    position without the formal legislative step.
  - **Tina Smith ($250, Senate, already a WWPA_S cosponsor per E4)** —
    2024-09-25 and 2024-12-16 releases show sustained, specific, personally-
    authored criticism ("Amazon's mistreatment of workers," "unjust quota
    system," citing a Senate Labor Committee report analyzing Amazon's own
    injury data) tied directly to her own bill. Her cosponsorship (E4) is
    corroborated, not just formal box-checking — this is the case's second
    clean confirming example alongside Norcross, both on the smallest dollar
    amounts in the 39-member set ($250 and $1,000).
  - **Donald Norcross** — same 2 releases already in E3/E5 (bill-introduction
    announcements), no new information, confirms search methodology works.
- **source records:** release_id 127923 (Gallego), 80354 and 75616 (Smith),
  65691 and 112368 (Norcross, already cited). All resolve via
  `press_releases.url`.
- **caveats:** `LIKE` text search on exact bill names/numbers will miss a
  member who refers to the bill only descriptively ("the warehouse safety
  bill") without naming it — this is a floor on the true count of
  position-taking, not a ceiling. Only checked the 39 Amazon-money members,
  not compared against a baseline rate of how often non-Amazon-money members
  do the same (a full novelty/base-rate check would want that comparison —
  flagged for skeptic pass). Gallego's non-cosponsorship as of retrieval
  could reflect timing (S.2613 was introduced 2025-07-31; Gallego's release
  is from 2025-12-11, so there was time to cosponsor and he didn't) rather
  than reluctance — worth noting the gap explicitly rather than assuming
  motive.
- **verdict:** supports, with an important new nuance. Confirms the case's
  central finding two more ways: Smith is now the case's second (not just
  Norcross's) clean example of small-dollar-amount + genuine criticism +
  real legislative follow-through. Gallego adds a *new* wrinkle worth
  flagging in report language: verbal/press support for a bill without the
  formal step exists in this data too — a middle category between "silent"
  and "cosponsor" that plain cosponsorship counts would have missed entirely.
  If this case ships, Gallego's case should be described precisely (backed
  the bill in a press release, did not cosponsor it) rather than folded into
  either "critic" or "cosponsor" bucket.

## E7 — committee-stage action: AICOA was marked up and reported out of Judiciary; WWPA never got a hearing; two Amazon-money Judiciary members are collision-match "critics," not real ones
- **query/script:** congress.gov `/bill/.../actions` and `/bill/.../committees`
  endpoints for all 4 bills (source: `sources/congress-gov-bills.md`); cross-
  referenced against `member_committees_history` in `gain.db` for Amazon-money
  members who sat on House or Senate Judiciary (the committee of jurisdiction
  for both antitrust bills).
- **result:** the two antitrust bills had real committee-stage action the
  warehouse-worker bills never got: **S.2992** was marked up 2022-01-20 and
  reported out of Senate Judiciary 2022-03-02 (favorably, with a substitute
  amendment); **H.R.3816** had two markup sessions (2021-06-23/24) and was
  reported out of House Judiciary 2022-12-21. **S.4260** and **H.R.8639**
  never advanced past "referred to committee" — no hearing, no markup, ever.
  Of the 39 Amazon-money members, only 3 show up on Judiciary in
  `member_committees_history` at all: **Tom Cotton** (Senate Judiciary,
  minority, seen from the earliest snapshot 2022-01-04 — covers the S.2992
  markup), **Ted Cruz** (Senate Judiciary, minority, same coverage), and
  **Sydney Kamlager-Dove** (House Judiciary, minority, first seen 2025-02-02
  — too late to say anything about H.R.3816's 2021 markup). Checked Cotton's
  and Cruz's full Amazon press-mention text (4 and 3 releases respectively):
  all 7 are collision matches, not Amazon-specific criticism — a multi-
  company FTC investigation mention, a release where Cotton's own text
  *favorably contrasts* Amazon against Temu ("Temu directly copies Amazon
  storefronts... knock-off Chinese versions"), TikTok/poppy-seed/TAKE IT DOWN
  Act mentions where Amazon is incidental (a product bought on Amazon, not
  Amazon conduct). Same pattern as Warner/Reed/E5: **no genuine Amazon critic
  among the Amazon-money members who sat on the committee that actually acted
  on the antitrust bill.**
- **source records:** `data/congress_bills/bill_117_s_2992.json`,
  `bill_117_hr_3816.json` (committees + actions); `member_committees_history`
  rows for bioguide C001095, C001098, K000400, committee_id SSJU/HSJU;
  press release_ids 60021, 77939, 84243, 95711 (Tom Cotton, bioguide
  C001095); 16821, 70717, 99206 (Ted Cruz, bioguide C001098) — all via
  `derived_client_press_mentions`, entity_id=125.
- **caveats:** congress.gov's structured API does not expose individual
  committee-markup vote tallies (who voted which way at the committee
  stage) — that would require the committee's own markup transcript/vote
  record, typically an unstructured PDF, out of scope for this pass.
  Committee *membership*, not vote record, is what's actually being measured
  here — sitting on the committee that killed or advanced a bill is a
  position of influence/visibility, not a recorded position. Coverage gap:
  `member_committees_history`'s earliest snapshot is 2022-01-04 (barely
  covers S.2992's 2022-01-20 markup, does NOT cover H.R.3816's 2021-06-23/24
  markup — no Amazon-money House member's 2021 Judiciary seat can be checked
  from this table; would need `legislators-historical.yaml` committee data
  from before the snapshot window, not currently pulled). Only 3 of 39
  members intersect Judiciary at all — this is a small-N check, not a
  population-level test; most of the 39 sit on other committees whose
  markup/hearing history on these bills has not been pulled (Commerce,
  Small Business, HELP for WWPA's actual committee — but WWPA never had a
  hearing there either, so that's moot for this case's 2 target bills).
- **verdict:** supports, modestly (small N). Extends E5's finding one more
  step down the influence chain: not just press mentions, but committee
  *seats* — the two Amazon-money members positioned to act on the antitrust
  bill Amazon opposed were never real Amazon critics either. Consistent with
  the case's overall shape so far: wherever criticism is genuine (Norcross,
  Smith, and to a lesser extent Gallego), it comes from members with no
  particular institutional leverage over the bill in question; wherever
  members had institutional position (Judiciary seat, or the largest dollar
  amounts), the "criticism" turns out to be a press-mention artifact, not a
  real position.

## E8 — Gallego's other top corporate donors get no criticism; Amazon (and one nuclear-energy donor) are the exceptions, in opposite directions
- **query/script:** identified Gallego's top ~40 distinct contributing
  registrants by deduped FECA dollars (same dedup pattern as screen 40's
  `money` CTE — distinct contributor/payee/date/amount tuples per registrant,
  to avoid the raw-summing inflation bug documented in screen 40); searched
  his own press releases (506 total in corpus) for mentions of the
  identifiably-corporate ones (excluding law/lobbying/PR firms acting as
  registrant-of-record, unions, and trade associations, where the registrant
  isn't the actual funding company) — Pinnacle West, Honeywell, KPMG,
  Fresenius, General Dynamics, Deloitte, General Atomics, Elevance Health,
  Altria, Cigna, Northrop Grumman, Charter Communications, Synchrony, plus
  Amazon for comparison.
- **result:** Amazon ranks **60th of 482** distinct registrants giving to
  Gallego by dollar amount ($11,000) — a small, unremarkable slice of a very
  broad donor base, not a standout relationship by size. Of his other
  top-40 identifiable corporate donors, **12 of 13 got zero mentions** in his
  506 press releases (Honeywell, KPMG, Fresenius, General Dynamics, Deloitte,
  General Atomics, Elevance Health, Altria, Cigna, Northrop Grumman,
  Synchrony; Charter Communications' one apparent hit was a false-positive
  substring match on "political spectrum"). The one exception, besides
  Amazon, is **Pinnacle West Capital Corporation / APS** ($45,000 — his
  **2nd-largest** identifiable corporate donor, 4x Amazon's amount): two 2026
  releases (135182, 136106) where Gallego introduces a bipartisan nuclear-
  investment bill (the ARC Act, with Sen. Risch of Idaho).
  **CORRECTION (same session, on closer read of the full release text):**
  the "APS praise" is **not Gallego's own words** — it's a supportive quote
  from APS's own CEO, Ted Geisler, embedded in an omnibus "what industry is
  saying" release alongside **13 other organizations quoted just as
  favorably** (Third Way, ClearPath, Nuclear Energy Institute, American
  Public Power Association, U.S. Chamber of Commerce, IBEW, Holtec
  International, Clean Air Task Force, Building Trades Unions, Nuclear
  Innovation Alliance, U.S. Nuclear Industry Council, Idaho National
  Laboratory, and Arizona's other major utility SRP). Gallego's own quote in
  the introduction release (135182) never names APS or Pinnacle West at all
  — it's generic nuclear-policy language. This reads as standard
  bipartisan-bill-launch messaging (round up every stakeholder's supportive
  quote) applied to a national energy bill, not evidence Gallego is
  specifically boosting his donor. The boring explanation (a national
  bipartisan bill drawing broad industry support, of which APS is one of
  ~14 voices, is not the same as Gallego personally praising his donor) is
  strong here and was not adequately tested before the first draft of this
  evidence block was written — flagged and corrected before it reached a
  lead.
- **source records:** registrant-dollar rollup via `senate_contribution_items`
  joined through `honoree_member_map` (bioguide=G000574, confidence>=0.9) and
  `senate_contribution_filings`; press release_ids 135182 ("Gallego, Risch
  Introduce Bill to Accelerate New Nuclear Investment"), 136106 ("What Are
  They Saying: Gallego, Risch Nuclear Bill is Critical...") for the Pinnacle
  West praise; release_id 100066 (incidental Amazon collision — a
  crib-shortage anecdote) and **126102** — Gallego's own letter to Amazon CEO
  Andy Jassy demanding accountability for mass layoffs ("Amid Expected
  Record-Breaking Cyber Monday Sales, Gallego calls on Amazon to Explain Mass
  Layoffs," 2025-12-01). **Correction:** release 126102 IS present in
  `derived_client_press_mentions` (verified directly:
  `SELECT * FROM derived_client_press_mentions WHERE release_id=126102`
  returns it, entity_id=125) — an initial read of this session mistakenly
  flagged it as missing from that table based on an incomplete recall of
  E4/E5's earlier (narrower) query path, not an actual gap. No undercount
  bug in the derived table; struck the incorrect claim rather than letting
  it stand.
- **caveats:** the "top 40" cutoff and the exclusion of law-firm/union/trade-
  association registrants from the search set were judgment calls, not a
  formal rule — a full pass would search all 482 registrants' underlying
  client identities, not just the ones with obviously corporate names. This
  is a single-member case study (N=1 legislator, ~14 donors checked), not a
  population-level test of "do members criticize small donors and praise big
  ones" — worth being explicit that this doesn't generalize past Gallego
  without checking other members the same way. **Methodological trap caught
  during this pass:** a naive `LIKE '%APS %'` search for Pinnacle West's
  trade name matched false positives via substring collision (e.g. "gAPS "
  inside "gaps") across ~18 unrelated releases before the pattern was
  tightened to word-boundary punctuation (`queries.sql#q9`) — same failure
  mode as the "UBS"/"Spectrum" false positives caught earlier in this
  session. Any future short-acronym donor-name search in this corpus needs
  word-boundary-safe LIKE patterns or a regex-capable check, not a bare
  substring match; verify every candidate hit by reading it before citing.
- **verdict:** supports (Amazon-specific finding), Pinnacle West thread
  demoted to weak/unconfirmed. Confirms the core point: 12 of 13 other
  corporate donors get total silence from Gallego, so his genuine, repeated
  Amazon criticism isn't just background noise or "how he talks about any
  donor" — it stands out even against his own record. But the Pinnacle
  West/APS "say-for-pay" reading does NOT survive a close read of the source
  text — it's a national bill with broad industry backing, APS is one
  supportive voice of many, and Gallego's own words never single the company
  out. **Not logged as a separate lead** — fails the boring-explanation gate
  on its own, before any novelty check. Kept here only as a caveat on E8's
  "12 of 13 silent, 1 exception" framing: the honest count is 13 of 13
  Gallego shows no personal, donor-specific favoritism toward — Amazon
  remains the sole case where his own words single out a specific donor by
  name, and that's critical, not favorable.

## E9 — filing-level check on Norcross/Smith contributions: Smith's "$250 from Amazon" is not Amazon money; Norcross's $1,000 confirmed genuine; Gallego's $11,000 checked against the Arizona-employer boring explanation
- **query/script:** `queries.sql#q10` (contribution-level detail, not just
  the honoree-level dollar rollup used everywhere else in this case);
  `queries.sql#q11` (Mark Kelly comparison); `queries.sql#q12` (39-member
  set dollar distribution by chamber).
- **result — Norcross:** exactly one contribution, `contributor_name` =
  "AMAZON.COM SERVICES LLC SEPARATE SEGREGATED FUND (AMAZON PAC)" — the
  actual corporate PAC — $1,000 direct to "DONALD NORCROSS FOR CONGRESS,"
  2022-04-15. Genuine corporate PAC money, confirmed.
  **Result — Smith:** the $250 item has `contributor_name = 'SELF'`, payee
  "VELVET HAMMER PAC" (Smith's own leadership PAC), filed under
  `filer_type='lobbyist'` (lobbyist_id resolves to Kasia Witkowski, an
  Amazon-registered in-house lobbyist). This is an **individual's personal
  political donation**, disclosed on Amazon's LD-203 filing only because
  LD-203 requires registered lobbyists to report their own personal FECA
  giving alongside the company PAC's — not because Amazon-the-company gave
  Smith money. **Smith should be removed from this case's list of
  "Amazon-money-taking critics."**
  **Result — Gallego, re-verified:** 4 separate contributions, all
  `contributor_name` = the actual Amazon PAC (not an individual), to
  "GALLEGO FOR ARIZONA" ($1,000 2022-07-26; $2,500 2022-10-24; $2,500
  2023-01-11) and "JUNTOS PAC" ($5,000 2025-04-22, likely a Gallego-
  affiliated PAC — not independently verified in this pass). Genuine
  corporate PAC money, confirmed, spanning his House-to-Senate transition
  and continuing after his public Amazon criticism began (the 2025
  contribution postdates his earlier critical mentions).
  **Result — Arizona-employer boring explanation:** Arizona's other senator,
  Mark Kelly (bioguide K000377), received **zero dollars** from Amazon PAC
  in this dataset — arguing against "Amazon rewards Arizona senators as a
  courtesy to a major in-state employer" as the explanation for Gallego's
  amount. But the amount doesn't need that explanation to be unremarkable
  anyway: **$11,000 is exactly the median** Amazon PAC contribution among
  the 39-member Senate subset (range $250–$38,200, n=21) — not a small
  amount by this case's own standards, but not a large or targeted one
  either.
- **source records:** contribution items via `senate_contribution_items`
  joined to `senate_contribution_filings` (registrant_id=54494), filtered to
  `contributor_name` and `filer_type` fields not previously inspected at
  this granularity in E1/E4/E6/E8 (those all worked from the honoree-level
  dollar aggregate). Kelly comparison via `honoree_member_map` for
  bioguide=K000377 (19 honoree name variants, zero matching Amazon-PAC
  contribution rows).
- **caveats:** this check was only run for Norcross, Smith, and Gallego —
  the other 36 of the 39-member set have NOT been checked at this
  contribution-level granularity, meaning the same `contributor_name='SELF'`
  individual-lobbyist trap could be inflating other members' apparent
  "Amazon money" totals throughout E1-E8 without having been caught. This is
  a corpus-level methodological gap, not specific to this case — worth
  flagging to whoever maintains screen 40 and the `money` CTE pattern more
  broadly, since the existing dedup logic (documented in queries.sql/screen
  40) guards against double-counting but not against this SELF/individual-
  contributor conflation.
- **verdict:** materially changes the case. Removes Smith as a confirming
  case entirely (she was never an Amazon-money recipient). Confirms Norcross
  and Gallego's amounts are genuine but reveals both were smaller/more
  unremarkable than the case's earlier framing implied — Norcross's $1,000
  is trivial by any standard, and Gallego's $11,000, while real, is exactly
  median for this set, not an outlier. The Arizona-employer explanation is
  checked and not confirmed (Kelly got nothing), but the underlying
  observation it was meant to explain (Gallego's dollar amount) turns out
  not to need explaining — it was never unusual to begin with. Net: the
  case's surviving finding is narrower and weaker than previously stated —
  see case.md Verdict for the full reassessment and recommendation.

## E10 — builder/skeptic/judge tribunal: SELF-trap checked corpus-wide (catches Angie Craig), two more genuine critics found among WWPA_HR cosponsors (Pallone, Stansbury)
- **query/script:** `queries.sql#q13` (SELF/individual-lobbyist trap across
  full 39-member set, independent re-derivation of E9's contribution-level
  check); `queries.sql#q14` (press mentions for WWPA_HR cosponsors not
  previously checked against E1's critic list: Pallone, Thompson, Gomez,
  Stansbury).
- **result — SELF-trap, corpus-wide:** of 39 members, two have Amazon
  contribution totals that are *entirely* SELF/`filer_type='lobbyist'` money,
  not corporate PAC: **Tina Smith** ($250, already excluded per E9) and
  **Angie Craig** ($6,200, both contributions dated 2022-03-09/2023-06-05,
  same `lobbyist_id=56820` — one individual's personal giving, not the
  Amazon PAC). Craig was cited in E4 as an AICOA_HR cosponsor among the
  money-taking set; she should be removed from that tally the same way Smith
  was removed from the confirming-critic tally. Every other member's total,
  including Norcross's $1,000 and Gallego's $11,000, is confirmed
  independently as genuine `filer_type='organization'` PAC money (re-derived
  directly from `senate_contribution_items`, not read from prior evidence
  blocks).
- **result — WWPA_HR cosponsor cross-check:** E5 cross-referenced AICOA's two
  cosponsors (Warner, Reed) against E1's critic list and found neither was a
  genuine critic — but the same check was never run in the other direction,
  against WWPA_HR's cosponsor list (Pallone $15,000, Thompson $6,000, Gomez
  $5,000, Stansbury $1,000, plus Norcross as sponsor, already known). Pulled
  full press-mention lists for all four unchecked names via
  `derived_client_press_mentions`, entity_id=125: **Pallone** — "Pallone
  Demands Online Marketplaces Remove Dangerous, Recalled Products Linked to
  Infant Deaths" (2023-08-29, release already cited in E1 as a genuine
  critical mention) — genuine, on-topic, and he cosponsored H.R.8639 in 2024.
  **Stansbury** — "Rep. Stansbury, Labor Caucus Urges Amazon to Respect its
  Employees' Rights and Requests Information From the Company About its
  Anti-Union Activities" (2024-10-24) — genuine, on-topic, and she
  cosponsored H.R.8639 in 2024. **Gomez** — 2 mentions, both tax-policy
  releases (child tax credit, taxing the ultra-wealthy), no Amazon-specific
  criticism — not a genuine critic. **Thompson** — 2 mentions, an unrelated
  federal-grant announcement and a general "tech giants/mega
  corporations/crypto companies" demand letter not specific to Amazon's
  labor conduct — not a genuine critic.
- **result — dollar-gradient check:** listing all 39 members by dollar rank
  against AICOA/WWPA cosponsorship status (both chambers) shows no gradient:
  WWPA_HR cosponsors span $1,000 (Norcross, Stansbury) to $15,000 (Pallone);
  the two AICOA_S cosponsors are the two largest-dollar recipients in the
  entire set (Warner $38,200, Reed $25,750) but were already established
  (E5) as non-genuine critics, so their cosponsorship isn't informative about
  money buying deference from critics — it's simply not a data point about
  criticism at all.
- **source records:** `senate_contribution_items`/`senate_contribution_filings`
  re-derived directly for all 39 bioguides (registrant_id=54494,
  contribution_type='feca', honoree_member_map confidence>=0.9); press
  release_ids for Pallone (already cited E1), Stansbury (new — pull via
  `derived_client_press_mentions` bioguide_id=S001218, entity_id=125), Gomez
  and Thompson (new, ruled out) — all resolve via `press_releases.url`.
- **caveats:** this cross-check was still limited to the 39-member,
  entity_id=125-linked set and to exact bill-name/text matches (same
  limitation as E1/E6) — a member who criticizes Amazon's labor practices
  without the FTS/LIKE pattern catching it, or without a press release at
  all, would not surface here. N=4 genuine on-topic critics is still a small
  sample; cosponsorship remains a low-cost signal (neither bill got a floor
  vote). The reframed finding is a *reverse* result (no suppression detected)
  rather than a *positive* capture finding — reverse/null results are weaker
  news hooks than positive findings even when equally well-sourced, worth
  flagging for editorial judgment on whether this clears the bar as its own
  short piece.
- **verdict:** supports a reframed claim, refutes the original one. The
  original hypothesis (money buys silence/deference) does not survive: the
  full set of genuine on-topic critics (4, not 1) shows uniform legislative
  follow-through, not selective suppression correlated with dollar amount.
  Corrects E4's AICOA_HR cosponsor tally (removes Craig, same SELF-trap as
  Smith). This is the tribunal's judged verdict — see case.md Verdict for
  the full writeup and status change (`parked` → `open (reframed)`,
  confidence low → medium).
