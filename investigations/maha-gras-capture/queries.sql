-- queries.sql — maha-gras-capture
-- All queries read db/gain.db (read-only). Re-run to verify any cited number.

-- q1: FOO quarterly time series with z-score vs 2022-2024 baseline
WITH baseline AS (
  SELECT
    issue_code,
    AVG(total_activities) AS mean_acts,
    SQRT(AVG(total_activities*total_activities) - AVG(total_activities)*AVG(total_activities)) AS sd_acts,
    AVG(total_income_apportioned) AS mean_income
  FROM derived_issue_quarter_volume_press
  WHERE issue_code='FOO' AND year BETWEEN 2022 AND 2024
  GROUP BY issue_code
)
SELECT
  d.year, d.quarter, d.total_activities,
  ROUND(d.total_income_apportioned/1e6, 2) AS income_m,
  ROUND((d.total_activities - b.mean_acts) / b.sd_acts, 2) AS z_acts
FROM derived_issue_quarter_volume_press d
JOIN baseline b ON b.issue_code = d.issue_code
WHERE d.issue_code='FOO'
ORDER BY d.year, d.quarter;

-- q2: Filing UUIDs where food industry clients name GRAS reform or S. 3122 in 2025
SELECT
  sf.filing_uuid,
  r.name AS registrant,
  c.name AS client,
  sla.description
FROM senate_filings sf
JOIN senate_registrants r ON r.id=sf.registrant_id
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sla.general_issue_code='FOO'
  AND sf.filing_year=2025
  AND (lower(sla.description) LIKE '%gras%'
    OR lower(sla.description) LIKE '%generally recognized as safe%'
    OR lower(sla.description) LIKE '%s. 3122%'
    OR lower(sla.description) LIKE '%better fda act%'
    OR lower(sla.description) LIKE '%better food disclosure%')
ORDER BY c.name, sf.filing_uuid;

-- q2b: dedup client list + filing count for GRAS/S.3122 mentions in 2025 FOO
SELECT c.name AS client, COUNT(DISTINCT sf.filing_uuid) AS n_filings
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sla.general_issue_code='FOO'
  AND sf.filing_year=2025
  AND (lower(sla.description) LIKE '%gras%'
    OR lower(sla.description) LIKE '%generally recognized as safe%'
    OR lower(sla.description) LIKE '%s. 3122%'
    OR lower(sla.description) LIKE '%s.3122%'
    OR lower(sla.description) LIKE '%better fda act%'
    OR lower(sla.description) LIKE '%better food disclosure%')
GROUP BY c.name
ORDER BY n_filings DESC;

-- q2c: which clients name S.3122 explicitly (bill number/title, not just generic GRAS)?
SELECT DISTINCT c.name, sf.filing_uuid
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sf.filing_year=2025
  AND (lower(sla.description) LIKE '%s.3122%' OR lower(sla.description) LIKE '%s. 3122%'
    OR lower(sla.description) LIKE '%better fda act%' OR lower(sla.description) LIKE '%better food disclosure%')
GROUP BY c.name;

-- q2d: any non-reform-group client naming current S.2341 (careful: distinct from
-- 2023's same-titled predecessor S.3387, 118th Congress -- check description text)
SELECT c.name, sla.description
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sf.filing_year=2025
  AND (lower(sla.description) LIKE '%s.2341%' OR lower(sla.description) LIKE '%s. 2341%' OR lower(sla.description) LIKE '%toxic-free foods%')
GROUP BY c.name;

-- q3: Press release texts for competing GRAS bills (see evidence.md E3)
SELECT title, date, url, text
FROM press_releases
WHERE url IN (
  'https://www.booker.senate.gov/news/press/booker-markey-introduce-legislation-to-get-dangerous-chemicals-out-of-food',
  'https://www.britt.senate.gov/news/press-releases/u-s-senators-katie-britt-roger-marshall-rick-scott-introduce-bill-to-ensure-safer-food-for-american-families/'
);

-- q4: Hyde-Smith MAHA/industry press release
SELECT title, date, url, text
FROM press_releases
WHERE url='https://www.hydesmith.senate.gov/food-and-ag-groups-seek-more-input-maha-activities';

-- q5: MAHA press release counts by keyword and party
-- SUPERSEDED 2026-07-15 -- see q5b. Bare '%maha%'/'%gras%' substring matching
-- collides with common words (Omaha, Mahalo, Taj Mahal, Mahan -> maha;
-- Grassley, grassroots, grasp, grasslands, Ingrassia, Mardi Gras -> gras),
-- inflating both counts. Kept for the record, not for citing numbers from.
SELECT
  m.last_party,
  SUM(CASE WHEN lower(pr.text) LIKE '%maha%' OR lower(pr.text) LIKE '%make america healthy%' THEN 1 ELSE 0 END) AS maha,
  SUM(CASE WHEN lower(pr.text) LIKE '%seed oil%' THEN 1 ELSE 0 END) AS seed_oil,
  SUM(CASE WHEN lower(pr.text) LIKE '%dietary guideline%' THEN 1 ELSE 0 END) AS dietary_guidelines,
  SUM(CASE WHEN lower(pr.text) LIKE '%generally recognized as safe%' OR lower(pr.text) LIKE '%gras%' THEN 1 ELSE 0 END) AS gras
FROM press_releases pr
JOIN members m ON m.bioguide=pr.bioguide_id
WHERE pr.year=2025
GROUP BY m.last_party;

-- q5b: CORRECTED (2026-07-15) -- word-boundary-safe MAHA count via press_fts,
-- title-anchored to avoid collision with body-text false positives
SELECT count(*) AS maha_releases_2025, count(DISTINCT p.bioguide_id) AS maha_members
FROM press_releases p
WHERE p.year=2025 AND (p.title LIKE '%MAHA%' OR p.text LIKE '%Make America Healthy Again%');

-- q5c: CORRECTED (2026-07-15) -- GRAS/food-chemical-reform-specific releases,
-- FTS5 (tokenized, so no substring collision) + broadened phrase set, with
-- manually-verified exclusions for a same-acronym-space but unrelated fight
-- (livestock feed additive approval, FDA-regulated but not human-food GRAS
-- reform) and adjacent-but-distinct MAHA topics (food dye bans, beauty
-- product chemical bans) that matched the phrase set but aren't this fight.
SELECT p.bioguide_id, p.date, p.title, p.party, p.url
FROM press_fts
JOIN press_releases p ON p.release_id = press_fts.release_id
WHERE press_fts MATCH '"food chemical" OR "food additive" OR "food additives" OR "self-affirm" OR "generally recognized as safe" OR "ingredient transparency" OR "food ingredient loophole"'
  AND p.year=2025
  AND p.url NOT IN (
    'https://langworthy.house.gov/media/press-releases/congressman-langworthy-introduces-bill-support-american-farmers-national',
    'https://schrier.house.gov/media/press-releases/congresswoman-schrier-introduces-bill-streamline-regulation-support-farmers',
    'https://www.king.senate.gov/newsroom/press-releases/king-colleagues-introduce-bipartisan-bill-to-cut-red-tape-in-the-livestock-feed-sector',
    'https://fletcher.house.gov/news/documentsingle.aspx?DocumentID=6964',
    'https://schakowsky.house.gov/media/press-releases/schakowsky-fletcher-matsui-pressley-introduce-safer-beauty-bill-package',
    'https://meng.house.gov/media-center/press-releases/meng-introduces-legislation-banning-harmful-food-dyes',
    'https://lawler.house.gov/news/documentsingle.aspx?DocumentID=5165',
    'https://delauro.house.gov/media-center/press-releases/delauro-pallone-urge-biden-administration-ban-carcinogenic-red-food-dye',
    'https://delauro.house.gov/media-center/press-releases/delauro-applauds-red-3-ban',
    'https://roy.house.gov/media/press-releases/rep-chip-roy-charts-bold-new-path-make-america-healthy-again-landmark-report',
    'https://www.scott.senate.gov/media-center/press-releases/sen-scott-questions-hhs-secretary-kennedy-at-help-committee-hearing/'
  )
ORDER BY p.date;

-- q5d: CORRECTED (2026-07-15) -- whole milk comparison, same word-boundary-safe approach
SELECT count(*) AS milk_releases_2025, count(DISTINCT bioguide_id) AS milk_members
FROM press_releases
WHERE year=2025 AND (title LIKE '%whole milk%' OR text LIKE '%Whole Milk for Healthy Kids%');

-- q6 (pending): Contribution flow to Britt/Marshall vs Booker/Markey
-- honoree_member_map crosswalk → senate_contribution_items
-- to be written when say-vs-pay drilldown runs

-- q8: curated advocacy-org census across issue codes (generalization of the GRAS pattern)
-- NOT a name-pattern heuristic -- tried that, it fails (catches industry coalitions
-- with advocacy-sounding names). This is a manually verified list of 16 known
-- public-interest/consumer/environmental registrants confirmed present in the corpus.
CREATE TEMP TABLE advocacy_orgs(name TEXT);
INSERT INTO advocacy_orgs VALUES
  ('AMERICAN CIVIL LIBERTIES UNION'),('AMERICAN PUBLIC HEALTH ASSOCIATION'),
  ('CENTER FOR RESPONSIBLE LENDING'),('CENTER FOR SCIENCE IN THE PUBLIC INTEREST'),
  ('COMMON CAUSE'),('CONSUMER FEDERATION OF AMERICA'),('CONSUMER REPORTS'),
  ('EARTHJUSTICE'),('ENVIRONMENTAL DEFENSE ACTION FUND'),('ENVIRONMENTAL DEFENSE FUND'),
  ('ENVIRONMENTAL WORKING GROUP'),('NATURAL RESOURCES DEFENSE COUNCIL'),
  ('PUBLIC CITIZEN'),('SIERRA CLUB'),('THE GOOD FOOD INSTITUTE'),('UNION OF CONCERNED SCIENTISTS');

SELECT sla.general_issue_code, ric.name,
  COUNT(DISTINCT sf.client_id) n_clients_total,
  COUNT(DISTINCT CASE WHEN c.name IN (SELECT name FROM advocacy_orgs) THEN sf.client_id END) n_advocacy
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
JOIN ref_issue_codes ric ON ric.value=sla.general_issue_code
WHERE sf.filing_year=2025
GROUP BY sla.general_issue_code
HAVING n_clients_total >= 200
ORDER BY n_advocacy ASC, n_clients_total DESC;

-- q7: all distinct clients citing GRAS in FOO filings, all years -- industry vs advocacy census
SELECT DISTINCT c.name
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sla.general_issue_code='FOO'
  AND (lower(sla.description) LIKE '%gras%' OR lower(sla.description) LIKE '%generally recognized as safe%')
ORDER BY c.name;

-- q7b: quarterly escalation -- distinct clients + filings citing GRAS, 2025 Q1 - 2026 Q1
SELECT sf.filing_year, sf.filing_period, COUNT(DISTINCT c.id) n_clients, COUNT(DISTINCT sf.filing_uuid) n_filings
FROM senate_filings sf
JOIN senate_clients c ON c.id=sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
WHERE sla.general_issue_code='FOO'
  AND (sf.filing_year=2025 OR (sf.filing_year=2026 AND sf.filing_period='first_quarter'))
  AND (lower(sla.description) LIKE '%gras%' OR lower(sla.description) LIKE '%generally recognized as safe%')
GROUP BY sf.filing_year, sf.filing_period
ORDER BY sf.filing_year,
  CASE sf.filing_period WHEN 'first_quarter' THEN 1 WHEN 'second_quarter' THEN 2 WHEN 'third_quarter' THEN 3 WHEN 'fourth_quarter' THEN 4 END;

-- q7c: spend comparison, advocacy (CSPI/ANH/GFI) vs industry, GRAS-citing filings
-- CAVEAT: spend is filing-level total (all issues that registrant/client filing covers), NOT issue-specific.
-- See evidence.md E7 -- ADM's filings cover ~10 issue codes each; CSPI's cover 1.
WITH gras_filings AS (
  SELECT DISTINCT sf.filing_uuid, c.name AS client, COALESCE(sf.income_amt, sf.expenses_amt) AS spend
  FROM senate_filings sf
  JOIN senate_clients c ON c.id=sf.client_id
  JOIN senate_lobbying_activities sla ON sla.filing_uuid=sf.filing_uuid
  WHERE sla.general_issue_code='FOO'
    AND (lower(sla.description) LIKE '%gras%' OR lower(sla.description) LIKE '%generally recognized as safe%')
)
SELECT
  CASE WHEN client IN ('CENTER FOR SCIENCE IN THE PUBLIC INTEREST','ALLIANCE FOR NATURAL HEALTH USA','THE GOOD FOOD INSTITUTE')
    THEN 'advocacy' ELSE 'industry' END AS side,
  COUNT(DISTINCT client) n_clients, COUNT(*) n_filings, ROUND(SUM(spend)/1e6,3) total_spend_m
FROM gras_filings GROUP BY side;

-- q6: say-vs-pay -- food-industry PAC contributions to key bill sponsors
-- (high-confidence honoree matches only)
SELECT m.last, m.last_party, sci.contributor_name, ROUND(SUM(sci.amount_num),0) AS amt, COUNT(*) n
FROM senate_contribution_items sci
JOIN honoree_member_map hmm ON hmm.honoree_name = sci.honoree_name
JOIN members m ON m.bioguide = hmm.bioguide
WHERE hmm.bioguide IN ('B001288','B001319','M001198','S001217','C001039','M000133')
  AND hmm.confidence >= 0.9
  AND (
    lower(sci.contributor_name) LIKE '%pepsi%' OR lower(sci.contributor_name) LIKE '%coca%' OR
    lower(sci.contributor_name) LIKE '%kraft%' OR lower(sci.contributor_name) LIKE '%general mills%' OR
    lower(sci.contributor_name) LIKE '%nestle%' OR lower(sci.contributor_name) LIKE '%conagra%' OR
    lower(sci.contributor_name) LIKE '%cargill%' OR lower(sci.contributor_name) LIKE '%adm%' OR
    lower(sci.contributor_name) LIKE '%archer daniels%' OR lower(sci.contributor_name) LIKE '%bunge%' OR
    lower(sci.contributor_name) LIKE '%consumer brands%' OR lower(sci.contributor_name) LIKE '%grocery manufacturers%' OR
    lower(sci.contributor_name) LIKE '%american beverage%' OR lower(sci.contributor_name) LIKE '%dairy%' OR
    lower(sci.contributor_name) LIKE '%food%' OR lower(sci.contributor_name) LIKE '%mondelez%' OR
    lower(sci.contributor_name) LIKE '%bakers%'
  )
GROUP BY m.last, sci.contributor_name
ORDER BY m.last, amt DESC;

-- q1b: base-rate check — overall Senate lobbying activity volume by quarter
-- (confirms FOO surge is issue-specific, not just riding a global 2025 volume increase)
SELECT sf.filing_year, sf.filing_period, COUNT(*) AS total_all_activities
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
WHERE sf.filing_year BETWEEN 2022 AND 2026
GROUP BY sf.filing_year, sf.filing_period
ORDER BY 1,2;
