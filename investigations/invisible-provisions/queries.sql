-- queries.sql: invisible-provisions
-- All cited queries. Run against db/gain.db (read-only).
-- Labels match evidence.md blocks.

-- E1: TEC lobby-to-press ratio vs corpus (quiet-issue-quadrant screen)
-- Requires: derived_issue_quarter_volume_press
WITH
baseline AS (
  SELECT issue_code, issue_name,
    SUM(total_activities)         AS acts_2224,
    SUM(total_income_apportioned) AS income_2224,
    SUM(n_press_releases)         AS press_2224
  FROM derived_issue_quarter_volume_press
  WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code, issue_name
),
with_ratio AS (
  SELECT *,
    CAST(acts_2224 AS REAL)   / press_2224 AS act_per_press,
    CAST(income_2224 AS REAL) / press_2224 AS inc_per_press
  FROM baseline WHERE press_2224 >= 100
),
stats AS (
  SELECT
    AVG(act_per_press) AS mean_atp,
    AVG(inc_per_press) AS mean_ipp,
    SQRT(AVG(act_per_press*act_per_press) - AVG(act_per_press)*AVG(act_per_press)) AS sd_atp,
    SQRT(AVG(inc_per_press*inc_per_press) - AVG(inc_per_press)*AVG(inc_per_press)) AS sd_ipp
  FROM with_ratio
)
SELECT
  r.issue_code, r.issue_name,
  ROUND(r.acts_2224)          AS acts,
  ROUND(r.press_2224)         AS press,
  ROUND(r.act_per_press, 2)   AS act_per_press,
  ROUND(r.inc_per_press/1e6, 3) AS inc_per_press_M,
  ROUND((r.act_per_press - s.mean_atp) / s.sd_atp, 2) AS z_act,
  ROUND((r.inc_per_press - s.mean_ipp) / s.sd_ipp, 2) AS z_inc
FROM with_ratio r, stats s
ORDER BY z_act DESC;

-- E2: Spectrum lobbying flatness 2022-2026
SELECT sf.filing_year, sf.filing_period,
  count(*) as acts,
  count(distinct sf.registrant_id) as registrants
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
WHERE sla.general_issue_code = 'TEC'
  AND sf.filing_year BETWEEN 2022 AND 2026
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
  AND lower(sla.description) LIKE '%spectrum%'
GROUP BY sf.filing_year, sf.filing_period
ORDER BY sf.filing_year,
  CASE sf.filing_period
    WHEN 'first_quarter' THEN 1 WHEN 'second_quarter' THEN 2
    WHEN 'third_quarter' THEN 3 WHEN 'fourth_quarter' THEN 4
  END;

-- E3: TEC government entity targets
SELECT ge.name, count(*) as n
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_activity_government_entities sage ON sage.activity_id = sla.activity_id
JOIN ref_government_entities ge ON ge.id = sage.government_entity_id
WHERE sla.general_issue_code = 'TEC'
  AND sf.filing_year BETWEEN 2022 AND 2024
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
GROUP BY ge.name ORDER BY n DESC LIMIT 20;

-- E4: ACP press by party
SELECT m.last_party, m.last_type,
  count(DISTINCT pr.bioguide_id) as members_mentioning,
  count(*) as n_releases
FROM press_releases pr
JOIN members m ON m.bioguide = pr.bioguide_id
WHERE pr.year BETWEEN 2022 AND 2024
  AND (lower(pr.text) LIKE '%affordable connectivity%'
    OR lower(pr.text) LIKE '%acp funding%'
    OR lower(pr.text) LIKE '%broadband subsid%')
GROUP BY m.last_party, m.last_type
ORDER BY n_releases DESC;

-- E5: Spectrum-lobbyist FECA by party (confidence >= 0.6; contribution_type = 'feca')
WITH spectrum_registrants AS (
  SELECT DISTINCT sf.registrant_id
  FROM senate_lobbying_activities sla
  JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
  WHERE sla.general_issue_code = 'TEC'
    AND sf.filing_year BETWEEN 2022 AND 2024
    AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
    AND lower(sla.description) LIKE '%spectrum%'
),
spectrum_money AS (
  SELECT hmm.bioguide, sum(sci.amount_num) as spectrum_feca
  FROM senate_contribution_items sci
  JOIN senate_contribution_filings scf ON scf.filing_uuid = sci.filing_uuid
  JOIN spectrum_registrants sr ON sr.registrant_id = scf.registrant_id
  JOIN honoree_member_map hmm ON hmm.honoree_name = sci.honoree_name
  WHERE sci.contribution_type = 'feca' AND hmm.confidence >= 0.6
  GROUP BY hmm.bioguide
)
SELECT m.last_party,
  count(*) as senators,
  round(avg(sm.spectrum_feca)/1000, 1) as avg_spectrum_k,
  round(sum(sm.spectrum_feca)/1e6, 2) as total_spectrum_M
FROM members m
JOIN spectrum_money sm ON sm.bioguide = m.bioguide
WHERE m.last_type = 'sen'
GROUP BY m.last_party;

-- E15: Corpus-wide ranking re-run against expanded ISSUE_KEYWORDS map (75 of 79
-- codes, up from 21-22). Same structure as E1/E6 but run after
-- scripts/build_derived_issue_quarter_volume_press.py was rebuilt 2026-06-30.
-- Surfaced GAM (Gaming/Gambling/Casino) as new dominant outlier: 17.0x, z=5.08.
WITH
baseline AS (
  SELECT issue_code, issue_name,
    SUM(total_activities) AS acts_2224,
    SUM(n_press_releases) AS press_2224
  FROM derived_issue_quarter_volume_press
  WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code, issue_name
),
with_ratio AS (
  SELECT *, CAST(acts_2224 AS REAL) / press_2224 AS act_per_press
  FROM baseline WHERE press_2224 >= 100
),
stats AS (
  SELECT AVG(act_per_press) AS mean_atp,
    SQRT(AVG(act_per_press*act_per_press) - AVG(act_per_press)*AVG(act_per_press)) AS sd_atp
  FROM with_ratio
)
SELECT r.issue_code, r.issue_name,
  ROUND(r.acts_2224) AS acts, ROUND(r.press_2224) AS press,
  ROUND(r.act_per_press, 2) AS ratio,
  ROUND((r.act_per_press - s.mean_atp) / s.sd_atp, 2) AS z
FROM with_ratio r, stats s
ORDER BY z DESC LIMIT 15;

-- E15: GAM yearly scout trend (UNVERIFIED, not yet drilled to a sub-provision)
SELECT year, ROUND(SUM(total_activities)) as acts, ROUND(SUM(n_press_releases)) as press
FROM derived_issue_quarter_volume_press
WHERE issue_code = 'GAM' AND year BETWEEN 2022 AND 2025
GROUP BY year ORDER BY year;

-- E15 (added 2026-07-15): per-member press-release baseline, for findings.md
-- write-up. Answers "is 31-60/year actually low?" independent of the
-- lobby-to-press ratio/z-score comparison (which we deliberately did not
-- cite in the findings.md entry). Denominator = members with >=1 release
-- that year (a generous baseline; excludes silent members rather than
-- diluting with them).
SELECT strftime('%Y', date) AS yr,
  count(*) AS total_releases,
  count(DISTINCT bioguide_id) AS active_members,
  ROUND(CAST(count(*) AS REAL) / count(DISTINCT bioguide_id), 1) AS avg_per_active_member
FROM press_releases
WHERE date >= '2022-01-01' AND date < '2025-01-01'
GROUP BY yr;
-- Result: 2022: 19,702 releases / 267 members / 73.8 avg
--         2023: 30,249 releases / 341 members / 88.7 avg
--         2024: 31,583 releases / 371 members / 85.1 avg
