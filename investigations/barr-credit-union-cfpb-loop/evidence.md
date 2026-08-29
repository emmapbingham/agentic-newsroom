# Evidence — barr-credit-union-cfpb-loop

## E1 — The pair: $40k ACU money honoring Barr + endorsement-citing releases
- **query/script:** `queries.sql#q1` (screen run 36,
  investigations/screens/client-mention-honoree-triangle/screen.sql)
- **result:** deduped FECA honoring Barr from CUNA/ACU registrant: $40,000;
  3 press releases citing ACU: 2023-12-15 "Barr's Introduces UDAAP Reform
  Legislation", 2025-01-23 "Barr Reintroduces TABS Act to Bring
  Accountability to the CFPB", 2025-05-03 "Rep. Andy Barr Reintroduces Bill
  to Reform CFPB's UDAAP Authority".
- **source records:** releases
  https://barr.house.gov/press-releases?ID=B168D678-0C8F-4766-B711-1C51D5C74372,
  https://barr.house.gov/press-releases?ID=0BF254FA-1F21-4097-9427-787F8B587593,
  https://barr.house.gov/press-releases?ID=137CFE45-CC34-4094-9E40-1A491C1059A0
  (mention rows in derived_client_press_mentions carry release_id/url);
  contribution filings in E2.
- **caveats:** which release is which title needs the row-level join (q1b);
  "endorsement" characterization is from release text quoting ACU — re-read
  the exact quotes before publication. ACU exists as TWO alias entities
  (apostrophe variant) — E1 total is one entity's registrant; NAFCU-legacy
  registrant adds $6,000 (q3).
- **verdict:** supports

## E2 — The dated money timeline, incl. the day-one Senate pivot
- **query/script:** `queries.sql#q2`
- **result:** deduped items (date | amount | payee | filing_uuid):
  2022-09-12 $5,000 B.A.R.R. PAC (4774a561-a64a-4990-81c2-b2505cba6ec9);
  2023-03-28 $5,000 Barr for Congress (d7cd0f30-3895-4715-ada4-de3136c076bc);
  2023-09-13 $5,000 B.A.R.R. PAC (93624f0a-fdf4-45e7-913b-e4c2225e2108);
  2024-07-26 $5,000 + $5,000 campaign + B.A.R.R. PAC, same day
  (84a0158c-daed-4dd7-86df-d2e5efb5ca90);
  **2025-02-20 $5,000 "ANDY BARR FOR SENATE, INC."**
  (6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4) — the day McConnell announced
  retirement (NPR, 2025-02-20; outside record, context only);
  2025-02-28 $5,000 B.A.R.R. PAC (same filing);
  2025-12-15 $5,000 Barr for Senate (c19daac7-cd73-4fba-9a94-74508a609a96).
  All organization-filed. Verify any at
  https://lda.gov/filings/public/contribution/{uuid}/print/
- **caveats:** LD-203 `date` is as-reported by the filer (check date vs
  attribution date unknown); "Andy Barr for Senate, Inc." on 2025-02-20
  predates his formal April 2025 announcement — an FEC committee
  redesignation/timing check is REQUIRED before this detail is used;
  bill-introduction interleaving (Dec 2023, Jan 2025, May 2025) is from
  release dates, not Congress.gov — pull official introduction dates.
- **verdict:** supports (pending the two named verifications)

## E3 — Second credit-union registrant adds $6k
- **query/script:** `queries.sql#q3`
- **result:** NAFCU-legacy registrant ("NATIONAL ASSOCIATION OF
  FEDERALLY-INSURED CREDIT UNIONS (FKA...)"): $6,000 honoring Barr.
  Credit-union association total: $46,000.
- **source records:** via q3 filing_uuids.
- **caveats:** CUNA+NAFCU merged into America's Credit Unions (Jan 2024);
  treat as one interest after the merger, two before.
- **verdict:** supports (scale context)

## E4 — ACU honoree base rate: Barr is top-tier (rank 5 of 527), not median
- **query/script:** `queries.sql#q4` + `#q4b`/`#q4c` (run 2026-07-07)
- **result:** the CUNA/ACU registrant's deduped FECA footprint honors **527
  members** for **$6,208,500** total (mean **$11,781**, median ~**$10,000**,
  max **$50,000**). Barr's $40,000 ranks **5th of 527** (top ~1%, ~4x median).
  Top of the stack is Democratic leadership: Katherine Clark $50k, Hakeem
  Jeffries $45k, Maxine Waters $42.5k, Adam Schiff $41k, Adam Smith $40k,
  then **Andy Barr $40k**, Pete Aguilar $40k, Young Kim $39k. Barr is
  effectively ACU's #1 House Republican and among the very top of Financial
  Services members (Waters, Meeks, Sherman, Huizenga all below him).
- **source records:** deduped DISTINCT (contributor,payee,date,amount) FECA
  items over `senate_registrants LIKE 'CREDIT UNION NATIONAL%'`, honoree match
  confidence ≥ 0.9. Desk-derived.
- **caveats:** ACU spreads leadership money **bipartisanly** — Barr is favored
  as HFSC-subcommittee chair, not uniquely. So this **does not kill** the story
  on scale (refute condition (b) fails: $40k is top-tier, not median), but it
  also shows $40k is a normal top-tier committee-relationship figure, not an
  outlier. honoree_member_map at 0.9 can under/over-collect a member's exact
  string; ranks near Barr (±$1-2k) are within match noise.
- **verdict:** supports (scale) — Barr is genuinely top-tier, not median.

## E5 — full pivot stack: ACU is NOT day-one and NOT the biggest; the timing hook weakens
- **query/script:** `queries.sql#q5` + `#q5b` (run 2026-07-07)
- **result:** **419 registrants** report FECA honoring Barr (deduped). ACU's
  $40,000 ranks **~11th** — ten registrants gave more: Carlyle $52.5k, American
  Bankers Assn $47.5k, Independent Insurance Agents & Brokers $45k, FMR/Fidelity
  $44.5k, Mortgage Bankers Assn $42.5k, Capital One $41.5k, Deloitte $40.5k,
  U.S. Bancorp $40,041, JPMorgan $40,017, American Land Title $40k. **Day-one
  test (q5b):** five registrants reported contributions to "ANDY BARR FOR
  SENATE, INC." **before** ACU's 2025-02-20 — Cresco Labs 2025-01-31 ($1,000),
  Nationwide 2025-02-04 ($2,500), Independent Insurance Agents 2025-02-10
  ($5,000), Huntington Bancshares 2025-02-13 ($2,500), UPS 2025-02-17 ($5,000).
  ACU (2025-02-20) is the **6th** to the Senate committee. 231 of 419
  registrants gave after the pivot; only **4** have a first-post-pivot gift
  dated exactly 2025-02-20.
- **source records:** deduped DISTINCT (registrant,contributor,payee,date,
  amount) FECA items, honoree confidence ≥ 0.9. Desk-derived.
- **caveats:** the "Andy Barr for Senate, Inc." committee was already reporting
  contributions as early as **2025-01-31**, three weeks before McConnell's
  2025-02-20 retirement announcement (see E9 — it is a pre-existing committee
  redesignated to the Senate race). So the "money following him from day one,
  literally" / "the very day McConnell announced" hook is a **dating
  coincidence**, not primacy — this materially **weakens** the case's central
  timing narrative. Reframe: the financial industry's pivot to Barr's Senate
  committee was broad and underway in January; ACU is one clear, documented
  thread (endorse→legislate→pay), but neither the earliest nor the largest
  donor.
- **verdict:** weakens (the day-one/McConnell-timing hook) — supports only the
  broader "financial industry and Barr" framing.

## E6 — ACU's Senate lobbying names both Barr CFPB bills by number
- **query/script:** `queries.sql#q6` + `#q6b` (run 2026-07-07)
- **result:** of 107 ACU Senate lobbying activity rows, 10 mention UDAAP. From
  2025 Q1 through 2026 Q1 the activity descriptions list, verbatim:
  **"Support Taking Account of Bureaucrats Spending Act (H.R. 654) Support
  Rectifying UDAAP Act (H.R. 1652)"** — Barr's TABS Act (H.R. 654, spelled out)
  and his Rectifying UDAAP Act (H.R. 1652), both by title and bill number.
  Earlier 2022 filings mention UDAAP only generically ("Issues related to UDAAP
  guidance and requirements"), predating the bills.
- **source records:** filing_uuids carrying the named-bill text: 2025 Q1
  `579f0209-4eac-4933-b277-3978e56896a8`; Q2 `758dcddf-2136-44be-8215-baf436e320ba`;
  Q3 `aa11bc45-472a-4514-85c6-a2dfcfd9b8d0`; Q4 `43e75f1f-32fe-40a2-92ee-b70fe92b74b7`;
  2026 Q1 `93c9dba6-1595-4335-aecb-7d63567571c4`. Verify at
  https://lda.gov/filings/public/filing/{uuid}/print/
- **caveats:** the literal acronym "TABS" never appears (the bill is named by
  its full title + H.R. 654); a `LIKE '%TABS%'` screen returns zero and would
  miss it — match on the bill title/number. The `LIKE '% Barr%'` hits are
  **false positives** (the token falls inside "Member Business Loan Act" /
  "Credit and Debit Card" phrasing, not references to Rep. Barr) — do not cite
  them. The real, strong signal is the named-bill support text.
- **verdict:** supports (strong) — ACU's own Senate filings list support for
  both Barr bills by name and number, in every quarter since he introduced them.

## E7 — endorsement quotes survive the primary text (2 of 3 name ACU), but ACU is one voice in an industry wall
- **query/script:** `queries.sql#q7` — full `press_releases.text` for the three
  E1 urls (run 2026-07-07)
- **result:**
  - **2023-12-15** (first Rectifying UDAAP intro): quotes **five** financial
    trade groups — AFSA, ICBA, CBA, ABA, and jointly **"CUNA President and CEO
    Jim Nussle and NAFCU President and CEO Dan Berger"** (the pre-merger
    predecessors, Dec 2023 before the Jan-2024 merger): *"The CFPB has attempted
    to exert its power well beyond what Congress ever intended, most strikingly
    with its UDAAP authority… I applaud Rep. Barr's efforts to rein in the
    CFBP's abuse of this authority…"* This release does **not** say "America's
    Credit Unions" — it names CUNA + NAFCU.
  - **2025-01-23** (TABS Act reintro): quotes ACU **by name** —
    *"America's Credit Unions thanks Rep. Barr for introducing this critically
    important legislation… The TABS Act would bring needed accountability,
    oversight, and transparency to the agency…" said Jim Nussle, America's
    Credit Unions President/CEO.* One of five endorsers quoted (also ABA, ACA
    International, AFSA, CBA).
  - **2025-05-03** (Rectifying UDAAP reintro): quotes ACU **by name** —
    *"America's Credit Unions applauds Rep. Barr's efforts to rein in the CFPB's
    regulatory overreach…" – Jim Nussle, America's Credit Unions President/CEO.*
    One of five (also ABA, CBA, ICBA, AFSA).
- **source records:** press_releases text at the three E1 urls.
- **caveats:** the "endorsement in his own releases" characterization **survives
  the primary text** for the two 2025 releases (ACU quoted by name); for
  2023-12-15 it is **CUNA + NAFCU** (ACU's predecessors), accurate only if
  described as such. Material qualifier (refute condition (c)): in **all three**
  releases ACU/CUNA is **one voice in a 4-5-endorser industry wall** (ABA, CBA,
  ICBA, AFSA, ACA) — the endorsement-quote practice is uniform financial-
  industry boilerplate, **not ACU-specific**. Cite ACU as quoted, not as the
  sole or singular endorser.
- **verdict:** supports (ACU quoted by name in the 2025 releases) with a
  material caveat that weakens ACU-specificity.

## E8 — the 2025-02-20 pivot item verified against the source LD-203 filing
- **query/script:** `queries.sql#q8` (ingest) + outside fetch of the LDA API
  (run 2026-07-07)
- **result:** fetched `https://lda.senate.gov/api/v1/contributions/6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4/`
  (84,258-byte JSON, **368 contribution items**), registrant "CREDIT UNION
  NATIONAL ASSOCIATION. INC. DBA AMERICA'S CREDIT UNIONS", 2025 Mid-Year.
  Confirmed row present verbatim: **date 2025-02-20, amount $5,000.00, payee
  "ANDY BARR FOR SENATE, INC.", honoree "Rep. Andy Barr", contribution_type
  feca**, contributor "AMERICA'S CREDIT UNIONS PAC" — **exactly matching our
  ingest** (E2). The same filing also carries the 2025-02-28 $5,000 B.A.R.R.
  PAC item.
- **source records:** LDA API JSON (above) and
  https://lda.gov/filings/public/contribution/6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4/print/
  (the human filing page returned 404 on fetch; the `/api/v1/contributions/`
  path is the fetchable/authoritative source). Ingest row: q8.
- **caveats:** LDA's small-model page summaries are unreliable over 368 items
  (two WebFetch passes missed the row); the raw JSON scan is authoritative. The
  filing reports the contribution **date** as 2025-02-20; it does not itself
  distinguish a check date from an attribution date — resolved as chronologically
  genuine by E9.
- **verdict:** supports — the pivot item is real and correctly ingested.

## E9 — FEC: "Andy Barr for Senate, Inc." is a redesignated pre-existing committee; 2025-02-20 is plausible
- **query/script:** outside fetch, FEC API DEMO_KEY (run 2026-07-07; context
  only, disclosed outside data)
- **result:** `https://api.open.fec.gov/v1/committee/C00467571/?api_key=DEMO_KEY`
  → committee **"ANDY BARR FOR SENATE, INC."**, ID **C00467571**, treasurer Paul
  Kilgore, type "Senate", designation "Principal campaign committee",
  **candidate_ids H0KY06104 (House, KY-06) AND S6KY00286 (Senate, KY)**,
  first_file_date **2009-09-28**, cycles 2010-2026. This is Barr's **original
  2009 House principal campaign committee** (candidate H0KY06104, first filed for
  his 2010 House run), **redesignated** to his Senate candidacy (S6KY00286) for
  the 2026 cycle — the FEC committee ID is retained through redesignation and
  the committee renamed "Andy Barr for Senate, Inc."
- **source records:** FEC API committee C00467571 (open.fec.gov, DEMO_KEY).
- **caveats:** because it is a pre-existing committee **redesignated** (not newly
  formed), it could receive and report money under the Senate name as soon as the
  redesignation was on file. The committee summary does **not** give the exact
  redesignation date (**owed:** the FEC Form 1/2 amendment date) — but the LD-203
  corpus (E5, q5b) independently shows contributions reported to "ANDY BARR FOR
  SENATE, INC." as early as **2025-01-31**, so the Senate redesignation was
  effective by late January 2025, ~3 weeks **before** McConnell's 2025-02-20
  announcement. A 2025-02-20 contribution to it is therefore **chronologically
  plausible and not a check/attribution artifact** — but this same fact confirms
  the committee predated the announcement, reinforcing E5 that the "day McConnell
  announced" framing is a dating coincidence.
- **verdict:** supports (the 2025-02-20 date is genuine/plausible) — weakens the
  timing hook (committee active weeks earlier). Owed: exact FEC redesignation date.
