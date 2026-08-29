# Tariff stance classification — enrichment spec

**Status:** specified, **held for the desk to run** (first LLM-enrichment job).
**Decided:** 2026-06-15 (taxonomy + scope approved by editor).

The project's first **LLM-as-data-producer** job: classify what each tariff (TAR)
lobbying activity is *asking for*, so the case's "mostly seeking relief" narrative
(E8/E9, built from 10 hand-read descriptions) becomes a **quantified, baselined
split**. Produces a reference-tier `derived_*` table with per-row `method` +
`confidence`, per the data-layers model (LLM output → reference tier, filterable
by confidence).

## Consumer (the gate: no consumer, no build)

The `tariff-2025-stealth-surge` case. Specifically it (1) replaces the
illustrative relief-vs-protection claim with a measured split, (2) supplies the
**baseline contrast** that makes the new-entrant finding interpretable (do
newcomers skew more to relief than established players?), and (3) quantifies the
**under-reported seam** the novelty-scan identified — coverage asserts "mostly
relief" anecdotally; nobody has measured it.

## Scope & unit

- **Population:** **all Senate TAR activity, all years** (`general_issue_code =
  'TAR'`), not just 2025 and not just the new-entrant cohort. The whole market is
  required for the baseline; all years buys a *temporal* baseline (was the market
  always relief-skewed, or did the 2025 blitz flip it?). House is a later
  extension (Senate-only v1: stable ids, panel-aligned, avoids cross-chamber
  double-counting via the bridge).
- **Classification unit:** **distinct normalized description**
  (`TRIM(LOWER(description))`), not rows — descriptions are heavily templated.
  ~**1,156** distinct all-years (~650 in 2025). Label once, join back to
  activities.
- **Dedup before aggregating:** the headline split is computed over **canonical
  (latest-posted) filings** per (registrant, client, year, period) — the same
  dedup the income/issue panels use — so amendments/duplicate re-files don't
  inflate the denominator.

## Cohort tagging (deterministic, not LLM)

A column on the output table, derived in SQL (reconcile against E2: ~126 + ~85):

- `genuinely_new` — first TAR year = 2025 **and** no TRD activity before 2025
  (the ~126; logic = `queries.sql` q8/q9).
- `incumbent_adding_tar` — first TAR year = 2025 **and** had pre-2025 TRD (~85).
- `established` — TAR activity before 2025.

## The taxonomy (5 labels) — the classifier rubric, verbatim

**Central rule — classify the *direction of the ask*, not the instrument.**
Section 232/301, IEEPA, AD/CVD, de minimis, USMCA are direction-neutral: the same
instrument appears on both sides ("301 *exclusion* letters" = relief; a domestic
petition *for* AD/CV duties = protection). The label is the ask, never the
mechanism.

**Decision order (top-down, first match wins):** directional ask? →
`relief`/`protection`/`mixed`. No ask but passive watching posture? →
`monitoring`. Else → `unclear`.

| Label | Definition | Signals | Example (real) |
|---|---|---|---|
| `relief` | Seeks to **reduce, remove, avoid, delay, or be exempted from** a tariff burden on itself / its inputs / its products — or (foreign actors) remove a U.S. tariff on their goods / avoid retaliation. | exclusion/exemption sought or *maintained*; "tariff relief"; advocacy *against* imposing/raising; duty suspension, refund, delay; market-access restoration; opposing retaliation. | "Tariff exclusion"; "…advocated… to not impose reciprocal tariffs…"; "maintaining exemption for USMCA-qualified goods…" |
| `protection` | Seeks to **impose, raise, maintain, or strengthen enforcement of** tariffs/barriers on imports/competitors, to its own benefit. | support for new/continued import tariffs; petitioning *for* AD/CVD; closing de minimis to "level the field"; domestic-sourcing/Berry enforcement; barrier-driven "domestic manufacturing." | "…tariffs and increased domestic manufacturing capabilities." (implicit). **Rarer, often implicit → lower confidence; red-team these.** |
| `monitoring` | Watching/tracking is the **entire** disclosed activity; no ask either way. | passive verbs are the whole story — monitor, track, report on, stay apprised, assess impact — no advocacy. | "Monitor and report on trade and tariff discussions." |
| `mixed` | The same description discloses asks in **both** directions. | e.g. exclusion on imported inputs *and* tariffs on competing finished goods. **Expect small.** | (compound; rare) |
| `unclear` | Tariffs named, but **no determinable direction or posture.** | topic-only; instrument-only; or advocacy stated with direction withheld. | "Issues related to Canadian tariffs."; "de minimis"; "Advocate for automobile manufacturers… in tariff negotiations." |

**Cross-cutting rules (go in the prompt verbatim):**
1. **Ask beats posture.** "Monitor and advocate for exclusion" → `relief`. Active
   engagement with no stated direction ("engage on tariff policy") → `unclear`,
   not `monitoring` (monitoring needs the passive language).
2. **Classify the disclosed text, not inferred intent.** A "monitor" filing may
   hide an ask; label what's filed.
3. **Actor context is a confidence *booster*, not a label-maker.** "Advocate for
   automakers on Section 232 tariffs" probably means relief — but if the text
   doesn't say *reduce*, mark relief at **low** confidence (or `unclear`). Don't
   import outside knowledge ("Schaeffler is German → relief") as if disclosed —
   same anti-laundering discipline as the news firewall.
4. **Multi-issue descriptions:** classify only the tariff-relevant clause; if it
   has no direction → `unclear`.
5. `unclear` is a **deliverable**, not just residual: a large share is a finding
   about how little these filings disclose, and the honest denominator for "X% of
   *classifiable* activity sought relief."

## Classifier (Haiku) — prompt skeleton & output

Model **claude-haiku-4-5**. Batch ~25 descriptions/call; the rubric above is the
static system prompt (prompt-cached). Structured output per item:

```json
{ "id": "<desc index>", "label": "relief|protection|monitoring|mixed|unclear",
  "confidence": 0.0,            // reflects what the TEXT supports (rule 3)
  "rationale": "<=15 words, quoting the operative phrase" }
```

`rationale` is for audit only (never a published claim). High confidence requires
an explicit directional verb in the text; inferred direction → lower.

## Output table — `derived_tariff_stance` (reference tier)

Grain: one row per **canonical** Senate TAR activity. Built by
`scripts/build_derived_tariff_stance.py`, which (a) reads the desc-level
classification map (the raw Haiku output, stored in this case's `derived/` as
case-local work product), (b) joins it to activities by `desc_norm`, (c) attaches
the deterministic `cohort` tag, (d) restricts the headline aggregate to canonical
filings.

| Column | Notes |
|---|---|
| `activity_id`, `filing_uuid` | source keys (provenance) |
| `registrant_id`, `client_id`, `filing_year`, `filing_period` | join keys |
| `description`, `desc_norm` | raw + normalized classification key |
| `stance_label` | relief / protection / monitoring / mixed / unclear |
| `stance_confidence` | 0–1, per rule 3 |
| `cohort` | genuinely_new / incumbent_adding_tar / established |
| `method` | e.g. `claude-haiku-4-5; rubric v1` (model + prompt version) |

Catalog it in `docs/derived_db.md` on landing (grain, builder, "questions this
answers", caveats). Reference tier — **filter by confidence** before any headline.

## Run plan (run-economics: pilot before fan-out)

1. **Gold set:** hand-label ~40 descriptions (stratified: clear relief, clear
   protection, monitoring, boilerplate, multi-issue) — the ground truth.
2. **Pilot:** one Haiku agent over the gold set. Measure tokens + agreement vs
   gold; inspect disagreements; tune the rubric/prompt if needed.
3. **Set the confidence threshold** from the pilot's score distribution (mirror
   the honoree-map ≥0.9 discipline; the one parameter set empirically).
4. **Fan out** over all ~1,156 distinct descriptions (~0.12–0.15M tokens total,
   ~5–7% of one grid sweep). Log model + rubric version.
5. **Build** `derived_tariff_stance`; reconcile against E8/E9 (the 10 hand-read
   descriptions must land where we read them) — build-time premise reconciliation.
6. **Verify** (independent builder → red-team → adjudicator,
   `track-investigation/reference/verification.md`): red-team re-checks a sample
   (esp. all `protection` calls and low-confidence `relief`), confirms the split
   holds at the chosen threshold, and that `unclear` isn't hiding directional
   asks. Only then does the split become report-grade.

## Provenance & caveats

- Every classified row carries its `filing_uuid` + the exact `description` — the
  label is a **model-inferred attribute of the filed text**, never a fact from
  the record. Headlines are computed at the confidence threshold and quote the
  raw description.
- Client country reads "US" for foreign-owned subsidiaries (beneficial ownership
  hidden) — the foreign-ownership share is a *separate* owed step, not this job.
- Senate-only v1; House extension would dedup via the cross-chamber bridge.
