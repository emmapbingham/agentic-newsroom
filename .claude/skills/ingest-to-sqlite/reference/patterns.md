# Schema & ingestion patterns (SQL)

## Contents
- Source ID as primary key
- Money/numbers: raw + parsed
- Controlled vocabulary → reference table
- Nested array → child / link table
- FTS5 over free text
- Source-scoped, idempotent rebuild
- Dedupe exact-duplicate source records
- Recover, don't silently drop
- Validate by reconciliation

Concrete DDL/SQL for the methodology in `SKILL.md`. Adapt names to your data.

## Source ID as primary key

If the source has a stable id, use it directly — no surrogate needed.

```sql
CREATE TABLE registrants (
    id   INTEGER PRIMARY KEY,   -- the source's own id; never reassigned
    name TEXT NOT NULL,
    ...
);
```

If a nested object lacks an id, use an autoincrement surrogate but keep the
parent's source key as a foreign key.

## Money/numbers: raw + parsed

```sql
income      TEXT,   -- exactly as filed: '10000.00', '', or NULL
income_amt  REAL    -- parsed; NULL if blank/unparseable
```
```python
def money(v):
    if v is None: return None
    t = str(v).strip().replace("$", "").replace(",", "")
    try: return float(t) if t else None
    except ValueError: return None
```

## Controlled vocabulary → reference table

```sql
CREATE TABLE IF NOT EXISTS ref_issue_codes (value TEXT PRIMARY KEY, name TEXT);
-- fact table references it:
CREATE TABLE activities (
    ...,
    issue_code TEXT REFERENCES ref_issue_codes(value)
);
```
Backfill any code seen in data but missing from the official list, so foreign
keys never dangle: `INSERT OR IGNORE INTO ref_issue_codes VALUES(?, ?)`.

## Nested array → child / link table

```sql
-- 1:N child
CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY,
    parent_uuid TEXT NOT NULL REFERENCES filings(filing_uuid),
    seq         INTEGER,            -- preserve array order
    ...
);
-- M:N link (e.g. activity <-> lobbyist)
CREATE TABLE activity_lobbyists (
    activity_id INTEGER REFERENCES activities(activity_id),
    lobbyist_id INTEGER REFERENCES lobbyists(id),
    role        TEXT
);
```

## FTS5 over free text

Standalone FTS table with the surrogate key as an unindexed column to map back:

```sql
CREATE VIRTUAL TABLE activities_fts USING fts5(
    description, notes, activity_id UNINDEXED);
INSERT INTO activities_fts(rowid, description, notes, activity_id)
SELECT activity_id, description, notes, activity_id FROM activities;
```
```sql
SELECT a.* FROM activities_fts f JOIN activities a ON a.activity_id=f.activity_id
WHERE activities_fts MATCH '"phrase here" OR keyword';
```

## Source-scoped, idempotent rebuild

`schema_shared.sql` (every ingester runs it; never drops):
```sql
CREATE TABLE IF NOT EXISTS ref_issue_codes (...);
CREATE TABLE IF NOT EXISTS ingest_log (
    id INTEGER PRIMARY KEY, source TEXT, source_file TEXT,
    record_kind TEXT, n_records INTEGER, ingested_at TEXT);
```
`schema_<source>.sql` (owns one namespace; drops+creates only its tables):
```sql
DROP TABLE IF EXISTS src_child;   -- children before parents
DROP TABLE IF EXISTS src_parent;
CREATE TABLE src_parent (...);
CREATE TABLE src_child  (...);
```
Ingester: run shared then per-source schema, clear own log rows, load.
```python
con.executescript(open("schema_shared.sql").read())
con.executescript(open("schema_src.sql").read())
con.execute("DELETE FROM ingest_log WHERE source = 'src'")
```

## Dedupe exact-duplicate source records

```python
seen = set()
for rec in records:
    key = rec["uuid"]
    if key in seen:        # byte-identical dupes appear in real dumps
        dups += 1; continue
    seen.add(key)
    ...
print(f"duplicate records skipped: {dups}")
```

## Recover, don't silently drop

```python
def parse_root(fp):
    try:
        return ET.parse(fp).getroot(), False
    except ET.ParseError:
        raw = fp.read_bytes().decode("utf-8", "replace")
        cleaned = strip_invalid_xml_char_refs(raw)   # fix and retry
        try: return ET.fromstring(cleaned), True
        except ET.ParseError: return None, False      # truly unparseable -> count it
```

## Validate by reconciliation

```python
db_n  = con.execute("SELECT count(*) FROM filings").fetchone()[0]
raw_n = len({r["uuid"] for r in raw_records})         # distinct from the source
assert db_n == raw_n, f"{db_n} != {raw_n}"
assert not con.execute("PRAGMA foreign_key_check").fetchall()
```
Or use `scripts/check_db.py db --expect filings=<raw_n>`.
