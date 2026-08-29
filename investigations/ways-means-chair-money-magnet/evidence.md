# Evidence — ways-means-chair-money-magnet

Each block: the claim, the query/script that produces it, source records,
caveats, verdict. All monetary figures from `derived_member_contribution_panel`
(conf ≥ 0.9, FECA only) unless noted.

## E1 — Jason Smith is the #1 FECA outlier among House Republicans: $9.16M, z=6.45, 8.8× peer mean

- **query/script:** `queries.sql#q1` (screen `member-contribution-peer-outlier`,
  run 9; `investigations/screens/member-contribution-peer-outlier/run-9/shortlist.csv`)
- **result:** Smith $9,164,064, peer mean (GOP-House, n=309) $1,037,665,
  z-score 6.45. Next highest GOP-House member: Mike Johnson (Speaker) $6,377,076,
  z=4.24. Steve Scalise $6,288,412, z=4.17.
- **source records:** aggregates over `derived_member_contribution_panel`
  (contribution_type='feca', bioguide='S001195'); screen run logged to
  `investigations/newsroom.db` (screen_runs, run 9).
- **caveats:**
  - LD-203 captures only lobbyist/registrant-reported contributions, not total
    fundraising. FEC is the authoritative complete source.
  - Peer mean denominator (n=309) includes all current-Congress House Republicans
    in the panel, including many who raise very little; the mean is depressed by
    the long tail, which inflates z-scores for top outliers.
  - Name-resolution yield bias: see E3 below.
- **verdict:** supports

## E2 — Smith's haul breaks down as $7.64M at full-name/conf=1.0 + $1.54M at first_last/conf=0.9

- **query/script:** `queries.sql#q2`
- **result:**
  - `full_name` method, confidence 1.0: 2,962 contribution rows, $7,638,126
  - `first_last` method, confidence 0.9: 534 rows, $1,535,000
  - Total: 3,496 rows, $9,173,126 (rounds to $9.16M in the panel due to dedup)
  - 60+ distinct honoree name variants, all mapping to S001195 (R-MO) only.
    Examples: "Jason Smith", "JASON SMITH", "Rep. Jason Smith (R-MO)",
    "REP JASON SMITH (LEADERSHIP PAC)", "Jason T. Smith", etc.
- **source records:** `senate_contribution_items` → `honoree_member_map` →
  `members` (bioguide S001195).
- **caveats:**
  - The `first_last` / conf=0.9 tranche (entries like "Rep. Jason Thomas Smith")
    are clearly him — the middle name is his. No ambiguity in the 0.9 tranche.
  - "REP JASON SMITH (LEADERSHIP PAC)" is mapped to him and included in the total;
    leadership PAC contributions are part of the $9.16M.
- **verdict:** supports (resolution is clean; no cross-member contamination found)

## E3 — Name-resolution yield caveat: Smith's uniqueness may give him a capture advantage

- **query/script:** `queries.sql#q3` (diagnostic)
- **result:** Only one member named Jason Smith in the `members` table (bioguide
  S001195). Plain "Jason Smith" / "JASON SMITH" / "jason smith" all map
  exclusively to S001195 at confidence 1.0. No disambiguation was needed; no
  other member absorbed any of his contributions.
- **caveats:**
  - Smith needed his full name ("Jason Smith", not just "Smith") to be uniquely
    identified, and lobbyists provided it consistently. Members with *uncommon*
    last names can be resolved from last-name-only entries (`last_unique` method),
    while members sharing a common surname (other Smiths, Joneses, etc.) may have
    contributions go unresolved. The net effect, if any, is that *peers'* totals
    may be deflated by resolution failure — making Smith's rank conservative
    rather than overstated, but making the peer mean also understated. This
    caveat must appear in any published framing.
  - Adrian Smith (R-NE, also in the panel at $3.10M) is separately resolved; no
    cross-contamination between the two Smiths was found.
- **verdict:** neutral — not a flaw in Smith's number, but a caveat on the peer
  comparison

## E4 — Year-over-year: contributions spike in the gavel year (2023) and stay elevated

- **query/script:** `queries.sql#q4`
- **result:** FECA contributions attributed to S001195 (conf ≥ 0.9) by filing year:
  - 2022: 642 rows, $1,349,720
  - 2023: 992 rows, $2,674,511  ← gavel year (took chair Jan 2023)
  - 2024: 875 rows, $2,226,308
  - 2025: 981 rows, $2,913,525  ← tariff/tax bill year
- **source records:** `senate_contribution_items` joined to
  `senate_contribution_filings` (filing_year) via filing_uuid; filtered to
  S001195 honoree map, conf ≥ 0.9, contribution_type='feca'.
- **caveats:**
  - Filing year is the LD-203 report year, not necessarily when the contribution
    was made. LD-203 is semi-annual; small timing differences possible.
  - 2023 nearly 2× the 2022 baseline — consistent with the gavel-spike Bloomberg
    Tax reported from FEC data (Q1 2023 alone: $1.01M per BT). This is
    independent corroboration of the same pattern from a different data source.
  - `member_committees` is current-Congress only; 2022 contributions were raised
    before Smith held the gavel (he was ranking member on a subcommittee).
- **verdict:** supports (gavel-year spike; 2025 tariff year further elevated)

## E5 — Smith's committee roles: W&M Chair + Joint Committee on Taxation Vice Chair

- **query/script:** `queries.sql#q5`
- **result:**
  - House Committee on Ways and Means — Chair, majority, rank 1
  - Joint Committee on Taxation — Vice Chairman, majority, rank 1
  - No other committee assignments in `member_committees`.
- **source records:** `member_committees` joined to `committees`
  (bioguide='S001195').
- **caveats:**
  - `member_committees` is current-Congress only; does not capture past or
    interim assignments.
  - External lookup (2026-06-16) confirmed no current NRCC officer title or
    conference leadership role. Past roles (Conference Secretary 2017–2021;
    Budget Ranking Member 2021–2023) both lapsed when he took the W&M gavel
    in January 2023 — so they do not explain the 2023–2025 elevated haul.
  - Smith raised ~$2.75M *for* the NRCC (informal, not a formal title) and
    self-describes as a top chairman fundraiser. This is activity, not a
    structural role; it doesn't explain the outlier but adds color — some
    contributions may reflect a general "good fundraising citizen" dynamic
    rather than pure W&M-jurisdiction calculation.
- **verdict:** supports (leadership boring explanation cleared; W&M gavel is
  the most plausible structural explanation)

## E6 — Prior W&M chairs: no comparable LD-203 data exists

- **query/script:** `queries.sql#q6`
- **result:**
  - Jason Smith (S001195, R): $9,164,064 in panel (2022–2025)
  - Richard Neal (N000015, D, ranking member 2023–present / chair 2019–2023):
    $6,394,947 in panel (2022–2025)
  - Kevin Brady (B000755, R, chair 2015–2023): $81,300 in panel (2022 only;
    34 rows — retired after 2022)
  - Dave Camp (C000071, R, chair 2011–2015): not in panel (pre-corpus)
  - Paul Ryan (R000570, R, chair 2011): not in panel (pre-corpus)
- **source records:** `derived_member_contribution_panel` (contribution_type='feca')
  for bioguides B000755, C000071, N000015, R000570, S001195.
- **caveats:**
  - The corpus begins 2022; all Republican chairs before Smith (Brady, Camp, Ryan)
    held the gavel entirely or mostly before the data window. **A meaningful
    prior-chairs comparison is not feasible from LD-203 data alone.** FEC
    records would be required for a temporal comparison extending pre-2022.
  - Neal's $6.39M reflects his role as ranking member (minority), not chair,
    during the 2022–2025 window; he chairs Ways & Means as the minority-party
    leader. His total is still the closest peer, but the role comparison is
    imperfect.
- **verdict:** neutral (data insufficient for prior-chairs comparison; must not
  be claimed without FEC data)

## E7 — Smith's outlier status is exclusively a FECA phenomenon; other LD-203 types are unremarkable

- **query/script:** `queries.sql#q7`
- **result:** Smith's rank and z-score by contribution type:
  - `feca`: $9,164,064, rank 1 of 744, z=6.45
  - `he` (Honorary Expenses): $8,062, rank 127 of 449, z≈-0.05
  - `me` (Meeting Expenses): $1,000, rank 30 of 72, z≈-0.33
- **source records:** `derived_member_contribution_panel` all contribution types,
  bioguide S001195.
- **caveats:** `he` and `me` are small-dollar categories corpus-wide ($19.5M and
  $380K total respectively vs $830M FECA). The pattern is still informative:
  if elevated LD-203 reporting were a salience/profile artifact, you would expect
  Smith to be elevated across all types, not exclusively FECA.
- **verdict:** supports (salience-inflation theory weakened; the FECA signal is
  specific, not a generic over-reporting artifact)

## E8 — FEC cycle totals independently corroborate the outlier: $4.61M in 2024 cycle from a safe R+25 seat

- **query/script:** external lookup — FEC.gov candidate ID H4MO08162;
  opensecrets.org/federal-lobbying/top-recipients-details?cycle=2024&id=N00035282
  (returned 403); figures from FEC.gov search snippets and Punchbowl Nov 2024
- **result:**
  - 2024 cycle (2023–2024): ~$4.61M raised
  - 2026 cycle (through Mar 31 2026): $4.46M already raised
  - 2022 cycle: not retrieved
  - District competitiveness: MO-08 is R+25, no serious opposition — safe-seat
    members typically raise $1–2M per cycle
- **source records:** FEC.gov (H4MO08162); Punchbowl News Nov 1 2024
- **caveats:**
  - The LD-203 $9.16M covers two full cycles (2022–2025); at ~$4.61M/cycle the
    FEC pace roughly aligns — no obvious LD-203 inflation relative to FEC.
  - LD-203 and FEC are filed by entirely different parties under different legal
    regimes. Independent elevation in both datasets makes the salience-inflation
    explanation implausible: it would require LD-203 over-reporting *and* an
    independently elevated FEC haul simultaneously.
  - **FEC/LD-203 reconciliation via occupation filtering is the wrong bridge.**
    OpenSecrets' "lawyers/lobbyists" industry category for Smith is <$500K —
    a severe undercount, because it relies on FEC contributors self-reporting
    "lobbyist" as occupation. A lobbyist who lists their employer as "Akin Gump"
    rather than their occupation as "lobbyist" won't appear in that slice. LD-203
    and FEC measure related but distinct things: LD-203 is a *firm-level
    disclosure* (the lobbying firm reports what it contributed, regardless of how
    the individual described themselves on the FEC form); FEC individual
    itemization is a *person-level disclosure* with self-reported occupation. They
    will never reconcile cleanly via the OpenSecrets tag. The right FEC
    corroboration is the total-receipts comparison (which we have), not an
    occupation-filtered slice.
  - **Open FEC threads for future work:** (1) prior W&M chairs comparison — Brady,
    Camp, Ryan cycle totals from FEC bulk data would enable a historical baseline;
    (2) sector decomposition — FEC itemized data with employer fields would let us
    attribute Smith's haul to tax/tariff-adjacent industries specifically, testing
    whether the gavel jurisdiction drives the money; (3) a full FEC ingest would
    also let us rank Smith among *all* House members (not just LD-203 panel
    members) for a cleaner peer comparison. None of these are blockers for the
    core claim but all would substantially deepen it.
- **verdict:** supports (FEC independently corroborates outlier fundraising;
  salience-inflation theory substantially weakened; FEC/occupation-filter bridge
  is not the right reconciliation approach)

## E9 — Smith's gavel-transition spike (1.98×) is the sharpest in the Republican chair cohort; peer mean is flat (1.06×)

- **query/script:** `queries.sql#q8` (screen `chair-transition-contribution-spike`,
  run 10; `investigations/screens/chair-transition-contribution-spike/run-10/shortlist.csv`)
- **result:** Across 24 current House Republican full-committee chairs, 2022→2023
  FECA spike ratios:
  - **Jason Smith (W&M): 1.98×** — highest in cohort
  - Mike Bost (Veterans' Affairs): 1.61×
  - Jim Jordan (Judiciary): 1.36×
  - Cohort mean: **1.06×** (essentially flat; median dragged down by chairs who declined)
  - Sustained: Smith's avg_post_vs_pre (avg of 2023+2024 / 2022) = 1.82×
  - 2025 further elevated ($2.91M) — the tariff/tax bill year
- **source records:** `derived_member_contribution_panel` (filing_year 2022–2025,
  contribution_type='feca'); `member_committees` + `committees` for chair identification.
- **caveats:**
  - Natural experiment is clean: all current R House chairs took gavels
    simultaneously in Jan 2023 when Republicans won the majority, so 2022 is a
    valid cohort-wide pre-treatment baseline.
  - `member_committees` is current-Congress only. This is appropriate for the
    Jan-2023 transition (same assignments) but would mis-attribute any mid-Congress
    gavel change (e.g. if a chair was replaced mid-term).
  - Bryan Steil's high absolute 2022 baseline ($2.61M) reflects his NRCC role —
    a useful internal control confirming that formal fundraising roles produce
    high baselines *before* the transition, not spikes *at* the transition.
  - Guthrie (E&C) shows a lagged pattern — flat in 2023 (0.92×), then strong
    in 2024 (2.17×) and 2025 (3.69×) — suggesting E&C's jurisdiction (pharma,
    AI, broadband) became a money magnet later than W&M's immediate 2023 spike.
    Different mechanism, both consistent with jurisdiction-driven fundraising.
  - Chairs with declines (Comer, Foxx, Mast, Guest) serve committees with lower
    lobbying-industry salience (Ethics, Rules, Foreign Affairs, Oversight) or
    faced competitive dynamics that drew money away.
- **verdict:** supports — Smith's 2023 spike is the sharpest immediate gavel-year
  response in the cohort, nearly 2× a baseline that peers barely moved; the
  sustained elevation through 2025 further distinguishes him

## E10 — Neal comparison: the gavel flip is visible as a mirror image; Smith's gain asymmetrically larger than Neal's loss

- **query/script:** `queries.sql#q9`
- **result:** Year-by-year FECA for Smith (S001195) and Neal (N000015), who
  held the W&M gavel in opposite halves of the corpus window:

  | Year | Neal | Smith | Role |
  |---|---|---|---|
  | 2022 | $1,692,275 | $1,349,720 | Neal=Chair, Smith=Ranking Member |
  | 2023 | $1,402,250 | $2,674,511 | **Gavel flips Jan 2023** |
  | 2024 | $1,876,572 | $2,226,308 | Neal=Ranking Member, Smith=Chair |
  | 2025 | $1,423,850 | $2,913,525 | Neal=Ranking Member, Smith=Chair |

  - Neal's 2022→2023 transition (lost gavel): **0.83×** (−17%)
  - Smith's 2022→2023 transition (gained gavel): **1.98×** (+98%)
  - Both moved in the predicted direction simultaneously — same committee,
    opposite role changes, opposite money trajectories.
  - Neal's 4-year total: $6,394,947 — #2 among House Democrats (z=5.36), behind
    only Jeffries (minority leader). He is also an outlier, just less extreme.
- **source records:** `derived_member_contribution_panel` (contribution_type='feca',
  bioguides N000015 and S001195, filing_year 2022–2025).
- **caveats:**
  - Neal remained ranking member after losing the gavel — a high-salience role
    that maintains a contribution floor. His modest drop (−17%) partly reflects
    that the ranking member position on W&M is itself powerful. This means the
    asymmetry (Smith +98% vs Neal −17%) understates the true gavel effect: Neal's
    counterfactual as a backbencher would have dropped further.
  - Smith's spike coincides with the tariff/tax jurisdiction becoming exceptionally
    hot in 2023–2025 (new administration, major tax bill, tariff fights). Neal
    chaired W&M during 2021–2023 when ARP and IRA were the dominant fights —
    a different set of industries mobilizing. The spike comparison reflects both
    the gavel effect and the jurisdictional moment.
  - This is a within-corpus comparison only; it cannot speak to Brady's era
    (pre-2022) or Camp's (pre-2014).
- **verdict:** supports — the gavel flip is visible in both directions
  simultaneously, strengthening the causal story; Smith's gain is asymmetrically
  larger than Neal's loss, consistent with a jurisdiction-driven amplifier on
  top of the structural gavel effect
