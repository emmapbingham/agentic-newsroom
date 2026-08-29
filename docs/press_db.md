# Press-release tables in `db/gain.db`

Congressional press releases scraped from `*.house.gov` / `*.senate.gov` member
sites (`data/congress_press/`, 504 MB JSONL), in the `press_*` namespace of the
combined `db/gain.db`. Light, clean metadata wrapping a free-text body — so the
table is thin and the value is the FTS5 index over title + text.

## Build / rebuild

```bash
python scripts/ingest_press.py             # -> db/gain.db (~25s)
python scripts/validate_press.py --reconcile
```

Source-scoped + idempotent (rebuilds only `press_*`). Schema:
`scripts/schema_shared.sql` + `scripts/schema_press.sql`. Discovery:
`scripts/discover_press_schema.py`.

## What's inside (2022-01 – 2026-03)

| Table | Rows | What it is |
|---|---:|---|
| `press_releases` | 141,332 | one row per release: metadata + full `text` |
| `press_members` | 536 | roster derived from the corpus (most-recent metadata + span) |
| `press_fts` | 141,332 | FTS5 over `title` + `text` |

By chamber: 93,641 House / 47,569 Senate / 122 unattributed. By party: 79,065 D /
61,152 R / 993 Ind. By year: 2022=19.7k, 2023=30.2k, 2024=31.6k, 2025=48.3k,
2026 Q1=11.5k.

## Key facts (verified)

- **`url` is 100% unique** (141,332/141,332) — the natural key and the public
  source link for any quote. Stored with a surrogate `release_id` (= FTS rowid).
- **`bioguide_id` present on 99.9%** (122 missing — committee/leadership posts
  with no `member` object). This is the join key to the lobbying/contribution
  data, once the member↔bioguide crosswalk exists. **536 distinct members.**
- `date` ('YYYY-MM-DD') missing on 14 records; a derived `year` column supports
  fast grouping. `text` kept verbatim (newlines preserved) for exact quoting.

## Queries

```sql
-- a member's releases over time
SELECT date, title FROM press_releases
WHERE bioguide_id = 'C001059' ORDER BY date;

-- full-text search the corpus
SELECT p.date, p.member_name, p.title FROM press_fts f
JOIN press_releases p ON p.release_id = f.release_id
WHERE press_fts MATCH 'pharmaceutical OR "drug prices"'
ORDER BY p.date DESC;

-- volume by member
SELECT name, party, state, n_releases FROM press_members
ORDER BY n_releases DESC;
```

## Toward "say vs. pay"

`press_releases.bioguide_id` is the member key on this side; the lobbying side
identifies members only by free-text `honoree_name` (contributions) and by
chamber/committee (activities). The **member↔bioguide crosswalk** (from
`unitedstates/congress-legislators`) is the missing bridge — it maps honoree
names + committee assignments to `bioguide_id`, connecting rhetoric to money.
