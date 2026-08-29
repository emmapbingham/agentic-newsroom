# External source: congress.gov Bill API (api.congress.gov)

Used to check cosponsorship on the four bills named in Amazon's LDA lobbying-
activity descriptions (case `investigations/amazon-money-without-praise/`), to
test whether members who took Amazon PAC-adjacent money and criticized Amazon
in press releases also cosponsored the antitrust/warehouse-worker bills Amazon
was lobbying on.

- **Source:** https://api.congress.gov/ (official Library of Congress API)
- **License:** U.S. government work, public domain.
- **Retrieved:** 2026-07-08.
- **Auth:** requires a free API key (https://api.congress.gov/sign-up), stored
  in gitignored `.env` as `CONGRESS_GOV_API_KEY` — never committed.
- **Bills pulled:**
  - S.2992 (117th Congress) — American Innovation and Choice Online Act
  - H.R.3816 (117th Congress) — American Innovation and Choice Online Act
  - S.4260 (118th Congress) — Warehouse Worker Protection Act
  - H.R.8639 (118th Congress) — Warehouse Worker Protection Act
- **Endpoints used:**
  - `/v3/bill/{congress}/{type}/{number}` — title, sponsor, latest action/status
  - `/v3/bill/{congress}/{type}/{number}/cosponsors` — full cosponsor list with
    `bioguideId` and `sponsorshipDate` (all four bills returned under the 250
    row pagination limit — no paging needed)
- **Downloaded to:** `data/congress_bills/` (gitignored raw JSON responses:
  `bill_<congress>_<type>_<number>.json`, `cosponsors_<congress>_<type>_<number>.json`)
- **Derived output:** `investigations/amazon-money-without-praise/derived/cosponsorship_crosswalk.json`
  — the 39 Amazon-money members (from screen 40 / entity_id=125) crossed
  against sponsor/cosponsor status on all four bills, keyed by `bioguideId`
  (same id space as `members.bioguide` in `gain.db` — no fuzzy matching
  needed, direct join).
- **Reproducibility:** re-run `investigations/amazon-money-without-praise/analysis/pull_cosponsors.py`
  (fetches from the API fresh) or re-derive from the saved raw JSON in
  `data/congress_bills/` if present.
- **Caveats:** cosponsor lists are live/current-as-of-retrieval; a member
  could withdraw cosponsorship (the API's `isOriginalCosponsor` field and a
  `withdrawnCosponsors` count are available but not pulled in this round —
  `pagination.countIncludingWithdrawnCosponsors` matched `count` for all four
  bills at retrieval time, i.e. zero withdrawals recorded then). None of the
  four bills received a floor vote in either chamber (confirmed via
  `latestAction` — all died in committee/calendar), so cosponsorship, not
  roll-call votes, is the only legislative-behavior signal available for this
  case.
