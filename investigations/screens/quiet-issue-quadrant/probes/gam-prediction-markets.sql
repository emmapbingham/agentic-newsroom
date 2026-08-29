-- probe: CFTC/prediction-market GAM activity is 2025-2026 only, zero before
SELECT f.filing_year, count(*) AS n_acts
FROM senate_filings f
JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
WHERE a.general_issue_code = 'GAM'
  AND (a.description LIKE '%prediction market%' OR a.description LIKE '%CFTC%' OR a.description LIKE '%event contract%')
GROUP BY f.filing_year ORDER BY f.filing_year;
