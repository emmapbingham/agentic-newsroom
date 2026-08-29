# External source: `unitedstates/congress-legislators`

The member↔bioguide crosswalk (`member_*` tables in `db/gain.db`) is built from
this external dataset. Disclosed here per the challenge's outside-data rule.

- **Source:** https://github.com/unitedstates/congress-legislators
- **License:** Public domain (CC0 / "The data is in the public domain").
- **Retrieved:** 2026-06-09, from the `main` branch raw files.
- **Files used** (downloaded to `data/congress_legislators/`, gitignored):
  - `legislators-current.yaml` — 536 current members
  - `legislators-historical.yaml` — 12,230 historical members
  - `committees-current.yaml` — committees + subcommittees
  - `committee-membership-current.yaml` — current committee assignments
- **Download URL base:**
  `https://raw.githubusercontent.com/unitedstates/congress-legislators/main/<file>`

### Historical committee-membership snapshots (added 2026-07-02)

`committee-membership-current.yaml` is a **live file** the upstream project
scrapes and overwrites in place — there is no separate
`committee-membership-historical.yaml`, so the file above only ever gives
*today's* roster. To attribute committee membership correctly for 2022–2026
data (spanning the 117th, 118th, and 119th Congresses), `member_committees_history`
(`scripts/ingest_committee_history.py`) pulls the **same file's git history**
at 18 pinned commit shas — exact reproducibility via commit sha rather than
`main`:

- **Retrieved:** 2026-07-02.
- **Files used:** `committee-membership-current.yaml` at each of 18 pinned
  commits (not `main`), spanning 2022-01-04 to 2026-03-25 at roughly 2–3
  month intervals, including snapshots shortly after both Congress
  transitions (118th: 2023-02-17, 119th: 2025-02-02). The full list of
  (sha, date) pairs is in `scripts/ingest_committee_history.py`'s
  `SNAPSHOTS` constant — that list *is* the citable manifest; not
  duplicated here to avoid drift between two copies.
- **Download URL pattern:**
  `https://raw.githubusercontent.com/unitedstates/congress-legislators/<sha>/committee-membership-current.yaml`
- **Downloaded to:** `data/congress_legislators/history/` (gitignored),
  one file per snapshot.
- **Reproducibility:** `python scripts/ingest_committee_history.py` downloads
  any missing pinned snapshot and rebuilds `member_committees_history`.
  `--refresh` re-downloads all 18. Because every commit is pinned by sha
  (not `main`), this is exactly reproducible independent of when the
  upstream project's live file is next scraped/updated — unlike the
  `main`-branch files above, which drift over time unless a commit is
  pinned.
- **License/redistribution:** same as the rest of this manifest — public
  domain source, no upstream data redistributed in this repo (the YAML
  snapshots live under gitignored `data/`; only `member_committees_history`,
  a derived crosswalk table in the gitignored `db/gain.db` build artifact,
  and this manifest are produced).

## Reproducibility

`scripts/ingest_members.py` downloads any missing file from the URL base above,
then ingests. To refresh to the latest upstream data:

```bash
python scripts/ingest_members.py --refresh
```

Because the upstream dataset is updated over time (new members, committee
changes), pin a commit if exact reproducibility is required: download from
`.../raw/<commit-sha>/<file>` instead of `main`. The retrieved files are kept in
`data/congress_legislators/` so a given build is reproducible from them.

## How it's used

- `members`/`member_terms` — roster + cross-ids (FEC, OpenSecrets, GovTrack, ICPSR).
- `committees`/`member_committees` — who sits where (current congress).
- `member_committees_history` — who sat where, at any point 2022–2026
  (point-in-time, `valid_from`/`valid_to`; see the historical-snapshots
  section above and `docs/members_db.md`).
- `honoree_member_map` — resolves the free-text contribution `honoree_name` to a
  `bioguide`; matches carry a `method` + `confidence` (see `docs/members_db.md`).

No upstream data is redistributed in this repo (the YAML lives under the
gitignored `data/`). Only the derived crosswalk tables in `db/gain.db` (also a
gitignored build artifact) and this manifest are produced.
