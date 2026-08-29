# Data layers — where everything lives, and why it stays reproducible

The invariant: **anything in `db/gain.db` is deterministically rebuildable from
committed scripts + disclosed sources.** What stays out is anything mutable,
hand-edited, or specific to one hypothesis. (Note: *derived* and *fuzzy* are fine
in `gain.db` — the crosswalk's `honoree_member_map` is both — as long as it's
rebuildable, source-scoped, and carries an audit trail.)

## The tiers (all in `gain.db`, namespaced, logged by `ingest_log.tier`)

| Tier | Examples | Built by | Notes |
|---|---|---|---|
| `raw` | `senate_*`, `house_*`, `press_*` | `ingest_<src>.py` | raw → normalized |
| `reference` | `member_*`, `committees`, `honoree_member_map`, future `fec_*` | `ingest_<src>.py` + disclosed `sources/` | external enrichment |
| `derived` | `derived_*` marts (e.g. `derived_member_contribution_panel`; panels, clusters, scored sets) | `build_<name>.py` | pure function of other `gain.db` tables |

What stays **out** of `gain.db`, in `investigations/<slug>/derived/`:
hypothesis-specific, exploratory, hand-tuned numeric work product that only one
case needs (parquet, or a per-case `derived.db`), produced by `analysis/*.py`.

## The build DAG

`scripts/build_gain_db.py` rebuilds the whole DB in dependency order:

```
raw (independent):  senate, house, press
reference:          members        # honoree resolution reads senate_contribution_items
derived:            build_*.py     # read only gain.db tables
```

A full run is a from-scratch rebuild (it wipes `db/gain.db` so shared-schema
changes take effect); `--only <stage>` refreshes one stage in place. Each stage
is itself source-scoped + idempotent.

## The promotion path (case-local → shared)

Shared derived data isn't designed up front — it **graduates**:

1. A case needs, e.g., a monthly member×issue panel → it starts as
   `investigations/<slug>/analysis/panel.py → derived/panel.parquet` (case-local).
2. A *second* case wants the same panel → that's the signal. Refactor `panel.py`
   into a deterministic, source-scoped `scripts/build_member_issue_panel.py` that
   writes a `derived_member_issue_panel` table in `gain.db`, log it
   (`tier='derived'`), document it in `docs/`, and add it to the DAG after `members`.
3. Now it's shared infrastructure, joinable in plain SQL, rebuilt with everything.

**Promote when:** reused ≥ 2×, deterministic, broadly meaningful, cheap to keep
fresh. Until then keep it case-local — premature promotion bloats the shared base.

## Writing an analysis script (case-local)

```python
import sqlite3, pandas as pd
con = sqlite3.connect("db/gain.db")               # READ the source of truth
df = pd.read_sql_query("SELECT ...", con)          # pull what you need
# ... compute (numpy / scipy / statsmodels) ...
out.to_parquet("investigations/<slug>/derived/panel.parquet")   # write work product
```

Rules: read `gain.db`, never write to it; deterministic (seed any randomness);
the script + its output are the citation in `evidence.md`.

## Available analysis tooling (installed)

`pandas`, `numpy`, `scipy`, `statsmodels` (cross-correlation, lagged regression,
significance tests), `matplotlib` (charts for the report), `pyarrow` (parquet I/O).
Add more with `uv add <pkg>` and note why in the case `log.md`.

## Lineage / "show your work"

`ingest_log` records `(source, tier, record_kind, n_records, ingested_at)` for
every build step. Any non-`raw` table should have a one-line note in `docs/`
saying what it's computed from and by which script. That's the reproducibility
the rubric's Verifiability axis rewards: raw → (ingest) → reference → (build) →
derived marts → (analysis) → case `derived/` → cited in `case.md`.
