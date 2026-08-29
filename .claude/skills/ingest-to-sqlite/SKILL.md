---
name: ingest-to-sqlite
description: Turns a messy structured dataset (JSON, JSONL, XML, CSV, or nested API dumps) into a normalized, queryable, auditable SQLite database. Encodes a verifiable-ingestion methodology — preserve the source's own IDs as keys, store money and numbers both raw and parsed, fold controlled vocabularies into reference tables, add FTS5 for free text, stamp every fact row with a source key or URL, make rebuilds source-scoped and idempotent, and validate by reconciling row counts and foreign keys against the raw source. Use when building a database or ETL pipeline from raw data files, designing a SQLite schema, normalizing nested data, or making query results traceable for journalism, research, or analytics. Includes a generic database verifier.
license: MIT
---

# Ingest to SQLite (verifiably)

A repeatable way to turn raw data files into a SQLite database you can trust:
cheap to query, normalized, and auditable — every row traceable back to its
source record. Optimized for the case where downstream claims must be defended
(journalism, research, compliance).

**Profile first.** Don't design a schema blind — run the `profile-dataset` skill
to learn the keys, fan-out, and sparsity, then come back here.

## The methodology

1. **Preserve the source's own IDs.** If the data already has stable ids
   (`registrant.id`, a UUID, a filing number), make them your primary/foreign
   keys. Never fuzzy-match what is already keyed. Only build a crosswalk for the
   fields that genuinely lack ids.
2. **One fact per row.** Flatten nested arrays into child tables with a foreign
   key back to the parent (M:N → a link table). Keep a `seq` for array order.
3. **Store money/numbers twice:** the raw string exactly as filed (auditable)
   and a parsed numeric column (`*_amt`). Aggregate on the parsed column, quote
   the raw one.
4. **Controlled vocabularies → reference tables** (`ref_*`) with foreign keys.
   Codes/enums become small lookup tables shared across sources.
5. **Free text → FTS5.** Add a full-text index for any body/description field
   you'll search. Map the FTS rowid to your surrogate key.
6. **Stamp provenance on every fact row** — the `filing_uuid` / `url` /
   `source_file` that lets any value resolve to the public record.
7. **Source-scoped, idempotent rebuilds.** Split the schema into a shared part
   (`CREATE ... IF NOT EXISTS` for `ref_*` + an `ingest_log` with a `source`
   column) and a per-source part (`DROP`+`CREATE` only that source's tables).
   Re-running one source never touches the others. No whole-file wipes.
8. **Validate by reconciliation, not vibes.** After loading, assert the row
   count equals the distinct-record count from the raw source, and that there
   are zero orphan foreign keys. See "Verify" below.
9. **Log what you dropped.** Exact-duplicate source records, unparseable files,
   rows missing a key — count them and print the totals. Silent loss reads as
   "complete" when it isn't. (Recover where you can: e.g. sanitize bad input and
   retry before giving up on a record.)

Concrete SQL/DDL for each pattern is in [reference/patterns.md](reference/patterns.md).

## Build hygiene

- Bulk load with `PRAGMA journal_mode=OFF; synchronous=OFF; foreign_keys=OFF`,
  then turn foreign keys back ON and run the checks. (A rebuildable artifact
  doesn't need crash safety mid-build.)
- Dedupe dimensions in memory on their id; write them once at the end.
- `executemany` with batched lists; commit per file.

## Verify

```bash
python scripts/check_db.py path/to.db \
  --expect main_table=<raw_count> other_table=<raw_count>
```

Runs `quick_check` + `foreign_key_check`, prints every table's row count, and
reconciles the `--expect` counts against numbers you computed from the raw
source. Exits non-zero if anything fails — wire it into the build.

## Worked examples

The project this skill came from — the agentic-newsroom repo
(https://github.com/emmapbingham/agentic-newsroom) — ingests three very
different sources with exactly this methodology. Read them as templates; they
are not bundled with the skill:
- nested JSON with clean ids → `scripts/ingest_senate.py` + `scripts/schema_senate.sql`
- ~409k XML files, no UUIDs, bad chars recovered → `scripts/ingest_house.py`
- flat JSONL + FTS + derived roster → `scripts/ingest_press.py`

Stdlib only. License: MIT.
