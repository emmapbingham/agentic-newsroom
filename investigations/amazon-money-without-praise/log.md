# Log — amazon-money-without-praise

## 2026-07-08
- did: promoted from leads (slug=amazon-money-without-praise, lead_id=73,
  screen_run_id=36). Editor directed promotion in session (agent-live,
  acknowledged). Opened investigations/amazon-money-without-praise/.
- did: pulled Amazon.com Services' LDA lobbying-activity descriptions
  (senate_clients.id 184204, 210237) to see what Amazon is actually lobbying
  on, prompted by "what is Amazon paying these members for."
- found: see E2 (issue-code rollup — Labor Issues/Antitrust/Workplace tops
  the list at 29 activities) and E3 (specific bills named: American
  Innovation and Choice Online Act, Warehouse Worker Protection Act — these
  are the exact subjects members are publicly criticizing Amazon over).
- dead ends: none yet — this is the first drilldown pass in this case.
- open questions: E3's "opposing" framing is an inference from bill content,
  not a directly sourced Amazon position statement — needs corroboration
  before it's stated as fact. E1's press-mention sample was carried over from
  the original lead and hasn't been re-derived with fresh source citations in
  this case yet.
- NEXT: (1) re-derive E1 with press_id/url citations per mention so the case
  doesn't depend on the lead's un-cited sample; (2) scope E4 — whether a
  vote/cosponsorship check on S.2992/H.R.3816 and S.4260/H.R.8639 is feasible
  (needs external data outside gain.db — congress.gov bulk data or ProPublica
  Congress API, with a sources/ manifest); decide whether that's in scope for
  this case or a boring-explanation check that can be skipped if E1+E3 alone
  are judged sufficiently newsworthy.

## 2026-07-08 (same day, continued) — cosponsorship check
- did: user requested the cosponsorship/vote check flagged as NEXT above.
  Confirmed api.congress.gov requires a free API key (unauthenticated calls
  403); user signed up and provided a key. Stored it in a new gitignored
  `.env` at repo root (`.gitignore` didn't previously list `.env` explicitly
  by name but `.env` was already covered by the existing `.env`/`.envrc`
  pattern at line 174 — confirmed via `git check-ignore -v .env`). Wrote
  `sources/congress-gov-bills.md` manifest per CLAUDE.md's external-data
  disclosure convention (matches the existing `congress-legislators.md`
  pattern). Pulled sponsor + cosponsor lists for S.2992, H.R.3816, S.4260,
  H.R.8639 via the API; raw JSON cached in `data/congress_bills/`
  (gitignored). Wrote `analysis/pull_cosponsors.py` (stdlib urllib, matching
  repo convention — no `requests`/`dotenv` deps) to make this reproducible;
  verified it reruns cleanly and reproduces the same 39-row crosswalk.
- found: see E4 in evidence.md. None of the 4 bills got a floor vote (all
  died in committee/calendar). Of the 39 Amazon-money members, only 1-5 per
  bill (of ~18-21 eligible per chamber) cosponsored — consistent with
  "criticism is cheap talk" for most. But the two largest-dollar recipients
  (Warner $38,200, Reed $25,750) cosponsored the antitrust bill anyway, and
  Donald Norcross ($1,000) is H.R.8639's primary **sponsor** — the strongest
  possible break from the "money buys silence" framing. No dollar-amount
  gradient predicts cosponsorship.
- dead ends / correction: while building E4 I found E2/E3's original pull
  used the wrong Amazon filer — `senate_clients.id IN (184204, 210237)`
  ("AMAZON.COM SERVICES, INC." as client of outside firms AVOQ LLC / Endgame
  Strategies LLC), which is NOT the entity screen 40 actually reaches (screen
  40 is in-house-filers-only, exact entity<->registrant name match). The
  correct entity is registrant_id=54494, "AMAZON.COM SERVICES LLC",
  self-filed. Re-pulled E2/E3 against the correct entity — finding survives
  and is actually stronger (bills named in nearly every quarterly filing,
  2022 through 2026 Q1, across 3 Congresses, including a 119th-Congress
  successor bill S.2613 not previously known to this case). Corrected
  case.md, evidence.md, queries.sql in place; old (wrong-entity) numbers
  struck through/annotated, not silently deleted.
- open questions: E3's Consumer Issues/Safety/Products bill list (SHOP SAFE
  Act etc.) was carried over from the wrong-entity pull and not yet
  re-verified against registrant_id=54494 — flagged TODO in evidence.md. E1
  press-mention sample still not re-derived with fresh citations (same TODO
  as this morning, still open). Builder/skeptic pass not yet run — in
  particular, need to check whether Warner/Reed/Norcross (the cosponsorship
  outliers) actually appear in E1's *critical* press-mention sample, or
  whether they're money-takers who never criticized Amazon (which would pull
  them out of the "hypocrisy" framing entirely and might explain the outlier
  pattern cleanly: no criticism, no need to avoid the bill).
- NEXT: (1) re-verify E3's non-antitrust/warehouse-worker bill list against
  registrant_id=54494; (2) re-derive E1 with real press_id/url citations;
  (3) for each of the 9 cosponsor/sponsor outliers (esp. Warner, Reed,
  Norcross), check whether they're actually in the critical-press-mention
  set — this could resolve the "mixed" verdict cleanly either way;
  (4) once (1)-(3) done, run builder -> skeptic -> judge before this reaches
  report language.

## 2026-07-08 (same day, continued) — resolved Warner/Reed/Norcross
- did: user asked to check whether Warner, Reed, or Norcross actually
  criticized Amazon (NEXT item 3 above). Pulled full press_releases.text for
  Warner's 4 Amazon mentions, Reed's 2, and Norcross's 10-mention title list
  (release_ids in E5).
- found: see E5 in evidence.md. Warner's 4 mentions are all collision —
  2 multi-company AI-safety letters (Amazon one of ~7 recipients), 1 release
  where Warner *praises* Amazon as a VA jobs-recruiting win, 1 with no Amazon
  text in the retrieved body at all (likely FTS/alias false positive). Reed's
  2 mentions: one lists Amazon only as a DOGE staffer's stock holding
  (incidental, about the staffer's ethics not Amazon), the other quotes
  Heinrich (not Reed) naming Amazon generically alongside Walmart. Neither
  Warner nor Reed ever criticized Amazon specifically. Norcross, by contrast,
  is sharply and repeatedly critical — 8+ releases 2022-2023 on warehouse
  safety (OSHA-investigation demands, a presser outside an Amazon warehouse,
  reaction to a worker's death, "Slams Amazon") — then sponsors H.R.8639 in
  2024 and its 2025 bicameral reintroduction. He took the smallest amount in
  the 39-member set ($1,000).
- dead ends: none — this fully resolved the ambiguity flagged this morning.
- open questions: only Warner/Reed/Norcross (the cosponsorship outliers) have
  been checked against real press text; the other 36 of 39 members still rest
  on the lead's original un-cited sample (same E1 TODO as before — now more
  urgent, since Warner/Reed just demonstrated the collision-match risk is
  real, not hypothetical, and could affect other members in the 39-set too).
- NEXT: (1) re-derive E1 for the full 39-member set (or at least re-verify
  the specific quotes already used — Wyden, Baldwin, Blackburn/Blumenthal,
  Hoyer/Pallone/Van Hollen, Warren — the same way Warner/Reed were just
  checked, since those were also carried over un-verified from the lead);
  (2) re-verify E3's non-antitrust/warehouse-worker bill list against
  registrant_id=54494; (3) builder -> skeptic -> judge pass; (4) novelty scan.
  Confidence raised low -> medium in case.md pending (1)-(3).

## 2026-07-08 (same day, continued) — press-declared bill support (E6)
- did: user asked whether there's a way to check bill support besides
  cosponsorship/votes. Discussed options (member's own press releases stating
  a position; committee actions; Dear Colleague letters; outside news) —
  picked press-release search first since it's free (already-ingested data,
  no new API calls) and catches earlier/looser signals cosponsorship misses.
  Ran a text search (`LIKE`) of all 39 Amazon-money members' own
  `press_releases.text` for the bill names/numbers directly (not just
  "Amazon" — the bill itself), across all spellings/numbers for both bill
  families (AICOA: S.2992/H.R.3816; WWPA: S.4260/H.R.8639/S.2613).
- found: see E6 in evidence.md. Zero AICOA mentions across all 39 — the
  antitrust fight isn't something these members chose to press-release about,
  even the two (Warner/Reed) who turned out to be false-positive critics.
  WWPA: 5 releases from 3 members. Norcross (already known, confirms search
  works). **Tina Smith ($250)** — her WWPA cosponsorship (E4) is corroborated
  by sustained, personally-authored criticism tied directly to her own bill —
  second clean confirming case alongside Norcross, both smallest-dollar in
  the set. **Ruben Gallego ($11,000)** — new finding: explicit press quote
  backing WWPA ("I'm proud to support this bill") plus direct Amazon
  criticism in the same release, but the E4 crosswalk shows he has NOT
  formally cosponsored it. A real instance of verbal support without the
  legislative follow-through step — a middle category plain cosponsorship
  counts would have missed entirely.
- dead ends: none.
- open questions: only checked exact bill-name/number text matches — would
  miss a member who describes a bill only descriptively without naming it
  (a floor on the true count, not a ceiling). Haven't compared against a
  baseline rate for non-Amazon-money members doing the same (would help the
  skeptic pass distinguish "notable" from "normal legislator behavior").
  Gallego's non-cosponsorship could be timing (bill introduced 2025-07-31,
  his release 2025-12-11 — 4+ months, so probably not pure timing) rather
  than reluctance; noted the gap rather than assuming motive.
- NEXT: unchanged from prior entry — (1) re-derive E1 for the full 39-member
  set; (2) re-verify E3's non-antitrust/warehouse-worker bill list against
  registrant_id=54494; (3) consider a baseline-rate check (do non-Amazon-money
  members show similar press-support-without-cosponsorship rates?) before
  treating Gallego as case-specific; (4) builder -> skeptic -> judge pass;
  (5) novelty scan.

## 2026-07-08 (same day, continued) — committee-stage action (E7)
- did: user asked about committee action data as another way to see bill
  support beyond cosponsorship/votes. Pulled congress.gov's
  `/bill/.../actions` and `/bill/.../committees` for all 4 bills. Found AICOA
  (both bills) had real committee-stage action (markup + reported out of
  Judiciary); WWPA (both bills) never advanced past referral -- no hearing
  ever. Checked `member_committees_history` in gain.db for which of the 39
  Amazon-money members sat on House/Senate Judiciary at any point covered by
  the snapshot history (earliest 2022-01-04).
- found: see E7 in evidence.md. 3 of 39 intersect Judiciary: Tom Cotton and
  Ted Cruz (Senate Judiciary, both present from the earliest snapshot --
  covers S.2992's Jan 2022 markup), Sydney Kamlager-Dove (House Judiciary,
  first seen 2025-02-02, too late for H.R.3816's 2021 markup). Pulled
  Cotton's (4 releases) and Cruz's (3 releases) full Amazon press-mention
  text -- same collision pattern as Warner/Reed: none are genuine
  Amazon-specific criticism. Cotton's Temu release is actually favorable to
  Amazon by contrast ("Temu directly copies Amazon storefronts... knock-off
  Chinese versions"). No genuine Amazon critic among the Amazon-money members
  positioned on the committee that acted on the bill Amazon was fighting.
- dead ends: congress.gov's structured API does not expose individual
  committee-markup vote tallies (who voted which way at markup) -- would
  need the committee's own unstructured vote record/transcript, out of scope
  for this pass. Also confirmed committee-history coverage gap:
  `member_committees_history`'s earliest snapshot (2022-01-04) can't say
  anything about H.R.3816's mid-2021 markup -- no House-side check possible
  for that specific vote without pulling `legislators-historical.yaml`
  committee data from before the snapshot window (not done).
- open questions: this is a small-N check (3 of 39) -- doesn't generalize to
  a population-level claim about all 39. Most of the 39 sit on other
  committees whose relationship to these two specific bills is moot (WWPA
  never had a hearing anywhere, so committee seat elsewhere doesn't matter
  for it; AICOA's only committee of jurisdiction was Judiciary in both
  chambers).
- NEXT: same list as prior entry, now including E7 in the "confirms the
  pattern" tally: (1) re-derive E1 for the full 39-member set; (2) re-verify
  E3's non-antitrust/warehouse-worker bill list against registrant_id=54494;
  (3) baseline-rate check before treating Gallego as case-specific; (4)
  builder -> skeptic -> judge pass; (5) novelty scan. Confidence stays at
  medium (E7 adds supporting detail but is small-N, doesn't move confidence
  further on its own).

## 2026-07-08 (same day, continued) — targeted novelty check on Gallego
- did: user asked if there's coverage of Gallego's Amazon-money/WWPA position
  specifically, since he's the case's most novel figure so far (real
  criticism + real verbal support + no cosponsorship + $11,000). Ran two
  bounded web searches (WebSearch tool, not part of gain.db) rather than a
  full case-level novelty scan.
- found: no coverage connecting his Amazon PAC money to his WWPA position or
  Amazon criticism specifically -- a miss (weak evidence of novelty for this
  narrow angle only, not the whole case). Separately found real, active,
  unrelated news: Gallego is under a DOJ investigation (first reported
  ~2026-06-29, confirmed by CBS News/Axios/ABC News/Fox News) into alleged
  personal misuse of his leadership PAC's funds (family trips, Super Bowl
  tickets, childcare reimbursement) -- not related to Amazon. One adjacent
  detail: per that coverage his leadership PAC "received more than half of
  its $1.5 million in funding from corporate PACs," i.e. his corporate-PAC
  funding generally is already a live news thread, separate from this case's
  specific finding.
- dead ends: none -- this was a clean, useful search.
- open questions / risk note: recorded the DOJ-investigation context in
  case.md's Prior coverage section, explicitly fenced (per
  fish-for-leads/reference/prior-art.md) as NOT part of this case's evidence
  chain -- it's adjacent context for an editor/lawyer, not support for any
  Claim. Flagged in Sources/legal-risk notes: naming a sitting senator
  already under federal investigation raises the legal-risk bar regardless
  of topic; do not conflate the two claims (Amazon/WWPA finding vs. PAC-fund
  misuse investigation) if Gallego is named in report language.
- NEXT: unchanged -- this was a side check, not a case-level novelty scan.
  Full novelty scan still pending case being closer to report-ready (see
  prior NEXT list, unchanged).

## 2026-07-08 (same day, continued) — Gallego's other corporate donors (E8)
- did: user asked whether Gallego criticized any other corporations he took
  money from -- tests whether his Amazon pattern (small money, genuine
  criticism, verbal-not-formal support) is Amazon-specific or just how he
  operates. Pulled his top ~40 distinct donor registrants by deduped FECA
  dollars (same dedup pattern as screen 40's `money` CTE), excluded
  law/lobbying-firm and union/trade-association registrants (not the actual
  funding company), searched his 506 press releases for mentions of the
  remaining ~13 identifiable corporate names plus Amazon for comparison.
- found: see E8 in evidence.md. Amazon ranks only 60th of 482 distinct
  registrants giving to Gallego ($11,000) -- a small, unremarkable slice of a
  very broad donor base. 12 of his other 13 top corporate donors got zero
  press mentions at all. The one exception: Pinnacle West Capital Corp / APS,
  his 2nd-largest identifiable corporate donor ($45,000, 4x Amazon) -- gets
  praise, not criticism: Gallego introduced a nuclear-investment bill and
  called APS a nuclear-leadership pioneer. Opposite direction from Amazon,
  and a genuine say-for-pay match (the exact pattern screen 40 was designed
  to catch) riding along inside this case.
- dead ends / correction: initially misread the derived_client_press_mentions
  table as missing release 126102 (Gallego's Amazon-layoffs letter) and wrote
  that into evidence.md as an "undercount bug" -- rechecked directly
  (`SELECT * FROM derived_client_press_mentions WHERE release_id=126102`),
  confirmed the row IS there, corrected the evidence.md text rather than
  letting the wrong claim stand. Also caught a real methodology bug: a naive
  `LIKE '%APS %'` search for Pinnacle West's trade name substring-matched
  false positives (e.g. "gAPS " inside "gaps") across ~18 unrelated
  Gallego releases before tightening to word-boundary-safe patterns
  (queries.sql#q9) -- same failure class as the "UBS"/"Spectrum" false
  positives caught earlier this session. Verified the tightened query
  reproduces exactly the 2 real Pinnacle West hits cited in E8.
- open questions: this is a single-member case study (N=1, ~14 donors
  checked) -- doesn't establish a population-level base rate for "members
  criticize small donors, praise big ones." The Pinnacle West/APS finding is
  itself a fresh, unscanned lead (a second say-for-pay match sitting inside
  this case) -- hasn't been noveltly-scanned or evaluated as its own
  potential thread.
- NEXT: (1) decide whether Pinnacle West/APS is worth a quick side novelty
  check or spinning into its own lead vs. staying a supporting data point
  here; (2) re-derive E1 for the full 39-member set; (3) re-verify E3's
  non-antitrust/warehouse-worker bill list against registrant_id=54494;
  (4) baseline-rate check; (5) builder -> skeptic -> judge pass; (6) full
  case-level novelty scan.

## 2026-07-08 (same day, continued) — Pinnacle West lead: gated, not logged
- did: user asked to log the Pinnacle West finding as a separate lead in
  newsroom.db's leads table (per fish-for-leads doctrine: a drilldown
  surfacing a named actor with a motive should get a leads row, same shape
  as the Sunland Park worked example in lead-gates.md). Before writing
  `story`, ran the boring_explanation-first test the gate doctrine requires:
  read the full text of both cited releases (135182, 136106) rather than
  relying on the earlier grep snippet.
- found: the boring explanation wins. Release 135182 (bill introduction) is
  Gallego's own words and never names APS or Pinnacle West at all -- only
  generic nuclear-policy language, co-sponsored with Sen. Risch (R-ID, not
  an Arizona senator, i.e. not home-state boosterism either). Release 136106
  is a standard "what industry is saying" roundup with 14 organizations
  quoted supportively (Third Way, ClearPath, NEI, APPA, U.S. Chamber, IBEW,
  Holtec, Clean Air Task Force, Building Trades, Nuclear Innovation
  Alliance, U.S. Nuclear Industry Council, Idaho National Lab, SRP, and
  APS) -- APS's CEO quote is one of many, not evidence Gallego personally
  favors this donor. This is generic bipartisan-bill-launch messaging, not a
  say-for-pay match. Corrected evidence.md E8 and case.md to reflect this --
  the earlier characterization ("Gallego praises APS by name") overstated
  what the source actually shows and did not survive a full read.
- decision: NOT logged as a separate leads row. Per lead-gates.md gate #3
  (boring explanation first), a lead that fails its own boring-explanation
  test before promotion doesn't get surfaced to the editor -- the doctrine
  explicitly says filtered leads still get a row with a suppressed-*
  disposition (not unrecorded), but this candidate never had a screen_run_id
  or made it to a formal `story`/`claim` draft -- it was caught at the
  gate-test stage during evidence-writing, before a lead was ever drafted.
  Recording the gate outcome here in the case log (rather than a
  leads-table row) since there's no screen run or formal candidate to
  attach a suppressed-boring disposition to -- the newsroom.db leads table
  models screen-sourced candidates, and this was a case-internal drilldown
  byproduct that self-filtered before reaching candidate status.
- open questions: none -- corrected the record, this thread is closed.
  Revised E8 headline: 13 of 13 (not 12 of 13) of Gallego's other top
  corporate donors get zero personal attention from him; Amazon remains the
  sole exception, and it's critical attention, not favorable.
- NEXT: unchanged except item (1) is now resolved (no Pinnacle West lead to
  log) -- (2) re-derive E1 for the full 39-member set; (3) re-verify E3's
  non-antitrust/warehouse-worker bill list against registrant_id=54494;
  (4) baseline-rate check; (5) builder -> skeptic -> judge pass; (6) full
  case-level novelty scan.

## 2026-07-08 (same day, continued) — reassessment: Smith's money isn't real, case weakened (E9)
- did: user pushed back on the case's state -- pointed out only 3 of 39
  members (Norcross, Smith, Gallego) survived as genuine confirming cases,
  that Norcross/Smith's dollar amounts ($1,000/$250) are tiny relative to
  corporate lobbying scale, asked whether that's "just incidental," flagged
  Gallego as the more interesting figure, asked whether the filings show any
  detail on Norcross/Smith's specific contributions, and asked for a
  coverage scan on Norcross/Smith. Pulled contribution-level detail
  (contributor_name, filer_type) for all three instead of relying on the
  honoree-level dollar aggregate used everywhere else in this case.
- found: see E9 in evidence.md. Norcross's $1,000 confirmed genuine --
  direct from the actual Amazon PAC. **Smith's $250 is NOT Amazon corporate
  money** -- contributor_name='SELF', filer_type='lobbyist', traced to Kasia
  Witkowski, an individual Amazon-registered lobbyist, giving her own $250
  personal donation to Smith's leadership PAC. Disclosed on Amazon's LD-203
  filing only because lobbyists must report personal political giving
  alongside the company PAC's. This is not a corporate-influence signal --
  removed Smith from the case's confirming-case list entirely. Gallego's
  $11,000 re-verified as 4 genuine Amazon PAC contributions, continuing
  after his criticism began.
- did (continued): checked the user's Arizona-employer boring-explanation
  hypothesis for Gallego -- Amazon's PAC gave Mark Kelly (AZ's other
  senator) exactly $0, arguing against blanket state-based favoritism. But
  found the amount didn't need that explanation anyway: $11,000 is exactly
  the Senate median in the 39-member set (range $250-$38,200) -- not an
  outlier by size, just typical.
- did (continued): ran the requested coverage scan on Norcross and Smith.
  No coverage found connecting either's Amazon PAC money to their WWPA
  position specifically -- Norcross's Amazon criticism itself is
  well-covered (Inquirer, Bloomberg Law, Labor Tribune) as a labor story,
  but not the money-vs-rhetoric angle. Given Smith's money turned out not to
  be real, this scan is now moot for her.
- dead ends: none -- this was a clean, decisive check that materially
  changed the case's shape.
- open questions / decision: rewrote case.md's Verdict section in full
  (not a patch) to state the reassessed finding honestly: what survives is
  N=1 (Gallego), a real but modest money/follow-through gap, not the
  systemic 39-member pattern the lead originally framed. Recommended
  **park, not kill** -- the verified facts are true and could resurface as
  one exhibit in a broader pattern if found elsewhere in the corpus, but not
  worth further standalone drilldown right now. Confidence lowered
  medium -> low; status noted as "open (leaning parked)."
- open questions (methodology, corpus-wide): the SELF/individual-lobbyist
  contribution trap that caught Smith has NOT been checked for the other 36
  of the 39-member set -- other members' "Amazon money" totals in E1/E4/E6/E8
  could be similarly inflated by individual lobbyist contributions mixed
  into the honoree-level aggregate. This is a corpus-level gap (the existing
  `money` CTE dedup pattern guards against double-counting, not against this
  conflation) worth flagging beyond this one case if anyone builds on screen
  40's pattern again.
- NEXT: case is parked pending a reason to revisit. If resumed: re-check the
  SELF/individual-contributor trap across the full 39-member set before
  trusting any of E1/E4/E6/E8's dollar figures for members other than
  Norcross/Gallego (now verified) and Smith (now excluded).

## 2026-07-09 — full-case novelty scan (user wrapping up the case)
- did: user asked to wrap up the case, starting with a full novelty scan
  (case-level, not the narrow Gallego-only check from 2026-07-08) covering
  three angles: members taking Amazon money, members taking action on bills
  affecting Amazon, and members praising/criticizing Amazon in press. Ran 9
  WebSearch queries across the general theme, Gallego+WWPA, Norcross+WWPA,
  Amazon-lobbying-against-WWPA generally, AICOA PAC-contribution/cosponsor
  framing, and a couple of adjacent-framing follow-ups.
- found: general Amazon-PAC-vs-criticism theme is well covered but on
  different axes (climate hypocrisy, election-denier donation-pause reversal,
  general corporate-PAC-vs-progressive-rhetoric pieces) — none connect Amazon
  money to a member's own criticism of Amazon specifically, none mention
  AICOA/WWPA. One close-adjacent hit: Sludge's "Top Dem Bundler Lobbies
  Against Worker Protections for Amazon" (2024-12-27) — covers a
  lobbyist-bundler's conflict of interest on WWPA, not a member's own PAC
  receipts vs. their own bill position; doesn't name Gallego or Norcross.
  No coverage found connecting either Gallego's or Norcross's Amazon PAC
  money to their WWPA position specifically — confirms the 2026-07-08 Gallego
  check and extends it to Norcross (not previously checked).
- dead ends: none — clean scan, no scoop risk surfaced.
- open questions: none new. Novelty was never the blocking issue for this
  case — N=1 (Gallego) + 1 clean anti-capture point (Norcross) is still too
  thin to carry a standalone piece regardless of novelty. This scan confirms
  the surviving finding isn't scooped, which matters only if the case is
  revived as a supporting exhibit elsewhere.
- decision: updated case.md's `coverage` field to `scanned` and wrote the
  Prior coverage section in full. Case remains `parked` — this scan doesn't
  change that status, it closes out the one open item (novelty scan) that
  was still outstanding when the case was parked.
- NEXT: none for this case unless a reason to revisit surfaces (broader
  cross-company pattern found elsewhere, or a stronger single case than
  Gallego/Norcross turns up). The corpus-wide SELF/individual-lobbyist
  contribution trap (E9) remains an unresolved methodological flag for
  anyone reusing screen 40's `money` CTE pattern, independent of this case.

## 2026-07-09 (continued) — builder-skeptic-judge tribunal, case reframed
- did: user asked to run builder/skeptic/judge and get a final verdict, per
  `track-investigation/reference/verification.md`. Ran inline (not as a
  billed Workflow — case is at low confidence, not yet report-bound, so a
  full fleet tribunal wasn't warranted per the skill's "scale to stakes"
  guidance). Builder assembled the park-day claim (N=1 Gallego + Norcross
  anti-capture). Skeptic (me, same session but explicitly re-deriving from
  gain.db rather than reading prior evidence blocks) ran the skeptic
  checklist: re-verified Norcross's contribution independently (confirmed,
  filer_type='organization'), then ran the SELF/individual-lobbyist trap
  (flagged in E9 as an unchecked corpus-wide gap) across the full 39-member
  set for the first time, then checked the dollar-gradient claim by listing
  all 39 members' cosponsorship status by rank, then ran the critic
  cross-check E5 had already validated as a method (does a cosponsor's press
  record show genuine criticism, or just a name on a list) against the
  WWPA_HR cosponsor list, which had never been checked that way.
- found: see E10 in evidence.md. Two results. (1) The SELF-trap check is
  clean for Norcross/Gallego but catches a second case: Angie Craig's
  $6,200 (cited in E4 as an AICOA_HR cosponsor among the money-taking set)
  is entirely one individual lobbyist's personal donations (lobbyist_id
  56820), not Amazon PAC money -- same pattern as Smith, now also excluded.
  (2) Cross-referencing WWPA_HR's cosponsor list against E1's critic
  criteria surfaced two more genuine, on-topic critics never counted in the
  case's confirming-case tally: Frank Pallone ($15,000, already had a
  genuine critical mention on file in E1 but was never checked against his
  own cosponsorship) and Melanie Stansbury ($1,000, a direct Amazon
  labor-rights press release). Gomez and Thompson, the other two WWPA_HR
  cosponsors, were checked and ruled out (their mentions aren't genuine
  Amazon criticism). Net: 4 genuine on-topic critics in the dataset
  (Norcross, Pallone, Stansbury, Gallego), all 4 show legislative
  follow-through (sponsor, cosponsor, cosponsor, verbal-support), zero show
  suppression. The dollar-gradient theory doesn't hold either -- cosponsors
  span $1,000 to $15,000.
- dead ends: none -- this was a clean, decisive skeptic pass that changed
  the case's shape a second time (first E9 narrowed it, now E10 broadens and
  reverses the framing).
- judge: the original hypothesis (Amazon money buys silence/deference from
  critics) is not supported by the corrected, complete count -- it's closer
  to refuted. What's supported instead is the reverse-of-expectation
  finding: no detectable relationship between Amazon PAC money and whether a
  genuinely critical member follows through legislatively, verified across
  all 4 genuine critics in the dataset, not just 1-2. Confidence raised low
  -> medium. Status changed parked -> "open (reframed)". Rewrote case.md's
  Verdict section (kept the 2026-07-08 verdict in a collapsed <details> block
  for the record, per closeout.md's "don't delete, condense" convention, even
  though this isn't a formal closeout -- the case is reopening, not closing).
- open questions: this reframed finding hasn't been through its own novelty
  scan yet -- the 2026-07-09 novelty scan (see prior log entry) was run
  against the *original* framing (money buys silence) and checked Gallego +
  Norcross by name; it did NOT check Pallone or Stansbury specifically, and
  didn't test the reframed claim itself ("critics who take Amazon money
  still legislate against it") as a general pattern. Per
  feedback_novelty_scan_scope (scan the general claim, not just the named
  instances), this should be re-scanned before the reframed finding goes
  further. Still N=4 -- a real but small sample; the "no floor vote on either
  bill" caveat from E4 still applies to all cosponsorship signals cited here.
- NEXT: (1) re-run novelty scan against the reframed general claim +
  Pallone/Stansbury by name; (2) decide with editor whether this reframed
  "money didn't buy silence" finding clears the bar as a short standalone
  piece (reverse/null results are a harder sell than positive findings even
  when equally well-sourced) or stays a supporting exhibit; (3) if it
  proceeds, correct E4's cosponsor table to remove Angie Craig and note the
  Pallone/Stansbury reclassification in case.md's Sources/legal-risk section
  (currently only names Gallego/Norcross/Smith/Warner/Reed/Cotton/Cruz --
  needs Pallone and Stansbury added with the same "public record, cited only
  for own press releases and cosponsorship" framing).

## 2026-07-09 (continued) — cross-case check: Pallone overlaps with critics-take-health-money
- did: user noted Pallone is also a primary confirming case in
  `investigations/critics-take-health-money/` (closed 2026-06-24). Checked
  that case's case.md/evidence.md for the Pallone material and for any other
  overlapping names.
- found: Pallone is one of that case's two focused confirming examples (with
  Carter) — 25 critical releases naming PhRMA/Merck by name + $2.52M in
  deduped health-sector FECA (3.5x the health-committee-member average),
  framed there as a documented donor/rhetoric tension (causation not
  established). That case was already novelty-scanned as well-covered —
  RFK Jr. raised the exact Pallone-pharma-money angle in a June 2025
  congressional hearing, and KFF Health News runs an ongoing tracker on this
  pattern for him specifically. Angie Craig also appears in that case's
  leaderboard (14th of 14, $852k health-sector FECA) but was not one of its
  two focused confirming examples -- no direct conflict with her exclusion
  here (E10's SELF-trap finding), just worth noting as the same person
  appearing in two cases.
- assessment: not a contradiction -- a member can take broad sector money
  while criticizing named companies in it (health case's mechanism) and
  separately take one company's money while criticizing that company and
  still legislating against its position (this case's mechanism) -- but it
  means Pallone carries mixed evidence depending which case is read, and a
  report citing him in both without reconciling the two readings would look
  sloppy or cherry-picked. Added a "Cross-case conflict" note to this case's
  case.md (Prior coverage section) and a reciprocal note to
  critics-take-health-money's case.md Sources/legal-risk section, so neither
  case can reach report language without a pointer to the other.
- dead ends: none.
- open questions: none new -- this is a flag for whoever drafts report
  language, not something that needs more drilldown right now.
- NEXT: unchanged from prior entry, plus: if/when either case's Pallone
  material is drafted into report language, reconcile the two readings in
  the text per both case.md notes.

## 2026-07-09 (continued) — does Pallone's pattern generalize across sectors?
- did: after the Pallone cross-case flag, user asked whether Pallone shows
  similar donor/rhetoric patterns in other areas, and how to address it.
  Pulled his full top-40 donor registrant list (deduped FECA, E8's pattern)
  and searched his 496 press releases for mentions of his largest non-health
  donors; also sampled his general "demand/slam"-titled releases to see what
  he's actually loud about.
- found: his donor base is broad (Energy & Commerce jurisdiction) --
  telecom/tech donors (Comcast $45k, NCTA $45k, Charter $40k, Verizon $36k,
  Google $38k, Microsoft $35k) are comparable in size to his health-sector
  money, but get zero press mentions -- same "biggest donor cluster, total
  silence" shape as Gallego's other donors in the Amazon case (E8). His
  large "demands/slams" release volume is aimed almost entirely at
  government targets (Trump admin, FEMA, DHS, EPA, FERC) or one sustained
  local fight (RWJBarnabas Health's Long Branch, NJ hospital closure -- a
  real named-company target, but RWJBarnabas isn't a federal LDA/FECA donor
  in this corpus, so no money conflict there). Re-checked the pharma
  criticism itself: two named-company releases (PhRMA, Merck) in a 3-week
  window in June 2023, tied to one legislative fight (Medicare drug-price
  negotiation) -- narrower than the health case's "25 critical releases"
  framing once general IRA-messaging is separated from named-company
  criticism.
- assessment: Pallone is not a serial critic-taker across sectors -- the
  pharma episode and the Amazon episode are both narrow, real, event-driven,
  single-company observations, not evidence of a durable trait. This
  resolves the cross-case tension (added 2026-07-09 earlier) rather than
  deepening it: the two cases aren't competing readings of the same
  behavior, they're two separate narrow episodes involving the same person.
  Wrote a "Follow-up" note into both cases' case.md recommending report
  language scope any Pallone claim to its specific episode (name the
  company, the bill, the window) rather than characterizing him generally.
- dead ends: RWJBarnabas Health and Amtrak (his other frequent named
  targets) are not found in `senate_registrants` -- not registered federal
  lobbying entities under those names in this corpus, so no donor-conflict
  check is possible for them here (may lobby under a different registered
  name, or may not lobby federally at all -- not pursued further, out of
  scope for this follow-up).
- NEXT: unchanged from prior entries.

## 2026-07-08 (same day, continued) — formally parked
- did: user confirmed the park decision from the prior entry. Set
  `status: parked` in case.md frontmatter (this vocab's status ladder --
  `open -> supported -> refuted -> parked -> killed | closed` -- defines
  `parked` as a non-terminal state distinct from both closeout paths in
  reference/closeout.md, so followed the spirit of that checklist --
  condense Verdict, confirm frontmatter, don't delete anything -- without
  forcing this into `killed` or `closed`, neither of which fit: nothing was
  refuted (unlike killed) and there's no publication step pending (unlike
  closed)). Condensed case.md's Verdict section from the accreted
  E1-through-E9 history into a single current paragraph per the closeout
  checklist's guidance -- the full history stays in log.md (this file),
  not duplicated in case.md.
- found: n/a -- this is a state-change entry, not a drilldown.
- dead ends: none.
- open questions: unchanged from prior entry -- the corpus-wide
  SELF/individual-lobbyist contribution trap (caught via Smith) has not been
  checked across the other 36 of the 39-member set, and remains a
  methodological flag for any future work using screen 40's `money` CTE
  pattern, independent of whether this case itself is resumed.
- NEXT: none -- case parked, see case.md Verdict for the condensed final
  state. Resume only if a reason to revisit surfaces (e.g. a broader
  cross-company version of this pattern found elsewhere in the corpus).
