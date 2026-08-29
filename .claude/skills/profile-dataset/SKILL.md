---
name: profile-dataset
description: Profiles an unknown structured dataset (JSON, JSONL, XML, or CSV) before ingesting it — reports a path-level schema with types, null/empty rates and list cardinality, flags candidate primary keys, and runs a key-integrity check that reveals whether an identifier is a clean stable key or needs entity resolution. Use when starting on an unfamiliar dataset, deciding how to model or join data, choosing primary/foreign keys, assessing data quality, or before writing an ingestion or ETL script. Trigger phrases include profile a dataset, inspect data structure, schema discovery, what is in this file, find the key, and JSON/XML/CSV structure.
license: MIT
---

# Profile a dataset

Understand an unfamiliar structured dataset **before** you write any ingestion
code. The bundled profiler answers the three questions that decide a schema:

1. **What fields exist, and how reliable are they?** — path-level types, null/
   empty rates, list cardinality, example values.
2. **What can serve as a key?** — scalar fields that are ~unique (candidate
   primary keys) and very-high-cardinality fields (ids or free text).
3. **Is a given id actually a clean key, or does it need entity resolution?** —
   does one id map to one name, and does a name map to one id?

## Quick start

```bash
python scripts/profile.py PATH [PATH ...] [--format auto|json|jsonl|xml|csv] [--sample N]
```

- Globs are supported and expanded: `'data/house/2025_1stQuarter_XML/*.xml'`.
- `--sample N` caps records **per file** (0 = all) for JSON/JSONL/CSV. XML is
  one record per file, so `--sample` has no effect there — cap cost by passing
  fewer files (e.g. one quarter's glob). Use all records when you need exact
  null rates / key checks.
- Format is auto-detected by extension; override with `--format`.
- For XML, each file's root element is one record; nested elements become paths
  (repeated tags become lists), so `alis.ali_info[].issueAreaCode` reads like
  JSON.

### Key-integrity check (the important one)

To decide whether an identifier is a stable join key or a fuzzy mess, pass a
candidate id and a name field (dotted paths for nested fields):

```bash
python scripts/profile.py data/...json --key registrant.id --name registrant.name
```

It reports (names are compared case- and whitespace-insensitively, so
`"ACME Corp"` vs `"Acme Corp"` does not count as ambiguity; raw variants are
shown in the examples):
- `<key> values mapping to >1 <name>` → **0 means a CLEAN key** (the id always
  names the same entity).
- `<name> values mapping to >1 <key>` → **0 means 1:1**; non-zero means the same
  name appears under multiple ids (deduplication / entity resolution needed).

## How to read the output

- **SCHEMA** — one line per field path. High `empty%` on a field you wanted to
  join on is a red flag. `len[max=N]` on a list shows the worst-case fan-out.
- **CANDIDATE KEYS** — fields that are ~unique are primary-key candidates;
  fields flagged "high-cardinality" are usually a key or free text.
- **KEY INTEGRITY** — see above. This is what tells you to trust an id vs. build
  a crosswalk.

## Workflow

1. Profile a representative slice (one file or a `--sample`).
2. Read off the primary key, the foreign keys (ids that recur across records),
   and the fields too sparse to rely on.
3. Run `--key/--name` on each id you plan to join on. Trust clean keys; plan
   entity resolution for the rest.
4. Hand the schema to an ingestion step (see the `ingest-to-sqlite` skill).

Worked examples that produced real schemas with this approach live in the
project this skill came from, as `scripts/discover_*_schema.py` in the
agentic-newsroom repo (https://github.com/emmapbingham/agentic-newsroom) —
not bundled with the skill.

The profiler is stdlib-only (no dependencies). License: MIT.
