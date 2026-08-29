-- probe: who is filing to oppose H.R.2208/S.4196 (Ysleta del Sur Pueblo & Alabama-Coushatta
-- Tribes of Texas Equal and Fair Opportunity Act) / H.R.2873/S.1536 (Tribal Gaming
-- Regulatory Compliance Act, the renumbered successor bill)
WITH tagged AS (
  SELECT DISTINCT c.name AS client, r.name AS registrant,
    CASE WHEN a.description LIKE '%Oppos%' OR a.description LIKE '%oppos%' THEN 'OPPOSE'
         WHEN a.description LIKE '%Advocacy%' OR a.description LIKE '%Support%' OR a.description LIKE '%support%' OR a.description LIKE '%encourage sponsors%' THEN 'SUPPORT'
         ELSE 'unclear' END AS stance
  FROM senate_filings f
  JOIN senate_clients c ON c.id=f.client_id
  JOIN senate_registrants r ON r.id=f.registrant_id
  JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
  WHERE a.description LIKE '%2208%' OR a.description LIKE '%4196%' OR a.description LIKE '%Ysleta%' OR a.description LIKE '%Alabama-Coushatta%'
     OR a.description LIKE '%2873%' OR a.description LIKE '%1536%' OR a.description LIKE '%Tribal Gaming Regulatory Compliance%'
)
SELECT client, registrant, stance, count(*) FROM tagged GROUP BY client, registrant, stance ORDER BY stance, client;

-- Sunland Park Racetrack & Casino full activity history on this bill
SELECT f.filing_year, f.filing_period_display, a.description
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
WHERE c.name = 'SUNLAND PARK RACETRACK & CASINO'
ORDER BY f.filing_year, f.filing_period_display;
