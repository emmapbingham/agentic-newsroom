-- probe: local-government Senate clients (city/county/township/municipal), what they
-- actually lobby on. Base rate for evaluating whether a local government showing up on
-- any given issue code is surprising or routine.
WITH localgov AS (
  SELECT id, name FROM senate_clients
  WHERE name LIKE '%TOWNSHIP%' OR name LIKE '%CITY OF %' OR name LIKE '%COUNTY OF%' OR name LIKE '%TOWN OF%'
     OR name LIKE '% COUNTY' OR name LIKE '%MUNICIPAL%' OR name LIKE '%VILLAGE OF%'
)
SELECT a.general_issue_code, count(*) AS n_acts
FROM senate_filings f
JOIN localgov lg ON lg.id = f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
GROUP BY a.general_issue_code ORDER BY n_acts DESC;

-- count of distinct local-gov clients vs. total Senate clients (base rate)
SELECT
  (SELECT count(DISTINCT name) FROM senate_clients
   WHERE name LIKE '%TOWNSHIP%' OR name LIKE '%CITY OF %' OR name LIKE '%COUNTY OF%' OR name LIKE '%TOWN OF%'
      OR name LIKE '% COUNTY' OR name LIKE '%MUNICIPAL%' OR name LIKE '%VILLAGE OF%') AS n_localgov,
  (SELECT count(DISTINCT id) FROM senate_clients) AS n_total_clients;
