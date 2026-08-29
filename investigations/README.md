# Investigations

Durable, cross-session case files for investigative work over `db/gain.db`. The
operating manual is the **`track-investigation`** skill (`.claude/skills/`); this
README is the index and quick orientation.

## Read this first: these are working files, not published findings

This directory is the **raw substrate** of the investigative work, published
deliberately and in full. It contains cases at every status:

| Status | Meaning |
|---|---|
| `closed` / `written-up` | Investigated, verified, and (mostly) written up in `findings-report.md` |
| `killed` | Investigated and abandoned — the claim failed on accuracy, novelty, or newsworthiness |
| `open` | Still in progress; hypotheses unverified |

**Only [`findings-report.md`](../findings-report.md) represents concluded
work.** Everything here — including hypotheses that were tested and *rejected*
— is a working record. Case files name real people and organizations in
hypotheses that did not survive scrutiny; each one states its status,
confidence, and the strongest innocent explanation up front, and none asserts
wrongdoing. Read the `## Verdict` section before quoting anything.

We publish the negative results on purpose: a methodology that only shows its
wins isn't evaluable. The killed cases are where the discipline is visible.

## Why on disk (not in a chat)

A context window compacts and isn't reproducible or submittable. So an
investigation lives as files here: it survives sessions (resume by reading
`log.md`), it's versioned, every claim cites a source record, and it becomes the
raw material for the findings report.

## Structure

```
investigations/
  README.md          # this file
  newsroom.db        # editorial ledgers: screens, screen_runs, leads,
                     #   derived_tables, sweeps, actions
                     #   (durable state, tracked in git; schema_newsroom.sql)
  screens/           # <screen>/screen.sql + run-<id>/ shortlists & figures
  sweeps/            # fleet sweep reports
  briefs/            # editorial briefs
  <slug>/            # one promoted lead = one case
    case.md          # hypothesis · status · confidence · why it's newsworthy
    log.md           # running journal: tried, dead ends, open questions, next step
    evidence.md      # each claim -> exact query/script + source record ids -> verdict
    queries.sql      # reproducible queries
    analysis/        # deterministic scripts (read gain.db) -> derived/ (optional)
    derived/         # numeric work product: *.parquet / derived.db (optional)
```

Templates for `case.md` / `log.md` / `evidence.md` are in the skill's
`reference/templates.md`.

## The two tiers

1. **Leads** — every surfaced hunch is a row in `newsroom.db`'s `leads` table,
   carrying a plain-language `story`, `probe_sql`, `boring_explanation`, and a
   `disposition`. Cheap; this is the exploratory surface. (Earlier versions of
   this project kept these in a `LEADS.md` file; they now live in the ledger.)
2. **`<slug>/`** — a lead graduates to a case only after it passes the
   surfacing gates and an editor promotes it. This is the focused, convergent
   work.

## The newsroom layer (screening at scale)

Between raw hunches and case work sits a deterministic screening pipeline:
**derived tables** (shared `derived_*` tables — panels, baselines; proposed
with a named consumer, cataloged in `docs/derived_db.md` once built) →
**screens** (registered SQL emitting ranked shortlists; every run is logged in
`screen_runs`, which doubles as the multiple-comparisons ledger) → **leads**
(rows in the `leads` table, the currency that crosses into editorial review;
every state change also lands in `actions`). The ledgers live in `newsroom.db`
(`scripts/schema_newsroom.sql`). Browse everything — corpus, ledgers, canned
citation queries — with `scripts/serve_newsroom.sh` (Datasette).

## Where data lives (the short version)

- **`db/gain.db`** = immutable source of truth. Investigations *read* it.
- **case-local `derived/`** = numeric work product for *this* hypothesis,
  produced by a script in `analysis/` that reads `gain.db`.
- Reusable derived data is **promoted** into `gain.db` as a `derived_*` table
  (rebuildable, logged in `ingest_log.tier`). See the skill's
  `reference/data-layers.md`.

## Verifiability

Every evidence entry records the **exact query/script** and the **source record
ids** (`filing_uuid` / `url` / `house_filing_id`), so anyone can re-run it against
a rebuilt `db/gain.db` and get the same rows. Claims depending on a name match
carry the crosswalk `method`/`confidence`.

Start or resume work via the `track-investigation` skill.
