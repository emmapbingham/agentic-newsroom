# Log — barr-credit-union-cfpb-loop

## 2026-07-06
- did: promoted from leads (slug=barr-credit-union-cfpb-loop,
  screen_run_id=36 — first run of the client-mention-honoree-triangle
  screen, built this session on the client-alias entity-resolution
  pipeline). Case seeded with the surfacing-session drilldown: the pair
  (E1), the dated money timeline incl. the 2025-02-20 "Barr for Senate"
  item filed the day McConnell announced retirement (E2), the NAFCU-legacy
  $6k (E3).
- found: see E1–E3. Editor (Emma) judged this the strongest Politico-shaped
  lead so far; promotion rationale = arc with dates, live Senate race,
  every link in public records.
- dead ends: none yet.
- open questions: (1) verify 2025-02-20 item on the LD-203 filing itself
  (6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4) + FEC committee records — the date
  precedes his formal April announcement and could be a reporting artifact;
  (2) base rate: ACU's full honoree footprint (q4) — is Barr exceptional or
  median for Financial Services members?; (3) full registrant stack honoring
  Barr around the pivot (q5) — who else was "day one"?; (4) ACU activity
  descriptions naming UDAAP/TABS (q6); (5) official bill introduction dates
  from Congress.gov vs contribution dates; (6) exact ACU endorsement quotes
  from the three releases (press_releases.text).
- NEXT: run q4 + q5 (base-rate and pivot-stack checks) — these decide
  whether the story is "ACU and Barr" or "the financial industry and Barr,
  ACU as the clearest thread."

## 2026-07-07
- did: six evidence chores E4-E9. Ran drafted q4/q5/q6 + sub-queries q4b/q4c/
  q5b/q6b/q7/q8 against db/gain.db (read-only); all LD-203 sums deduped to
  DISTINCT (contributor,payee,date,amount), honoree confidence >= 0.9. Two
  outside fetches (disclosed): LDA API for filing 6acc01c1 (E8) and FEC API
  DEMO_KEY committee C00467571 (E9). 7 web fetches used (budget 8).
- found:
  - E4 (base rate): Barr $40k = rank 5 of 527 ACU honorees (median ~$10k,
    max $50k). Top-tier, ~4x median — does NOT kill the story on scale; but
    ACU gives leadership money bipartisanly (top 4 are Dem leaders), so $40k
    is a normal top-tier committee figure, not a singular outlier. SUPPORTS.
  - E5 (pivot stack): the big one. ACU is NOT day-one and NOT the biggest.
    Ten registrants gave Barr more (Carlyle $52.5k, ABA $47.5k...); ACU ~11th.
    FIVE registrants reported to "ANDY BARR FOR SENATE, INC." BEFORE ACU's
    2025-02-20 (earliest Cresco Labs 2025-01-31). The Senate committee was
    reporting money 3 weeks before McConnell's announcement. WEAKENS the
    "day-one / very day McConnell announced" hook -> dating coincidence.
  - E6: ACU's 2025-2026 Senate lobbying descriptions name both Barr bills by
    number -- "Support Taking Account of Bureaucrats Spending Act (H.R. 654)
    Support Rectifying UDAAP Act (H.R. 1652)". Note: acronym "TABS" never
    literally appears; %Barr% LIKE hits are false positives. SUPPORTS (strong).
  - E7: 2025-01-23 and 2025-05-03 releases quote "America's Credit Unions" by
    name (Jim Nussle); 2023-12-15 quotes CUNA+NAFCU (predecessors), not ACU.
    In all three ACU is one of a 4-5-endorser industry wall (ABA/CBA/ICBA/
    AFSA/ACA) -> endorsement-quote practice is industry boilerplate, not
    ACU-specific (refute condition (c) partly lands). SUPPORTS w/ caveat.
  - E8: verified against source LDA filing JSON -- row 2025-02-20 $5,000.00
    "ANDY BARR FOR SENATE, INC." honoree "Rep. Andy Barr" feca, contributor
    "AMERICA'S CREDIT UNIONS PAC", present verbatim, matches ingest. SUPPORTS.
  - E9: "Andy Barr for Senate, Inc." (FEC C00467571) is Barr's ORIGINAL 2009
    House committee (cand H0KY06104) REDESIGNATED to Senate (cand S6KY00286)
    for 2026. Pre-existing/redesignated => 2025-02-20 contribution is genuine
    and plausible, NOT a check/attribution artifact. Confirms committee
    predated McConnell announcement -> reinforces E5.
- dead ends: %TABS% and %Barr% string screens on ACU lobbying (false-neg /
  false-pos respectively); LDA human filing page 404s on fetch (use the
  /api/v1/contributions/ path); WebFetch small-model summaries missed the
  target row in a 368-item JSON (raw JSON scan needed).
- open questions / owed: (1) exact FEC redesignation date for C00467571
  (Form 1/2 amendment) -- E5/E9 bound it to <= 2025-01-31 via LD-203, but the
  primary FEC date is still owed; (2) official Congress.gov introduction dates
  for H.R. 654 / H.R. 1652 vs contribution dates (carried over from E2).
- NEXT: the timing hook (E5/E9) is materially weaker than the seed framing --
  editor call on reframe to "the financial industry and Barr, ACU as the
  clearest endorse->legislate->pay thread" before builder->skeptic->judge.
  Verdict in case.md left unchanged per scope.

## 2026-07-07 (overnight, agent-auto — PROVISIONAL)
- did: builder → skeptic → judge on E1–E9 (Opus builder/skeptic, Fable judge).
  Verdict written to case.md; status open → parked.
- found: facts all verify (skeptic re-derive exact; nits: "tied for 5th",
  "10th of 419"). Story refuted: timing hook dead (E5/E9); no uniqueness —
  ACU runs the same triple with ≥5 members incl. 3 sitting senators
  (Cramer/Scott/Budd; also Fitzgerald HUMPS Act, Emmer anti-CBDC), 10 ACU
  pairs in screen 36 alone; ACU is a pipeline cherry-pick (ABA gave $47.5k
  AND endorsed, invisible to the mention screen — alias-reachability
  selection effect, now a documented bound).
- judge's call: park the Barr-centric case; surface the systemic reframe as
  lead `acu-legislative-bench` (novelty-lite miss; skeptic's member table is
  the seed). E1–E9 become the Barr chapter if the bench story is promoted.
- also: the alias-reachability bound (trade associations members don't
  name-check are invisible to mention screens) added to the hardening
  agenda — it biases WHICH entity a pair-screen surfaces.
- NEXT: editor review (actions queue, priority 5); if bench story promoted,
  first chores = replicate the triple for each of the 10 members + ABA/ICBA
  equivalents (is ACU's bench denser than peers'?) + Congress.gov dates.

## 2026-07-07 (editor session — closeout)
- did: editor (Emma) promoted `acu-legislative-bench` per the judge's
  recommended path (separate session/case). Caught on review that this case
  itself was left at status=parked with its overnight verdict/close actions
  still unreviewed, even though it had already been superseded. Closed out
  properly: condensed Verdict to a single current paragraph per the
  closeout checklist, fixed frontmatter (status -> closed, confidence -> high
  on the facts, coverage -> well-covered as a standalone component / tracked
  separately for the systemic angle), added the pre-publication line-items
  list to Sources/legal-risk notes (FEC redesignation date, Congress.gov
  bill dates, Barr/ACU comment).
- found: nothing new — this is a closeout pass, not a research session.
- dead ends: n/a.
- NEXT: none for this case — see `investigations/acu-legislative-bench/` for
  all active work. This file stays as the standalone record of the
  Barr-only framing test.
