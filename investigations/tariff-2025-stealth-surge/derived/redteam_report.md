# Red-team of the LLM stance labels

**Date:** 2026-06-15. **Method:** an independent Opus verifier re-classified a
94-item worklist **blind** (no prior labels shown) and **strict on `protection`**,
applying rubric v3. Worklist = all 21 distinct `protection` descriptions
(exhaustive) + all 12 `mixed` (exhaustive) + a deterministic 30-item sample of
agreed-`relief` + a 30-item sample of agreed-`unclear` + id 78. Inputs:
`derived/redteam_worklist.json` (blind), `derived/redteam_labels.json` (verdicts),
`derived/redteam_key.json` (hidden pipeline labels).

## Verdict: the finding holds, and every correction is conservative for it

| Bucket (pipeline) | n | blind verifier confirms | note |
|---|---|---|---|
| `protection` | 21 | **15** | 6 did not survive a strict blind pass |
| `mixed` | 12 | 6 | noisy (the known-weak class) |
| `relief` (sample) | 31 | **29 (94%)** | robust |
| `unclear` (sample) | 30 | 24 | 6 actually had a (relief) direction |

### Protection (exhaustive, the high-stakes class): 15/21 confirmed
Confirmed (strong, conf 0.75–0.95): ids 108, 171, 172, 364, 635, 636, 637, 813,
933, 934, 964, 965, 966, 967, 1092. **Refuted → `unclear`** (strict: an instrument
/ petition / "inclusion" is *named* but no support-verb is stated — don't infer
the ask): id 119, 275 (Auxin AD/CVD circumvention petition — named, not endorsed),
366, 367 ("inclusion of fabricated steel in the 232 tariffs" — no verb).
**Disputed → conservatively `unclear`**: id 299, 300 ("disapproving the Commerce
rule suspending liquidation/duties under Proclamation 10414" — genuinely
confusing; pipeline read protection, verifier read relief; needs a human call if
ever cited). Net: canonical protection activities **52 → 42**.

### Mixed (exhaustive): the known-weak class, corrected
2 → `relief` (id 251, 305 — the "extend 301 *exclusions*" vs "extend 301 *tariffs*"
wording trap the pipeline fell into), 2 → `protection` (id 757, 758 — "maintenance
and strengthening of 201/301/232; new 232 tariffs" is clear protection), 1 →
`unclear` (578), 1 → `relief` (783, "Oppose Tariffs on Canada/IEEPA"); 6 stay
`mixed`.

### id 78 resolved → `protection`
The self-contradictory adjudication ("Advocating against the renewal of the
exclusion to the Section 301 tariffs") — opposing an exclusion keeps the tariff
up = protection. Both the contradiction flag and the blind verifier agree.

### relief (sample): 94% confirmed — robust
2 flips: id 78 (→ protection, handled above) and id 106 (→ unclear, "drawback of
taxes/customs; no tariff direction").

### unclear (sample): relief is UNDER-counted
6/30 sampled `unclear` items actually carry a relief direction the base
classifiers missed — almost all via **MTB/GSP** mentions (id 202, 252, 464, 752,
879, 1023). So the true relief share is if anything **higher** than reported, and
the ~23% "discloses a direction" rate is a **lower bound** (the MTB/GSP bare-mention
boundary is the fuzzy edge).

## Red-teamed split (canonical, all-years, corrections applied to audited buckets)
**relief 593 (90%) / protection 42 (6%) / mixed 23 (3%)** of 658 directional
activities — **relief:protection ≈ 14:1** (was ~11:1 all-conf; the high-confidence
cut was ~21:1). The relief-dominance and market-wide findings are unchanged;
protection is now measured **smaller**, the conservative direction.

## Residual caveats for report-grade
- **Name protection examples individually**: 6/21 protection calls failed a strict
  blind pass, so any *named* protection actor in the report must be verified from
  its filing (the robust set is the 15+2 confirmed ids above); avoid id 299/300.
- **Relief is a lower bound** (the `unclear` bucket hides MTB/GSP relief); state
  the disclosure-rate denominator as approximate at that boundary.
- **Same model family**: the verifier is Opus, as was the adjudicator —
  correlated errors are possible. The blind + strict design and the conservative
  direction of all corrections bound the risk; a human spot-check of the 15
  confirmed protection calls would close it fully.
