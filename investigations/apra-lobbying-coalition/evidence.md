# Evidence — apra-lobbying-coalition

## E1 — Lobbying volume on named federal privacy bills

**CORRECTED 2026-07-08 (post-E16 filter fix) — see the "E1 corrected"
block below. The figures directly under "result"/"verdict" here are
superseded; do not cite them going forward.**

- **query/script:** `queries.sql#q1`, `#q1b`, `#q1c`
- **result (superseded):** 1,008 combined Senate+House lobbying activities
  (509 Senate / 499 House) mentioning ADPPA/APRA or a named predecessor
  bill (American Privacy Rights Act, Consumer Online Privacy Rights Act,
  Data Privacy Act, American Data Privacy [and Protection Act], "ADPPA"),
  2022–2026. By year (Senate): 2022=147, 2023=139, 2024=198, 2025=21,
  2026=4. 101 distinct Senate-side clients.
- **source records:** originally scouted in the `fish-for-leads` pass
  (screen_run_id 23, lead slug `cpi-federal-privacy-bill-quiet-coalition`);
  re-derived directly against `db/gain.db` in this case 2026-07-03 (see
  verdict below). Individual `filing_uuid`s not yet pulled for citation —
  next step if this becomes a cited claim.
- **caveats:** Keyword-matched on `senate_lobbying_activities.description` /
  `house_activities.description` LIKE patterns, which may over- or
  under-count depending on how consistently registrants name the bill vs.
  describe it generically ("federal privacy legislation," "data privacy
  issues" with no bill number). This risk cuts toward under-counting and
  is exactly what E3 confirms for the advocacy-org roster specifically —
  the true self-identified-as-APRA universe may be smaller than the
  keyword match suggests, once each client's actual language is read
  rather than assumed.
- **verdict (superseded):** re-derived 2026-07-03, numbers confirmed exact
  (`python3` direct query against `db/gain.db`): Senate by year
  2022=147/2023=139/2024=198/2025=21/2026=4 (509 total); House by year
  2022=143/2023=139/2024=195/2025=21/2026=1 (499 total) — 509+499=1,008,
  matches the scout number exactly. 101 distinct Senate clients confirmed.
  **Superseded — this used the same shared filter E16 found contaminated
  by H.R. 1165 ("Data Privacy Act of 2023," an unrelated financial-sector
  bill).**

### E1 corrected (2026-07-08, post-E16 filter fix)

- **query/script:** `queries.sql#q1`/`#q1b`/`#q1c`, re-run after removing
  the bare `%data privacy act%` clause (confirmed by direct query to add
  zero genuine APRA/ADPPA rows and 810 false-positive rows corpus-wide —
  see E16).
- **result:** Senate (CPI-only) by year: 2022=147, 2023=83, 2024=169,
  2025=14, 2026=3 (416 total, down from 509). House (CPI-only) by year:
  2022=143, 2023=83, 2024=166, 2025=14, 2026=1 (407 total, down from 499).
  Combined 823 (down from 1,008). 79 distinct Senate-side clients (down
  from 101). 2022 is essentially unchanged (H.R. 1165 wasn't introduced
  until 2023) — the contamination is entirely 2023 onward.
- **verdict:** the correction shrinks 2023 the most (139→83, a 40% drop),
  consistent with H.R. 1165's 2023 introduction generating ongoing "Data
  Privacy Act of 2023" filings through 2025. The by-year shape changes
  (2024 is now clearly the peak year, not a near-tie with 2022) but the
  underlying claim — sustained multi-year Senate+House activity on
  APRA/ADPPA specifically — still holds. **Use 416/407/823 (79 clients)
  going forward, not 509/499/1,008 (101 clients).**

## E2 — Press-release volume on named privacy bills

- **query/script:** `queries.sql#q2`, `queries.sql#q2b`, `#q2c`
- **result:** 19 press releases naming the bills directly by name; 40 under
  a broader "federal privacy / comprehensive privacy / national privacy"
  search. **Revised 2026-07-08 (below): 53 total** once a full manual
  read-through of every "data privacy"-mentioning release not caught by
  either query is added.
- **source records:** not yet resolved to individual `press_releases.url`s
  — next step if this becomes a cited claim.
- **caveats:** measures "did a member of Congress issue a press release,"
  not "was this covered by outside press" — see the non-evidentiary web
  search in `log.md` 2026-07-03, which found real trade/policy coverage
  (Washington Post, IAPP, WilmerHale, IBM, Senate Commerce Committee) that
  this number does not capture. Do not cite E2 alone as evidence of "quiet"
  coverage — it measures one specific channel only.
- **verdict:** re-derived 2026-07-03, both numbers confirmed exact against
  `db/gain.db` (19 direct bill-name matches, 40 broader-search matches).
  No longer "unverified." **Superseded by the 2026-07-08 re-check below —
  the keyword net itself was too narrow; see the revised total.**

### E2 revision (2026-07-08) — was the keyword net itself too narrow?

The editor asked directly: E2 only searched exact bill names plus three
broad phrases ("federal data privacy," "comprehensive privacy," "national
privacy") — had we actually tested for quiet, or just for those specific
strings?

- **method:** queried all `press_releases` containing the bare substring
  "data privacy" (327 total) — a maximally broad net — then identified the
  290 that fall outside E2's original two queries entirely. A general-purpose
  agent read the full text (not just titles) of all 290 and classified each
  as on-topic (substantively about the comprehensive federal
  consumer/commercial privacy standard fight — ADPPA H.R.8152, APRA
  H.R.8818, the Cantwell/McMorris Rodgers discussion draft, or a direct
  successor like Moran's Consumer Data Privacy and Security Act) versus
  off-topic (privacy language attached to a materially different policy
  fight).
- **result:** **13 of the 290 are genuinely on-topic** — real statements
  the original keyword net missed, e.g. Sen. Moran's statement on the
  Cantwell/McMorris Rodgers discussion draft (`release_id` 59350, 2024-04-09,
  bioguide M000934) and DelBene urging Congress to act on data privacy
  alongside the Biden AI executive order (`release_id` 44878, 2023-10-30,
  bioguide D000617). Full 13-item list with dates/bioguides/one-line
  rationale: see `log.md` 2026-07-08 entry (not yet copied into a derived
  CSV — do that before individually citing any of the 13).
- **result — the other 277 confirm the broader "data privacy" substring is
  dominated by unrelated policy fights, not this bill:** reproductive-health
  data privacy (My Body My Data Act family, ~35), the 2025 DOGE/Musk
  federal-data-access controversy (~30, concentrated Feb–Dec 2025 — a
  phenomenon with zero overlap with the 2022–2024 APRA fight this case
  covers), TikTok/foreign-adversary data concerns (~25), the COPPA 2.0/Kids
  Online Safety Act family (~25 — already correctly excluded from this
  case's scope per case.md's explicit KOSA-is-a-different-bill framing),
  committee/subcommittee-name boilerplate (~20, e.g. "Subcommittee on
  Consumer Protection, Technology, and Data Privacy" as a proper noun with
  no substantive engagement), AI-governance mentions in passing (~20),
  23andMe bankruptcy/genetic data (~10), auto/vehicle data privacy (~8,
  a distinct sectoral bill), financial/insurance-sector privacy (~10), and
  ~90 miscellaneous one-offs (student/FERPA, Olympic-athlete surveillance,
  FISA, immigration data, voter rolls, drone surveillance).
- **caveats:** this read used one agent's judgment calls on borderline cases
  (documented: TikTok/Meta/COPPA-controversy statements that pivot to
  explicitly demand the comprehensive bill were counted on-topic — the
  advocacy is the substantive point, not incidental phrasing). Not
  independently re-read by a second pass. The 90-item "miscellaneous"
  off-topic bucket was characterized by theme, not individually verified
  against a checklist — a different reader could plausibly move a few items
  across the line, but not at a scale that would materially change the
  headline number.
- **verdict:** **the "quiet" framing survives this stress test, but the
  E2 baseline number moves from 40 to 53** (19 exact bill-name + 21
  additional under the original broad-phrase search + 13 net-new from this
  read). The gap between the broadest possible naive keyword net (327,
  bare "data privacy") and the actual on-topic count (53) is itself a
  finding: an 85% (277/327) false-positive rate if "data privacy" alone
  had been used as the measure, driven substantially by a *different*,
  much louder 2025 controversy (DOGE/Musk data access) that has nothing to
  do with this bill. This is a caution for E2 going forward and for any
  future press-corpus keyword work in this corpus: a bare policy-domain
  substring match overcounts badly when multiple distinct legislative
  fights share the same vocabulary in the same window.

## E3 — Advocacy-org roster does not self-identify as engaged on APRA specifically

- **query/script:** `queries.sql#q3`
- **result:** read the full, un-keyword-filtered activity text for all CPI
  activities filed by the 8 advocacy/nonprofit organizations identified in
  the CPI client roster (Electronic Frontier Foundation, Fight for the
  Future, Center for Humane Technology, Due Process Institute, Avaaz
  Foundation, David's Legacy Foundation, Children and Screens, Sandy Hook
  Promise Action Fund). **None of the 8 mention APRA, ADPPA, or any of the
  bill-name strings used in E1's match, anywhere in their activity text.**
  Each is engaged on a different, specific bill or topic:
  - Electronic Frontier Foundation: American Innovation and Choice Online
    Act (antitrust/interoperability), Open App Markets Act, Cyber Incident
    Reporting Act.
  - Fight for the Future: generic "human rights in relation to
    decentralized technologies" / "internet governance" — no bill number
    at all.
  - Center for Humane Technology: generic "Artificial Intelligence" — no
    bill number, every filing 2023–2026.
  - Due Process Institute: opposing the RESTRICT Act (S.686) and Cooper
    Davis Act (S.1080) — surveillance/law-enforcement bills, not privacy
    regulation.
  - Avaaz Foundation: Digital Services Oversight and Safety Act (HR6796),
    Algorithmic Accountability — platform-transparency bills, not APRA.
  - David's Legacy Foundation, Children and Screens, Sandy Hook Promise
    Action Fund: all three exclusively cite the Kids Online Safety Act and
    its companion child-safety bills (Children and Teens Online Privacy
    Protection Act, Protecting Kids on Social Media Act, Kids PRIVACY Act,
    Platform Accountability and Transparency Act) — a different bill
    family from APRA, and one confirmed by web search (see `log.md`
    2026-07-03) to be currently well-covered and actively contested, not
    quiet.
- **source records:** `senate_lobbying_activities.description`, joined via
  `senate_filings`/`senate_clients`, for the 8 named organizations —
  `queries.sql#q3` returns the full row set; individual `filing_uuid`s not
  yet pulled for citation (next step if this becomes a cited claim).
- **caveats:** House-side activity for these same organizations not yet
  checked — this result is Senate-only. Only checked the 8 organizations
  identified by name-pattern search in the earlier session (see
  case.md's advocacy-org list) — there could be other public-interest
  orgs in CPI's client roster not caught by that name-pattern search
  (e.g. a consumer-rights group without "foundation," "institute," or
  "coalition" in its name).
- **verdict:** confirms the case's flagged correction — **there is no
  identified organized public-interest voice engaged on APRA/ADPPA
  specifically** in this corpus, as distinct from the broader claim that
  CPI has "some" advocacy presence (which is true, just on other bills).
  This sharpens rather than resolves the case's "advocacy-side presence"
  confirm/kill criterion — the coalition around APRA specifically may be
  entirely industry-side, with organized public-interest lobbying energy
  concentrated instead on KOSA and antitrust bills. Does not yet establish
  WHY (resource constraints? strategic prioritization? APRA seen as
  net-positive so no need to oppose it? not yet known) — needs a check of
  whether any advocacy org's PUBLIC statements (not LDA filings) supported
  or opposed APRA even without lobbying disclosure on it specifically.

## E4 — RELX Inc.: a single-company illustration of the say-vs-pay gap, sourced to individual filings

- **query/script:** ad hoc, run in a separate session via the
  `client-press-mention-gap` screen (newsroom.db screen id 39) and follow-up
  drilldown — not yet folded into `queries.sql`. Flagged here as a worked
  example for this case's still-open coalition-shape and press-thinness
  questions, not as a replacement for E1-E3's corpus-wide numbers.
- **result:** RELX Inc. (Senate clients `RELX INC`, `RELX INC.`, `RELX, INC.`
  — one collapsed entity, $6.64M total disclosed income 2022-2026Q1) is
  directly in this case's coalition: 28 distinct Senate filings across
  2022Q2-2024Q4 name APRA/ADPPA/American Privacy Rights Act/American Data
  Privacy and Protection Act by name in their activity description (zero in
  2025-2026, consistent with the bill's death after the canceled June 2024
  markup). `filing_uuid`s: `8b790642-e6fe-46cd-8a4b-51ab17e26eeb`,
  `f8842605-ca4a-4b20-9825-b68f7f0f7d8d`, `613832da-3e98-4076-a944-30b82f84f158`,
  `38f9d66d-b039-4b5b-80b6-8d12a44b97d0`, `c3cd155c-0108-437e-9506-169ff764a46d`,
  `588067e4-c9f3-48d4-9b3e-5879e8b37f33`, `b78404ab-b387-40e4-a2da-a7c9b9f79556`,
  `9912ea5a-2325-45d8-94ea-5d271e6407c8`, `dd2bf25e-c0fb-4e32-85d8-7b399d619471`,
  `b2146832-44c6-4e1d-a9e5-67219e7c0014`, `f6f27d04-3d3c-4f37-bd38-6d05e236581c`,
  `04a210c1-597d-474d-8886-acc3f1241a88`, `94250adc-da3d-454a-85b6-4ae5ea9b22fe`,
  `53257dd2-070a-4ddd-a477-812da794ee25`, `818e415a-a881-4612-9be8-39af86c23ef4`,
  `5788daba-23d6-4edd-98c1-b3035e6dd659`, `79594f79-5597-435a-9b14-3da6280b9c7a`,
  `93b287c9-213b-4bbb-bbfa-a5b192995b3a`, `42ac0c6e-ae81-42d8-952c-c78899a0f182`,
  `9b6e0835-50d8-40f8-8218-45ac61cf62f9`, `4bc14151-98e3-47db-b260-36e064930ac5`,
  `a570a691-f778-4375-8804-03c6d2a410eb`, `35bd9908-e84a-4204-a62e-2bfbd80a32f9`,
  `f63db9f1-1337-4fd3-9d6a-3b922c61ca7a`, `ace72933-00b4-4996-b20d-5255144a2fec`,
  `338d7ba0-71f3-4e54-9f6e-a6992a222c8a`, `eedd9f04-6638-4128-a8c5-b404a1de3e16`,
  `552d35f4-5f6e-4751-9d04-31fda96635e7`.

  RELX's own filings never mention "RELX" and are never named in any
  congressional press release under any known RELX brand (Elsevier,
  ThreatMetrix, Reed Exhibitions all checked, all zero). A separate,
  much smaller registered filer — LexisNexis Risk Solutions FL Inc.
  ($150K total income, below this case's/the screen's entity threshold,
  not part of the 101-client E1 count) — IS named, critically, in 5 press
  releases: `release_id` 63144 (Blake Moore, 2024-05-13), 70713 (Ron Wyden,
  2024-07-26, driver-data-broker sales), 88430 (Darin LaHood, 2025-02-13),
  129694 (Lauren Underwood, 2025-12-23, ICE detainee tablet data access),
  135456 (Josh Hawley, 2026-02-11, fraud/dark-money data web) — full URLs
  in the session transcript, not yet copied into this file.

  RELX Inc. also files LD-203 contributions: $428,609.16 across 163 items,
  2022-03-21 to 2025-12-04, to a bipartisan mix of party campaign
  committees (DSCC and NRSC $45K each), leadership PACs (Blue Dog, New
  Democrat Coalition, Republican Mainstreet Partnership), and ~90 named
  individual members at `honoree_member_map` confidence 0.6-1.0. Cross-
  referenced against `member_committees`: a disproportionate share of
  named honorees sit on committees with direct jurisdiction over RELX's
  own lobbying topics — Senate Judiciary's Intellectual Property (4) and
  Privacy, Technology, and the Law (3) subcommittees; House Judiciary's
  Courts, IP, AI, and the Internet subcommittee (4); Senate/House Energy
  and Commerce including Communications and Technology (6) and Health (6)
  subcommittees; Senate Finance and House Ways and Means including their
  Health Care subcommittees (11, 10, 8 respectively) — matching RELX's two
  disclosed lobbying tracks (Elsevier copyright/AI via AVOQ/Brownstein
  Hyatt/Klein Johnson, ~$2.7M; and privacy/data-broker/Medicaid-eligibility
  policy via Health Policy Source/Venable/CGCN, ~$2.6M, Health Policy
  Source being RELX's single largest registrant at $1.45M).

  Checked for overlap: none of the 5 members who criticized LexisNexis by
  name in press releases (Moore, Wyden, LaHood, Underwood, Hawley) appears
  as an RELX honoree at any confidence level. Clean negative result — rules
  out both a "paying off critics" and a "conspicuously avoiding critics"
  reading; the two groups are simply disjoint in this data.
- **source records:** all `filing_uuid`s above for the APRA-naming
  activities; `release_id`s 63144/70713/88430/129694/135456 for the press
  side; contribution-side `filing_uuid`s not yet individually pulled (163
  items across the registrant's contribution filings) — needed before this
  becomes a cited dollar-figure claim rather than a directional one.
- **caveats:** single-company illustration, not a coalition-wide claim —
  this is one client out of the case's 101, chosen because a separate
  session had already drilled into it, not because it was sampled
  systematically or is known to be representative. The committee-overlap
  finding is descriptive, not evidentiary of anything improper: sitting on
  a relevant committee and receiving industry contributions is normal,
  common practice for exactly the companies with business before that
  committee, not unique to RELX. The link between RELX Inc.'s privacy
  lobbying and LexisNexis Risk Solutions' separate small filing/press
  mentions is corporate-family adjacency, not proven coordination — they
  are distinct LDA registrants. Money to committees-of-jurisdiction is
  a pattern worth checking across the other 100 clients before treating it
  as a coalition-wide finding.
- **verdict:** not yet a corpus-wide claim — logged as a worked single-
  entity example that surfaces this case's next real question directly:
  **what does the full 101-client coalition's contribution/committee
  pattern look like, and is RELX's committee-targeting typical or unusual
  within it?** See `log.md` 2026-07-06 entry and the new open item below.

## E5 — Full roster read: position language is almost entirely absent

**Interim result, on the superseded 71-entity roster — to be overwritten in
place (not appended as a new E-number) once re-run against the full
345-entity roster (`derived/roster_corrected_deduplicated.csv`).** When that
happens, delete `analysis/build_roster.py` and `derived/roster_deduplicated.csv`
— nothing should cite the 71-entity roster once E5 covers the full one.

- **query/script:** `queries.sql#q4`, `#q5`; `analysis/build_roster.py` →
  `derived/roster_deduplicated.csv`.
- **result:** read all 509 CPI-scoped activity descriptions entity-by-entity
  (293 distinct after dedup). The overwhelming majority — including large
  repeat filers like Microsoft, Meta, Salesforce, SAP, IBM, Workday — use
  pure disclosure boilerplate ("issues related to X," a bill number with no
  adjective attached). A keyword scan for oppose/support/preemption/
  private-right-of-action language, read in context, turned up genuine
  bill-specific position language for only **2 entities**:
  - **Software & Information Industry Association (SIIA):** names its
    focus within "ADPPA and other privacy legislation" as *"private rights
    of action, prohibited data practices, and First Amendment-related
    issues"* — the one place in the roster where a specific contested
    provision (private right of action) is named, not just the bill.
  - **American Advertising Federation:** the only client reading as an
    explicit position statement — "Support legislation that would create a
    national privacy law... Oppose legislation that would overly restrict
    the responsible use of data for advertising," naming APRA as "support
    in part, oppose in part."
- **caveats:** Senate-only; House-side roster (~87 raw client names) not
  reconciled. Silence from the other entities is expected, not informative
  — LDA requires naming the bill lobbied on, not stating a stance.
- **verdict:** **LDA activity text alone cannot resolve "unified coalition
  vs. multi-faction split."** The 2 entities that do disclose a position
  both point the same direction (qualified support for a federal standard,
  resistance to private-right-of-action) — not a coalition split, but too
  thin a sample to characterize the other ~340 entities. Resolving
  coalition shape further needs outside sources (comment letters,
  testimony, trade press), not more corpus reads. **Not yet re-run** on the
  ~274 entities E6 added to the roster.

## E6 — Scale baseline: is this coalition unusually large? Corrected count and verdict

- **query/script:** `queries.sql#q6`–`#q7`; `analysis/build_corrected_roster.py`
  → `derived/roster_corrected_deduplicated.csv`.
- **method:** E1's original count (101) was a raw `senate_clients.id` count,
  not distinct companies, and was also scoped to `general_issue_code =
  'CPI'` only. Two problems, corrected together: (1) APRA/ADPPA is
  disclosed under 15+ issue codes, not just CPI — Consumer Issues (CSP)
  alone has more matching activity than CPI does, so a CPI-only filter
  misses real, focused engagement (Zillow, State Farm, Yahoo, Interpublic,
  and others, confirmed by spot-check). (2) Dropping the issue-code filter
  with no other control overcounts worse — large filers often bury one
  bill-name mention inside a single annual filing that lists 50+ unrelated
  bills (some over 20,000 characters), pulling in irrelevant filers like
  American Airlines or the ACLU. The fix: match on any issue code, but
  require `length(description) < 600` to keep only focused mentions
  (verified this cutoff against samples on both sides), then manually
  deduplicate name variants (corporate-suffix punctuation, "formerly"/"fka"
  aliases, spelled-out vs. abbreviated names, DBA variants — same method as
  a manual roster read, not just mechanical regex normalization, which
  misses aliases like "TECHNET" vs. "TECHNOLOGY NETWORK AKA TECHNET").
- **result (superseded 2026-07-08, see "E6 corrected" below):** **345
  distinct entities, 2,545 Senate lobbying activities**, 2022–2026.
  Compared against the same corrected method applied to three other bills
  over the same window:
  | Bill | Activities | Entities |
  |---|---|---|
  | **APRA/ADPPA family (this case)** | **2,545** | **345 (verified)** |
  | KOSA (Kids Online Safety Act) | 1,292 | ~149 (mechanical estimate) |
  | AICOA/Open App Markets Act (antitrust) | 902 | ~104 (mechanical estimate) |
  | RESTRICT Act | 99 | ~24 (mechanical estimate) |

  **APRA/ADPPA is the largest coalition of the four compared bills** — both
  by activity count and distinct-entity count.
- **source records:** counts only at this stage — individual `filing_uuid`s
  not yet pulled (next step if a specific figure becomes a cited claim).
  `derived/roster_corrected_deduplicated.csv` has the full 345-entity
  roster with merged variant lists.
- **caveats:** the 600-character cutoff is an empirical heuristic, not a
  principled threshold — exact entity counts could shift modestly under a
  different cutoff, but the ranking (APRA largest) is robust given the 2x+
  margin over second-place KOSA. KOSA/AICOA/RESTRICT's entity counts are
  still mechanical-normalization estimates (upper bounds), not manually
  verified the way APRA's is — a real number for those three is still
  open. The underlying keyword-match method can still undercount any of
  the four bills where a registrant describes legislation generically
  without naming it.
- **verdict (superseded):** **APRA/ADPPA's coalition (345 entities) is the
  largest of the four bills compared** — this was the case's headline
  scale figure until 2026-07-08, when the skeptic pass (E16) found the
  underlying filter contaminated by an unrelated bill (H.R. 1165, "Data
  Privacy Act of 2023"). **Superseded by the corrected figure below.**

### E6 corrected (2026-07-08, post-E16 filter fix)

- **query/script:** `analysis/build_corrected_roster.py`, re-run after
  removing the bare `%data privacy act%` clause from its `QUERY` constant
  (see E16 for the contamination finding and confirmation).
- **result:** **319 distinct entities (deduplicated), 371 raw client
  names, 1,950 Senate lobbying activities**, 2022–2026 — down from 345
  entities/399 raw names/2,545 activities (a ~25% reduction in activities,
  ~24% in raw client names, ~7.5% in deduplicated entities — H.R. 1165's
  contamination inflated activity *count* more than distinct-entity
  *count*, since the same contaminated clients often also had genuine
  APRA activity and stayed on the roster regardless). Full corrected
  roster: `derived/roster_corrected_deduplicated.csv` (regenerated
  2026-07-08, same script, overwrites the contaminated version — the
  file's git/derived history is not preserved separately, but the
  contaminated 345-count is recorded here and in E16 for the record).
  Top clients by activity count are unchanged in identity (DirecTV,
  Intuit, Yahoo, Comcast, Consumer Technology Association, Discovery
  Communications, American Honda Motor, Business Roundtable, Computer &
  Communications Industry Association, Interpublic Group) — the
  contamination did not concentrate in any one filer, consistent with
  E16's finding that H.R. 1165's own coalition (financial-sector/GLBA
  privacy) is a large, mostly-distinct set of filers, not a subset that
  happens to overlap heavily with APRA's top clients.
- **result — updated comparison table:**
  | Bill | Activities | Entities |
  |---|---|---|
  | **APRA/ADPPA family (this case, corrected)** | **1,950** | **319 (verified)** |
  | KOSA (Kids Online Safety Act) | 1,292 | ~149 (mechanical estimate, not yet re-checked for an equivalent contamination bug) |
  | AICOA/Open App Markets Act (antitrust) | 902 | ~104 (mechanical estimate, not yet re-checked) |
  | RESTRICT Act | 99 | ~24 (mechanical estimate, not yet re-checked) |

  **APRA/ADPPA remains the largest coalition of the four compared bills**
  — the ranking survives the correction (1,950 vs. KOSA's 1,292 is still
  a 1.5x margin, comfortably ahead) — but the margin is narrower than the
  original "2x+" framing implied, and KOSA/AICOA/RESTRICT's own counts
  have not been checked for the same kind of bill-name-collision
  contamination this correction just found in APRA's filter. Treat the
  *ranking* as solid and the *exact margin* as provisional until the other
  three bills get the same scrutiny.
- **caveats:** same 600-character-cutoff caveat as before (empirical
  heuristic, not principled) — applies independently of the E16 fix. The
  corrected 319/1,950 figures have not yet been independently re-verified
  by a second pass the way the original 345/2,545 were checked by the
  skeptic — this is the judge's own direct re-run, not a third-party
  re-check of the correction itself.
- **verdict:** **use 319 entities / 1,950 activities going forward, not
  345/2,545.** The core claim — APRA/ADPPA's coalition is the largest of
  the four compared bills — survives. The exact scale and margin over
  KOSA should be described as "roughly 1.5x KOSA's size, the largest of
  four compared bills" rather than "2x+ margin," pending a from-scratch
  contamination check on the other three bills' own filters.

## E8 — Position-language re-read on the full 345-entity roster: signal widens, but a filter artifact hides E5's own two headline entities

- **query/script:** `queries.sql#q8`, `#q8b`; `analysis/build_position_read.py`
  → `derived/position_read_candidates.csv`.
- **method:** re-ran E5's position-signal keyword scan (oppose/support/private
  right of action/preemption/preempt/concern/favor), this time against the
  full corrected roster's matching rows (any issue code, `length(description)
  < 600` — E6/E7's filter), not the superseded 71-entity CPI-only roster E5
  used. Read every matched description in full (not just the keyword
  fragment) to separate genuine bill-specific position language from
  boilerplate "support"/"concern" language attached to a *different* bill in
  the same laundry-list description.
- **result — the <600 filter itself excludes E5's own two findings:**
  American Advertising Federation's actual ADPPA position statement ("Favor
  legislation that would create a national privacy law... Oppose legislation
  that would overly restrict...") runs 780–1,038 characters across every
  filing year — every single AAF row is over the 600-char cutoff, so AAF
  drops out of this re-read entirely. SIIA's core CPI-issue-code ADPPA
  statement is 811 characters, also over the cutoff — SIIA survived this
  re-read only because one shorter cross-posted row under the EDU issue code
  (589 chars) happened to squeak under. **The cutoff, built in E6 to exclude
  omnibus 50-bill laundry lists, also silently excludes verbose single-bill
  position statements** — a filter artifact discovered by this re-run, not
  present in E5 because E5 hand-read the CPI-only text directly rather than
  re-deriving from the cutoff query.
- **result — under the &lt;600 filter, 36 raw client names (up from E5's 8)
  carry a position keyword co-occurring with a bill-name match.** Read
  through in full, genuine bill-specific position language (not generic
  reuse of "support"/"concern" for an unrelated bill in the same
  description) was found for:
  - **Alabama Farmers Federation** — outright: *"Opposed H.R. 8818, the
    American Privacy Rights Act"* (2024, `INS`).
  - **American Association for Justice** — support, specifically for
    *"Ensuring a private right of action in H.R. 8152"* (2022, `CSP`) —
    the opposite position from SIIA/AAF/ATPC on that specific provision.
  - **American Transaction Processors Coalition** — support H.R. 1165,
    *"specifically highlighting support for strong preemption and no
    inclusion of a private right of action"* (2023, `FIN`) — same direction
    as SIIA/AAF.
  - **California State Senate** — *"Advocated for elimination of preemption
    provisions from American Privacy Rights Act, HR 8818"* (2024, `CSP`) —
    a state legislature itself lobbying Congress against federal preemption
    of state privacy law; opposite direction from the industry preemption
    coalition.
  - **Chamber of Progress** — support H.R. 8818 (2024, `LAW`), alongside
    child-safety and NO FAKES Act bills; a tech-industry-funded advocacy
    group taking an explicit support position.
  - **Center for Freedom and Prosperity** — support H.R. 1165 (2023–2025,
    `BAN`), alongside opposing ESG-related DOL rules and interchange price
    controls — a free-market advocacy group's routine boilerplate list, but
    APRA/ADPPA support is explicit each year.
  - **Electronic Frontier Foundation** — **revises E3.** E3 concluded EFF
    was silent on APRA specifically (its CPI-only search found EFF engaged
    only on AICOA/Open App Markets/Cyber Incident Reporting). This broader,
    any-issue-code search finds EFF *does* file substantively on
    ADPPA/APRA — filed under the `CIV` issue code (civil rights), not `CPI`,
    which is why E3's CPI-scoped search missed it. 2023 filing: *"unintroduced
    American Data Privacy and Protection Act, provisions relating to
    privacy, preemption, private right of action"*; a longer 2022 filing
    (`q8b`, no length cutoff) confirms recurring, detailed ADPPA engagement
    across multiple years, naming specific provisions (biometric data on
    minors, student privacy) rather than boilerplate. No explicit
    support/oppose verb attached, but this is a real, substantive, and
    previously-missed advocacy-side presence on APRA specifically —
    **the "no organized public-interest voice engaged on APRA specifically"
    finding in E3 does not hold once the issue-code filter is dropped.**
  - **National Fusion Center Association** — flags *"potential public
    safety implications of American Privacy Rights Act"* for law
    enforcement (2024, `LAW`) — a distinct, law-enforcement-adjacent
    opposition angle not seen in the industry/advocacy split.
  - **SIIA** — unchanged from E5 (oppose, First Amendment/preemption/AI/
    private right of action).
  - Several others (Boys & Girls Clubs of America, Health Innovation
    Alliance, NRECA) show consistent multi-year re-filed support/engagement
    language but describe support for narrow carve-outs (nonprofit data
    protection, ERISA preemption context) rather than a position on the
    bill as a whole — read as adjacent-interest engagement, not a clean
    support/oppose stance.
  - The remaining ~24 of the 36 names are **false positives**: the keyword
    ("support," "concern," etc.) is generic boilerplate attached to a
    different bill in the same multi-bill description (e.g. Spotify's,
    TikTok's, and Sentry's rows all use "support"/"concern" for unrelated
    provisions elsewhere in the same filing, not for APRA).
- **result — dropping the length cutoff entirely (`q8b`) surfaces 103 raw
  client names**, but the great majority are large multi-bill omnibus
  filings (some over 20,000 characters, e.g. American College of Physicians,
  Chamber of Commerce, Competitive Carriers Association) where the keyword
  match is very likely attached to an unrelated bill in the list — this is
  exactly the overcount problem E6 built the cutoff to solve, and a full
  read of all 103 was not completed this session. A partial read of the
  600–2,500-char band (moderate-length, more likely single-topic)
  surfaced two more real hits: **Insights Association** (*"Support for
  comprehensive federal consumer privacy legislation and amendments to
  H.R. 8152... ADPPA"*, 2021–2022) and confirmed EFF's fuller multi-bill
  engagement; the rest of that band's ~39 names were boilerplate false
  positives on the same pattern as the &lt;600 band.
- **source records:** `derived/position_read_candidates.csv` — **regenerated
  2026-07-08 post-E16 filter fix: 114 rows / 30 distinct raw client names
  (down from the original contaminated 222 rows/36 names)**. All entities
  named in this block's findings (SIIA, American Advertising Federation,
  Alabama Farmers Federation, American Association for Justice, American
  Transaction Processors Coalition, California State Senate, Chamber of
  Progress, Center for Freedom and Prosperity, Electronic Frontier
  Foundation, National Fusion Center Association, Insights Association)
  were checked against the corrected list and survive — the contamination
  removed generic H.R. 1165 "support"/"oppose" boilerplate rows, not any
  of this block's genuine APRA-specific position language. Individual
  `filing_uuid`s not yet pulled for the entities listed above with genuine
  position language — needed before any of these becomes an individually
  cited claim.
- **caveats:** this is still a keyword scan, not exhaustive reading of all
  345 entities' full text — silence from the ~330 entities not flagged by
  a keyword hit is expected (LDA doesn't require a stated position) and
  remains uninformative on its own, per E5's original caveat. The &lt;600
  filter's exclusion of AAF/SIIA's real statements is a **method warning
  for any future use of the corrected roster's cutoff for text analysis**,
  not just a scale-count tool — flag this in `docs/` or the investigation
  skill if it recurs. The 103-name no-cutoff list is not fully read; the
  omnibus-filing overcount risk there is real and unresolved.
- **verdict:** **the coalition is not unanimous — at least two clear
  fault lines exist**, though still described by too few entities to call
  it a structured "split": (1) **private right of action** — American
  Association for Justice supports it, SIIA/ATPC oppose it, matching a
  predictable trial-lawyers-vs-industry line; (2) **state-law preemption**
  — the industry coalition (SIIA, ATPC, and by implication most trade
  associations) wants federal preemption of state privacy laws, while
  California's state senate explicitly lobbied to strip preemption from
  HR 8818, a state-vs-federal-authority fault line distinct from the
  industry-vs-consumer-advocate line. **E3's "no organized public-interest
  voice on APRA specifically" finding is revised, not confirmed** — EFF is
  substantively engaged, just findable only via a broader issue-code net
  than E3 used. This still falls short of proving the *345-entity* coalition
  splits into organized blocs (only ~10 entities show any real position
  language after read-through, out of 345) — but it moves the case from
  "no signal beyond 2 aligned entities" (E5) to "a real, if thin, multi-
  sided fault-line structure exists and is discoverable in this corpus,
  just not exhaustively mapped."

## E9 — Roster-wide say-vs-pay: reused the client-press-mention-gap screen's alias infrastructure, partial coverage

- **query/script:** `analysis/build_press_mention_join.py` →
  `derived/press_mention_join.csv` (raw-name grain),
  `derived/press_mention_join_by_entity.csv` (entity grain, rolled up).
  Reuses `derived_client_alias_index` and `derived_client_press_mentions`
  (built by `scripts/build_derived_client_alias_index.py` /
  `build_derived_client_press_mentions.py` for the unrelated
  `client-press-mention-gap` screen, `screens/client-press-mention-gap/
  screen.sql`) rather than rebuilding entity-name matching from scratch.
- **method:** the editor asked whether any of the 345-entity roster shows up
  in congressional press by name — same say-vs-pay bridge E4 hand-built for
  RELX alone, now attempted at roster scale. Rather than a fresh bulk
  substring match (rejected in this session's earlier discussion — several
  roster names are common English words/short brand names with heavy
  collision risk, e.g. Visa, Apple, Block, Target, HP), checked for reusable
  prior work first: `derived_client_alias_index` already holds an
  LLM-reviewed alias/generic-flag table for Senate clients with ≥$1M total
  disclosed income 2022–2026Q1 (5,336 rows, 2,352 canonical entities), and
  `derived_client_press_mentions` already holds precomputed FTS
  phrase-match hits against that alias set (35,425 mentions, 1,010
  entities). Joined the roster's 399 raw client names against both tables
  by exact `canonical_name` match. For the subset with a usable
  (`status='candidate'`) alias but no precomputed mentions yet (14 names —
  apparently added to the alias index after the mentions table was last
  built), re-ran `build_derived_client_press_mentions.py` fresh — a
  mechanical FTS rebuild, no new LLM calls, idempotent (confirmed: rebuild
  produced the identical 35,425-row/1,010-entity count as before the
  rebuild, so nothing outside this session's scope was disturbed).
  **Per editor instruction, stopped there — did not hand-roll alias review
  for the ~256 raw names below the $1M threshold that have never been
  reviewed at all; that is explicitly out of scope for this pass.**
- **result — coverage:** of 399 raw client names (345 deduplicated
  entities), 99 raw names (92 entities) have a usable reviewed alias; 44
  raw names were previously flagged too-generic-to-match (no data);
  256 raw names (233 entities) were never reviewed (out of scope this
  pass, per instruction). Of the 92 entities with a usable alias, 81 have
  at least one press mention.
- **result — a real finding, but the #1 entity by mention count is a
  collision false positive.** By raw mention count: VISA (1,149 mentions,
  291 distinct members) >> TikTok Inc. (544) > Amazon.com Services (321) >
  Intel (263) > Microsoft (195) > General Motors (160) > American Heart
  Association (151) > ByteDance (150) > Verizon (113) > AIG (105) >
  National Retail Federation (105)... **Manually sampled 15 of VISA's 1,149
  matched releases: 15/15 are about immigration visas or visa-fraud policy,
  zero are about Visa Inc. the payments company.** The alias index's own
  prior review is inconsistent here: `VISA, U.S.A., INC.` was correctly
  flagged `rejected_too_generic`, but `VISA, INC.` — the raw name this
  roster's own dedup script (`build_corrected_roster.py`) actually uses —
  was left as `candidate` with bare alias "VISA," and was never caught.
  **This is a real bug in the reused table, discovered by this join, not
  introduced by it** — flag for `client-press-mention-gap`'s own case file
  too, since its screen ranks by the same contaminated count. TikTok,
  Amazon, Intel, Microsoft, GM, and American Heart Association's top hits
  were spot-checked and look clean (genuinely about those entities).
- **result — 14 reviewed entities with zero press mentions**, by lobbying
  volume: American Property Casualty Insurance Association (33 lobbying
  activities), LiveRamp (19), Amazon.com Services (19 — note: this row is
  the `INC.` raw-name variant; the `LLC` variant has 321 real mentions
  rolled into the entity total, this is a within-entity name-split
  artifact not a real Amazon-specific zero), Twilio (14), Aflac (10),
  Swiss Re (8), OneMain Financial (8), Dapper Labs (6), American
  Transaction Processors Coalition (6), Medtronic (3), JM Family
  Enterprises (3), Acxiom (3), Deutsche Bank USA (1).
- **source records:** `derived_client_press_mentions.release_id`/`url` for
  every matched mention (already carries `press_releases.url`); roster
  entity ↔ raw name mapping in `derived/roster_corrected_deduplicated.csv`.
  VISA's specific matched releases not yet individually pulled for a
  citation list (not needed — this is a negative/bug finding, not a claim
  to cite).
- **caveats:** covers only 92 of 345 entities (27%) — the reviewed subset
  skews toward the roster's larger, more prominent filers (same $1M
  income-threshold bias as the underlying alias index), so absence of
  press coverage among the *unreviewed* 233 entities cannot be assessed at
  all from this pass, and presence/absence patterns here should not be
  extrapolated to the full 345 without the excluded ~256 raw names.
  "Mentioned by name" still means "did a member say this company's literal
  name," not "did a member discuss this company's lobbying position" —
  same caveat as E4 and the client-press-mention-gap screen itself. The
  VISA bug means any future reuse of `derived_client_alias_index`/
  `derived_client_press_mentions` for a ranking or "top mentioned entity"
  claim must re-verify each high-count entity's aliases are genuinely
  unambiguous, not just trust the existing `status='candidate'` flag —
  this review pass had a real gap.
- **verdict:** **the say-vs-pay pattern E4 found for RELX (heavy lobbying,
  no press mentions of the lobbying entity) does not hold uniformly across
  the reviewed subset of the coalition** — most of the roster's largest,
  most recognizable filers (TikTok, Amazon, Intel, Microsoft, GM, Verizon,
  AIG) get substantial press mentions, though for reasons that may be
  unrelated to APRA lobbying specifically (TikTok's volume is almost
  certainly driven by the separate foreign-adversary-ownership fight, not
  privacy). The 14 zero-mention entities among the reviewed set are a
  cleaner, smaller RELX-style candidate list if that pattern is worth
  pursuing further. **Not yet a full-coalition finding** — the majority of
  the roster (256 of 399 raw names) remains unreviewed and out of scope
  until the editor authorizes extending review to smaller filers.

## E10 — Which members got the most APRA-related press coverage, and what did they receive from the coalition?

- **query/script:** ad hoc (see `log.md` 2026-07-08 third session); ranking
  derived from `derived/apra_press_releases.csv` (62 rows: 19 exact
  bill-name matches + 13 fork-verified on-topic finds from the E2 revision,
  UNVERIFIED broad-phrase-only rows excluded). Contribution join:
  `analysis/build_top4_contributions.py` → `derived/top4_member_contributions.csv`.
- **result (superseded numbers, corrected 2026-07-08 post-E16 — pattern
  unchanged):** top 4 members by confirmed on-topic APRA press-release
  count: Schakowsky (10), Trahan (6), Moran (3), DelBene (2). Joined
  against LD-203 contributions from registrants tied to an APRA-matched
  Senate filing for a roster client (same registrant-scoping method as
  E4): DelBene $1,009,040 (86 registrants) > Moran $689,775 (87) > Trahan
  $243,990 (49) > Schakowsky $169,990 (31) — **this inverts the press
  ranking**: the two members with the fewest press releases got the most
  money from this registrant set. **Corrected registrant set (E16 filter
  fix) gives**: DelBene $777,040 (72 registrants) > Moran $630,275 (78) >
  Trahan $166,990 (43) > Schakowsky $97,490 (29) — same inversion, same
  ranking, dollar totals down ~20-30% (H.R. 1165-linked registrants
  correctly dropped from the roster). **Use the corrected figures going
  forward.**
- **caveats:** roughly half these rows (124/253, pre-correction count) are
  third-party lobbying firms (e.g. Brownstein Hyatt, K&L Gates), not the
  roster company itself — LD-203 filings have no client field, so a
  third-party firm's giving can't be attributed to any one of its named
  clients' motive. See E11 for the in-house-only re-cut that fixes this.
- **verdict:** press-release volume and contribution-receipt volume do not
  correlate for these 4 members — not evidence of anything by itself
  (different mechanisms, different actors within "the coalition"), but it
  rules out a naive "more money = more public statements" reading. Holds
  after the E16 filter correction.

## E11 — Same 4 members, in-house registrants only (exact-date contribution items)

- **query/script:** `analysis/build_top4_inhouse_timeline.py` →
  `derived/top4_inhouse_contribution_timeline.csv`.
- **method:** restricts E10 to registrants where the registrant IS the
  roster client (company lobbies for itself) — the only case where "this
  entity lobbied on APRA" and "this entity gave this contribution" are the
  same legal person, editor-requested after the third-party-firm
  attribution problem was raised.
- **result (superseded numbers, corrected 2026-07-08 post-E16 — pattern
  unchanged):** 513 individual items. DelBene $693,300 (280 items) >
  Moran $392,750 (136) > Schakowsky $119,250 (48) > Trahan $101,500 (49)
  — same inverted pattern as E10, holds after removing the attribution-
  ambiguous half of the data. One negative item: a DelBene/Aflac -$2,500
  refund/correction, 2025-10-20 (`filing_uuid` in the CSV). **Corrected
  (E16 filter fix): 387 individual items across 156 in-house registrants.
  DelBene $480,800 (218 items) > Moran $333,250 (116) > Trahan $47,500
  (28) > Schakowsky $46,750 (25)** — same ranking, same inversion of the
  press ranking, dollar totals down ~30-50% per member (fewer, cleaner
  in-house registrants after H.R. 1165-linked ones drop out). **Use the
  corrected figures going forward.**
- **verdict:** confirms E10's pattern is not a third-party-firm artifact.
  Holds after the E16 filter correction — the ranking and inversion are
  unchanged, only the underlying registrant set and dollar totals shrank.

## E12 — Timeline chart: contributions vs. press releases vs. bill milestones, 4 members

- **query/script:** `analysis/build_top4_timeline_chart.py` →
  `derived/top4_timeline_chart.png`.
- **result:** visual timeline, one lane per member (contribution circles
  sized by amount, press-release triangles, 5 bill-milestone reference
  lines). Bill milestone dates web-sourced 2026-07-08 (NOT corpus
  evidence): ADPPA introduced 2022-06-21; APRA discussion draft released
  2024-04-08 (matches Schakowsky's/Castor's corpus press-release dates
  exactly); APRA formally introduced 2024-06-25; markup canceled ("killed")
  2024-06-27; 118th Congress ends/bill expires 2025-01-03.
- **caveats:** eyeball-only at this resolution — no visible spike or gap in
  contribution timing around any milestone for any of the 4 members. Named
  as a first-pass exploratory chart, not a statistical test (see E13/E14,
  which is where an actual test found something).
- **verdict:** no aggregate 4-member contribution-timing signal around bill
  milestones — the case's contribution-timing thread moved to (a) checking
  for a recurring calendar artifact (found: a routine holiday-season giving
  lull, present every year 2022-2025, not APRA-specific — logged in
  `log.md`, not its own evidence block since it's a null/artifact finding)
  and (b) the kill-decision-specific check in E13.

## E13 — Contributions to the reported kill-decision-makers vs. the bill's own sponsors

- **query/script:** `analysis/build_kill_decision_contributions.py` →
  `derived/kill_decision_contributions.csv`.
- **method:** a 2026-07-08 web search (non-corpus) found specific reporting
  (The Hill, IAPP, Foley & Lardner — see `log.md`) that Speaker Mike Johnson
  (`J000299`) and Majority Leader Steve Scalise (`S001176`) arranged a
  leadership meeting the night before the June 27, 2024 markup that
  excluded committee chair Cathy McMorris Rodgers (`M001159`) — APRA's own
  lead House GOP sponsor — and used it to block the bill over her
  objection. Checked in-house (E11-style) contributions from APRA-lobbying
  registrants to Johnson, Scalise, Rodgers, and Sen. Maria Cantwell
  (`C000127`, the discussion draft's Senate co-author, added as a second
  contrast case since Rodgers' data turned out to be confounded — see
  below).
- **result (superseded numbers, corrected 2026-07-08 post-E16 — pattern
  unchanged) — totals and share of each person's own in-house giving:**
  Johnson $672,283 (68% of his total in-house-registrant giving); Scalise
  $780,700 (84%); Rodgers $516,000 (66.5%, but see caveat); Cantwell
  $45,700 (46%). **Corrected (E16 filter fix, 156 in-house registrants,
  487 items): Johnson $606,783 (142 items), Scalise $639,700 (146),
  Rodgers $455,500 (173), Cantwell $30,700 (26).** Share-of-total-giving
  percentages were a manual follow-up calculation in the original session
  (comparing each person's APRA-linked total against their full
  ALL-registrant giving) and have not been re-derived against the
  corrected totals — needed before an exact percentage is cited, but the
  **qualitative pattern (no separation between blockers and sponsors)
  holds** on the corrected raw totals: all four remain in the same
  overlapping-donor-pool pattern, no outlier separates Johnson/Scalise
  from Rodgers/Cantwell in a way that tracks their reported position on
  the bill.
- **result — Rodgers' contribution data is confounded, not usable as a
  clean contrast:** her APRA-linked giving **tapers** after her Feb 8,
  2024 retirement announcement — corrected month-by-month check (E16/
  skeptic pass) shows Feb 2024 still at $93,500/35 items, declining
  through March before trailing off, not an abrupt cutoff as originally
  described. This still fully explains the pattern (retiring members'
  PAC pipelines dry up on announcement) and has nothing to do with APRA —
  **do not cite Rodgers' post-Feb-2024 decline as evidence of anything
  APRA-related, and use "tapers"/"declines," not "stops abruptly," when
  describing it.**
- **result — Cantwell's timing shows no gap around the markup cancellation**
  (steady giving through 2024-06-18, into Aug/Sep 2024 and 2025) — the
  opposite pattern from Rodgers, consistent with Cantwell not being
  sidelined and continuing to work the issue afterward (she reintroduced a
  privacy bill 2026-03-26, `release_id` 140868, already in
  `apra_press_releases.csv`).
- **verdict:** **no contribution signal distinguishes the people who
  blocked the bill from the people who championed it.** Everyone checked —
  both reported blockers and both sponsors — draws from the same large,
  overlapping donor pool, in proportions explained by institutional role
  (House leadership vs. rank-and-file, House vs. Senate), not position on
  APRA. This closes out the "money bought the kill decision" hypothesis as
  tested and not supported. **Holds after the E16 filter correction and
  the skeptic's independent re-derivation** (see E16) — corrected totals
  are lower across the board but the pattern (no separation) and the
  Rodgers-retirement explanation are unchanged; only the "abrupt cutoff"
  wording needed fixing.

## E14 — Lobbying activity (not money) spikes at drafting-stage moments, and is industry-dominated

**CORRECTED 2026-07-08 (post-E16 filter fix). The "22x" and "2.2x,
single-highest-quarter" figures below are superseded — see "E14
corrected" for the clean numbers and the restated finding. Keep the
original write-up for the record (it's what a second reader would have
seen before the skeptic caught the contamination), but do not cite the
22x/2.2x/"single highest quarter" figures going forward.**

- **query/script:** `analysis/build_drafting_stage_spike.py` →
  `derived/drafting_stage_spike.csv` (quarterly counts),
  `derived/drafting_stage_spike_composition.csv` (per-quarter client list
  + industry/non-industry classification).
- **method:** editor asked whether industry lobbying volume itself (not
  contributions) spikes around drafting-stage moments, prompted by a Wired
  article's framing (Dell Cameron, "Surprise! The Latest 'Comprehensive' US
  Privacy Bill Is Doomed" — prior coverage, not evidence, see `case.md`)
  that APRA was "engineered to appease conservative lobbyists representing
  the interests of big business." Pulled APRA-matched Senate lobbying
  activity by quarter (same bill-name/ADPPA filter as E1/E6/E8) against the
  corpus-wide quarterly baseline (all Senate activities, no filter) to rule
  out a general Q2 filing-season artifact. Then classified every distinct
  client name in the two spike quarters and their immediately-preceding
  baseline quarters as industry (corporation/trade association) vs.
  non-industry (reusing E3/E8's advocacy-org list, extended by inspection).
- **result (superseded) — real, corpus-wide-baseline-checked spikes, not
  an artifact:** corpus-wide quarterly activity is flat (45,758-51,688 per
  quarter, all four years, ~13% band). APRA-matched activity is not:
  Q1 2022 → Q2 2022 (ADPPA introduced 2022-06-21) jumps 9 → 199 activities
  (22x); Q1 2024 → Q2 2024 (APRA discussion draft 04-08, formal
  introduction 06-25, markup canceled 06-27 — all three land in one
  quarter) jumps 139 → 304 (2.2x, and Q2 2024 is the single highest
  quarter in the full 2022-2026 series).
- **result (superseded) — both spikes are ~98-100% industry-composed,
  same as their baselines:** Q1 2022: 5/5 clients industry (100%).
  Q2 2022: 148/148 (100%). Q1 2024: 103/104 (99%, 1 non-industry: David's
  Legacy Foundation). Q2 2024: 223/228 (98%, 5 non-industry: David's
  Legacy Foundation, Susan B. Anthony List, Brennan Center for Justice,
  Planned Parenthood, Public Knowledge — the only one of the 5 that's core
  privacy-advocacy adjacent is Public Knowledge; the rest are reproductive-
  rights or general civil-liberties groups likely engaged on a different
  angle, not confirmed as APRA-specific advocacy). No single entity
  dominates either spike quarter (max 4-5 activities out of 199-304,
  spread across 148-228 distinct clients) — this is a breadth phenomenon
  (many industry entities each filing once or twice that quarter), not a
  handful of big players.
- **caveats:** the non-industry classification is a manual read-through of
  ~230 names per quarter (four quarters checked) — see the skeptic
  spot-check in E16 (found 2 misclassifications, folded into the
  corrected re-run below). "Industry" here means corporation/trade-
  association by name pattern — it does not distinguish entities actively
  negotiating bill language from ones passively renewing a standing
  lobbying contract that happens to name the bill that quarter.
- **verdict (superseded):** ~~corroborates, rather than contradicts, the
  "industry shaped the bill's language" reading — lobbying activity spikes
  sharply and specifically at the two moments the bill's actual text
  became live, well above a flat corpus-wide baseline~~ — **the "22x" and
  "single highest quarter" framing does not survive the E16 filter fix.
  See "E14 corrected" below for the accurate pattern.**

### E14 corrected (2026-07-08, post-E16 filter fix + House-side replication)

- **query/script:** `analysis/build_drafting_stage_spike.py`, re-run after
  removing the bare `%data privacy act%` clause from `BILL_FILTER` and
  adding two entities (American Heart Association, American Association
  for Justice) to `NON_INDUSTRY_MARKERS` per the skeptic's spot-check
  (E16). House-side replication run as a separate ad hoc query, same
  clean filter, against `house_filings`/`house_activities`.
- **result — full clean quarterly series (Senate), 2022-2026:**
  Q1 2022=8, Q2 2022=199, Q3 2022=293, Q4 2022=288, Q1 2023=79, Q2
  2023=76, Q3 2023=70, Q4 2023=66, Q1 2024=72, Q2 2024=273, Q3 2024=241,
  Q4 2024=195, Q1 2025=30, Q2 2025=17, Q3 2025=18, Q4 2025=15, Q1 2026=10.
  Corpus-wide baseline unchanged (flat, 44,863-51,688 per quarter, ~15%
  band — a slightly wider band than the originally reported ~13%, still
  clearly flat relative to APRA-matched activity's 3-4x swings).
- **result — the "22x"/"2.2x, single-highest-quarter" claims do not
  survive.** Clean Q1 2022 (8) is near-zero because the bill did not
  exist yet — not a meaningful baseline quarter, so a ratio computed
  against it is not informative (8→199 is technically ~25x but this is an
  artifact of comparing against pre-bill noise, not a real base rate).
  More importantly: **clean Q2 2024 (273) is NOT the series' highest
  quarter** — clean Q3 2022 (293) and Q4 2022 (288) both exceed it. The
  real pattern is a **sustained elevated plateau across two multi-quarter
  windows** — 2022 H2 (Q2-Q4 2022, all in the 199-293 range, following
  ADPPA's June 2022 introduction and its July 20, 2022 committee markup)
  and 2024 H1-ish (Q2-Q3 2024, 273/241, following APRA's discussion
  draft/introduction/markup-cancellation) — roughly 3-4x above the
  pre-bill-attention baseline (72-79 in the low quarters of 2023-2024),
  not a single-event spike pinned to one precise quarter.
- **result — House-side replication (new, found by the skeptic, not run
  in the original E14):** House Q1 2024 → Q2 2024 = 70 → 267, a **3.81x**
  jump, essentially identical to the clean Senate ratio for the same
  window (72 → 273 = 3.79x). House Q3/Q4 2022 (283/280) also exceed House
  Q2 2024 (267), the same non-single-quarter pattern as Senate. House
  corpus-wide baseline is flat in the same band as Senate (45,681-47,692
  per quarter in 2022/2024). **This is a genuine, independent cross-
  chamber corroboration of the underlying phenomenon** (elevated
  drafting-stage lobbying activity, real and not an artifact) that the
  original E14 did not have — it strengthens the finding even as the
  precise "22x spike" framing is corrected away.
- **result — composition, corrected list, still ~97-99% industry:**
  Q1 2022: 4/4 industry (100%). Q2 2022: 147/148 industry (99%, 1
  non-industry: American Association for Justice — a correction from the
  skeptic's spot-check; not previously flagged). Q1 2024: 52/54 industry
  (96%, 2 non-industry: American Heart Association, David's Legacy
  Foundation). Q2 2024: 198/205 industry (97%, 7 non-industry: David's
  Legacy Foundation, Susan B. Anthony List, American Association for
  Justice, Brennan Center for Justice, American Heart Association,
  Planned Parenthood, Public Knowledge). The qualitative finding —
  overwhelmingly industry-composed, breadth not concentration — is
  unchanged; the precise percentage moved from ~98% to ~97-99% depending
  on quarter, within the range the original caveat already anticipated.
- **source records:** `derived/drafting_stage_spike.csv` and
  `derived/drafting_stage_spike_composition.csv` regenerated 2026-07-08
  (same filenames, overwrite the contaminated version — the contaminated
  22x/2.2x figures are preserved above in this file and in E16 for the
  record). House-side replication numbers are ad hoc, not yet written to
  a derived CSV — do that before individually citing the House figures.
- **caveats:** all of E14's original caveats still apply (manual
  classification, corpus-wide not case-specific "industry" definition).
  New caveat: the "sustained plateau, not single spike" framing is itself
  an eyeball read of 17 quarterly numbers, not a formal changepoint or
  spike-detection test — a more rigorous statistical characterization
  (e.g., where exactly the elevated period starts/ends) has not been run.
- **verdict:** **the underlying phenomenon — industry lobbying activity
  elevated well above a flat baseline during the bill's two active
  legislative windows, and now cross-chamber replicated — survives and is
  , if anything, on firmer footing than before (House replication is new
  evidence the original case didn't have). But it should be reported as
  a sustained ~3-4x-elevated plateau across multi-quarter windows, NOT as
  a "22x spike" or "the single highest quarter tied to markup
  cancellation" — those specific claims were filter-contamination
  artifacts and do not survive.** Combined with E13 (no contribution
  signal at the kill decision) and E8 (industry-side fault lines match
  reported sticking points, though see the Wired-corroboration caveat in
  E16), the mechanism this case's data supports remains: industry
  lobbying's leverage operated through drafting-stage advocacy on bill
  text, sustained across the bill's active legislative periods, not
  through campaign contributions timed to a specific vote or decision.

## E15 — Checking Wired's named opposition organizations against this corpus's LDA data

- **query/script:** ad hoc, `senate_clients` name lookup + full-text
  (no length cutoff) search on the resulting client IDs for
  APRA/ADPPA bill-name mentions.
- **method:** the user supplied a Wired article (Dell Cameron, "Surprise!
  The Latest 'Comprehensive' US Privacy Bill Is Doomed," June 27, 2024;
  cited at `wired_source.md`) reporting that by the week of the
  markup cancellation, APRA had "lost the support of dozens of major
  privacy and civil liberties groups," naming specifically the ACLU,
  Center for Democracy & Technology (CDT), NAACP, Japanese American
  Citizens League, Autistic Self Advocacy Network, Asian Americans
  Advancing Justice, Access Now, Demand Progress, and Free Press Action —
  objecting to the removal of civil-rights and algorithmic-decision
  provisions. Checked each named organization against `senate_clients` (is
  it a registered Senate LDA filer at all?) and, where it is, searched its
  full activity-description text (no `length(description) < 600` cutoff,
  unlike E6/E8's roster-scale queries) for any APRA/ADPPA bill-name
  mention.
- **result:**

  | Organization | Registered Senate filer? | Lobbied on APRA by name? |
  |---|---|---|
  | ACLU | Yes | Yes — 6 quarters, Q2 2024–Q3 2025 |
  | Demand Progress Action | Yes | Yes — 3 filings, 2024 |
  | NAACP (2 entities) | Yes | No |
  | Free Press Action Fund | Yes | No |
  | Center for Democracy & Technology | No | — |
  | Autistic Self Advocacy Network | No | — |
  | Asian Americans Advancing Justice | No | — |
  | Japanese American Citizens League | No | — |
  | Access Now | No (name collision only — "Coalition for Access Now" in this corpus is an unrelated CBD/hemp-industry group) | — |

  Of the two organizations that do show APRA-specific activity, the
  content differs. **Demand Progress Action's** three 2024 filings (issue
  code `CSP`, 588–763 characters) are substantive and specific: *"American
  Privacy Rights Act[:] Establishes a federal privacy baseline for
  treatment of covered data,"* alongside FTC surveillance-rulemaking and
  data-broker issues. **ACLU's** six filings (issue code `CIV`,
  10,630–18,195 characters each) are large multi-bill omnibus lists; the
  APRA line reads *"H.R.8818-American Privacy Rights Act of 2024-Issues
  Lobbied: Privacy"* with near-identical wording repeated each quarter and
  no mention of the specific civil-rights or algorithmic-decision
  provisions Wired reports as ACLU's stated objection.
- **source records:** `senate_clients.name` = 'AMERICAN CIVIL LIBERTIES
  UNION' (and the Foundation/Inc. variants), 'DEMAND PROGRESS ACTION, INC',
  'NAACP EMPOWERMENT PROGRAMS, INC.', 'NAACP LEGAL DEFENSE & EDUCATIONAL
  FUND INC', 'FREE PRESS ACTION FUND' — `filing_uuid`s not yet individually
  pulled for citation.
- **caveats:** this checks presence/absence of Senate LDA registration and
  APRA-specific bill-name mentions only — it does not and cannot establish
  whether an organization engaged with Congress on APRA through channels
  that don't require LDA registration (e.g. the direct letter to E&C
  Democrats Wired quotes from, or member outreach below LDA's compensation/
  time thresholds). A "No" in the table above means "not found lobbying on
  APRA in this corpus," not "did not oppose APRA." House-side LDA data not
  checked (Senate-only, consistent with the rest of this case's lobbying
  work). This is a fact-check of what this case's existing coalition
  characterization (E3, E8) can and cannot corroborate against one outside
  source — it is not a claim about lobbying-disclosure law's scope or
  design.
- **verdict:** partially corroborates E8's revision of E3 — Demand
  Progress Action is a second organization (after EFF) with genuine,
  substantive APRA-specific lobbying language, found only because Wired
  named it as a check target rather than through this case's own
  name-pattern searches. ACLU's presence is real but disclosure-minimum;
  it does not capture the provision-level objection Wired reports. Six of
  the nine organizations Wired names are either not registered Senate LDA
  filers at all, or registered but not found lobbying on APRA specifically
  in this corpus.

## Open — not yet run

- ~~E14's drafting-stage spike is Senate-only — check whether the same
  quarterly spike pattern (and industry-dominated composition) holds on
  the House side.~~ **DONE 2026-07-08 (E16/E14 corrected) — House-side
  replicates at nearly the same ratio (3.81x vs. Senate's 3.79x, Q1→Q2
  2024).**
- ~~E14's industry/non-industry classification (~230 names × 4 quarters)
  was a single-pass manual read, not independently cross-checked by a
  second reader — worth a spot-check before this becomes a headline claim
  in the findings report.~~ **DONE 2026-07-08 — skeptic spot-checked a
  25-row sample, found 2 misclassifications (American Heart Association,
  American Association for Justice), folded into E14 corrected.**
- E15's org-by-org check used only Wired's named list. `maha-gras-capture`
  (a separate case) built and used a manually-curated 16-org verified
  public-interest/consumer-advocacy registrant list for a similar
  industry-vs-advocacy census on a different bill (GRAS reform) — worth
  cross-checking that list against APRA too, since it was built precisely
  because name-pattern searches (E3's original method here) missed
  industry-funded groups with advocacy-sounding names and vice versa.
- **NEW (from E16):** KOSA/AICOA/RESTRICT's own bill-name filters have not
  been checked for the same kind of contamination bug found in APRA's
  filter (a common bill-name phrase colliding with an unrelated bill) —
  needed before E6 corrected's "APRA is 1.5x KOSA" margin can be trusted
  precisely.
- Extend `derived_client_alias_index` review to the ~256 roster raw names
  below the $1M threshold (233 distinct entities) that E9 left out of
  scope — **do not start without editor authorization**, per 2026-07-08
  instruction (token cost concern from a prior over-broad review pass).
- Fix or flag the VISA/`VISA, INC.` alias bug in `derived_client_alias_index`
  itself (set to `rejected_too_generic`, matching `VISA, U.S.A., INC.`'s
  existing correct flag) — belongs to the shared `client-press-mention-gap`
  infrastructure, not just this case, since that screen's own ranking is
  also contaminated by the same bug.
- Read the remaining ~64 unread names in the 103-name no-cutoff list
  (`q8b`), and decide whether the omnibus-overcount risk there can be
  managed with a smarter per-entity filter (e.g. only the sentence/clause
  containing the bill-name match, not the full description) rather than a
  blunt character-count cutoff — E8's finding that the existing cutoff
  hides AAF/SIIA's real language means the character-cutoff approach
  itself may need to be replaced, not just re-tuned, before any further
  position-language work on this corpus.
- Pull `filing_uuid`s for the ~10 entities with genuine position language
  found in E8, before any of them becomes an individually cited claim.
- Check the ~274 entities E6 added to the roster that did NOT show up in
  E8's keyword scan at all — E8 covers the position-keyword subset, not
  a systematic pass confirming the rest are silent (expected but not yet
  explicitly re-confirmed post-E6's roster correction).
- Manually verify KOSA/AICOA/RESTRICT's entity counts with the same rigor
  as E6's APRA figure (currently mechanical-normalization estimates).
- E3's House-side check (Senate-only so far) and a check for advocacy
  orgs not caught by the original name-pattern search.
- Whether any advocacy org's public statements (outside LDA filings)
  addressed APRA even without a lobbying disclosure naming it.
- Press-release baseline for E2 (how many member releases does a
  comparable bill typically draw) — not yet run.
- House-side roster (87 raw client names, not yet reconciled against the
  Senate 345-entity roster — needs its own fuzzy-match pass per this
  corpus's "House lobbyist/client records are name-only" caveat).
- Timeline of the June 27, 2024 markup cancellation and the bill's
  January 2025 expiration, cross-referenced against any spike/silence in
  Senate/House LDA activity or member press in that window.
- **From E4:** LD-203 contribution/honoree data and committee-overlap
  checks (like RELX's) for the rest of the coalition — does RELX's pattern
  hold across the coalition generally, or is RELX unusual? Real scope of
  work against 344 other entities, not a quick follow-up.
- Since lobbying-activity text can't establish coalition sub-faction
  structure beyond the 2 entities that disclosed a position (E5), is it
  worth pursuing outside sources, or should this criterion be marked
  not-answerable-from-this-corpus and the case narrowed to what E2/E4
  (press-visibility gap) can support?

## E16 — Skeptic re-derivation: shared bill-name filter contamination bug, and a House-side replication

- **query/script:** ad hoc, run by an independent skeptic agent
  (2026-07-08) re-deriving E14's spike query and E6's scale query directly
  against `gain.db`, then independently re-confirmed by the judge with a
  direct query against `senate_lobbying_activities` for rows matching
  `%data privacy act%` but none of the APRA/ADPPA-specific phrases.
- **method:** the case's shared 5-phrase bill-name filter (used by E1, E6,
  E8, E10-E14, defined in `queries.sql`) includes a bare
  `lower(description) LIKE '%data privacy act%'` clause. This also matches
  unrelated bills, typically sitting inside long multi-bill omnibus
  description fields. Re-ran E14's spike query and E6's scale query with
  contaminated rows excluded.
- **correction to this block's own "method" section, found by the judge's
  direct follow-up query (2026-07-08, same session):** the skeptic's report
  named H.R. 5807/S. 3065 as the primary contaminant. A full breakdown of
  all 810 contaminated Senate rows found the dominant contaminant is
  actually **H.R. 1165, "Data Privacy Act of 2023"** (a financial-sector/
  GLBA-adjacent bill, unrelated to APRA/ADPPA) — 789 of 810 rows (97%)
  contain an H.R. 1165 reference. H.R. 5807/S. 3065, S. 583, S. 3337, and
  a Wyden discussion draft account for the remaining 21 rows. Confirmed by
  direct query: dropping the bare clause entirely loses **zero** rows that
  also contain an actual APRA bill number (H.R. 8818, H.R. 8152) — the
  clause adds no true positives, only false ones, so the fix (drop it
  entirely, no partial exclusion list needed) is safe and simpler than
  the skeptic's original ad hoc exclusion approach.
- **result — E14's spike figures do not survive as originally stated:**
  clean Q1 2022 = 0 (bill did not exist yet, not a valid baseline quarter);
  clean Q2 2022 = 193; clean Q1 2024 = 71; clean Q2 2024 = 272. The
  "2.2x, single-highest-quarter" claim fails — clean Q3 2022 (287) and
  Q4 2022 (282) both exceed clean Q2 2024 (272). Real pattern: a sustained
  ~3-4x-elevated plateau across two multi-quarter windows (2022 H2, 2024
  H1), not a single-event spike at one precise quarter.
- **result — a genuine strengthening, found by the skeptic, not in the
  original case work:** independently replicated the clean pattern on the
  House side (previously flagged as an open, never-run item) — House
  Q1 2024 → Q2 2024 = 69 → 266, a 3.86x jump, almost identical to the
  clean Senate ratio (3.83x) for the same window. House baseline is flat
  in the same ~45,600-51,100 band as Senate. This is real cross-chamber
  corroboration that the original E14 did not have.
- **result — E6's scale figure is inflated ~25%:** clean estimate is
  ~1,918 activities / ~367 raw client names, vs. the reported 2,545/399.
  The ranking (APRA largest of 4 compared bills) likely survives — margin
  over KOSA's 1,292 remains comfortable even at the clean estimate — but
  KOSA's own count was not checked for the same contamination pattern in
  this pass, so the exact margin is less certain than "2x+."
- **result — E14's manual industry/non-industry classification, spot-
  checked:** a 25-row random sample of Q2 2024's 228 classified entities
  found 2 misclassifications (American Heart Association, American
  Association for Justice — both coded "industry," neither is a
  corporation or trade association in the sense the finding uses). Moves
  the composition estimate from ~98% to ~97% industry — does not change
  the qualitative finding.
- **result — the Wired-corroboration framing is less distinctive than
  written up:** American Association for Justice's preemption/private-
  right-of-action position (cited in E8 as matching Wired's reported APRA
  sticking points) is not APRA-specific — the same filings state the
  identical position on KOSA, verbatim ("Legislation related to forced
  arbitration, federal preemption issues... including the Kids Online
  Safety Act"). These are AAJ's standing institutional positions across
  any bill touching federal preemption of state consumer-protection law,
  not a discovery specific to APRA.
- **result — E13 wording check:** Rodgers' contribution timeline is a
  taper, not an "abrupt" stop — Feb 2024 still shows $93,500/35 items,
  declining through March before trailing off. Doesn't change the
  retirement-explains-it verdict, corrects the description.
- **source records:** re-derived directly from `senate_lobbying_activities`
  / `house_activities` description text; dominant contaminating bill:
  H.R. 1165 ("Data Privacy Act of 2023," 789/810 contaminated rows);
  minor contaminants: H.R. 5807/S. 3065, S. 583, S. 3337, an unrelated
  Wyden discussion draft. Individual `filing_uuid`s for the clean/
  contaminated split not yet pulled — needed before a corrected filter's
  output is cited row-by-row.
- **caveats:** KOSA/AICOA/RESTRICT comparison counts not re-checked for
  the same bug in this pass (flagged in the Open list).
- **RESOLVED 2026-07-08 (same session, judge action):** the bare
  `%data privacy act%` clause was removed from the shared filter at the
  source — `queries.sql` (all 6 occurrences) and all 7 analysis scripts
  that embedded the identical inline filter (`build_roster.py`,
  `build_position_read.py`, `build_drafting_stage_spike.py`,
  `build_kill_decision_contributions.py`, `build_corrected_roster.py`,
  `build_top4_inhouse_timeline.py`, `build_top4_contributions.py`) —
  fixed once at the source, not patched per-finding. E1, E6, E8, E10, E11,
  E13, and E14 were re-run against the fixed filter and updated in place
  above with "corrected" sub-blocks; `derived/roster_corrected_deduplicated.csv`,
  `derived/drafting_stage_spike.csv`, `derived/drafting_stage_spike_composition.csv`,
  `derived/position_read_candidates.csv`, `derived/top4_member_contributions.csv`,
  `derived/top4_inhouse_contribution_timeline.csv`, and
  `derived/kill_decision_contributions.csv` were all regenerated.
- **verdict:** confirms a real, previously uncaught data-quality bug
  affecting nearly every headline number in this case, but the underlying
  phenomena (elevated drafting-stage industry lobbying activity, no
  contribution signal at the kill decision, LDA's blind spot on the
  reported opposition) all survive independent re-derivation. One thread
  (House-side replication) comes back stronger than before. Judge's
  verdict (case.md): filter fixed at the source, affected evidence blocks
  re-run, headline numbers restated — not a refutation.

## E17 — No Q1 2026 plateau signal for the SECURE Data Act (H.R. 8413) — corpus coverage gap, not a negative finding about the bill

- **query/script:** ad hoc, run directly against `db/gain.db`. Not yet
  folded into `queries.sql`/`analysis/` — do that if this becomes a
  recurring check (e.g. re-run once Q2 2026 data is ingested).
- **method:** editor asked whether E14's revised "sustained plateau"
  methodology (corrected 2026-07-08, see E14 corrected) shows any early
  signal in Q1 2026 for the SECURE Data Act (H.R. 8413, "Securing and
  Establishing Consumer Uniform Rights and Enforcement over Data Act"),
  a new comprehensive federal privacy bill the editor identified as
  introduced in Q1 2026 (web-sourced correction, same session: actually
  **introduced April 22, 2026 — Q2 2026, not Q1** — see Prior coverage
  note below). Checked: (1) whether H.R. 8413 or "SECURE Data Act" appears
  in this corpus by name; (2) E14's clean APRA/ADPPA-family filter's tail
  through Q1 2026; (3) a broader "comprehensive/national/federal privacy"
  phrase search, any bill name, for a pre-introduction anticipation
  signal; (4) a targeted search for "secure" + "privacy" co-occurring in
  short (&lt;600 char), single-topic Q1 2026 filings, to catch any staff-
  level discussion-draft language that might predate formal introduction
  (the same anticipatory pattern APRA itself showed — Moran's April 2024
  discussion-draft statement, see E2 revision).
- **result — the bill does not appear in this corpus at all:** zero rows
  match "H.R. 8413," "secure data act," or "securing and establishing
  consumer" anywhere in `senate_lobbying_activities`. This is expected,
  not informative on its own: **the corpus's most recent data is 2026 Q1
  (24,347 Senate filings), and the bill was introduced April 22, 2026 —
  Q2 2026.** LDA quarterly filings are typically due ~20 days after
  quarter-end (Q2 2026 activity would be filed by ~July 20, 2026), so
  Q2 2026 lobbying activity naming this bill would not be expected in
  this corpus yet regardless of how much real lobbying is happening on
  it right now. **This is a corpus coverage-window gap, not a finding
  about the bill's lobbying volume.**
- **result — no pre-introduction anticipation signal in Q1 2026 either:**
  checked whether Q1 2026 shows an early uptick the way Q2 2022 and
  Q2 2024 followed real drafting-stage moments. It does not — the
  APRA/ADPPA-family filter's own Q1 2026 count (16 activities/15 clients)
  continues the same declining tail visible since Q1 2025 (40→26→26→19→16),
  consistent with a dead bill, not a rising signal. The broader
  "comprehensive/national/federal privacy" phrase search (any bill name)
  shows Q1 2026 at 43 activities, in the same 43-54 range as every
  quarter back to Q1 2025 — no uptick. A targeted search for short,
  single-topic Q1 2026 filings combining "secure" and "privacy" language
  (looking for possible discussion-draft anticipation, the same pattern
  Moran's April 2024 APRA statement showed) returned 7 rows, all name
  collisions with unrelated bills (SECURE Notarization Act, Secure Rural
  Schools, SAFE Banking Act) — zero genuine SECURE Data Act language.
- **caveats:** this is a single-quarter absence check, not a full
  replication of E14's methodology (which needs multiple quarters on
  both sides of an introduction date to establish a baseline and a
  plateau). It cannot distinguish "no lobbying activity yet" from "real
  lobbying activity exists but this corpus doesn't cover the quarter it
  would appear in" — those are different claims and this check only rules
  out the former for Q1 2026, not the latter for Q2 2026. House-side not
  checked (Senate-only, consistent with the rest of this case's lobbying-
  volume work). If SECURE Data Act lobbying becomes a story, this needs
  re-running once Q2/Q3 2026 Senate LDA data is ingested (Q2 2026 filings
  become public ~July 20, 2026; Q3 ~October 20, 2026) — the real test of
  E14's plateau methodology on this bill is whether Q2/Q3 2026 shows the
  same kind of sustained, corpus-baseline-checked elevation APRA showed
  at its own introduction, not whether Q1 2026 shows anything (it
  couldn't, given the corpus's coverage window).
- **verdict:** **no finding, positive or negative, can be made about the
  SECURE Data Act from this corpus yet** — the "no spike" determination
  from a prior session is technically correct (Q1 2026 shows nothing) but
  was checking a quarter that could not have shown a signal regardless of
  the bill's real-world lobbying activity, since the bill didn't exist
  until three weeks into Q2 2026. This is a data-coverage-window
  limitation, not a substantive result — do not cite "no Q1 2026 signal"
  as evidence the SECURE Data Act lobbying coalition is smaller or
  quieter than APRA's was at a comparable stage. **Correct next step:**
  re-run this same check (E14's clean filter + broader phrase search)
  once Q2 2026 Senate LDA data is available (~July 20, 2026) and compare
  against APRA's own Q2 2022/Q2 2024 introduction-quarter pattern.
