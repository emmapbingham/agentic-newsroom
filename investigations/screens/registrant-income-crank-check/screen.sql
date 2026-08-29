-- registrant-income-crank-check screen
-- Surfaces Senate registrants whose self-reported LDA income is implausible
-- for their own scale: a flat income_amt repeated on >=3 filings for a
-- registrant with <=2 clients and <=2 lobbyists ever, at >=$100k.
--
-- Origin: a single confirmed crank filer ("STATE OF LOC NATION GLOBAL PUBLIC
-- BENEFIT CORPORATION" / registrant LOC COMMUNITY ASSOCIATION, filer
-- self-titling "HH Empress Queen Christina Clement") self-reported a flat
-- $20,000,000 on every 2025 quarterly filing and distorted the
-- Family/Abortion (FAM) issue code's 2025 apportioned-income aggregate by
-- roughly two-thirds. The LDA has no income-plausibility check at filing
-- time -- nothing stops a registrant from entering an arbitrary number.
--
-- HIGH PRECISION, NOT HIGH RECALL: this threshold caught exactly one
-- confirmed crank out of 16 flagged rows. The other 15 are small real firms
-- (plausible flat-retainer solo consultancies, income_per_activity in the
-- $560-$10,000 range) -- not cranks. A genuine finding from this screen
-- still requires the same manual read that caught LOC: pull the client's
-- own activity descriptions (incoherent/grandiose language, generic
-- boilerplate repeated verbatim every quarter) and the filer's
-- posted_by_name across filings (self-titling escalation is a strong tell).
-- Do not report a row as a "crank" from the numeric ranking alone.
--
-- Run against db/gain.db. Requires: derived_registrant_income_integrity.

SELECT
  registrant_name,
  income_amt,
  n_filings_same_amt,
  n_clients,
  n_lobbyists,
  n_activities,
  income_per_activity,
  flag_reason
FROM derived_registrant_income_integrity
ORDER BY income_per_activity DESC;
