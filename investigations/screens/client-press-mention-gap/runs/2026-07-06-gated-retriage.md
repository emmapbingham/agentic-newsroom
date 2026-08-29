# Gated re-triage of run 29 (before/after exhibit)

**Date:** 2026-07-06. **Purpose:** first exercise of the new surfacing gates
(`fish-for-leads/reference/lead-gates.md`) against a run that pre-dates them —
run 29 of `client-press-mention-gap` (1,402 candidates), which surfaced leads
54–58 (Gilead, Fluor, Emergent BioSolutions, RELX, Omeros) as five separate
rows under the pre-gate loop. Leads 54–58 are left untouched (NULL disposition,
awaiting editor triage as surfaced); this file records what the gated loop
would have surfaced instead.

## Gate 1 — template collapse: 5 → 1

All five leads instantiate one template: *"Company X reported $NM in Senate
lobbying income (2022–2026Q1) but ~zero congressional press mentions."* Under
the gates this is **one pattern-lead** with an exemplar table:

| entity | income | mentions | note |
|---|---|---|---|
| Gilead Sciences | $13.64M | 5 | highest spend in the near-zero tail |
| RELX Inc. | $6.64M | 0 | zero under all alias/brand variants; also an APRA-coalition member (see apra-lobbying-coalition E4) |
| Fluor Corporation | $5.48M | 2 | both mentions incidental |
| Emergent BioSolutions | $5.34M | 3 | one mention is *critical* |
| Omeros Corporation | $5.29M | 0 | clean true zero, alias-verified |

Editor cost: one read instead of five, for the same judgment surface.

## Gate 2 — actor test: named actors, but no *act*

The screen is registered `grain='actor'` (rows are clients), but the anomaly
each row exhibits is an **absence property** (never named in member press),
and the only action behind it is routine lobbying. No candidate shows a
choice — no surge, no switch, no going-quiet. So the per-entity rows are weak
as stories; the drill hooks that would upgrade them are: (a) Omeros — what its
own filing descriptions say it wants (drilldown started in the surfacing
session); (b) RELX — the cross-link to the APRA coalition case, where it is
already a worked example.

## Gate 3 — boring explanation (written first)

Congressional press mentions measure *constituent-facing salience*, not
lobbying attention received. Firms with B2B/procurement/IP-facing asks (RELX:
data analytics; Fluor: government construction; Emergent: BARDA contracts)
give members no constituent story to name them in — high spend + low mentions
is the *expected* profile for that class. The shortlist's own top confirms the
gradient (Qualcomm: $27.6M, 13 mentions). This suppresses the per-entity
framing ("X is suspiciously quiet") but not the pattern framing ("which class
of money is systematically invisible in member communication, and is the
near-zero tail explained by business model alone?") — Emergent's *critical*
mention and Omeros's true zero don't fit the innocent account cleanly.

## Gate 4 — novelty-lite (bounded; 2 searches, 2026-07-06)

- "Gilead Sciences federal lobbying spending congressional attention" — hits
  are OpenSecrets/Quiver aggregator pages of the same LDA totals; no dated
  article makes the spend-vs-mention-gap finding. **Miss.**
- "Omeros Corporation lobbying Congress" — OpenSecrets profile only. **Miss.**

Misses are weak evidence (bounded search); the surviving lead surfaces
*without* any novelty claim. The case-level scan still owns the verdict if
promoted.

## Net result

Pre-gate loop: **5 leads** surfaced (editor read all five; 0 promoted).
Gated loop: **1 pattern-lead** — "the press-invisible money: ~$36M of lobbying
income across 5 verified entities with ≤5 congressional mentions each;
boring-explanation (B2B salience) accounts for most of the tail but not the
critical-mention and true-zero exemplars" — with the two drill hooks attached.

**Suggested dispositions for leads 55–57 (Fluor, Emergent, RELX) and 54 or 58:**
`duplicate-of` the retained pattern exemplar, reason "template-collapsed
(gated retriage 2026-07-06)". Left for the editor to apply — the retriage ran
after surfacing, and triage verdicts are the editor's to record.
