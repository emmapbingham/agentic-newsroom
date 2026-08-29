# The lobbying coalition behind (and around) federal privacy legislation

- **slug:** apra-lobbying-coalition
- **status:** closed
- **confidence:** medium (builder→skeptic→judge verified 2026-07-08;
  headline numbers corrected same day after a filter bug was found and
  fixed — see Verdict)
- **coverage:** partially scanned — one directly relevant prior article
  found (Wired, see Prior coverage); no systematic novelty scan run.
  Treat as under-scanned, not as a novelty claim.
- **opened:** 2026-07-03   **closed:** 2026-07-08

## Hypothesis

A large, heterogeneous coalition — **319 distinct Senate-side entities**
(verified 2026-07-06, corrected 2026-07-08 after a shared-filter
contamination bug was found and fixed — see evidence.md E6/E16 for method)
spanning tech platforms, data brokers, ad-tech, insurers, and trade
associations — lobbied steadily on federal comprehensive privacy legislation
(ADPPA 2022, APRA/H.R.8818 2024, and predecessor/adjacent bills) for
three-plus years,
while congressional press attention (member-issued releases specifically)
stayed thin throughout. The bill died quietly — its June 27, 2024 markup was
canceled amid GOP opposition signals, and it expired unremarked at the end
of the 118th Congress in January 2025.

**Deliberately no framing commitment yet** — not "invisible," not "loud
industry vs. quiet public," not any pre-decided shape. The open questions are:
who exactly is in this coalition and are they aligned or fighting each other;
is the lobbying volume actually unusual for a bill of this scale; what (if
anything) explains the bill's quiet death; and whether there's a genuine
public-interest counterweight in the data or a near-total absence of one.
Any of those could be the real story, or none of them — this case exists to
find out, not to confirm a pre-set angle.

## Why it's newsworthy

Comprehensive federal privacy legislation would be one of the most
consequential tech-policy laws in a generation — it would set the first
national floor on how companies collect, use, and sell personal data,
touching nearly every American's relationship with the internet. A very
large, well-resourced set of lobbying interests engaged with it steadily for
years. Whatever the eventual angle, the underlying facts (dozens of major
companies and trade groups engaged, a bill that vanished without a floor
vote, a check on how much of that engagement generated any public-facing
congressional messaging) are worth knowing regardless of which way the
verdict cuts.

## What would confirm it / what would kill it

Framing-agnostic confirm/kill criteria — testing the underlying facts, not a
pre-chosen narrative:

- **Scale check — ANSWERED 2026-07-06, CORRECTED 2026-07-08 (evidence.md
  E6/E16):** **APRA/ADPPA's Senate coalition (1,950 activities / 319
  distinct entities, corrected figure) is the largest of three compared
  bills** — above KOSA (1,292 activities) and AICOA (902), well above
  RESTRICT Act (99). Supports an "unusually large coalition" framing,
  though the margin over KOSA (~1.5x) is narrower than an earlier
  contaminated count implied — see the Verdict's filter-bug note.
- **Coalition shape — REVISED 2026-07-08 (evidence.md E8):** re-running the
  position-language read on the full 345-entity roster (up from E5's
  71-entity CPI-only roster) surfaces real fault lines, not just alignment:
  American Association for Justice supports a private right of action while
  SIIA/American Transaction Processors Coalition oppose it; the California
  State Senate lobbied to strip federal preemption from HR 8818 while the
  industry coalition wants it. Still thin — only ~10 of 345 entities carry
  genuine position language after full read-through — but no longer
  "2 entities pointing the same direction." E8 also found a filter artifact:
  the roster-scale query's `length(description) < 600` cutoff (built to
  exclude omnibus laundry-list filings) silently excludes AAF's and SIIA's
  own real position statements, which run 780–1,038 characters — a method
  warning for any future text analysis using the corrected-roster cutoff.
  ~64 of a 103-name no-cutoff candidate list remain unread.
- **Advocacy-side presence — REVISED 2026-07-08 (evidence.md E8):** E3's
  "no organized public-interest voice engaged on APRA specifically" finding
  does NOT hold. Electronic Frontier Foundation files substantively on
  ADPPA/APRA — naming preemption, private right of action, and specific
  provisions (biometric data on minors, student privacy) across multiple
  filing years — but under the `CIV` (civil rights) issue code, not `CPI`,
  which is why E3's CPI-scoped search missed it entirely. Insights
  Association (marketing research trade group) also shows explicit support
  language. The advocacy-side presence question is answered: yes, at least
  one organized public-interest voice (EFF) is substantively engaged on
  APRA specifically — the earlier "entirely industry-side" framing is
  wrong.
- **Press-thinness explanation — KEYWORD-NET STRESS-TESTED 2026-07-08
  (evidence.md E2 revision):** editor asked whether E2's original 19/40
  count was an artifact of too narrow a keyword search. Checked directly:
  a maximal "data privacy" substring search returns 327 press releases; a
  forked agent read all 290 outside E2's original net in full text. Only
  **13 were genuinely on-topic** (revised total: 53, up from 40) — the
  other 277 are a *different*, much louder set of controversies sharing
  the same vocabulary (2025 DOGE/Musk federal-data-access fight ~30,
  reproductive-health privacy ~35, TikTok/foreign-adversary data ~25,
  COPPA/KOSA family ~25 — already correctly excluded from this case's
  scope, plus committee-name boilerplate and misc.). **The "quiet"
  framing survives this stress test** — broadening the net 8x (40→327)
  only adds 13 real hits, not a hidden flood — but the number itself
  moves from 40 to 53, and any future press-corpus keyword work in this
  corpus should expect an ~85% false-positive rate from a bare
  policy-domain substring when several distinct legislative fights share
  vocabulary in the same window. Still open: does a broader (non-member-
  press) coverage check confirm real public/trade coverage existed (per
  the 2026-07-03 web search: WaPo, IAPP, WilmerHale, IBM, Senate Commerce
  Committee "what others are saying" page) while member press specifically
  stayed relatively thin — and if so, is that gap itself informative, or
  just the ordinary base rate for policy bills that don't pass? No
  baseline comparison (how many press releases does a similarly-scaled
  passed/failed bill typically draw) has been run yet.
- **Kill:** the lobbying volume turns out to be unremarkable for a bill of
  this scale/duration; OR the "coalition" dissolves into unconnected
  sub-fights with no coherent story; OR real public coverage was extensive
  enough that "thin press" was only ever a member-press-release artifact
  with no story behind it.

## Verdict

Closed 2026-07-08. This case does not resolve to one dramatic headline
claim — it resolves to a set of tested, verified takeaways, several of
which are negative results for more dramatic hypotheses that were
directly tested and did not hold up. Verified via a full builder→skeptic→
judge tribunal (2026-07-08); the skeptic independently re-derived every
headline number against `db/gain.db` and found a real contamination bug in
a shared bill-name filter (a bare "Data Privacy Act" keyword collided with
an unrelated bill, H.R. 1165), which inflated this case's two most
quotable early numbers by ~25%. That filter was fixed at the source and
every affected evidence block (E1, E6, E8, E10, E11, E13, E14) was re-run
same day; the figures below are the corrected, post-fix numbers, safe to
cite. Full detail, including the superseded pre-correction figures (kept,
not deleted, for the record): `evidence.md` (17 evidence blocks) and
`log.md`.

**319 distinct entities filed 1,950 Senate lobbying activities** naming
APRA/ADPPA or a named predecessor bill, 2022–2026 — the largest of three
comparison bills checked (KOSA 1,292, AICOA 902, RESTRICT Act 99), though
those three counts are unverified mechanical estimates and the exact
margin over KOSA should be treated as provisional. That activity **rose
roughly 3-4x above a flat corpus-wide baseline across two sustained
multi-quarter windows** — 2022 H2 and 2024 Q2-Q3 — tracking the bill's
actual drafting calendar (introduction, discussion draft, markup) rather
than spiking at one precise event; the pattern independently replicates on
the House side at nearly the same ratio, and both windows are ~97-99%
composed of corporations and trade associations spread across hundreds of
distinct filers, not concentrated in a few players. **Campaign
contributions did not track this same pattern** — three separate tests
(press-coverage correlation, milestone timing, and a direct contrast of
the reported kill-decision-makers Johnson/Scalise against the bill's own
sponsors Rodgers/Cantwell) all came back negative; everyone checked draws
from the same large donor pool in amounts explained by institutional role,
not position on the bill. The coalition's own filed position language
shows two thin but real fault lines (private right of action, state
preemption) that echo the provisions a Wired investigation names as the
bill's actual final-week sticking points — read as background corroboration,
not a distinctive discovery, since the same organizations take identical
positions on unrelated bills. Finally, checking Wired's own named list of
nine opposition organizations against this corpus found only two with any
registered lobbying activity on the bill at all — a citable illustration
that lobbying-disclosure data structurally cannot see most organized
opposition that operates below LDA's registration threshold or through
channels (direct letters, member outreach) the disclosure regime wasn't
built to capture.

A live thread for whoever picks this up next: a successor bill, the
SECURE Data Act (H.R. 8413), was introduced April 22, 2026 — three weeks
into the quarter this corpus's data does not yet cover. No finding can be
made about it yet, but the drafting-stage lobbying-activity pattern found
here gives a concrete, testable prediction once Q2 2026 Senate LDA data is
ingested (expected ~2026-07-20): compare that bill's own introduction-
quarter lobbying activity against APRA's Q2 2022/Q2 2024 pattern using the
same corrected methodology (E14). See evidence.md E17.

**Not report-ready if this case is picked up again:** E9 (roster-wide
say-vs-pay, only 27% entity coverage, has a live uncorrected VISA-alias
bug in reused infrastructure); E4 (RELX single-company illustration, not
sampled systematically); KOSA/AICOA/RESTRICT's exact entity counts
(mechanical estimates, not checked for the same contamination bug found
in APRA's own filter). **Tested and should not be resurrected without new
evidence:** money-timed-to-the-kill-decision (3 separate negative tests);
"no organized public-interest voice on APRA" (superseded — EFF and
Demand Progress Action are both substantively engaged); "this reveals
something about lobbying-disclosure law's scope" (editor-rejected as out
of scope for this project).

## Prior coverage

Full novelty scan not yet run — findings below are from targeted web
searches done in service of specific evidence questions, not a systematic
scan, and should be re-checked before the case closes.

- **2026-07-03** (non-evidentiary, done to sanity-check the "thin press"
  claim before opening this case): real trade/policy coverage of APRA
  (Washington Post, IAPP, WilmerHale, IBM Think, Senate Commerce Committee)
  and real, currently-live coverage of a related-but-distinct bill, the
  Kids Online Safety Act/KIDS Act (Axios, NBC News, The Hill, Roll Call,
  all within days of 2026-07-03) — KOSA is NOT part of this case's
  hypothesis and should not be conflated with APRA.
- **2026-07-08 — Wired, "Surprise! The Latest 'Comprehensive' US Privacy
  Bill Is Doomed"** (June 27, 2024; cited at `wired_source.md` —
  full text not redistributed). Reports the June 27 markup cancellation came
  amid GOP leadership vowing to block the bill "whether it was approved by
  the committee or not," matching this case's independently-sourced
  Johnson/Scalise account (E13). The article's central account is that
  the bill's final-week revisions stripped civil-rights and algorithmic-
  decision-audit provisions to court conservative Republicans — one clause
  describes this as "engineered to appease conservative lobbyists
  representing the interests of big business" — and that this stripping
  is what caused a wave of privacy/civil-rights organizations (ACLU,
  Center for Democracy & Technology, NAACP, Japanese American Citizens
  League, Autistic Self Advocacy Network, Asian Americans Advancing
  Justice, Access Now, Demand Progress, Free Press Action) to withdraw
  support and lobby E&C Democrats against the bill in its final days.
  E&C ranking Democrat Frank Pallone praised committee chair McMorris
  Rodgers after the cancellation; Rep. Nanette Barragán is quoted citing
  California-preemption concerns, independently corroborating this case's
  own E8 finding (California State Senate opposing preemption). Checked
  each named organization against this corpus's Senate LDA data (E15,
  2026-07-08) — see evidence.md for the full table; two of nine appear
  lobbying on APRA specifically, most do not appear in this corpus at all
  or are registered filers without an APRA-specific filing found.
- Also web-sourced 2026-07-08 (used for corroborating dates, not treated
  as case evidence): The Hill, IAPP, Foley & Lardner, and The Spokesman-
  Review (Rodgers' retirement announcement) — see `log.md` for the full
  search trail.

## Sources / legal-risk notes

No allegation of wrongdoing — this is lobbying disclosure activity, which is
legal and required to be disclosed. Full deduplicated roster (**319
entities, corrected 2026-07-08 — see evidence.md E6/E16 for the filter fix
that changed this from the earlier 345**; top clients by activity count
include DirecTV, Intuit, Yahoo, Comcast, Consumer Technology Association,
Discovery Communications, American Honda Motor, Business Roundtable,
Computer & Communications Industry Association, Interpublic Group) is in
`derived/roster_corrected_deduplicated.csv`, regenerable via
`analysis/build_corrected_roster.py` (see evidence.md E6). If specific
companies' positions (support/oppose/amend) get characterized in a finding,
that characterization must be sourced to their own filed language or public
statements, not inferred from lobbying activity alone — LDA filings
disclose that a client lobbied on an issue, not their position. Entities
with genuine bill-specific position language on file so far (evidence.md
E5 + E8, updated 2026-07-08): SIIA, American Advertising Federation,
Alabama Farmers Federation, American Association for Justice, American
Transaction Processors Coalition, California State Senate, Chamber of
Progress, Center for Freedom and Prosperity, Electronic Frontier
Foundation, National Fusion Center Association, Insights Association —
may be named with their own quoted language (`filing_uuid`s not yet
individually pulled for most of these, see E8's Open item). No other
entity's position should be characterized beyond "disclosed lobbying
activity on this bill." ~64 of 103 candidate names in E8's broader,
no-length-cutoff scan remain unread and could add more names to this list.
