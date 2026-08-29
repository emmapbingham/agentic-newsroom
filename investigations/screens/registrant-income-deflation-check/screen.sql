-- registrant-income-deflation-check screen
-- Mirror-image companion to registrant-income-crank-check: surfaces Senate
-- registrants with a real lobbyist team (>=5 lobbyists ever) whose
-- self-reported income-per-activity is implausibly LOW for their scale
-- (far below the corpus norm, ~$26,940/activity) -- the deflation-side
-- hypothesis (under-reporting, structuring) rather than the crank-check's
-- inflation-side one.
--
-- RESULT (2026-07-06): negative. All 4 flagged registrants hand-checked;
-- none are a deflation story. 3 are self-lobbying nonprofits/associations
-- (client == registrant -- "client income" isn't the right frame for
-- in-house lobbying: Food & Water Watch, SUNY Buffalo, American Apparel &
-- Footwear Association). The 4th, Capitol Advocacy Partners, is a
-- legitimate small-municipality government-relations shop with real flat
-- retainers ($5k-$20k/quarter) spread across 18 small clients (cities,
-- school districts, charter-school nonprofits) and a 10-lobbyist team --
-- low income-per-activity because the client base is genuinely small-dollar,
-- not because income is concealed.
--
-- METRIC-DESIGN TRAP this screen taught (see derived table's builder
-- docstring and the corpus beat book): income_per_activity MUST divide by
-- activities counted only on the filings that contributed to the income
-- sum, not by all activities the registrant ever logged. ~65% of this
-- corpus's filings carry no parseable income; dividing by all activities
-- mechanically deflates the ratio for any registrant with mostly-blank
-- quarters, regardless of real under-reporting. First build (uncorrected
-- denominator) false-flagged Kellen Company, Drummond Woodsum, and Delta
-- Development Group -- all sparse reporters, not deflators.
--
-- Run against db/gain.db. Requires: derived_registrant_income_deflation.

SELECT
  registrant_name,
  n_clients,
  n_lobbyists,
  n_filings_income,
  total_income,
  act_on_income_filings,
  income_per_activity,
  flag_reason
FROM derived_registrant_income_deflation
ORDER BY income_per_activity ASC;
