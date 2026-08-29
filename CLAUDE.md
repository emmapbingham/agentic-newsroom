# CLAUDE.md

Working notes for Claude Code in this repo. Read this first, then
`docs/beat_book.md` (the corpus beat book) and the `docs/*_db.md` manuals for
detail.

## What this is

Our winning entry to the **GAIN Agentic AI Investigative Journalism
Challenge** (Northwestern, 2026). The work is complete; this file is the
working notes, kept because they document how the repo is meant to be used.

The deliverables were reusable **Agent Skills** (MIT, validating against the
Agent Skills spec) + a findings report + this kind of documentation, judged on
**Organization, Efficiency, Verifiability, Capability**. Every finding ties to
a specific source record.

**Approach:** foundation first — build a cheap, deterministic query
layer over the data → run many queries to surface a lead → pull on it → write up
the finding → crystallize the reusable moves into skills. Don't pick an
investigative angle before the data can answer it.

## The data (`data/`, gitignored)

Federal lobbying + congressional messaging, 2022 – 2026 Q1:
- `data/senate/` — Senate LDA filings + LD-203 contributions (JSON, 2.2 GB)
- `data/house/` — House LDA filings (XML, ~409k files, 5.9 GB)
- `data/congress_press/` — member press releases (JSONL, 504 MB)

All public records; expect self-reported data, gaps, inconsistent conventions.

## The database (`db/gain.db`, gitignored — a build artifact)

One combined SQLite DB. Each source owns a table namespace; shared `ref_*`
vocabularies and `ingest_log`. Build (~7 min total, ~3.9 GB):

```bash
python scripts/build_gain_db.py              # canonical from-scratch rebuild, in order
python scripts/build_gain_db.py --validate   # + reconciliation / integrity checks
python scripts/build_gain_db.py --only press # refresh one stage in place
# or run a single ingester directly: scripts/ingest_{senate,house,press,members}.py
```

`build_gain_db.py` runs the stages in dependency order — **raw** (`senate`,
`house`, `press`) → **reference** (`members`; its honoree resolution reads
`senate_contribution_items`) → **derived** (future `build_*` marts). Each
ingester is **source-scoped and idempotent** (drops/recreates only its own
tables); a full `build_gain_db.py` run wipes + rebuilds so shared-schema changes
take effect. Schema: `scripts/schema_shared.sql` + `scripts/schema_<source>.sql`.

**Lineage / data tiers.** Everything in `gain.db` is deterministically
rebuildable; `ingest_log.tier` records each build step as `raw | reference |
derived`. Investigation-specific numeric work product stays *out* of `gain.db`
(in `investigations/<slug>/derived/`); reusable derived data gets *promoted* into
a `derived_*` table. Full model: the `track-investigation` skill's
`reference/data-layers.md`.

### Table map (see `docs/*_db.md` for full columns)

| Namespace | Key tables |
|---|---|
| `senate_*` | `senate_filings`, `senate_lobbying_activities`, `senate_activity_lobbyists` (`covered_position`), `senate_activity_government_entities`, `senate_contribution_filings`, `senate_contribution_items` (`honoree_name`, `amount_num`), dims `senate_registrants`/`senate_clients`/`senate_lobbyists`, `senate_activities_fts` |
| `house_*` | `house_filings`, `house_activities`, `house_filing_lobbyists`, `house_foreign_entities`, `house_affiliated_orgs`, `house_activities_fts` |
| `press_*` | `press_releases` (`bioguide_id`, `text`), `press_members`, `press_fts` |
| `member_*` | `members` (`bioguide`, ids, party/state), `member_terms`, `committees`, `member_committees`, `honoree_member_map` (`honoree_name` → `bioguide`, `method`, `confidence`) |
| `ref_*` | `ref_issue_codes`, `ref_government_entities`, `ref_filing_types`, `ref_contribution_item_types` |

### The bridges (verified — these make it one corpus)

- **Senate ↔ House:** `house_filings.senate_registrant_id` (parsed from the
  House `senateID` prefix) → `senate_registrants.id`. Matches **100%** of House
  filings; 6,630 registrants file in both chambers.
- **Senate registrant ↔ House registrant id:** `senate_registrants.house_registrant_id`.
- **Press ↔ money (say vs. pay):** `press_releases.bioguide_id` ↔
  `members.bioguide`, and contribution `honoree_name` →
  `honoree_member_map.bioguide` → `members`. The crosswalk (from
  `unitedstates/congress-legislators`, `member_*` tables) is **built**; honoree
  matches carry `method`/`confidence` — filter `confidence >= 0.9` for
  high-trust analysis. `member_committees` adds committee context. See
  `docs/members_db.md`.

### Canonical joins

```sql
-- who lobbies whom on what (Senate)
SELECT r.name, c.name, a.general_issue_code_display, a.description
FROM senate_filings f
JOIN senate_registrants r ON r.id=f.registrant_id
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid;

-- a topic across all three corpora at once
SELECT count(*) FROM senate_activities_fts WHERE senate_activities_fts MATCH 'PBM';
SELECT count(*) FROM house_activities_fts  WHERE house_activities_fts  MATCH 'PBM';
SELECT count(*) FROM press_fts             WHERE press_fts             MATCH 'PBM';

-- a firm's footprint in both chambers (via the bridge)
SELECT count(*) FROM house_filings WHERE senate_registrant_id =
  (SELECT id FROM senate_registrants WHERE name LIKE 'BROWNSTEIN HYATT%');
```

The beat book (`docs/beat_book.md`, recipes in `docs/beat_book_recipes.md`)
has the full recipe library.

## Verifiability — every claim must cite a record

- Senate lobbying rows (`senate_filings`/`senate_lobbying_activities`) →
  `filing_uuid` → `https://lda.gov/filings/public/filing/{filing_uuid}/print/`
- Senate contribution rows (`senate_contribution_filings`/`senate_contribution_items`,
  LD-203) → `filing_uuid` → `https://lda.gov/filings/public/contribution/{filing_uuid}/print/`
  (different path segment — `contribution/` not `filing/` — and a different
  UUID namespace from lobbying filings, even though both columns are named
  `filing_uuid`). Both require the trailing `/print/` — the bare
  `.../{filing_uuid}/` path 404s. LDA is migrating `lda.senate.gov` →
  `lda.gov` (same paths); use `lda.gov` in new work.
- House rows → `house_filing_id` and `source_file`
- Press rows → `url`
Money is stored twice everywhere: raw string as filed + parsed `*_amt`.
Aggregate on the parsed column, quote the raw.

## Data-quality caveats (some are themselves stories)

- Junk free-text to filter when aggregating: `covered_position` and
  `honoree_name` contain `"N/A"`, `"See prior filing"`, `"Legislative
  Consultant"`; `honoree_name` mixes party PACs (NRSC/DSCC) with individuals and
  has no standard name format.
- Source dups: 72+7 byte-identical Senate `filing_uuid`s; deduped on ingest.
- 10 House XML files had XML-illegal characters; the ingester sanitizes +
  recovers them (100% coverage).
- House lobbyists are name-only (no stable id; fuzzy to the Senate dimension);
  House `federal_agencies` is free text, not a controlled vocab.

## Investigations & workflow

The pipeline: **sweep** (rare fleet op that designs screens, `sweep-for-screens`
skill) → **go fish** (everyday: run one live screen → surface 3–5 candidate leads
logged to `newsroom.db`, `fish-for-leads` skill) → **promote** one → **case**
(`track-investigation` takes over).

Screens are re-runnable SQL ranking queries carrying a `grain` (actor /
structure — structure screens get drilled to named actors before surfacing);
every run is logged (the multiple-comparisons ledger). Candidates pass
**surfacing gates** (template collapse, actor test, boring-explanation-first,
novelty-lite coverage check — `fish-for-leads/reference/lead-gates.md`) before
costing editor attention. Leads are an append-only run-record carrying a
plain-language `story`, `probe_sql`, `boring_explanation`, and a `disposition`
(gate suppression or editor verdict, with a one-line reason — the recorded
taste the next go-fish reads). Promotion hands off to the case, which owns the
verdict after. Before a finding ships, run **builder → skeptic →
judge** verification (the skeptic's checklist guards against this corpus's
failure modes: junk values, honoree match confidence, House+Senate
double-counting, base rates, multiple comparisons). All of this is encoded in
the **`track-investigation`**, **`sweep-for-screens`**, and
**`fish-for-leads`** skills.

Ledgers: `investigations/newsroom.db` (tracked; tables: `screens`, `screen_runs`,
`leads`, `derived_tables`, `sweeps`, `actions`; schema
`scripts/schema_newsroom.sql`). **Provisional autonomy:** every state change is
an `actions` row (actor `editor`/`agent-live`/`agent-auto`, review state,
signed `reviewed_by`); agents may act provisionally — including promote/kill —
and the editor reviews a ranked queue afterward. Hard gate: nothing
report-bound or external without a transitively acknowledged chain
(`fish-for-leads/reference/actions.md`).
Sweep reports: `investigations/sweeps/`. Browse corpus + ledgers:
`scripts/serve_newsroom.sh` (Datasette + canned `cite_*` provenance queries).
Fleet fan-outs (sweeps) are user-triggered Workflows — pilot one agent before
any fleet; probe budgets; tier models by fleet size.

## Layout

- `scripts/` — `discover_*` (profilers), `schema_*.sql`, `ingest_*`, `validate_*`,
  `build_gain_db.py` (ordered build). Stdlib + small analysis stack; uv, py ≥3.13.
- `docs/` — per-source DB manuals, plus `beat_book.md` (the corpus **beat
  book** — update it when a sweep/case teaches a new trap) and
  `press-issue-classifier.md`.
- `.claude/skills/` — seven Agent Skills: `profile-dataset`, `ingest-to-sqlite`,
  `orient-sqlite-corpus`, `explore-sqlite-corpus`, `track-investigation`,
  `sweep-for-screens`, `fish-for-leads`.
- `investigations/` — `newsroom.db` + `sweeps/` (newsroom layer; leads in DB,
  not a markdown file), per-case files (the findings substrate).
- `datasette/` — metadata for `scripts/serve_newsroom.sh`.
- `sources/` — external-data provenance manifests (e.g. congress-legislators).
- `database_orientation.ipynb` — build-confidence notebook over `db/gain.db`.
- `exploration.ipynb` — original data exploration (team).
- `findings-report.md` — the findings report: five findings + two method
  demonstrations. `figures/` holds its figures.
- `REPRODUCING.md` — how to rebuild the DB and re-derive the report's numbers.

## Conventions

- Don't load the raw 5.9 GB/2.2 GB files into a model — query `db/gain.db`.
- Use the IDs the data already provides; don't fuzzy-match what's keyed.
- New source → follow the `discover → schema_<src>.sql → ingest_<src>.py →
  validate_<src>.py` pattern; keep it source-scoped and idempotent.
