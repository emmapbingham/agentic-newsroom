# Data-Quality Patterns

How to detect and surface data-quality signals in an orientation notebook.
Write one cell per check. Live queries only — no hard-coded facts.

## Contents
- [What to flag and how](#what-to-flag-and-how)
- [Common failure modes](#common-failure-modes)
- [Cell structure for a quality check](#cell-structure-for-a-quality-check)
- [When to flag vs. when to drop](#when-to-flag-vs-when-to-drop)

---

## What to flag and how

Two tiers:

**Tier 1 — flag inline** (affects interpretation of visible numbers): Add a
`print()` note directly below the relevant cell in the main analysis section.
Point the reader to documentation. Example:
```python
print("NOTE: 'N/A' values are included in the counts above — filter before "
      "member-level analysis. See docs/senate_db.md for detail.")
```

**Tier 2 — data-quality section only** (known issue, does not distort visible
numbers): A dedicated cell in the data-quality section that quantifies the issue.

Do not duplicate numbers between the two sections. If a count appears in section
2, do not restate it in section 7.

---

## Common failure modes

### Junk placeholder values in categorical/text fields

Pattern: fields that are nominally informative but contain "N/A", "See prior
filing", "None", "Unknown", "TBD", etc. Especially common in free-text fields
that were optional to fill out.

Detection:
```python
junk = q("""
SELECT column_name, count(*) AS n
FROM table_name
WHERE column_name IN ('N/A', 'None', 'Unknown', 'See prior filing', '')
GROUP BY column_name ORDER BY n DESC
""")
total = conn.execute('SELECT count(*) FROM table_name WHERE column_name IS NOT NULL').fetchone()[0]
junk['% of non-null'] = (junk['n'] / total * 100).map('{:.1f}%'.format)
junk['n'] = junk['n'].map('{:,}'.format)
display(junk)
```

Flag if: junk values are included in aggregates shown earlier. State which
earlier aggregate they affect.

### Duplicate source records

Pattern: same logical record ingested twice (same UUID, same composite key).

Detection:
```python
dups = conn.execute("""
SELECT count(*) - count(DISTINCT key_col) AS n_duplicates
FROM table_name
""").fetchone()[0]
print(f"Duplicate key_col values: {dups:,}")
```

Flag if non-zero. State whether the ingester deduplicated them or not.

### Mixed entity types in one column

Pattern: a column that should contain individual names also contains org names,
PAC names, committee names (e.g. contribution `honoree_name` mixing members
with NRSC/DSCC/PACs).

Detection: spot-check with a top-N query:
```python
top = q("""
SELECT honoree_col, count(*) AS n
FROM table_name
GROUP BY honoree_col ORDER BY n DESC LIMIT 20
""")
display(top)
print("NOTE: includes PACs and party committees — filter to individuals before "
      "member-level analysis.")
```

### Low-confidence crosswalk matches

Pattern: a name-matching crosswalk (no stable ID) produces matches at varying
confidence levels; low-confidence matches should be treated as leads, not facts.

Detection:
```python
low = conn.execute("""
SELECT count(*) FROM crosswalk_table
WHERE method = 'last_name_only' OR confidence < 0.7
""").fetchone()[0]
total_matched = conn.execute("""
SELECT count(*) FROM crosswalk_table WHERE resolved_id IS NOT NULL
""").fetchone()[0]
print(f"Low-confidence matches: {low:,} of {total_matched:,} resolved rows ({pct(low, total_matched)})")
print("Treat as leads to verify — not publishable facts.")
```

### Negative or implausible numeric values

Pattern: monetary or count columns with negative values (refunds, data-entry
errors) that inflate/deflate aggregates if not filtered.

Detection:
```python
neg = conn.execute("""
SELECT count(*), min(amount_col), max(amount_col)
FROM table_name WHERE amount_col < 0
""").fetchone()
print(f"Negative amounts: {neg[0]:,}  min={neg[1]:,}  max={neg[2]:,}")
print("NOTE: Negative values exist — filter amount_col > 0 before summing.")
```

### Sparse key fields (< 95% coverage)

Pattern: a join key or id column that is supposed to be universal but has
unexpected NULLs. Indicates partial ingestion, optional filing, or a schema
mismatch.

Detection:
```python
null_rate = conn.execute("""
SELECT
  count(*)                                               AS total,
  sum(CASE WHEN key_col IS NULL THEN 1 ELSE 0 END)       AS n_null
FROM table_name
""").fetchone()
if null_rate[1] / null_rate[0] > 0.05:
    print(f"WARNING: key_col is {null_rate[1]/null_rate[0]*100:.1f}% null — joins will drop these rows.")
```

---

## Cell structure for a quality check

Each quality check cell should:
1. Run a live query
2. Print a short descriptive header
3. Display the result
4. Add a `print()` explanation of what the numbers mean for downstream use

Template:
```python
result = q("SELECT ...")
total = conn.execute("SELECT count(*) FROM ...").fetchone()[0]
result['%'] = (result['n'] / total * 100).map('{:.1f}%'.format)
result['n'] = result['n'].map('{:,}'.format)
print("Table: description of what this check reveals")
print("(implication for analysis — what to filter or flag)")
display(result)
```

Precede each cell with a one-sentence markdown cell naming the check, so the
notebook is scannable.

---

## When to flag vs. when to drop

**Flag** (keep in the notebook):
- Issues that affect numbers already shown (wrong totals, inflated aggregates)
- Issues a data user will hit within the first few queries (missing join keys)
- Issues that are surprising given the stated schema or documentation

**Drop** (document elsewhere, e.g. in `docs/`):
- Build-time facts that are already handled and have no ongoing effect
  (e.g. "10 files had bad characters; they were sanitized on ingest")
- Issues with zero rows (e.g. a dedup check that finds no duplicates)
- Issues documented elsewhere that do not affect this corpus's numbers
