# Stance-classification pilot — report

**Date:** 2026-06-15. **Purpose:** before fanning out over ~1,156 distinct TAR
descriptions, measure classifier accuracy on a hand-labeled gold set and choose
the model + thresholds. Run-economics: pilot before any fan-out.

## Setup

- **Gold set:** 40 distinct descriptions, stratified (relief/protection-signal,
  monitoring, boilerplate, multi-issue, middle), hand-labeled by Opus applying
  the rubric. Distribution: relief 21, unclear 12, monitoring 6, protection 1,
  mixed 0. Artifacts: `derived/pilot_gold.json`, `derived/pilot_input.json`
  (blind input, no labels).
- **Classifiers:** blind agents reading only the rubric + input, writing
  `{id,label,confidence,rationale}`. v1 = Haiku + rubric in spec. v2 = Haiku &
  Sonnet + `analysis/classifier_prompt_v2.md` (rubric hardened against the v1
  error patterns; both models read the *same* file → clean model comparison).

## Results vs gold

| Run | Raw (5-way) | Collapsed (relief/protection/mixed/no-ask) | Directional errs | False protection | ≥0.8 conf |
|---|---|---|---|---|---|
| Haiku v1 | 72% | 88% | 5 | 1 | 88% (24 kept) |
| Haiku v2 | **85%** | 85% | 6 | **0** | 85% (26 kept) |
| Sonnet v2 | **85%** | **88%** | 5 | **0** | **91% (34 kept)** |

- **High-trust directional calls (both v2 models agree, both conf ≥0.8): 16/16 =
  100% match gold.** The headline-bearing rows are clean.
- **≥0.9 confidence → 100% agreement** for both v2 models.
- v2 fixed all 6 of v1's monitoring↔unclear errors (the rubric's "monitoring
  requires a watching verb" rule worked).

## What the errors are (and why they're safe)

- **No false-protection in v2** (both models). The dangerous direction —
  inventing a protection ask — is gone. Errors are *conservative*: relief
  under-called as mixed/unclear, never protection inflated.
- **Residual weakness is shared by both models**: over-calling `mixed` on
  multi-clause relief items that contain a rhetorical nod to "American
  manufacturing" (#16, #17) or a secondary clause (#22). Because both models share
  it, their agreement does **not** validate these — but `mixed` items route to the
  red-team anyway, and the error shrinks (not inflates) the relief share, so the
  "mostly relief, protection rare" conclusion is robust to it.
- **Sonnet-only**: occasionally upgrades a bare "MTB/GSP" mention to relief by
  instrument semantics (#6, #38). This exposed a real rubric gap — MTB/GSP are
  inherently duty-*relief* programs, unlike direction-neutral 232/301 — fixed in
  v3 (supporting MTB/GSP = relief; a bare mention with no verb is still unclear).

## Decision

- **Fan out with BOTH classifiers (Haiku v2 + Sonnet v2)** over all ~1,156
  descriptions and use **inter-model agreement as the quality gate**: where they
  agree (empirically 100% precise on high-conf directional calls), auto-accept;
  route **disagreements + any `mixed`/`protection` + either-conf < 0.8** to a hand
  red-team. Cost ≈ 0.3M tokens total (~2 sweeps' worth ÷ 7), still trivial.
- Headline split computed on auto-accepted rows at conf ≥ 0.8; the red-team bucket
  reported separately with its own denominator.
- Substantive bonus: even a protection-oversampled draw yielded **1/40** true
  protection — early corroboration of the "mostly relief" narrative.

## Caveats

- Gold is single-annotator (Opus). The same-40 re-pilot measures "did the v2
  fixes land," not an unbiased accuracy estimate — the fan-out's own inter-model
  agreement + the red-team are the real validation before report-grade.
- The dual-classifier agreement is a *floor* on precision, not proof: shared
  failure modes (the `mixed` over-call) pass the gate, so the red-team must still
  sample agreed-relief rows, not only disagreements.
