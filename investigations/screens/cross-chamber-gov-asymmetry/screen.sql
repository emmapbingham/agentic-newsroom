-- Screen: cross-chamber-gov-asymmetry  (contrast: data-vs-law / source-vs-source)
-- Baseline: a registrant lobbying the same way in both chambers should code the
--   catch-all "Government issues" (GOV) at a similar RATE in each. A large gap
--   means the firm uses specific issue codes in one chamber but the GOV sink in
--   the other for comparable work — selective vagueness that breaks the public's
--   issue-classification lens. Maps to lead gov-catch-all-miscoding.
-- Rates are over ACTIVITY rows (not summed dollars), so no multi-filing/dup
--   grain artifact (cf. the quarantined true-income-mismatch screen).
-- Restricted to registrants with >=50 activity rows in EACH chamber.
WITH s AS (
  SELECT f.registrant_id AS rid, count(*) AS tot,
         sum(a.general_issue_code = 'GOV') AS gov
  FROM senate_lobbying_activities a
  JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
  GROUP BY f.registrant_id
),
h AS (
  SELECT hf.senate_registrant_id AS rid, count(*) AS tot,
         sum(a.issue_area_code = 'GOV') AS gov
  FROM house_activities a
  JOIN house_filings hf ON hf.house_filing_id = a.house_filing_id
  WHERE hf.senate_registrant_id IS NOT NULL
  GROUP BY hf.senate_registrant_id
)
SELECT
  r.name AS registrant_name,
  s.rid  AS registrant_id,
  s.tot  AS senate_activities,
  h.tot  AS house_activities,
  round(100.0 * s.gov / s.tot, 1) AS senate_gov_pct,
  round(100.0 * h.gov / h.tot, 1) AS house_gov_pct,
  round(abs(100.0 * s.gov / s.tot - 100.0 * h.gov / h.tot), 1) AS score  -- pp gap
FROM s
JOIN h ON h.rid = s.rid
JOIN senate_registrants r ON r.id = s.rid
WHERE s.tot >= 50 AND h.tot >= 50
ORDER BY score DESC
LIMIT 50;
