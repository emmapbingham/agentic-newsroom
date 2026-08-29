# Notebook Cell Templates

Canonical patterns for writing orientation notebook cells. Adapt to the actual
schema — these are templates, not copy-paste blocks.

## Contents
- [Setup cell](#setup-cell)
- [Ingest log cell](#ingest-log-cell)
- [Table inventory cell](#table-inventory-cell)
- [Volume-over-time cell](#volume-over-time-cell)
- [Money completeness cell](#money-completeness-cell)
- [Key field coverage cell](#key-field-coverage-cell)
- [Top-N dimension cell](#top-n-dimension-cell)
- [Bridge verification cell](#bridge-verification-cell)
- [TOC markdown cell](#toc-markdown-cell)

---

## Setup cell

Always the first code cell. Include the `pct()` helper and consistent plot style.

```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
from IPython.display import display
warnings.filterwarnings('ignore')

DB_PATH = 'path/to.db'   # <-- set to actual path
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

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

print('Connected to', DB_PATH)
```

---

## Ingest log cell

Use only if `ingest_log` exists. Query it; don't assume its columns — inspect
them first with `PRAGMA table_info(ingest_log)`.

Typical pattern (adapt column names to what is actually there):

```python
log = q("""
SELECT source, record_kind,
       sum(n_records)   AS total_records,
       count(*)         AS n_batches,
       max(ingested_at) AS last_ingested
FROM ingest_log
GROUP BY source, record_kind
ORDER BY source, record_kind
""")
display(log)
```

Precede with a markdown cell: "Every ingester writes here; row counts should
match the raw source counts."

---

## Table inventory cell

Build the list in Python from actual `sqlite_master` queries, then add
descriptions for the tables you know. Use `pd.option_context` for the
description column.

```python
# Discover all non-FTS tables
all_tables = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%_fts%' ORDER BY name"
).fetchall()]

# Provide descriptions for known tables; unknown ones get an empty string
descriptions = {
    'table_name': 'one-line description of what each row represents',
    # ...
}

rows = [{
    'table': t,
    'rows': conn.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0],
    'description': descriptions.get(t, ''),
} for t in all_tables]

counts = pd.DataFrame(rows)[['table', 'rows', 'description']]
counts['rows'] = counts['rows'].map('{:,}'.format)
with pd.option_context('display.max_colwidth', None):
    display(counts)
```

---

## Volume-over-time cell

For a table with a date or year column. Produces a bar chart + summary table.

```python
by_year = q("""
SELECT strftime('%Y', date_col) AS year, count(*) AS n
FROM your_table
WHERE date_col IS NOT NULL
GROUP BY year ORDER BY year
""")

fig, ax = plt.subplots()
ax.bar(by_year['year'], by_year['n'], color='steelblue')
ax.set_title('Records per Year')
ax.set_xlabel('Year'); ax.set_ylabel('Count')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout(); plt.show()

total = by_year['n'].sum()
by_year['% of total'] = (by_year['n'] / total * 100).map('{:.1f}%'.format)
by_year['n'] = by_year['n'].map('{:,}'.format)
display(by_year)
```

---

## Money completeness cell

For tables with a raw money string + a parsed numeric column (e.g. `income` /
`income_amt`). Shows what fraction of rows have usable money values.

```python
money = q("""
SELECT
  count(*)                                                             AS total,
  sum(CASE WHEN amt_col IS NOT NULL AND amt_col > 0 THEN 1 ELSE 0 END) AS has_value,
  sum(CASE WHEN raw_col IS NULL THEN 1 ELSE 0 END)                     AS no_raw
FROM your_table
""")
t = money['total'][0]
rows = [
    {'field': 'total rows',             'count': f"{t:,}",                          '% of total': '100.0%'},
    {'field': 'has parsed amount > 0',  'count': f"{money['has_value'][0]:,}",       '% of total': pct(money['has_value'][0], t)},
    {'field': 'no raw string at all',   'count': f"{money['no_raw'][0]:,}",          '% of total': pct(money['no_raw'][0], t)},
]
display(pd.DataFrame(rows))
```

Add a `print()` note explaining why blanks are expected (e.g. registration
filings, below-threshold reporters).

---

## Key field coverage cell

For each id or join-key column that will be used in joins. One table, multiple
fields.

```python
cov = q("""
SELECT
  count(*)                                                  AS total,
  sum(CASE WHEN col_a IS NOT NULL THEN 1 ELSE 0 END)        AS has_col_a,
  count(DISTINCT col_a)                                      AS distinct_col_a,
  sum(CASE WHEN col_b IS NOT NULL THEN 1 ELSE 0 END)        AS has_col_b,
  count(DISTINCT col_b)                                      AS distinct_col_b
FROM your_table
""")
t = cov['total'][0]
rows = [
    {'column': 'total rows',      'non-null': f"{t:,}",                         '% non-null': '100.0%', 'distinct': ''},
    {'column': 'col_a',           'non-null': f"{cov['has_col_a'][0]:,}",        '% non-null': pct(cov['has_col_a'][0], t), 'distinct': f"{cov['distinct_col_a'][0]:,}"},
    {'column': 'col_b',           'non-null': f"{cov['has_col_b'][0]:,}",        '% non-null': pct(cov['has_col_b'][0], t), 'distinct': f"{cov['distinct_col_b'][0]:,}"},
]
display(pd.DataFrame(rows))
```

---

## Top-N dimension cell

For a lookup dimension (top registrants, top issue codes, top members, etc.).
Always include `% of total` — and make the denominator the whole fact table,
not the top-N sum, so the percentage means what it says.

```python
top = q("""
SELECT dim_col, count(*) AS n
FROM fact_table
GROUP BY dim_col
ORDER BY n DESC
LIMIT 15
""")
total = q("SELECT count(*) AS n FROM fact_table")['n'][0]  # whole table, not top-15 sum
top_raw = top.copy()                                       # keep numeric n for charts
top['% of total'] = (top['n'] / total * 100).map('{:.1f}%'.format)
top['n'] = top['n'].map('{:,}'.format)
display(top)
```

For a horizontal bar chart (better than a vertical one for long labels):

```python
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(top_raw['dim_col'][::-1], top_raw['n'][::-1], color='steelblue')
ax.set_title('Top 15 — [Dimension Name]')
ax.set_xlabel('Count')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout(); plt.show()
```

---

## Bridge verification cell

For each foreign key that joins two source namespaces. Print the result as
structured prose so findings are readable without a table.

```python
bridge = q("""
SELECT
  count(*)                                                                  AS total,
  sum(CASE WHEN fk_col IS NOT NULL THEN 1 ELSE 0 END)                      AS matched,
  count(DISTINCT fk_col)                                                    AS distinct_fk
FROM child_table
""")
t = bridge['total'][0]
m = bridge['matched'][0]
print(f"Child rows total:      {t:>10,}")
print(f"Matched to parent:     {m:>10,}  ({pct(m, t)})")
print(f"Distinct FK values:    {bridge['distinct_fk'][0]:>10,}")
print()
print("Verdict: <state the match quality and whether the join is safe to use>")
```

For each bridge: state what it connects, the match rate, and whether it is
deterministic (id-to-id) or probabilistic (name-based / crosswalk).

---

## TOC markdown cell

Cell 0 of the notebook. Use Jupyter anchor format: `#n-section-title` (all
lowercase, spaces → hyphens, punctuation stripped).

```markdown
# [Corpus Name] — Database Orientation

**Purpose:** Build human confidence in `path/to.db` before drawing any
conclusions from it. Every number ties to a query you can re-run. This notebook
deliberately avoids identifying leads — it only answers: *what is in the
database, how complete is it, and where should we be cautious?*

**Contents**

1. [Setup & ingest log](#1-setup--ingest-log)
2. [Table inventory](#2-table-inventory)
3. [Source: namespace_a](#3-source-namespace_a)
4. [Source: namespace_b](#4-source-namespace_b)
5. [Cross-source bridges](#5-cross-source-bridges)
6. [Data-quality checks](#6-data-quality-checks)
```

Adjust section numbers and anchors to match the actual sections you write.
