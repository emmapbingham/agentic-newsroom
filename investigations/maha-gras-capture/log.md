# Log — maha-gras-capture

## 2026-06-25
- did: promoted from leads (slug=foo-fda-reform-rfk-lobby, screen_run_id=16);
  opened case files; seeded evidence blocks E1-E5 from session drilldown
- found: see E1 (FOO surge), E2 (GRAS lobby descriptions), E3 (competing bills),
  E4 (Hyde-Smith/258 groups), E5 (MAHA press gap)
- dead ends: FOO n_press_releases=0 is a keyword-coverage artifact — cannot use
  derived table press column for FOO; queried press_releases directly instead.
  Seed oil press = 4 releases in 2025 — genuinely sparse, not a data gap.
- open questions:
  1. Does S. 3122 actually contain federal preemption language? Need bill text.
  2. Which specific filing UUIDs show ADM/Conagra/Cargill naming S. 3122?
     Log them for provenance.
  3. Did any member who took food industry contributions cosponsor S. 2341
     (Booker/Markey)? Say-vs-pay angle.
  4. Is there a contribution signal — did food industry PAC money flow toward
     Britt/Marshall and away from Booker/Markey supporters?
  5. Was GRAS or preemption language inserted into OBBBA or any appropriations
     vehicle? (Some lobbying descriptions mention OBBBA.)
- NEXT: Verify E1 (re-derive FOO z-score cleanly). Then pull specific filing
  UUIDs for E2 (ADM, Conagra, Cargill GRAS descriptions). Then check
  contribution flow to Britt/Marshall vs Booker/Markey (say-vs-pay, E6).

## 2026-07-02
- did: verified E1 (confirmed z=6.14, issue-specific not base-rate noise —
  see queries.sql#q1b). Re-ran E2 with full dedup — found 25 clients not 7;
  American Beverage Association is the one unambiguous S.3122-only citation;
  IDFA/Pharmavite/EDF name BOTH bills neutrally, complicating the clean
  "industry=pro-weak-bill" framing; caught a false-positive risk (Abbott/Apeel
  citing S.3387, a same-titled 2023 predecessor, not current S.2341). Retrieved
  S.3122 bill text/status: confirmed NO preemption provision in the bill AS
  INTRODUCED/CURRENT — it was drafted in, then REMOVED after MAHA pushback
  (Marshall responded to "MAHA moms"). Ran E6 say-vs-pay: food-industry PACs
  gave Marshall ~$53.5K, Britt ~$16.5K, Cammack ~$7.5K (all high-conf honoree
  matches); Booker $5.3K from one minor PAC; Markey $0 from any food PAC.
  Clear asymmetry, confirmed by data.
- found: **Novelty scan changes the picture substantially.** This is
  well-covered ground: Food Dive has a running series (Oct 2025 "Food industry
  prepares to fight MAHA in states"; Nov 2025 "Congress appears unwilling to
  stop state ingredient bans"; Dec 2025 "How MAHA transformed the food
  industry"); Food Safety Magazine explicitly headlined "MAHA Pushback Kills
  'Big Food'-Aligned Legislative Effort to Stop State Food Laws"; Civil Eats,
  POLITICO Pro, NOTUS, Agri-Pulse all covered the preemption removal in real
  time (Nov 2025). As of Q1 2026, NOTUS reports lobbying orgs on GRAS reform
  nearly tripled (12 -> 35 orgs) after Kennedy directed FDA to explore closing
  the loophole; the live co-optation vector industry has rallied around is now
  Rep. Kat Cammack's narrower HOUSE bill (not S.3122, whose preemption clause
  is dead), per POLITICO Pro ("Food industry lines up behind House bill to
  deflect RFK Jr.," June 2026) and NOTUS ("Lobbying Groups Are Coming for RFK
  Jr.'s Fight to Regulate Food Additives").
- dead ends: none new. S.3387 (2023 predecessor to S.2341) false-positive
  caught and excluded from E2 citations.
- open questions: does the case pivot to the Cammack bill (unreported-with-data
  angle, live as of June 2026), kill outright (core hypothesis as originally
  framed is refuted — preemption fight was public and MAHA won it), or
  reposition as a precision data exhibit on the S.3122/Marshall period using
  E6's verified say-vs-pay numbers? User asked for a plain narrative summary
  before deciding — see next turn.
- NEXT: awaiting user decision on case direction after narrative summary.

## 2026-07-02 (cont.)
- did: corrected an overstated claim (said FRESH/Cammack bill was "less
  public" than S.3122 -- user pushed back, right call: EWG/CSPI/Food Safety
  News backlash was fast and loud, not quiet). Confirmed data cutoff is 2026
  Q1 (Senate filings latest 2026-04-21 = Q1 deadline; press releases end
  2026-03-31) -- FRESH Act (~April 2026) is outside corpus, cannot be
  evidenced with LDA data. Pivoted to user's sharper question: is there a
  registered "MAHA lobby" at all? Answer: no (E7) -- 25 industry clients vs 3
  advocacy-ish clients (CSPI/ANH/GFI) on GRAS, zero MAHA-branded registrants
  anywhere. Quantified spend imbalance but caveated hard: LDA reports spend at
  filing level (all issues), not per-issue, so $70.58M-industry-vs-$75K-
  advocacy is not an apples-to-apples "GRAS spend" number -- ADM's filings
  cover ~10 issue codes each, CSPI's cover 1. Web search found a qualitative
  echo of this (Georgetown's Gostin: industry political spending "far more
  than tobacco" while "MAHA...doesn't do much") but no one's quantified the
  registered-lobbying organizational asymmetry the way E7 does -- likely
  genuinely novel framing.
  User then asked for the bigger pattern: what other issues look like K-street
  vs. the public, and how often does the public win. Scoped this carefully --
  corpus can show WHERE the imbalance exists (registered lobbying presence)
  but has NO signal for "did the public win" (that's bill-outcome tracking,
  external per-case research, not a SQL query). Built E8: tried a name-pattern
  heuristic first, it failed (caught industry coalitions with advocacy-sounding
  names). Built instead a manually-verified 16-org advocacy list, screened all
  2025 issue codes with 200+ clients. Result: Environment, Agriculture,
  Consumer Safety, Food, Computer Industry, Pharmacy all show heavy imbalance;
  Insurance, Medical Research, Real Estate, Utilities show ZERO advocacy
  presence from the curated list. Sanity check caught 3 Insurance clients with
  consumer-sounding names that are actually industry trade groups --
  reinforces why this must stay curated, not keyword-matched.
- found: E8 is real but is a SCREEN/lead-generator, not a finding -- each
  candidate issue code (Environment, Insurance, etc.) would need its own
  case-style drilldown before any capture claim. It's also structurally
  one-sided: it can only see the K-Street side. The public-pressure side (like
  MAHA's actual win against S.3122 preemption) is invisible to LDA data by
  construction -- has to come from outside research on a per-case basis, same
  as we just did for GRAS.
- dead ends: name-pattern advocacy heuristic (coalition/foundation/center for
  keyword matching) -- caught industry-funded groups with sympathetic names,
  abandoned in favor of curated list.
- open questions: does E8 get formalized as a proper named screen via
  generate-query-ideas (recommended -- it's reusable beyond this case), or
  stay a one-off case artifact? Which of the imbalanced issue codes (if any)
  get their own case-style outcome drilldown?
- NEXT: user to decide whether to (a) formalize E8 as a screen, (b) pick one
  or more candidate issue codes for outcome drilldown, or (c) close out
  maha-gras-capture as-is with E1-E8 as the final evidence set and move on.

## 2026-07-02 (closeout)
- did: formalized E8 as newsroom.db screen id=34 `advocacy-desert-issues`
  (population-structure contrast). Wrote
  investigations/screens/advocacy-desert-issues/screen.sql with full method
  notes (curated roster, why name-matching failed, what the screen can/cannot
  show). Logged the already-completed 2026-07-02 run as screen_runs row
  (10 candidates surfaced, no leads promoted from this run — registration
  only). No fleet sweep run; this was direct registration of validated SQL,
  per user's request to avoid spending sweep tokens.
  Closed maha-gras-capture per closeout checklist: status -> closed,
  confidence -> medium, coverage -> well-covered (legislative narrative) /
  novel (organizational-asymmetry framing). Condensed Verdict to current
  single-paragraph state (was an accreted "Open, no verified claims" stub).
  User explicit: not being killed (still newsworthy), not going into the
  findings report as a headline finding, kept as a precision exhibit + as the
  template case for future advocacy-desert-issues follow-ups.
- found: n/a (closeout, no new evidence)
- open questions: which (if any) advocacy-desert-issues candidate code
  (Insurance, Environment, Medical Research, Real Estate, Utilities) gets
  promoted to its own case next, via a future fish-for-leads run using screen
  id=34.
- NEXT: none for this case (closed). Future work continues via
  fish-for-leads against the advocacy-desert-issues screen.
