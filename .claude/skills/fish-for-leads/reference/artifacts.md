# Newsroom artifacts: durable vs ephemeral-but-logged

Everything in `newsroom.db` is either **durable infrastructure** (built once,
re-used many times) or **ephemeral-but-logged** (produced per-run, kept for
the record but not a worklist). The distinction drives how each artifact is
created, read, and handed off.

## Durable infrastructure

### Screens

A screen is a registered, deterministic SQL ranking query with a named baseline.
It is the system's reusable fishing rod — run it whenever you want a ranked
shortlist from that angle.

- **Lifecycle:** `live` (can run now) / `backlog` (waiting for its `needs_table`
  to be built).
- Every screen states its **baseline** in one line: what "expected" means, such
  that the screen ranks deviation from it. No baseline, not a screen.
- SQL lives on disk at `investigations/screens/<name>/screen.sql`.
- A screen becomes `live` when its `derived_table` dependency exists in
  `derived_tables`.

### Derived tables

Shared `derived_*` tables in `gain.db` — panels, baselines, enrichments. Each
makes a class of questions cheap to answer.

- **Lifecycle:** proposed (in a sweep report) → built (in `gain.db` + cataloged
  in `derived_tables`) → screens using it flip from `backlog` to `live`.
- **Gate: check the catalog before computing from raw.** `derived_tables` is the
  discoverability index. An agent that recomputes a shared table in a slightly
  different way creates a provenance hazard.
- Build scripts are deterministic (`scripts/build_derived_*.py`), logged in
  `ingest_log` (tier='derived'), documented in `docs/derived_db.md`.
- **Dedup before aggregating.** One canonical record per entity-period before
  summing; duplicates/amendments/versions inflate totals.
- If an LLM produced the data (classification, entity resolution): store per-row
  `method` + `confidence`, log model + prompt version, treat as a reference tier
  filterable by confidence.

### Sweeps

One row per fleet operation in `sweeps`. A sweep's job is to **design new
screens** and **propose derived tables** — not to generate leads directly. Browse
sweep reports in `investigations/sweeps/`.

## Ephemeral-but-logged

### Screen runs

Every execution of a screen is logged in `screen_runs` (screen_id, run_at,
params, n_candidates, shortlist_path, figures_path). This is the
**multiple-comparisons ledger**: the skeptic's first question — "this lead
surfaced out of how many screens?" — is only answerable if runs are counted.
Selection effects you can't count are effects you can't correct.

Runners save a distribution figure next to each shortlist
(`investigations/screens/<name>/run-<id>/`).

### Leads

One row per candidate a screen run surfaced — including candidates the
surfacing gates suppressed (`reference/lead-gates.md`). **Not a worklist** — a
row is "surfaced (or suppressed) on date X by screen run Y," carrying the
`story`, `probe_sql`, `scout_number`, and `boring_explanation`.

- **Lifecycle:** `surfaced_at` is set on creation. `disposition` +
  `disposition_reason` + `disposition_at` record the fate: gate suppressions
  (`suppressed-covered`, `suppressed-boring`) are written at surfacing time;
  editor verdicts (`pass-boring`, `pass-covered`, `duplicate-of`, `artifact`,
  `promoted`) at triage time. NULL = awaiting triage. Promotion also sets
  `promoted_at` + `case_slug`. Rows are never deleted; apart from disposition
  fields they are immutable — the case owns the verdict after promotion.
- **The disposition ledger is the editor's taste, recorded.** The go-fish loop
  reads recent dispositions before surfacing; per-screen yield
  (promotions per lead surfaced) comes from joining dispositions back to
  screens.
- Browse past leads in Datasette — the `story` column is the front door.
- `probe_sql` is the anti-duplication key: it answers "is this the same candidate
  as one I passed over before?"
- `scout_number` must be flagged unverified; re-derive before citing in any
  durable document.
