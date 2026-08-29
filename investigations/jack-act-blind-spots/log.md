# Log — jack-act-blind-spots (formerly hanson-vva-conviction-flicker)

## 2026-07-06
- did: promoted from leads (slug=hanson-vva-conviction-disclosure-flicker,
  screen_run_id=33; first run of the new conviction-quarterly-gaps screen,
  built on derived_convicted_lobbyist_register this same session). Case files
  seeded from the lead + the surfacing-session drilldown.
- found: E1 (3/7 gap, uuids), E2 (corpus norm = re-disclose; kills the
  "form doesn't require it" out), E3 (disclosed text is the 2013 BIS
  settlement, actual predicate is the 2009 §1001 plea — D.D.C.
  1:09-cr-00071), E4 (House corroborates text; gap analysis not done).
- legal basis filed: sources/jack-act-notice.md (JACK Act guidance: every
  LD-2, any prior conviction, no lookback; "intentionally omitting... may
  constitute a violation of federal law").
- dead ends: none yet this case; note the sibling Hunter candidate went to
  duplicate-of (lead 2 owns it).
- open questions: does an amendment cure any of the 3 gaps (q5, drafted)?
  live LDA pages match our ingest for the 3 gap uuids? What sentence did
  Hanson receive; any vacatur (docket pull)? House-side flicker (needs
  name-keyed register)? Who prepares VVA's LD-2s (same preparer across the
  flicker boundary would strengthen; different would support clerical)?
- NEXT: run q5 (amendment cure check) + spot-check the 3 gap filings on
  lda.senate.gov, then builder → skeptic → judge.

## 2026-07-07
- did: ran the four owed evidence chores — E5 (amendment cure, q5 precise),
  E6 (live LDA spot-check via API), E7 (House-side flicker, q7), E8 (criminal
  docket). Appended E5–E8 to evidence.md; added q5 (rewritten precise) + q7 to
  queries.sql. No newsroom.db write, no case.md edit, no commit.
- found:
  - E5 SUPPORTS — no amendment cures any gap. 2023 Q3/Q4 have no amendments at
    all; 2025 Q1 has a `1A` amendment that carries no disclosure AND drops
    Hanson from the lobbyist list. Kill-check (a) closed.
  - E6 SUPPORTS — live LDA API matches ingest exactly: 2023 Q3 (06b7c4cf) lists
    Hanson, conviction_disclosures empty; 2024 Q1 (1dd174b2) lists Hanson,
    disclosure present (BIS text, 2013-07-16). Rules out ingest artifact
    (kill (d)). Note: HTML SPA pages 404 to fetch; used the `v1/filings/{uuid}/`
    API (same system of record). Budget spent before re-pulling the other 2 gaps.
  - E7 SUPPORTS — House name-keyed data shows the identical flicker: Harold
    Hanson listed on 8 VVA House LD-2s; house_convictions rows only on the four
    2024 quarters; gap on 2023 Q3/Q4 + 2025 Q1 (plus a 2023 Q2 amendment listing
    without disclosure, and the 2025 Q1 `1A` dropping Hanson — mirrors Senate).
    Independent (name-keyed) corroboration of the id-keyed Senate finding.
    Completes E4's owed gap analysis.
  - E8 OWED/neutral — live docket pull FAILED: CourtListener HTML 403
    (Cloudflare), REST API 401 (auth). WebSearch surfaced only BIS orders +
    unrelated economics papers. Plea (Count 3, §1001, 2009-11-13) stands from
    E3's prior search; SENTENCE + vacatur still unverified — retry via
    authenticated CourtListener/PACER before publication.
- surprises: both amendments touching the flicker (Senate 1A + House 1A, 2025
  Q1) REMOVED Hanson from the lobbyist list rather than adding the JACK
  disclosure — the corrective action taken was de-listing, not disclosing.
- web budget: 8 fetches (4 LDA HTML 404, 2 LDA API OK, 2 CourtListener fail) +
  1 WebSearch. Exhausted.
- dead ends: CourtListener is bot-blocked (403/401) for unauthenticated fetch.
- open questions (unchanged / narrowed): live re-pull of the two remaining gap
  uuids (2023 Q4, 2025 Q1) — cheap owed confirm; Hanson's sentence + no-vacatur
  (needs authed docket); LD-2 preparer identity across the flicker boundary.
- NEXT: builder → skeptic → judge on the assembled E1–E8.

## 2026-07-07 (overnight, agent-auto — PROVISIONAL)
- did: builder → skeptic → judge tribunal on E1–E8 (builder + skeptic =
  independent Opus agents; judge = Fable main loop). Verdict written to
  case.md; status open → parked.
- found: facts supported at high confidence (gaps real, live-verified,
  uncured, both chambers); story framing REFUTED by the skeptic's re-derive —
  (1) not a flicker: 2023 Q3+Q4 = one late batch filing (2024-02-21, same
  preparer John Stovall) during onboarding; 2025 Q1 = departure quarter,
  corrected by de-listing; (2) base-rate norm contaminated (Burkman+Wohl
  autofill = 74% of post-conviction quarterlies; Wohl's sole gap is also his
  latest quarter — boundary gaps recur); (3) JACK predicate forks on the
  BIS-vs-court instrument with the docket unverified. Same-preparer
  continuity makes clerical the parsimonious read; intent unobservable.
- judge's call: parked, not killed — the filing-level facts are solid and
  the vein may be worth a SYSTEMIC re-scope (Hunter 0/6 + Hanson boundary
  gaps + wrong-instrument citations = "the JACK Act failing quietly at the
  edges"), which is an editor decision.
- open (if revived): authenticated docket pull (sentence/vacatur); re-pull 2
  remaining gap uuids live; the systemic re-scope decision.
- NEXT: editor review of the parked verdict (actions queue, priority 5).

## 2026-07-07 (editor session — restructure)
- did: editor (Emma) reviewed the parked verdict, walked through the Hunter
  candidate (lead 2 / hunter-conviction-disclosure-gaps, previously
  duplicate-of'd against this case) in detail, then directed a full
  restructure per the judge's recommended systemic re-scope. Renamed case
  hanson-vva-conviction-flicker -> jack-act-blind-spots (`git mv`, history
  preserved). E1-E8 relabeled EHanson1-8; the overnight tribunal verdict
  added as EHanson9. Rewrote case.md around the combined systemic claim
  (Hunter + Hanson + enforcement vacuum), not the Hanson-only flicker.
- found (new this session, source-verified, not desk-derived-only):
  - EHunter1: rebuilt derived_convicted_lobbyist_register against a scratch
    copy of the live gain.db (table was not standing in gain.db as of this
    session) to confirm current, not stale — Hunter 144165: 1 disclosure (the
    RR, filed 2023-10-15, self-posted "Duncan Hunter"), then 0/6 subsequent
    quarterlies disclosed (Q1/Q2/Q3/Q4 2023, Q1/Q2 2024), all for VALOON LLC
    representing Trex Enterprises Corporation.
  - EHunter2: the RR disclosure text (verbatim, 2019-12-03 plea, 18 U.S.C.
    §371, campaign-fund conversion) — establishes VALOON/Hunter's own
    predicate judgment is on record, in writing, post-pardon.
  - EHunter3 (the discriminator): posted_by_name = "Duncan Hunter" on ALL 7
    filings, RR through the last missing quarterly, no preparer change —
    forecloses the clerical-handoff explanation that (correctly) killed the
    standalone Hanson story. No boundary event either: the RR (disclosed) is
    filing 1 of 7; every later filing by the same hand is missing it.
  - EHunter4: cross-referenced the JACK Act notice's own text (no lookback,
    silent on pardons, "once required, required on every future filing") —
    no clean legal off-ramp; VALOON's own Oct-2023 RR disclosure (3 years
    post-pardon) already resolved the pardon question against exemption.
  - E-GAO: fetched and read GAO-26-108486 (2025 Lobbying Disclosure
    compliance report, published 2026-06-30) directly via PDF text
    extraction (uv + pypdf; WebFetch's inline extraction failed on the raw
    PDF, standard tool couldn't render pages locally — poppler not
    installed). Confirmed: zero JACK Act civil/criminal enforcement actions
    or prosecutions since the law's 2019 enactment (p.9); GAO's own
    compliance check ran criminal-background screens on a random 247-lobbyist
    sample and found zero convictions — a base-rate artifact, not a
    diligence finding, since the sample was never conditioned on having a
    conviction (Enclosure IV, p.28); the standing USAO referral mechanism
    (12,391 referrals since 2016) triggers on non-filing, not on a filed
    report silently missing one field. Saved to sources/ (PDF +
    gao-jack-act-enforcement-2026.md notes).
  - E-register: re-confirmed the 18-lobbyist register on rebuild; framed
    explicitly as context/scope-bound (2 clear outliers: Hunter, Hanson —
    not a corpus-wide pattern), so the case doesn't overclaim breadth.
  - Novelty-lite (Hunter): LegiStorm covered his 2023 registration, the
    Trex/earmark/pardon backstory — nothing on the disclosure-gap pattern
    itself. Miss.
- surprises: Hunter's case is structurally the stronger of the two chapters
  precisely because it has NO ambiguity Hanson's had — no boundary event, no
  preparer change, and the one filer whose own hand wrote the disclosure
  once is the same hand that omitted it six times after.
- dead ends: none new; Hanson's docket pull remains blocked (CourtListener
  403/401), carried over as owed.
- NEXT: run this case (Hunter + Hanson + E-GAO, as one combined systemic
  claim) through builder -> skeptic -> judge — explicitly instruct the
  skeptic to attack the SYSTEMIC framing (is 2 outliers + 1 enforcement
  report enough to say "the law fails at the edges," or does it need a
  third instance / a different comparison set?), not re-litigate either
  filer's individual facts, which are already source-verified.

## 2026-07-07 (editor session — case-level novelty scan)
- did: ran the case-level novelty scan (owed since the restructure) per
  reference/prior-art.md — 6 bounded WebSearch queries covering: general
  JACK Act enforcement, GAO report coverage, the disclosure-gap pattern
  generically, Hunter/VALOON/Trex by name, the GAO methodology critique
  specifically, and Hanson/VVA by name. Updated case.md frontmatter
  (`coverage: unscanned` -> `novel`) and rewrote the Prior coverage section.
- found: no coverage anywhere of (a) either filer's disclosure-gap pattern,
  (b) the combined systemic claim, or (c) the GAO-methodology base-rate
  argument. Law-firm alerts (Ballard Spahr, Steptoe, Kelley Drye, Arnold &
  Porter, Whiteford Taylor) all cover 2019 passage only, none revisit
  compliance since. One new corroborating detail: Federal Register + 
  OpenSanctions both confirm Hanson's BIS order is administrative
  (export-control), not a criminal conviction in the traditional sense —
  strengthens EHanson3's wrong-instrument point rather than complicating it.
  GAO's own recent-years numbers (247-258 lobbyists sampled per year,
  zero disclosable convictions each time) are consistent across the
  2019-2025 report series — corroborates E-GAO's base-rate-artifact read.
- verdict: **novel**, hedged per the asymmetry rule (miss = weak evidence,
  not proof of absence). Recorded in case.md; not yet logged to the actions
  journal (newsroom.db) — should be, action='novelty-scan', priority 4,
  before this leaves provisional status.
- open: sources/ directory referenced in case.md's "Outside data" section
  (jack-act-notice.md, gao-jack-act-enforcement-2026.md, the saved GAO PDF)
  does not exist on disk as of this session — either those saves didn't
  land or were lost; needs a check before publication since case.md cites
  them as disclosed outside data.
- NEXT: this was the user-requested first step in an editor pass to
  close out this case (finish/close vs. kill vs. park). Novelty is now
  clear (favorable). Remaining before a close/kill decision: reconcile the
  missing sources/ directory, and decide whether to run builder->skeptic->
  judge on the combined systemic claim (still owed per the restructure
  session) before closing, or close on the strength of the filing-level
  facts + this novelty result alone.

## 2026-07-07 (editor session — sources relocation + GAO methodology cross-check)
- did: (1) moved the case's outside data from top-level `sources/` to
  case-local `investigations/jack-act-blind-spots/sources/` (`git mv` x5:
  jack-act-notice.md + its source PDF, gao-jack-act-enforcement-2026.md +
  its source PDF, bis-order-harold-hanson-2013.pdf) — top-level `sources/`
  is reserved for data that feeds `gain.db` builds (per
  reference/data-layers.md), and this case's outside data doesn't. Fixed
  the one live cross-reference outside the case (`recipes.md`) to the new
  path; left the historical NOTES.md entry alone (point-in-time log, wrong
  slug already). (2) At the editor's request, fetched and cross-checked all
  6 prior annual GAO LDA compliance reports (2019-2024 coverage,
  GAO-20-449 through GAO-25-107523) against the 2026 report's methodology.
- found: same stratified-random-sample methodology every year since the
  JACK Act took effect, and the identical result every year — zero sampled
  lobbyists disclosed a conviction, across 2019-2025 coverage (7 reports).
  Sample sizes 161-268 individual lobbyists/year. One near-miss in
  GAO-22-105181 (2021 coverage): GAO found "information relevant to the
  JACK Act for one lobbyist" but couldn't locate court records — unnamed,
  unresolved, same records-access wall as this case's own Hanson docket
  pull. Wrote up as new evidence item E-GAO-series (evidence.md) and a new
  source note (sources/gao-jack-act-enforcement-2019-2024-series.md).
  GAO's CDN blocks direct `curl` fetches (Akamai/Edgesuite Access Denied);
  worked around via WebFetch (which downloads the binary even when its own
  text extraction fails) + local `pypdf` extraction, same pattern as the
  2026 report in the restructure session.
- surprises: none on substance — this is confirmatory, not new direction.
  The finding *strengthens* the systemic claim's second pillar: the
  base-rate-artifact critique isn't a one-year quirk, it's how the audit
  has worked for the JACK Act's entire lifespan.
- dead ends: none.
- open questions: unchanged (Hanson docket pull, still blocked; comment from
  VALOON/Hunter and VVA; builder->skeptic->judge on the combined systemic
  claim, still owed).
- NEXT: same as before this session — decide whether to run the tribunal on
  the combined claim before closing, or close on current evidence + the
  now-clear novelty result. The GAO-series finding is now available either
  way it goes.

## 2026-07-07 (editor session — enforcement-landscape check)
- did: editor asked whether any enforcement/audit mechanism exists for the
  JACK Act besides GAO. Ran 6 bounded web searches covering: private right
  of action/qui tam, House/Senate Ethics Committee jurisdiction, and the
  statutory text + practical operation of the Secretary of Senate/Clerk of
  House's own "review for accuracy" role (2 U.S.C. §1605), cross-checked
  against GAO-26-108486's own definitions of "referral"/"noncompliance"
  (already saved in sources/, no new fetch needed for that part).
- found: no other enforcement channel exists. (1) No qui tam/private right
  of action under the LDA — enforcement is Secretary of Senate + Clerk of
  House + DOJ/USAO only. (2) Lobbying disclosure has been outside House/
  Senate Ethics Committee jurisdiction since the 95th Congress (1977-78,
  moved to Judiciary) — ethics committees' financial-disclosure role is a
  separate track. (3) The Secretary/Clerk offices' own statutory "review...
  for accuracy" language (2 U.S.C. §1605) is broad on its face, but GAO's
  report defines "referral"/"noncompliance" exclusively as failure-to-file,
  never as a filed-but-incomplete report, in three separate places — no
  source found describing those offices cross-checking a filed LD-2's JACK
  Act line against an outside conviction record. That check only happens in
  GAO's own bounded annual sample. Wrote up as new evidence item
  E-enforcement-map (evidence.md); added a summary sentence to case.md's
  hypothesis section (enforcement-layer bullet).
- surprises: none structurally — confirms the case's implicit assumption
  (GAO + USAO referral pipeline is the whole system) rather than revealing a
  gap the case had missed. Good news for the "nobody checks" framing: it's
  not just that the one process meant to catch this can't; it's that no
  other process exists at all.
- dead ends: Congress.gov CRS report RL34377 (the authoritative CRS product
  on the Secretary/Clerk's role) blocked WebFetch with a 403 — could not get
  a direct quote from CRS confirming the accuracy-vs-completeness
  distinction. Point (3) above currently rests on GAO's own operational
  language (three independent mentions, consistent), not a CRS or statutory
  source stating the limitation explicitly — flagged as a caveat in
  E-enforcement-map, worth a follow-up fetch (e.g. via a different route
  into Congress.gov, or the LDA guidance PDF directly) before treating it as
  airtight for publication.
- open questions: unchanged (Hanson docket pull; comment from VALOON/Hunter
  and VVA; builder->skeptic->judge on the combined systemic claim). Add: the
  CRS RL34377 fetch, if the accuracy-review point needs to be load-bearing
  in the eventual write-up.
- NEXT: unchanged — tribunal decision vs. close-now decision is still the
  open fork.

## 2026-07-07 (editor session — CRS RL34377 correction)
- did: editor supplied a direct copy of CRS Report RL34377 ("Lobbying
  Registration and Disclosure: The Role of the Clerk and Secretary,"
  updated 2021-11-29), the exact source the prior session's
  E-enforcement-map flagged as needed but couldn't fetch (Congress.gov
  403'd WebFetch). Saved to sources/, extracted with pypdf, read in full
  (14 pages).
- found: the prior session's point (3) — "the Clerk/Secretary's accuracy
  review is filing-existence-only, same as GAO's referral trigger" — does
  NOT hold up against the actual CRS text and needed correction, not just
  addition. RL34377 (p.3) states the Clerk's Legislative Resource Center
  and the Secretary's Office of Public Records "have been given
  responsibility for reviewing each filing to ensure accuracy" as a duty
  presented separately from, and prior to, the 60-day-notice/USAO-referral
  process — not folded into it as the earlier version assumed. The report
  gives no further detail on what that accuracy review entails in practice
  (no statement on whether it's a substantive content check or a lighter
  completeness pass) and never connects it to the JACK Act field
  specifically. Corrected E-enforcement-map's verdict on this sub-point
  from "supports" to "needs-more" — the honest state is that this duty
  exists, is undocumented in depth, and no source (CRS or GAO) describes it
  ever catching a JACK Act gap — not that it structurally couldn't. Updated
  case.md's enforcement-layer bullet to match (no longer claims the
  Secretary/Clerk review is "filing-existence-only"; now flags it as an
  affirmative, distinct, under-documented duty).
- surprises: this is a case where the caveat flagged in the same evidence
  item, one session prior, turned out to be load-bearing — good discipline
  validated (flagging "rests on inference, not a direct quote, get the
  source" caught a real overreach before it could enter a write-up).
- dead ends: none — this closes the CRS follow-up that was the one open
  item from the enforcement-landscape check.
- open questions: unchanged (Hanson docket pull; comment from VALOON/Hunter
  and VVA; builder->skeptic->judge on the combined systemic claim). The
  Clerk/Secretary accuracy-review depth remains genuinely open — would need
  a records request or interview to resolve, not a desk source; not
  pursued further this session, flagged as out of scope for the current
  evidence-gathering phase.
- NEXT: unchanged — tribunal decision vs. close-now decision is still the
  open fork. The correction here should make that tribunal's job easier,
  not harder: one fewer overstated claim to catch.

## 2026-07-07 (editor session — corpus-wide disclosure-gap check + combined-claim tribunal)
- did: (1) editor asked, ahead of the tribunal, whether Burkman/Wohl (the
  corpus's two mega-filer convicted lobbyists) have undiscovered disclosure
  gaps of their own, and wanted a verified corpus-wide missing-disclosure
  percentage. Rebuilt `derived_convicted_lobbyist_register` fresh and
  queried it directly (`q-corpuspct`, evidence.md E-corpuspct). (2) Ran the
  builder->skeptic->judge tribunal on the combined systemic claim (Hunter +
  Hanson + enforcement-vacuum, as one claim per the restructure's explicit
  instruction) — the last owed item before a close/kill decision, per every
  prior session's NEXT note.
- found: (1) Burkman 0/471 missing, Wohl 1/182 missing (his one gap is his
  earliest quarter, a boundary effect consistent with EHanson9, not a new
  chapter) — neither is a third/fourth gap case. Corpus-wide: 1.13% of all
  post-conviction quarterly filing-**instances** lack the disclosure
  (877/887 disclosed, 15 lobbyists with post-conviction quarterlies); at
  the lobbyist level, 3 of 15 (20%) have >=1 gap quarter, 12 of 15 have
  zero. Excluding Burkman/Wohl as an autofill-dominated population: 3.85%
  (9/234). (2) Tribunal verdict: **Supported, high confidence.** Skeptic
  ran the full corpus checklist (namesake/identity, House+Senate
  double-counting, multiple comparisons, base rate, junk-text/sparse-data
  applicability, correlation-vs-causation applicability) and could not
  refute the core claim. The base-rate check (using the new E-corpuspct
  figures as the skeptic's strongest material) does not kill the claim —
  a low aggregate corpus-wide rate is consistent with "rare and genuinely
  unchecked" (the case's actual framing, not "widespread," which it
  already disclaimed) and doesn't bear on whether GAO's audit mechanism is
  structurally positioned to catch a gap if one occurs (it isn't,
  independently established by E-GAO/E-GAO-series). One surviving scope
  caveat carried forward, not a refutation: Clerk/Secretary accuracy-review
  depth remains undocumented (E-enforcement-map's existing "needs-more").
- surprises: none structurally — the corpus-wide percentage was the
  tribunal's most plausible kill-shot ("if it's only ~1%, this isn't a
  systemic story") and it didn't land, because the case's claim was never
  "widespread," it was "rare, real, and unchecked." Good discipline
  validated: E-register's "not a corpus-wide epidemic" framing, written
  before this check existed, held up exactly as stated once tested.
- dead ends: none.
- open questions: unchanged pre-publication line items (Hanson docket pull
  — sentence/vacatur, still blocked by CourtListener bot protection; comment
  from VALOON/Hunter and VVA) — these are closeout/publication items, not
  open verification questions per the judge's verdict.
- NEXT: run closeout (reference/closeout.md) — condense case.md's Verdict
  to a single current paragraph, confirm frontmatter matches, list
  pre-publication line items. Status should move from `open` toward
  `closed` once that's done; this session leaves it at "open (verified —
  ready for closeout)" rather than flipping status directly, since
  closeout is its own checklist not yet run.

## 2026-07-07 (editor session — closeout)
- did: ran the closeout checklist (Path 2 — close it out, per
  track-investigation/reference/closeout.md). Condensed case.md's Verdict
  section from the tribunal session's accreted builder/skeptic/judge prose
  to a single current paragraph (full tribunal reasoning stays in
  evidence.md's E-tribunal, not deleted, just not duplicated in case.md).
  Set frontmatter: status open -> closed, confidence -> high (matches the
  judge's actual verdict, not a stale pre-verification value), coverage
  already novel from the 2026-07-07 scan (no change needed, confirmed not
  stale). Cleaned the "Owed before publication" list in Sources/legal-risk
  notes to only the 3 genuine pre-publication line items (Hanson docket
  pull, VALOON/Hunter + VVA comment, possible counsel comment) — removed
  "full case-level novelty scan" since that's done and cited above it.
- found: nothing new — this was a writing/frontmatter pass, not a data
  pass. Confirms the prior session's judge recommendation (close, not kill
  or park) was actionable as stated.
- surprises: none.
- dead ends: none.
- open questions: the 3 pre-publication line items listed in case.md's
  Sources/legal-risk notes section — none of them are open verification
  questions, all are publication-stage (documents to pull, people to call).
- NEXT: none for data/verification work — case is closed. Publication
  stage: pursue the 3 pre-publication line items when this case's chapter
  of the findings report is being drafted. If a future session finds new
  evidence that bears on this case (e.g. a records-request answer on the
  Clerk/Secretary accuracy-review depth), re-open per the skill's status
  vocab rather than starting a new case.

## 2026-07-15 — post-closeout addendum: second undisclosed VALOON registration

- Context: submission bundle reproduce-verification pass (curating
  reproduce/queries/jack-act-blind-spots.sql for the contest submission); the
  verifying agent's unrestricted Hunter sweep returned 10 filings, not 7.
- Added E-hunter-njf + q-hunter-njf: VALOON's second registration (client NJF
  Worldwide, `6c0afe7d…`, posted 2023-12-01) lacks the conviction disclosure,
  as do two termination filings. 1 of 10 Hunter filings discloses.
- Findings-report Hunter bullet extended with the one-line version.
- Direction conservative (gap understated before); no counted claim changes;
  case stays closed. No new NEXT.
