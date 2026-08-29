# Senate LDA tables in `db/gain.db`

`db/gain.db` is the single combined investigation database. Each source owns a
table namespace (`senate_*`, later `house_*`, `press_*`) and shares the
reference vocabularies (`ref_*`) and the `ingest_log`. This doc covers the
Senate Lobbying Disclosure Act slice, built from `data/senate/`. It turns 2.2 GB
of deeply-nested JSON into queryable relational tables so investigative
questions become cheap, deterministic SQL with every answer traceable to a
source filing.

## Build / rebuild

```bash
python scripts/ingest_senate.py            # -> db/gain.db (all years, ~80s)
python scripts/validate_senate.py --reconcile
```

The build is **source-scoped and idempotent**: it drops and recreates only the
`senate_*` tables and refreshes shared `ref_*`, leaving any `house_*`/`press_*`
tables and their `ingest_log` rows untouched. Schema: `scripts/schema_shared.sql`
(shared) + `scripts/schema_senate.sql` (Senate). Discovery evidence:
`scripts/discover_senate_schema.py`.

## What's inside (2022 – 2026 Q1)

| Table | Rows | What it is |
|---|---:|---|
| `senate_filings` | 418,098 | LD-1/LD-2 filings (one registrant→client→period) |
| `senate_lobbying_activities` | 798,998 | one issue/description per row |
| `senate_activity_lobbyists` | 2,121,327 | activity↔lobbyist, with `covered_position` |
| `senate_activity_government_entities` | 2,015,824 | activity↔entity lobbied |
| `senate_contribution_filings` | 155,682 | LD-203 political-contribution reports |
| `senate_contribution_items` | 636,805 | individual contributions (`honoree_name`, `amount`) |
| `senate_contribution_pacs` | 22,377 | PACs named on reports |
| `senate_filing_foreign_entities` | 3,627 | foreign interests behind a client |
| `senate_filing_affiliated_orgs` | 3,663 | affiliated organizations |
| `senate_filing_conviction_disclosures` | 1,156 | lobbyist criminal-conviction disclosures |
| `senate_registrants` | 6,823 | dim — keyed on the API's `registrant.id` |
| `senate_clients` | 41,468 | dim — keyed on `client.id` |
| `senate_lobbyists` | 23,543 | dim — keyed on `lobbyist.id` |
| `senate_activities_fts` | 798,998 | FTS5 over activity descriptions |
| `ref_*` (shared) | — | controlled vocabularies (issue codes, gov entities, …) |

## Key design facts (verified, not assumed)

- **`registrant.id` is one global key** across both filings and contributions
  (0 name↔id collisions). It also carries **`house_registrant_id`** — a free
  bridge to the House LDA data.
- **`client.id`** (API-addressable, 1:1 with a name) is the clients PK.
  `client.client_id` is a coarser grouping (kept as a column for later
  entity-resolution, *not* the key).
- **`lobbyist.id`** is a stable global key.
- Money is stored twice: raw string as filed (`income`, `amount`, …) and parsed
  (`income_amt`, `amount_num`, …). Aggregate on the parsed column, cite the raw.
- Every fact row carries `filing_uuid`. The public record is:
  `https://lda.gov/filings/public/filing/{filing_uuid}/print/` for lobbying
  filings, or `https://lda.gov/filings/public/contribution/{filing_uuid}/print/`
  for contribution (LD-203) filings — different path segment, different UUID
  namespace, and both require the trailing `/print/` (the bare
  `.../{filing_uuid}/` path 404s). LDA is migrating `lda.senate.gov` →
  `lda.gov` (same paths); use `lda.gov` going forward.

## The investigative joins

```sql
-- who lobbies whom on what
SELECT r.name registrant, c.name client, a.general_issue_code, a.description
FROM senate_filings f
JOIN senate_registrants r ON r.id=f.registrant_id
JOIN senate_clients c     ON c.id=f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid;

-- revolving door: lobbyists who disclose a prior government post
SELECT l.first_name, l.last_name, al.covered_position, count(*) n
FROM senate_activity_lobbyists al JOIN senate_lobbyists l ON l.id=al.lobbyist_id
WHERE al.covered_position IS NOT NULL
GROUP BY al.lobbyist_id, al.covered_position ORDER BY n DESC;

-- money: contributions by honoree
SELECT honoree_name, sum(amount_num) total
FROM senate_contribution_items GROUP BY honoree_name ORDER BY total DESC;

-- full-text search activity descriptions
SELECT a.* FROM senate_activities_fts fts
JOIN senate_lobbying_activities a ON a.activity_id=fts.activity_id
WHERE senate_activities_fts MATCH '"artificial intelligence"';
```

## Data-quality caveats (some are themselves stories)

- **Exact-duplicate filings in source:** 72 filing + 7 contribution `filing_uuid`s
  appear twice (byte-identical); deduped on first occurrence.
- **Junk free-text values** to filter when aggregating:
  - `covered_position` includes placeholders: `"See prior filing"`, `"N/A"`,
    `"Legislative Consultant"` (not actually a covered position).
  - `honoree_name` includes `"N/A"` (~$22M unattributed) and party committees
    (NRSC, DSCC, NRCC, Senate Majority PAC) mixed with individual members.
- **`honoree_name` has no standard format** — "The Honorable Mike Flood",
  "Sen. Dan Sullivan", "US Senator Tammy Duckworth", "Rep. Adrian Smith". A
  member↔bioguide crosswalk (a later foundation step) is needed to join money to
  the press corpus.
- **Sparse money:** only ~65% of filings carry a parseable `income`/`expenses`.
- `government_entities` resolves only to chamber/agency level (SENATE, HOUSE,
  HHS, …) — not to a specific member or committee. Member-level targeting must
  be inferred from `description` text + committee membership.
