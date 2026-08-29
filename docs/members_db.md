# Member crosswalk tables in `db/gain.db`

The bridge that connects lobbying/contribution money to the press corpus. Built
from the public-domain `unitedstates/congress-legislators` dataset
(see `sources/congress-legislators.md`).

## Build / rebuild

```bash
python scripts/ingest_members.py        # -> db/gain.db (~40s; downloads source if missing)
python scripts/validate_members.py
```

Source-scoped + idempotent (`member_*` + `committees` + `honoree_member_map`).
Schema: `scripts/schema_shared.sql` + `scripts/schema_members.sql`.

## What's inside

| Table | Rows | What it is |
|---|---:|---|
| `members` | 12,766 | one row per legislator (536 current + historical), keyed by `bioguide` |
| `member_terms` | 45,530 | every term (type, state, district, party, dates) |
| `committees` | 230 | 49 committees + 181 subcommittees (`parent_committee_id`) |
| `member_committees` | 3,879 | current committee assignments (`side`, `rank`, `title`) |
| `honoree_member_map` | 51,250 | resolves contribution `honoree_name` → `bioguide` |
| `committee_issue_jurisdiction` | 134 | hand-curated committee → LDA issue-code map (see below) |

`members` also carries cross-ids: `fec_ids`, `opensecrets_id`, `govtrack_id`,
`icpsr_id`.

## The two joins this unlocks

```sql
-- 1. press rhetoric for a member who received money (bioguide is shared)
SELECT p.date, p.title FROM press_releases p WHERE p.bioguide_id = ?;

-- 2. contribution money -> the member honored (the new bridge)
SELECT mem.official_full, sum(i.amount_num) total
FROM senate_contribution_items i
JOIN honoree_member_map hm ON hm.honoree_name = i.honoree_name
JOIN members mem ON mem.bioguide = hm.bioguide
WHERE hm.bioguide IS NOT NULL
GROUP BY mem.bioguide ORDER BY total DESC;
```

Chain them and you have **say vs. pay**: money honoring a member ↔ their
committee power ↔ what they say in press releases.

## Honoree resolution — read the confidence

`honoree_member_map` is best-effort name matching with an auditable
`method`/`confidence` on every row:

- `full_name` / **1.0** — exact match on official or first+last name (14,962).
- `first_last` / **0.9** — first+last (handles nicknames, e.g. "Earl Buddy Carter").
- `last_unique` / **0.6** — only the last name matched, but it's unique in the
  pool (e.g. "Katherine Porter" → Katie Porter). Verify these before relying on them.
- unmatched (`bioguide` NULL) — **by design**: ~45% of distinct honorees are
  non-members (party committees NRSC/DSCC, leadership PACs, inaugural committees,
  caucuses, "N/A"). They account for ~41% of honored dollars and should *not*
  map to a member.

Matching pool = current members + historical whose last term ended ≥ 2015
(bounds last-name ambiguity to plausibly-honored people). **Filter
`confidence >= 0.9`** for high-trust analysis; treat `0.6` as a lead to confirm.

## Caveats

- A person honored in a non-member capacity (e.g. "Secretary Xavier Becerra")
  still resolves to their member `bioguide` if they ever served — correct
  identity, but note the context.
- Committee membership is **current congress only** (the source dataset doesn't
  carry historical membership) — **but see `member_committees_history` below**,
  which fixes this for the 2022–2026 corpus window.

## `member_committees_history` — point-in-time committee rosters (2022–2026)

`member_committees` (above) only carries the *current* roster: the upstream
`committee-membership-current.yaml` is a live file the `congress-legislators`
project scrapes and overwrites, with no separate historical-membership file
published. But the press+lobbying corpus spans 2022–2026 Q1 (117th, 118th,
119th Congresses), so using today's committee assignments to attribute
pre-2025 press/contributions would misattribute members who changed
committees between Congresses.

The fix: the file's **git history** has real point-in-time snapshots going
back to 2022 (it's been overwritten in place on every roster change since
at least 2019). This table pulls 18 pinned commit snapshots at ~2-3 month
spacing across 2022-01 through 2026-03 — including snapshots right after
both Congress transitions (118th: Feb 2023, 119th: Feb 2025) — and builds a
validity-windowed table.

```bash
python scripts/ingest_committee_history.py             # -> db/gain.db (downloads 18 pinned snapshots)
python scripts/ingest_committee_history.py --validate
python scripts/ingest_committee_history.py --refresh    # re-download snapshots
```

- **Grain:** `(bioguide, committee_id, valid_from)`. 11,779 rows across 18
  snapshots. `valid_to` is the next snapshot date the assignment was absent
  (or NULL if still held as of the latest pulled snapshot, 2026-03-25).
- **Approximation:** an assignment is treated as continuously held between
  two consecutive snapshots that both show it — a swap that happens and
  reverses *within* one ~2-3 month window is invisible. Bounded by snapshot
  spacing, not exact to the day.
- **Verified at build:** Jason Smith (`S001195`) resolves as HSWM (Ways &
  Means) chair as of the 2023-06-01 snapshot — matches the independently
  verified fact from the `ways-means-chair-money-magnet` case. 398 members
  have a 2023-02 committee assignment absent by 2025-02, confirming this is
  real roster change, not a static re-committed file.
- **Source:** pinned commit shas (not `main` — exact reproducibility),
  downloaded to `data/congress_legislators/history/` (gitignored). See
  `scripts/ingest_committee_history.py` for the sha/date list.
- **Caveats:** snapshot spacing (~2-3 months) means brief/reversed
  reassignments are missed; a subcommittee or committee that was renamed or
  restructured between snapshots may not resolve cleanly against the current
  `committees` table (rows referencing an unknown `committee_id` are silently
  dropped at build time — check `ingest_log` record count against raw YAML
  member counts if auditing coverage precisely).
- **Not yet wired into any consumer** — `derived_member_contribution_panel`
  (see `docs/derived_db.md`) still builds against `member_committees`
  (current-only); rebuilding it against this table is a documented follow-up,
  not yet done.

## `committee_issue_jurisdiction` — committee → LDA issue-code map

**Not** derived from `congress-legislators` or any raw source — hand-curated
editorial judgment, source of truth is the checked-in CSV
`investigations/reference/committee_issue_jurisdiction.csv`, loaded by
`scripts/ingest_committee_jurisdiction.py`. Built 2026-07-02 to give
lobbying-vs-press screens a real institutional anchor (which committee's
members should be talking about a given LDA issue code), since the corpus
cannot tie a lobbying activity to a specific committee or member directly
(`senate_activity_government_entities` and House `federal_agencies` only
resolve to chamber/agency, not committee).

```bash
python scripts/ingest_committee_jurisdiction.py          # -> db/gain.db
python scripts/ingest_committee_jurisdiction.py --validate
```

- **Grain:** `(committee_id, issue_code)`, `weight` in `primary`/`secondary`/`none`.
  134 rows. All 44 full (top-level) House + Senate committees are represented —
  either mapped to one or more issue codes, or given an explicit `weight='none'`
  row (issue_code NULL) documenting that the committee has no legislative-issue
  jurisdiction (Ethics, Rules, House Administration, investigative-only select
  committees like the Jan 6 subcommittee). The absence of a code is therefore a
  documented decision, not a silent gap.
- **Subcommittee rows** exist only for committees spanning genuinely distinct
  issue areas: Energy & Commerce, Financial Services (House) / Banking (Senate),
  Finance (Senate), Commerce/Science/Transportation (Senate), Energy & Natural
  Resources (Senate). Where both a full-committee fallback row and a
  subcommittee row exist for the same code family, **prefer the subcommittee
  row** — the full-committee row is marked `secondary` with a note pointing to
  the subcommittee to use instead.
- **Appropriations is full-committee only** (`HSAP`/`SSAP` → `BUD`,
  `primary`). Its subcommittees are organized by spending category (Defense,
  Labor-HHS-Education, etc.), not by the LDA's 79 issue codes, and mapping them
  would be a false-precision exercise — deliberately out of scope.
- **Verified against the one prior ad hoc mapping** (the `committee-funded-silence`
  screen, run 2026-06-23, whose jurisdiction assignments were never saved to
  disk): this table reproduces Ways & Means → TAX (primary), Armed Services →
  DEF (primary), E&C Health subcommittee → HCR + MMM (primary) — the three
  examples cited in that screen's notes.
- **Caveats:** this is a judgment call, not ground truth — committees legislate
  on overlapping and sometimes contested turf (e.g. Medicare touches both
  Ways & Means and E&C Health; tariffs touch both Ways & Means and Finance).
  `weight` distinguishes strong/clear jurisdiction from touches-on-it jurisdiction,
  but does not eliminate the overlap. A handful of `secondary` rows map policy
  areas with no dedicated LDA issue code (e.g. crypto/digital assets) to the
  closest existing code — noted per-row. Re-verify any specific committee's
  mapping against its own published jurisdiction rules before treating a
  screen result as a strong claim.
