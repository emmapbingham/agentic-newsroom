# db/gain.db schema map

Compact reference. Full column lists + caveats: repo `docs/senate_db.md`,
`docs/house_db.md`, `docs/press_db.md`.

## senate_* (Senate LDA — clean stable ids)

- **senate_filings** (`filing_uuid` PK) — `filing_type`, `filing_year`,
  `filing_period`, `registrant_id`→senate_registrants, `client_id`→senate_clients,
  `income`/`income_amt`, `expenses`/`expenses_amt`, `termination_date`,
  `filing_document_url`.
- **senate_lobbying_activities** (`activity_id` PK) — `filing_uuid`,
  `general_issue_code`→ref_issue_codes, `general_issue_code_display`,
  `description` (free text), `foreign_entity_issues`.
- **senate_activity_lobbyists** — `activity_id`, `lobbyist_id`,
  **`covered_position`** (revolving-door signal), `is_new`.
- **senate_activity_government_entities** — `activity_id`,
  `government_entity_id`→ref_government_entities (the chamber/agency lobbied).
- **senate_contribution_filings** (`filing_uuid` PK) — `registrant_id`,
  `lobbyist_id`, `filer_type`, `filing_year`.
- **senate_contribution_items** (`item_id` PK) — `filing_uuid`,
  `contributor_name`, `payee_name`, **`honoree_name`** (member/official),
  `amount`/`amount_num`, `date`.
- **senate_contribution_pacs** — `filing_uuid`, `pac_name`.
- **senate_filing_foreign_entities** — `filing_uuid`, `name`, `country`,
  `ownership_percentage`, `contribution`/`contribution_amt`.
- **senate_filing_affiliated_orgs**, **senate_filing_conviction_disclosures**
  (`lobbyist_id`, `date`, `description`).
- Dimensions: **senate_registrants** (`id` PK, `name`, `house_registrant_id`),
  **senate_clients** (`id` PK, `name`, `client_id`), **senate_lobbyists**
  (`id` PK, names).
- **senate_activities_fts** — FTS5(`description`, `foreign_entity_issues`,
  `activity_id` UNINDEXED).

## house_* (House LDA — name-only lobbyists, free-text agencies)

- **house_filings** (`house_filing_id` PK) — `doc_type` ('LD1'/'LD2'),
  `filing_year`, `filing_period` ('Q1'..'Q4'/'REG'), `organization_name`,
  `client_name`, **`senate_registrant_id`** (→senate_registrants.id — the
  bridge), `house_id`, `income`/`income_amt`, `expenses`/`expenses_amt`,
  `source_file`.
- **house_activities** (`activity_id` PK) — `house_filing_id`, `issue_area_code`,
  `description`, **`federal_agencies`** (free text = entity lobbied),
  `foreign_entity_issues`.
- **house_filing_lobbyists** — `house_filing_id`, `first_name`, `last_name`,
  `suffix`, **`covered_position`**, `is_new` (no lobbyist id).
- **house_foreign_entities**, **house_affiliated_orgs**, **house_convictions**.
- **house_activities_fts** — FTS5(`description`, `federal_agencies`,
  `foreign_entity_issues`, `activity_id` UNINDEXED).

## press_* (press releases)

- **press_releases** (`release_id` PK, `url` UNIQUE) — `title`, `date`, `year`,
  `domain`, `scraper`, **`bioguide_id`** (member key), `member_name`, `party`,
  `state`, `chamber`, `text` (full body).
- **press_members** (`bioguide_id` PK) — `name`, `party`, `state`, `chamber`,
  `n_releases`, `first_date`, `last_date`.
- **press_fts** — FTS5(`title`, `text`, `release_id` UNINDEXED).

## member_* (the bridge to members — built from congress-legislators)

- **members** (`bioguide` PK) — `first`, `last`, `nickname`, `official_full`,
  `is_current`, `last_type`/`last_state`/`last_party`, `fec_ids`,
  `opensecrets_id`, `govtrack_id`. 536 current + historical.
- **member_terms** — `bioguide`, `type`, `state`, `district`, `party`, `start`,
  `end` (one row per term).
- **committees** (`committee_id` PK) — `type`, `name`, `parent_committee_id`
  (subcommittees). **member_committees** — `bioguide`, `committee_id`, `side`
  (majority/minority), `rank`, `title`.
- **honoree_member_map** (`honoree_name` PK) — `bioguide`, **`method`**,
  **`confidence`** (1.0 full name … 0.6 last-name-only). Resolves
  `senate_contribution_items.honoree_name` → a member. NULL bioguide = a
  non-member honoree (PAC/committee/challenger), by design.
- **committee_issue_jurisdiction** (`committee_id`, `issue_code`) — hand-curated
  (not derived), source `investigations/reference/committee_issue_jurisdiction.csv`.
  `weight` primary/secondary/none. The only way to connect a lobbying issue
  code to a committee/member — neither `senate_activity_government_entities`
  nor House `federal_agencies` resolve below chamber/agency level. See
  `docs/members_db.md`.
- **member_committees_history** (`bioguide`, `committee_id`, `valid_from`,
  `valid_to`) — point-in-time committee rosters 2022-2026, from 18 pinned
  git-history snapshots of the upstream committee-membership file (which is
  otherwise current-Congress-only). Use instead of `member_committees` for
  any analysis spanning multiple Congresses. See `docs/members_db.md`.

## ref_* (shared lookups)

`ref_issue_codes` (value→name; 3-letter ALI codes, used by Senate + House),
`ref_government_entities` (id→name), `ref_filing_types`,
`ref_contribution_item_types`. `ingest_log` records each source's load.

## Bridges

```sql
house_filings.senate_registrant_id = senate_registrants.id          -- Senate<->House
senate_registrants.house_registrant_id                              -- secondary
press_releases.bioguide_id = members.bioguide                       -- press <-> member
senate_contribution_items.honoree_name = honoree_member_map.honoree_name
    AND honoree_member_map.bioguide = members.bioguide              -- money <-> member
```
