# The press-issue classifier (`derived_press_issue_labels`)

Methodology record for the ML press-topic classifier built alongside
`ISSUE_KEYWORDS` (a parallel method, not a replacement).

Executed 2026-07-03. This is the plan as approved and carried out — a
point-in-time record, not a forward runbook. It is the cited authority for the
audit thresholds hardcoded in `scripts/press_topic_classifier.py`,
`scripts/build_derived_press_issue_labels.py`, and
`scripts/build_derived_issue_quarter_volume_press_ml.py`; the mismatch section
below is what those scripts point at when a check fails.

**Revised mid-session** from an original "replace `ISSUE_KEYWORDS`" framing to
"build a second, clearly-labeled, coexisting method" — see the Verifiability
pivot section below for why.

## FINAL STATUS (end of session, 2026-07-03)

**Kept:** `M0` — the pure-LDA-description logistic regression classifier
(`scripts/press_topic_classifier.py`, `scripts/build_derived_press_issue_labels.py`,
`scripts/validate_press_issue_labels.py`), scoring the whole corpus into
`derived_press_issue_labels` (currently 100,541 rows, threshold 0.3). This
is real, working, committed infrastructure — coexists with `ISSUE_KEYWORDS`
exactly per the coexistence design below.

**Abandoned:** the Haiku-labeled training-data augmentation (the two-round
iterative design described in this doc, `M1`/`M2`). Reason: repeated,
hard-to-predict Haiku labeling-quality failures discovered late each
time — an over-labeling problem (fixed by a hard cap), then a more serious
*indiscriminate mislabeling* pattern (TRA and EDU codes applied to clearly
unrelated releases based on surface vocabulary — "infrastructure"→TRA,
"student/research"→EDU — found in BOTH the held-out evaluation set AND
round 2's actual training data, meaning `M1`/`M2` likely had real defects
baked in, not just an evaluation-layer problem). Diagnosed via a targeted
test: Opus, given the identical prompt and the exact 10 releases Haiku got
wrong, got 0/10 wrong and correctly diagnosed the same surface-vocabulary
failure mode. This confirmed the problem was Haiku-specific to this
75-way substantive-vs-surface classification task, not a fundamental flaw
in LLM-based labeling as an approach — but redoing all labeling on Opus
(~$5.50 in token-equivalent cost, trivial) was judged not worth the
engineering/attention cost already sunk, for a component that the
Verifiability Pivot (below) had already scoped to lead-discovery-only, never
a standalone quantitative claim. Scratch labeling artifacts (pilot/round1/
round2 batches and labels, the two failed held-out test-set labeling
attempts, cached M1/M2 models) live only in the session scratchpad
(`/private/tmp/.../scratchpad/`), not the repo — nothing to clean up in
`db/gain.db` or the codebase.

**Open question for a future session, if anyone wants to pick this up
again:** does `M0` (bare LDA classifier, no augmentation) actually surface
better leads than `ISSUE_KEYWORDS` in practice? Not yet tested empirically —
the next session's stated priority is to actually use `M0` for lead-surfacing
work rather than continue optimizing it. If `M0` turns out to have the same
kind of domain-mismatch recall gaps documented earlier in this doc (real,
but smaller than the over-labeling crisis that sank the augmentation
track), that's an argument for revisiting Opus-based augmentation
specifically — cheaply, in one clean pass, no more multi-round iteration —
but only if `M0` proves insufficient in actual use, not preemptively.

## Context

An audit of the press-release-to-issue-code keyword map (`ISSUE_KEYWORDS`,
used to build the quiet-issue-quadrant screen and every other "press
attention to topic X" measure) found it broken in ways that go beyond the
already-known INS bug:

- **INS** recalls only 23% of its own bare-word anchor — a known, documented
  bug (`investigations/insurance-jurisdiction-no-press-lift`), fixed
  case-locally but never promoted into the shared map.
- **IMM (54.6%), TAX (49.5%), ENV (47.0%), HCR (36.6%)** of the *entire*
  corpus match — likely over-broad, unverified by the existing audit tool
  (`scripts/audit_issue_keyword_recall.py`), which only checks under-recall,
  never over-matching.
- **9 keyword strings are shared across 15 code pairs** (`tariff` →
  TAX/TRD/TAR, `medicare`/`medicaid` → HCR/MMM, etc.) — double-counting one
  release into multiple codes' totals with no disambiguation.
- **Only 26 of 79 codes have ever been audited** at all (bare-anchor check).
- **The map exists as four independent, drifting copies**: the canonical
  `ISSUE_KEYWORDS` in `scripts/build_derived_issue_quarter_volume_press.py`;
  a hand-synced duplicate in `scripts/build_derived_member_press_topics.py`
  (docstring literally says "must stay in sync" — it's a copy-paste twin,
  not an import); an orphan derived table
  (`derived_member_press_topic_panel`) that's unvalidated, unregistered in
  `build_gain_db.py`, and undocumented in `docs/derived_db.md`; and a case
  (`critics-take-health-money`) with its own fourth, inline keyword set.

## Model-selection history — three approaches tried, in order

**1. Hand-rolled TF-IDF + cosine similarity (no library).** First prototype,
validated well on INS/TAX/GOV/multi-label spot-checks. Replaced with
scikit-learn per editor request (`uv add scikit-learn`, now in
`pyproject.toml`/`uv.lock`) — using a maintained library instead of
hand-rolled linear algebra.

**2. sklearn TF-IDF + cosine-similarity-to-per-code-centroid.** Two
sub-pitfalls surfaced:
- Fitting `TfidfVectorizer` on 79 giant PRE-AGGREGATED per-code text blobs
  (one "document" per code) instead of ~1.5M individual LDA activity
  descriptions degenerates IDF (document frequency computed over 79
  pseudo-documents, not real examples) and produces a model that LOOKS
  plausible but is silently broken — INS, TAX, and GOV converged on the
  same top matches. Fixed by fitting on individual descriptions instead.
- Even fixed, cosine-to-centroid has no threshold that works across codes.
  A global percentile-of-self-similarity threshold either kills recall on
  precise codes (TAX collapsed to 425 matched releases, -99% from the old
  keyword map, when hand-checking confirmed genuinely on-topic releases
  were excluded) or reintroduces false positives on codes whose vocabulary
  overlaps generic legislative-process language (ENV/VET matched NIH/WHO/
  gun-safety releases at a looser threshold). A "genericness" proxy
  (centroid's cosine similarity to the corpus-wide mean centroid) was
  tried as an automatic way to set per-code percentiles — it did not
  reliably predict the right direction (VET needed a HIGH percentile
  despite scoring "distinctive"; TAX needed a LOW percentile despite
  scoring "generic"). Root cause: averaging all of a code's training
  examples into one point conflates "typical example of this code" with
  "the vocabulary that actually distinguishes this code from the other
  74" — exactly the information a threshold decision needs and centroid
  distance doesn't provide.

**3. Multinomial logistic regression, one-vs-rest, `class_weight="balanced"`
(adopted).** A discriminative classifier optimizes directly for separating
each code from the rest. Side-by-side comparison against the exact codes
that broke the centroid approach (INS/TAX/ENV/VET/CPT/PHA) showed sharp,
correctly-scoped top matches for all six, AND — critically —
`predict_proba` produces probabilities comparable ACROSS codes, so a
single global probability threshold (0.3, validated by sweep + hand-check)
is viable, unlike cosine similarity. Training cost: ~5-6 min (lbfgs
solver, 79 classes minus 4 excluded, ~1.5M training examples, ~46K
features) — local, free, one-time per rebuild.

Full technical detail and the model-selection rationale live in
`scripts/press_topic_classifier.py`'s module docstring — keep that in sync
if the method changes again.

## The domain-mismatch finding — why LDA-only training data has a ceiling

Coverage-delta validation (comparing the classifier's INS matches against
both the old narrow keyword map AND the case's own hand-disambiguated
`BROAD_INS_KEYWORDS`) surfaced a real, structural limitation: the
classifier trained purely on LDA activity descriptions correctly excludes
most of the old keyword map's false positives (health-insurance-as-a-
benefit mentions wrongly caught by bare "insurance premium" etc. — a
genuine precision win, confirmed by hand-checking ~20 samples, 100% correct
exclusions), but under-recalls genuinely industry-specific insurance
content (e.g. a Cassidy floor speech specifically urging Congress to
prevent an NFIP lapse — a confirmed miss).

Root cause, confirmed by direct measurement: LDA activity descriptions are
terse lobbyist-filing fragments (median 87 characters — "Insurance
Regulation Federal pandemic insurance backstop..."); press releases are
long narrative advocacy prose (median 2,308 characters) where the
substantive policy content is often embedded in scene-setting rhetoric
that shares little vocabulary with LDA filing language. A classifier
trained purely on the former learns "the vocabulary of a lobbying filing,"
not necessarily "the concept," and under-recalls on register-mismatched
but substantively on-topic press releases.

**Proposed fix, tested via a pilot:** augment the ~1.47M LDA training
examples with a modest number of LLM-labeled ACTUAL PRESS RELEASES — text
in the same register as what the classifier is ultimately scoring, closing
the domain gap directly rather than hoping volume alone bridges it.

## The verifiability pivot — why this became "coexist," not "replace"

Mid-session, before committing further Haiku-labeling budget, we stepped
back and asked whether ML belongs in a data-journalism analysis pipeline at
all. Conclusion, reached jointly:

- **Neither the keyword map nor the classifier is fit to be a standalone
  quantitative finding.** LIKE-matching a phrase or a trained model scoring
  a release both fall short of "this release is substantively about X" —
  this was true even before the classifier existed (the INS case's own
  E1-E5 exists because the keyword map's numbers weren't trustworthy on
  their own). The bar was never "make the classifier as auditable as the
  keyword map" — it's "neither method alone licenses a number like '4.2x
  more lobbying dollars per press release' as a published fact."
- **Given that, both methods are legitimate as lead-discovery tools** (candidate
  surfacing for a human to then read and verify against primary source
  text — the same screen → leads → promote → verify discipline this
  project's pipeline already runs), but **neither may be the sole basis for
  a numeric claim in a finding.** Any case making a quantitative "how much
  press attention" claim needs a human read-through of the actual flagged
  releases, the same discipline the INS case already established
  (`analysis/ins_committee_press_share.py` re-derives from source rather
  than trusting the map).
- **Both methods stay in the repo, side by side, not one replacing the
  other.** `ISSUE_KEYWORDS`/`derived_issue_quarter_volume_press`/
  `derived_committee_quarter_press` are UNCHANGED — including the
  still-open INS recall bug, left as-is and documented, not silently
  fixed by deletion. The classifier becomes new, clearly-labeled,
  ADDITIONAL infrastructure, not a migration target for the existing
  tables. A judge (or a future investigator) can inspect both methods and
  see the tradeoff directly: a one-line grep rule vs. a trained model,
  neither treated as ground truth.
- The findings report's methodology section gets an explicit passage on
  this: two independent press-topic-classification methods exist, neither
  is ground truth, both are used only to discover candidates, every
  published claim is hand-verified against primary source text.

**This reverses two items from the original plan:** consumer-table
migration (originally §4/§5, "replace ISSUE_KEYWORDS in the three
consumer tables") is now explicitly OUT OF SCOPE — see the Explicitly Out
of Scope section below.

## Naming / coexistence architecture

- `derived_issue_quarter_volume_press` (keyword-based) — **unchanged**,
  including its known INS bug.
- `derived_issue_quarter_volume_press_ml` (classifier-based) — **new**,
  same grain/shape, sourced from `derived_press_issue_labels` instead of a
  LIKE sweep.
- `derived_committee_quarter_press` (keyword-based) — **unchanged**.
- `derived_committee_quarter_press_ml` (classifier-based) — **new**, same
  pattern.
- `derived_member_press_topic_panel` (the pre-existing orphan table) —
  **out of scope for this change**; not migrated, not duplicated. Its
  orphan/undocumented status is a pre-existing bug independent of this
  redesign; worth fixing separately, not bundled here.
- The `_ml` suffix means METHOD, not VERSION — it is not a migration path
  and is not expected to ever replace the unsuffixed table.
- `quiet-issue-quadrant-ml` — a new, separate screen entry (its own row in
  the newsroom `screens` ledger), not an edit to the existing
  `quiet-issue-quadrant/screen.sql`. Keeps `screen_runs` history honest
  about which method produced which run, preserving the multiple-
  comparisons ledger discipline — a lead surfaced by the keyword screen and
  a lead surfaced by the ML screen are different pieces of evidence even
  when they point at the same release.
- One shared methodology doc — `docs/press_topic_classification_methods.md`
  — lays out both methods side by side: what each does, each one's known
  failure modes (INS bug for keywords; domain-mismatch/under-tested-code
  caveats for the classifier), and the hard rule that neither may be cited
  as a standalone quantitative finding. Both table docstrings point to this
  doc rather than duplicating the caveat inline.

## Two-round Haiku-augmented training design

Rather than a single big batch of LLM-labeled press releases, training
proceeds in two rounds so each round's sampling targets wherever the
*current* model is actually uncertain — not a fixed set of codes picked by
hand, which testing showed is an unreliable way to predict where problems
live (see below).

**Why not hand-pick codes to fix:** initially assumed INS/TAX/ENV/VET (the
4 codes hand-checked during development) were "the" problem codes and
planned to concentrate the Haiku-labeling budget there. Tested this
assumption using disagreement sampling (below) before committing budget,
and it was wrong: with the classifier's own excluded-code list correctly
applied, ambiguous cases (top-code probability in [0.15, 0.35] — real
signal but not confident) spread across 20+ codes (CIV, FOR, ECN, HCR, LAW,
EDU, DEF, BUD, HOM lead the list), most of which were never hand-checked.
Concentrating budget on 4 codes discovered by manual spot-check would have
systematically missed the codes actually showing the most uncertainty.

**Total Haiku-labeling budget: ~1,000 press releases**, priced at Haiku
4.5 rates (~$1.36-2.72 depending on batching — see cost estimate below),
but executed via Claude Code subagent fan-out (`Agent` tool,
`model: "haiku"`) rather than a separate Anthropic API key/billing setup,
per editor preference to use existing Claude Code usage rather than stand
up new API infrastructure. Pilot batch (200 releases) already completed
and validated this session (see Pilot Results below); ~800 more to run in
two iterative rounds.

**Round 0 (done):** baseline classifier, `M0` — trained on ~1.47M LDA
activity descriptions only, no Haiku-labeled data. This is the classifier
described in the Model-selection History section above.

**Pilot (done, 200 releases, counts toward the 1,000 total):**
- Sampling: keyword-hit oversampling toward the 4 suspected-problem codes
  (`flood insurance`, `insurance premium`, `tax credit`, `environmental
  protection agency`, `veterans affairs`, `veteran`) plus random fill to
  200.
- Labeled via one Haiku subagent (`Agent` tool, `model: "haiku"`),
  multi-label, 0+ codes per release from the 75-code (excluded-code-free)
  vocabulary, with explicit disambiguation guidance (e.g. "health
  insurance" ≠ INS — INS is insurance-as-a-regulated-industry, not
  insurance-as-a-benefit).
- Output: 200/200 valid labels, 65% single-topic, 30.5% multi-topic, 4.5%
  zero-topic. Hand-spot-checked: 100% correct on the health-insurance-vs-
  INS confusion (27/27 correctly routed away from INS); correctly
  distinguished genuine NFIP-focused releases from passing flood-insurance
  mentions in unrelated bills.
- **Held-out test of augmentation (label-expanded 200→283 training rows,
  retrained alongside the LDA data, evaluated on FRESH held-out press
  releases never seen by either model or Haiku):** confirmed a real,
  measurable effect in both directions — 13 new correct flood-insurance/
  NFIP matches gained (0 lost) on the recall side, but also 20 newly
  INCORRECT ACA/health-insurance-related INS matches introduced (0 before)
  on the precision side, even though none of the 200 pilot labels
  themselves mixed INS with health-insurance text. Diagnosed as a
  small-sample decision-boundary side effect (283 augmentation rows is
  very thin relative to INS's ~11,730 LDA-derived positive examples,
  compounded by `class_weight="balanced"` amplifying a small class's
  pull), not a labeling-quality problem — this is exactly why training
  proceeds in more than one round rather than one large batch off a single
  snapshot.

**Round 1 (not yet executed — this doc's forward-looking portion):**
1. **Disagreement sampling.** Run `M0.score_batch()` over a fresh random
   draw of press releases (a probe pool, e.g. 20,000). Take each release's
   max probability across all 75 non-excluded codes; releases landing in
   [0.15, 0.35] are the "ambiguous zone" — `M0` sees signal but isn't
   confident. Bucket by top-code pick and sample from the ambiguous pool
   *proportionally* to how much each code shows up there (not
   pre-selected codes) — verified corpus-wide result from this session:
   5,664/20,000 land in this zone with the excluded-code list correctly
   applied, spread across 20+ codes led by CIV/FOR/ECN/HCR/LAW/EDU/DEF/
   BUD/HOM.
2. **Random fill** — a separate plain-random draw, independent of `M0`'s
   opinion, so codes `M0` is *wrongly confident* about (not ambiguous,
   just wrong) get a chance to surface too.
3. **Label via Haiku subagent fan-out** (same prompt/format as the pilot,
   batches of ~200), merged and deduplicated against already-labeled
   releases (the pilot 200).
4. **Retrain** on LDA descriptions + pilot (200, label-expanded) + round 1
   (label-expanded) → `M1`.

**Round 2 (not yet executed):**
1. **Re-scan** — run `M1.score_batch()` over a FRESH random draw (excluding
   anything already labeled in the pilot or round 1) and find `M1`'s own
   ambiguous zone. This is the point of iterating: `M1`'s uncertainty
   profile will differ from `M0`'s, both because round 1 resolved some of
   what `M0` was unsure about and because augmentation can introduce new
   boundary drift elsewhere (as the pilot's INS/ACA bleed-through
   demonstrated).
2. **Label + retrain** the same way, on top of everything accumulated so
   far (LDA + pilot + round 1 + round 2) → `M2`.

**Open parameters — decided:**
- **Budget split: round 1 = 300, round 2 = 500** (of the remaining 800
  after the 200-release pilot). Deliberately uneven: round 1 is a first
  pass off `M0` against a still-broad, not-yet-understood ambiguity map
  (20+ candidate codes) — its job is mainly to generate the evidence for
  how the map *shifts* after augmentation, not to fully resolve anything.
  Round 2 gets the larger share once `M1`'s actual remaining uncertainty
  is known, so the bigger spend targets confirmed problems.
- **Per-code cap: 15%** of a round's disagreement-sampled budget for any
  single code. Sanity-checked against the actual distribution — CIV led
  the exploratory ambiguous-zone scan at ~12% of the pool, so 15% lets
  naturally-dominant codes get proportionally more attention without one
  code eating the whole round.
- **Ambiguity band: [0.15, 0.35], confirmed, not just assumed.**
  Sanity-checked against the real max-probability distribution over a
  20,000-release probe: median max-prob 0.428, 33% of the corpus sits
  below the 0.3 production threshold, and [0.15, 0.35] straddles that
  threshold rather than sitting arbitrarily far from it — i.e. it
  correctly targets cases near the actual decision boundary, not just
  low-confidence-on-everything cases.
- **Round-2 dedup: re-draw a fresh probe pool**, excluding only releases
  already labeled (pilot + round 1) — not round 1's unused candidate
  pool. Simpler, avoids sampling bias from reusing a stale pool, cheap to
  redo (one more `score_batch()` pass).

**Final evaluation (not yet executed):** held-out probe set — never
included in any labeled round — scored by `M2`, hand-spot-checked against
the known confusions (health-insurance-vs-INS, flood-insurance-genuine-
INS) plus whatever new confusable pairs rounds 1/2 surface. Same
before/after methodology as the pilot's held-out test. Only after this
holds up does `M2` become the classifier backing
`derived_press_issue_labels` / the `_ml` tables / `quiet-issue-quadrant-ml`.

## Approach (as executed so far)

### 1. Build the classifier as a standalone, reusable module — DONE

**Dependency:** `scikit-learn` (added via `uv add scikit-learn`, present in
`pyproject.toml`/`uv.lock` alongside the existing numpy/scipy/pandas).

`scripts/press_topic_classifier.py` — `PressTopicClassifier` dataclass:
- `load_activity_descriptions(con)` — every individual
  `senate_lobbying_activities.description` / `house_activities.description`
  row as its own training document (~1.47M rows). **Never pre-aggregate
  into one blob per code before fitting** — see Model-selection History
  above for what that pitfall does.
- `PressTopicClassifier.fit(con)` — fits `TfidfVectorizer(stop_words=
  "english", min_df=3, max_df=0.5, sublinear_tf=True)` then
  `LogisticRegression(max_iter=500, class_weight="balanced", C=1.0,
  solver="lbfgs")`, one-vs-rest over the 75 non-excluded codes. Excluded
  codes (`EXCLUDED_CODES = {"GOV","MIA","SCI","CON"}`) are dropped from the
  training data BEFORE fitting, not filtered from predictions after —
  carried over from `ISSUE_KEYWORDS`' own exclusion list; GOV re-confirmed
  generic under both the centroid and (by inheritance) logistic-regression
  approaches, MIA/SCI/CON excluded by analogy, not individually re-tested.
- `.score(text)` / `.score_batch(texts)` — `predict_proba`, comparable
  across codes by construction.
- `.is_low_confidence(code)` — flags codes with fewer than
  `LOW_TRAIN_VOLUME` (1,000) LDA training examples (APP/DOC/MON/REL/UNM in
  practice).

### 2. Threshold — DONE (0.3, global)

Validated by a sweep (0.15-0.60) across INS/TAX/ENV/VET/CPT/PHA/HCR/IMM/
AGR/MON/TOB plus hand-checked precision at 0.3 for ENV/VET/TAX/CPT — clean,
on-topic top matches for all, no repeat of the centroid approach's
false-positive pattern. `predict_proba`'s cross-code comparability is what
makes a single global threshold viable, unlike cosine similarity.

### 3. `derived_press_issue_labels` table + ingester — DONE, final (M0 only)

`scripts/build_derived_press_issue_labels.py` — grain `(release_id,
issue_code)`, columns `probability`, `is_primary` (argmax per release,
free from the same `predict_proba` matrix), `low_confidence`. NOT yet
registered in `build_gain_db.py`'s stage list — still a standalone script,
run manually (`python scripts/build_derived_press_issue_labels.py`).
`scripts/validate_press_issue_labels.py` — thin wrapper calling
`validate(con)` in the builder, reconciliation checks + coverage-delta
comparison against old keyword-map counts (point-in-time, hardcoded from
this session's audit — reported as a delta, not asserted as improvement
per se, since "fewer matches" is sometimes correct (precision fix) and
sometimes a real gap (the INS domain-mismatch finding)).

**Final state:** this table reflects `M0` (pure LDA classifier) — the
Haiku-augmented `M1`/`M2` retrain described below was abandoned (see FINAL
STATUS at the top of this doc). 100,541 rows as of end of session.

## Explicitly out of scope for this change (revised)

- **Migrating `derived_issue_quarter_volume_press` or
  `derived_committee_quarter_press` off `ISSUE_KEYWORDS`.** Reversed from
  the original plan — see the Verifiability Pivot section. Both keyword-
  based tables stay exactly as they are, INS bug included, undocumented as
  fixed because it isn't being fixed by deletion.
- **Migrating or duplicating `derived_member_press_topic_panel`** (the
  pre-existing orphan table). Its orphan/unregistered/undocumented status
  is a separate, pre-existing bug — not bundled into this redesign.
- Retroactively editing `investigations/critics-take-health-money`'s
  inline keyword set (closed case's evidence trail).
- Re-opening or re-verifying any past case's findings.
- Solving the GOV/MIA/SCI/CON generic-code problem — confirmed out of
  reach for the classifier too; stays excluded from training.
- Full LLM classification of the entire corpus — priced (~$75 one-time
  full-corpus, Haiku 4.5 + Batch API) and set aside as disproportionate;
  the ~1,000-release training-augmentation budget is a different, much
  smaller thing (labels a training SAMPLE, not the corpus being scored).
- **Any case citing `derived_press_issue_labels` / the `_ml` tables /
  `quiet-issue-quadrant-ml`'s counts as a standalone quantitative finding
  without a human read-through of the underlying releases.** This is now
  a hard rule, not a nice-to-have — see the Verifiability Pivot section.

## Verification — done vs. not done (end of session)

**Done:**
- `scripts/validate_press_issue_labels.py` runs clean against the final
  `M0`-based table (100,541 rows, threshold 0.3).
- `M0` itself was spot-checked extensively against INS/TAX/ENV/VET/CPT/PHA
  (see Threshold section above) — this is real, hand-verified evidence,
  distinct from the abandoned Haiku-augmentation evaluation.

**Not done — left for a future session, not blocking `M0`'s use:**
- No real precision/recall benchmark exists comparing `ISSUE_KEYWORDS` vs.
  `M0` vs. anything else. Everything so far is spot-check evidence, not a
  scored metric. Attempting to build one (a Haiku-labeled held-out test
  set) is what surfaced the labeling-quality problems that ended the
  augmentation track — the *test-set-building* problem turned out to be
  exactly as hard as the *training-augmentation* problem, for the same
  underlying reason (Haiku's surface-vocabulary matching on this specific
  75-way task). A future benchmark attempt should either use Opus (cheap,
  ~$5.50 for this volume, per the FINAL STATUS section) or a
  human-labeled set.
- `docs/press_topic_classification_methods.md` not written.
- `quiet-issue-quadrant-ml` sibling screen not created.
- `_ml`-suffixed sibling tables (`derived_issue_quarter_volume_press_ml`,
  `derived_committee_quarter_press_ml`) not created — `M0` currently only
  populates the standalone `derived_press_issue_labels` table; nothing
  downstream consumes it yet.
- Beat book (then the `gain-lobbying-investigation` skill, now
  `docs/beat_book.md`) not updated to mention the classifier.
- **Next session's actual priority, per direct instruction:** use `M0` to
  surface leads (via `fish-for-leads` or ad hoc querying of
  `derived_press_issue_labels`), not continue building out the
  classifier's supporting infrastructure. The unfinished items above are
  documented for completeness, not queued as next steps.
