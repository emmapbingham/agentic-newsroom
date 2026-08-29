---
name: sweep-for-screens
description: "Runs the rare, expensive fleet sweep that expands a data-journalism newsroom's fishing capability over a sourced SQLite corpus — designs new deterministic SQL screens and proposes the derived tables they need, without generating leads directly. Reads and writes screens/derived_tables/sweeps in newsroom.db; the fish-for-leads skill runs the screens and surfaces leads. Encodes the contrast taxonomy (six ways a lead can deviate from a baseline, crossed with the corpus's grains) that partitions idea space across a scout fleet, fleet run-economics (pilot-first, probe budgets, tier models by fleet size, hard token ceilings), and the beat-nomination discipline for using outside reporting to aim the corpus without letting it into evidence. Use when sweeping for new screen ideas, designing a screen, expanding fishing capability, proposing a derived table, or running a fleet sweep. Trigger phrases: sweep for leads, design new screens, expand the newsroom, run a sweep, propose a derived table."
license: MIT
---

# Generate query ideas (sweep)

The rare, expensive fleet operation in the newsroom pipeline. One human editor
directing an agent fleet over a corpus:

```
SWEEP (rare, expensive) ──► designs SCREENS + proposes DERIVED TABLES
  (this skill)               (capability expansion, not lead generation)
        │
        ▼
GO FISH (everyday, cheap) ──► run ONE live screen ──► surface 3–5 candidate LEADS
  (fish-for-leads skill)      (logged to leads run-record)
        │
        ▼
PROMOTE one ──► CASE (durable) ──► track-investigation takes over from here
```

Two principles govern everything:

1. **The scarce resource is editorial attention.** Every layer exists to ensure
   what reaches the editor is worth their time and carries its provenance.
2. **"Interesting" means deviation from an expectation.** Every lead-generation
   method is a choice of baseline plus a ranking of residuals. Stay deterministic
   until the last possible moment: SQL ranks the whole population for free;
   spend model tokens only on the residual tail.

---

## On invocation — read sweep posture first

Read `investigations/newsroom.db` and report:

```sql
SELECT status, priority, count(*) FROM screens GROUP BY status, priority ORDER BY status, priority;
SELECT run_at, n_screens_added FROM sweeps ORDER BY run_at DESC LIMIT 1;
SELECT name, answers FROM derived_tables;
```

Report as a short table: live screens (by priority), backlog screens grouped by
priority (high/medium/low) and what derived table each is waiting on, built
derived tables, last sweep date. Then recommend whether a sweep is warranted
(the prior slate of screens is exhausted) or whether `fish-for-leads` should run
instead (live screens remain unrun).

If `newsroom.db` does not exist, hand off to `fish-for-leads` for setup — it
owns `assets/schema_newsroom.sql`.

---

## Sweep (the one operating phase here)

The expensive fleet operation that expands the system's fishing capability. Its
job is to design *new screens* and propose *derived tables they need* — not to
generate leads directly.

Run a sweep to:
- Discover new screen designs the editor hasn't thought of
- Enumerate which derived tables would make those screens computable
- Repopulate thin or mispruned cells from the prior sweep

A good sweep yields weeks of new runnable screens. Don't re-run until the
prior slate of screens is exhausted. Full fleet skeleton and brief essentials:
`reference/workflow-patterns.md`. The contrast taxonomy that partitions the idea
space across scouts: `reference/taxonomy.md`.

After a sweep: register new screens in `screens` — the synthesis agent must
assign each proposed screen a `priority` (high/medium/low, by story value) and
a `grain`, and write both into the row:

- `grain='actor'` — shortlist rows name a registrant/member/client/lobbyist
  who did something. `fish-for-leads` surfaces these directly as leads.
- `grain='structure'` — rows are issue/committee/code-level patterns.
  `fish-for-leads` drills these to named actors before surfacing (a category
  observation is a drill target, not a story; see
  `fish-for-leads/reference/lead-gates.md`).

Declaring grain once at registration means the surfacing route is never
re-litigated per run. Use `status='backlog'` if the derived table isn't built
yet, `status='live'` if it is. Add the `sweeps` row, write a human-readable
sweep report. Mark everything scout-reported / unverified. Record each
registration in the `actions` journal (priority 3; actor per
`fish-for-leads/reference/actions.md`) — registrations are provisional like
every agent action, reviewable in the editor's queue.

**Propose derived tables — don't build them.** A sweep's output on the data
side is a *proposal*: name, the question it makes cheap (`answers`), a
`builder_script` idea, and feasibility — written into the sweep report and into
`screens.needs_table` for any backlog screen it unlocks. `fish-for-leads` owns
the actual build step (on-demand when unlocking a backlog screen, or working
through a sweep's proposal list). This keeps sweep output deterministic and
review-before-build — a fleet should not be writing to `gain.db`.

**Check the catalog before proposing.** `derived_tables` is the discoverability
index; a sweep that reproposes a table that already exists (in a slightly
different shape) creates a provenance hazard downstream.

## Beat nomination (direction in, never evidence)

Screens may be nominated by what's in the news — but reporting only ever aims
the corpus, never substitutes for a record. Full policy, including the
coverage-gap trap and how to log nomination as selection context:
`reference/beat-nomination.md`. Short version: **direction in, novelty out,
news never in the evidence middle.**

---

## Fleet economics

- **Never launch a fleet on an unflown brief.** Pilot one agent, measure tokens
  + tool calls + output quality, then fan out.
- **Probe budgets in every brief.** "At most N queries; prefer COUNT/EXISTS
  probes; marking something unverified is acceptable."
- **Output ceilings.** "Your best 2, plus one-line runners-up" halves synthesis
  input.
- **Tier models by fleet size, not task dignity.** Cheap model × N saves
  linearly; single-agent steps can afford the better model.
- **Hard token ceiling on every workflow.** Verify `args` reach the script
  (log them first) before launching.
- Full rules: `reference/run-economics.md`.

---

## Provenance (non-negotiable)

- A proposed screen states its **baseline** in one line — no baseline, not a
  screen.
- Anything that bounds coverage (top-N, thresholds) is logged, not silent.
- Sweep-reported figures are unverified by construction; never let a scout
  number reach a durable document (beat book, catalog, case file, report)
  without re-derivation downstream.
- **Maintain the beat book** (whatever skill or doc holds your corpus's
  schema, bridges, and traps — see the bindings below): update whenever a
  sweep teaches a new trap. Tuition paid once stays paid.

---

## The seam with fish-for-leads

`sweep-for-screens` owns capability expansion: designing screens and
proposing derived tables. It does not run screens, log runs, surface leads, or
build the tables it proposes.

**`fish-for-leads` takes over** for everything downstream: building the derived
tables a sweep proposed, running screens, surfacing leads, and promoting to
`track-investigation`.

Neither skill redefines a term the other owns.

---

## Schema (newsroom.db) — this skill's tables

| Table | What it is |
|---|---|
| `screens` | Durable re-runnable SQL ranking queries. `live` = can run now; `backlog` = waiting for a derived table. `priority` (high/medium/low) governs selection order within each status; `grain` (actor/structure) governs how `fish-for-leads` surfaces the results. This skill creates rows here; `fish-for-leads` runs them. |
| `derived_tables` | Discoverability index of built shared derived tables in `gain.db`. This skill proposes entries (via sweep reports + `screens.needs_table`); `fish-for-leads` builds and registers them. |
| `sweeps` | One row per fleet sweep: run metadata, cost, screens added. Owned here. |

Full schema (all tables, including `screen_runs`/`leads` which this skill
doesn't touch): `fish-for-leads/assets/schema_newsroom.sql`.

## Adapting to your newsroom

Three bindings are project-specific; everything else (the contrast taxonomy,
fleet economics, beat-nomination firewall) transfers unchanged:

- **Ledger DB** — where screens/sweeps are registered (here
  `investigations/newsroom.db`; schema in
  `fish-for-leads/assets/schema_newsroom.sql`).
- **Corpus DB** — the sourced corpus screens run against (here `db/gain.db`).
- **Beat book** — the skill or doc holding your corpus's schema, bridges, and
  grains (here `docs/beat_book.md` in the project repo, not part of this
  suite; the grains list in `reference/taxonomy.md` is that corpus's example
  binding).

Sibling skills in this suite: `fish-for-leads` (runs the screens),
`track-investigation` (owns promoted cases).

License: MIT.
