# Log: invisible-provisions

Append-only. Most recent entries at bottom.

---

## 2026-06-25 — Case opened

Promoted from lead `tec-quiet-lobbying` (screen: quiet-issue-quadrant, run 15).

**Session summary:** The `quiet-issue-quadrant` screen surfaced TEC as the
second-quietest issue code by lobby-to-press ratio (4.99x, z=2.28). Drilldown
through the session identified spectrum auction reauthorization as the specific
mechanism: authority lapsed March 2023, restored in OBBBA 2025 as a revenue
offset. Sustained flat lobbying (~220 acts/quarter, 2022-2025) with no spike
around lapse or restoration. Congress is the primary lobbying target (not FCC).
ACP press split is nearly bipartisan. Industry contribution flow bipartisan.

**Key finding shape:** The provision moved not because lobbying escalated but
because the OBBBA needed the CBO score. The lobbying was background noise that
kept the option alive, not a targeted campaign that forced action.

**Framing decision:** Case opened as "invisible provisions" — a class story
needing 2-3 examples. Spectrum is exhibit 1. Framing to be sharpened once
additional examples are in hand from `issue-quarterly-surge`.

**Evidence blocks written:** E1 (TEC ratio), E2 (spectrum flatness), E3
(Congress as target), E4 (ACP partisan split), E5 (bipartisan money flow).
All UNVERIFIED — scout numbers only.

**Next session:**
1. Run `issue-quarterly-surge` to surface additional candidate provisions.
2. Verify E1-E5 (re-derive figures independently).
3. Source OBBBA spectrum provision text + CBO score ($88B+ figure is from
   editor's research, needs a citable primary source).
4. Check keyword-gap alternative for TEC press quietness (do members discuss
   spectrum under different terms?).

---

## 2026-06-25 — MMM / Physician Fee Schedule scoping

**Decision:** Pivoted from `issue-quarterly-surge` screen to re-running
`quiet-issue-quadrant` and examining full ranked output. MMM (Medicare/Medicaid)
is the corpus's quietest issue code (z=2.68, above TEC at z=2.28) and had not
been explored — previously skipped due to a prior Medicare case that was killed
as overstated.

**Key findings this session:**

- MMM topic breakdown: IRA/drug pricing (2,328 acts), Physician Fee Schedule
  (1,929), 340B (1,562), Medicare Advantage (1,540), Telehealth (1,189).
  PFS lobbying grew 560 → 631 → 738 acts/year from 111–135 registrants.
- PFS press silence confirmed: 31 / 60 / 57 press releases per year across
  all of Congress, ~13-18:1 lobby-to-press ratio. Bipartisan — no party is
  talking about it more. About half the members who did publish were not on
  health committees.
- 340B is the most extreme sub-topic by ratio (~50:1) but absolute press
  numbers are very small.
- Site-neutral payments: small but fast-growing lobby presence (215→376→399
  acts/yr), near-zero press (1–5 releases/yr).
- Web research confirmed PFS legislative mechanism: annual statutory cut
  averted each year via last-minute conversion-factor rider in omnibus spending
  bill. CY2023 fix: CAA 2023 (Dec 29, 2022). CY2024 fix: partial via CAA 2023
  pre-position + mid-year CAA 2024 (Mar 9, 2024). Pattern extends back years
  further per AMA records.

**Housekeeping:** Saved `quiet-issue-quadrant` SQL to
`investigations/screens/quiet-issue-quadrant/screen.sql`, updated `sql_path`
in newsroom.db, patched `run-data-newsroom` skill to make sql_path persistence
an explicit requirement.

**Evidence blocks written:** E6 (MMM corpus rank), E7 (PFS lobby trend),
E8 (PFS press silence + committee breakdown), E9 (PFS legislative mechanism
from web research). All UNVERIFIED except E9 (external source, needs primary
citation).

**PFS as exhibit 2:** Strong candidate. Fits the invisible-provisions pattern
cleanly — technically complex formula, narrow concentrated industry, Congress
acts via must-pass rider annually, no floor vote, no press. Structurally
parallel to spectrum (exhibit 1): both cases where a formula or lapse is quietly
managed rather than debated.

**Next session:**
1. Decide whether to verify E6-E9 now or add a third exhibit first.
2. For E9: find primary legislative text (CAA 2023, CAA 2024) and CMS
   conversion-factor fact sheets as citable sources.
3. Consider 340B or site-neutral as possible exhibit 3 candidate.

---

## 2026-06-25 — Section 174 R&D expensing as exhibit 3 candidate

**Approach:** Pivoted from issue-code–level screening to bill-number extraction.
Extracted H.R.XXXX references from free-text descriptions across non-MMM/TEC/BUD
codes, normalized bill numbers, cross-checked against press_fts. Most heavily
lobbied bills (IRA, NDAA, IIJA, FAA reauth) are high-profile and not useful.
H.R.7024 (Tax Relief for American Families and Workers Act) stood out: 305
registrants / 1,563 acts under TAX, with near-zero press on the business
provisions specifically.

**Key finding:** H.R.7024 bundled politically visible child tax credit (413 press
releases / 159 members) with technically obscure business provisions — Section
174 R&D expensing, bonus depreciation (168k), business interest (163j). The
business provisions generated 14–66 press releases from 13–35 members across all
of Congress. Classic invisible-provisions packaging: use a salient item as cover
for the industry payload.

**Legislative arc (from web research):**
- TCJA (2017) changed R&D expensing to 5-year amortization, effective 2022
- Industry lobbied 2022–2024 to reverse it (~305 registrants in our corpus)
- H.R.7024 passed House 357-70 (Jan 31, 2024), died Senate cloture 48-44
  (Aug 1, 2024) — Republicans blocked over child tax credit, not business terms
- Section 174A fix ultimately passed in OBBBA (signed July 4, 2025) —
  same bill that contained spectrum auction reauthorization (exhibit 1)

**Fit assessment:** Strong candidate for exhibit 3. Different mechanism from
spectrum (lapsed authority) and PFS (annual formula cut): here a prior tax law
change created an industry problem, lobbying sought reversal, Congress eventually
delivered via must-pass reconciliation after one failed vehicle. The OBBBA
connection to exhibit 1 is an editorial bonus — both exhibits landed in the same
bill after years of separate quiet lobbying.

**Evidence blocks written:** E10 (lobby volume + press silence from corpus),
E11 (H.R.7024 House passage + Senate failure, external), E12 (OBBBA fix,
external). E10 UNVERIFIED; E11-E12 EXTERNAL SOURCE.

**Next session:**
1. Decide on verification order — three exhibits now in hand (E1-E5 TEC/spectrum,
   E6-E9 PFS, E10-E12 Section 174). May be enough to begin verification pass.
2. For E11-E12: pull Congress.gov roll call and OBBBA statutory text as primary
   citations.
3. For E9: CMS conversion-factor fact sheets needed as primary citation.
4. Consider whether bonus depreciation (168k) or 340B warrants a separate
   exhibit or is better as supporting color within the Section 174 block.

---

## 2026-06-25 — Verification pass + novelty scan

**Verification pass (E1, E6, E7, E8, E10):**

- **E1 VERIFIED:** TEC 4.989x / z=2.284. Scout rounded correctly to 4.99x / z=2.28. ✓
- **E6 VERIFIED:** MMM 5.592x / z=2.681. Scout rounded correctly to 5.59x / z=2.68. ✓
- **E7 VERIFIED:** PFS lobby trend 560/631/738 acts per year, 111/114/135 registrants.
  Exact match to scout. ✓
- **E8 VERIFIED with precision correction:** Press 31/60/57 releases per year — exact
  match. Committee breakdown 39 health-committee / 31 other — confirmed. Lobby-to-press
  ratio: scout said "~13-18:1" but 2023 is actually 10.5:1; corrected to "10-18:1." ✓
- **E10 VERIFIED with material correction:** Scout 305/1,563 was an undercount.
  Verified: 395 registrants / 2,085 acts. Discrepancy: scout excluded 2023 Q4
  filings that named H.R.7024 before its formal Jan 2024 introduction — those are
  legitimate records. Scout lobby figure must not be cited. Press also revised:
  CTC 420/161 (not 413/159), R&D 54/28 (not 66/35), bonus dep 15/14 (not 14/13). ✓

**Novelty scan:** Four web searches — lobby-to-press methodology, spectrum/OBBBA,
PFS lobbying silence, Section 174 lobbying analysis. No prior publication found using
this methodology or covering these three exhibits as a pattern. Individual provisions
are well-documented by trade press and advocacy groups; the measurement layer is
novel. Coverage verdict: `novel`. Logged in case.md Prior Coverage section.

**No prior coverage found per novelty scan.** Case is ready for builder → skeptic
→ judge pass on the verified claims.

**Remaining before publication:**
- E9: Primary citations (CAA 2023 / 2024 text, CMS conversion-factor fact sheets)
- E11-E12: Congress.gov roll call + OBBBA Section 174A statutory text
- E2: Re-verify spectrum flatness numbers (202-231 acts/quarter, 118-149 registrants)
- Builder → skeptic → judge verification pass
- CBO citation for $88B spectrum score

---

## 2026-06-25 — E2 verification + extended framing/novelty scan

**E2 VERIFIED:** Spectrum lobbying flatness confirmed across all 17 complete quarters
2022–2025. Range: 202–231 acts/quarter, 127–149 registrants, ~$6.5–7.8M income/quarter.
No anomaly around March 2023 lapse or July 2025 OBBBA restoration. Income trend is
flat-to-very-slightly-upward. Scout range was correct. → evidence.md E2.

**Extended framing scan (E13):** Ran broader web search on how the concept of
industry lobbying on technical/low-salience issues has been framed before in
academic and journalistic contexts. Key findings:

- **Culpepper (2010), *Quiet Politics and Business Power*** is the canonical
  academic reference. Theory: low salience → business lobbies quietly → legislator
  deference → industry wins. Qualitative/comparative (European corporate control);
  no LDA data; no quantitative operationalization.
- EU salience measurement literature (Beyers et al.) has tried to quantify salience
  via media articles but hasn't touched US LDA/press data.
- Bloomberg Government, ProPublica, Sludge have covered pieces of this at the
  narrative or tool level; none has built a cross-issue-code lobbying-to-press ratio.
- No prior publication covers spectrum + PFS + Section 174 as a pattern.

**Framing implication:** The writeup should name Culpepper explicitly — "we built
a data instrument to measure what Culpepper described" — rather than presenting
the concept as novel. The *methodology* (lobby-to-press ratio across 80 LDA codes)
and the *US federal data application* are what's new.

**Coverage verdict confirmed:** `novel` on method + multi-exhibit pattern.

**Updated case.md:** Prior Coverage section expanded with academic + journalism
landscape. Next steps list updated — E2 now VERIFIED, framing scan done.

**Remaining before builder → skeptic → judge:**
- E9: CMS fact sheets + CAA 2023/2024 statutory text (primary citations for PFS mechanism)
- E11-E12: Congress.gov roll calls + OBBBA Section 174A text (primary citations)
- CBO spectrum score citation (~$88B; web confirms figure, need direct CBO link)

---

## 2026-06-25 — Primary citations for E9, E11, E12 + CBO spectrum score

**E9 — PFS mechanism citations added:**
- CAA 2023 (signed Dec 19, 2022): scheduled 4.47% CF cut reduced to ~2.08% effective
  cut via +2.5% CF adjustment. Resulting CF ~$33.89. Also pre-positioned +1.25% for
  CY2024. Source: AASM summary (aasm.org) + CMS CY2023 PFS fact sheet URL.
- CAA 2024 (signed Mar 9, 2024): added +2.93% CF update for Mar 9-Dec 31, 2024.
  Pre-CAA CY2024 CF was $32.74 (-3.4% from $33.89). Source: AHA + McDermott+ summaries
  + CMS CY2024 PFS fact sheet URL. CMS site blocks direct fetch; cited by URL.

**E11 — H.R.7024 roll call citations added:**
- House Vote #30 (Jan 31, 2024): 357-70. Passed under suspension of rules (2/3 required).
  Source: clerk.house.gov roll call + GovTrack.
- Senate Vote #230 (Aug 1, 2024): 48-44 cloture on motion to proceed — failed (60 needed).
  Source: senate.gov roll call + GovTrack. Note: cloture on motion to proceed, not final
  passage; bill never got an up-or-down Senate vote.

**E12 — OBBBA Section 174A citations added:**
- OBBBA = P.L. 119-21, signed July 4, 2025. Section 174A: immediate domestic R&D
  expensing for tax years after Dec 31, 2024; small business retroactive election for
  2022-2024 (deadline July 6, 2026); foreign R&D still 15-year amortization.
  Sources: Grant Thornton, ABGI tracker, CBO pub 61570.

**CBO spectrum score clarified:**
- Enacted figure is $85B FY2025-2034 (not $88B — $88B was an earlier House version
  score). Scored as "Auction Wireless Spectrum" under Other Offsetting Receipts.
  Source: CBO pub 61570 (P.L. 119-21 budgetary effects) via CRFB analysis.
  Updated case.md E1 exhibit to reflect correct figure.

**Status:** All primary citations now in place. Case is ready for builder -> skeptic
-> judge verification pass.

---

## 2026-06-30 — Builder → skeptic → judge verification pass

**Purpose:** First real test of this skill's verification pattern (previously
unexercised). Ran inline (three roles, one session) per the skill's guidance
for lighter checks — no Workflow launch (billed, user-triggered only).

**Builder:** Re-confirmed E1/E6 headline numbers directly against
`derived_issue_quarter_volume_press` (MMM 5.59x z=2.68, TEC 4.99x z=2.28, BUD
4.41x z=1.91) — matched prior verified figures exactly. Rest of the case was
already built from the prior four sessions' work.

**Skeptic:** Ran the full corpus-specific checklist (see reference/verification.md)
independently against all three exhibits, re-deriving rather than reading the
builder's queries first. Two material findings, both framing corrections rather
than kills:
1. **Denominator overstatement.** `ISSUE_KEYWORDS` in
   `build_derived_issue_quarter_volume_press.py` only maps 22 of 79 issue codes
   to press keywords; the other 57 get `n_press_releases=0` structurally, not
   because Congress is silent. case.md had said MMM was "quietest in the entire
   corpus" — actually quietest of the 21-code subset that clears the `press>=100`
   threshold within the 22 mapped codes. E13 also overclaimed "runnable across
   all 80 LDA issue codes." Both fixed directly in case.md/evidence.md.
2. **Senate-only undercount in sub-topic drilldowns.** E2/E7/E10 query
   `senate_lobbying_activities` alone; House lobbying is real and comparable in
   size (+2,684 acts on PFS, +2,244 on Section 174, all-years) but wasn't
   counted in the cited totals — even though E1/E6's corpus-wide ranking
   itself *does* sum Senate+House correctly. Fixed via explicit "Senate LDA
   only" labeling in case.md exhibit text; full House-inclusive re-sum left as
   an open next step (not required to sustain the claim's direction).
   Checklist items checked and clean: junk free-text exposure, honoree-match
   confidence (not load-bearing here), base rate/multiple comparisons (21-item
   ranking, not large-N), time-window alignment, FTS false-positive risk.

**Judge:** Verdict **supported, with corrections**. Confidence **medium-high**
on individual exhibit numbers (twice-verified now); **medium** on the
"class of provisions" framing given N=3 hand-curated exhibits. Neither
skeptic finding reverses any exhibit's direction — both narrow precision.
Corrections applied directly to case.md/evidence.md same session. Full
detail: evidence.md E14, case.md "Verdict" section.

**Housekeeping gap found:** `queries.sql` only has E1-E5 saved; E6-E12's
queries live only in evidence.md. Should be backfilled before this case is
used as a skill-behavior reference, since "every cited query lives in
queries.sql so numbers re-run" is a stated provenance rule.

**Meta-observation for skill review:** the checklist-driven skeptic pass
surfaced findings that pure "does the number reproduce" verification (the
2026-06-25 session) did not — the coverage-gap and Senate-only issues are
about what the query *means*, not whether it runs correctly. This is exactly
the failure mode the skill's opening line names ("plausible-but-wrong: a
clean-looking query that means something other than the headline"). Worth
discussing whether/how to strengthen the skill doc based on this run — see
next user turn.

---

## 2026-06-30 — verification.md updated; ISSUE_KEYWORDS expanded 21→75 codes; new outlier (GAM) surfaces

**Skill change:** Added a **Denominator/scope honesty** item to the skeptic's
checklist in `.claude/skills/track-investigation/reference/verification.md`
(after "Base rate"). Neither "base rate" nor "multiple comparisons" — the two
closest existing items — actually covers "is the comparison population itself
honestly described," which is what E14's Finding 1 was. New item: check what
built the comparison set (a hand-curated keyword map, a filtered query, etc.),
not just whether the ranking math within it is correct.

**Root-cause check on the keyword gap:** Investigated why 57 of 79 issue codes
had zero press keywords rather than assuming vagueness. Spot-checked five
"obviously specific, not vague" unmapped codes directly against `press_releases`:
tobacco (763 hits), aviation (5,348), copyright/patent/trademark (541), food
safety/labeling (708), gambling (215). All had substantial real press coverage
waiting — the exclusion was never a deliberate vagueness call, just an
incomplete map built in one commit (433711c) for one screen's immediate needs.
Genuinely too-generic codes do exist (media/science/government/constitution —
tens of thousands of generic-usage hits each) and were kept excluded, but now
with an explicit code comment explaining why, replacing a silent gap with a
documented one.

**ISSUE_KEYWORDS expanded 21→75 of 79 ref_issue_codes**, in both
`scripts/build_derived_issue_quarter_volume_press.py` (canonical copy) and
`scripts/build_derived_member_press_topics.py` (synced copy — the two must
match per the code comment). Deliberately still excluded: MIA, SCI, GOV, CON
(documented in-file). TOR included despite low absolute volume (~36 raw hits)
with a low-confidence note rather than excluded, to avoid repeating the same
silent-gap pattern on thin grounds.

**Keyword QA caught one false positive before it reached a finding:** initial
GAM (Gaming/Gambling/Casino) keyword set included "lottery," which
overwhelmingly matched unrelated immigration press releases ("diversity visa
lottery," "green card lottery") rather than gambling — eyeballed 8 sample
matches, most were visa-lottery language from members like Lofgren, Meng,
Clarke. Removed "lottery" from GAM. Also tightened MON ("currency" →
"digital currency"/"currency manipulation" — raw "currency" matched generic
foreign-aid/monetary-policy mentions) and UTI ("rate case" dropped, "utility"
→ "utility bill"/"public utility" — raw "utility" and "rate case" were
noisy). Rebuilt both derived tables after each fix; confirmed GAM's ranking
survived the "lottery" removal (17.0x cf. 13.27x pre-fix — dropping the noisy
keyword *increased* the ratio because it removed press volume, not lobbying
volume).

**Result: re-ran the case's E1/E6 ranking query against the expanded map.**
Comparison population widened from 21 codes to **73 codes** (of 79 total,
`press_2224 >= 100` threshold). Full top-15 by z-score, 2022-2024:

| code | name | acts | press | ratio | z |
|---|---|---|---|---|---|
| GAM | Gaming/Gambling/Casino | 1,751 | 103 | 17.0x | **5.08** |
| ART | Arts/Entertainment | 1,149 | 124 | 9.27x | 2.35 |
| CSP | Consumer Issues/Safety/Products | 7,398 | 797 | 9.28x | 2.35 |
| CPT | Copyright/Patent/Trademark | 5,779 | 660 | 8.76x | 2.17 |
| INS | Insurance | 4,821 | 591 | 8.16x | 1.96 |
| SPO | Sports/Athletics | 1,275 | 175 | 7.29x | 1.65 |
| CPI | Computer Industry | 6,969 | 1,089 | 6.4x | 1.33 |
| COM | Communications/Broadcasting/Radio/TV | 4,532 | 744 | 6.09x | 1.23 |
| MMM | Medicare/Medicaid | 25,816 | 4,617 | 5.59x | 1.05 |
| MED | Medical/Disease Research/Clinical Labs | 4,507 | 818 | 5.51x | 1.02 |
| AER | Aerospace | 3,040 | 608 | 5.0x | 0.84 |
| TEC | Telecommunications | 13,136 | 2,633 | 4.99x | 0.84 |
| NAT | Natural Resources | 14,452 | 2,947 | 4.9x | 0.81 |
| RES | Real Estate/Land Use/Conservation | 2,764 | 597 | 4.63x | 0.71 |
| BUD | Budget/Appropriations | 88,593 | 20,071 | 4.41x | 0.63 |

**GAM is now the dominant outlier — z=5.08, more than double the next-highest
code (z=2.35), and the ratio (17.0x) and z-score are both larger than any
figure previously cited for TEC or MMM against the 21-code baseline.** TEC and
MMM, the case's two verified exhibits, drop to z≈0.84-1.05 against the fuller
73-code comparison — no longer statistical outliers, just upper-middle of the
pack. This is precisely the outcome the skeptic's Finding 1 warned was
possible: the two headline exhibits may have looked extreme only because the
comparison population was artificially narrow.

**Quick GAM lobbying/press trend (UNVERIFIED, scout-level only — not yet
drilled down):**
| year | acts | press |
|---|---|---|
| 2022 | 593 | 6 |
| 2023 | 571 | 45 |
| 2024 | 587 | 52 |
| 2025 | 721 | 72 |

Sustained lobbying (~570-720 acts/yr), press rising off a near-zero base but
still an order of magnitude below lobbying volume throughout. Shape is
consistent with the invisible-provisions pattern (steady industry lobbying,
minimal congressional communication) but not yet drilled to a specific
provision, government-entity target, or resolution vehicle the way exhibits
1-3 were. Sports betting expansion (post-Murphy v. NCAA, ongoing state-by-state
rollout with federal-preemption/taxation questions) is the obvious hypothesis
to test first, given SPO's co-occurrence at z=1.65.

**Case status implication:** this is not yet a fourth exhibit — it's an
unverified, undrilled scout number, same starting point exhibits 1-3 each had.
But it directly changes how exhibits 1-3 should be framed: TEC and MMM are no
longer defensible as "the quietest in the corpus" under any denominator wider
than the original hand-picked 21-22 codes. case.md and evidence.md updated to
reflect this (see below). GAM drilldown is the natural next session.

**Next session:**
1. Drill GAM: government-entity targets, registrant list, specific
   sub-provision (sports betting federal excise tax? PASPA-adjacent state
   preemption fights? online gaming/iGaming?), resolution mechanism if any.
2. Decide whether GAM replaces one of exhibits 1-3, is added as exhibit 4, or
   changes the case's core claim from "three examples of a pattern" to
   "here is the actual quietest issue in the corpus, plus context."
3. Re-verify E1/E6's exhibit text now that the "quietest in corpus" framing
   needs a second correction pass (the 2026-06-30 skeptic fix said "21-code
   subset"; now the honest comparison is "73-code corpus, and TEC/MMM are not
   the extreme cases in it").
4. queries.sql backfill (E6-E12, still outstanding) — add this new ranking
   query too, labeled distinctly from the original E1/E6 query (same SQL,
   different underlying table state).

**Next session:**
1. Fix E13 "80 LDA issue codes" claim — DONE this session, see above.
2. Backfill queries.sql with E6-E12.
3. Decide whether to extend `ISSUE_KEYWORDS` coverage before publication or
   caveat the 22-code scope permanently.
4. Ready for findings-report drafting once queries.sql backfill is done.

## 2026-07-15 — written up in findings.md, GAM left as unverified aside

Deadline day. Wrote up E1-E3 (spectrum, PFS, Section 174) in `/findings.md`
as three independently-verified examples of the quiet-provision signature,
explicitly *not* claiming "quietest in the corpus" — per user instruction,
framing is just "quiet provisions and their signature," full stop. GAM
mentioned in the caveats as an unverified scout-level aside (stronger ratio,
undrilled), not used as evidence. GAM drilldown, queries.sql backfill
(E6-E14), and the open "GAM's role" decision are left undone — out of scope
for the report given the deadline.

## 2026-07-15 (cont'd) — added independent press-volume baseline (E15)

User pushback on the findings.md draft: the press-release counts (31-60/yr,
54-66/yr) had no baseline showing they're actually low, other than the
lobby-to-press ratio we'd just deliberately dropped from the write-up. Added
E15: a per-member press-release baseline computed directly against
`press_releases` (members who post any releases average 74-89/year each,
2022-2024), independent of the issue-code ranking. This lets the entry say
"fewer releases across all of Congress than one typical engaged member
produces alone in a year" without leaning on the ratio/z-score comparison.
Query and result logged in queries.sql. findings.md entry updated to cite
this baseline directly.
