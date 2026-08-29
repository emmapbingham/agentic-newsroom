---
name: explore-sqlite-corpus
description: Creates a blank-canvas Jupyter exploration notebook for a SQLite corpus — pre-filled with the database connection, helper functions, and plot style, but no pre-written queries. Use when a user wants to start free-form data exploration on a SQLite database, needs an exploration notebook to accompany an orientation notebook, or wants a clean starting point for domain-driven analysis.
license: MIT
---

# Explore a SQLite Corpus

Create a ready-to-use Jupyter notebook at `exploration.ipynb` (or a
user-specified path) with all the boilerplate filled in. The notebook has no
pre-written queries — that is deliberate. The user drives exploration based on
their domain knowledge; this notebook just removes the setup friction.

## What to generate

One notebook with two cells:

**Cell 1 — markdown header:**
```markdown
# [Corpus Name] — Exploration

Free-form analysis notebook. Start from what you know about the domain —
write queries that answer the questions your external knowledge suggests.
When something looks anomalous, note it for follow-up.
```

(If the project has a case-tracking convention — a leads ledger, an
`investigations/` directory — name it in that last sentence instead of the
generic wording.)

**Cell 2 — setup (code):**
```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from IPython.display import display

DB_PATH = 'path/to.db'  # set to actual db path
conn = sqlite3.connect(DB_PATH)

def q(sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)

def pct(part, whole, decimals=1):
    return f"{part / whole * 100:.{decimals}f}%"

plt.rcParams.update({
    'figure.figsize': (10, 4),
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.grid': True,
    'axes.grid.axis': 'y',
    'grid.alpha': 0.4,
})

# Quick table listing — run this first to see what's available
tables = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", conn
)
display(tables)
```

Fill in the actual `DB_PATH` and corpus name (if the user didn't name a
database, glob for `*.db` / check project docs and confirm). That's the entire
notebook. Prerequisites: `pandas`, `matplotlib`, and Jupyter must be installed
in the project environment.

**Verify before handing off:** execute the notebook
(`jupyter nbconvert --to notebook --execute --inplace <path>`) and confirm the
setup cell runs and the table listing is non-empty. If it fails, fix `DB_PATH`
(or flag the missing dependency) and re-run — deliver a notebook that is known
to work, not one that should.

## After creating the notebook

Once the notebook is written, read any available schema documentation so you're
ready to help write correct queries without guessing column names. Look for:

- `docs/` — per-source DB manuals (e.g. `docs/*_db.md`)
- `CLAUDE.md` — may contain a table map and canonical join examples
- `PRAGMA table_info(<table>)` via Bash if docs are absent or incomplete

Do this silently — no need to summarize the docs to the user. The goal is to
have the schema loaded so that any query you suggest in the conversation uses
real column names.

## What not to add

Do not add sample queries, example analyses, or suggested questions. The point
is a blank canvas. If the user wants guidance on what to explore, that's a
conversation — not something to pre-populate in the notebook.

License: MIT.
