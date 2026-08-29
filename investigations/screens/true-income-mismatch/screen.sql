-- Screen: true-income-mismatch  (contrast: source-vs-source)
-- Baseline: an engagement filed in BOTH chambers for the same quarter should
--   report the same income to each. Reads derived_cross_chamber_engagements.
-- Ranks 'both' engagement-quarters where Senate vs House income disagree by
--   >10% AND >$20k, by absolute dollar gap. The sweep claimed near-total
--   agreement (34/56,882 pairs >10%); this screen names the exceptions.
SELECT
  registrant_name,
  client_name,
  filing_year,
  quarter,
  senate_income_sum,
  house_income_sum,
  abs(senate_income_sum - house_income_sum) AS score,
  senate_filing_uuids,
  house_filing_ids
FROM derived_cross_chamber_engagements
WHERE presence = 'both'
  AND senate_income_sum > 0 AND house_income_sum > 0
  AND abs(senate_income_sum - house_income_sum) > 20000
  AND abs(senate_income_sum - house_income_sum)
      / max(senate_income_sum, house_income_sum) > 0.10
ORDER BY score DESC
LIMIT 50;
