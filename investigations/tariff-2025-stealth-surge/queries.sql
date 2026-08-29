-- Case: tariff-2025-stealth-surge
-- Every cited number reruns from these. Panels are derived_* tables rebuilt by
-- scripts/build_derived_registrant_{income,issue}.py (deduped, latest-posted).
-- Connect read-only: sqlite3 "file:db/gain.db?mode=ro"

-- q1: TAR lobbying by year — activities and distinct registrants (the surge)
SELECT filing_year, sum(n_activities) AS activities, count(*) AS registrants
FROM derived_registrant_issue_panel
WHERE issue_code = 'TAR'
GROUP BY filing_year ORDER BY filing_year;

-- q2: registrants whose FIRST TAR year is 2025 (the first-timer cohort)
SELECT count(*) FROM (
  SELECT registrant_id, min(filing_year) AS fy
  FROM derived_registrant_issue_panel
  WHERE issue_code = 'TAR' GROUP BY registrant_id) WHERE fy = 2025;

-- q3: issue new-entrant rush — TAR vs every other issue (singular-outlier test)
WITH first_year AS (
  SELECT registrant_id, issue_code, min(filing_year) AS fy
  FROM derived_registrant_issue_panel GROUP BY registrant_id, issue_code),
by_issue AS (
  SELECT issue_code,
         sum(fy=2022) e22, sum(fy=2023) e23, sum(fy=2024) e24, sum(fy=2025) e25
  FROM first_year GROUP BY issue_code)
SELECT issue_code, (e22+e23+e24)/3.0 AS baseline_avg, e25 AS entrants_2025,
       round(e25 - (e22+e23+e24)/3.0, 0) AS excess
FROM by_issue WHERE (e22+e23+e24)/3.0 >= 5
ORDER BY excess DESC LIMIT 10;

-- q4: income surge Q4-2024 -> Q1-2025 for the named firms (deduped panel)
SELECT registrant_name, filing_year, quarter, income_sum
FROM derived_registrant_income_panel
WHERE registrant_name LIKE 'BALLARD PARTNERS%'
   OR registrant_name LIKE 'MILLER STRATEGIES%'
   OR registrant_name LIKE 'CONTINENTAL STRATEGY%'
   AND ((filing_year=2024 AND quarter='Q4') OR (filing_year=2025 AND quarter='Q1'))
ORDER BY registrant_name, filing_year, quarter;

-- q5: top first-time-2025 TAR registrants by 2025 TAR activity, with a sample
--     filing_uuid (resolves at https://lda.gov/filings/public/filing/{uuid}/print/)
WITH fy AS (SELECT registrant_id, min(filing_year) f
            FROM derived_registrant_issue_panel WHERE issue_code='TAR' GROUP BY 1),
new25 AS (SELECT registrant_id FROM fy WHERE f=2025)
SELECT p.registrant_name, p.n_activities AS tar_acts_2025,
  (SELECT f.filing_uuid FROM senate_lobbying_activities a
   JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
   WHERE f.registrant_id=p.registrant_id AND a.general_issue_code='TAR'
     AND f.filing_year=2025 LIMIT 1) AS sample_uuid
FROM derived_registrant_issue_panel p JOIN new25 n ON n.registrant_id=p.registrant_id
WHERE p.issue_code='TAR' AND p.filing_year=2025
ORDER BY p.n_activities DESC LIMIT 15;

-- q6: incumbent scale-up — Ballard's TAR activity trajectory
SELECT filing_year, n_activities
FROM derived_registrant_issue_panel
WHERE issue_code='TAR'
  AND registrant_id=(SELECT id FROM senate_registrants WHERE name LIKE 'BALLARD PARTNERS%' LIMIT 1)
ORDER BY filing_year;

-- q7 (TODO, refutation check): TRD (Trade) trend alongside TAR — did tariff work
--     simply migrate from TRD to TAR? Run before publication.
SELECT issue_code, filing_year, sum(n_activities) acts, count(*) regs
FROM derived_registrant_issue_panel
WHERE issue_code IN ('TAR','TRD') GROUP BY 1,2 ORDER BY 1,2;

-- q8: top TAR clients of the GENUINELY-NEW entrants (first TAR 2025, no prior TRD)
WITH fy AS (SELECT registrant_id, min(filing_year) f FROM derived_registrant_issue_panel WHERE issue_code='TAR' GROUP BY 1),
new25 AS (SELECT registrant_id FROM fy WHERE f=2025),
genuine AS (SELECT registrant_id FROM new25 n WHERE NOT EXISTS
  (SELECT 1 FROM derived_registrant_issue_panel p WHERE p.registrant_id=n.registrant_id AND p.issue_code='TRD' AND p.filing_year<2025))
SELECT c.name, c.country, c.ppb_country, count(*) AS tar_acts
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
JOIN senate_clients c ON c.id=f.client_id
WHERE a.general_issue_code='TAR' AND f.filing_year=2025 AND f.registrant_id IN (SELECT registrant_id FROM genuine)
GROUP BY c.id ORDER BY tar_acts DESC LIMIT 18;

-- q9: what they're lobbying FOR — sampled TAR activity descriptions (same cohort)
WITH fy AS (SELECT registrant_id, min(filing_year) f FROM derived_registrant_issue_panel WHERE issue_code='TAR' GROUP BY 1),
new25 AS (SELECT registrant_id FROM fy WHERE f=2025),
genuine AS (SELECT registrant_id FROM new25 n WHERE NOT EXISTS
  (SELECT 1 FROM derived_registrant_issue_panel p WHERE p.registrant_id=n.registrant_id AND p.issue_code='TRD' AND p.filing_year<2025))
SELECT c.name, a.description, f.filing_uuid
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
JOIN senate_clients c ON c.id=f.client_id
WHERE a.general_issue_code='TAR' AND f.filing_year=2025 AND f.registrant_id IN (SELECT registrant_id FROM genuine)
  AND a.description IS NOT NULL AND length(a.description)>20
GROUP BY c.id ORDER BY length(a.description) DESC LIMIT 10;
