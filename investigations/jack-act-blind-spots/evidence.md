# Evidence — jack-act-blind-spots

Two independent filer chapters (Hanson, Hunter) plus the enforcement-context
finding (GAO). Each chapter's facts stand on their own; the systemic claim is
their combination plus the enforcement record — see case.md Verdict.

---

## Hanson / VVA chapter (carried over from hanson-vva-conviction-flicker, E1-E8 relabeled EHanson1-8)

## EHanson1 — 3 of 7 post-conviction original quarterlies lack the disclosure
- **query/script:** `queries.sql#q-hanson1` (register row; built by
  `scripts/build_derived_convicted_lobbyist_register.py`)
- **result:** lobbyist_id 143691, HANSON, HAROLD: n_post_quarterlies=7,
  n_post_disclosed=4, n_post_missing=3. Missing: 2023 Q3
  (06b7c4cf-88ec-478e-affe-ff9c7b71b4f3), 2023 Q4
  (5550037a-1d72-451e-a3f5-4ff8cc3ca369), 2025 Q1
  (39b000c9-ee52-4fc8-8998-fefb18cbcf44). Present: all four 2024 quarterlies
  (1dd174b2, 0cc30def, f3fe3aef, 4f1097d5).
- **source records:** filing_uuids above →
  https://lda.gov/filings/public/filing/{uuid}/print/
- **caveats:** register counts ORIGINAL quarterlies only (amendments checked
  separately, see EHanson5); "post-conviction" here uses the disclosed date
  2013-07-16, which is actually the BIS order date (see EHanson3) — all 7
  filings postdate both dates, so the count is insensitive to this.
- **verdict:** supports

## EHanson2 — The corpus norm is re-disclosure on every quarterly; gaps are deviation
- **query/script:** `queries.sql#q-hanson2`
- **result:** 12 of 15 convicted lobbyists (Senate register, pre-Hunter-drill
  population) with ≥1 post-conviction quarterly have zero missing; BURKMAN
  471/471 disclosed, WOHL 181/182. Only HUNTER (6/6 missing), HANSON (3/7),
  WOHL (1/182) deviate.
- **source records:** derived_convicted_lobbyist_register (rebuildable);
  underlying senate_filing_conviction_disclosures rows.
- **caveats:** small population; the norm could reflect filing-software
  autofill rather than diligence (see E-GAO note on the same population's
  concentration) — this matters for the "how unusual" framing, not for the
  legal obligation itself.
- **verdict:** supports (kills the "form doesn't require re-disclosure" out)

## EHanson3 — The disclosed text/date is the BIS administrative settlement, not the court conviction
- **query/script:** `queries.sql#q-hanson3` (disclosure text); outside records
  for the identification (disclosed, not corpus evidence).
- **result:** VVA's disclosure text quotes the BIS §764.2(g) charging language
  verbatim and dates it 2013-07-16 (the BIS order date; 15-year export-
  privilege denial). Court record: U.S. v. Qi Hanson, D.D.C. 1:09-cr-00071 —
  Harold Dewitt Hanson pleaded guilty 2009-11-13 to Count 3, false statement,
  18 U.S.C. §1001 (a JACK predicate verbatim). So the disclosure, when
  present, mis-describes the conviction; the obligation itself stands on the
  2009 plea.
- **source records:** senate_filing_conviction_disclosures rows for
  lobbyist_id 143691; BIS order (Federal Register 2013-17512); CourtListener
  docket 6455213.
- **caveats:** docket entries read via CourtListener search result — pull the
  actual docket before publication (sentence, any vacatur).
- **verdict:** supports (and sharpens: even the present disclosures are wrong)

## EHanson4 — House-side filings carry the same disclosure text (corroboration)
- **query/script:** `queries.sql#q-hanson4`
- **result:** house_convictions has the identical description for "Harold
  Hanson", date 07/16/2013 — VVA's House filings disclose (at least
  sometimes).
- **source records:** house_convictions rows (house_filing_id + source_file).
- **caveats:** House lobbyists are name-only; gap analysis done separately
  (EHanson7).
- **verdict:** neutral (corroborates identity/text)

## EHanson5 — No amendment cures any of the three gap quarterlies
- **query/script:** `queries.sql#q-hanson5`
- **result:** for each gap period, no amendment carries a disclosure row for
  lobbyist 143691. 2023 Q3/Q4 have no amendments at all. 2025 Q1 has a `1A`
  amendment (a4a090e8) that carries no disclosure AND drops Hanson from the
  lobbyist list entirely rather than adding the disclosure.
- **source records:** filing_uuids 06b7c4cf / 5550037a / 39b000c9 / a4a090e8 →
  https://lda.gov/filings/public/filing/{uuid}/print/
- **caveats:** "cure" = an amendment carrying a
  senate_filing_conviction_disclosures row for lobbyist_id 143691 — none
  exists.
- **verdict:** supports (no later amendment cures any gap; the
  most-recent-gap amendment dropped the lobbyist instead)

## EHanson6 — Live LDA source matches ingest (not an ingest artifact)
- **query/script:** WebFetch of the LDA REST API `v1/filings/{uuid}/`.
- **result:** 2023 Q3 gap (06b7c4cf) — live API confirms `conviction_disclosures`
  empty, matching ingest. 2024 Q1 (1dd174b2) — live API confirms the BIS-text
  disclosure present, matching ingest.
- **source records:** https://lda.senate.gov/api/v1/filings/06b7c4cf-88ec-478e-affe-ff9c7b71b4f3/
  and .../1dd174b2-f577-4155-9c42-785623a6c562/
- **caveats:** the other two gap uuids (2023 Q4, 2025 Q1) not individually
  re-pulled live — mechanism confirmed identical to ingest on the pair
  pulled, which is what rules out a parser artifact.
- **verdict:** supports (rules out ingest artifact)

## EHanson7 — House-side (name-keyed) shows the same gap pattern
- **query/script:** `queries.sql#q-hanson7`
- **result:** 19 VVA House filings; Harold Hanson appears on 8.
  house_convictions carries 'Harold Hanson' ONLY on the four 2024 filings —
  the identical three-quarter gap as the Senate side (2023 Q3, 2023 Q4, 2025
  Q1), plus an extra pre-2024 listing (2023 Q2 amendment) without disclosure.
- **source records:** house_filing_id values (+ source_file); house_convictions
  rows for 'Harold Hanson'.
- **caveats:** House lobbyists are name-only-keyed — matched last_name LIKE
  '%Hanson%', first_name Harold.
- **verdict:** supports (independent House-side corroboration; not an
  artifact of one keying scheme)

## EHanson8 — Criminal docket (legal predicate) — live pull failed
- **query/script:** WebFetch CourtListener docket 6455213 (HTML + REST API).
  OUTSIDE DATA — legal predicate / case identification only.
- **result:** CourtListener HTML returned HTTP 403 (Cloudflare bot block);
  REST API returned HTTP 401 (auth required). Plea stands from EHanson3's
  prior search: D.D.C. 1:09-cr-00071, guilty plea 2009-11-13, Count 3, 18
  U.S.C. §1001. Sentence and any vacatur remain unverified/owed.
- **source records:** CourtListener docket 6455213 — not retrieved.
- **caveats:** OUTSIDE DATA, cited for legal predicate/identification only —
  never evidence for any filing-level claim above.
- **verdict:** neutral / owed

## EHanson9 — Builder→skeptic→judge tribunal verdict (Hanson chapter, standalone)
- **query/script:** N/A — verification tribunal (Opus builder/skeptic, Fable
  judge), overnight 2026-07-07, on EHanson1-8 as then-labeled E1-E8.
- **result:** facts supported at high confidence (gaps real, live-verified,
  uncured, both chambers). Story-as-standalone-flicker REFUTED: the three
  gaps are two boundary events, not scattered evasion — 2023 Q3+Q4 were one
  late batch filing (2024-02-21, same preparer John Stovall) during Hanson's
  onboarding; 2025 Q1 is his departure quarter, later corrected by
  de-listing. The 12/15 "norm" (EHanson2) is contaminated by two autofill
  mega-filers (Burkman/Wohl = 74% of the comparison population); boundary
  gaps recur even there (Wohl's sole gap is his latest quarter too). Judge:
  park the standalone Hanson case; recommend systemic re-scope — this
  restructure.
- **caveats:** this verdict was rendered on the Hanson-only case; it does not
  cover Hunter or the GAO finding, both added in this restructure.
- **verdict:** refutes (standalone "flicker" framing only) — does not touch
  the underlying gap facts, which stand.

---

## Hunter / VALOON chapter (new, this session — source-verified, not desk-derived-only)

## EHunter1 — 0 of 6 post-conviction quarterlies disclose, after 1 registration that did
- **query/script:** `queries.sql#q-hunter1` (register row, rebuilt this
  session from `scripts/build_derived_convicted_lobbyist_register.py` against
  a scratch copy of the live `gain.db` to confirm current, not stale)
- **result:** lobbyist_id 144165, HUNTER, DUNCAN: n_filings_disclosed=1 (the
  registration only), n_post_quarterlies=6, n_post_disclosed=0,
  n_post_missing=6. The one disclosure is on filing f760418c-a038-48d1-a6b3-d37173508fff
  (type RR = Registration, 2023 Q1, posted 2023-10-15). Missing quarterlies:
  4ac94cc9 (Q1 2023), 5767af8b (Q2 2023), cbbf216d (Q3 2023), a2ab1e69 (Q4
  2023), 11d51df2 (Q1 2024), 24be134b (Q2 2024).
- **source records:** filing_uuids above →
  https://lda.gov/filings/public/filing/{uuid}/print/
- **caveats:** register's `n_post_quarterlies` filters to filings dated after
  `conviction_date` (2019-12-03, the plea date as disclosed on the RR) — the
  RR itself is not counted as a "post" quarterly since it's a registration,
  which is why it shows n_filings_disclosed=1 separately.
- **verdict:** supports

## EHunter2 — The disclosure text (verbatim, from Hunter's own registration)
- **query/script:** `queries.sql#q-hunter2`
- **result:** senate_filing_conviction_disclosures row on the RR reads (as
  filed, typos preserved): "Defendant agrees to plead guilty ot Count One of
  the Indictment charging him with conspiring with co-defendant Margaret
  Hunter to knowingly and willfully convert Duncan D. Hunter for Congress
  Campaign Committee (the 'Campaign') funds to personal use... in violation
  of Title 18, United States Code, Section 371." Date: 2019-12-03.
- **source records:** filing_uuid f760418c-a038-48d1-a6b3-d37173508fff.
- **caveats:** 18 U.S.C. §371 (conspiracy) is not itself one of the JACK
  Act's enumerated predicate offenses by name (bribery, extortion,
  embezzlement, illegal kickback, tax evasion, fraud, conflict of interest,
  false statement, perjury, money laundering) — but the disclosed conduct
  ("convert campaign funds to personal use") is naturally read as embezzlement-
  adjacent, and more importantly, VALOON/Hunter already made the predicate
  judgment themselves by disclosing it once. This is the fact that forecloses
  a "we don't think this conviction qualifies" defense — see EHunter4.
- **verdict:** supports

## EHunter3 — All 7 filings (RR + 6 quarterlies) self-filed by Hunter, same name, no preparer change
- **query/script:** `queries.sql#q-hunter3` (`posted_by_name`, `dt_posted`
  across all 7 filings)
- **result:** `posted_by_name` = "Duncan Hunter" on every one of the 7
  filings, spanning 2023-10-15 (RR) through 2024-08-12 (last Q2 2024
  quarterly). No preparer change across the gap.
- **source records:** filing_uuids as in EHunter1 + the RR.
- **caveats:** this is the discriminator this case's Hanson chapter used in
  reverse — Hanson's gaps correlate with a preparer/onboarding boundary,
  which supported a clerical read; Hunter's gaps do NOT correlate with any
  preparer change, which forecloses that specific innocent explanation.
  "I (Hunter) forgot" on 6 consecutive occasions remains conceivable and
  intent is still not observable (2 U.S.C. §1606 requires knowing/corrupt
  omission for sanctions) — this evidence closes off the mechanical
  explanation, not the intent question.
- **verdict:** supports (kills the preparer-continuity/clerical-handoff
  explanation available in the Hanson chapter; does not establish intent)

## EHunter4 — No legal off-ramp: pardon and predicate ambiguity don't excuse a disclosure VALOON already made
- **query/script:** N/A — legal-standard cross-reference, `sources/jack-act-notice.md`
  point 2-3 + point 5 against EHunter1-2.
- **result:** the JACK Act notice states the disclosure, once triggered, is
  required "on every future registration or quarterly report" with no
  lookback limit, and is explicitly silent on pardons (Trump pardoned Hunter
  December 2020). VALOON's RR disclosure was filed October 2023 — nearly 3
  years post-pardon — meaning VALOON/Hunter's own filing already resolved
  the "does the pardon excuse this" question against a pardon-based
  exemption. The notice's suggested workaround for its own pardon-silence
  ("when the registrant itself disclosed the conviction on at least one
  filing, the registrant's own predicate judgment is on record") applies
  directly here.
- **source records:** `sources/jack-act-notice.md`; EHunter1-2's filing_uuids.
- **caveats:** a genuine legal ambiguity remains open in principle (could
  VALOON's counsel have reversed the predicate-offense judgment after
  October 2023?) — but no amendment or later filing reflects such a reversal;
  the burden would be on VALOON to show one, and none exists in the record.
- **verdict:** supports (closes the two most obvious innocent-explanation
  routes: pardon-based exemption, and preparer/clerical drift)

---

## Enforcement-context chapter (new, this session)

## E-GAO — GAO's 2026 audit: zero JACK Act enforcement ever, and its own methodology can't see this failure mode
- **query/script:** N/A — outside document, GAO-26-108486 (published
  2026-06-30), fetched and read directly (PDF text extraction) this session.
  Full notes: `sources/gao-jack-act-enforcement-2026.md`; saved copy
  `sources/gao-26-108486-2025-lobbying-disclosure.pdf`.
- **result:** (1) "USAO officials did not report taking any civil or criminal
  enforcement actions for LDA violations against lobbyists in 2025...
  [DOJ] has not brought any prosecutions related to nondisclosure of relevant
  crimes under the JACK Act since the law's enactment" (p.9, law effective
  2019-01-03). (2) GAO's JACK Act compliance check ran criminal-background
  checks (Accurint/CLEAR) on its general 247-lobbyist LD-2 sample and found
  zero had a disclosable conviction — i.e., it audited "does this random
  lobbyist have a conviction," never "is this known-convicted lobbyist
  disclosing correctly." (3) The USAO's only standing enforcement mechanism
  (12,391 referrals since 2016, ~46% resolved) triggers on failure to file
  LD-2/LD-203 at all — it has no described mechanism for catching a
  timely-filed report that omits one required field, which is exactly
  Hunter's and Hanson's failure mode.
- **source records:** GAO-26-108486, pp. 9, 28 (Enclosure IV). Outside data,
  disclosed; legal/context standard only — never evidence for a claim about
  Hunter or Hanson specifically.
- **caveats:** do not characterize GAO's 0-of-247 finding as "GAO reviewed
  compliance and it's fine" — it is a base-rate artifact of a random sample
  almost never containing a convicted lobbyist (this corpus's own convicted-
  lobbyist population is ~18 total), not a finding about known-convicted
  filers' behavior.
- **verdict:** supports (the systemic claim's second pillar: not just two
  gaps, but a demonstrated absence of any mechanism that would have caught
  either one)

---

## E-register — the broader convicted-lobbyist population (context, not the story)
- **query/script:** `queries.sql#q-register` (rebuilt this session against a
  scratch copy of live `gain.db`)
- **result:** 18 lobbyists total in the Senate register (`derived_convicted_lobbyist_register`).
  Two clear outliers among those with post-conviction quarterlies: HUNTER
  (0/6 disclosed) and HANSON (4/7 disclosed, 3 missing). WOHL has 1 gap of
  182 (see EHanson2's caveat — likely also a boundary-quarter effect, not
  drilled in this case). BURKMAN 471/471. Others (Smith, Juliano, Patti,
  Suplizio) show 0 post-conviction quarterlies in this rebuild — not yet
  checked for why (could be inactive, could be a filter edge case; not
  pursued, not needed for this case's claim).
- **source records:** derived_convicted_lobbyist_register (rebuildable via
  `scripts/build_derived_convicted_lobbyist_register.py`).
- **caveats:** small population (18) — do not frame this as "widespread,"
  frame it as "the outliers exist, are documented, and nothing catches them."
- **verdict:** context (bounds the claim's scope — this is not a corpus-wide
  epidemic, it's two verified outliers plus a demonstrated enforcement gap)

---

## E-corpuspct — Burkman and Wohl checked directly (no other gap filers); corpus-wide missing-disclosure rate is 1.13% of instances, 20% of lobbyists
- **query/script:** `queries.sql#q-corpuspct` (rebuilt this session against a
  fresh `derived_convicted_lobbyist_register`, all 18 rows re-verified, not
  just the pre-Hunter-drill population EHanson2 used)
- **result:** **Burkman and Wohl checked directly for their own disclosure
  gaps** (the user's question, prompted by the tribunal prep) — neither is a
  third gap case. BURKMAN: 471/471 post-conviction quarterlies disclosed, 0
  missing. WOHL: 181/182 disclosed, 1 missing (his single gap is his most
  recent quarter — a boundary effect per EHanson9's read, not drilled
  further here since he was already flagged, not a new find). Full 18-row
  register re-confirmed: only HUNTER (0/6) and HANSON (4/7) have gaps of
  more than one quarter; WOHL's lone gap is the only other deviation in the
  whole corpus. Six additional lobbyists not in EHanson2's original
  comparison population (Haddow 94/94, Avant 48/48, Stone 13/13, Ring 6/6,
  Brown 5/5, Miller 9/9) are all fully compliant — the register's `n=18`
  scope was already complete, this just confirms none of the previously
  unlisted names hide a gap.
  **Corpus-wide missing-disclosure percentage:** of the 15 lobbyists with
  ≥1 post-conviction original quarterly (887 quarterlies total across all
  15), 877 carry the disclosure and 10 don't — **1.13% of all
  post-conviction filing-instances corpus-wide lack the required
  disclosure.** At the lobbyist level: 3 of 15 (20%) have at least one gap
  quarter (Hunter, Hanson, Wohl); 12 of 15 (80%) have zero. Excluding
  Burkman/Wohl as an autofill-driven mega-filer population (EHanson9's
  contamination point — 621+239 of the corpus's 887 post-conviction
  quarterly-listings, i.e. ~72%, come from these two alone): 234
  quarterlies, 9 missing, **3.85%**.
- **source records:** `derived_convicted_lobbyist_register` (rebuildable,
  `scripts/build_derived_convicted_lobbyist_register.py`); underlying
  `senate_filing_conviction_disclosures` rows, same table EHanson1/EHunter1
  cite.
- **caveats:** this is instance-level (quarterly-report count), not
  lobbyist-count — Burkman/Wohl's filing volume (710 of 887
  post-conviction quarterly-listings between them) mechanically dominates
  the instance-level percentage; report both the instance-level (1.13%)
  and lobbyist-level (20% / 3 of 15, or 2 of 13 excl. Wohl's single-quarter
  boundary gap) figures together so the write-up doesn't imply "over 98%
  compliance" settles the systemic question — a low corpus-wide rate is
  fully consistent with the case's claim (rare + unchecked, not
  widespread + unchecked). Same base-rate-artifact logic as E-GAO/E-GAO-series:
  a low aggregate percentage in an 18-person population says nothing about
  whether the mechanism would catch a gap if one occurred, which is the
  actual claim. Wohl's single gap is treated here as instance count only —
  not drilled to a boundary-event explanation the way Hanson's was,
  since it isn't part of this case's evidenced chapters and doesn't change
  either percentage's order of magnitude if reclassified.
- **verdict:** context (answers the editor's direct question — no,
  Burkman/Wohl don't have undiscovered gaps beyond what EHanson2 already
  showed; provides the verified corpus-wide denominator for the write-up:
  ~1% of instances / ~20% of lobbyists, small-population caveat applies)

---

## E-GAO-series — the zero-JACK-Act-disclosures result holds in all 7 annual reports, not just 2026
- **query/script:** N/A — outside documents, GAO-20-449 through GAO-26-108486
  (7 reports, coverage years 2019-2025), fetched via WebFetch (GAO's CDN
  blocks direct `curl`) and text-extracted locally with `pypdf`. Full notes
  and per-year table: `sources/gao-jack-act-enforcement-2019-2024-series.md`
  (this session) + `sources/gao-jack-act-enforcement-2026.md` (prior
  session, the 2025-coverage report). Saved copies of all 7 PDFs in
  `sources/`.
- **result:** every annual report since the JACK Act's 2019 effective date
  uses the same stratified-random-sample methodology (~95-100 LD-2s per
  review period, ~160-270 individual lobbyists once all named lobbyists are
  counted) and reports the identical JACK Act finding: zero sampled
  lobbyists disclosed a conviction, every single year, 2019 through 2025
  coverage. No report describes a methodology change. One near-miss
  surfaced in GAO-22-105181 (2021 coverage): "we found information relevant
  to the JACK Act for one lobbyist, [but] could not locate any relevant
  court records" — unnamed, unresolved, not usable as evidence for any
  claim but confirms GAO's own reviewers hit the same records-access
  friction this case's Hanson docket pull did (E8, still owed).
- **source records:** GAO-20-449 p.17 (2019); GAO-21-375 p.18 (2020);
  GAO-22-105181 p.18 (2021); GAO-23-105989 p.17 (2022); GAO-24-106799 p.17
  (2023); GAO-25-107523 p.18 (2024); GAO-26-108486 p.9/Enclosure IV p.28
  (2025, already filed as E-GAO). All saved in `sources/`.
- **caveats:** same as E-GAO — this is structural/systemic context (the
  audit methodology's designed behavior over time), not evidence about
  Hunter or Hanson specifically. Do not write "GAO checked 7 years running
  and found nothing" as a compliance finding; each year's zero is the same
  base-rate artifact (a random sample of ~160-270 lobbyists drawn from a
  pool where predicate convictions are rare — this corpus's own convicted-
  lobbyist register is ~18 total) repeated seven times, not seven
  independent confirmations that the system works.
- **verdict:** supports (extends E-GAO from a single-year finding to a
  7-year pattern — the base-rate-artifact critique is not a one-off
  characteristic of the most recent report, it's how this audit has always
  worked since the law took effect)

---

## E-enforcement-map — no *external* JACK Act enforcement channel besides GAO's audit + USAO referral; but the Clerk/Secretary's own accuracy-review duty is real and unresolved
- **query/script:** N/A — bounded web search (6 queries) covering
  alternative enforcement channels: private right of action / qui tam,
  House/Senate Ethics Committee jurisdiction, and the statutory text and
  practical operation of the Secretary of the Senate / Clerk of the House's
  own review role (2 U.S.C. §1605); revised after the editor supplied a
  direct copy of CRS Report RL34377 ("Lobbying Registration and Disclosure:
  The Role of the Clerk and Secretary," updated 2021-11-29, saved
  `sources/2021-11-29_RL34377_...pdf`, extracted via `pypdf`) — corrects the
  session's earlier, web-search-only version of this evidence item.
- **result:** two findings hold as originally filed; the third is corrected.
  (1) **No private right of action / qui tam** — unchanged, no new source
  contradicts this. (2) **Ethics Committees have no jurisdiction** —
  unchanged. (3) **CORRECTED: the Clerk/Secretary's accuracy-review duty is
  not filing-existence-only — CRS describes it as a distinct, affirmative
  duty, and its actual depth is genuinely unresolved, not resolved against
  the case's favor.** RL34377 states plainly: "The Clerk of the House's
  Legislative Resource Center and the Secretary of the Senate's Office of
  Public Records have been given responsibility for **reviewing each filing
  to ensure accuracy** and for issuing notices to those who have not
  complied" (p.3) — presented as a duty separate from, and prior to, the
  60-day-notice/USAO-referral process, not folded into it. This directly
  supersedes the earlier draft of this evidence item, which read GAO's
  operational description of "referral" (a failure-to-file trigger) as
  proof that the *accuracy* review itself is also failure-to-file-only —
  that inference doesn't hold: GAO's report describes what happens *after*
  the Clerk/Secretary catch something, not the scope of the initial
  accuracy review. RL34377 gives no further detail on what "reviewing each
  filing to ensure accuracy" actually entails in practice (no description
  of whether it includes cross-checking a substantive field like the JACK
  Act conviction line against an outside record, versus a lighter
  format/completeness pass) and does not mention the JACK Act disclosure
  field specifically in connection with this review duty anywhere in the
  report (JACK Act is discussed only re: the 2019 guidance update, p.7-8).
  **This is a genuine open question, not a closed one** — neither
  "accuracy review would catch Hunter/Hanson" nor "accuracy review
  couldn't" is source-supported; only that the duty exists and its depth
  is undocumented.
- **source records:** CRS RL34377 pp.3, 7-8 (`sources/2021-11-29_RL34377_
  4dbf02d95d7468071a6d76b7fb49660f888cda57.pdf`); 2 U.S.C. §1605(a)(2)
  (quoted in RL34377 p.6, n.26); 2 U.S.C. §1606 (penalties, via Cornell
  LII); GAO-26-108486 pp.1-2, Enclosure III p.30, Enclosure VI p.40
  (`sources/gao-26-108486-2025-lobbying-disclosure.pdf`) — now cited only
  for the referral/noncompliance mechanism, not for the accuracy-review
  scope; House Ethics Committee jurisdictional history (Congress.gov CRS
  product 98-15, via web search — not saved locally, context source only).
- **caveats:** this is a legal/structural-landscape finding, not evidence
  about Hunter or Hanson specifically. **Do not claim the Clerk/Secretary's
  review would or wouldn't catch a JACK Act gap** — RL34377 establishes the
  duty exists and is distinct from the referral pipeline, but not its
  practical depth. If this needs to be load-bearing for the write-up,
  the honest framing is: "a body with an affirmative accuracy-review
  mandate exists and neither GAO's reports nor CRS's own account of that
  office's work describes it catching (or attempting to catch) a JACK Act
  disclosure gap in practice" — which is still consistent with the case's
  broader point (no *known instance* of this working) but weaker than "no
  mechanism could catch this," which is not supported.
- **verdict:** needs-more on the narrow accuracy-review sub-claim (corrects
  the prior overreach); supports on the broader claim that no *additional*
  enforcement body (private suit, Ethics Committee) exists — the
  enforcement landscape is GAO's audit + USAO referrals + this
  under-documented Clerk/Secretary accuracy-review step, and only the first
  two have any documented operation on the record.

---

## E-tribunal — Builder→skeptic→judge verdict on the combined systemic claim
- **query/script:** N/A — verification tribunal (inline, single session, not
  the billed Workflow form), run 2026-07-07 at editor request, on the
  combined claim as restructured (Hunter + Hanson + enforcement-vacuum
  chapters as one claim, per case.md's Verdict-section instruction).
- **result:** **Supported, high confidence.** Skeptic ran the full
  corpus-specific checklist (identity/namesake, House+Senate
  double-counting, multiple comparisons, base rate/denominator honesty,
  sparse-data/junk-text applicability, correlation-vs-causation
  applicability) and could not refute the core claim. Namesake check: both
  `lobbyist_id`s are sole matches for their names in `senate_lobbyists` — no
  ambiguity. Double-counting check: E-corpuspct's percentage is Senate-only
  by design; House-side rows (EHanson7, Hunter's 11 House filings) are
  corroboration, not folded into the same denominator. Multiple-comparisons
  check: the "2 gap filers" claim draws from the full closed population of
  18 self-disclosed convicted lobbyists (1,156 disclosure rows), not a hit
  mined from ~23,543 Senate lobbyists — no correction needed. Base-rate
  check (the skeptic's strongest material, using E-corpuspct built this
  session): a 1.13%-of-instances / 20%-of-lobbyists corpus-wide gap rate
  does not kill the claim — it's consistent with "rare and genuinely
  unchecked" (the case's actual framing) rather than contradicting it, and
  the same base-rate-artifact logic the case already applies to GAO's
  0-of-247 sample applies here: a low aggregate rate says nothing about
  whether the one audit mechanism is positioned to catch a gap if one
  occurs (E-GAO/E-GAO-series independently establish it is not). One
  surviving scope caveat, not a refutation: the Clerk/Secretary
  accuracy-review duty's practical depth is genuinely undocumented in any
  source found (E-enforcement-map) — carried as "needs-more" on that narrow
  sub-claim, not "no mechanism could catch this."
- **source records:** N/A (tribunal reasoning over EHunter1-4, EHanson1-9,
  E-GAO, E-GAO-series, E-enforcement-map, E-register, E-corpuspct — all
  cited above with their own source records).
- **caveats:** run inline (single session, sequential builder/skeptic/judge
  reasoning), not as the billed multi-agent Workflow form described in
  `reference/verification.md` — appropriate for this case's stakes per the
  skill's "scale to stakes" guidance, but if this needs the strongest
  possible independence guarantee before publication, a user-triggered
  `verify-finding` Workflow run remains available as a stronger version of
  the same check.
- **verdict:** supports (combined systemic claim verified; recommend close)

## E-hunter-njf — a second VALOON registration (NJF Worldwide) also lacks the disclosure

**Claim.** The register's Hunter row (E-Hunter) counts the TREX Enterprises
engagement: 1 disclosed registration + 6 undisclosed quarterlies. An
unrestricted sweep of every Senate filing naming Hunter (q-hunter-njf) finds
three more, none with the disclosure: a **second VALOON registration** for
client NJF WORLDWIDE (`6c0afe7d-e6e3-4226-bf73-9df4d595e17e`, posted
2023-12-01 — six weeks after the disclosed TREX registration) and two
termination filings (NJF `34953057-d52b-4863-a767-9c0517f433d3`, 2023 Q4;
TREX `bfb45a5c-76f1-40cd-b82d-f804f62c0509`, 2024 Q3). In total, 1 of 10
filings naming Hunter carries the JACK Act disclosure.

**Why it matters.** A registration is squarely within the Act's disclosure
requirement (the TREX registration is where VALOON *did* disclose), so the
NJF registration is a fourth-quarter-of-2023 omission that the register's
original-quarterlies scoping did not count. Terminations are noted more
cautiously (arguably in scope as termination *reports*, but not part of any
counted claim). Direction: the reported gap is understated, not overstated.

**Provenance.** Found 2026-07-15 during the submission reproduce-verification
pass (an agent re-deriving q4 ran the unrestricted variant). Query:
q-hunter-njf in queries.sql; verified against db/gain.db (built 2026-07-07).

**Verdict.** Supported; strengthens E-Hunter. The findings-report entry now
carries a one-line version. Case remains closed.
