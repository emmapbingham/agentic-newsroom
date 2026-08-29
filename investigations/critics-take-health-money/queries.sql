-- queries.sql — critics-take-health-money
-- All queries run against db/gain.db (read-only).

-- q1: scout — vocal pharma critics x health-sector FECA (from lead probe_sql; unverified)
WITH critics AS (
  SELECT pr.bioguide_id, count(*) as n_critical
  FROM press_releases pr
  WHERE pr.year BETWEEN 2022 AND 2025
    AND (
      lower(pr.text) LIKE '%drug price%'
      OR lower(pr.text) LIKE '%big pharma%'
      OR lower(pr.text) LIKE '%insulin price%'
      OR lower(pr.text) LIKE '%price gouging%'
      OR lower(pr.text) LIKE '%lower drug%'
    )
  GROUP BY pr.bioguide_id
  HAVING n_critical >= 10
),
money AS (
  SELECT bioguide, SUM(feca_total) as f
  FROM derived_member_issue_money_panel
  WHERE issue_code IN ('HCR','PHA','MMM')
    AND year BETWEEN 2022 AND 2024
  GROUP BY bioguide
)
SELECT m.official_full, m.last_party, m.last_state,
       c.n_critical,
       round(mo.f/1e3, 1) as health_feca_k
FROM critics c
JOIN money mo ON mo.bioguide = c.bioguide_id
JOIN members m ON m.bioguide = c.bioguide_id
ORDER BY mo.f DESC
LIMIT 20;

-- q3: Pallone confirmed critical release count (25 releases, 2022-2025)
SELECT count(*) FROM press_releases pr
WHERE pr.bioguide_id = 'P000034'
  AND pr.year BETWEEN 2022 AND 2025
  AND (lower(pr.text) LIKE '%drug price%' OR lower(pr.text) LIKE '%big pharma%'
    OR lower(pr.text) LIKE '%insulin price%' OR lower(pr.text) LIKE '%price gouging%'
    OR lower(pr.text) LIKE '%lower drug%');

-- q4: Pallone confirmed deduped FECA from health registrants (2022-2024)
WITH health_registrants AS (
  SELECT DISTINCT sf.registrant_id
  FROM senate_filings sf JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
  WHERE sla.general_issue_code IN ('HCR','PHA','MMM')
    AND sf.filing_type IN ('Q1','Q2','Q3','Q4') AND sf.filing_year BETWEEN 2022 AND 2024
)
SELECT round(SUM(sci.amount_num)/1e3,1) as feca_k, COUNT(DISTINCT scf.registrant_id) as n_reg
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid=sci.filing_uuid
JOIN honoree_member_map hmm ON hmm.honoree_name=sci.honoree_name
WHERE hmm.bioguide='P000034' AND hmm.confidence>=0.9 AND sci.contribution_type='feca'
  AND sci.amount_num>0 AND scf.filing_year BETWEEN 2022 AND 2024
  AND scf.registrant_id IN (SELECT registrant_id FROM health_registrants);

-- q5: Pallone top donors with lobby issue codes (named donors)
WITH health_registrants AS (
  SELECT DISTINCT sf.registrant_id, GROUP_CONCAT(DISTINCT sla.general_issue_code) as issue_codes
  FROM senate_filings sf JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
  WHERE sla.general_issue_code IN ('HCR','PHA','MMM')
    AND sf.filing_type IN ('Q1','Q2','Q3','Q4') AND sf.filing_year BETWEEN 2022 AND 2024
  GROUP BY sf.registrant_id
)
SELECT sr.name, hr.issue_codes, round(SUM(sci.amount_num)/1e3,1) as feca_k,
       scf.filing_year, scf.filing_uuid
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid=sci.filing_uuid
JOIN senate_registrants sr ON sr.id=scf.registrant_id
JOIN honoree_member_map hmm ON hmm.honoree_name=sci.honoree_name
JOIN health_registrants hr ON hr.registrant_id=scf.registrant_id
WHERE hmm.bioguide='P000034' AND hmm.confidence>=0.9 AND sci.contribution_type='feca'
  AND sci.amount_num>0 AND scf.filing_year BETWEEN 2022 AND 2024
GROUP BY sr.name, scf.filing_year
ORDER BY feca_k DESC LIMIT 20;

-- q6: Pallone names PhRMA and Merck in critical releases — do they give to him?
SELECT sr.name, round(SUM(sci.amount_num)/1e3,1) as feca_k, scf.filing_year, scf.filing_uuid
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid=sci.filing_uuid
JOIN senate_registrants sr ON sr.id=scf.registrant_id
JOIN honoree_member_map hmm ON hmm.honoree_name=sci.honoree_name
WHERE hmm.bioguide='P000034' AND hmm.confidence>=0.9 AND sci.contribution_type='feca'
  AND sci.amount_num>0 AND scf.filing_year BETWEEN 2022 AND 2024
  AND (upper(sr.name) LIKE '%MERCK%' OR upper(sr.name) LIKE '%PHRMA%')
GROUP BY sr.name, scf.filing_year;

-- q7: Carter confirmed critical release count (31 with PBM keywords, 2022-2025)
SELECT count(*) FROM press_releases pr
WHERE pr.bioguide_id='C001103' AND pr.year BETWEEN 2022 AND 2025
  AND (lower(pr.text) LIKE '%drug price%' OR lower(pr.text) LIKE '%big pharma%'
    OR lower(pr.text) LIKE '%insulin price%' OR lower(pr.text) LIKE '%price gouging%'
    OR lower(pr.text) LIKE '%lower drug%' OR lower(pr.text) LIKE '%pbm%');

-- q8: Carter confirmed deduped FECA from health registrants (2022-2024)
WITH health_registrants AS (
  SELECT DISTINCT sf.registrant_id
  FROM senate_filings sf JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
  WHERE sla.general_issue_code IN ('HCR','PHA','MMM')
    AND sf.filing_type IN ('Q1','Q2','Q3','Q4') AND sf.filing_year BETWEEN 2022 AND 2024
)
SELECT round(SUM(sci.amount_num)/1e3,1) as feca_k, COUNT(DISTINCT scf.registrant_id) as n_reg
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid=sci.filing_uuid
JOIN honoree_member_map hmm ON hmm.honoree_name=sci.honoree_name
WHERE hmm.bioguide='C001103' AND hmm.confidence>=0.9 AND sci.contribution_type='feca'
  AND sci.amount_num>0 AND scf.filing_year BETWEEN 2022 AND 2024
  AND scf.registrant_id IN (SELECT registrant_id FROM health_registrants);

-- q9: Carter donors — McKesson and Cardinal Health (PBM/distributor sector)
SELECT sr.name, round(SUM(sci.amount_num)/1e3,1) as feca_k, scf.filing_year, scf.filing_uuid
FROM senate_contribution_items sci
JOIN senate_contribution_filings scf ON scf.filing_uuid=sci.filing_uuid
JOIN senate_registrants sr ON sr.id=scf.registrant_id
JOIN honoree_member_map hmm ON hmm.honoree_name=sci.honoree_name
WHERE hmm.bioguide='C001103' AND hmm.confidence>=0.9 AND sci.contribution_type='feca'
  AND sci.amount_num>0 AND scf.filing_year BETWEEN 2022 AND 2024
  AND (upper(sr.name) LIKE '%MCKESSON%' OR upper(sr.name) LIKE '%CARDINAL HEALTH%'
       OR upper(sr.name) LIKE '%CENCORA%' OR upper(sr.name) LIKE '%EXPRESS SCRIPTS%')
GROUP BY sr.name, scf.filing_year;

-- q10: McKesson lobbying issues (confirms PHA, MMM, HCR registrant)
SELECT sla.general_issue_code, count(*) as n
FROM senate_filings sf JOIN senate_registrants sr ON sr.id=sf.registrant_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE upper(sr.name) LIKE '%MCKESSON%' AND sf.filing_year BETWEEN 2022 AND 2024
GROUP BY sla.general_issue_code ORDER BY n DESC LIMIT 5;

-- q2: deduped FECA — one registrant counted once per member regardless of issue codes
-- (avoids triple-counting registrants active in HCR+PHA+MMM)
WITH critics AS (
  SELECT pr.bioguide_id, count(*) as n_critical
  FROM press_releases pr
  WHERE pr.year BETWEEN 2022 AND 2025
    AND (
      lower(pr.text) LIKE '%drug price%'
      OR lower(pr.text) LIKE '%big pharma%'
      OR lower(pr.text) LIKE '%insulin price%'
      OR lower(pr.text) LIKE '%price gouging%'
      OR lower(pr.text) LIKE '%lower drug%'
    )
  GROUP BY pr.bioguide_id
  HAVING n_critical >= 10
),
health_registrants AS (
  -- registrants that lobbied on any of HCR, PHA, MMM in any Q filing 2022-2024
  SELECT DISTINCT sf.registrant_id
  FROM senate_filings sf
  JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
  WHERE sla.general_issue_code IN ('HCR','PHA','MMM')
    AND sf.filing_type IN ('Q1','Q2','Q3','Q4')
    AND sf.filing_year BETWEEN 2022 AND 2024
),
deduped_feca AS (
  -- one row per (registrant, member, year) — no issue-code fan-out
  SELECT hmm.bioguide,
         scf.filing_year,
         scf.registrant_id,
         SUM(sci.amount_num) as reg_feca
  FROM senate_contribution_items sci
  JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
  JOIN honoree_member_map hmm ON hmm.honoree_name = sci.honoree_name
  WHERE hmm.confidence >= 0.9
    AND sci.contribution_type = 'feca'
    AND sci.amount_num > 0
    AND scf.filing_year BETWEEN 2022 AND 2024
    AND scf.registrant_id IN (SELECT registrant_id FROM health_registrants)
  GROUP BY hmm.bioguide, scf.filing_year, scf.registrant_id
),
member_totals AS (
  SELECT bioguide,
         SUM(reg_feca) as total_feca,
         COUNT(DISTINCT registrant_id) as n_registrants
  FROM deduped_feca
  GROUP BY bioguide
)
SELECT m.official_full, m.last_party, m.last_state,
       c.n_critical,
       round(mt.total_feca/1e3, 1) as health_feca_k,
       mt.n_registrants
FROM critics c
JOIN member_totals mt ON mt.bioguide = c.bioguide_id
JOIN members m ON m.bioguide = c.bioguide_id
ORDER BY mt.total_feca DESC
LIMIT 20;
