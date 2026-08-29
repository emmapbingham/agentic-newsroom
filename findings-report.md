# Findings report

Five findings, then two method demonstrations (verified investigations whose
headline story didn't survive as news — there, the deliverable is the reusable
method that did). A few conventions, stated once:

- **Every claim ties to a source record.** Senate lobbying filings are cited
  by `filing_uuid` (open at `https://lda.gov/filings/public/filing/{uuid}/print/`;
  LD-203 contribution filings use `.../contribution/{uuid}/print/`), House
  filings by `house_filing_id` plus their source XML file, press releases by
  URL, external facts by citation. Per finding, the exact SQL that reproduces
  every aggregate is in `investigations/<case>/queries.sql` (all verified
  2026-07-15 against the built database); [`REPRODUCING.md`](REPRODUCING.md)
  has the rebuild steps.
- **Every finding passed a builder → skeptic → judge** verification pass (the
  "tribunal") against a corpus-specific checklist (junk values, entity-match
  confidence, House+Senate double-counting, base rates, multiple
  comparisons) — implemented in the `track-investigation` skill.
- **Novelty scans** are bounded web searches at a stated date. "No coverage
  found" means that, not an absolute negative.
- **No allegation of wrongdoing** is made or implied where lobbying and
  contributions are lawful, disclosed activities. Entries claim what the
  records show, not motive — except where an entry's caveats say otherwise.

---

## Findings

### The JACK Act's blind spots: convicted lobbyists' disclosures fail quietly, and nobody checks

The JACK Act (2019) requires lobbyists convicted of certain crimes to disclose
the conviction on *every* lobbying filing they appear on, forever. We found 18
lobbyists in the Senate register with conviction disclosures, and most comply.
Two don't. Former Rep. Duncan Hunter's firm disclosed his conviction once, on
its 2023 registration — then omitted it from all six quarterly filings since.
Vietnam Veterans of America's lobbyist Harold Hanson is missing the disclosure
in three of seven post-conviction quarters, and the filings that *do* carry it
cite the wrong instrument (a 2013 administrative export-control order, not his
2009 criminal conviction).

We can't know why these filings omit the disclosure, and don't assume it was
intentional. The more interesting question is who would ever notice. GAO
audits lobbying compliance every year — but it samples random lobbyists and
asks whether they have an undisclosed conviction, rather than checking how
known-convicted lobbyists actually file. Gaps like these are invisible to that
audit by design, across all seven annual reports since the law took effect.
And DOJ has never brought a JACK Act nondisclosure case. Which leaves the
question the story turns on: is this law enforced by anyone at all?

**Records.**
- Hunter/VALOON LLC: disclosed on registration
  `f760418c-a038-48d1-a6b3-d37173508fff`; absent from all 6 subsequent
  quarterlies (`4ac94cc9-fa1d-498b-84cc-b23c81e7fbda`,
  `5767af8b-a3b8-4a14-9834-e4a3d8dd4e66`, `cbbf216d-9264-4121-8fd1-1084ed381f52`,
  `a2ab1e69-04a9-4326-871e-3a5f914c3c76`, `11d51df2-e229-4a84-b28c-9c9faa5fb999`,
  `24be134b-6ad1-4010-93ed-aadff7d38aae`). All self-filed under Hunter's own
  name — no preparer change that would suggest a clerical handoff. The firm's
  *second* registration (client NJF Worldwide,
  `6c0afe7d-e6e3-4226-bf73-9df4d595e17e`, filed six weeks after the disclosed
  one) also omits the disclosure, as do two termination filings — in total,
  1 of 10 filings naming Hunter carries it.
- Hanson/VVA: missing in `06b7c4cf-88ec-478e-affe-ff9c7b71b4f3` (2023 Q3),
  `5550037a-1d72-451e-a3f5-4ff8cc3ca369` (2023 Q4),
  `39b000c9-ee52-4fc8-8998-fefb18cbcf44` (2025 Q1); confirmed by live LDA API
  re-pull and House-side corroboration. Present disclosures cite the 2013 BIS
  order, not the 2009 D.D.C. plea (1:09-cr-00071, 18 U.S.C. §1001).
- Scale, reported honestly: 877 of 887 post-conviction quarterly
  filing-instances corpus-wide *do* carry the disclosure — this is not "widespread." Hunter and
  Hanson are the only multi-quarter gaps.
- Enforcement vacuum: GAO-26-108486 p.9 (no DOJ prosecutions under the Act,
  ever; same result in all six prior reports, GAO-20-449 through
  GAO-25-107523); no private right of action; no Ethics Committee jurisdiction
  since 1977–78 (CRS RL34377).

**How we found and checked it.** A screen over the conviction-disclosure
register flags any convicted lobbyist whose filing sequence has gaps after
their conviction date. Hanson was the original lead; the skeptic pass, trying
to kill it as a one-off, instead found Hunter's gap and the GAO-methodology
blind spot. Verified via live LDA re-pulls (rules out ingest artifacts),
House-side corroboration, and the full tribunal — supported, high confidence.
Novelty scan (2026-07-07): no prior coverage of either gap or the GAO
argument.

**Caveats.** This entry describes an *apparent* statutory disclosure gap and
stops short of asserting a violation. The gap is documented; corrupt/knowing
intent (the legal standard under 2 U.S.C. §1606) is not observable in the
record and is not claimed. Two reporting steps remain outstanding: a D.D.C.
docket pull (1:09-cr-00071) for Hanson's sentence/any vacatur (blocked by
CourtListener bot protection; the plea is independently confirmed via
disclosure text), and requests for comment from VALOON/Hunter and VVA. Until
those are done, treat the filing record as evidenced and the reporting around
it as incomplete.

---

### A New Mexico casino has quietly opposed a Texas tribal-gaming bill for four years

Two Texas tribes — the Ysleta del Sur Pueblo and the Alabama-Coushatta — are
specifically excluded from the national law (IGRA) that lets tribes operate
casinos, and for years a bill to remove that exclusion has been introduced and
died, Congress after Congress. In the lobbying data we found an opponent
nobody has ever named in print: Sunland Park Racetrack & Casino, just across
the border in New Mexico, which has filed opposition in every quarter but one
since mid-2022 and states its motive in its own sworn filings — if the tribes
came under IGRA, they could one day negotiate a casino compact with Texas and
become a cross-border competitor.

The previously reported story of this bill was Republican opposition — Cornyn
asked a Senate committee to hold it in 2019. That thread just got more
interesting: Cornyn lost his 2026 primary runoff to Ken Paxton, the Texas AG
who personally led and won the state's litigation to close the Ysleta del Sur
tribe's Speaking Rock casino, and who is now the Republican nominee for the
November general. Gathering opposition on both fronts, no recent coverage
anywhere, and a live electoral hook — the elements of a story are in place.

**Records.**
- Sole opponent, sustained: 15 Senate filings 2022 Q3–2025 Q4 — the initial
  registration plus 14 quarterly opposition reports, covering 13 of the span's
  14 quarters (e.g.
  `cad7638e-7cd3-4152-8e78-1e49703a636d`,
  `05c490f1-f2b9-4e05-9444-293b6ca58d1e`,
  `efa83a81-33ba-4132-82ff-742da9f76087`), corroborated by 13 House filings
  (e.g. `301422514`, source `data/house/2022_3rdQuarter_XML/301422514.xml`;
  `301843696`, source `data/house/2025_4thQuarter_XML/301843696.xml`), same
  lobbyist (Landon Fulmer, registrant 401104304). The one gap (2023 Q1) is an
  explained lapse: the registration was terminated for exactly that quarter,
  then re-filed. Two other clients track the bill without stating a position.
- Stated motive, verbatim from its filings: "We oppose this bill… Were this
  bill to pass, they could eventually force Texas into gaming compact
  negotiations, something we oppose."
- Timing: the bill passed the House twice by voice vote (2019, 2021);
  Sunland Park's opposition begins 2022 Q3, and the bill hasn't cleared a
  subcommittee since (congress.gov action history for all four bill numbers).
  Correlation only — not claimed as cause.
- The electoral hook: Cornyn's 2019 hold
  ([KTRE](https://www.ktre.com/2019/10/16/sen-cornyn-sends-letter-opposing-alabama-coushatta-tribes-gaming-facility/));
  Paxton beat Cornyn 63.8–36.2 in the 2026-05-26 runoff
  ([Texas Tribune](https://www.texastribune.org/2026/05/26/texas-john-cornyn-ken-paxton-us-senate-republican-primary-runoff/));
  Paxton led the Speaking Rock litigation
  ([Texas Monthly](https://www.texasmonthly.com/news-politics/tigua-indian-tribe-loses-yet-another-court-fight-to-keep-speaking-rock-casino-open/)).
- Base rate: corpus-wide, only 3 clients on tribal-gaming issues show any
  explicit opposition language; Sunland Park's streak is ~4.5× the
  next-longest. No LD-203 money ties to this registrant — a pure "say" story
  (positions stated in filings, with no contribution money in the picture).

**How we found and checked it.** Surfaced from a gaming-issue-code screen for
one-sided, sustained opposition; drilled through the Senate↔House registrant
bridge to rule out a single-chamber artifact; legislative history pulled from
congress.gov directly. Verified via the tribunal, including the base rate and
the no-money check. Novelty scan spanned national, regional, tribal, and
trade press: nothing names Sunland Park on this bill.

**Caveats.** Scoped to "who has quietly opposed this bill and never been
named" — not "why the bill stalls" (the Cornyn explanation predates Sunland
Park and stands on its own). The motive rests on Sunland Park's own filing
language. Paxton's documented record is the Speaking Rock litigation; any
characterization of his position on *this bill* must come from his own words —
re-check immediately before publishing, as he is an active candidate.

---

### Three provisions Congress passed with no public pressure: finding a quiet provision's signature

Some consequential policy moves through Congress with heavy industry lobbying,
almost no public attention from members, and a resolution buried in a
must-pass bill instead of a standalone vote. We built a simple instrument —
the ratio of lobbying volume to member press releases, by issue — to find
these, and drilled three to fully cited exhibits: FCC spectrum auction
authority (lapsed in 2023, quietly restored in the 2025 reconciliation bill at
a CBO-scored **$85 billion** over ten years); the Medicare Physician Fee
Schedule cut (averted every year by a year-end rider, never a floor vote); and
Section 174 R&D expensing (industry lobbied three years to reverse it, failed
once on Senate cloture, then passed inside the same 2025 bill that fixed
spectrum). Same shape every time: steady, well-funded lobbying; a near-silent
Congress; no recorded vote.

The contrast that makes the silence measurable: members who post press
releases at all average 74–89 per year *each*. On Medicare PFS, all of
Congress combined managed 31–60 a year. And on Section 174, the same members
who wouldn't talk about R&D expensing put out ~7× more releases about the
*same bill's* child-tax-credit provision — they publicize a bill when it's a
family tax cut, not when it's a corporate accounting fix.

**Records.** (Every aggregate below is reproducible from
`investigations/invisible-provisions/queries.sql`.)
- Spectrum: ~870 Senate lobbying activities a year (202–231 per quarter), 127–149 registrants,
  flat across all 17 quarters — steady pressure, no public spike even at the
  2023 lapse. Congress, not the FCC, is the target in 17,239 of 24,740
  government-entity mentions. Restored authority scored at $85B FY2025–2034
  (CBO pub 61570, P.L. 119-21).
- Medicare PFS: lobbying grew 560 → 631 → 738 activities/year (2022–2024)
  against 31–60 press releases across all of Congress; patched by CAA 2023 and
  CAA 2024 riders, no standalone vote.
- Section 174: 395 registrants, 2,085 activities naming H.R.7024 or its
  provisions, against 54 releases on the R&D fix vs. 420+ on the same
  bill's child tax credit. Passed the House 357–70, died on Senate cloture
  48–44 (2024), became permanent in the 2025 reconciliation bill.

**How we found and checked it.** A lobby-to-press ratio screen over issue
codes and press releases; spectrum and PFS came straight off the screen,
Section 174 needed a human pivot into bill-number extraction. The per-member
press baseline deliberately counts only members who post at all (a generous
denominator). All three exhibits were verified twice; every figure traces to a
`filing_uuid`, a CBO/CMS/congress.gov citation, or a roll-call.

**Caveats.** Three verified examples of a named mechanism — not a claim that
these are the quietest issues in the corpus (at least one issue code shows a
stronger ratio and was left undrilled). The mechanism itself is well known;
the contribution is a reproducible way to find and measure specific
instances.

---

### How a federal privacy bill died: what the lobbying data shows — and what it structurally can't

Congress has twice come close to a comprehensive federal privacy law (ADPPA in
2022, APRA in 2024) and both times the bill died around markup. We tracked the
fight through the lobbying data and tested the dramatic explanations first:
did money buy the kill? Was no public-interest voice in the room? Neither
holds up. What the data does show: the largest lobbying coalition of any
comparable tech bill (1,950 activities, 319 distinct clients after dedup —
ahead of KOSA at 1,292 and AICOA at 902), whose *activity* rose 3–4× above
baseline in the drafting windows before each bill appeared — while the
contribution money stayed flat and uncorrelated with any milestone.

The most durable takeaway is about the data itself. Wired reported nine
privacy and civil-rights organizations lobbying against APRA's final version.
Only two of the nine appear in the disclosure data at all on this bill. The
opposition was real; it moved through channels (letters, coalitions,
below-threshold advocacy) that lobbying disclosure structurally cannot see. Any
investigation built on this data — including ours — is blind to that side of
the fight, and honest reporting on "who lobbied" has to say so.

**Records.** (Every aggregate below is reproducible from
`investigations/apra-lobbying-coalition/queries.sql`.)
- Coalition size, one corrected filter applied to all four bills (re-run
  2026-07-15): APRA/ADPPA 1,950 activities / 319 deduped clients > KOSA 1,292
  > AICOA/Open App Markets 902 > RESTRICT Act 99. Top filers: DirecTV,
  Intuit, Yahoo, Comcast, CTA, Discovery.
- Drafting-window rise: sustained 3–4× activity elevation in H2 2022 and
  Q2–Q3 2024 (205 distinct filers in the 2024 window; exemplars
  `a328ac9e-0742-470f-b8c5-b065de7abaf7`,
  `74f1546f-cd5a-4904-b2e5-f8ce665fd9c6`); ~97–99% corporations and trade
  associations. Replicates House-side (3.81× vs. Senate 3.79×, Q1→Q2 2024).
- Money tested three ways, null each time: press-vocal members didn't get the
  most money (ranking inverts); no contribution clustering at any of five
  milestones; the two leaders reported to have arranged the final block
  (Johnson $606,783; Scalise $639,700) don't stand out from the bill's own
  sponsors once institutional role is accounted for. Exemplar
  `93358f66-5a5c-4cbd-af5a-6b5d4436d493`.
- The blind spot: of Wired's nine named opponents (2024-06-27, Dell Cameron),
  only ACLU and Demand Progress Action show any registered activity naming
  the bill — and only the latter with substantive matching language.
- Where filings do state positions (~3% of the roster), the two splits match
  Wired's reported final-week sticking points: private right of action
  (AAJ for, `c7f7f417-9697-4aa6-aba5-011290f6809a`; SIIA against,
  `7f88d69f-2685-4324-b878-8cc4a874f168`) and state preemption (California
  lobbying to strip it, `1dc679a4-c117-4287-bae3-503f3d3ca5ff`).
- A live prediction: the successor SECURE Data Act (H.R.8413, April 2026)
  postdates the corpus (zero mentions, confirmed). If the mechanism is
  general, its introduction-quarter filings (public ~2026-07-20) should show
  the same sustained, industry-broad, contribution-flat rise.

**How we found and checked it.** Surfaced from a press-to-lobbying ratio
screen; tracked across ~8 sessions (the five finding-relevant sessions are
listed below). The tribunal's skeptic re-derived every
headline number and caught a real bug — a bill-name filter contaminated by an
unrelated "Data Privacy Act of 2023," inflating early numbers ~25%. The filter
was fixed at source, every affected number re-run, and the cross-bill
comparison re-checked under the corrected filter. Superseded numbers are kept
marked-not-deleted in the case evidence file.

**Caveats.** Deliberately a set of takeaways, not one headline — testing the
dramatic hypotheses and finding them unsupported *is* the finding. No
wrongdoing alleged. The fault-line reading rests on the ~3% of the roster that
discloses positions; the rest's silence is what LDA permits, not unanimity.
Volume work is Senate-side except where House replication is noted. Novelty
checks were targeted, not exhaustive — treat "not yet found elsewhere" as
provisional.

---

### Amazon's PAC money didn't buy silence from its critics in Congress

Amazon's PAC gives to 39 members of Congress who have criticized the company
by name in their own press releases. On another organization in this corpus
(America's Credit Unions — see the first method demonstration below), that
say-pay pattern — what members *say* lining up with whose money they *take* —
tracks with members echoing the donor's talking points, so we asked whether
Amazon's money quiets its critics. It doesn't.
Four of the 39 were genuinely, specifically critical of Amazon's
warehouse-labor practices — the exact subject Amazon's in-house lobbyists
worked every relevant quarter, on the Warehouse Worker Protection Act — while
taking real Amazon PAC money. All four acted anyway: Rep. Norcross ($1,000)
sponsored the bill, Rep. Pallone ($15,000 in total — the largest sum) and
Rep. Stansbury ($1,000) cosponsored, and Sen. Gallego ($11,000 in total)
backed it publicly. No dollar gradient, nobody went quiet. The finding reverses the
hypothesis we started with: for members willing to criticize Amazon by name at
all, the money bought no silence we can detect.

**Records.**
- Amazon lobbied the WWPA by name across two Congresses (in-house lobbying
  filings, registrant 54494): 2024 Q2–Q4 (`7aa7ca99-9c14-4fc7-ad20-45caa738ca87`,
  `f3f53731-47d1-42fa-b09d-e2339702497d`,
  `2d06ab44-9b9e-4a24-888b-4bc6b431bfba`) and its renumbering S.2613 through
  2026 Q1 (`f6449d57-3dc3-459c-93f0-e93210053421`,
  `ea7b9ed1-5e08-4c31-a04b-fe04480d73d2`,
  `eb88d053-1e97-4089-8e38-d2234c9bb80e`). LDA discloses subject, not stance —
  Amazon's "opposition" is an inference from the bills' content
  (pro-enforcement labor legislation), flagged as such here and in Caveats;
  no source in or out of the corpus directly states its position on these
  bills. All PAC-money citations below are LD-203 contribution filings (open
  via the `contribution/` URL path, not `filing/`).
- Norcross: $1,000 on 2022-04-15 (`e2064ae7-a2e2-4e2c-9c2b-bb565664ff32`);
  called for an [OSHA investigation into Amazon warehouses](https://norcross.house.gov/press-releases?ID=F21B3BE1-82BD-4756-ADE0-889298BE6FB1)
  two weeks later; primary sponsor of H.R.8639.
- Pallone: $15,000 total across five contributions — 2022: $2,500 to Pallone
  for Congress + $2,500 to his Shore PAC
  (`7525d5d1-4696-40b8-a46d-71caff7f36ff`); 2023: $4,000 + $1,000
  (`b0d60f07-36a6-4e84-a833-5985743366a0`); 2025: $5,000
  (`4aeb0fb5-80e0-445f-b9c6-77da72d2840a`);
  [criticized Amazon by name](https://pallone.house.gov/media/press-releases/pallone-demands-online-marketplaces-remove-dangerous-recalled-products-linked);
  cosponsored in 2024.
- Stansbury: $1,000 on 2025-09-09 (`2c970fc6-d190-4a53-8302-d4ae5d9540cd`);
  [urged Amazon to respect employees' rights](https://stansbury.house.gov/media/press-releases/rep-stansbury-labor-caucus-urges-amazon-respect-its-employees-rights-and);
  cosponsored.
- Gallego: $11,000 total across four contributions — 2022: $2,500 + $1,000
  (`7525d5d1-4696-40b8-a46d-71caff7f36ff`); 2023-01-11: $2,500
  (`774c155b-e8b3-475c-8dec-d24b479d8474`); 2025: $5,000 to his JUNTOS PAC
  (`4aeb0fb5-80e0-445f-b9c6-77da72d2840a`);
  [pressed Amazon on mass layoffs](https://www.gallego.senate.gov/news/press-releases/amid-expected-record-breaking-cyber-monday-sales-gallego-calls-on-amazon-to-explain-mass-layoffs/)
  but did not formally cosponsor — a real, weaker signal, stated precisely.
- Two other money-taking cosponsors (Gomez, Thompson) were checked and ruled
  out as genuine critics (their "mentions" are tax/grant releases) — not
  counterexamples either way.

**How we found and checked it.** Surfaced from a client-mention ×
honoree-contribution screen built to catch say-pay alignment; Amazon ranked
4th by member count but broke the pattern. The skeptic pass re-derived the
funding source for all 39 members and caught two whose "Amazon money" was one
lobbyist's personal giving, not PAC money (Tina Smith $250, Angie Craig
$6,200 — both excluded); it also cross-referenced the cosponsor list against
the criticism criteria, which moved the genuine-critic count from 1 to 4 and
reversed the finding. Novelty-scanned twice (2026-07-09, 2026-07-15): no
prior coverage.

**Caveats.** N=4 is small, and neither the WWPA nor its Senate companion ever
got a floor vote — cosponsorship is a real but low-cost signal. Amazon's
"opposition" is an inference (see Records). Tina Smith and Angie Craig must
*not* be described as Amazon PAC recipients. Sen. Gallego is reported to be
under an active, unrelated DOJ investigation into alleged campaign-finance and
leadership-PAC misuse
([Axios, 2026-06-29](https://www.axios.com/2026/06/29/gallego-doj-investigation-campaign-finance));
he denies wrongdoing — noted for editorial awareness only, unrelated to this
finding.

---

## Method demonstrations

*Both entries below are verified investigations whose headline story was
tested and did not survive as news. What survived is a reusable, validated
method — presented as capability exhibits, and labeled as such.*

### Sizing a trade association's "legislative bench" — applied to America's Credit Unions

Can you measure an endorse → legislate → pay cycle from disclosure data? We
built the triple-join that finds one: a client that credits members' bills by
number in its sworn lobbying filings, contributes to those members via LD-203,
and gets named in their press releases. Applied to America's Credit Unions
(ACU), it found a real 11-member bench, every link independently verified. And
then the pre-registered "boring explanation" won: run unfiltered across all
192 clients in the same screen, ACU is not an outlier — a mid-tier trade
association doing mid-tier things. ACU's LD-203 contributions honor 527
members; only 27 ever get a press mention. The story died honestly; the
method and its base-rate discipline are the deliverable.

The pattern is easiest to *see*: the bundled interactive timeline
([`figures/acu-bench-timeline.html`](figures/acu-bench-timeline.html), static
fallback [`.png`](figures/acu-bench-timeline.png)) plots, per member,
LD-203 contributions, ACU press mentions, ACU lobbying filings naming the
member's bill, and bill-introduction dates on one axis — lobbying ticks
follow bill stars, press hugs bills, and the money circles march on their own
steady schedule regardless.

One profile is worth remembering: Sen. Katie Britt is the only bench member
whose ACU money entirely *predates* her flagship bill — every ACU
contribution honoring her, 2022-03-10 (earliest,
`c809596c-366a-485b-8c71-0cebd0b1aa76`) through 2025-12-30 (latest,
`c19daac7-cd73-4fba-9a94-74508a609a96`), came before the Community Bank
Relief Act was introduced (S.3849, 2026-02-11); it's visible on the timeline
as the one lane where every circle sits left of the star. She is also the
only one whose single named ACU quote hedges (ACU's CEO in
[her 2026-02-13 release](https://www.britt.senate.gov/news/press-releases/u-s-senators-katie-britt-ted-cruz-introduce-legislation-to-protect-community-banks/):
"…the only real long-term solution is full repeal of the Durbin Amendment").
Neither breaks the null model alone; together she's the one member who
doesn't read as a standard synchronized relationship.

**How we found and checked it.** Mention-screen → LD-203 honoree money →
named-bill lobbying text, replicated per member, then stress-tested by
re-running the seeding screen unfiltered across all 192 clients. Verified via
the tribunal, including independent re-derivation of the bill-lineage claims.
The interactive bench timeline is at `figures/acu-bench-timeline.html`
(D3 inlined, fully offline). Structural limit: the method only sees
associations a member name-checks in their own releases.

**Caveats.** A method demonstration, not a claim about ACU — the ACU-scale
story was tested and killed on its own data. Corpus-wide *rankings* from this
screen are unverified until a client-alias cleanup lands (e.g. "VISA" matching
immigration-visa language); ACU's own 11-member count is unaffected. Money is
LD-203 "contributions honoring," not FEC totals. No quid pro quo alleged.

### A base-rate discipline that killed a 14-member leaderboard down to two

The most common false positive in say-vs-pay analysis: a member "criticizes an
industry while taking its money," where both facts are explained by committee
assignment. Our screen surfaced a plausible-looking leaderboard of 14
health-committee members naming drug and PBM companies as bad actors while
taking sector money. The committee base rate — House health-committee members
average $714k in health-sector money vs. $290k for non-committee members —
plus a hand re-read of every "critical" release killed 12 of the 14. Two
genuine outliers remain: Rep. Frank Pallone ($2.52M, 3.5× his committee
average; named [Merck](https://pallone.house.gov/media/press-releases/pallone-mercks-outrageous-lawsuit-block-medicare-price-negotiation)
and [PhRMA](https://pallone.house.gov/media/press-releases/pallone-phrmas-lawsuit-over-medicare-drug-price-negotiation)
in June 2023 releases) and Rep. Buddy Carter ($1.19M, 1.7×; named
[Express Scripts](https://buddycarter.house.gov/news/documentsingle.aspx?DocumentID=12926)
in a 2024 bipartisan letter). In both cases the named company is *not* in the member's
donor record — its sector peers are (Pallone: CVS `a99c78fe-a9d1-4fdc-af65-576dc351ce66`,
Pfizer `ce25b617-1b18-4143-a0da-b77a4bf2a03b`,
Humana e.g. `2c9ab318-1bb6-41cb-a5c6-e0f86045dff9`,
Elevance e.g. `daba6403-b182-46e5-9a73-828c809e94d4`;
Carter: McKesson `31282006-540f-4d69-a310-82d9c29f4ae3`,
Cardinal Health `6980fc36-a290-4a5d-8a48-be5718502f28`).

**How we found and checked it.** A member-issue-money panel joined to LD-203
and press releases, for members with 10+ pharma-critical releases and large
deduped health-sector totals. The skeptic computed the committee base rate and
re-read each release by hand — that's what shrank 14 to 2. A follow-up showed
Pallone's criticism doesn't generalize: his comparably-sized telecom/tech
donors (Comcast, Charter, Google, Microsoft) draw zero press criticism — a
narrow, event-driven episode, not a durable trait.

**Caveats.** A documented tension, not causation — the order of money and
criticism isn't established, and neither member takes money from the exact
company he names. Carter is a licensed pharmacist (a structural confound,
disclosed). **Extensively pre-covered** (KFF's pharma-money tracker, STAT's
2020 accounting, prior Carter/McKesson reporting): treat as corroboration
using this corpus's records, not a scoop.
