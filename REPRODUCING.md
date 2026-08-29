# Reproducing the database and the findings

Everything in [`findings-report.md`](findings-report.md) traces to a SQLite
database built deterministically from the challenge corpus. This repo contains
the complete build pipeline (`scripts/`) and, per finding, the exact queries
that produce the report's numbers (`investigations/<case>/queries.sql`).

## 0. Get the data

The corpus is the **GAIN Agentic AI Investigative Journalism Challenge**
dataset (Northwestern) — federal lobbying disclosures and congressional
messaging, 2022 – 2026 Q1:

| Directory | Contents | Size |
|---|---|---|
| `data/senate/` | Senate LDA filings + LD-203 contributions (JSON) | 2.2 GB |
| `data/house/` | House LDA filings (XML, ~409k files) | 5.9 GB |
| `data/congress_press/` | Member press releases (JSONL) | 504 MB |

The data is **not redistributed in this repo** (`data/` is gitignored) — it is
the challenge organizers' distribution to make. All of it originates in public
records: LDA filings are published by the Senate Office of Public Records and
the House Clerk (and are individually citable at `lda.gov`, see below), and
press releases come from members' own websites. Point `data/` at your copy —
a symlink is fine.

## 1. Rebuild `db/gain.db` (~7 minutes, ~3.9 GB)

Requirements: Python ≥ 3.13, PyYAML (`pip install pyyaml`, or `uv sync` using
the checked-in `pyproject.toml` / `uv.lock`). Everything else is stdlib.

No API key is needed to build the database or run any query in this guide. Two
scripts that *re-pull* congress.gov bill metadata need a free key — see
[`.env.example`](.env.example); their outputs are already committed, so you
only need it to refresh them.

```bash
ln -s /path/to/challenge-data data     # data/senate, data/house, data/congress_press
python scripts/build_gain_db.py --validate
```

The build runs the stages in dependency order — raw (`senate`, `house`,
`press`) → reference (`members`, committee jurisdiction/history) → derived
marts — and `--validate` reconciles row counts and foreign keys against the
raw source after each stage. Expected raw-stage counts:

| Table | Rows |
|---|---|
| `senate_filings` | 418,098 |
| `house_filings` | 409,650 |
| `press_releases` | 141,332 |
| `senate_contribution_items` | 636,805 |
| `honoree_member_map` | 51,250 |

One disclosed external input: the `members` stage builds the member↔bioguide
crosswalk from `unitedstates/congress-legislators` (public domain; see
[`sources/`](sources/)). The ingester downloads it into
`data/congress_legislators/` automatically if absent.

Other useful invocations:

```bash
python scripts/build_gain_db.py --only press   # refresh one stage in place
python scripts/ingest_senate.py                # or run a single ingester
```

## 2. Reproduce a finding's numbers

`investigations/<case>/queries.sql` holds the queries for each findings-report
entry, verified query-by-query against the built database on 2026-07-15. Each
query is preceded by a comment quoting the report claim it reproduces.

| Finding | Case directory |
|---|---|
| The JACK Act's blind spots | `investigations/jack-act-blind-spots/` |
| A New Mexico casino vs. a Texas tribal-gaming bill | `investigations/sunland-park-ysleta-opposition/` |
| Three provisions Congress passed with no public pressure | `investigations/invisible-provisions/` |
| How a federal privacy bill died (APRA) | `investigations/apra-lobbying-coalition/` |
| Amazon's PAC money didn't buy silence | `investigations/amazon-money-without-praise/` |
| Method demo: a trade association's "legislative bench" | `investigations/acu-legislative-bench/` |
| Method demo: a base-rate discipline for "critic takes money" | `investigations/critics-take-health-money/` |

```bash
sqlite3 db/gain.db < investigations/jack-act-blind-spots/queries.sql
```

Two cases need derived tables beyond the standard build:

- **`jack-act-blind-spots`** → run
  `python scripts/build_derived_convicted_lobbyist_register.py` first.
- **`amazon-money-without-praise`** (first query) and the ACU screen-context
  query → the client-alias index and press-mention tables:
  ```bash
  python scripts/build_derived_client_alias_index.py
  python scripts/apply_client_alias_llm_review.py \
      investigations/derived/client_alias_review/consolidated_review_2026-07-06.txt
  sqlite3 db/gain.db < investigations/derived/client_alias_review/manual_alias_rejects_2026-07-06.sql
  python scripts/build_derived_client_press_mentions.py
  ```
  The review file is disclosed investigation work product (agent-assisted alias
  review, 2026-07-06); the apply step is deliberately **not** part of the
  deterministic rebuild. Entity ids in these tables are build-local — the query
  files resolve entities by name, never by id. One population count in the ACU
  case (192 clients at case time) drifts to 188 on a fresh rebuild for this
  reason; the query's comment explains, and the report cites no rank from that
  screen.

Without the `sqlite3` CLI, the files are plain SQL:

```bash
python3 -c "import sqlite3; con=sqlite3.connect('file:db/gain.db?mode=ro',uri=True); \
[print(r) for r in con.execute('''<paste one query>''')]"
```

Claims resting on records outside the corpus (GAO reports, congress.gov action
history, press-release text at member websites, election results) are listed in
each case's `evidence.md` as external verification steps, with citations in the
report entry.

## 3. Verifying an individual record

Every fact row keeps its source record's ID or URL, so any claim can be checked
against the original filing:

| Source | How to cite / verify |
|---|---|
| Senate lobbying filing | `https://lda.gov/filings/public/filing/{filing_uuid}/print/` |
| Senate LD-203 contribution | `https://lda.gov/filings/public/contribution/{filing_uuid}/print/` |
| House filing | `house_filing_id` + `source_file` (the source XML) |
| Press release | `url` |

Note the two LDA paths use **different UUID namespaces** despite both columns
being named `filing_uuid`, and both require the trailing `/print/` — the bare
`.../{uuid}/` path 404s.

Money is stored twice everywhere: the raw string as filed, and a parsed `*_num`
/ `*_amt` column. Aggregate on the parsed column, quote the raw.

## 4. Browsing the corpus

```bash
scripts/serve_newsroom.sh    # Datasette over gain.db + newsroom.db,
                             # with canned cite_* provenance queries
```

## 5. The investigation working state

`investigations/` contains every case file (hypothesis logs, evidence journals,
dead ends), including cases that were killed or are still open. See
[`investigations/README.md`](investigations/README.md) — only
`findings-report.md` represents concluded work.

The newsroom ledger schema (screens, runs, leads, actions) is at
`scripts/schema_newsroom.sql` and also ships inside the fish-for-leads skill at
`.claude/skills/fish-for-leads/assets/schema_newsroom.sql`.
