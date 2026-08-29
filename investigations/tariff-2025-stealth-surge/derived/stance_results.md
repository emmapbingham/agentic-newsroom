# Tariff stance — classification results (substrate for E10)

**Run:** 2026-06-15. Dual-model (Haiku-v3 + Sonnet-v3) classification of all **1,156
distinct all-years Senate TAR descriptions**; **Opus adjudication of 173 contested
rows**; canonical-filing dedup. Pipeline/method: `analysis/pilot_report.md`,
rubric `analysis/classifier_prompt_v2.md` (v3), build
`analysis/build_stance.py`. Labels are **LLM-produced (reference tier) — filter by
confidence.**

## Pipeline accounting
- 1,156 distinct descriptions → Haiku + Sonnet (16 agents, 370K tok). Exact
  agreement **87%**, collapsed (relief/protection/mixed/no-ask) **89%**.
- Contested **173** (154 disagreements + 18 agreed mixed/protection + 1 shaky) →
  Opus (3 agents, 98K tok). 983 auto-accepted on agreement.
- Activities: 3,283 TAR activity rows carry a stance → **2,940 canonical** after
  latest-posted dedup per (registrant, client, year, period).
- Cost ≈ $2.2 API-equivalent (~0.47M tokens, ~21% of one grid sweep).

## The split (canonical activities; directional = relief + protection + mixed)
| Scope | n directional | relief | protection | mixed |
|---|---|---|---|---|
| All years, all conf | 683 | 86% | 8% | 7% |
| All years, conf ≥0.8 | 539 | **92%** | **4%** | 4% |
| 2025, all conf | 177 | 86% | 8% | 6% |
| 2025, conf ≥0.8 | 146 | **90%** | **5%** | 5% |

**Relief outnumbers protection ~9:1 (all) to ~21:1 (high-confidence).**

## The baseline contrast (2025 canonical) — why we classified the whole market
| Cohort | n canonical | directional n | relief% | protection% |
|---|---|---|---|---|
| genuinely-new 2025 | 371 | 37 | 84% | 8% |
| incumbent adding TAR 2025 | 345 | 40 | 90% | 8% |
| established (pre-2025 TAR) | 563 | 100 | 86% | 8% |

**The relief skew is market-wide, not a newcomer trait.** New entrants are *not*
more relief-seeking than incumbents (84% vs 90%); protection is a steady ~8%
across every cohort. The new-entrant story is about **entry/volume** (who showed
up — E2/E3/E5), *not* a distinctive **stance**. Classifying only the cohort
(without the baseline) would have falsely credited newcomers with a distinctive
relief posture — the baseline is what prevents that error.

## Disclosure-quality finding (the denominator)
Only **~23% of canonical TAR activity discloses a determinable direction**
(683/2,940 all-conf; 539 at conf ≥0.8). The remainder is `unclear` (topic /
instrument / bill named, no ask — 2,127) or `monitoring` (130). Every "% relief"
above is among the **classifiable minority**; most tariff-lobbying filings don't
state what they are asking for — itself a reportable fact about LDA disclosure.

## Reconciliation vs E8/E9
E8/E9 (10 hand-read descriptions) said the genuine-new cohort is "mostly relief,
protection minority." **Confirmed and quantified:** genuine-new directional = 84%
relief / 8% protection. The illustrative read held; the new contribution is the
measured market-wide magnitude **and** the baseline that reframes it.

## Caveats / red-team scope (before report-grade)
- **LLM-produced labels** (Haiku + Sonnet + Opus); reference tier. Precision floor
  = dual-model agreement (100% on high-trust directional calls in the pilot). The
  red-team must still: verify **all `protection` calls** (52 canonical all-years),
  sample agreed-`relief`, and confirm `unclear` isn't hiding directional asks.
- **id 78** adjudication is self-contradictory (label `relief`, rationale argues
  `protection`) — re-label by hand.
- **Cohort directional n is small** (genuine-new = 37) → cohort percentages are
  noisy; the robust statement is the market-wide all-years split.
- A couple of `mixed` adjudications hinge on "extend 301 *tariffs*" vs "extend 301
  *exclusions*" wording (#251, #305) — spot-check.
- Senate-only; a House extension would dedup via the cross-chamber bridge.

## Files
`derived/dual_classified.json` (both models, all 1,156) · `derived/contested.json`
+ `derived/adj/` (the 173) · `derived/final_map.json` (combined) ·
`derived/tariff_stance_activities.csv` (activity grain + cohort + canonical flag) ·
`derived/stance_summary.json` (these numbers).
