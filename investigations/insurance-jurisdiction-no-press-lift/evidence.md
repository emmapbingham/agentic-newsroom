# Evidence — insurance-jurisdiction-no-press-lift

Every number here is reproduced by
`analysis/ins_committee_press_share.py` (case-local, reads `db/gain.db`
only) — re-run it to regenerate all figures at once, or use the individual
queries in `queries.sql`. Figures below supersede the original lead's
scout numbers where they differ slightly (the roster-join method was the
same, but this is the clean re-derivation, not the ad hoc session check).

## E1 — The shared `ISSUE_KEYWORDS['INS']` keyword set undercounts by ~4x

- **query/script:** `queries.sql#q1`, `#q2`
- **result:** bare word "insurance" appears in **6,159** press releases
  corpus-wide. The shared, in-production keyword set
  (`scripts/build_derived_issue_quarter_volume_press.py`,
  `ISSUE_KEYWORDS['INS']` = `['insurance industry', 'insurance regulation',
  'insurer', 'insurance premium']`) matches only **1,422** (23.1% of the
  bare-word count).
- **source records:** `press_releases.text`, corpus-wide (no single URL —
  this is a corpus-level count).
- **caveats:** the bare word "insurance" includes health-insurance and
  unemployment-insurance mentions that correctly belong to other issue
  codes (HCR, UNM) — 100% bare-word recall was never the target. See E2.
- **verdict:** supports (the recall gap is real, motivating a fix)

## E2 — The recall gap is isolated to INS, not systemic across `ISSUE_KEYWORDS`

- **query/script:** `scripts/audit_issue_keyword_recall.py` (shared,
  reusable diagnostic — see Methodology section below)
- **result:** ran the bare-word-ratio audit across 26 of 75 issue codes
  that have a clean single-word anchor. INS scored **0.23** (matched ÷
  bare-word count); every other audited code scored **1.29–13.74**
  (HCR/FIR/VET/BAN/RET/ENG/AVI/EDU/MMM/FIN/DEF/AGR/HOM/TAX/TRA/BUD/LBR/
  PHA/TEC/ENV/ALC/HOU/AUT/TRD/IMM all clear 1.0 — their keyword sets
  deliberately widen beyond the single anchor word, so recall exceeding
  100% of the bare word is expected and normal).
- **source records:** n/a — corpus-level diagnostic, no single record.
- **caveats:** only 26 of 75 codes have an obvious single bare-word anchor;
  the other 49 are unaudited. INS being the only outlier among the audited
  26 is reassuring but not a guarantee the other 49 are clean.
- **verdict:** supports (confirms INS specifically is broken; other
  `ISSUE_KEYWORDS`-based findings in this corpus are probably fine)

## E3 — A broadened, industry-disambiguated INS keyword set (case-local fix)

- **query/script:** `queries.sql#q3`; `BROAD_INS_KEYWORDS` in
  `analysis/ins_committee_press_share.py`
- **result:** the broadened 15-keyword set (see Methodology section for the
  full list and the disambiguation logic) matches **2,406** releases
  (39.1% of the 6,159 bare-word count) — appropriately still well under
  100%, since most of the excluded bare-word mentions are genuinely
  health/unemployment insurance, not insurance-industry regulation.
- **source records:** `press_releases.text`, corpus-wide.
- **caveats:** this fix is **case-local** — it lives in this case's
  analysis script, NOT in the shared `ISSUE_KEYWORDS['INS']` used by
  `derived_issue_quarter_volume_press` / `derived_committee_quarter_press`.
  Promoting it would require rebuilding both derived tables and
  re-verifying `quiet-issue-quadrant`'s existing INS ranking (not done).
- **verdict:** supports (the fix is defensible and used for all downstream
  figures in this case)

## E4 — Corpus-wide INS baseline, and the committee-level gap

- **query/script:** `analysis/ins_committee_press_share.py`
  (E-corpus-baseline, E-committee-topic-share sections); underlying joins
  in `queries.sql#q5`, `#q6`
- **result:**
  - Corpus-wide INS topic share (broad keywords): **2,406 / 141,332 =
    1.70%**.
  - **HSBA04** (House Financial Services — Housing and Insurance): of
    3,234 press releases from members while seated on the committee
    (roster resolved via `member_committees_history`, point-in-time — see
    Methodology), INS = **52 (1.61%)**, essentially at the 1.70% baseline
    (no lift). The committee's *other* primary jurisdiction, HOU
    (Housing): **1,309 (40.48%)**, vs. a 35.28% corpus baseline for HOU —
    a real, if modest, lift.
  - **SSBK04** (Senate Banking — Securities, Insurance and Investment): of
    7,022 releases, INS = **187 (2.66%)**, a small lift over the 1.70%
    baseline. The committee's other primary jurisdiction, FIN (Financial
    Institutions): **2,258 (32.16%)**, vs. a 24.67% corpus baseline — a
    clearer lift (1.3x).
- **source records:** `press_releases` joined to `member_committees_history`
  by `bioguide` + `committee_id`, filtered to releases dated within the
  member's seated window. No single citable record — this is an aggregate;
  drill to `press_releases.url` for any individual release.
- **caveats:** small N (2 committees). `committee_issue_jurisdiction` is a
  hand-curated map (see `docs/members_db.md`) — HOU and FIN are each this
  committee's OWN primary jurisdiction per that map, not an arbitrary
  comparison topic.
- **verdict:** supports the core finding (real gap between INS and the
  committee's other topic, for the same members)

## E5 — Boring explanation tested: "insurance is just an inherently quiet topic" — ruled out

- **query/script:** `analysis/ins_committee_press_share.py`
  (E-lobby-money, E-dollar-normalized sections); `queries.sql#q7`, `#q8`
- **result:** INS lobbying scale: **$137,020,996** apportioned Senate
  income, **6,728** activities (2022–2026). Ranking all issue codes with
  >$50M apportioned income (53 codes) by press-releases-per-$1M-lobbied,
  INS scores **17.56** — ranking **14th quietest of 53** (26th
  percentile). This is on the quieter side but **not an extreme outlier**:
  GAM (3.60), SPO (5.28), CPT (5.33), CPI (6.34), and CSP (6.45) are all
  markedly quieter per dollar than INS. INS sits well above genuinely
  silent-per-dollar codes and closer to the middle of the distribution
  (median of the 53 ≈ 32).
- **source records:** `derived_issue_quarter_volume_press`, aggregated
  across `issue_code='INS'` and comparably-sized codes; no single citable
  record (aggregate).
- **caveats:** press counts for codes other than INS use their own
  (un-audited beyond E2's 26-code sample) `ISSUE_KEYWORDS` set, not a
  broadened override — if any of those 52 other codes has an INS-style
  recall bug, its ranking here would be understated too. Only the 26 codes
  in E2 have been checked.
- **verdict:** partially refutes the "insurance is inherently unnewsworthy"
  boring explanation — INS is moderately quiet per dollar lobbied, in line
  with the lower-middle of comparable industries, not a standout silence.
  This does NOT explain away the committee-jurisdiction gap in E4 (which is
  about elevation *within* a committee vs. its own baseline, not the
  corpus-wide absolute level).

## E6 — Independent cross-check against the ML press-topic classifier (`M0`)

- **query/script:** `analysis/ins_ml_classifier_crosscheck.py`
- **context:** a second, independent method for "is this release about
  INS" now exists — `scripts/press_topic_classifier.py` (`M0`, a
  multinomial logistic regression trained on ~1.5M LDA activity
  descriptions, scored into `derived_press_issue_labels`, threshold 0.3;
  see `docs/press-issue-classifier.md`). It
  uses no keywords at all, so it can't share the keyword map's specific
  bug — but it has its own documented limitation (LDA filing language vs.
  press-release narrative prose register mismatch) that predicts it will
  *also* under-recall genuine insurance-industry content, just for a
  different reason.
- **result, in three parts:**
  1. **Overlap with the narrow (in-production) keyword set is low:** the
     classifier recalls only **230/1,422 = 16.2%** of the narrow
     `ISSUE_KEYWORDS['INS']` matches — worse than that keyword set's own
     23.1% recall of the bare word "insurance" (E1), the very problem this
     case originally flagged as a bug.
  2. **Recall on unambiguous industry-specific content is also weak:** of
     363 corpus releases containing "NFIP," "flood insurance," "property
     insurance," or "casualty insurance" (unambiguously INS-territory, no
     health/unemployment-insurance confound possible), the classifier
     flags only **93 (25.6%)**.
  3. **Where it does match, it reintroduces the opposite confusion the
     broad keyword set was built to avoid:** hand-checking the
     classifier's highest-confidence matches NOT caught by the broad
     keyword set surfaced releases about the ACA coverage gap, junk health
     plans, Medicaid expansion, and health-care-premium legislation
     (probabilities 0.76–0.90) — i.e. HCR-territory health-insurance-as-
     benefit content, exactly the confusion `BROAD_INS_KEYWORDS` was
     hand-disambiguated to exclude (see Methodology §2). This matches the
     domain-mismatch failure mode already documented in the classifier's
     own plan doc (the pilot's "20 newly incorrect ACA/health-insurance
     INS matches" finding).
  4. **Despite both of the above, the committee-level pattern reproduces:**
     corpus-wide INS share (classifier) = 461/141,332 = 0.33%. HSBA04:
     16/3,234 = 0.49% (essentially at/near baseline). SSBK04: 31/7,022 =
     0.44% (a small lift, same direction and rough magnitude as E4's
     keyword-based 2.66% vs 1.70%). Neither committee shows a meaningful
     jurisdiction lift on INS under this completely independent
     measurement method either.
- **source records:** `derived_press_issue_labels` (release_id, issue_code,
  probability >= 0.3), joined to `press_releases` and
  `member_committees_history` the same way as E4. No single citable
  record — aggregate; drill to `press_releases.url` for any individual
  release.
- **caveats:** this is NOT a validation of the classifier as accurate — if
  anything it's evidence the classifier is a *worse* instrument than the
  case's own hand-disambiguated broad keyword set for this specific code
  (lower recall on genuine content, a different but real false-positive
  mode on ACA/health-insurance content). Per the classifier's own coexistence
  rule (see plan doc), this is not being treated as a standalone
  quantitative finding — it is used here only as an adversarial recall/
  precision check on E4, not as a replacement measurement. The fact that
  two methods with different, uncorrelated failure modes (narrow keyword
  substring matching vs. LDA-filing-language TF-IDF/logistic regression)
  land on the same qualitative committee-level conclusion is what makes
  this a meaningful cross-check, not the classifier's absolute numbers
  themselves.
- **verdict:** supports (E4's core finding — no meaningful INS jurisdiction
  lift at HSBA04 or SSBK04 — survives a second, structurally independent
  measurement method with different failure modes; strengthens confidence
  the gap is not a keyword-map artifact specifically, though see caveat)

## Open / untested

- **Technical-density boring explanation** (insurance may be harder to
  message on than housing/banking, independent of lobbying or salience) —
  not yet tested. Candidate comparison: `CPT` (Copyright/Patent/Trademark),
  which also scored low in E5 (5.33 press/$1M) and is similarly technical
  subject matter with an identifiable committee (House Judiciary, `HSJU`,
  per `committee_issue_jurisdiction`). If HSJU also shows no jurisdiction
  lift on CPT vs. its other topic (LAW), the "technical topics don't get
  committee messaging lift" explanation generalizes and this case is not
  insurance-specific. If HSJU *does* show a normal lift on CPT, insurance
  remains the outlier.
- **Committee tenure** — not yet checked per-member. A member who recently
  joined the subcommittee wouldn't be expected to show elevated topic share
  yet; `member_committees_history` roster snapshots only resolve cleanly
  from 2022-01-04 forward (see Methodology).
