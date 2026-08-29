# House LDA tables in `db/gain.db`

The House Clerk's Lobbying Disclosure Act filings (LD-1 registrations, LD-2
quarterly reports), parsed from `data/house/` (~409k XML files, 5.9 GB) into the
`house_*` namespace of the combined `db/gain.db`. Same disclosure regime as the
Senate data, filed separately in a different XML shape — kept in its own tables
so House-vs-Senate discrepancies stay visible.

## Build / rebuild

```bash
python scripts/ingest_house.py             # -> db/gain.db (all dirs, ~3 min)
python scripts/validate_house.py           # add --find-unparsed to scan disk
```

Source-scoped and idempotent: drops/recreates only `house_*` tables and its own
`ingest_log` rows. Schema: `scripts/schema_shared.sql` + `scripts/schema_house.sql`.
Discovery evidence: `scripts/discover_house_schema.py`.

## What's inside (2022 – 2026 Q1)

| Table | Rows | What it is |
|---|---:|---|
| `house_filings` | 409,650 | one row per filing (LD1 or LD2), `doc_type` discriminator |
| `house_activities` | 830,597 | issue + free-text description per `ali_info`/`ali_Code` |
| `house_filing_lobbyists` | 1,409,887 | filing-level lobbyists (name-only) + `covered_position` |
| `house_foreign_entities` | 47,983 | foreign interests (LD1) |
| `house_affiliated_orgs` | 71,468 | affiliated orgs (LD1) |
| `house_convictions` | 1,160 | lobbyist criminal-conviction disclosures |
| `house_activities_fts` | 830,597 | FTS5 over description + federal_agencies |

`doc_type`: 385,929 LD2 (quarterly) + 23,721 LD1 (registrations). `filing_year`
and `filing_period` (`Q1`–`Q4`/`REG`) come from the source directory.

## The Senate↔House bridge (verified)

`house_filings.senate_id` is `"{senate_registrant_id}-{client_suffix}"`. The
prefix is parsed into **`senate_registrant_id`**, which matches a
`senate_registrants.id` for **409,627 / 409,650 (100.0%)** of House filings —
6,630 registrants appear in both chambers. This is a deterministic join, not a
fuzzy match:

```sql
-- registrants filing in both chambers
SELECT r.name, count(*) house_filings
FROM house_filings h JOIN senate_registrants r ON r.id = h.senate_registrant_id
GROUP BY r.id ORDER BY 2 DESC;

-- House activity full-text search
SELECT a.* FROM house_activities_fts f
JOIN house_activities a ON a.activity_id = f.activity_id
WHERE house_activities_fts MATCH 'cryptocurrency';
```

The weaker secondary link `house_id` (first 5–6 digits ≈
`senate_registrants.house_registrant_id`, ~62%) is kept raw for cross-checking.

## Differences from the Senate data (matter when querying)

- **House lobbyists have no stable ID** — name + `covered_position` only. They
  are stored inline per filing (not a keyed dimension); matching them to the
  Senate `lobbyist.id` dimension is a later fuzzy-ER task.
- **`federal_agencies` (entity lobbied) is free text** (e.g. "U.S. SENATE, U.S.
  HOUSE OF REPRESENTATIVES"), not a controlled vocabulary like the Senate's
  `government_entities`. Stored raw on `house_activities`.
- **Lobbyists normalized to the filing level.** LD2 nests them per `ali_info`;
  the ingester stores the deduped union per filing (drops the issue↔lobbyist
  pairing within a filing, which is rarely needed and preserved on the Senate
  side if it is).
- **LD1 vs LD2 asymmetry**: LD1 has filing-level lobbyists, bare `ali_Code`s
  (no description), and foreign/affiliated orgs; LD2 has per-`ali_info`
  descriptions + income/expenses and no foreign/affiliated orgs.

## Data-quality caveats

- **10 filings had invalid XML character references** (control chars illegal in
  XML 1.0) and failed a strict parse; the ingester sanitizes those references
  and recovers all 10 (coverage is 100%, lossless).
- Same junk free-text in `covered_position` as the Senate side: `"See prior
  filing"`, `"N/A"`, `"Legislative Consultant"`, `"Partner"` — filter when
  aggregating revolving-door signal. Real entries do surface (e.g. "Senior
  Counsel, House Financial Services Committee").
