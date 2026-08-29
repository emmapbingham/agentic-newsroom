---
name: fish-for-leads
description: "Operates the everyday, cheap go-fish loop over a data-journalism newsroom's sourced SQLite corpus — runs one live screen, gates candidates before they cost editor attention (template collapse, actor test, novelty-lite), surfaces survivors as leads, builds derived tables on demand, and promotes leads into cases. Every state change lands in the actions journal with an actor and review state; agents act provisionally and the editor reviews a ranked queue afterward (acknowledge or overturn, signed). On invocation reads full posture (screens with yield, leads, dispositions, unreviewed actions). Hands off to track-investigation on promotion, and to sweep-for-screens when the live slate is exhausted. Use when running the newsroom, going fishing, surfacing or triaging leads, reviewing autonomous actions, promoting a lead, or building a derived table. Trigger phrases: run the newsroom, newsroom status, go fish, surface leads, triage leads, review actions, promote a lead, check posture."
license: MIT
---

# Fish for leads (go-fish)

The everyday, cheap operating loop in the newsroom pipeline. One human editor
directing an agent fleet over a corpus:

```
SWEEP (rare, expensive) ──► designs SCREENS + proposes DERIVED TABLES
  (sweep-for-screens skill)
        │
        ▼
GO FISH (everyday, cheap) ──► run ONE live screen ──► surface 3–5 candidate LEADS
  (this skill)                (logged to leads run-record)
        │
        ▼
PROMOTE one ──► CASE (durable) ──► track-investigation takes over from here
  (this skill hands off)
```

Two principles govern everything:

1. **The scarce resource is editorial attention.** Every layer exists to ensure
   what reaches the editor is worth their time and carries its provenance.
2. **"Interesting" means deviation from an expectation.** Every lead-generation
   method is a choice of baseline plus a ranking of residuals. Stay deterministic
   until the last possible moment: SQL ranks the whole population for free;
   spend model tokens only on the residual tail.

---

## On invocation — read posture first

Read `investigations/newsroom.db` and report:

```sql
SELECT status, priority, count(*) FROM screens GROUP BY status, priority ORDER BY status, priority;
SELECT count(*) FROM screen_runs;
SELECT count(*) FROM leads WHERE disposition IS NULL;      -- awaiting editor triage
SELECT disposition, count(*) FROM leads GROUP BY disposition;
SELECT name FROM derived_tables;
SELECT run_at, n_screens_added FROM sweeps ORDER BY run_at DESC LIMIT 1;

-- per-screen yield: which rods actually catch fish the editor keeps
SELECT s.name, s.grain, count(DISTINCT r.id) AS runs, count(l.id) AS leads,
       sum(l.disposition='promoted') AS promoted
FROM screens s
LEFT JOIN screen_runs r ON r.screen_id = s.id
LEFT JOIN leads l ON l.screen_run_id = r.id
GROUP BY s.id HAVING runs > 0 ORDER BY promoted DESC, leads DESC;
```

Report as a short table: live screens (by priority), backlog screens grouped by
priority (high/medium/low), runs so far, leads awaiting triage, disposition
counts, built derived tables, last sweep date. Then recommend one next action —
if no live screens remain unrun and the backlog is empty, recommend a sweep
(`sweep-for-screens` skill) instead of forcing a run.

**Use the yield table.** A screen with ≥3 runs whose leads have drawn zero
editor interest (no promotions, dispositions all passes) is a candidate to
deprioritize — flag it rather than silently re-fishing dead water. Also read
the last ~15 disposition reasons (`SELECT slug, disposition, disposition_reason
FROM leads WHERE disposition IS NOT NULL ORDER BY disposition_at DESC LIMIT 15`)
before surfacing anything: they are the editor's taste, recorded — calibrate
against what was recently passed on and why.

**Report the review queue.** Posture includes unreviewed autonomous actions:

```sql
SELECT object_type, object_ref, max(priority) AS pri, count(*) AS n,
       min(date(at)) AS oldest
FROM actions WHERE review_state='unreviewed'
GROUP BY object_type, object_ref ORDER BY pri DESC, oldest;
```

If high-priority (≥4) actions await review, recommend a review pass before
new fishing. Full actor/review doctrine: `reference/actions.md`.

If `newsroom.db` does not exist, offer **setup**: initialize from
`assets/schema_newsroom.sql`, create `investigations/sweeps/`, initialize
Datasette (`scripts/serve_newsroom.sh`).

With an argument, run that phase directly: `status`, `go-fish [screen-name]`,
`promote <slug>`, `build <derived-table>`.

---

## The operating phases

### 1. Go fish (everyday)

The routine move. The editor asks for leads; leads are delivered. If building a
derived table is needed first, do it transparently and note it briefly — the
editor does not need to choose a screen or approve a build step.

**Screen selection:**
1. Prefer `live` screens (status='live'). Among live screens, pick the highest
   priority one not recently run. If the editor names a specific screen, use that.
2. If no live screens are available (or all have run recently), pick the highest
   priority `backlog` screen, build its derived table (see §3), flip it to
   `live`, then run it. Include a brief note: "Built `derived_x` to unlock this
   screen." If the backlog is also empty, that's the signal to run a sweep
   (`sweep-for-screens` skill) rather than force a run here.

**Run the screen:**
1. **Before running:** confirm the screen has a `sql_path` set and a file at
   that path. If not, write the SQL to
   `investigations/screens/<name>/screen.sql` and update `sql_path` in
   `screens`. Every screen must have its SQL on disk so it can be re-run without
   archaeology into case files or session history.
2. Run it with the canonical runner — it executes the SQL read-only, writes the
   full shortlist to `runs/run-<id>/shortlist.csv`, saves the top-N
   distribution figure, and logs the `screen_runs` row in one step:

   ```bash
   python scripts/run_screen.py <screen-name>          # --top N to size the figure
   ```

   A copy of the runner ships with this skill (`scripts/run_screen.py`;
   needs pandas + matplotlib). It reads the corpus/ledger/screens paths from
   the environment bindings below — copy it into the project's `scripts/`
   (adjusting its path constants) when binding a new corpus.
   Only fall back to manual execution (read-only; `mode=ro` always) if the
   runner is unavailable — and then log the `screen_runs` row (`screen_id`,
   `run_at`, params, `n_candidates`, `shortlist_path`, `figures_path`) and
   follow the same `run-<id>/` artifact layout yourself.
3. Read the top 3–5 rows and **run the surfacing gates** (full procedure with
   worked examples: `reference/lead-gates.md`). In cost order:
   1. **Template collapse** — candidates sharing one story template become ONE
      pattern-lead with an exemplar table, not N rows. Five reads to render one
      editorial judgment is four wasted.
   2. **Actor test** — route by the screen's `grain`. Actor-grain: surface as a
      lead if a named actor did something (filed, paid, surged, went quiet,
      switched). Structure-grain: don't surface the category observation raw —
      spend one cheap drill pass ("top 3 actors inside this anomaly; does any
      have a motive?") and surface the actor-grain result.
   3. **Boring explanation first** — write `boring_explanation` *before*
      `story`. If it wins, log the row with `disposition='suppressed-boring'`
      and don't render it.
   4. **Novelty-lite** — one bounded web search on the candidate's core claim.
      A decisive hit (dated article, same finding) → log the row with
      `disposition='suppressed-covered'`, the citation in
      `disposition_reason`, and don't render it. A miss is neutral: surface,
      and never call it "novel" (that's the case-level scan's job — hits are
      strong evidence, misses are weak).
4. For each survivor, write a `leads` row:
   - `slug` — kebab-case, unique
   - `screen_run_id` — the run just logged
   - `story` — **2–3 plain-language sentences; the front door, not a stats dump**.
     A reader who doesn't know this congressperson, firm, or issue should
     understand why this is potentially interesting in 20 seconds. Stats are
     backing, not the lede.
   - `claim` — one falsifiable sentence
   - `probe_sql` — the exact query that produced this row
   - `scout_number` — the key figure, flagged "unverified — re-derive before citing"
   - `boring_explanation` — the strongest innocent account of the same rows
     (already written, per the gate). If the screen was reporting-nominated,
     this must also answer "am I just confirming the article?" (see
     `sweep-for-screens/reference/beat-nomination.md`).
5. Render each lead's `story` for the editor. Back the story with claim +
   scout_number + boring_explanation below. Don't render the full row; don't
   re-summarize after rendering. Mention gate suppressions in one line each
   ("suppressed 2: <slug> (covered — <outlet, date>), <slug> (boring)").

**Leads are ephemeral but logged.** A surfaced candidate is just a row in the
run-record — not a worklist. Gate-suppressed candidates get rows too (with
`suppressed-*` dispositions): the multiple-comparisons ledger must record what
was filtered, not just what survived. The `screen_run_id` answers "out of how
many runs?"

**Record every state change in the actions journal** (`actions` table; full
doctrine `reference/actions.md`): surfaces, suppressions, builds,
registrations, promotions — one row each with actor (`editor` / `agent-live` /
`agent-auto`), one-line basis, and priority tier. Agents act provisionally
(including promotion, in unattended runs) and the editor reviews afterward;
executions (screen runs) stay in `screen_runs`, decisions go here.

### 2. Review — the editor samples, acknowledges, overturns

The editor's entry point after any autonomous work ("review actions", "what
needs my attention"). Render `unreviewed` actions **grouped by object**,
ranked by priority then age — an object's chain reads as one item ("promoted
X → opened case → verified supported: acknowledge chain?"). For each, the
editor can:

- **Acknowledge** — set `review_state='acknowledged'`, `reviewed_at`,
  `reviewed_by` (a name from your newsroom's reviewer roster — always record
  who signed off), `review_note` ('chain ack' covers the object's whole chain).
- **Overturn** — append a new `editor` action (`action='overturn'`, basis =
  what replaces it, born acknowledged), set the target row to `overturned`,
  then perform the compensating state change.
- **Ignore** — stays provisional; posture keeps showing count + age.

Lead verdicts are the same mechanism plus the lead-local materialization:

```sql
UPDATE leads SET disposition = '<pass-boring|pass-covered|duplicate-of|artifact>',
                 disposition_reason = '<one line: the editor''s why>',
                 disposition_at = datetime('now')
WHERE slug = '<slug>';
-- and the actions row: actor='editor', action='pass', born acknowledged.
```

Verdicts: `pass-boring` (innocent explanation wins / no story), `pass-covered`
(already reported), `duplicate-of` (name the earlier lead in the reason),
`artifact` (data-quality mirage). A pass with no recorded reason is attention
spent and evaporated — the reasons are the taste data the next go-fish reads.

**Promote** is the remaining verdict. When the editor picks a lead to pursue
(or an unattended run promotes provisionally — record `agent-auto`, priority
4–5, and see the budget cap in `reference/actions.md`):

```sql
UPDATE leads SET promoted_at = datetime('now'), case_slug = '<slug>',
                 disposition = 'promoted',
                 disposition_reason = 'promoted to case <slug>',
                 disposition_at = datetime('now')
WHERE slug = '<slug>';
```

Then hand off to `track-investigation`, which opens the case. The case is the
verdict's home from that point on. Apart from its disposition fields, the
`leads` row stays immutable — it records what was surfaced and when, not the
case outcome. `track-investigation` also owns the post-verification novelty
scan; the surfacing-time novelty-lite gate deliberately does not replace it
(see `track-investigation/reference/prior-art.md`).

### 3. Build a derived table

When a backlog screen's `needs_table` names a missing derived table — whether
proposed by a `sweep-for-screens` sweep or discovered on-demand — build it:

1. Check `derived_tables` first — it may already exist.
2. If not: write a deterministic `scripts/build_derived_<name>.py` that reads
   `gain.db` (never writes to it) and creates a `derived_<name>` table. Log
   it in `ingest_log` (tier='derived'). Document it in `docs/derived_db.md`.
3. Add a row to `derived_tables` (name, answers, builder_script).
4. The screen's status flips from `backlog` to `live` — update it.

**Check the catalog before computing from raw.** An agent that rediscovers and
recomputes a shared table in a slightly different way is a provenance hazard.
`derived_tables` is the discoverability index.

**Dedup before aggregating.** Reduce to one canonical record per entity-period
before summing. Duplicate quarterly filings or amendments inflate income totals:
an early scout in this newsroom reported a "$118M disclosure gap" that shrank
to ~$35M — mostly clerical duplicates — once records were deduplicated.

---

## Provenance (non-negotiable)

- A lead's evidence may cite **only source records and queries** — never an
  agent summary or another lead.
- Anything that bounds coverage (top-N, thresholds) is logged, not silent.
- **Scout numbers are unverified until re-derived.** Tag them; never promote
  into a durable document without re-derivation. One over-corrected figure
  reached six files before the verifier caught it.
- **An unverified number must not enter a durable doc** (beat book, catalog,
  case file, report) until it has passed verification.
- **Maintain the beat book** (whatever skill or doc holds your corpus's
  schema, bridges, and traps — see the bindings below): update whenever a
  sweep or case teaches a new trap. Tuition paid once stays paid.

---

## The seam with track-investigation

`fish-for-leads` owns everything up to and including a promoted lead: running
screens, logging runs, surfacing leads, building on-demand derived tables, and
promotion.

When a lead is promoted, **`track-investigation` takes over** — it opens the
case, runs drilldown, builds evidence, runs verification, and conducts the
post-verification novelty scan. The `leads` row points at the case; the case is
the verdict's home.

Neither skill redefines a term the other owns.

---

## Schema (newsroom.db)

| Table | What it is |
|---|---|
| `screens` | Durable re-runnable SQL ranking queries. `live` = can run now; `backlog` = waiting for a derived table. `priority` (high/medium/low) governs selection order within each status; `grain` (actor/structure) governs how candidates are surfaced (see the gates). `sweep-for-screens` creates rows; this skill runs and flips them. |
| `screen_runs` | Multiple-comparisons ledger. Every execution logged; answers "this lead surfaced out of how many runs?" |
| `leads` | Append-only run-record of surfaced candidates. Not a worklist. Carries `story`, `probe_sql`, `scout_number`, `boring_explanation`, plus `disposition`/`disposition_reason` — the recorded editorial fate (or gate suppression). Rows are never deleted; NULL disposition = awaiting triage. |
| `derived_tables` | Discoverability index of built shared derived tables in `gain.db`. Check here before recomputing from raw. Built by this skill; proposed by `sweep-for-screens`. |
| `sweeps` | One row per fleet sweep: run metadata, cost, screens added. Owned by `sweep-for-screens`; read here for posture. |
| `actions` | Append-only journal of every state change: actor (`editor`/`agent-live`/`agent-auto`), basis, priority, review state, signed `reviewed_by`. The editor's review queue. Agents act provisionally; the hard gate is that nothing report-bound ships without a transitively acknowledged chain. Doctrine: `reference/actions.md`. |

Full schema: `assets/schema_newsroom.sql`. Artifact lifecycles (durable vs
ephemeral-but-logged, per table): `reference/artifacts.md`. Surfacing-gate
procedure with worked examples: `reference/lead-gates.md`. Actor/review
doctrine incl. unattended-run policy: `reference/actions.md`.

---

## Adapting to your newsroom

This skill was built in a federal-lobbying newsroom; the method is
corpus-agnostic. To adopt it, bind five things:

- **Corpus DB** — the sourced read-only SQLite corpus (here `db/gain.db`).
- **Ledger DB** — where screens/runs/leads/actions live (here
  `investigations/newsroom.db`; init from `assets/schema_newsroom.sql`).
- **Screens directory** — on-disk home for each screen's SQL and run artifacts
  (here `investigations/screens/<name>/`).
- **Reviewer roster** — the humans allowed to sign `reviewed_by` (here
  'emma'/'ian').
- **Beat book** — the skill or doc holding your corpus's schema, bridges, and
  data traps (here `docs/beat_book.md` in the project repo; not part of this
  suite).

Sibling skills in this suite: `sweep-for-screens` (designs screens),
`track-investigation` (owns promoted cases).

License: MIT.
