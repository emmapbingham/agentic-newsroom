# Evidence — acu-legislative-bench

## Barr chapter (imported unchanged from barr-credit-union-cfpb-loop; relabeled EBarr1-9)

Source case: `investigations/barr-credit-union-cfpb-loop/evidence.md`. Queries
re-run from that case's `queries.sql` (copied verbatim into this case's
`queries.sql` as q-barr1..q-barr9) — re-verify before citing in this case's
own name; do not treat the import as re-verification.

## EBarr1 — The pair: $40k ACU money honoring Barr + endorsement-citing releases
- **query/script:** `queries.sql#q-barr1`
- **result:** deduped FECA honoring Barr from CUNA/ACU registrant: $40,000;
  3 press releases citing ACU/CUNA (2023-12-15, 2025-01-23, 2025-05-03).
- **source records:** see barr-credit-union-cfpb-loop/evidence.md E1.
- **caveats:** ACU exists as two alias entities pre-merger; E1 total is one
  entity — NAFCU-legacy registrant adds $6,000 (EBarr3).
- **verdict:** supports

## EBarr2 — The dated money timeline, incl. the Senate-committee pivot
- **query/script:** `queries.sql#q-barr2`
- **result:** see barr-credit-union-cfpb-loop/evidence.md E2 for the full
  dated timeline (2022-2025, six FECA items, $5k each).
- **verdict:** supports (pending FEC redesignation-date verification, still owed)

## EBarr3 — Second credit-union registrant adds $6k
- **query/script:** `queries.sql#q-barr3`
- **result:** NAFCU-legacy registrant: $6,000 honoring Barr. Combined
  credit-union total: $46,000.
- **verdict:** supports (scale context)

## EBarr4 — ACU honoree base rate: Barr is top-tier (rank 5 of 527), not median
- **query/script:** `queries.sql#q-barr4` + `q-barr4b`/`q-barr4c`
- **result:** ACU's deduped FECA footprint honors 527 members, $6,208,500
  total, median ~$10,000. Barr's $40,000 = rank 5 of 527 (top ~1%). ACU
  spreads leadership money bipartisanly (top 4 are Dem leadership).
- **verdict:** supports (scale) — top-tier, not an outlier relative to how
  ACU treats committee leadership generally.

## EBarr5 — full pivot stack: ACU is not day-one, not the biggest donor
- **query/script:** `queries.sql#q-barr5` + `q-barr5b`
- **result:** 419 registrants honor Barr; ACU ranks ~11th ($40k; ten gave
  more, led by Carlyle $52.5k, ABA $47.5k). Five registrants reported to
  "ANDY BARR FOR SENATE, INC." before ACU's 2025-02-20 (earliest: Cresco Labs
  2025-01-31).
- **verdict:** weakens the Barr-specific timing hook; supports only the
  broader "financial industry and Barr" framing, not ACU uniqueness.

## EBarr6 — ACU's Senate lobbying names both Barr bills by number
- **query/script:** `queries.sql#q-barr6` + `q-barr6b`
- **result:** 2025Q1-2026Q1 ACU Senate filings state verbatim: "Support
  Taking Account of Bureaucrats Spending Act (H.R. 654) Support Rectifying
  UDAAP Act (H.R. 1652)" — both Barr bills, by title and number, every
  quarter since introduction.
- **caveats:** literal "TABS" acronym never appears — match on bill
  title/number, not acronym string.
- **verdict:** supports (strong) — the pattern this case generalizes: named-
  bill support text in ACU's own sworn Senate filings.

## EBarr7 — endorsement quotes: ACU named in 2 of 3 releases, one voice among 4-5
- **query/script:** `queries.sql#q-barr7`
- **result:** 2025-01-23 and 2025-05-03 releases quote "America's Credit
  Unions" by name (Jim Nussle); 2023-12-15 quotes CUNA+NAFCU (pre-merger).
  In all three, ACU/predecessors are one of 4-5 trade-group endorsers
  (also ABA, CBA, ICBA, AFSA, ACA).
- **verdict:** supports (ACU quoted by name) with a material caveat: the
  endorsement-quote practice is industry-wide boilerplate, not ACU-specific
  — this caveat must be re-tested per bench member, not assumed to transfer.

## EBarr8 — the pivot item verified against the source LD-203 filing
- **query/script:** `queries.sql#q-barr8` + outside LDA API fetch
- **result:** LDA API JSON for filing 6acc01c1-... confirms the 2025-02-20
  $5,000 "ANDY BARR FOR SENATE, INC." row verbatim, matching ingest exactly.
- **verdict:** supports — ingest accuracy confirmed at the source.

## EBarr9 — FEC: "Andy Barr for Senate, Inc." is a redesignated pre-existing committee
- **query/script:** outside fetch, FEC API (context only, disclosed)
- **result:** committee C00467571 is Barr's original 2009 House committee,
  redesignated to Senate for 2026; active under the Senate name by at least
  2025-01-31 per LD-203 corroboration (EBarr5).
- **verdict:** supports (2025-02-20 date genuine) but confirms the committee
  predated McConnell's announcement — reinforces EBarr5's weakening of the
  timing hook.

---

## Bench-wide claim (unverified — this case's actual new work starts here)

## E-scout — the aggregate screen row (NOT yet a verified claim)
- **query/script:** screen run 36,
  `investigations/screens/client-mention-honoree-triangle/screen.sql`
- **result:** 10 ACU member-pairs surfaced in one screen run; skeptic's
  overnight pass (transcript, not re-derived here) named ≥5 as carrying the
  full triple: Barr, Cramer, Tim Scott, Fitzgerald, Budd, plus Emmer and
  Britt.
- **source records:** none independently pulled yet for members other than
  Barr — this is a scout number from the promoted lead, unverified as a set.
- **caveats:** **do not cite this number in any durable document.** Each
  member needs an EBarr6-equivalent (named-bill lobbying text) and an
  EBarr1/EBarr7-equivalent (honoree money + press quote) pulled
  independently before the bench claim can be described as verified.
- **verdict:** needs-follow-up — this is the case's open work, not a finding.

## E0 — screen re-derivation caught a display bug (10x underread), and corrected the base table
- **query/script:** `queries.sql#q1` (screen run 36, ACU/entity 644 only, CSV mode)
- **result:** the first read of screen run 36 this session used `sqlite3 -mode column -width ...`,
  which truncated/wrapped the `feca_usd` column and silently read every dollar figure ~10x low
  (e.g. Scott showed $2,750; true deduped value is $27,500). Re-run in `-mode csv` and
  cross-checked against Barr's already-verified $40,000 (EBarr1) — matches exactly, confirming
  the underlying query/dedup logic was always correct; the error was a CLI display artifact only.
  **Corrected top-line table (all 10 ACU pairs, deduped FECA $ + n_contribs + n_mentions):**
  | member | party/state | feca_usd | n_contribs | n_mentions |
  |---|---|---|---|---|
  | Andy Barr | R-KY | $40,000 | 8 | 3 |
  | Katie Britt | R-AL | $33,500 | 8 | 2 |
  | Tom Emmer | R-MN | $30,000 | 6 | 2 |
  | Kevin Cramer | R-ND | $27,500 | 7 | 2 |
  | Tim Scott | R-SC | $27,500 | 6 | 2 |
  | Joyce Beatty | D-OH | $25,000 | 8 | 2 |
  | Scott Fitzgerald | R-WI | $24,000 | 9 | 6 |
  | Vicente Gonzalez | D-TX | $22,000 | 6 | 2 |
  | Juan Vargas | D-CA | $21,000 | 7 | 4 |
  | Ted Budd | R-NC | $20,000 | 4 | 2 |
- **source records:** all 10 rows independently re-derived from `senate_contribution_items` /
  `senate_contribution_filings` / `honoree_member_map` (confidence>=0.9) / `derived_client_press_mentions`,
  registrant_id=11322 (the one ACU registrant that resolves via exact-normalized-name match;
  entity 645's alias variant does not match any registrant — documented alias-index bound, not a bug).
- **caveat for any future session/report:** always use `-mode csv` or `-mode line` for money
  figures from this DB via the sqlite3 CLI; `-mode column` with fixed `.width` silently truncates.
- **verdict:** supports — corrects and supersedes the scout table's dollar figures in `case.md`/E-scout;
  member roster (10 pairs) and mention counts were already accurate, only $ was wrong.
- **addendum (2026-07-09):** this table reflects the original screen-36 output (10 pairs at
  `n_mentions>=2`) as a historical record — left unchanged here. The bench itself is now 11 members;
  Gary Peters was added per E13/E14 (editor's call to drop the `>=2` construction threshold once a
  member's full triple is independently verified). Peters: $20,000, 4 contribs, 1 mention (ties Budd
  for lowest $; lowest mention count on the bench). See E14 for the addition writeup.

## E1 — Kevin Cramer: full triple confirmed
- **query/script:** `queries.sql#q-cramer1` (money), `#q-cramer2` (lobbying text), press pulled by URL
- **result:**
  - **Money:** $27,500 deduped FECA honoring Cramer from ACU (registrant 11322), 7 contributions,
    2022-07-18 to 2025-12-15, split CRAMER FOR SENATE + BADLANDS PAC.
  - **Bill:** Protecting Access to Credit for Small Businesses Act (SBA 7(a) direct-lending ban),
    cosponsored by Cramer alongside Scott. ACU's Senate lobbying names it by number every quarter
    it appears: **S. 3992** (2024 filings, 118th Congress) → **S. 2486** (2025 Q3–2026 Q1 filings,
    119th Congress reintroduction) — renumbering across Congresses is normal, not a discrepancy.
  - **Press:** 2 mentions, both 2024 (2024-03-20, 2024-04-09). Neither release carries a *named*
    ACU quote — both list "America's Credit Unions" only inside a multi-org "organizations
    supporting" roster (alongside ABA/ICBA/CBA/BPI in one, ABA/CBA/ICBA/BPI/ATR/CEI/Chamber in
    the other). Cramer himself is quoted; ACU is not.
- **source records:** filing_uuids `4774a561-...`, `93624f0a-...`, `84a0158c-...`, `c19daac7-...`
  (contributions); lobbying filing_uuids include `8ba5c3c0-...` (2024Q1, S.3992 text),
  `93c9dba6-...` (2026Q1, S.2486 text); press urls: cramer.senate.gov/.../legislation-protects-lenders...
  and .../senators-introduce-resolution-of-disapproval-on-cfpb-credit-card-late-penalty-final-rule.
- **verdict:** supports — money + named-bill lobbying confirmed; press leg present but roster-only,
  not a named quote (weaker than Barr's EBarr7, which had 2 of 3 named).

## E2 — Tim Scott: full triple confirmed, with one named quote
- **query/script:** `queries.sql#q-scott1` (money), `#q-scott2` (lobbying text), press pulled by URL
- **result:**
  - **Money:** $27,500 deduped FECA honoring Scott from ACU, 6 contributions, 2022-09-21 to
    2025-12-30, split TIM SCOTT FOR SENATE / TIM SCOTT FOR AMERICA / TOMORROW IS MEANINGFUL PAC.
  - **Bill:** same Protecting Access to Credit for Small Businesses Act as Cramer (Scott is the
    lead sponsor). Same S.3992 -> S.2486 renumbering pattern in ACU's Senate lobbying text.
  - **Press:** 2 mentions (2024-03-20, 2025-07-29). The 2025-07-29 release (Scott's own
    reintroduction) carries a **named quote**: "...said Jim Nussle, President and CEO, America's
    Credit Unions." The 2024-03-20 release lists ACU only in a roster (with ABA/CBA/ICBA/BPI/SC
    Bankers).
- **source records:** filing_uuids `4774a561-...`, `d7cd0f30-...`, `84a0158c-...`, `c19daac7-...`;
  lobbying filing_uuid `93c9dba6-...` (S.2486 text, 2026Q1); press urls: scott.senate.gov/.../sens-scott-kennedy-introduce-bill-to-stop-biden-admins-big-government-lending-scheme
  and .../senator-scott-colleagues-introduce-bill-to-stop-government-overreach-in-small-business-lending.
- **verdict:** supports (strongest of the two — has a named quote, matching Barr's pattern).

## E3 — Katie Britt: partial — money + roster mentions, one bill unconfirmed in lobbying text
- **query/script:** money as in E0 table; press pulled by URL; lobbying searched for "Community Bank Relief"
- **result:** $33,500 deduped FECA, 8 contribs, 2022-03-10 to 2025-12-30. Two 2025-2026 press
  mentions: 2025-10-22 (illicit-finance-law modernization bill, co-led w/ Scott/Kennedy — ACU named
  in a 3-org roster, no quote) and 2026-02-13 ("Community Bank Relief Act" w/ Ted Cruz — ACU **named
  quote**, Scott Simpson, President & CEO). ACU's Senate lobbying names "Community Bank Relief"
  once, in the 2026 Q1 filing only (the quarter the bill was introduced) — too recent to show a
  multi-quarter pattern yet, unlike Barr/Cramer/Scott's bills.
- **source records:** britt.senate.gov press urls (2025-10-22, 2026-02-13); lobbying filing_uuid
  `93c9dba6-...` (2026Q1).
- **verdict:** supports, weaker — triple present but the lobbying leg has only one data point so
  far (bill is brand new); the 2025-10-22 release's underlying bill was not separately checked
  against lobbying text (no clean distinctive title fragment identified this session).

## E4 — Tom Emmer: full triple confirmed, with named quote
- **query/script:** money as in E0 table; lobbying searched "Anti-CBDC Surveillance State"; press by URL
- **result:** $30,000 deduped FECA, 6 contribs, 2022-02-10 to 2025-02-28. 2 press mentions
  (2025-03-06, 2025-07-17), both about the Anti-CBDC Surveillance State Act (Emmer's flagship
  bill). The 2025-03-06 release carries a **named quote**: "...said Carrie Hunt, Chief Advocacy
  Officer of America's Credit Unions." ACU's Senate lobbying names "Anti-CBDC Surveillance State"
  in 5 filings, 2025 Q1 through 2026 Q1.
- **source records:** emmer.house.gov press urls (2025-03-06 stakeholder-support release,
  2025-07-17 House-passage release); lobbying filings matching 2025Q1-2026Q1 (5 filing_uuids,
  query not individually cited by uuid this pass — re-derive via q-emmer2 if needed for report).
- **verdict:** supports — named quote + consistent multi-quarter lobbying text, same strength as
  Scott/Barr.

## E5 — Scott Fitzgerald: full triple confirmed (highest mention count of the bench)
- **query/script:** money as in E0 table; lobbying searched 4 bill-title fragments; press by URL
- **result:** $24,000 deduped FECA, 9 contribs, 2022-03-17 to 2025-02-28 — but 6 press mentions,
  the densest of any bench member (more than Barr's 3). Fitzgerald champions at least 3-4 distinct
  bills over the period (Making the CFPB Accountable to Small Business(es) Act, Credit Union Board
  Modernization Act as cosponsor, HUMPS Act, Expanding Access to Lending Options Act). ACU's
  lobbying text confirms 3 of these by title: "CFPB Accountable" (7 filings, 2022Q4-2026Q1),
  "Uncertain Methods and Practices" (the HUMPS Act's un-acronymed title, 4 filings, 2025Q4-2026Q1
  — literal "HUMPS" acronym never appears, same caveat as Barr's TABS), "Expanding Access to
  Lending Options" (9 filings, 2024Q1-2026Q1). Named quote confirmed in 2024-01-10 release (Jim
  Nussle, re: a different bill — the Vargas/Huizenga Credit Union Board Modernization Act, which
  Fitzgerald co-sponsors); other releases are supporter-roster only or no ACU mention in the quote
  block.
- **source records:** fitzgerald.house.gov press urls (6, listed in queries.sql); lobbying
  filing_uuids for the 3 matched bills (counts above; individual uuids in queries.sql#q-fitz2).
- **verdict:** supports (strong) — most bills, most mentions, most independently-confirmed lobbying
  matches of the non-Barr bench. Best candidate for a second worked example alongside Barr/Scott if
  the case narrows to 2-3 profiled members.

## E6 — Ted Budd: partial — shared-bill triple confirmed, second bill not isolable
- **query/script:** money as in E0 table; lobbying re-uses S.2486/S.3992 match from E1/E2; press by URL
- **result:** $20,000 deduped FECA, 4 contribs, 2022-09-28 to 2025-12-30 (lowest $ and n_contribs
  of the bench). 2 press mentions: 2025-07-31 (Budd is a named co-sponsor of the same Scott/Cramer
  SBA bill — ACU listed in roster, no quote) and 2024-06-18 (a Fed debit-interchange pause bill,
  Budd's own — search terms "debit"/"Federal Reserve"/"interchange" all too generic against ACU's
  boilerplate issue-code text to isolate a clean match; not confirmed either way this session).
  The SBA-bill leg of the triple is confirmed via the same S.2486/S.3992 text already verified for
  Scott/Cramer (Budd is a listed cosponsor in both the bill text and ACU's supporting-orgs roster).
- **source records:** budd.senate.gov press urls (2024-06-18, 2025-07-31); lobbying filing_uuid
  `93c9dba6-...` (shared with E1/E2).
- **verdict:** supports, weakest of the confirmed six — money is the bench's smallest, no named
  quote, and one of two bills couldn't be isolated in lobbying text (search-term limitation, not a
  confirmed miss — flag as "unconfirmed," not "absent").

## E7 — Joyce Beatty: originally read as a triple break; CORRECTED 2026-07-09 — a second bill (H.R. 3709) closes the lobbying gap

- **query/script:** money as in E0 table; lobbying searched "Fair Hiring", "5911", "justice-involved"
  (all zero hits, also checked NAFCU-legacy registrant, zero); press by URL
- **result (original, H.R. 5911 only):** $25,000 deduped FECA, 8 contribs, 2022-03-10 to 2025-12-15 —
  strong money leg (5th highest of the bench). 2022-12-23 release: Beatty's Fair Hiring in Banking Act
  (H.R. 5911, justice-involved-individuals employment bill) — ACU cited only via legacy name "CUNA"
  in a 4-org roster (no quote); **zero matches** in ACU's Senate lobbying descriptions for "Fair
  Hiring", the bill number, or plausible paraphrases, checked against both the merged-entity
  registrant (11322) and the NAFCU-legacy registrant. This zero-match result for H.R. 5911
  specifically still stands — re-confirmed, not overturned by the correction below.
- **CORRECTION (2026-07-09):** editor identified a second Beatty bill this case had missed: **H.R.
  3709, "Advancing the Mentor-Protégé Program for Small Financial Institutions Act"** (119th
  Congress, introduced 2025-06-04, Beatty as sole sponsor) — the actual subject of Beatty's
  2025-06-05 press release (one day after introduction, matching the bench's dominant same-day/
  next-day sub-pattern), which this case had on file but had never matched to a bill because E7 was
  scoped to H.R. 5911 only. The release's full text (`press_releases.text`, not just `title`/`url`)
  carries FIVE organizational endorsement quotes (ICBA, ABA, National Bankers Association, and —
  the one that matters here — **"America's Credit Unions applauds Rep. Joyce Beatty's efforts to
  promote programs that support minority depository institution (MDI) credit unions..." (Jim
  Nussle, ACU President/CEO)** — a genuine named quote, not a roster mention. Checked ACU's Senate
  lobbying text for this bill: **1 match** — the 2026 Q1 filing (posted 2026-04-14) states
  verbatim "Support Advancing the Mentor-Protege Program for Small Financial Institutions Act
  (H.R. 3709)." Confirmed via Congress.gov (119th HR.3709, Beatty sole sponsor, introduced
  2025-06-04) — live API call, not assumed.
- **source records:** beatty.house.gov press urls (2022-12-23, 2025-06-05); negative lobbying
  search for H.R.5911 logged in `queries.sql#q-beatty2`; H.R.3709 lobbying match and Congress.gov
  confirmation logged in `queries.sql#q-e7-correction`.
- **caveats:** the press release's own text says Beatty "reintroduced" H.R.3709, implying an
  earlier-Congress predecessor bill with a possibly different number — searched Beatty's full
  sponsored-legislation history (all bills, all Congresses) for any "Mentor-Protégé"-titled bill
  and found none besides HR.3709 itself; either the predecessor used a different title (not
  resolved) or "reintroduced" refers to the underlying Treasury program concept rather than a
  specific prior bill of this name. Not chased further — doesn't affect the core correction (money +
  named press quote + lobbying-text match all present for H.R.3709 specifically).
- **verdict:** REVISES E7. Beatty is **no longer the bench's one clean lobbying-absence case** —
  she has TWO tracked bills: H.R. 5911 (zero lobbying match, still a genuine negative result on
  that specific bill) and H.R. 3709 (money + named press quote + 1 lobbying-text match, a real
  though thin triple). The correct characterization is a **split record across two bills**, not a
  uniform break: one bill supported in ACU's sworn filings, one not, both real and both press-
  covered. This changes E11 item 4, E12/E13/E14/E15's characterizations of Beatty as the bench's
  sole "lobbying-absent" example — see those entries' 2026-07-09 addenda below. Does not fully
  restore Beatty to "clean full-triple" status either: H.R.5911's negative result is unaffected and
  should still be cited precisely (money+press only, no lobbying text, for THAT bill specifically),
  while H.R.3709 is a new, thin (1-filing) but real triple.

## E8 — Juan Vargas: full triple confirmed, named quote, most-lobbied bill in the bench
- **query/script:** money as in E0 table; lobbying "Credit Union Board Modernization" (22 filings,
  the most of any bill checked); press by URL
- **result:** $21,000 deduped FECA, 7 contribs, 2022-02-24 to 2025-12-15. 4 press mentions (densest
  after Fitzgerald) — all four about the same bill, the Credit Union Board Modernization Act
  (H.R. 582, cosponsored w/ Huizenga), introduced/passed-House/reintroduced across 2023 and 2025.
  ACU's Senate lobbying names this bill in 22 filings spanning 2022 Q1 through 2026 Q1 — the
  longest and most consistent run of any bill checked in this case. Named quote present in the
  2024-01-10 release (Jim Nussle, same quote block cited in Fitzgerald's E5 — a shared release).
- **source records:** vargas.house.gov press urls (4, in queries.sql#q-vargas1); 22 lobbying
  filing_uuids (queries.sql#q-vargas2, not enumerated individually here).
- **verdict:** supports (strong) — best-attested lobbying leg in the whole bench by filing count;
  a Democrat, so this is the first confirmed cross-party replication, refuting a
  Republican-only reading of E7's Beatty miss.

## E9 — Vicente Gonzalez: full triple confirmed
- **query/script:** money as in E0 table; lobbying "Veterans Member" (21 filings); press by URL
- **result:** $22,000 deduped FECA, 6 contribs, 2022-06-27 to 2025-12-15. 2 press mentions
  (2025-01-16, 2026-02-24). The 2025-01-16 release (Veterans Members Business Loans Act,
  w/ Fitzpatrick/Hirono/Sullivan) carries a **named quote**: "At America's Credit Unions, we
  support Senators...and Representatives...for their reintroduction..." ACU's Senate lobbying
  names "Veterans Member[s] Business Loan[s]" in 21 filings, 2022 Q1 through 2026 Q1. The
  2026-02-24 release (FHLB access bill) also carries a named ACU quote but that bill's lobbying
  text was not separately isolated this session.
- **source records:** gonzalez.house.gov press urls (2025-01-16, 2026-02-24); lobbying filing
  count/date-range as above (uuids in queries.sql#q-gonzalez2).
- **verdict:** supports (strong) — second confirmed Democrat, named quote, long consistent
  lobbying run. Combined with Vargas (E8), refutes a partisan-only reading of the bench.

## Bench replication — summary after E1-E9

Of the 9 members drilled this session (all except Barr, already verified):
- **7 of 9 fully confirmed** (money + named-bill lobbying text + press mention, at least roster-
  level): Cramer, Scott, Britt (weak lobbying leg — 1 data point), Emmer, Fitzgerald, Budd (1 of 2
  bills unconfirmed by search-term limits, not a negative), Vargas, Gonzalez.
- **1 of 9 broke the triple**: Beatty — money and press (with named quote) present, but zero
  lobbying-text match for her specific bill despite an unambiguous, specific bill title/number to
  search on. This is evidence the pattern is NOT universal across every bill a bench member
  champions — ACU picks which member bills to name in sworn filings, and Beatty's justice-reform
  bill wasn't one of them even though ACU publicly endorsed it by name in press.
- **Named quotes** (not just roster mentions) confirmed for: Scott, Britt (2nd bill), Emmer,
  Fitzgerald, Vargas, Gonzalez (both bills) — i.e., most of the bench, not just Barr. Roster-only:
  Cramer (both), Budd (SBA bill), Britt (1st bill), Beatty (both).
- **Cross-party:** the two Democrats drilled (Vargas, Gonzalez) both show strong triples with named
  quotes — the pattern is not Republican-specific, though Beatty (also a Democrat) is the one
  break. n=3 Democrats is too small to call a party pattern either way.
- **Not yet independently drilled:** none remaining from the original scout list — Barr (EBarr1-9)
  plus these 9 covers all 10 screen-36 pairs.

<!-- Individual per-member queries logged in queries.sql as q-cramer*, q-scott*, q-britt*,
     q-emmer*, q-fitz*, q-budd*, q-beatty*, q-vargas*, q-gonzalez*. -->

## E10 — the killing blow: ACU's bench ranks 22nd of 192 clients in the same screen (THIS IS THE CASE'S OWN boring_explanation, confirmed)
- **query/script:** `queries.sql#q-rank1` (full un-filtered screen-36 population, ranked by
  distinct-member count per client)
- **result:** the client-mention-honoree-triangle screen (same screen that surfaced ACU) returns
  **1,008 (client, member) pairs across 192 distinct clients and 280 distinct members** at the
  n_mentions>=2 threshold. Ranking clients by how many distinct members they show the identical
  money+lobbying+mention pattern with:
  | rank | client | n_members | total feca_usd |
  |---|---|---|---|
  | 1 | VISA, INC. | 84 | $914,000 |
  | 2 | THE GOLDMAN SACHS GROUP, INC. | 59 | $172,750 |
  | 3 | LEAGUE OF CONSERVATION VOTERS | 44 | $241,961 |
  | 4 | AMAZON.COM SERVICES, INC. | 39 | $396,150 |
  | 5 | NATIONAL SHOOTING SPORTS FOUNDATION, INC. | 34 | $272,787 |
  | 6 | EVERYTOWN FOR GUN SAFETY ACTION FUND | 31 | $54,000 |
  | 7 | INTEL CORPORATION | 28 | $239,500 |
  | 8 | BOEING COMPANY | 25 | $366,950 |
  | 9 | MICROSOFT CORPORATION | 24 | $369,800 |
  | ... | ... | ... | ... |
  | **22** | **CREDIT UNION NATIONAL ASSOCIATION (ACU)** | **10** | **$270,500** |

  ACU's 10-member "bench" is **8.4x smaller than Visa's** (84 members), and ACU sits outside the
  top 20 of 192 clients screened — below-median-to-unremarkable, not an outlier. Separately: Barr
  himself (this case's original worked exemplar) shows the identical triple with a *second*,
  unrelated client — National Thoroughbred Racing Association ($30,000, 6 mentions, vs. ACU's
  $40,000/3 mentions) — meaning even Barr's own "bench membership" isn't ACU-exclusive, weakening
  the framing further.
- **source records:** full screen-36 query, un-filtered by client name, in `queries.sql#q-rank1`;
  re-derivable directly against `derived_client_alias_index` / `senate_contribution_items` /
  `derived_client_press_mentions` / `honoree_member_map` (confidence>=0.9) — no new derived table
  needed, this is the same screen the case was seeded from, just not filtered to ACU.
- **caveats:** this ranks by *count of members*, not by density/explicitness per member (ACU's
  bills are named by number in sworn lobbying text more often than some competitors' might be —
  not checked for Visa/Goldman/etc., and would require the same per-member drilldown this case
  just ran on ACU, at 8x the scale). The screen's own selection bound still applies (mention-
  pipeline-selected, in-house filers only) — Visa's true rank could be even higher or lower under
  a lobbying+LD203-only screen. This doesn't rule out a *Visa* story; it rules out an *ACU* story
  built on "bench at trade-association scale" as the hook.
- **verdict:** REFUTES the case's central newsworthiness claim. This is the case's own
  `boring_explanation` ("this is just what every large trade association/company does — committee
  government working as designed") confirmed directly, using the same screen and the same
  methodology the case itself validated — no separate ABA/ICBA/MBA build was even needed, because
  the mention pipeline already contains dozens of larger, denser benches than ACU's.

## E11 — the say/pay/lobby/bill typology: three quantified components, not one uniform triple

Superseded once already (2026-07-09 first pass, weaker — see log.md), then corrected same day
using quantitative work recovered from an earlier session (2026-07-08) that
had produced a sharper version of
this typology before the case was killed. This entry replaces the earlier pass with the properly
quantified one.

- **query/script:** three `python3` scripts run directly against the four `derived/bench_*.csv`
  files (not yet promoted to `analysis/` as standalone files — recovered from the prior session's
  transcript and re-run to confirm; see `queries.sql#q-e11a/b/c`). (a) nearest-event gap calculator
  (press→nearest bill, press→nearest contribution, per press release); (b) before/after-first-bill
  contribution split, bucketed 0-30d / 30-180d / >180d after, with dollar totals; (c) a
  45-day-responsiveness test — for every contribution, does *any* bill-intro or press event fall in
  the 45 days immediately before it (a "responsive" payment) vs. sitting in the gaps between events;
  plus a raw gap-length audit between consecutive contributions per member.
- **result:** the "triple" (money + lobbying-text + press) is not one behavior but **three
  components with genuinely different temporal signatures**:

  **1. Bill→press is near-tautological, not a finding.** 8 of 10 members show a press release
  same-day-to-a-few-days after a bill introduction (Cramer 0d, Scott 0d/1d, Fitzgerald most same-day
  across 5 bills, Vargas 0d/1d, Emmer's first 0d, Gonzalez's first 0d, Britt's second 2d) — this is
  "introduce a bill, announce it," a sanity check that the corpus captures what it should, not an
  editorial finding on its own.

  **2. Money's relationship to bill introduction, quantified per member (n=10):**
  | member | $ before first bill | $ after (0-30d) | $ after (30-180d) | $ after (>180d) | % after |
  |---|---|---|---|---|---|
  | Barr | $5,000 | $5,000 | $0 | $30,000 | 88% |
  | Britt | **$32,500** | $0 | **$1,000** | $0 | **3%** |
  | Emmer | $10,000 | $0 | $15,000 | $5,000 | 67% |
  | Cramer | $17,500 | $0 | $0 | $10,000 | 36% |
  | Scott | $17,500 | $0 | $0 | $10,000 | 36% |
  | Beatty | $0 | $0 | $2,500 | $22,500 | 100% |
  | Fitzgerald | $6,500 | $0 | $0 | $17,500 | 73% |
  | Gonzalez | $7,500 | $0 | $7,000 | $7,500 | 66% |
  | Vargas | $2,500 | $2,500 | $0 | $16,000 | 88% |
  | Budd | $15,000 | $0 | $0 | $5,000 | 25% |

  Most members' money lands mostly *after* first bill introduction (Barr 88%, Beatty 100%, Vargas
  88%), which superficially reads as "pay follows the bill." The 45-day responsiveness test shows
  this is misleading:

  | member | n contributions | responsive (within 45d after any bill/press event) |
  |---|---|---|
  | Barr | 8 | 3 (38%) |
  | Britt | 8 | 0 (0%) |
  | Emmer | 6 | 0 (0%) |
  | Cramer | 7 | 0 (0%) |
  | Scott | 6 | 0 (0%) |
  | Beatty | 8 | 2 (25%) |
  | Fitzgerald | 9 | 1 (11%) |
  | Gonzalez | 6 | 0 (0%) |
  | Vargas | 7 | 1 (14%) |
  | Budd | 4 | 0 (0%) |

  Even the members whose dollars are 88-100% chronologically-after their first bill show almost no
  clustering in the 45 days immediately following a specific bill/press event (0-38%, median 0%).
  Gaps between a member's consecutive contributions are irregular — 0 to 740 days, no fixed cadence
  (e.g. Budd: 251, 198, 740; Emmer: 0, 627, 0, 122, 365) — consistent with routine, drip-funded
  PAC-cycle giving that predates and outlasts any single bill, not payment triggered by legislative
  activity. **"Money follows the bill" is not supported by the sequencing for 9 of 10 members** —
  money is a standing relationship running on its own cadence.

  **3. Britt is the one genuine, quantified outlier — Type 2, not "late-starting."** $32,500 of her
  $33,500 total (97%) predates her *earliest tracked bill's* introduction; using her flagship bill
  specifically (Community Bank Relief Act, E3, 2026-02-11) every dollar predates it. 0% of her money
  is "responsive" (within 45 days after any bill/press event). This inverts the case's own framing:
  for Britt specifically the visible sequence is closer to *"ACU pays, then a bill eventually shows
  up to point to"* than *"ACU pays because of the bill."* (Corrects the first-pass 2026-07-09
  write-up, which mischaracterized Britt as "late-starting-then-continuous" lobbying-text coverage —
  that's a true but secondary observation about the *lobbying* leg; the load-bearing point about
  Britt is the money-timing inversion, not the lobbying-text gap. Also note: the earlier-session
  transcript this typology was recovered from computed $33,500/0%/0% using only Britt's flagship
  bill, before the 2026-07-08 press-hook-completeness check added her second bill, STREAMLINE Act,
  introduced 2025-10-20 — that check landed a $1,000 contribution in the 30-180d-after bucket
  against the *earlier* of her two bills. Both framings support the same conclusion; cite the
  flagship-bill version [$33,500/0%/0%] as primary since STREAMLINE is a `press-hook-check`-tier
  bill, not yet confirmed in ACU's lobbying text the way Community Bank Relief Act is.)

  **4. Lobbying-text continuity (from the first-pass 2026-07-09 typology, retained — this part
  wasn't in the recovered transcript and still holds as a separate, valid axis):** continuous
  quarterly coverage with no gaps (Vargas 22 filings — starting ~5 months *before* the bill's formal
  introduction, i.e. ACU lobbying the policy pre-bill-number; Gonzalez 21, same pre-introduction
  pattern; Fitzgerald 20 across 3 bills; Cramer/Scott/Budd 11 each on the shared S.3992/S.2486;
  Barr 10) vs. late-starting-then-continuous (Emmer, lobbying text starts ~18 months after
  introduction then runs every quarter) vs. genuinely absent (Beatty — zero matches across the
  bill's entire life, introduction through 2022 NDAA enactment; already documented as E7).

  **5. Beatty recontextualized by date, not just by absence.** Her bill (Fair Hiring in Banking Act)
  was already enacted into law in December 2022; ACU's press quote citing her didn't appear until
  2025-06-05 — *after* the bill was already law, not before or during its live legislative window.
  Read against Type 1 above (100% of her money lands after first-bill, standard background-giving
  cadence, 25% "responsive"), the fair characterization is that ACU is not claiming credit on a bill
  that had already passed, not that the bill was "too new" for lobbying text to catch up — the
  entire multi-year window was available and unused.

  **ADDENDUM (2026-07-09) — item 4's "genuinely absent" Beatty case is CORRECTED, see E7's revision.**
  Editor identified a second Beatty bill this case had missed: H.R. 3709 ("Advancing the
  Mentor-Protégé Program for Small Financial Institutions Act," 119th Congress, introduced
  2025-06-04) — the actual subject of her 2025-06-05 release, which carries a genuine named ACU
  quote (Jim Nussle), and which ACU's lobbying text DOES name (1 filing, 2026 Q1). Beatty is not
  a clean "absent" case — she has a split record: H.R. 5911 (zero lobbying match, negative result
  stands) and H.R. 3709 (money + named quote + 1 lobbying match, a real though thin triple). This
  interestingly SHARPENS rather than weakens item 5's point above: ACU's endorsement behavior is
  bill-specific, not member-specific — it named-quote-endorsed Beatty's small-institution bill
  while ignoring her justice-reform bill entirely, in the same member, same press cadence, same
  money relationship. The "genuinely absent" lobbying-continuity category (item 4) now has ZERO
  clean examples in the bench — every member has at least one bill with a lobbying-text match.
  Full detail: evidence.md E7 (revised).
- **source records:** all four `derived/bench_*.csv` files, cross-joined on `member`; underlying
  evidence refs are E1-E9/EBarr1-9/E10 as already cited per member — this entry adds no new primary
  source records, it re-characterizes existing ones by sequence and adds two new quantitative tests
  (before/after-bill split, 45-day responsiveness) not run in any prior evidence block.
- **caveats:** n=10 members, several sharing 1-2 bills (Cramer/Scott/Budd share S.3992/S.2486). The
  45-day-responsiveness threshold is a reasonable but somewhat arbitrary choice (not tested at 30d
  or 60d for sensitivity — worth a quick robustness check before this goes in the report). The
  lobbying-continuity 3-way split (item 4) has only 1 example of "absent" (Beatty) and 1 of
  "late-starting" (Emmer; Britt is reclassified above as primarily a money-timing outlier, not a
  lobbying-continuity case) — descriptive of this bench, not statistically validated at larger n.
- **verdict:** REFINES (does not overturn) the 2026-07-08 kill's scope (ACU is still not
  distinctive/newsworthy at bench *scale*, per E10) but materially strengthens the case's value as
  the **findings-report demo of the say/pay/lobby/bill methodology** — editor's 2026-07-09 call to
  keep the case open for exactly this purpose. The typology is now genuinely quantified (not just
  descriptive): bill→press is a tautology and should be labeled as such, not sold as a finding;
  money is a standing relationship independent of legislative timing for 9 of 10 members (median 0%
  responsive within 45 days); Britt is a real, citable, quantified outlier (100%/0%/0%) worth
  naming specifically in the writeup; lobbying-text continuity is a separate three-way axis, with
  Vargas/Gonzalez's pre-introduction lobbying as its most interesting single data point. This frame
  (tautology called out + money-independence quantified + one named outlier + lobbying-continuity
  axis) is the reusable lens for the Visa follow-on lead (E10, 84 members) if that case opens.

## E12 — the counterfactual: how many other members does ACU pay, and does the mention pipeline miss real bill-relevant relationships?

- **query/script:** `queries.sql#q-e12` — full ACU honoree population (same base as EBarr4/q-barr4)
  left-joined against `derived_client_press_mentions` (entity_id 644/645) to split into
  mentioned-at-all vs. never-mentioned; separately, spot-check of Bill Huizenga (`H001058`), the
  named cosponsor on Vargas's Credit Union Board Modernization Act (E8), against his own
  `press_releases` rows.
- **result:** ACU pays (FECA, confidence≥0.9 honoree match) **527 distinct members**, $6,208,500
  total (same population as EBarr4). Of those 527, only **27 (5.1%) receive any ACU press mention
  at all** — at any count, not just the `n_mentions>=2` screen threshold. The 10-member bench is a
  subset of those 27 at the `>=2` threshold; **2 more members clear the same `>=2` threshold but
  were not in the original bench** (Gary Peters, D-MI, 2 mentions/$20,000; Todd Young, R-IN, 2
  mentions/$8,500) — worth a note that the bench as built is not the *complete* set of `>=2` matches
  from ACU specifically, just the 10 pairs the seeding screen (screen-36) originally returned; not
  investigated further here, flagged for the methodology writeup as a completeness caveat on the
  bench's own construction.
  **The remaining 500 paid members (94.9%) get zero ACU press mentions, ever** — including several
  paid *more* than any bench member: Katherine Clark ($50,000, House Dem Whip), Hakeem Jeffries
  ($45,000, Minority Leader), Maxine Waters ($42,500, Financial Services Ranking Member), Adam
  Schiff ($41,000), Richard Neal ($35,000, Ways & Means Ranking Member) — this reads as leadership/
  committee-relationship money, structurally different from the bench's bill-specific pattern.
  **Direct test of the user's hypothesis (bill-relevant unmentioned member):** Bill Huizenga
  (R-MI) is paid $35,000 by ACU and is the named cosponsor, alongside Vargas, on the Credit Union
  Board Modernization Act (E8's bill) — introduced twice (118th HR.582, 119th HR.975) — yet has
  **zero ACU press mentions** despite being paid more than 8 of the 10 bench members. Checked his
  full `press_releases` history (17 rows, 2025-09-30 through 2026-03-30): no release from Huizenga's
  own office names the bill or ACU; the ONLY releases naming the credit-union bill are Vargas's
  (`bench_press_releases.csv`, 2023-01-26 and 2025-02-05), which credit Huizenga as co-lead in
  *Vargas's* text. **Confirms the user's hypothesis exactly**: Huizenga is bill-relevant AND paid,
  but invisible to the mention pipeline — not because he doesn't act on the bill, but because the
  pipeline attributes a press release to whichever member's own site hosts it
  (`press_releases.bioguide_id`), and cosponsors who let the lead sponsor issue the release never
  generate their own qualifying row. This is the mention-pipeline selection bound already documented
  in `docs/derived_db.md` (ABA is invisible the same way, as a client rather than a cosponsor), now
  demonstrated with a same-bill, same-case, named individual instance rather than only stated
  abstractly.
- **source records:** `honoree_member_map` (confidence≥0.9) join to `senate_contribution_items`/
  `senate_contribution_filings` (registrant 11322, `contribution_type='feca'`), left join
  `derived_client_press_mentions` (entity_id 644/645); Huizenga spot-check against `press_releases`
  filtered `bioguide_id='H001058'`. All re-derivable, no new derived table needed.
- **caveats:** this checks only ACU's own registrant (11322); doesn't check whether Huizenga is
  independently paid/mentioned by ABA/ICBA/other credit-union-adjacent associations (out of scope
  here, would be part of the ABA/ICBA/MBA build if that's ever run). Doesn't attempt full bill-text
  search across the 500 unmentioned members' own sponsored/cosponsored legislation — that would
  require either a Congress.gov sponsor-search per member (500 lookups, not attempted, costly) or
  parsing ACU's own lobbying-activity text for named bill numbers (168 distinct H.R./S. tokens found
  in a first pass via `queries.sql#q-e12b`, unfiltered by Congress session — bill numbers repeat
  across Congresses, as already documented for S.3992/S.2486, so this raw list is NOT yet a safe
  source for "which members" without per-bill Congress.gov resolution; not pursued further this
  session, flagged as a possible follow-up if the counterfactual needs to be quantified beyond one
  named instance). The Huizenga case is one clean, verified example, not a systematic count of "how
  many bill-relevant-but-unmentioned relationships exist" — that number is not yet known.
- **verdict:** SUPPORTS the user's hypothesis and STRENGTHENS the methodology-track deliverable.
  ACU's full paid-member population (527) dwarfs its press-mention population (27, 5%), and the
  bench (10) is a further sub-selection within that 5% — confirming numerically what E-scout/EBarr
  chapter already argued qualitatively (the mention pipeline is heavily selected, not a
  representative sample of ACU's relationships). The Huizenga case gives the selection bound a
  concrete, named, citable face: a real cosponsor of a real bench bill, paid more than most of the
  bench, structurally invisible to the exact triple-join method this case validated — the strongest
  single piece of evidence yet for why "mention-pipeline-selected" is a caveat that belongs
  prominently in the findings-report writeup, not a footnote.

## E13 — should Peters/Young be added to the bench? Peters: real triple, fails the threshold; Young: no

E12 flagged Gary Peters (D-MI) and Todd Young (R-IN) as clearing the same `n_mentions>=2` screen
threshold as the bench, but not chased further. Editor asked directly whether they should be added.

- **query/script:** `queries.sql#q-e13` — deduped press-mention count for both (repeating E0's
  `(bioguide, url)` dedup, which E12's quick query skipped); named-bill lobbying-text search for
  each member's flagship bill against ACU's Senate filings; contribution total (same base as E12).
- **result:** **E12's "2 mentions" for both was wrong — the same entity-644/645 double-count bug
  documented in E0 and fixed in `build_bench_press.py`, which E12's ad hoc query didn't apply.**
  Deduped on `(bioguide, url)`, both have exactly **1 real ACU press mention, not 2** — neither
  actually clears the bench's own `n_mentions>=2` entry threshold. This was a bug in E12, not a gap
  in how the bench was built; retracts E12's "completeness gap" framing for these two specific names
  (the general point — that the bench isn't necessarily the *complete* set of `>=2` pairs — stands on
  its own logic, just not demonstrated by these two).

  Checked the full triple anyway, since threshold aside, the substantive question is whether either
  belongs:
  - **Peters — real triple, would qualify on substance if the mention threshold were relaxed to
    >=1.** $20,000 ACU money (4 items, 2022-2025, standard cadence). His 2024-06-13 release
    ("Peters Reintroduces Bipartisan Bill to Bolster Housing Financial Literacy") is self-authored,
    naming him as sponsor. ACU's own Senate lobbying filings name "the Housing Financial Literacy
    Act of 2021 (H.R. 1395)" verbatim in 4 filings (2022 Q2 - 2023 Q1, i.e. the 117th-Congress
    version, predating his 2024 "reintroduces" release for a later Congress's version — bill-number
    lineage across the reintroduction not yet traced via Congress.gov, same caveat as every other
    bench member's multi-Congress bills). Money + named-bill lobbying text + self-authored press
    quote: all three legs present. **The only thing keeping Peters off the bench is the
    `n_mentions>=2` cutoff itself** — he has exactly 1 confirmed ACU mention, same as Beatty's or
    any other single-release member, but unlike Beatty he doesn't have a *second* press touchpoint
    to clear 2.
  - **Young — money + 1 press mention, lobbying leg does NOT confirm.** $8,500 ACU money (4 items).
    His 2023-03-03 release ("Young Reintroduces Bill to Block IRS Surveillance, Protect American
    Taxpayers") is self-authored. Searched ACU's Senate lobbying text for the bill by subject
    (IRS surveillance / taxpayer privacy / weaponization) and found **zero matches** — this bill is
    not a credit-union-specific bill (it's a general taxpayer-privacy bill; not obviously in ACU's
    core issue set the way every bench member's bill is), and ACU's own sworn filings never name it.
    Young's case is money + press only, no lobbying-text leg — structurally the same shape as
    Beatty's already-documented E7 break, not a new full-triple member.
- **source records:** contribution query same base as E12/EBarr4; press dedup same base as
  `analysis/build_bench_press.py`; lobbying-text search: `senate_lobbying_activities.description`
  LIKE search against registrant 11322's filings, both terms confirmed present/absent by direct
  string inspection (not just COUNT), see `queries.sql#q-e13`.
- **caveats:** Peters' bill lineage across Congresses (117th H.R.1395 → whatever number the 2024
  "reintroduction" carries) hasn't been resolved via Congress.gov the way the bench's 10 members'
  bills were in `bench_bill_dates.csv` — would need that pull before citing dates as precisely as
  the rest of the bench. This entry checks textual/substantive presence of the lobbying leg, not a
  full Congress.gov-verified date reconciliation.
- **verdict (superseded by E14, 2026-07-09):** as of this entry, Peters had a full triple by the
  loose "any real triple" standard and Young did not; this entry recommended NOT changing the bench
  and citing Peters only as a methodology point. Editor overruled the recommendation to leave the
  canonical 10 as-is: **"I don't know why we need to restrict it to 2 or more mentions."** The
  `n_mentions>=2` threshold was inherited from the screen-36 seeding query, not derived from
  anything about what makes a triple real — E1-E9's actual verification standard was always the
  independently-checked triple itself, not the screen's entry filter. Peters added to the bench;
  see E14 for the addition and a correction this pull surfaced (his lobbying-text match is for a
  DIFFERENT bill number/Congress than his press release covers, not a clean match as first read).
  Young was not added — money + press only, no lobbying leg, stands as before.

## E14 — Peters added to the bench; correction: the lobbying leg is 117th-Congress text, not his actual (118th) reintroduction

Editor's call (2026-07-09): drop the `n_mentions>=2` construction threshold and add Peters to the
bench, since E13 already established his full triple independently. While updating the derived
CSVs, pulling his bill's exact Congress.gov lineage surfaced a correction to E13's framing.

- **query/script:** `queries.sql#q-e14` (Congress.gov API: `member/P000595/sponsored-legislation`,
  paginated across all 913 of his sponsored bills to find the 118th-Congress "Housing Financial
  Literacy Act" entry; `bill/117/hr/1395/relatedbills` to confirm the House/Senate companion
  relationship). Rebuilt all 4 `derived/bench_*.csv` files via the updated `analysis/build_bench_*.py`
  / `pull_bill_dates.py` scripts (Peters added to each `MEMBERS` dict).
- **result:** the House bill this case already had on file, H.R. 1395 (117th Congress, "Housing
  Financial Literacy Act of 2021"), is sponsored by **Beatty, not Peters** — E13 conflated "ACU's
  lobbying text names this title" with "this is Peters' bill" because both share an identical short
  title. Peters' actual bill is the **Senate companion, S.1490 (117th Congress)**, introduced
  2021-04-29 — confirmed via Congress.gov's `relatedBills` endpoint as an "Identical bill" to
  H.R.1395, sponsored by Peters. His 2024-06-13 press release ("Reintroduces...") covers a
  **different bill number in the NEXT Congress: S.4542 (118th)**, introduced the same day as the
  release (found only by paginating all 913 of his sponsored-legislation entries — the title is
  identical across both Congresses, "Housing Financial Literacy Act," so a name search alone
  wouldn't distinguish them).

  Re-checked ACU's lobbying text against this corrected lineage: **ACU's Senate filings name
  "Housing Financial Literacy Act" only in 2022 Q2 - 2023 Q1 filings** (4 filings) — squarely inside
  the 117th Congress (S.1490's life, 2021-2023) — **and never again after**, including throughout
  all of 2024-2026 when S.4542 (the bill his actual press release covers) was live. ACU continues
  filing every quarter through 2026 Q1 on other issues/bills; the silence on this specific title is
  not a data gap, it's a real absence.

  **Peters' triple, precisely stated:** money (real, $20,000/4 items, standard cadence, same shape
  as every other bench member) + press (real, self-authored, same-day as his bill's introduction,
  same pattern as the bench's dominant same-day sub-type) + lobbying-text (real, but for the
  PRIOR Congress's bill number, with a documented gap covering the exact period his press release
  and reintroduction fall in). This is a **partial/lagged triple**, not a clean match like Barr/
  Cramer/Scott/Fitzgerald/Vargas/Gonzalez/Budd — closer in kind to Britt (money precedes the
  bill-press pair) or Beatty (a real, dated gap in one leg) than to the bench's fully-continuous
  majority.
- **source records:** Congress.gov API responses cached under `data/congress_bills/` (gitignored,
  shared cache pattern with `pull_bill_dates.py`); ACU lobbying filings per `queries.sql#q-e13b`
  (unchanged from E13, re-confirmed here against the corrected Congress numbers).
- **caveats:** this is a 2-data-point bill lineage (117th + 118th); did not check whether a 119th
  reintroduction exists yet (S.4861, "Housing Financial Literacy Act of 2026," introduced
  2026-06-23, found in the same API pull but not yet added to `bench_bill_dates.csv` — out of the
  case's 2022-2026 Q1 filing window used elsewhere, not pursued). ACU's 2022-2023 lobbying text was
  matched by title only (`%housing financial literacy%`), same method as every other bench member's
  lobbying leg in this case — no bill-number-specific text was found in any ACU filing for either
  S.1490 or S.4542 specifically, only the title phrase.
- **verdict:** Peters is the bench's 11th member, added per editor's decision to drop the `>=2`
  threshold as arbitrary. His inclusion is itself a useful demonstration for the findings-report
  writeup — not just as a "near-miss the threshold excluded" (E13's framing) but as a genuinely
  DIFFERENT typological case once correctly dated: a member whose ACU-lobbied bill and ACU-endorsed
  bill are technically two different pieces of legislation across two Congresses, with lobbying
  support that lapsed exactly when the press/money relationship continued. This sharpens rather than
  weakens the case's overall finding that the "full triple" is not one uniform pattern (E11) — Peters
  is now the clearest single illustration of that point, alongside Britt's money-precedes-bill
  inversion and Beatty's lobbying-text absence.

## E15 — the null model, stated explicitly, and every deviation from it across all 11 members

E11/E12/E14 established three separate empirical patterns piecemeal. Editor named them as one
explicit null model and asked whether the signal is in the deviations, not the pattern itself — a
useful reframe: this entry restates E11/E12/E14 as three baseline rules, then systematically checks
all 11 bench members (+ the 500-vs-27 population from E12) against each rule and catalogs every
exception, rather than leaving deviations scattered across separate entries.

- **query/script:** re-run of E11's per-member sequencing logic plus a new check —
  first-lobbying-mention date vs. first-bill-introduction date, per member — cross-referenced
  against ACU's raw lobbying-activity text to resolve any case where lobbying starts before the
  bill's introduction (rather than treating "before" as anomalous on its face). See `queries.sql#q-e15`.
- **the null model, as three baseline rules:**
  1. **Lobbying text follows bill introduction** — mechanically close to tautological, since the
     bench members were found BY searching ACU's lobbying text for their bill's name; a bill can't
     be lobbied by name before it has a name. Editor's prediction: if lobbying appears to start
     *before* the tracked bill's introduction, the likely explanation is an earlier-Congress
     predecessor bill with the same/similar name, not genuine pre-bill lobbying.
  2. **Press and bill introduction are coupled** — already quantified in the 2026-07-08 press-hook
     check and E11 (bill→press same-day-to-a-few-days for most members).
  3. **Money arrives on its own schedule, largely independent of press/bills** — already quantified
     in E11 (45-day responsiveness: median 0%, range 0-38%) and E12 (527 members paid, only 27 ever
     mentioned — money reaching hundreds of members who never get press or lobbying-text coverage
     at all).
- **result, checked against all 11 members:**

  **Rule 1 — confirmed, and the editor's predicted mechanism is exactly right.** Only 2 of 11
  members (Vargas, Gonzalez) have ACU lobbying text that appears to predate their tracked bill's
  introduction — every other member's lobbying starts after (7 members) or never starts (Beatty).
  Checked both "early" cases directly against the raw lobbying-activity text: **Vargas's earliest
  lobbying filing (2022-04-20, filing_uuid `9cc0cbde-933f-45e6-96a0-7dc27424380c`) already names
  "H.R. 6889, Credit Union Board Modernization Act"** — a 117th-Congress bill number, NOT the
  118th-Congress H.R.582 already in `bench_bill_dates.csv`. [CORRECTED 2026-07-09, verify pass: the
  same filing separately names a different bill, "H.R. 7003, Expanding Financial Access to
  Underserved Communities Act" — an earlier draft of this entry misattributed the Credit Union Board
  Modernization Act's title to that bill number instead of H.R.6889; H.R.7003 is unrelated to
  Vargas's tracked bill and plays no role in this case.] Gonzalez's 2022-04-20 filing similarly
  names "Veterans Member Business Loan Act" in a 117th-era bill list. Both are exactly the editor's
  predicted mechanism: an earlier-Congress predecessor bill with the same title, not ACU lobbying
  language ahead of any bill existing. **This is a real gap in E8/E9's original bill inventory** —
  neither has ever pulled the 117th-Congress bill number (only 118th/119th were in
  `bench_bill_dates.csv`) — logged as a follow-up, not yet fixed this session. Rule 1 holds with
  zero true exceptions once the "before" cases are explained.

  **Rule 2 — confirmed, no new deviations found beyond what's already logged.** Every member with
  both press and bill data shows the large majority of press releases within 7 days of a bill
  event; the small number of >7-day "loose" press releases per member (0-2 each) are the same
  already-explained cases from the 2026-07-08 press-hook check (other-milestone releases: reintro/
  passage/signed-into-law of an already-tracked bill) — no new unexplained gaps surfaced.

  **Rule 3 — confirmed as the least-patterned leg, and this is where the actual variation lives.**
  This is where the bench's real deviations concentrate, already documented across three entries:
  **Britt** — money entirely PRECEDES the bill/press pair (E11 item 3), the sharpest individual
  deviation from "money follows the relationship passively" — for her specifically the sequence
  looks like patron-first, bill-later. **Peters** — money and press are clean/normal, but the
  *lobbying* leg (not money) is what deviates, supporting a stale bill number through a real,
  dated gap (E14). **Beatty** — the one member with zero lobbying-text support despite money and
  press both being normal (E7). **The 500-vs-27 population split (E12)** is Rule 3's population-
  level version: the overwhelming majority of ACU's paid relationships never generate press or
  (by definition, since the mention pipeline is how bench candidates were found) lobbying-text
  matches either — money is the default state, press/lobbying coverage is the exception layered on
  top of a subset of it.
- **source records:** all figures cited here are re-derivations of E8/E9 (Vargas/Gonzalez bill
  lineage — NEW check this entry), E11 (money responsiveness), E12 (population split), E14
  (Peters). The 117th-Congress bill-number identification for Vargas/Gonzalez is a new textual
  read of `senate_lobbying_activities.description`, not yet resolved via Congress.gov the way the
  rest of the bench's bills are (no `bench_bill_dates.csv` row yet for H.R.6889 or Gonzalez's
  117th-era bill number — flagged as a follow-up).
- **caveats:** Rule 1's "before" check is a first-lobbying-mention vs. first-bill-date comparison,
  not a full audit of whether every early lobbying filing is provably about the SAME underlying
  policy as the later-numbered bill (plausible given identical/near-identical titles, but not
  Congress.gov-verified the way every other bench bill-date claim in this case is). Rule 3's
  "money is independent" finding is a correlational read of dates (E11), not a causal claim — it
  does not rule out money and legislative activity both being driven by a third factor (e.g.
  committee assignment, general relationship-building cycles) that this case hasn't modeled.
- **verdict:** SUPPORTS the editor's reframe. Stating the three patterns as an explicit null model
  and hunting deviations, rather than treating each pattern as a separate finding, is a clearer
  organizing frame for the findings-report writeup than E11-E14's original ad hoc ordering. Under
  this frame, the bench's actual "signal" members are precisely the ones already flagged by
  different means: Britt (money-timing deviation), Peters (lobbying-continuity deviation), Beatty
  (lobbying-absence deviation) — three different members, three different legs of the same null
  model each breaking once. No member breaks more than one leg. This is a stronger, more falsifiable
  way to present the case's methodology than the original "9 of 10/11 confirm a triple" framing,
  and directly motivates the still-open Vargas/Gonzalez bill-inventory gap as the next concrete
  task, not just a curiosity.

- **ADDENDUM (2026-07-09, same session) — Beatty's deviation is CORRECTED, see E7's revision.**
  Beatty has a second bill (H.R. 3709) this case had missed, with a real (if thin, 1-filing)
  lobbying-text match — she is no longer a clean Rule-1 "absent" case. Her deviation moves from
  "lobbying-text absent entirely" to a split record: one bill breaks Rule 1 (H.R.5911, still zero
  matches, negative result stands), one bill satisfies it (H.R.3709). This means **the bench
  currently has zero members with a clean, single-bill "lobbying absent" break** — every member has
  at least one bill with a confirmed lobbying-text match once their full bill inventory is
  complete. The pattern that survives is narrower and arguably more interesting: it's not "does
  this member's lobbying leg exist," it's "which of a member's MULTIPLE bills get lobbying support
  and which don't" — Beatty is now the bench's clearest illustration of THAT distinction (ACU
  named-quote-endorsed and lobbied her small-institution bill, but neither named-quote-endorsed
  with more than a roster mention nor lobbied her justice-reform bill), not of lobbying absence per
  se. Britt and Peters' deviations are unaffected by this correction.

## E16 — systematic pass: every unmatched press release, checked; 2 more missed bills found (Budd, Vargas)

Editor asked for a systematic version of the ad hoc discovery that found Beatty's second bill —
suspected more press releases were sitting without bills. Rather than keep discovering bills one at
a time by manual reading, this entry checks EVERY press release across all 11 bench members against
the current bill inventory in one pass, then reads the full text of every unmatched one.

- **query/script:** for each member, computed the minimum date-gap between every press release and
  every bill in `bench_bill_dates.csv`; flagged any release with no bill within +/-7 days. Then
  pulled the full `press_releases.text` (not just title) for each flagged release. `queries.sql#q-e16`.
- **result:** 6 of 28 press releases (post-Beatty-fix) had no bill within 7 days. Read all 6 in full:
  - **Barr 2025-05-03** (gap 65d) — confirmed already-known: this is the House-passage/"reintroduces"
    milestone of the already-tracked Rectifying UDAAP Act, not a new bill (matches the 2026-07-08
    press-hook check's finding).
  - **Emmer 2025-07-17** (gap 133d) — confirmed already-known: House-passage milestone of the
    already-tracked Anti-CBDC Surveillance State Act, not a new bill (same prior finding).
  - **Cramer 2024-04-09** (gap 20d) — read in full: this release is about a $6M HHS rural-health
    funding award to North Dakota, unrelated to any credit-union or ACU legislation. Correctly NOT a
    bill-related release; no action needed, confirms the press-hook check's "genuine miss" category
    is empty, not that every gap hides a bill.
  - **Beatty 2022-12-23** (gap 409d) — confirmed already-known: NDAA enactment milestone of the
    already-tracked Fair Hiring in Banking Act (pre-dates the E7 correction above, unaffected by it).
  - **Vargas 2024-01-10** (gap 349d) — **NEW FINDING.** This release is Vargas announcing his OWN
    cosponsorship of the Expanding Access to Lending Options Act — which is ALREADY in the bill
    inventory, but only credited to Fitzgerald (E5), not Vargas. Confirmed via Congress.gov:
    Vargas is an **original cosponsor** of H.R.6933 (118th), sponsorship date 2024-01-10 — same day
    as his release. ACU's lobbying text already names this bill (9 filings, already counted under
    Fitzgerald's E5 total). This is not a new bill in the corpus sense, but it IS a previously
    uncredited second bill-relationship for Vargas specifically — he now has 2 tracked bills
    (Credit Union Board Modernization Act, his flagship, E8; Expanding Access to Lending Options
    Act, shared with Fitzgerald, new).
  - **Budd 2024-06-18** (gap 90d) — **NEW FINDING, a genuinely new bill.** "Budd Introduces Bill to
    Force Federal Reserve to Pause Debit Card Proposal That Hurts Consumers" — the Secure Payments
    Act. Confirmed via Congress.gov: **S.4570 (118th), sole sponsor Budd, introduced 2024-06-18** —
    same day as the release (the bench's dominant same-day pattern). ACU's Senate lobbying text
    names it in 3 filings (2024 Q3-Q4, citing both the House companion H.R.7531 and Senate S.4570 by
    number). Budd now has 2 tracked bills: the shared SBA-lending bill (E6, with Cramer/Scott) and
    this one, sole-sponsored.
- **source records:** Vargas cosponsorship confirmed via Congress.gov `bill/118/hr/6933/cosponsors`
  (live API call); Budd's bill confirmed via `bill/118/s/4570` and `bill/118/hr/7531` (live API
  calls, both return Budd/Luetkemeyer as sponsors respectively); Budd's ACU lobbying-text match at
  `queries.sql#q-e16b`; Cramer's HHS release read in full via `press_releases.text`, confirmed
  unrelated (not logged as a query since it's a negative/exclusion, not a citation).
- **caveats:** this pass only checked press-release-to-bill in one direction (do unmatched releases
  hide missed bills). The REVERSE direction — does ACU's lobbying text name any bill, for any bench
  member, that never generated a matching press release at all — was NOT checked this session; it
  would require scanning ACU's full lobbying-issue text for bill numbers/titles tied to bench
  members' other sponsored legislation, a larger search than this pass, flagged as a follow-up, not
  attempted here.
- **verdict:** the systematic pass was worth running — it caught 2 real gaps (Budd's second bill,
  Vargas's uncredited cosponsorship) that ad hoc discovery had missed, and correctly confirmed that
  the other 4 apparent gaps were not new bills (3 already-known milestones, 1 genuinely unrelated
  release). Updated bill counts: Vargas now 2 tracked bills, Budd now 2 tracked bills. This
  strengthens rather than complicates E15's null model — Budd's new bill follows the same
  same-day-lobbying-and-press pattern as everything else in the bench, and Vargas's uncredited
  cosponsorship is additional support for an already-confirmed full-triple member, not a new
  deviation. No new deviation-from-null-model cases were found in this pass; the three named
  deviations (Britt, Peters, and — per E7's correction — the split-record framing for Beatty) still
  stand as the complete list.

## E17 — Britt's endorsement is conditional, not enthusiastic: ACU's own Simpson quote calls the bill it's backing "an important step" while demanding full Durbin Amendment repeal

Editor found this by reading ACU's own website (americascreditunions.org), not a member's press
release or an LDA filing — a different source type from anything else cited in this case. Worth
verifying carefully since it's the first ACU-first-party source used, and worth checking whether
the quote is unique to that outside page or was already sitting, unexamined, in the corpus.

- **query/script:** fetched `americascreditunions.org/news-media/news/credit-unions-back-legislation-
  update-durbin-amendment-threshold` directly (WebFetch was blocked with HTTP 403 — bot-detection,
  not access-restricted; a direct `curl` with a standard browser User-Agent returned HTTP 200 and
  the full article). Cross-checked against the corpus: `queries.sql#q-e17` pulls `press_releases.text`
  (not just title, which is all E3's original pass checked) for Britt's already-cited 2026-02-13
  release, `bioguide_id='B001319'`, title "U.S. Senators Katie Britt, Ted Cruz Introduce Legislation
  to Protect Community Banks."
- **result:** **the exact same quote was already sitting in the corpus, unexamined** —
  `press_releases.text` for Britt's 2026-02-13 release (already cited in E3, but only as "ACU named
  quote, Scott Simpson, President & CEO," with the quote's actual content never pulled or read) is
  effectively a syndicated version of the same news, from Britt's own site rather than ACU's, with
  matching sponsor names (Cruz/Britt/Barr), matching bill description (indexing the Durbin
  Amendment's $10B asset threshold to inflation), and the identical Simpson quote:

  > "This legislation is an important step forward. But the only real long-term solution is full
  > repeal of the Durbin Amendment. Government imposed price controls have distorted the market and
  > failed to deliver promised savings to consumers... Repeal would ensure credit unions can continue
  > delivering affordable, secure financial services without artificial caps that miss their mark."

  This is a **conditional endorsement**, not the uniformly enthusiastic "ACU applauds/supports"
  framing every other named quote in this case carries (compare EBarr7, E4's "Carrie Hunt" quote,
  E7's Nussle quote — all straightforwardly supportive with no qualifying language). ACU is on the
  record, in the same release that names and thanks Britt, saying her own bill doesn't go far
  enough and that ACU's actual policy goal (full repeal) is bigger than what she introduced.
  Systematically checked every OTHER bench member's press-release text for similar qualifying
  language ("doesn't go far enough," "important step," "long-term solution," "full repeal," "falls
  short," etc.) — **Britt's is the only hit in the entire bench.** This is a specific, individual
  finding, not evidence of a broader pattern of qualified endorsements.

  Checked whether ACU's sworn Senate lobbying text shows a distinct "repeal Durbin" push matching
  the public rhetoric: no — ACU's filings have named "Durbin Amendment"/"Reg. II"/"interchange" as a
  general issue-code line since 2022 (long before Britt's bill existed), and no filing isolates
  "repeal" as a distinct ask separate from that generic, years-long issue-code language. The public
  repeal-advocacy quote does not appear to be mirrored as a new, distinct lobbying position in the
  sworn filings — it reads as rhetorical positioning layered onto the endorsement, not (yet, as of
  the most recent 2026 Q1 filing) a documented change in ACU's formal ask.
- **source records:** `press_releases.text` where `bioguide_id='B001319'` and `date='2026-02-13'`
  (already in corpus, `bench_press_releases.csv` row, url:
  `https://www.britt.senate.gov/news/press-releases/u-s-senators-katie-britt-ted-cruz-introduce-
  legislation-to-protect-community-banks/`); externally, ACU's own syndication at
  `americascreditunions.org/news-media/news/credit-unions-back-legislation-update-durbin-amendment-
  threshold` (2026-02-13, quotes Scott Simpson, ACU President/CEO) — cited as corroborating context,
  not as the primary evidentiary source (the corpus's own `press_releases.text` already carries the
  identical quote and is the citable record for this case's evidentiary chain).
- **caveats:** this is one member, one release, one quote — not (yet) shown to be a pattern across
  the bench (checked, and it isn't). Whether ACU's public "full repeal" framing is genuinely at odds
  with Britt's bill, or just standard "step in the right direction, but here's our bigger ask"
  advocacy rhetoric common across trade associations, is an editorial judgment call, not something
  the data resolves — flagged as a nuance for the writeup rather than asserted as tension/hypocrisy.
  ACU's own external site (used to spot this) is not itself part of this case's verified evidentiary
  chain the way `gain.db` rows are — the finding is fully re-derivable from the corpus alone (the
  quote is in `press_releases.text`), so the external page functions as a discovery aid, not a
  citation dependency.
- **verdict:** a genuinely new, specific finding — not previously surfaced despite the underlying
  data (`press_releases.text`) being in the corpus and already cited (E3) since this bill was first
  drilled down. The gap was that E3's original pass, like most of E1-E9/E13/E14/E16, matched on
  `title`/`url` and confirmed a quote's *existence* but never pulled and read the quote's actual
  *content* for editorial nuance. This is a methodology lesson worth carrying forward: "ACU gives a
  named quote" has been treated as one category throughout this case, but quotes vary from
  unqualified support to conditional/dissatisfied support, and only reading the full text surfaces
  that distinction. Recommend re-reading each bench member's named-quote press releases in full
  before the findings-report writeup locks in language calling them all "endorsements" — Britt's
  needs its own framing.

## E18 — full-text read of all 28 press releases: Britt's caveat is confirmed unique; Scott Simpson identity CORRECTED (2026-07-09); no other new bills or gaps

Follow-up to E17's recommendation: read every ACU (and ACU-adjacent) mention across all 28 bench
press releases in full, not just Britt's, to check for other missed nuance.

- **query/script:** pulled `press_releases.text` for all 28 rows in `bench_press_releases.csv`,
  located every substring match for "America's/America’s Credit Unions," "ACU," or "CUNA," and read
  the surrounding paragraph for each hit. `queries.sql#q-e18`.
- **result:**
  1. **Britt's caveat is confirmed the only one.** Every other ACU/CUNA quote across the bench (17
     other quoted instances, 9 different members) is unqualified support — "applauds," "thanks,"
     "we support," "we look forward to" — with no "but," "important step," "not enough," or similar
     language anywhere else. This is now a full-text-verified negative result, not just a keyword
     search (E17 already ran the keyword search; this entry confirms it by reading every hit in
     context, catching anything a keyword list might miss).
  2. **CORRECTED (2026-07-09): "Scott Simpson" is ONE person, not a name collision.** This entry
     originally flagged "Scott Simpson" as two different executives sharing a name — quoted as
     ACU's national President/CEO in Britt's (2026-02-13) and Gonzalez's (2026-02-24) releases, and
     separately as "President and CEO of the California and Nevada Credit Union Leagues" in
     Vargas's 2025-02-05 release — and treated it as a free-text identity trap. **Editor looked him
     up directly and confirmed it's the same individual: Simpson moved from leading the
     California/Nevada Credit Union Leagues (a state league) to the national America's Credit
     Unions presidency.** The dates support this cleanly: the state-league quote is 2025-02-05; the
     first national-ACU-President quote in this bench is 2026-02-13, over a year later — consistent
     with a real career transition, not a same-day naming coincidence. This is NOT a data-quality
     trap; it's a genuine, useful fact — the same individual speaking for two different
     organizations in this bench reflects an actual leadership transition at ACU, worth noting for
     context (e.g. if citing Simpson's quotes in the findings writeup, his title/organization should
     be dated correctly per release) but not a corpus hazard the way E0's dedup bugs or the
     `honoree_name` free-text caveats are. No other-name-collision risk demonstrated by this case
     between two genuinely different people; withdraw the "trap" framing.
  3. **Fitzgerald's 2025-02-26 release covers two bills in one release, but only one has an ACU
     quote — checked, not a gap.** The release announces both the CFPB Accountable to Small
     Businesses Act (already tracked, E5) and a second bill, the Separation of Powers Restoration
     Act (SOPRA, a Chevron-deference bill). ACU's quote is explicitly and only about the CFPB
     Accountable bill; SOPRA gets no ACU mention, no other trade-association mention, and is not
     credit-union-specific subject matter. Correctly not a bill this case needs to track — the
     ACU-relevant half of a two-bill release was already the half in scope.
  4. **No other new bills, cosponsorships, or missed gaps found** in this full-text pass beyond what
     E16 already surfaced (Budd's Secure Payments Act, Vargas's Expanding Access cosponsorship) and
     E7 (Beatty's Mentor-Protégé bill) — those three remain the complete list of bill-inventory gaps
     found across this case's systematic checks.
- **source records:** all 28 `press_releases.text` rows joined via `bench_press_releases.csv`
  (bioguide_id/date/url); no new primary source records, this entry re-reads existing corpus text.
- **caveats:** this pass read every ACU/CUNA-adjacent quote for tone/qualifiers and every release's
  full text for missed bills — but did not run a similarly systematic check for OTHER trade
  associations' qualifiers (ABA, ICBA, BPI, etc. also appear in several releases with their own
  quotes) — out of scope for this case, which is ACU-specific.
- **verdict:** confirms E17's finding is a genuine, isolated outlier, not the tip of a broader
  pattern — strengthens rather than weakens its citability in the findings report (it's not diluted
  by being one of several similar cases). The "Scott Simpson" observation, corrected above, is a
  real fact about ACU's leadership transition (not a data trap) — worth a dated citation if used in
  the writeup, not a hazard flag. No new bills or bench
  members result from this pass.
