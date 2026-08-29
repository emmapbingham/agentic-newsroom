---
name: orient-sqlite-corpus
description: Produces a Jupyter orientation notebook for a multi-source SQLite corpus built with the ingest-to-sqlite convention. The notebook answers "what is in the database, how complete is it, and where should we be cautious?" — before any analysis or investigation begins. Use when a user asks to orient on a new SQLite database, build a database orientation notebook, understand what is in a corpus, or verify a database was built correctly.
license: MIT
---

# Orient a SQLite Corpus

Produce a Jupyter orientation notebook that builds human confidence in a SQLite
database **before** any analysis or investigation begins. The notebook's sole
question is: *what is in the database, how complete is it, and where should we
be cautious?* It is not an investigation notebook — no leads, no hypotheses.

## First step: inspect the database

Before writing any cells, run these queries to discover what the database
contains. Adapt the notebook to what you actually find.

```bash
# List all tables
sqlite3 path/to.db ".tables"

# Check whether an ingest_log table exists
sqlite3 path/to.db "SELECT name FROM sqlite_master WHERE type='table' AND name='ingest_log';"

# Get column counts for every table (cheap shape overview; row counts come
# from the summary-table cell in reference/notebook-cells.md)
sqlite3 path/to.db "SELECT name, (SELECT count(*) FROM pragma_table_info(name)) AS cols FROM sqlite_master WHERE type='table' ORDER BY name;"
```

Then read the cell templates and data-quality patterns:
- [reference/notebook-cells.md](reference/notebook-cells.md) — canonical cell patterns for every section
- [reference/data-quality.md](reference/data-quality.md) — how to detect and flag data-quality signals

## Notebook structure

Always include these sections (adapt queries to the actual schema):

1. **Setup & ingest log** — imports, DB connection, helper functions, ingest log summary if present
2. **Table inventory** — every table with row count + one-line description
3. **Per-source profiles** — one section per source namespace (e.g. `senate_*`, `press_*`); skip namespaces with no data
4. **Cross-source bridges** — verify every foreign key that joins two namespaces; compute match rate
5. **Data-quality checks** — live queries for known failure modes (see `reference/data-quality.md`)

Sections 3 and 4 are conditional on what you find. If there are no bridges, omit section 4.

## Per-source profile: what to always include

For each source namespace, write cells that cover:

- **Volume over time** — if a date/year column exists, bar chart of records by year
- **Filing/record type split** — if a type/category column exists, breakdown with %
- **Money completeness** — if numeric money columns exist, % with non-null positive values
- **Key field coverage** — for each id/join key column: % non-null, % distinct
- **Top-N dimension** — for the most-used lookup dimension (e.g. top registrants, top issue codes), a ranked table with % of total
- **FTS index** — if an FTS5 virtual table exists, confirm row count matches the source table

## Design rules (follow these in every cell you write)

See `reference/notebook-cells.md` for full templates. Short version:

- `display(df)` not `print(df.to_string())` — Jupyter renders proper HTML tables
- `pd.option_context('display.max_colwidth', None)` when a column contains descriptions
- Every count that has a natural denominator gets a `% of total` column; make the denominator explicit when it varies per row
- Format integers with `'{:,}'.format`, money with `'${:,.0f}'.format`
- Section headings use `---` + `## N. Title` markdown cells; include a linked TOC in cell 0
- Data-quality section: one cell per check, live queries only — no hard-coded facts; flag issues that affect interpretation of visible numbers with a pointer to docs

## Graceful fallback

If `ingest_log` is absent: skip the ingest log cell; open with the table inventory instead.

If a pattern (money, date column, bridge) is not present in this DB: omit that cell rather than showing an empty result.

Use `sqlite_master` to discover what tables and columns exist before writing cells that depend on them.

## Assumed conventions

The templates assume a DB built with the `ingest-to-sqlite` convention; each
degrades gracefully when its assumption is absent (see fallbacks above):

- source-namespaced tables (`<source>_*`) → drives the per-source sections
- an `ingest_log` table → drives the build-provenance cell
- money stored raw + parsed (`x`, `x_amt`) → drives money-completeness cells
- `*_fts` FTS5 shadow tables → drives the FTS reconciliation cell

## Verify before handing off

Execute the finished notebook end-to-end
(`jupyter nbconvert --to notebook --execute --inplace <path>`) and fix any
failing cell before presenting it. An orientation notebook exists to build
human confidence in the data — it must run clean, with every number produced
by the execution, not by hand.

License: MIT.
