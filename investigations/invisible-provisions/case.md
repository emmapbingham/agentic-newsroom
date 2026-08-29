---
slug: invisible-provisions
status: written-up
verdict: supported for exhibits 1-3, written up in /findings.md 2026-07-15 without the "quietest in corpus" claim
confidence: medium
coverage: novel
opened: 2026-06-25
lead_slug: tec-quiet-lobbying
screen: quiet-issue-quadrant (screen 15, run 15)
---

# Case: Invisible Provisions

## Why newsworthy

Some highly consequential federal policy gets made with almost no public
pressure, no constituent calls, and no member press releases — because it's too
technical for most voters to follow. Industries that understand the stakes lobby
steadily and quietly; Congress eventually acts when a must-pass vehicle makes it
convenient. The lobbying data can measure this: sustained industry lobbying with
near-zero corresponding congressional press, resolved as a rider rather than a
standalone vote.

The story is structural — about how a category of legislation moves through
Congress — not about a bad actor. The tone is explanatory: "here's a thing that
happens, here's what it costs when it stalls, here's who's paying attention when
voters aren't."

The framing is loose by design. We need 2-3 examples to make this work, and
the examples will determine whether there's a natural typology (different
mechanisms, different issue areas) or a single unified pattern. Spectrum auction
reauthorization is exhibit 1. Additional examples to be surfaced via
`issue-quarterly-surge` next session.

## Hypothesis (working)

Some technically complex federal issues have a measurable data signature: high
sustained lobbying intensity, near-zero member press output, no spike around
deadlines or lapses, resolution via must-pass vehicle rather than dedicated
floor vote. The lobby-to-press ratio from `derived_issue_quarter_volume_press`
is a candidate quantitative marker for this class. The interesting question is
whether different "boring-but-important" issues share this signature or have
meaningfully different mechanisms.

## Confirm / kill criteria

- **Confirm:** At least 2-3 additional issue codes or specific provisions show
  the same flat-lobbying / zero-press / rider-resolution pattern.
- **Confirm:** The spectrum case holds up to skeptic review (flatness is real,
  not an artifact of keyword mismatch or code aggregation).
- **Kill:** Additional examples don't hold — spectrum turns out to be idiosyncratic.
- **Kill:** The quiet-lobbying signal is explained by keyword gaps in the press
  mapping rather than genuine member silence.

## Exhibit 1: Spectrum Auction Reauthorization (TEC)

**What happened:** FCC spectrum auction authority lapsed March 2023 — first
lapse since 1994. Restored ~2 years later as a provision of the One Big
Beautiful Bill Act (OBBBA), 2025. Reportedly scored $88B+ over 10 years by CBO.
Not a headline provision of the OBBBA; characterized in coverage as a revenue
offset rather than a major policy fight.

**The lobbying signal:** ~870 Senate LDA activities/quarter mentioning
"spectrum," from ~140-170 distinct registrants, flat across every quarter
2022-2025 with no spike around the March 2023 lapse or the 2025 restoration.
~$27-29M/year in raw Senate income from TEC-spectrum filers. Broad bipartisan
industry coalition (AT&T, Charter, NCTA, CTIA, Microsoft, Apple, Cisco,
Lockheed, rural co-ops, AARP).

**The press signal:** TEC overall had a 4.99x lobby-to-press ratio 2022-2024
(z=2.28 vs the original 21-code baseline; z≈0.84 against the expanded 73-code
baseline — see "Keyword-map expansion" section, no longer an outlier).
Congressional press on
ACP (the specific sub-issue Democrats wanted earmarked) was nearly identical
across parties: 29 releases from 14 Democratic senators, 23 from 13 Republican
senators — undermining the "Democrats held ACP hostage" narrative.

**Government entity targets:** House and Senate are the primary targets
(17,239 of 24,740 entity mentions), not the FCC (1,757). Congress is the
right target — spectrum auction authority is a congressional authorization,
not a regulatory one.

**Resolution:** Passed as OBBBA rider, 2025. Budget math (needing CBO score)
appears to be the proximate cause of passage, not lobbying escalation.

**Numbers (E1 VERIFIED, E2 VERIFIED 2026-06-25):**
- 4.99x TEC lobby-to-press ratio 2022-2024; z=2.28 ✓
- ~$26M/quarter (~$6.5–7.8M/quarter) Senate TEC-spectrum income ✓
- 202–231 acts/quarter, 127–149 registrants, flat across all 17 complete quarters ✓
- CBO spectrum auction score: **$85 billion** FY2025–FY2034 (scored as "Auction Wireless
  Spectrum" under Other Offsetting Receipts in OBBBA). Source: CBO pub 61570 (P.L. 119-21)
  via CRFB analysis. Earlier references to "$88B" referred to an earlier House version
  of the spectrum provisions; the enacted figure is $85B.

## Exhibit 2: Medicare Physician Fee Schedule (MMM)

**What happened:** A statutory formula requires Medicare to cut physician payment
rates annually. Congress has averted or partially mitigated the cut every year
by inserting a conversion-factor adjustment into year-end omnibus appropriations
bills — never via standalone floor vote. CY2023: CAA 2023 (signed Dec 29, 2022)
reduced a scheduled 4.5% cut to 2.0%. CY2024: a 3.37% cut hit Jan 1, then was
partially reversed by CAA 2024 (signed Mar 9, 2024), leaving different rates
for Jan 1–Mar 8 vs. the rest of the year. Pattern extends back years further.

**The lobbying signal:** MMM has a 5.59x lobby-to-press ratio, z=2.68 against
the original 21-code baseline. **Superseded 2026-06-30:** with the keyword map
expanded to 73 ranked codes (see "Keyword-map expansion" section below), MMM's
z-score drops to ~1.05 — no longer an outlier, upper-middle of the corpus.
The ratio/count numbers themselves are unchanged and still accurate; only the
"quietest in the corpus" characterization no longer holds. PFS-specific
activities grew 560 → 631 → 738/year from 111–135 registrants — sustained and
growing (Senate LDA only; House lobbying on PFS adds ~2,684 more activities
across the period and is not yet broken out by year — see E14).

**The press signal:** 31–60 press releases per year on PFS topics across all of
Congress (22–41 members), against 560–738 lobby activities — roughly 13–18:1.
Bipartisan silence: no partisan asymmetry. About half the members who published
anything were not on health committees.

**Numbers (E6-E8 VERIFIED 2026-06-25):** MMM 5.59x / z=2.68 ✓; PFS 560/631/738
acts/yr ✓; 31/60/57 press releases/yr ✓; lobby-to-press ratio 18:1/10.5:1/13:1
by year (cite as "roughly 10-18:1"). Health committee: 39 members / 84 releases;
non-committee: 31 / 64.

## Exhibit 3: Section 174 R&D Expensing (TAX)

**What happened:** The Tax Cuts and Jobs Act (2017) quietly changed the treatment
of R&D expenses from immediate deduction to 5-year amortization, effective 2022.
Companies were hit with unexpected tax bills. Industry lobbied for three years
to reverse it. H.R.7024 (Tax Relief for American Families and Workers Act)
passed the House 357-70 (Jan 31, 2024) but died on Senate cloture 48-44
(Aug 1, 2024) — Republicans blocked it over the bundled child tax credit
expansion, not the business provisions. The fix ultimately landed in the OBBBA
(signed July 4, 2025) as Section 174A, permanently restoring immediate expensing
of domestic R&D, with retroactive relief for small businesses covering 2022–2024.

**The lobbying signal:** 305 distinct Senate registrants, 1,563 activities
mentioning H.R.7024 or its provisions in 2022–2024. TAX is a mid-pack issue
code (z near 0 overall), but this specific provision had a concentrated,
sustained lobby effort invisible at the code level.

**The press signal:** Child tax credit (the political packaging) drew 413 press
releases from 159 members. Section 174 R&D expensing drew 66 from 35. Bonus
depreciation: 14 from 13. The industry payload was nearly invisible; the
political cover attracted all the attention.

**Note:** Same OBBBA that fixed spectrum (exhibit 1) also fixed Section 174 —
two separately-lobbied quiet provisions that converged in the same must-pass
reconciliation vehicle.

**Numbers (E10 VERIFIED 2026-06-25, CORRECTED):** 395 registrants / 2,085 acts ✓
(scout 305/1,563 was an undercount — excluded legitimate 2023 Q4 filings). Senate
LDA only; House lobbying adds ~2,244 more activities mentioning H.R.7024 across
the period (see E14) — cite Senate figure as Senate-only, not total lobbying volume.
Press: child tax credit 420/161; Section 174 R&D 54/28; bonus depreciation 15/14.

---

## Framing (updated 2026-06-25)

Three exhibits now in hand with meaningfully different mechanisms:
- **Spectrum:** lapsed congressional authorization, restored as revenue offset
- **PFS:** annual statutory formula cut, averted via year-end omnibus rider
- **Section 174:** prior tax law change, lobbied for reversal over three years,
  failed one vehicle, passed in a second

The story is better understood as a **methodology demonstration** than a breaking
story. The mechanism (industry lobbying quietly on technical issues via must-pass
vehicles) is broadly known. What's new is the **systematic, data-driven
measurement** of it: a reproducible method that surfaces the pattern across 80
issue codes, identifies the quietest by a measurable ratio, drills to specific
provisions, and produces citable numbers. The value for the challenge writeup is
showing what structured data + agent pipeline can quantify in an afternoon that
no beat reporter could assemble manually across three issue areas in the same
sitting.

Story is not closed — verification and novelty scan still needed before any
publication decision.

## Prior coverage (novelty scan 2026-06-25, extended framing scan 2026-06-25)

### What has been published

**Academic — theory (Culpepper 2010):**
*Quiet Politics and Business Power* (Cambridge University Press) names and
theorizes the phenomenon: low public salience → business lobbies quietly →
legislators defer → industry wins. The theory is qualitative and comparative
(European corporate control rules). No quantitative operationalization; no US LDA
data. This is the right anchor for the academic framing of what we're measuring.
A 2021 follow-up confirms the mechanism persists in the populist era.

**Adjacent academic work:** EU salience measurement (Beyers/Dur/Wonka); strategic
lobbying venue choice (Victor); grassroots vs. direct lobbying on salience
(Cluverius). None uses LDA issue codes or congressional press volume as a signal.

**Journalism — outlet-level:**
- *Sludge*: tracks dark-money and transparency riders in omnibus bills; focused on
  disclosure policy specifically; no LDA quantitative screen.
- *ProPublica*: publishes LDA data journalism tools; no lobby-to-press ratio
  methodology or cross-corpus analysis.
- *Bloomberg Government*: narrative coverage of lobbying on low-attention issues;
  no data operationalization.
- Trade press (Wiley Law, AJMC, Thomson Reuters, Grant Thornton): covers each
  provision's legislative outcome without a systematic salience signal.

### What has not been published

- A quantitative lobby-to-press ratio screen applied across all LDA issue codes.
- A data-journalism piece combining US LDA lobbying filings with congressional
  press release volume to identify "quiet" issue areas.
- Coverage of spectrum reauthorization, PFS, and Section 174 as a *pattern* of
  the same legislative mechanism.

**Coverage verdict: `novel`** — both the methodology and the multi-exhibit
pattern are new. Culpepper provides the theoretical frame; our contribution is
a set of reproducible data tools applied with human editorial judgment.

**Accuracy note on "systematic":** The lobby-to-press ratio screen surfaced TEC
and MMM directly. Section 174 did not surface from issue-code screening — it
required a researcher pivot to bill-number extraction from free-text, a human
judgment call. The right framing: the tools are reproducible and the corpus is
comprehensive, but the analyst steers the investigation. Do not claim the method
is fully automated or that it surveyed all 80 codes without human judgment.

---

## Verdict (builder → skeptic → judge, 2026-06-30)

**Builder:** Re-confirmed E1/E6 headline ratios (MMM 5.59x z=2.68, TEC 4.99x
z=2.28, BUD 4.41x z=1.91) directly against `derived_issue_quarter_volume_press`.
All three exhibits' core numbers already independently verified in the prior
session (log.md 2026-06-25 entries). Case argued as methodology demonstration:
three exhibits, three distinct legislative mechanisms, sustained lobbying +
near-zero press + must-pass-vehicle resolution in each.

**Skeptic (E14 in evidence.md):** Ran the full corpus-specific checklist
independently, re-deriving rather than reading the builder's queries first.
Found two material framing problems, no claim-killing problems:
1. **Denominator overstatement** — case.md said MMM is "the quietest issue
   code in the entire corpus"; actually quietest of a 21-code subset that has
   hand-curated press keyword mappings (58 of 79 codes get `n_press_releases=0`
   by construction, not by genuine silence). E13's "runnable across all 80 LDA
   issue codes" claim is also not accurate as stated — only 22 codes have
   keyword coverage.
2. **Senate-only undercount** — E2/E7/E10 drilldowns query Senate LDA only;
   House lobbying is a real, comparable-magnitude addition (~2,684 more PFS
   acts, ~2,244 more Section 174 acts) omitted from the cited totals, though
   correctly included in the E1/E6 corpus-wide ranking itself.
   Checklist items that did NOT surface a problem: junk free-text exposure,
   honoree-match confidence (not load-bearing for the core claims), base
   rate/multiple comparisons (21-item ranking, not a large search space),
   time-window alignment, FTS false-positive risk on the specific phrases used.

**Judge:** Neither skeptic finding reverses the direction of any exhibit —
both narrow precision (correct denominator, correct chamber scope) without
touching the underlying pattern (sustained lobbying, near-zero press, rider
resolution). Corrections applied directly to case.md exhibit text 2026-06-30.
**Verdict: supported, with corrections. Confidence: medium-high** — high
confidence in each exhibit's individual numbers (independently re-verified
twice now); medium confidence in the "class of provisions" framing, since N=3
hand-selected exhibits (one found via issue-code screening x2, one via a
researcher's manual bill-number pivot) is suggestive of a pattern, not proof
that it generalizes. Framing already discloses this in case.md's "Accuracy
note on 'systematic'" section — consistent with the judge's read.

## Keyword-map expansion and a new outlier (2026-06-30)

**Why this happened:** the skeptic pass's Finding 1 (denominator overstatement
— see "Verdict" above and E14) noted that `ISSUE_KEYWORDS` only mapped 21-22
of 79 issue codes, so "quietest in the corpus" wasn't a fair claim. Before
closing or writing up this case, we expanded the map to check whether TEC/MMM
would still stand out once measured against an honest, near-complete
comparison population.

**What we found root-causing the gap:** the exclusion of 57 codes was never a
deliberate "too vague to map" decision — spot-checking five clearly-specific
unmapped codes (tobacco, aviation, copyright/patent, food industry, gambling)
against `press_releases` directly showed hundreds to thousands of real,
on-topic hits waiting for each. The map was simply incomplete, built in one
commit for one screen's immediate needs. A genuinely-too-generic subset does
exist (media, science/technology, government, constitution — each tens of
thousands of generic-usage hits) and stays excluded, now with an explicit
documented reason in the script rather than a silent gap.

**What we did:** expanded `ISSUE_KEYWORDS` from 21-22 to 75 of 79 codes in
both `scripts/build_derived_issue_quarter_volume_press.py` (canonical) and
`scripts/build_derived_member_press_topics.py` (synced copy), rebuilt both
derived tables. One keyword bug caught before it reached a finding: GAM's
initial keyword set included "lottery," which mostly matched unrelated
immigration press releases ("diversity visa lottery") rather than gambling —
caught by eyeballing sample matches (the skeptic checklist's "FTS false
matches" item, now reinforced by the new "denominator/scope honesty" item).
Removed "lottery"; also tightened MON ("currency" → "digital currency"/
"currency manipulation") and UTI ("rate case" dropped, "utility" →
"utility bill"/"public utility") after the same false-positive spot-check.

**Result — re-ran the E1/E6 ranking query against the expanded map, 2022-2024,
`press_2224 >= 100` threshold (73 codes now clear it, vs. 21 before):**

| code | name | acts | press | ratio | z |
|---|---|---|---|---|---|
| **GAM** | **Gaming/Gambling/Casino** | **1,751** | **103** | **17.0x** | **5.08** |
| ART | Arts/Entertainment | 1,149 | 124 | 9.27x | 2.35 |
| CSP | Consumer Issues/Safety/Products | 7,398 | 797 | 9.28x | 2.35 |
| CPT | Copyright/Patent/Trademark | 5,779 | 660 | 8.76x | 2.17 |
| INS | Insurance | 4,821 | 591 | 8.16x | 1.96 |
| SPO | Sports/Athletics | 1,275 | 175 | 7.29x | 1.65 |
| CPI | Computer Industry | 6,969 | 1,089 | 6.4x | 1.33 |
| COM | Communications/Broadcasting/Radio/TV | 4,532 | 744 | 6.09x | 1.23 |
| MMM | Medicare/Medicaid | 25,816 | 4,617 | 5.59x | 1.05 |
| TEC | Telecommunications | 13,136 | 2,633 | 4.99x | 0.84 |

**GAM (Gaming/Gambling/Casino) is now the dominant outlier — z=5.08, more
than double the next-highest code, and both its ratio (17.0x) and z-score
exceed anything previously cited for TEC or MMM.** TEC and MMM fall to
z≈0.84-1.05 against the fuller 73-code baseline — no longer statistical
outliers, just upper-middle of the pack. This is exactly the outcome the
skeptic's Finding 1 warned was possible.

**GAM scout-level trend (UNVERIFIED, not yet drilled down):**

| year | acts | press |
|---|---|---|
| 2022 | 593 | 6 |
| 2023 | 571 | 45 |
| 2024 | 587 | 52 |
| 2025 | 721 | 72 |

Sustained lobbying, press rising off a near-zero base but still far below
lobbying volume every year. Consistent shape with the invisible-provisions
pattern; not yet drilled to a specific sub-provision, government-entity
target, or resolution vehicle. Sports betting expansion (post-*Murphy v.
NCAA*, ongoing state-by-state rollout with federal preemption/taxation
questions live) is the first hypothesis to test, given SPO's co-occurrence
at z=1.65.

**What this changes and what it doesn't:**
- Exhibits 1-3's underlying claims (sustained lobbying, near-zero press,
  rider resolution, specific legislative mechanisms) are unaffected — those
  are about the *specific provisions*, verified independently of any
  corpus-wide ranking.
- What breaks is the *comparative* framing — "TEC/MMM are the quietest in the
  corpus" no longer holds under an honest denominator. The case's actual
  contribution was always the specific-provision drilldowns, not the
  ranking's extremity; the ranking was the *discovery mechanism* for TEC/MMM,
  not evidence that they're uniquely quiet.
- GAM is a new, stronger candidate for "actually the quietest issue in the
  corpus" but is unverified scout-level and undrilled — same starting point
  TEC/MMM/Section 174 each had before their evidence blocks existed.

**Open decision, not yet made:** whether GAM (a) replaces one of exhibits 1-3,
(b) is added as a fourth exhibit, or (c) reframes the case's core claim from
"here are three examples of a pattern, ranked by a screen" to "here is the
actual quietest issue in the corpus (GAM), plus three worked examples of the
same underlying mechanism found by other means." Decision deferred to next
session, pending GAM drilldown.

## Next steps

**Active:**
1. **GAM drilldown** — government-entity targets, registrant list, specific
   sub-provision, resolution mechanism (if any). First priority.
2. **Decide GAM's role** — replace, add as exhibit 4, or reframe the case's
   core claim (see "open decision" above).
3. **Re-verify E1/E6 exhibit text** against the 73-code baseline (superseded
   text already flagged inline above; needs a clean rewrite once GAM's role
   is decided, so it isn't rewritten twice).
4. Optional: add House-inclusive totals to E7/E10 exhibit text (currently
   Senate-only, correctly labeled, but not re-summed with House included).
5. Backfill `queries.sql` with E6-E14 (currently only E1-E5 saved) and add the
   expanded-keyword-map ranking query, labeled distinctly from the original
   E1/E6 query (same SQL, different underlying table state).
6. Ready for findings-report drafting once #1-#3 are resolved.

**Done:**
- ~~Verification pass on E1, E6, E7, E8, E10~~ — DONE 2026-06-25.
- ~~Novelty scan~~ — DONE 2026-06-25. Coverage verdict: `novel`.
- ~~E2 re-verify spectrum flatness~~ — DONE 2026-06-25.
- ~~Extended framing/novelty scan~~ — DONE 2026-06-25. Culpepper (2010) anchor.
- ~~E9 primary citations~~ — DONE 2026-06-25. CAA 2023 (Dec 19, 2022): scheduled
  4.47% cut reduced to ~2.08% effective cut via +2.5% CF adjustment. CAA 2024
  (Mar 9, 2024): +2.93% update for Mar 9–Dec 31. CMS fact sheet URLs cited.
- ~~E11 primary citations~~ — DONE 2026-06-25. House vote #30: 357–70 Jan 31 2024.
  Senate vote #230: 48–44 cloture failure Aug 1 2024. Official roll call URLs cited.
- ~~E12 primary citations~~ — DONE 2026-06-25. OBBBA = P.L. 119-21, Section 174A.
- ~~CBO spectrum score~~ — DONE 2026-06-25. Enacted figure is **$85B** FY2025–2034
  (not $88B — that was an earlier House version). Source: CBO pub 61570 via CRFB.
- ~~Builder → skeptic → judge pass~~ — DONE 2026-06-30. Verdict: supported, with
  corrections. See "Verdict" section above.
- ~~Fix E13's "runnable across all 80 LDA issue codes" claim~~ — DONE 2026-06-30.
- ~~Expand `ISSUE_KEYWORDS` and re-check ranking~~ — DONE 2026-06-30. Surfaced
  GAM as new dominant outlier — see "Keyword-map expansion" section above.
