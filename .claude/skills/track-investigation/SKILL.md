---
name: track-investigation
description: "Runs and tracks data-driven investigative-journalism cases across sessions over a SQLite corpus. Starts when a logged lead is promoted from the newsroom (fish-for-leads skill) — opens the case, runs drilldown, compiles evidence, verifies the finding (builder → skeptic → judge), and conducts a novelty scan. Defines durable on-disk case files (hypothesis, sourced evidence, running log), a layered data architecture that keeps the immutable source database, shared rebuildable derived tables, and case-local artifacts separate and reproducible. Built for the db/gain.db corpus but the discipline is general. Use when promoting a lead to a case, starting or resuming an investigation, building or refuting a case from data, managing investigation state across context windows, or verifying a finding. Trigger phrases: promote a lead, open a case, track an investigation, resume the investigation, build a case, verify a finding."
license: MIT
---

# Track an investigation

Keeps a case reproducible, sourced, and resumable across sessions — so a finding
can survive an editor, a lawyer, and a skeptical reader. Leads come from
`fish-for-leads`'s go-fish operation; this skill picks up at promotion.

## Promote a lead → open a case

When the editor picks a candidate from the newsroom's lead run-record:

1. Read the `leads` row: `slug`, `story`, `claim`, `probe_sql`, `scout_number`,
   `boring_explanation`, `screen_run_id`.
2. Set promotion state in `newsroom.db` and record the actions:
   ```sql
   UPDATE leads SET promoted_at = datetime('now'), case_slug = '<slug>',
                    disposition = 'promoted',
                    disposition_reason = 'promoted to case <slug>',
                    disposition_at = datetime('now')
   WHERE slug = '<slug>';
   -- + one `actions` row each for the promote and the open-case (actor
   --   editor / agent-live / agent-auto; editor-directed born acknowledged
   --   with reviewed_by). Promotion may be PROVISIONAL in unattended runs —
   --   see fish-for-leads/reference/actions.md for the review queue and the
   --   budget cap on unacknowledged promotions.
   ```
3. Create `investigations/<slug>/` with: `case.md`, `evidence.md`, `log.md`,
   `queries.sql`. Optionally `analysis/` + `derived/`.
4. Seed `case.md` from the lead's `story` (why newsworthy) and `claim`
   (hypothesis). The `scout_number` is the starting figure — tag it unverified
   until re-derived.

Templates: `reference/templates.md`.

## The case lives on disk, not in the conversation

A context window compacts and can't be cited. State lives in
`investigations/<slug>/`. Four files:

- **`case.md`** — hypothesis, why newsworthy, confirm/kill, one-line
  verdict + confidence, prior coverage, legal notes.
- **`evidence.md`** — one block per evidence item: claim → query/script +
  source record ids → verdict.
- **`log.md`** — append-only journal of what was done and decided; pointers
  to evidence blocks, not re-statements of their figures.
- **`queries.sql`** — every cited query, labeled, so numbers re-run.

## Resuming (do this first, every session)

1. Read `log.md` (most recent entries) — it says where you left off and the
   next step.
2. Read `case.md` for the current hypothesis + verdict + confidence.
3. Re-run a cited query if you need to reload a number — never trust a figure
   that isn't backed by a query in `evidence.md` / `queries.sql`.
4. Append to `log.md` as you go; update `case.md` status/confidence when it moves.

## Drilldown

Run deterministic queries against `gain.db` (read-only). For each finding:
write an evidence block in `evidence.md` with the exact query/script, source
record ids, and a one-line verdict. Log a pointer to it in `log.md` — don't
re-state the figure in the log, just point.

The `boring_explanation` from the original lead is the first thing to test.
Work through the lead's confirm/kill criteria systematically.

## Verifying a finding

Before anything reaches the findings report, run it through
**builder → skeptic → judge** (scale to stakes: skip for weak leads; mandatory
for report-bound claims). Full pattern and checklist: `reference/verification.md`.

Short version:
1. **Builder** assembles the strongest version of the case (claim + sourced
   evidence). Argues *for*. Updates `case.md` + `evidence.md`.
2. **Skeptic** (independent) tries to *kill* it — default stance: "this is
   nothing." Runs counter-queries. Must produce a concrete refutation *or*
   an explicit "couldn't refute, here's what I tried."
3. **Judge** weighs builder vs. skeptic, renders a verdict (`supported /
   refuted / needs-more / parked`) + confidence, writes it as the one-line
   verdict in `case.md`. May bounce back for more evidence.

Independence matters: the skeptic re-derives from the data, not just reads the
builder's case and agrees.

Record the judge's verdict in the `actions` journal (object=case,
action='verdict', priority 5 for report-bound work) — provisional until a
human acknowledges it, like every agent action. Novelty-scan verdicts are
recorded the same way (action='novelty-scan', priority 4).

## Novelty scan

After a finding is verified and before it reaches the report: run a bounded web
search to check whether it has been reported before. Record a `coverage` verdict
in `case.md` frontmatter: `novel` / `under-reported` / `well-covered`.

Full policy: `reference/prior-art.md`. Key points:
- `well-covered` demotes the scoop but keeps it as a precision exhibit.
- A *hit* (cited, dated article) is strong evidence; a *miss* is weak.
- News citations go in a fenced "Prior coverage" section — **never** in the
  evidence chain for any claim.

## Closing out a case

A case ends one of two ways — **kill** it (data stopped supporting the
hypothesis) or **close** it out (still think it's newsworthy, done with
data/LLM research for now). Both are terminal states with their own
frontmatter status; neither deletes anything. Checklist and templates:
`reference/closeout.md`.

Short version:
- **Kill:** requires a one-paragraph rationale in `case.md` — what refuted it,
  which evidence forced the call. Status → `killed`.
- **Close:** requires condensing `case.md`'s Verdict to a single current
  paragraph (not an accreted history — that belongs in `log.md`), confirming
  frontmatter (`status`/`confidence`/`coverage`) matches the actual latest
  state, and listing any pre-publication line items. Status → `closed`.

Kills and closes are recorded in the `actions` journal (priority 5) and may
be taken **provisionally** by an agent — a kill is reversible by design
(nothing is deleted; overturning it is an editor action plus a re-open). The
hard gate sits at the system boundary: **a case's Verdict may enter the
findings report — or drive any external contact — only when its action chain
is transitively acknowledged by a human, with `reviewed_by` recorded.** This
is also how claims about named people satisfy the human-review requirement.
Doctrine: `fish-for-leads/reference/actions.md`.

`case.md`'s Verdict section *is* the final report — no separate report file
per case. A cross-case findings report (the GAIN deliverable) pulls from
closed cases' Verdict + Prior coverage sections directly.

## Where data goes (so it stays reproducible)

- **`db/gain.db`** = immutable source of truth; cases *read* it.
- Numeric work product for one hypothesis → case-local `derived/`, produced by
  a deterministic script in `analysis/` that reads `gain.db`.
- Reusable derived data → *promote* it into `gain.db` as a `derived_*` table
  (and catalog it in `derived_tables` in `newsroom.db`).
- Every derived artifact is regenerable from a committed script.

Tiers, promotion path, and the build DAG: `reference/data-layers.md`.

## Provenance rules (non-negotiable)

- Every evidence claim records the **exact query/script** + **source record
  ids** (`filing_uuid` → lda.gov public URL — `filings/public/filing/{uuid}/print/`
  for lobbying filings, `filings/public/contribution/{uuid}/print/` for LD-203
  contribution filings; `url`; `house_filing_id`).
- Money: aggregate the parsed `*_amt`, quote the raw string as filed.
- Name-dependent claims carry the crosswalk `method` / `confidence`.
- External data gets a disclosed `sources/` manifest.

## Scale with the Workflow tool (user-triggered)

The verification tribunal can run as a fan-out of parallel agents; how to map
builder → skeptics → judge onto the Workflow tool, and when to run the roles
inline instead: see "Running it as a Workflow" in
[reference/verification.md](reference/verification.md).

---

## Adapting to another corpus

The discipline is general; four bindings are corpus-specific here. To adopt:

- **Source DB** — the immutable corpus (here `db/gain.db` + its rebuild
  script).
- **Lead ledger** — where promoted leads come from (here
  `investigations/newsroom.db`, owned by the sibling `fish-for-leads` skill;
  `sweep-for-screens` designs its screens).
- **Provenance-URL patterns** — how a record id becomes a public source URL
  (here the lda.gov templates above).
- **Skeptic checklist** — `reference/verification.md`'s failure-mode list is
  this corpus's tuition; rebuild it from *your* corpus's known failure modes
  (junk sentinel values, entity-resolution confidence, double-counting joins,
  base rates).

License: MIT.
