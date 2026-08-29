-- probe: local governments (cities/counties) lobbying on Indian/Native American Affairs
-- (IND), specifically fee-to-trust / tribal land-transfer issues -- connects to the
-- fee-to-trust mechanism from sunland-park-ysleta-opposition, but from the county's
-- side (tax base / land-use jurisdiction) rather than a rival casino's.
WITH localgov AS (
  SELECT id, name FROM senate_clients
  WHERE name LIKE '%TOWNSHIP%' OR name LIKE '%CITY OF %' OR name LIKE '%COUNTY OF%' OR name LIKE '%TOWN OF%'
     OR name LIKE '% COUNTY' OR name LIKE '%MUNICIPAL%' OR name LIKE '%VILLAGE OF%'
)
SELECT lg.name, count(*) AS n_acts, MIN(f.filing_year) AS first_yr, MAX(f.filing_year) AS last_yr
FROM senate_filings f
JOIN localgov lg ON lg.id = f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
WHERE a.general_issue_code = 'IND'
GROUP BY lg.name ORDER BY n_acts DESC;

SELECT DISTINCT lg.name, a.description
FROM senate_filings f
JOIN localgov lg ON lg.id = f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
WHERE a.general_issue_code = 'IND'
ORDER BY lg.name;
