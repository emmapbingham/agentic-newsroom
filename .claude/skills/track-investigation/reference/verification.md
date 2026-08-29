# Verifying a finding (builder → skeptic → judge)

The dominant failure mode of agentic investigation is the *plausible-but-wrong*
claim: a clean-looking query that means something other than the headline. This
pattern is the guard. **Scale to stakes** — skip it for weak/early leads; it's
mandatory before anything reaches the findings report.

## The roles

1. **Builder** — assembles the strongest version of the case: the claim, the
   evidence (each item sourced to a record + query), and the timeline. Writes /
   updates `case.md` + `evidence.md`. Argues *for*.
2. **Skeptic** (1+ independent) — tries to *kill* it. Default stance: "this is
   nothing." Runs its own counter-queries. Must produce either a concrete
   refutation / innocent explanation or an explicit "couldn't refute, here's
   what I tried." Use diverse lenses if more than one skeptic (data-quality
   lens, statistical lens, alternative-explanation lens).
3. **Judge** — weighs builder vs. skeptic(s), renders a verdict
   (`supported / refuted / needs-more / parked`) + a confidence, and writes it
   as the one-line **Verdict** in `case.md`. May bounce it back for more
   evidence.

Independence matters: the skeptic should not just read the builder's case and
agree — it should re-derive from the data.

## The skeptic's checklist (corpus-specific — run every item)

- **Junk free-text:** did an aggregate include `'N/A'`, `'See prior filing'`,
  `'None'`, `'Legislative Consultant'` in `covered_position` / `honoree_name`?
- **Honoree match quality:** does the claim rest on `honoree_member_map` rows
  with `confidence < 0.9` (esp. `last_unique` / 0.6)? Re-verify the identity
  by hand.
- **House+Senate double-counting:** is the same engagement counted in both
  `senate_*` and `house_*` (a registrant files in both chambers)? Use one side
  or dedupe via the bridge.
- **Base rate:** "chair X took industry money" — *do all chairs?* Compare
  against the peer distribution before calling it notable.
- **Denominator/scope honesty:** does the claim's "of N" population match what
  was actually screened? A derived table or keyword map that silently excludes
  most of the universe (e.g. a hand-curated keyword list covering 22 of 79
  categories) makes "quietest in the corpus" false even if the ranking within
  the mapped subset is correct. Check what built the comparison set, not just
  whether the ranking math is right.
- **Correlation ≠ causation / coordination:** timing alignment (press vs.
  lobbying) is suggestive, not proof. Name the confounds (news cycle, election
  calendar, must-pass bills).
- **Multiple comparisons:** a scan over 500 members × many issues will throw
  "significant" hits by chance. Correct for it; report how many comparisons.
- **Sparse / self-reported money:** only ~65% of Senate filings carry parseable
  income; LDA data is self-reported. Don't treat absence as zero.
- **FTS false matches:** does the keyword match the intended sense? Eyeball the
  hits; a `MATCH 'PBM'` can catch unrelated initialisms.
- **Time window:** are the contribution, lobbying, and press windows actually
  aligned (quarters / periods differ across sources)?
- **Identity:** small-N name claims (e.g. conviction disclosures) — confirm
  it's the same person, not a namesake.

A claim is report-ready only when the skeptic's concrete objections are each
answered with evidence, or the claim is narrowed to what survives.

## Running it as a Workflow (user-triggered)

For a report-bound finding, this maps to a `verify-finding` Workflow:

```
builder (1 agent, schema: claim + sourced evidence)
  -> parallel skeptics (N agents, distinct lenses, each tries to refute)
  -> judge (1 agent: verdict + confidence, writes case.md)
```

Workflows spawn many agents and are billed, so the **user launches** them —
this skill can't auto-launch one. For lighter checks, run the three roles
inline in one session.

## Output

The verdict + confidence go in `case.md`'s **Verdict** line; the skeptic's
surviving objections and the answers go in `evidence.md` as their own entries.
"We tried to refute it these N ways and couldn't" is itself reportable strength.
