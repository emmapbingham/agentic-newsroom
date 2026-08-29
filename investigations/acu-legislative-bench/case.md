# America's Credit Unions' legislative bench — a say-pay cycle, run at scale

- **slug:** acu-legislative-bench
- **status:** killed (ACU-distinctiveness claim only — reopened 2026-07-09 as the findings-report
  demo of the say/pay/lobby/bill methodology, not to overturn the kill; see Verdict)
- **confidence:** low (as a newsworthy claim about ACU specifically — E10 stands); high (as a
  demonstrated, quantified methodology — E11's typology, re-derivable per member)
- **coverage:** unscanned (surfacing-time novelty-lite only — case killed before a full scan was
  warranted; see Prior coverage)
- **opened:** 2026-07-07   **last updated:** 2026-07-09 (bench now 11 members, Peters added per E13/E14)   **killed:** 2026-07-08

## Hypothesis

America's Credit Unions (ACU, formerly CUNA, merged with NAFCU Jan 2024) runs
the same three-part circuit with at least five members of the banking
committees, not just Rep. Andy Barr: (1) the member introduces or champions a
CFPB-curbing or credit-union bill, (2) ACU's own sworn Senate lobbying filings
list support for that bill by number, and (3) ACU's LD-203 filings report
top-tier honoree money to that member — with (4) ACU's endorsement quote
appearing in the member's own press release, where the mention pipeline can
see it. Candidate bench: Barr (UDAAP/TABS), Cramer (late-fee rule
disapproval), Tim Scott (small-business lending), Fitzgerald (HUMPS Act),
Budd, plus Emmer (anti-CBDC) and Britt — three of whom (Cramer, Scott, Budd)
now sit in the Senate.

This case has **two deliverables**, not one:
1. **The finding** — a documented case study of a say-pay cycle (what a
   member says publicly, what money follows, what the sworn filings show)
   running at trade-association scale, not as a single-member story.
2. **The methodology** — validating and hardening the mention-filing-LD203
   triple-join as a reusable detection technique, including its known blind
   spot (see below).

## Why it's newsworthy

The Barr chapter (this case's own predecessor, `barr-credit-union-cfpb-loop`)
found every link of an endorse→legislate→pay loop in public records with
dates — but the skeptic's attempt to kill it as a Barr story instead found
the same loop running across at least five members of both parties, bipartisan
down to Beatty/Vargas/Gonzalez, three of them now senators. That reframe is
the actual story: not one member taking money, but one association's
documented *legislative bench* — a repeatable production line for turning
model bill language into press-release endorsements into sworn lobbying
support into contribution dollars, fully citable from ACU's own filings. It
also exposes a structural blind spot worth reporting on its own: the mention
pipeline only sees associations that members *name-check* in their own
releases — ABA gave Barr more money and endorsed the identical bills but is
invisible to mention-based screens (a selection effect, not an absence of
influence).

## What would confirm it / what would kill it

- **Confirms:** replicating the Barr triple (E1/E6/E7 pattern: honoree money +
  named-bill lobbying support + press-release endorsement quote) for each of
  Cramer, Scott, Fitzgerald, Budd, Emmer, Britt, at a similar scale/tier to
  Barr's; the resulting bench being denser or more explicit (named bill
  numbers in sworn filings) than peer associations' equivalents.
- **Refutes / boring:** this is just what every large trade association does
  — committee government working as designed. The decisive check (the lead's
  own boring_explanation): replicate the identical triple for ABA/ICBA/MBA
  **outside the mention pipeline** (their bench, if any, won't be visible to
  a mention-seeded screen — must be built from lobbying + LD-203 alone). If
  their benches are equally dense, the story is generic trade-association
  behavior or nothing; if ACU's is denser or its bill-number language more
  explicit, ACU is the story.
- Also refutes/weakens if: per-member replication doesn't hold at the claimed
  scale (some of the 10 screen-36 pairs may not carry the full triple — each
  needs its own E1/E6/E7-equivalent, not assumed from the aggregate screen
  row); bill dates (Congress.gov, still owed) don't interleave sensibly with
  contribution/lobbying dates.

## Verdict

**Killed 2026-07-08.** The case claimed America's Credit Unions (ACU) runs a
distinctive, trade-association-scale "legislative bench" — the same
endorse→legislate→pay triple found for Rep. Andy Barr, replicated across at
least five more banking-committee members, framed as newsworthy because it
was a *documented production line*, not just one member. Per-member
replication (E1-E9) actually succeeded: 8 of 9 non-Barr bench members
independently confirmed the full triple (money + named-bill Senate lobbying
text + press mention), with 1 clean, non-partisan break (Beatty). That part
of the methodology holds and isn't in question.

What killed the case is **E10**: running the same screen the case was seeded
from, but without filtering to ACU, shows ACU's 10-member bench well down
the list of 192 clients by the identical money+mention pattern — behind
several other clients (Goldman Sachs (59), League of Conservation Voters
(44), Amazon (39), National Shooting Sports Foundation (34), Everytown for
Gun Safety (31), Intel (28), Boeing (25), and Microsoft (24) among them)
that show the pattern with more distinct members. ACU is
unremarkable-to-below-median within the very population the case's own
screen surfaces, not an outlier. This is the case's own pre-registered
`boring_explanation` — "this is just what every large trade association
does, committee government working as designed" — confirmed directly,
using the same screen and methodology the case itself validated, without
even needing the separately-planned ABA/ICBA/MBA build. A secondary,
independent tell: Andy Barr himself (the case's worked exemplar) shows the
identical triple with a second, unrelated client — the National
Thoroughbred Racing Association ($30,000, 6 mentions vs. ACU's
$40,000/3 mentions) — so even Barr's own pattern isn't ACU-exclusive.

**CORRECTION (2026-07-09, post-tribunal):** E10's original writeup also
reported ACU's exact rank (22nd of 192) and a specific multiplier against
the then-top-ranked client, Visa (84 members, "8.4x smaller"). Both figures
are withdrawn as stated. A separate client-alias review
(`investigations/derived/client_alias_review/consolidated_review_2026-07-06.txt`)
flagged exactly this kind of contamination risk in the corpus-wide alias
index — `VISA, U.S.A., INC.` matches on "visa" as a generic word
(immigration/travel visa), and "Goldman" appears as a bare, collision-prone
alias — and neither E10 nor this case's tribunal pass checked the ranking
query against that review before citing it. `VISA, U.S.A., INC.` is
correctly marked `rejected_too_generic` in the alias index and excluded
from E10's query already, but `VISA, INC.` itself (the exact string that
produced the 84-member, rank-1 row) and the Goldman Sachs aliases remain
un-reviewed `candidate` status — so rank 1 and rank 2 in E10's table could
themselves be inflated by uncaught false-positive matches. The directional
finding is unaffected (ACU's own 10-11-member count doesn't depend on any
other client's alias quality, and ACU still isn't the case's own screen's
top-ranked client), but no specific rank or multiplier should be quoted
until E10 is re-run against an alias-cleaned index. Findings-report
language reflects this: "not the biggest bench," no rank number.

The kill is scoped narrowly: it refutes "ACU's bench is newsworthy because
of its scale/distinctiveness." It does **not** refute the underlying
factual claims in E1-E9 (those are re-derivable and still true), and it does
**not** refute the case's second deliverable — the mention+filing+LD-203
triple-join as a reusable detection method, which worked correctly across
10 members and caught its own display bug (E0) along the way. That
methodology is this case's lasting output; the corpus-wide ranking table in
E10 needs the alias-cleanup re-run before it's a lasting output in its own
right. The two follow-on leads E10 surfaced (Visa's bench; Barr's second
client relationship) are handed off separately, not pursued in this case —
Visa's follow-on in particular now depends on the alias fix.

## Barr chapter (imported evidence — the worked exemplar)

The predecessor case `barr-credit-union-cfpb-loop` is this case's first
worked member. Its evidence (E1–E9) is imported into this case's
`evidence.md` unchanged and re-labeled `EBarr1`–`EBarr9` — re-verify by
re-running `queries.sql` there before citing; do not re-derive from scratch.
Barr chapter verdict, unchanged: every factual link verified; Barr-specific
timing hook (2025-02-20 "day McConnell announced" framing) is dead — the
Senate committee (FEC C00467571, redesignated) was already active weeks
earlier (EBarr5/EBarr9); ACU is ~11th by dollars among Barr's honorers, not
the top or the earliest. What survives and generalizes: ACU's Senate lobbying
filings name Barr's two bills by number in every quarter since introduction
(EBarr6), and its 2025 press-release quotes name ACU specifically (EBarr7),
alongside 4-5 other trade groups in each release (industry-boilerplate
caveat — also worth testing per-member).

## Methodology track (this case's second deliverable)

**The null model and its deviations (E15, 2026-07-09) — the lead frame for
the findings-report writeup.** Editor named three baseline patterns and
asked whether the signal is in deviations from them, not the patterns
themselves: (1) lobbying text follows bill introduction (near-tautological
by construction — bench members were found by searching lobbying text for
bill names); where it looks earlier, expect an earlier-Congress predecessor
bill with the same title; (2) press and bill introductions are coupled;
(3) money arrives on its own schedule, mostly independent of press/bills,
reinforced by money reaching hundreds of members who get neither. Checked
all three against the full 11-member bench: (1) confirmed, with the
predicted mechanism verified by bill number — only Vargas and Gonzalez show
lobbying starting before their tracked bill, and both cases resolve to a
117th-Congress predecessor bill (Vargas: H.R.6889, "Credit Union Board
Modernization Act," found in ACU's earliest matching filing but never
pulled via Congress.gov — a real gap in E8's bill inventory, not fixed yet;
corrected 2026-07-09 verify pass — an earlier draft misattributed this
title to H.R.7003, a different bill named in the same filing);
(2) confirmed, no new deviations; (3) confirmed, and this is where the
bench's real deviations concentrate: Britt (money entirely precedes bill/
press, E11), Peters (lobbying leg deviates via a stale bill number, E14).
This is a stronger, more falsifiable frame than "9 of 11 confirm a triple"
and should organize the findings-report writeup: state the null model,
then walk the named deviations as the actual story. Full writeup:
evidence.md E15.

**Beatty's deviation corrected (E7 revised, 2026-07-09):** editor spotted a
second Beatty bill this case had missed — H.R. 3709, "Advancing the
Mentor-Protege Program for Small Financial Institutions Act" (119th,
introduced 2025-06-04) — by reading the text of her unmatched 2025-06-05
press release, which carries a genuine named ACU quote (Jim Nussle) and
which ACU's lobbying text does name (1 filing, 2026 Q1). Beatty is no
longer a clean "lobbying absent" case; she has a split record across two
bills (H.R.5911: zero lobbying match, still a real negative result;
H.R.3709: a real, thin triple). This closes E11 item 4's "genuinely
absent" lobbying-continuity category entirely — every bench member now has
at least one bill with a confirmed lobbying-text match. Reframes Beatty
from "lobbying leg missing" to "ACU's endorsement is bill-specific, not
member-specific" — same member, same money, same press cadence, but only
one of her two bills gets sworn lobbying support. All 4 `derived/bench_*.csv`
files and both charts rebuilt.

**Systematic press-release-vs-bill pass (E16, 2026-07-09):** editor asked
for a systematic version of the ad hoc discovery above, suspecting more
gaps existed. Checked all 28 press releases across all 11 members against
the bill inventory in one pass; read the full text of the 6 with no bill
within 7 days. 4 were already-known, correctly explained (2 bill-milestone
releases, 1 NDAA-enactment milestone, 1 genuinely unrelated HHS funding
release — confirming the check doesn't force a bill onto every gap). 2 were
real, new findings: **Budd** has a second, previously untracked bill — the
Secure Payments Act (S.4570, sole-sponsored, introduced same-day as his
release, 3 ACU lobbying-text matches). **Vargas** is an uncredited original
cosponsor of Fitzgerald's Expanding Access to Lending Options Act
(H.R.6933) — his own 2024-01-10 press release announcing it had never been
matched; ACU's lobbying support for this bill was already counted under
Fitzgerald, now also linked to Vargas. Neither finding adds a new deviation
to E15's null model — Budd's bill follows the bench's standard same-day
pattern, and Vargas's cosponsorship reinforces an already-confirmed
full-triple member. Not yet checked: the reverse direction (bills ACU
lobbies for a bench member that never generated a press release) — flagged
as a follow-up, not run this session. All 4 `derived/bench_*.csv` files and
both charts rebuilt again.

**Britt's endorsement is conditional, not enthusiastic (E17, 2026-07-09).**
Editor found this reading ACU's own website directly, then traced it back
to a quote already in the corpus but never read in full: Britt's
2026-02-13 release (E3) carries a Scott Simpson (ACU President/CEO) quote
calling the Community Bank Relief Act "an important step forward" while
stating "the only real long-term solution is full repeal of the Durbin
Amendment." Checked all 28 press releases across the bench for similar
qualifying language — Britt's is the only hit; not a bench-wide pattern.
ACU's sworn lobbying text shows no distinct "repeal Durbin" push matching
the public rhetoric (Durbin/interchange has been a generic issue-code line
since 2022, predating this bill). Real methodology lesson: every prior
entry (E1-E9/E13/E14/E16) confirmed a named quote's *existence* by
title/url match but never read the quote's full text — "ACU gives a named
quote" isn't one uniform category.

**Confirmed isolated (E18, 2026-07-09):** read all 28 press releases in full
following E17's recommendation. Britt's is the only qualified/conditional
quote in the bench — all 17 other quoted instances across 9 members are
unqualified support, no exceptions. Strengthens rather than dilutes E17's
citability. Also noted (initially misflagged as a data trap, CORRECTED
2026-07-09): "Scott Simpson" is quoted as ACU's national President/CEO
(Britt, Gonzalez, both 2026) and, over a year earlier, as President/CEO of
the California/Nevada Credit Union Leagues (Vargas, 2025-02-05) — editor
confirmed this is the same individual, who moved from the state league to
the national ACU presidency; a real leadership-transition fact, not a
name-collision hazard. No new bills or gaps found beyond E7/E16's.

The triple-join method (mention screen → honoree LD-203 money →
named-bill lobbying activity text) is being validated as a reusable
detection technique, not just applied once. Known bound, already documented
in `docs/derived_db.md` from the overnight hardening run: the method is
**mention-pipeline-selected** — it can only surface associations a member
name-checks in their own press releases. ABA (bigger ACU-adjacent spender,
same bills, same committees) is invisible to it. Any density/scale
comparison against ABA/ICBA/MBA must therefore be built independently from
lobbying + LD-203 data alone, never from the mention pipeline, or the
comparison is circular by construction.

**The counterfactual, quantified (E12, 2026-07-09):** ACU pays 527 distinct
members ($6.2M total); only 27 (5.1%) get any ACU press mention at all, and
the 10-member bench is a further sub-selection of those 27. The other 500
(95%) include several paid more than any bench member — House/Senate
leadership (Jeffries, Waters, Neal) reading as relationship money, not
bill-tied. Direct test: Bill Huizenga, paid $35,000, is the named cosponsor
on this case's own E8 bill (Credit Union Board Modernization Act) — yet has
zero ACU mentions, because the pipeline attributes releases by publishing
member (`press_releases.bioguide_id`), and cosponsors who let the lead
sponsor issue the release generate no qualifying row of their own. This
turns "mention-pipeline-selected" from an abstract caveat into a quantified
number plus one named, same-bill example — the strongest single argument
for why that caveat needs to be prominent in the findings-report writeup.

**Should Peters/Young join the bench? (E13, 2026-07-09):** No — and E12's
claim that both "clear the `n_mentions>=2` threshold" was itself wrong,
hitting the same entity-644/645 double-count bug documented in E0; deduped
properly, both have exactly 1 real mention, not 2, so neither clears the
bench's own construction rule. Checked the substance anyway: **Peters has a
real, verified full triple** ($20,000 money, self-authored press release,
AND ACU's lobbying filings name a bill matching the title "Housing
Financial Literacy Act" by number in 4 filings) — he's excluded purely
because he has 1 press touchpoint instead of 2. **Young does not** — money
+ 1 press release, but zero lobbying-text match for his bill, same shape as
Beatty's documented break.

**Peters added to the bench (E14, 2026-07-09):** editor overruled E13's
"leave it at 10" recommendation — "I don't know why we need to restrict it
to 2 or more mentions." Correct call: the `n_mentions>=2` threshold came
from the screen-36 seeding query, not from anything about what makes a
triple real. Adding him surfaced a correction to E13: the House bill
E13's lobbying match was keyed to by title, H.R.1395, is actually sponsored
by BEATTY, not Peters — his bill is the identical Senate companion, S.1490
(117th Congress, confirmed via Congress.gov). His 2024-06-13 "Reintroduces"
press release covers a DIFFERENT bill in the NEXT Congress, S.4542 (118th,
found only by paginating all 913 of his sponsored bills), introduced the
same day as the release. Re-checked against this corrected lineage: ACU's
4 lobbying filings naming "Housing Financial Literacy Act" are ALL in 2022
Q2 - 2023 Q1 (S.1490's life) — zero filings name it from 2023 Q2 onward,
through all of 2024-2026 Q1 when S.4542 (his actual bill) was live. Peters
is now the bench's 11th member with a **partial/lagged triple** — money +
same-day press are clean, but the lobbying leg supports the prior
Congress's bill number, with a documented gap covering the exact period
his real reintroduction falls in. Closer in kind to Britt (money precedes
bill/press) or Beatty (dated gap in one leg) than to the bench's clean
majority — visually confirmed on the rebuilt PNG/D3 charts (his lane shows
the 2021 star with nearby lobbying ticks, a long gap, then the 2024 star
lined up with a press triangle but no lobbying tick nearby). All 4
`derived/bench_*.csv` files and both charts rebuilt to include him.

**Say/pay/lobby/bill typology (E11, corrected 2026-07-09):** re-characterizing
E1-E9 as a single uniform "triple" undersold what the sequenced data shows.
A first pass this session got the framing wrong (treated money as bill-
calendar-driven and mislabeled Britt); recovering quantitative work from an
earlier session (2026-07-08, working in this case's `derived/` dir)
and re-running it against the current CSVs produced the corrected version:
(1) bill→press is near-tautological (same-day-to-a-few-days for 8 of 10
members) and should be labeled a sanity check, not sold as a finding; (2)
money is a standing/background relationship independent of legislative
timing for 9 of 10 members — quantified via a 45-day-responsiveness test
(median 0%, range 0-38%) and irregular contribution gaps (0-740 days, no
fixed cadence); (3) Britt is the one genuine, quantified outlier — 0% of
her money is responsive within 45 days of any bill/press event, and every
dollar predates her flagship bill's introduction — inverting the case's own
"pay follows bill" framing for her specifically; (4) lobbying-text
continuity is a separate three-way axis (continuous: Vargas/Gonzalez/
Fitzgerald/Cramer/Scott/Budd/Barr; late-starting-then-continuous: Emmer;
absent: Beatty only), with Vargas and Gonzalez's lobbying text pre-dating
their bills' formal introduction as the most interesting single data point
(ACU present at drafting, not just reacting). This is now the case's
findings-report demo of the methodology — editor's 2026-07-09 call to keep
the case open for that purpose, independent of the ACU-scale kill (E10
stands). Full writeup + tables: evidence.md E11; reusable script:
`analysis/bench_timing_typology.py`.

## Prior coverage

Surfacing-time novelty-lite only (2026-07-07, bounded, from the lead):
OpenSecrets carries ACU aggregate totals ($4.27M PAC, $6.8M lobbying, 2024);
no reporting found documenting the bench structure (endorse→bill-number→pay
across named members) itself. Case-level scan still owed before this reaches
the findings report — see `track-investigation/reference/prior-art.md`.

## Sources / legal-risk notes

- Named (all 11 now independently drilled, E1-E9 + Barr's EBarr1-9 + E7
  correction + E13/E14): Reps./Sens. Andy Barr, Kevin Cramer, Tim Scott,
  Scott Fitzgerald, Ted Budd, Tom Emmer, Katie Britt, Joyce Beatty, Juan
  Vargas, Vicente Gonzalez, Gary Peters. Beatty (2 tracked bills as of
  2026-07-09) has a split record — H.R.5911 (Fair Hiring in Banking Act):
  money + press, zero lobbying-text match, a real negative result;
  H.R.3709 (Mentor-Protege Program for Small Financial Institutions Act):
  money + named press quote + 1 lobbying-text match, a real though thin
  triple — frame per evidence.md E7 (revised), name both bills precisely,
  don't summarize her as either "full pattern" or "lobbying absent."
  Peters (added 2026-07-09) is a documented partial/lagged triple — money
  and same-day press are clean, but ACU's lobbying text names the bill
  only in the PRIOR Congress (S.1490, 117th), with a gap through the
  Congress his actual press release/reintroduction (S.4542, 118th) falls
  in — frame per evidence.md E14, not as a full-pattern member either.
- America's Credit Unions (fka CUNA, merged NAFCU Jan 2024); PAC:
  America's Credit Unions PAC / CULAC.
- Comparison associations to be named if the ABA/ICBA/MBA check runs: ABA
  (American Bankers Association), ICBA (Independent Community Bankers of
  America), MBA (Mortgage Bankers Association).
- All money figures are LD-203 filings as filed by the association
  (`contribution_type='feca'`), deduped across filer copies — not FEC
  totals; describe as "reported contributions honoring," not "campaign
  finance totals."
- Honoree matches via `honoree_member_map` at confidence ≥ 0.9 only.
- Nothing here alleges quid pro quo; standard pre-publication: comment from
  ACU and from each named member's office before the bench story runs.
