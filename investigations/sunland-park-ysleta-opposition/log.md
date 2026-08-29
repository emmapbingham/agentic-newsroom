## 2026-07-01 — case opened, promoted from leads

- did: Promoted lead `sunland-park-blocks-ysleta-gaming-bill` (newsroom.db
  `leads` table, `screen_run_id=17`, `quiet-issue-quadrant` screen re-run
  against the expanded 73-code ISSUE_KEYWORDS map). Lead surfaced while
  drilling GAM (Gaming/Gambling/Casino), the corpus's dominant lobby-to-press
  outlier this session (17.0x, z=5.08), specifically the tribal-gaming
  sub-cluster within it. Set `promoted_at` + `case_slug` in `newsroom.db`.
  Created case files (case.md, evidence.md, log.md, queries.sql,
  analysis/, derived/).
- did: Ran q1 (stance-tagged client/registrant list on H.R.2208/S.4196 →
  H.R.2873/S.1536), q2 (Sunland Park's full filing_uuid list), q3 (verbatim
  opposition text by quarter), q4 (Sunland Park's registrant), q5 (Ysleta/
  Alabama-Coushatta's registrants), and an ad hoc press_fts check on
  "Sunland Park" (not yet formalized as q6 in queries.sql — do that next
  session).
- found: See E1–E4 in evidence.md.
  - E1: Sunland Park is the only filer with explicit sustained opposition
    language; Boyd Gaming/Landry's track the bill but do not state a stance —
    important, don't conflate them with Sunland Park in the writeup.
  - E2: Opposition is continuous, 14 filing_uuids, 2022 Q3 – 2025 Q4, no gap.
  - E3: Sunland Park's stated motive is specific — fear that the bill would
    eventually force Texas into Class III gaming-compact negotiations,
    creating a new casino competitor.
  - E4: **Corrected the lead's premise.** The original lead said "zero press
    coverage of Sunland Park's role" — checking `press_fts` for "Sunland
    Park" actually returns 21 hits, not zero. All 21 are geographic
    references to the border town (immigration/border-security press
    releases, mostly Rep. Gabe Vasquez's district) — none are about the
    casino or this lobbying fight. The underlying claim survives but had to
    be re-stated precisely: "zero coverage of Sunland Park's casino/lobbying
    role," not "zero mentions of Sunland Park." This is exactly the kind of
    imprecise-claim risk the skeptic checklist exists to catch — caught it
    myself this time before it went further, but flagging for the skeptic
    pass to double check.
- dead ends: none yet — this is the first drilldown session.
- open questions:
  1. Has H.R.2208/S.4196/H.R.2873/S.1536 ever had a committee hearing, markup,
     or floor vote, in any Congress since 2022? This is the single most
     important unanswered question — it's the crux of confirms-vs-refutes
     (E5, congress.gov, external to gain.db).
  2. House LDA filings not yet cross-checked (E6) — could add clients or
     corroborate Senate-only findings.
  3. Sunland Park's corporate ownership/affiliations not yet researched (E7).
  4. Sunland Park's first opposition filing is 2022 Q3, not Q1/Q2 — worth
     checking whether the bill was introduced by Q3 2022 (reactive lobbying)
     or Sunland Park simply started later for unrelated reasons.
  5. Full news-media novelty scan still owed (only checked the press_releases
     corpus, which is member press releases, not general news).
- NEXT: Pull H.R.2208/H.R.2873's legislative history from congress.gov (E5) —
  this is the fact that determines whether "opposition may be causally
  effective" is even a defensible claim, or whether low legislative priority
  alone explains the stall. Do this before any builder→skeptic→judge pass.

## 2026-07-01 — E5 pulled: legislative history reframes the case (causality still unproven)

- did: Pulled legislative history for the bill across all four Congresses
  it's existed in (116th H.R.759 → 117th H.R.2208/S.4196 → 118th
  H.R.2873/S.1536 → 119th H.R.3723/S.2564, still pending). Attempted direct
  WebFetch of congress.gov `/all-actions` pages and govtrack.us bill pages
  first — both returned **HTTP 403 to every request**, so this had to be
  reconstructed from WebSearch snippets plus govinfo.gov bill-status pages
  (govinfo did fetch successfully; it's an official GPO source but its
  bill-status view is thinner than congress.gov's full action log).
- found: See E5 in evidence.md for full table + sourcing. Headline: the bill
  **passed the House unanimously twice** — 116th Congress (H.R.759, 2019) and
  117th Congress (H.R.2208, 2021-05-12) — with no opposition on record in
  the corpus at that point. Sunland Park's opposition filings begin 2022 Q3,
  *after* both House passages. Since then (118th and 119th Congress), the
  bill has stalled at committee referral both times — no hearing or markup
  found in either chamber, and the Senate side (S.4196/S.1536/S.2564) has
  **never**, in any Congress, gotten committee action at all.
- editorial decision (per user, 2026-07-01): **do not go in hard on
  causality.** The timing (opposition begins right when House momentum
  stops) is a notable coincidence worth reporting, but this data cannot
  prove Sunland Park's lobbying is *why* the bill stalled — leadership
  priorities, unrelated must-pass-vehicle fights, or Senate Indian Affairs'
  general throughput on this class of bill could equally explain it. Frame
  as "notable timing, unproven mechanism," not "Sunland Park blocked the
  bill." Updated case.md's confirms/refutes section and Verdict to reflect
  this explicitly.
- caveat needing human help: **congress.gov/govtrack.us block automated
  fetches (403).** E5's timeline is built from search snippets + govinfo.gov,
  not read first-hand off congress.gov's canonical "All Actions" log. Before
  this evidence is relied on for publication, someone needs to manually open
  each bill's All Actions tab in a browser and confirm nothing (a hearing,
  a markup, a committee vote) is missing from this reconstruction. Full list
  of URLs to check is in case.md's "Sources / legal-risk notes" section. If
  you (Emma) can grab the raw HTML or a copy-paste of each All Actions table
  and drop it in as a file, or paste the action list directly into the chat,
  that would let this get verified without needing a fetch method that
  bypasses the block.
- open questions added: Does Senate Indian Affairs generally have low
  committee throughput for tribal-recognition-adjacent bills (a base rate
  that alone could explain the Senate-side stall), or is this bill
  specifically stuck? Needs a comparison set of similar bills referred to
  that committee in the same period — not yet built.
- NEXT: Either (a) get E5 verified against congress.gov directly (see above),
  or (b) move to E6 (House LDA cross-check) / E7 (ownership research) while
  that verification is pending. No builder→skeptic→judge pass until E5 is
  confirmed, since it's now the case's central piece of external evidence.

## 2026-07-01 — E5 confirmed: Emma supplied congress.gov's actual All Actions data

- did: Emma manually pulled the "All Actions" table for every bill directly
  from congress.gov (browser access isn't blocked, only the automated fetch
  was) and dropped it in as `congress_all_actions.csv` in this case
  directory. Read the file and rewrote E5 in evidence.md against this
  authoritative source, replacing the earlier WebSearch-reconstructed
  version.
- found: The confirmed record sharpens the picture:
  - **H.R.759 (116th, 2019)** went through the full formal process — House
    Natural Resources → subcommittee → **markup, ordered reported by voice
    vote** (06/19/2019) → reported (H.Rept. 116-165) → **passed House by
    voice vote** (07/24/2019) → received in Senate → referred to Senate
    Indian Affairs almost 5 months later (12/17/2019) → nothing further.
  - **H.R.2208 (117th, 2021)** passed the House just 6 days after subcommittee
    referral (05/12/2021) via suspension of the rules — **no formal markup
    on record this time**, meaning the House can and does fast-track this
    exact bill without a markup step. Companion S.4196 went nowhere.
  - **H.R.2873/S.1536 (118th)** and **H.R.3723/S.2564 (119th, current)**:
    confirmed, directly from congress.gov, that neither chamber has held so
    much as a subcommittee markup on any version since 2021 — House side
    stops at subcommittee referral, Senate side stops at committee referral.
  - This means the one House passage that happened *after* Sunland Park's
    opposition could have started (there wasn't one — 2021 predates 2022 Q3)
    is moot; the relevant fact is that the process hasn't restarted *at all*
    since Sunland Park began opposing, not even to the informal degree 2021
    required.
- editorial note: reaffirmed the 2026-07-01 decision not to lean on
  causality — this is now a confirmed timing correlation (strong), not a
  proven mechanism. Updated case.md's confirms/refutes section, Verdict, and
  sources/legal-risk section to remove "provisional pending verification"
  language now that E5 is directly sourced.
- NEXT: E6 (House LDA cross-check) or E7 (Sunland Park ownership research).
  Consider whether a builder→skeptic→judge pass is warranted now that E5 is
  confirmed, even with E6/E7 still open — check with Emma on sequencing.

## 2026-07-01 — E6 and E7 done: House data corroborates, ownership context added

- did: E6 — joined Sunland Park's registrant (Landon Fulmer, id 401104304,
  found via the Senate↔House bridge) against `house_filings`; found Sunland
  Park itself also files House LD-2s, starting the same quarter (2022 Q3) as
  the Senate side. Pulled verbatim House opposition text (queries.sql q9) and
  re-ran the "who else opposes" sweep on House data (q10), mirroring q1.
  E7 — external research (WebSearch/WebFetch) on Sunland Park's corporate
  ownership and Landon Fulmer's other client relationships.
- found (E6): House filings **independently corroborate** E1–E3 — same
  verbatim opposition language in a second disclosure regime, no new
  opponent surfaces (the House sweep initially returned 6 other "OPPOSE"
  clients, e.g. American Federation of Government Employees, but all 6 are
  confirmed false positives from bill-number digit collisions — e.g. AFGE's
  hit is "S. 2873," the unrelated Protect Americas Workforce Act, not the
  tribal-gaming H.R.2873; false-positive rate was actually worse on House
  data than Senate). Boyd Gaming/Landry's track the bill on the House side
  too, still with no explicit stance — matches E1. **New gap found:** no
  2023 Q1 filing for Sunland Park in either chamber — first gap in the
  "continuous opposition" claim, not yet explained. Also: Ysleta del Sur/
  Alabama-Coushatta House filings extend through 2026 Q1, later than the
  Senate pull — worth a follow-up Senate re-check for parity (q11, not yet
  run).
- found (E7): Sunland Park was owned by the **Fulton family** (individual
  owner Stan Fulton, died 2018, family retained ownership) for the entire
  span of the opposition campaign. In **October 2025** — right in the middle
  of the Q3/Q4 2025 filing window — the property sold: real estate to
  **Gaming and Leisure Properties Inc.** (GLPI, a Pennsylvania gaming REIT),
  operations to **Strategic Gaming Management LLC**. Opposition filings
  continued unbroken through and past the sale (2025 Q4 filed as usual).
  Deal-value figures differ across sources ($184M vs. $301M) and are not
  reconciled — flagged as needing a primary-source check (SEC/GLPI filings,
  NM Gaming Control Board) before quoting either number. Landon Fulmer
  confirmed as a self-employed independent lobbyist with unrelated other
  clients (hospitals, an EV company) — no employment/equity tie to Fulton
  family found, standard paid-lobbyist relationship.
- editorial note: E7's ownership-change fact is notable but cuts against, not
  for, a "one owner's grudge" framing — the opposition survived a full
  ownership change, which (if anything) makes the stated competitive-threat
  rationale (E3) look more durable/institutional than personal. Flagging for
  the skeptic pass rather than asserting either way.
- open questions added: (1) why no 2023 Q1 filing in either chamber — was
  there a lull in bill activity that quarter, or something else; (2) whether
  post-sale (2026 Q2+, not yet in the corpus) filings show the new owner
  continuing the campaign, which would be worth checking again once that
  data exists; (3) reconcile the Senate/House filing-period mismatch at the
  tribes' end (2025 Q4 vs. 2026 Q1).
- NEXT: Reconcile E7's deal-value figures against a primary source if this
  goes to publication. Otherwise, case is ready for a builder→skeptic→judge
  verification pass — check with Emma on whether to run that now or pursue
  the fee-to-trust side-thread (`localgov-fee-to-trust-monitoring`) first.

## 2026-07-02 — E8: novelty scan finds Sunland Park's role is unreported, but the "why does it stall" mystery already has a different, published answer

- did: Ran the case's novelty scan, requested by Emma to cover Congressional
  press releases (in-corpus, all years available) plus external news
  (national + El Paso/NM regional), tribal/Native press, gaming-industry
  blogs/forums, and Congressional Record floor statements, going back to the
  late 2010s. In-corpus part done directly (press_fts queries against
  `press_releases`, see queries.sql-equivalent in evidence.md E8). External
  part delegated to a forked research agent (WebSearch/WebFetch) since it
  spanned many source categories and the raw search output wasn't worth
  keeping in the main session.
- found: In-corpus (2022-01-01 to 2026-03-31 — the full extent of
  `press_releases`, cannot reach further back): only 4 relevant releases,
  all bill-introduction announcements (Luttrell 2023/2025, Escobar
  2023/2025) — zero mentions of Sunland Park, opposition, or the bill
  stalling, in any year the corpus covers.
  External scan's central finding, after Emma's follow-up question about
  story dates: **every substantive prior-coverage item found is old** —
  either 2019-2020 (the Cornyn/Texas-state-government fight over H.R.759)
  or 2008-2011 (Sunland Park's unrelated, already-reported opposition to two
  *other* tribal casino proposals, the Chaparral and Jemez Pueblo bids, via
  a different lobbyist, Scott Scanland). **Nothing was found from 2021 to
  the present** — a six-year gap spanning H.R.2208's 2021 House passage, the
  118th Congress cycle, and the currently-pending 119th Congress bill.
  Two load-bearing facts from the 2019-2020 coverage:
  - Sen. Cornyn sent a letter asking Senate Indian Affairs to hold off on
    H.R.759, after telling the tribe's chairwoman in May 2019 he'd support
    it if it passed the House — a reversal, reported as such by KETK.
  - The stated reason, per Indianz.com: concerns from Gov. Abbott, Lt. Gov.
    Patrick, and AG Paxton rooted in Texas's own gambling restrictions.
  This is a **named, on-record, already-published explanation** for why the
  Senate side has never advanced any version of this bill — independent of,
  and predating, Sunland Park's 2022 Q3 opposition start.
  Confirmed still true after the scan: **no reporting anywhere connects
  Sunland Park to this specific bill (H.R.2208 onward)** — checked national,
  regional, tribal, and gaming-trade press, plus blogs/forums/Reddit and the
  Congressional Record. That part of the novelty claim survives.
- editorial exchange: Emma asked directly whether the found coverage was
  mostly ~2019, correctly suspecting the case's framing needed updating
  rather than abandoning. Reframed the hypothesis and newsworthiness
  sections in case.md accordingly: not "why does this bill mysteriously
  stall, maybe Sunland Park," but "this fight's press coverage stopped in
  2019-2020 under a different opponent; six years and three reintroductions
  later, a second, quieter, never-reported actor has been working against
  it the whole time, continuously, through a full change of its own
  ownership — an update story, not an unmasking." Also flagged that
  Sunland Park's opposition pattern itself is old (2008-2011), so the
  "institutional actor doing what it's always done" framing is more honest
  than "newly discovered opponent."
- source records (full list also in case.md "Prior coverage" and
  evidence.md E8): Cornyn/Texas angle —
  https://www.ktre.com/2019/10/16/sen-cornyn-sends-letter-opposing-alabama-coushatta-tribes-gaming-facility/,
  https://indianz.com/IndianGaming/2020/01/27/alabamacoushatta-tribe-turns-to-congress.asp,
  https://www.ketk.com/news/support-for-alabama-coushatta-grows-despite-cornyn-going-back-on-his-word/.
  Sunland Park's older pattern —
  https://www.santafenewmexican.com/news/local_news/feds-reject-pueblos-proposal-for-off-reservation-casino/article_3ce8ecd2-49e3-5445-bb2f-36cae936fb58.html,
  https://www.abqjournal.com/9671/updated-mescalero-apache-tribe-sunland-park-racetrack-object-to-proposed-jemez-casino.html.
- caveats: the external scan was bounded (WebSearch/WebFetch, freely
  indexed sources only) — not an exhaustive paid-archive search (no
  ProQuest/Nexis/newspapers.com), so "nothing found 2021-present" should be
  read as "nothing found in what's freely searchable," not an absolute
  negative. Also not yet checked: whether Cornyn's or Texas state
  government's 2019 objection is still active/current as of the 118th/119th
  Congress — if so, that's a second, more powerful "boring explanation"
  candidate for the Senate-side stall specifically (though it wouldn't
  explain the House-side stall since 2021, which the Cornyn angle says
  nothing about).
- NEXT: Consider whether to pursue confirming Cornyn/Texas's position is
  still current before further writeup. Case is otherwise ready for a
  builder→skeptic→judge verification pass, with the hypothesis now
  correctly scoped as "Sunland Park's specific opposition is unreported,"
  not "Sunland Park may explain why this keeps failing."

## 2026-07-01 — related thread noted from newsroom fishing (not yet drilled)

- did: While fishing the `quiet-issue-quadrant` screen further (run 17, same
  run this case was promoted from), found a structurally related pattern
  while checking base rates on local-government lobbying: 17 distinct
  cities/counties (Alaska fishing towns — Petersburg, Wrangell, Unalaska,
  King Cove; California counties — San Diego, Sonoma, Napa; Washington
  counties — Yakima, Pierce; Pinal County, AZ; others) lobby Congress
  specifically on Indian/Native American Affairs (issue code IND), almost
  entirely fee-to-trust and tribal land-transfer bills. Logged to
  `newsroom.db` as lead `localgov-fee-to-trust-monitoring`
  (screen_run_id=17) — not yet promoted or drilled in this case.
- found: This is the **same underlying legal mechanism** this case turns on
  (land placed into federal trust for a tribe, sometimes enabling gaming) —
  but seen from local government's side rather than a rival casino's.
  San Diego County's filings specifically and repeatedly track the Pala Band
  of Mission Indians Land Transfer Act and "Jamul Land Trust issues" — a
  live, named, recurring county-level fee-to-trust concern, not a one-off.
  Most language across the 17 is "monitor," not explicit "oppose" — weaker
  than Sunland Park's stance, so don't assume adversarial intent without
  checking each one's actual language the way E1/E3 did for Sunland Park.
- open questions: Is Sunland Park's opposition part of a broader pattern of
  local/competitive resistance to fee-to-trust generally, or is it sui
  generis (a commercial competitor's narrow self-interest, distinct from
  county governments' tax-base/jurisdiction concerns)? Worth checking
  whether any county actually opposes (not just monitors) a fee-to-trust
  application, and whether any county's opposition targets the *same*
  Ysleta del Sur / Alabama-Coushatta bill this case is about, or only
  unrelated tribes' land transfers elsewhere.
- NEXT (after E5, the legislative-history pull): check whether any El
  Paso-area or New Mexico county government shows similar fee-to-trust
  monitoring/opposition alongside Sunland Park's — would strengthen or
  complicate the "single identified opponent" framing at the heart of this
  case's newsworthiness. If county-level fee-to-trust opposition turns out
  to be a broader, unrelated pattern nationally, that's a separate
  companion piece, not a dilution of this case's specific claim.

## 2026-07-02 — E9: Cornyn's 2019 hold is stale, but Paxton's Senate run makes this newly timely

- did: Emma asked directly whether the 2019 Cornyn/Texas objection found in
  E8 is still the operative reason the bill isn't moving. Delegated to a
  forked research agent (WebSearch/WebFetch) to check Cornyn's current
  committee assignments and statements, Texas state government's current
  position, Senate Indian Affairs Committee's current leadership/activity,
  and whether the 2022 Supreme Court ruling changed the landscape.
- found: The specific 2019 mechanism (Cornyn's committee hold) is stale —
  he's not on Senate Indian Affairs anymore (Finance/Judiciary/Intelligence/
  Foreign Relations/Budget instead), and has said nothing about any
  successor bill (H.R.2208, H.R.2873/S.1536, H.R.3723/S.2564) since 2019-
  2020. But the underlying opposition hasn't softened — it's sharpened and
  personalized: **Cornyn lost the 2026-05-26 Texas GOP Senate primary
  runoff to Ken Paxton**, 63.8%-36.2%. Paxton was one of the three officials
  (with Abbott and Patrick) cited in the original 2019 objection, and has
  since, as sitting AG, **personally led litigation against Ysleta del
  Sur's Speaking Rock casino**, winning a court ruling calling the tribe's
  gaming "illegal activity." He's now the Republican Senate nominee for
  Cornyn's seat, facing Talarico in November 2026. Senate Indian Affairs
  is now chaired by Murkowski/Schatz, no connection to Texas politics found,
  no committee action on S.2564 (matches E5). The 2022 Supreme Court win
  for the tribes covers narrower bingo-style gaming, not full IGRA/Class
  III status — hasn't mooted the bill's purpose.
- editorial reaction (Emma): this "definitely adds to the update angle and
  would make the story quite timely" — agreed, wrote up as E9 in
  evidence.md and folded into case.md's newsworthiness section as the
  story's live electoral hook: the seat that once held a comparatively soft
  "hold on state concerns" position may soon belong to the tribes' most
  aggressive personal legal adversary, while Sunland Park has quietly
  worked the same side of the issue via federal lobbying the whole time.
- caveats flagged: Paxton is a sitting AG and active Senate candidate —
  his documented position is the Speaking Rock litigation (existing
  bingo-gaming dispute), not a direct statement on the pending federal bill;
  don't characterize him as opposing H.R.3723/S.2564 specifically without
  his own words on it. November 2026 election outcome not yet known —
  keep any writeup dated and clear this is developing. Added a legal-risk
  note in case.md's sources section specifically flagging Paxton's
  candidacy as requiring extra care.
- source records: https://www.cornyn.senate.gov/about/about-john-cornyn/ ;
  https://www.texastribune.org/2026/05/26/texas-john-cornyn-ken-paxton-us-senate-republican-primary-runoff/ ;
  https://www.houstonpublicmedia.org/articles/news/politics/election-2026/2026/05/26/552722/paxton-cornyn-runoff-election-results-texas-senate-republican-primary/ ;
  https://www.texasmonthly.com/news-politics/tigua-indian-tribe-loses-yet-another-court-fight-to-keep-speaking-rock-casino-open/ ;
  https://nativenewsonline.net/sovereignty/senate-indian-affairs-committee-shifts-leadership-for-119th-congress ;
  https://elpasomatters.org/2022/06/15/u-s-supreme-court-sides-with-el-pasos-tigua-tribe-in-decades-long-gambling-fight-with-texas/
- NEXT: Case now has E1-E9. Ready for a builder→skeptic→judge verification
  pass — check with Emma on timing given this is now genuinely time-
  sensitive (the election context could shift). Also still open: the
  fee-to-trust side-thread, E7's deal-value reconciliation, and confirming
  whether Paxton has said anything directly about the current bill (not
  just the older Speaking Rock litigation) before publication.

## 2026-07-02 — E10: builder→skeptic→judge verification pass run; case moved to supported/medium

- did: Ran the verification pass inline (single session, not a Workflow —
  stakes didn't warrant spawning a billed multi-agent fleet). Builder step
  synthesized E1-E9 into the strongest version of the claim. Skeptic step
  ran four fresh counter-queries directly against `gain.db` (q12-q15 in
  queries.sql), independent of the builder's existing queries, against the
  full checklist in the skill's `reference/verification.md`. Judge step
  weighed both and wrote the verdict into case.md.
- found: See E10 in evidence.md for full detail. Headline: skeptic could not
  refute the core claim. One genuinely new result (not just re-confirmation):
  a corrected base-rate check across the actual tribal-gaming lobbying niche
  (not the whole corpus) found only 3 clients total show any explicit
  "oppose" language, and Sunland Park's streak is ~4.5x the next-longest —
  this *strengthens* E1's "rare, sustained, sole opponent" framing. Also
  confirmed the 2023 Q1 gap is real (not a corpus-wide filing lull) and
  found a clean negative (zero LD-203 contributions tied to the lobbyist —
  pure disclosure story, no "pay" angle). Surfaced one new sourcing risk:
  an unrelated client, "City of Sunland Park" (the municipal government),
  also files LDA disclosures — flagged in case.md so it's never conflated
  with the casino.
- judge's verdict: **supported, confidence medium** (case.md status/
  confidence/coverage frontmatter all updated — also fixed `coverage:
  unscanned`, which was stale since E8/E9's novelty scan already ran;
  corrected to `under-reported`). Not upgraded to high because three items
  remain open: E7's unreconciled deal-value figures, the still-unexplained
  (though now confirmed real) 2023 Q1 gap, and Paxton's inferred-not-stated
  position on the current bill. None block publication of the claim as
  scoped; they're pre-publication line items.
- editorial note: case's Verdict section in case.md had grown into a full
  history across E5/E8/E9 updates, against the template's intent ("one
  line... no re-summary of evidence"). Condensed it to a single current
  verdict paragraph; the full history stays in this log and in evidence.md.
- NEXT: Case is verification-complete. Remaining before publication: (1)
  reconcile E7's deal-value figures against a primary source (GLPI SEC
  filing or NM Gaming Control Board), (2) decide whether the fee-to-trust
  side-thread (`localgov-fee-to-trust-monitoring`) gets pursued as a
  companion piece or left alone, (3) final read for Paxton-related
  legal-risk language before anything ships given his active candidacy.
  Otherwise this case is ready to close out — see conversation with Emma
  2026-07-02 re: what a "closed, still newsworthy" case's final artifact
  should look like (case.md's Verdict is intended to serve as that record;
  no separate report file planned unless the findings-report PDF pulls
  from it directly).

## 2026-07-02 — two pre-publication items closed: deal-value reconciled, Paxton re-checked

- did: Ran a bounded research pass (forked agent, WebSearch, moderate query
  budget) on the two E10 pre-publication line items directly relevant to
  this case: (1) reconcile E7's $184M/$301M deal-value discrepancy against
  a primary source, (2) re-check whether Paxton has made any direct
  statement on H.R.3723/S.2564 since E9's research.
- found:
  - **Deal value — not actually a discrepancy.** GLPI's own Q3 2025 SEC 8-K
    exhibit and investor release confirm $183.75M is the real-estate-only
    piece (closed 2025-10-15, 8.2% cap rate); Strategic Gaming Management's
    own PR Newswire release confirms $301M is the total combined deal
    (operations + real estate). Both outlets' figures were correct — they
    were each quoting a different, correctly-labeled piece of one
    structured transaction. Full citations added to E7 in evidence.md.
    Reconciled — no longer a pre-publication blocker.
  - **Paxton — still nothing found.** Two independent search passes (direct
    bill-number/title search; Paxton-campaign-plus-tribes search) found no
    statement, release, or campaign comment from Paxton mentioning
    H.R.3723, S.2564, or the "Tribal Gaming Regulatory Compliance Act" by
    name, as of 2026-07-02. The case's existing caution (source any claim
    about his position on *this* bill to his own words, not the Speaking
    Rock litigation) stands unchanged — this is a confirmed "still nothing"
    result, not new information, but worth having re-checked given how
    fast his campaign is moving.
- updated: evidence.md E7 (reconciliation detail + citations); case.md
  Sources/legal-risk notes (both items) and Verdict section (dropped the
  now-resolved deal-value item from the open pre-publication list).
- NEXT: Only remaining open item before this case can move to `closed`
  (per the new closeout checklist) is the unexplained 2023 Q1 filing gap —
  confirmed real (E10), cause still unknown. Also still pending: the
  fee-to-trust side-thread decision. Otherwise ready for Emma to run the
  closeout checklist whenever she's satisfied.

## 2026-07-02 — 2023 Q1 gap explained: a formal registration termination/re-registration, not a missed filing

- did: Emma doubted external research would turn up anything on the gap and
  suggested re-checking `gain.db` directly first. Ran two in-corpus queries
  (q16, q17 in queries.sql): (1) all of Fulmer's 2023 filings across every
  client, not just Sunland Park, to check whether the gap is
  Sunland-Park-specific or a lobbyist-wide lapse; (2) Sunland Park's
  `filing_type_display` sequence across all its filings.
- found: The gap is fully explained by the data already in hand — no
  external research needed. Sunland Park's Senate filing sequence is
  `2022 Q4: "4th Quarter - Termination"` → (gap) → `2023 Q2: "Registration -
  Amendment"`. Sunland Park formally terminated its LDA registration at the
  end of 2022 and re-registered mid-2023 — the registration was legally
  inactive for the gap quarter, not silently skipped. Confirmed
  Sunland-Park-specific, not a Fulmer-wide filing lapse: he filed for all
  four of his other clients (two hospitals, an EV/business-solutions
  client, a hospital association) in 2023 Q1 — Sunland Park is the only
  client with no filing that quarter.
- updated: evidence.md E6 (added the explanation inline); case.md Hypothesis
  ("no gap" → "one explained pause") and Verdict (all three E10
  pre-publication items now resolved, not just two).
- editorial note: this is a better answer than a boring "clerical oversight"
  guess would have been — it's a real, LDA-rules-compliant pause (a
  registration can't just sit dormant; termination + re-registration is the
  correct procedure when lobbying activity actually stops and resumes), so
  the honest writeup framing is "paused once, in early 2023, then resumed,"
  not "continuous with no exceptions." Doesn't affect the 14-filing
  continuity count or the sole-opponent finding — all counted filings are
  real and dated.
- NEXT: All three E10 pre-publication items are now closed. Remaining before
  formally closing this case out (per the closeout checklist): decide on
  the fee-to-trust side-thread (`localgov-fee-to-trust-monitoring`) — pursue
  as a companion piece or leave alone. Otherwise this case is ready for
  Emma to run the closeout checklist.

## 2026-07-02 — base-rate check: is terminate-then-re-register unusual? No — routine corpus-wide

- did: Emma asked directly whether Sunland Park's termination/re-registration
  pattern (found above) is normal LDA behavior or something worth flagging.
  Ran a corpus-wide base-rate check (q18 in queries.sql): filing-type
  distribution overall, then a count of distinct client/registrant pairs
  showing the same termination-then-later-re-registration pattern anywhere
  in the corpus.
- found: Routine, not unusual. Terminations (12,196 rows across the four
  quarterly termination types) and fresh registrations (20,935 Registration +
  2,525 Registration - Amendment) are both common filing types generally,
  and 8,550 distinct client/registrant pairs corpus-wide show this exact
  same-pair terminate-then-re-register pattern. This is ordinary LDA
  compliance housekeeping (the law requires termination when lobbying
  activity ceases, and re-registration within 45 days of resuming) — not a
  red flag or something distinctive to Sunland Park.
- updated: evidence.md E6 (added base-rate context + query, inline with the
  2023 Q1 gap explanation).
- editorial note: can't determine Sunland Park's actual motive for the pause
  (contract lapse vs. deliberate cost-saving vs. administrative reset) —
  self-reported disclosure data doesn't carry that. Writeup frame should
  stay "paused once, then resumed — a common and legally unremarkable
  pattern," not imply anything was hidden.
- NEXT: All E10 pre-publication items fully closed, including the base-rate
  question on the gap itself. Only remaining decision before formally
  closing this case out: the fee-to-trust side-thread
  (`localgov-fee-to-trust-monitoring`) — pursue as a companion piece or
  leave alone. Committing this round now.

## 2026-07-02 — E11: confirmed bill has no fee-to-trust mechanism; fee-to-trust side-thread decoupled; case closed out

- did: Emma asked whether the bill actually requires a fee-to-trust land
  conversion (the mechanism behind the separate `localgov-fee-to-trust-
  monitoring` lead) — flagged as a real, previously-unresolved question this
  case had never checked. Delegated to a forked research pass to pull the
  bill's actual text (not just summaries) and confirm.
- found: **No fee-to-trust component.** Confirmed against H.R.2873's (118th
  Congress) introduced text on govinfo.gov — Section 3 only applies IGRA to
  gaming on land the tribes already hold; no land-status or land-acquisition
  provision anywhere. CRS's own bill summary and a law-firm client alert
  independently describe the same mechanism. This settles the open question
  from the 2026-07-01 log entry: the fee-to-trust lead and this case's bill
  are genuinely unrelated — same topic area (Indian/Native American Affairs
  lobbying), different legal mechanism, different tribes in the fee-to-trust
  lead's case. Wrote up as E11 in evidence.md; updated case.md's
  Sources/legal-risk note on the side-thread to reflect the resolution.
- editorial decision (Emma, 2026-07-02): **close out the case.** With the
  fee-to-trust question resolved (unrelated, not a dependency) and all three
  E10 pre-publication items already closed, nothing remains open that blocks
  a `closed` status under the new checklist. The fee-to-trust lead can be
  picked up as its own separate thread later if desired — not a reason to
  keep this case open.
- did (closeout, per reference/closeout.md): condensed case.md's Verdict to
  a single current paragraph (folding in E11); confirmed frontmatter
  (`status: closed`, `confidence: medium`, `coverage: under-reported`) all
  match actual latest state; confirmed Sources/legal-risk notes list is the
  complete pre-publication checklist for an editor.
- NEXT: none — case closed. If picked up again: the fee-to-trust thread is
  available as a fresh, unrelated lead (not a resumption of this case).
