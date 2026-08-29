## 2026-06-16

- did: promoted lead from LEADS.md; created case folder; ran novelty scan
- found:
  - E1: Smith $9.16M, z=6.45, out-raises Speaker and all GOP-House peers (screen run 9)
  - E2: resolution clean — 60+ honoree variants, all conf ≥ 0.9, no cross-member
    contamination; $7.64M at conf=1.0, $1.54M at conf=0.9 (middle-name variants)
  - E3: name-resolution yield caveat documented — Smith's uniqueness means peers
    with common surnames may be *under*-counted, making his rank conservative but
    the peer mean also understated
  - E4: gavel-year spike confirmed from LD-203: 2022 $1.35M → 2023 $2.67M (2×),
    2025 $2.91M; independently corroborated by Bloomberg Tax FEC data (Q1 2023)
  - E5: committee roles confirmed (W&M Chair, JCT Vice Chair); no other assignments
    in member_committees
  - E6: prior-chairs comparison not feasible — Brady/Camp/Ryan predate 2022 corpus
  - novelty scan: `under-reported` — Bloomberg Tax (2023) reported the gavel spike
    from FEC data; no outlet has done the LD-203 cumulative ranking vs. leadership
- dead ends: prior-chairs comparison in LD-203 data (corpus window too narrow)
- open questions:
  1. Does Smith hold a formal NRCC or party fundraising-arm role? (external lookup
     required — this is the single most important open item; if yes, the outlier
     is structurally explained and the W&M-gavel framing weakens)
  2. Year-over-year gavel-transition spike test: the `chair-transition-contribution-spike`
     screen (planned for `chair-power-premium` case) would quantify this more
     rigorously and shared analysis would strengthen both cases
  3. Sector decomposition: does Smith's haul track tax/tariff-adjacent industries
     specifically? Would require sector coding of registrants (not yet built)
  4. FEC cross-check: total fundraising (not just LD-203 slice) for comparison
     with the Bloomberg Tax number and to contextualize the LD-203 fraction
- NEXT: external lookup — confirm or rule out any NRCC/leadership-arm role for
  Smith (Congress.gov, NRCC site, news search). This is deskside, free, single
  step. If no such role found, confidence rises and the gavel-transition spike
  test becomes the next analytical step.

## 2026-06-16 (continued)

- did: external lookup — NRCC/leadership role check (bounded web search, 6 queries)
- found: **No formal NRCC officer title or conference leadership role** in the
  119th Congress. Current formal roles: W&M Chair + JCT Vice Chair only.
  Past roles (Conference Secretary 2017–2021; Budget Ranking Member 2021–2023)
  lapsed at gavel handoff Jan 2023 — do not explain 2023–2025 elevated haul.
  Informal NRCC fundraising activity (~$2.75M raised *for* NRCC) is activity,
  not a structural title; noted as color in E5. (E5 updated.)
- dead ends: NRCC officer lists (Jan 2023 and Jan 2025 cycles) — Smith not listed
- open questions:
  1. Gavel-transition spike test: `chair-transition-contribution-spike` screen
     (planned for `chair-power-premium`) would quantify the 2022→2023 jump
     rigorously and strengthen both cases simultaneously
  2. Sector decomposition: does Smith's haul track tax/tariff-adjacent industries?
     Requires sector coding of registrants (not yet built)
  3. FEC cross-check: what fraction of his total FEC haul does the $9.16M
     LD-203 slice represent?
- NEXT: the leadership boring explanation is cleared — confidence rises to
  medium-high. Next analytical step is the gavel-transition spike test (shared
  with `chair-power-premium`), or sector decomposition if a registrant-sector
  instrument gets built.

## 2026-06-16 (continued)

- did: (1) queried all LD-203 contribution types for Smith; (2) external FEC
  lookup via FEC.gov and search snippets (OpenSecrets returned 403)
- found:
  - E7: Smith unremarkable on Honorary Expenses (rank 127, z≈-0.05) and Meeting
    Expenses (rank 30, z≈-0.33). FECA outlier status is type-specific, not a
    generic salience-inflation artifact across all LD-203 reporting.
  - E8: FEC independently corroborates — $4.61M in the 2024 cycle alone from a
    safe R+25 district (typical safe-seat: $1–2M). 2026 pace ($4.46M through
    March) on track to exceed that. LD-203 $9.16M across two cycles aligns with
    FEC per-cycle pace; no obvious inflation. Two independent datasets, two
    independent filing regimes, same outlier signal.
  - Salience-inflation theory substantially weakened on both fronts: (a) non-FECA
    LD-203 types are unremarkable, and (b) FEC corroborates without any LD-203
    mechanism at all.
- dead ends: OpenSecrets lobbyist-contribution breakdown (FEC filtered by
  occupation = lobbyist) — returned 403/paywalled. Not retrievable without
  FEC itemized data ingest or subscription.
- open questions:
  1. FEC lobbyist-contribution breakdown (occupation-filtered) — owed if case
     goes toward publication; requires FEC itemized ingest or LegiStorm/OpenSecrets
     subscription. This is the one remaining data gap that could tighten the
     LD-203-to-FEC comparison on the lobbyist-specific slice.
  2. Gavel-transition spike test (shared with `chair-power-premium`)
  3. Sector decomposition (requires registrant-sector instrument)
  4. Prior W&M chairs comparison (requires FEC data pre-2022)
- NEXT: case is in strong shape for the core claim. Remaining items are
  deepening steps, not blockers. Recommend proceeding to builder → red-team →
  adjudicator verification, or running the gavel-transition spike test first
  (deskside, shared with `chair-power-premium`).

## 2026-06-17

- did: ran `chair-transition-contribution-spike` screen (run 10, registered in
  newsroom.db) — gavel-transition spike test across all 24 current R House
  full-committee chairs, using 2022 as the pre-gavel baseline
- found: E9 — Smith's 2022→2023 spike is 1.98×, the highest in the cohort;
  cohort mean is 1.06× (flat). Natural experiment is clean: all chairs took
  gavels simultaneously Jan 2023. Sustained through 2025 (avg_post_vs_pre=1.82×).
  Notable secondaries: Guthrie (E&C) shows a lagged spike (flat 2023, then
  strong 2024–25 — E&C jurisdiction hot later); Steil's high 2022 baseline
  confirms NRCC role shows up as elevated pre-treatment, not a transition spike.
  Shortlist: `investigations/screens/chair-transition-contribution-spike/run-10/shortlist.csv`
- dead ends: none
- open questions:
  1. Neal comparison — closest within-corpus prior-chair peer; deskside, cheap
  2. Sector decomposition — requires registrant-sector instrument (not yet built)
  3. FEC open threads (prior chairs, lobbyist-occupation slice, full peer rank)
     — requires FEC bulk ingest if case goes toward publication
- NEXT: Neal comparison (one query, deskside) then consider builder → red-team
  → adjudicator verification for the core claim.

## 2026-06-17 (continued)

- did: Neal comparison — year-by-year FECA for Smith and Neal, who held the
  W&M gavel in opposite halves of the corpus window (q9)
- found: E10 — the gavel flip is visible as a mirror image in both directions
  simultaneously. Neal 2022→2023: −17% (lost gavel). Smith 2022→2023: +98%
  (gained gavel). Same committee, opposite role changes, opposite trajectories.
  Neal's 4-year total $6.39M puts him #2 among House Democrats (z=5.36) —
  the ranking member position on W&M is itself powerful, which means Neal's
  modest drop understates the true gavel effect (his counterfactual as a
  backbencher would have dropped further). Smith's asymmetrically larger gain
  likely reflects both the structural gavel effect and the W&M jurisdiction
  becoming exceptionally hot in 2023–25 (tariff/tax fights).
- dead ends: none
- open questions:
  1. Sector decomposition — requires registrant-sector instrument (not yet built)
  2. **Data expansion options (both deferred — not blockers for core claim):**
     - *Pre-2022 LD-203:* the LDA bulk data goes back to ~2008 in the same JSON
       format; extending the Senate ingester would cover Neal's 2019 gain
       transition and Brady's full W&M tenure. Best framed as a corpus-wide
       expansion (benefits multiple leads) rather than a case-specific pull.
       Estimated cost: ~4 years × ~500MB–1GB JSON; build time comparable to
       the existing Senate ingest (~2–3 min/year).
     - *FEC bulk data:* would enable prior-chairs cycle totals, full House peer
       ranking, and occupation-filtered lobbyist-contribution slice. Separate
       filing regime, separate ingest pipeline needed. Larger investment.
     Both serve the same purpose — historical context for the prior-chairs
     comparison — and neither changes the primary finding (Smith is a current
     outlier). Revisit if case goes toward publication and editors want the
     historical baseline.
- NEXT: the core evidence base is now strong (E1–E10). Recommend moving to
  builder → red-team → adjudicator verification for the core claim.

## 2026-06-17 (continued)

- did: builder → skeptic → judge verification (inline, three roles; 13 skeptic checks)
- found: SUPPORTED — all core numbers re-derive exactly (E1/E4/E9/E10); 13/13 checks
  passed; no junk, no contamination, no double-counting, no denominator error;
  surviving objections are framing/disclosure only (see evidence.md E-verification entries)
- verdict written to case.md; full check-by-check detail in this log file's prior
  state (transcript saved in repo history)
- NEXT: case is verified. Ready for findings report write-up.

## 2026-07-02

- did: user review of case for wrap-up; user flagged the case felt thin
  ("one mildly interesting number") without a prior-W&M-chairs comparison;
  before deciding whether to pull the deferred FEC bulk-ingest thread,
  re-ran the novelty scan on the *general* claim ("is the W&M chairmanship
  historically a money magnet") rather than the narrow one the 2026-06-16
  scan asked ("has anyone ranked Smith against LD-203 peers")
- found: general claim is well-covered, not novel. The "party dues" system
  (chairs of top "A" committees, W&M named explicitly, expected to raise
  $600K-$1.2M+ for the party per cycle) is institutionalized and documented
  (Brookings 2017). Roll Call, Feb 9 2023 ("Gavels for top House committees
  don't always come cheap"), reporting an Issue One study, already named
  Jason Smith specifically as the top 2022 party-money mover among all "A"
  committee chairs/ranking members in the same Jan 2023 transition window
  this case's E9/E10 independently re-derive from LD-203. Full reasoning
  in case.md Verdict.
- dead ends: none new — this closes the open question of whether to pull
  FEC bulk data for a prior-chairs comparison; decided not to, since it
  would likely only reconfirm the already-reported dues system
- NEXT: none — case killed, see Verdict in case.md
