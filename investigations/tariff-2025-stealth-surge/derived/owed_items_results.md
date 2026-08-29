# Owed-item results: foreign-ownership share + pre-2022 spot-check (2026-06-15)

## E11 — Foreign-ownership share of the genuine-new cohort

The genuine-new cohort = 126 registrants, **155 distinct 2025 TAR clients**.

- **Declared floor (verifiable):** only **10/155 (6.5%)** declare a non-US
  `country`/`ppb_country`; 17/155 carry a foreign-entity disclosure
  (`senate_filing_foreign_entities`). The field badly understates — foreign
  subsidiaries file as US.
- **Inferred share (reference tier):** a Sonnet pass over the 155 client names +
  filed country (`derived/client_foreign.json`, per-row basis + confidence)
  estimates **56/155 (36%) foreign-linked** (ultimate parent/HQ abroad); **39%
  activity-weighted** (173/443 cohort 2025 TAR activities).
- **The 6.5% → 36% gap is the finding:** the LDA country field hides most foreign
  involvement.
- **Named foreign-linked clients** (inferred parent country): Schaeffler [DE],
  Alpek [MX], DigitalEurope [BE], Dompé [IT], Takeda [JP], Tetra Pak [SE], Teva
  [IL], Wacker [DE], Anheuser-Busch [BE], Apotex [CA], bioMérieux [FR],
  BraunAbility [NL], …
- **Caveat:** the 36/39% is LLM-inferred (reference tier, name-based); the
  verifiable lower bound is the 6.5% declared + the named examples. Not resolved
  to corporate-registry grade.

## E12 — Pre-2022 spot-check (left-censoring of "genuinely new")

Checked 6 genuine-new firms against the public LDA API
(`https://lda.senate.gov/api/v1/filings/?registrant_name=…&filing_specific_lobbying_issues=tariff&ordering=dt_posted`)
for any pre-2022 tariff lobbying:

- **Confirmed no pre-2022 tariff** (4/6): **Clark Hill Public Strategies**
  (earliest LDA filing 2022 — didn't exist pre-window), **Westwin Elements**
  (earliest tariff 2025; a 2024 startup), **A10 Associates** (6 tariff filings,
  all 2025), **Teva Pharmaceuticals** (earliest tariff 2025).
- **Inconclusive** (2/6): **Checkmate Government Relations**, **Amgen** — 0 hits on
  the "tariff" text filter despite 2025 TAR rows in our corpus (their filing
  descriptions don't contain the literal word "tariff"), so the text search is
  blind to them. Both had no TAR/TRD in our 2022–24 window, making pre-2022 TAR
  unlikely but unconfirmed.
- **Method validated:** the same query surfaces **Ballard Partners'** tariff
  lobbying back to **2018**, confirming it detects pre-2022 activity when present
  (Ballard is an incumbent, not cohort — validation only).
- **Verdict:** no left-censoring found in the 4 confirmable cases → supports
  "genuinely new." Residual caveat: text-filter false-negatives leave 2
  unconfirmed; a code-level API query would close them.
