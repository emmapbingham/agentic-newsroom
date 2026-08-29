-- queries.sql — ways-means-chair-money-magnet
-- All queries read db/gain.db. Run with: sqlite3 db/gain.db < queries.sql
-- or paste individual blocks into a sqlite3 session.

-- q1: Smith vs GOP-House peers — the outlier screen
-- (Reproduces screen member-contribution-peer-outlier run-9; full shortlist at
--  investigations/screens/member-contribution-peer-outlier/run-9/shortlist.csv)
WITH money AS (
  SELECT bioguide, max(member_name) AS member_name, sum(total_amount) AS feca
  FROM derived_member_contribution_panel
  WHERE contribution_type='feca'
  GROUP BY bioguide
),
cp AS (
  SELECT bioguide, chamber, party FROM (
    SELECT bioguide, type AS chamber, party,
           row_number() OVER (PARTITION BY bioguide ORDER BY start DESC) AS rn
    FROM member_terms
  ) WHERE rn=1
),
m AS (
  SELECT money.bioguide, money.member_name, cp.chamber, cp.party, money.feca
  FROM money JOIN cp ON cp.bioguide = money.bioguide
),
cell AS (
  SELECT chamber, party,
         avg(feca) AS mu,
         avg(feca*feca) - avg(feca)*avg(feca) AS var,
         count(*) AS n
  FROM m GROUP BY chamber, party HAVING n >= 20 AND var > 0
)
SELECT m.member_name, m.party, m.chamber,
       round(m.feca,0)      AS feca,
       round(cell.mu,0)     AS peer_mean,
       cell.n               AS peer_n,
       round((m.feca - cell.mu)/sqrt(cell.var), 2) AS score
FROM m JOIN cell ON cell.chamber=m.chamber AND cell.party=m.party
WHERE m.chamber='rep' AND m.party='Republican'
ORDER BY score DESC
LIMIT 10;

-- q2: Smith's contribution breakdown by resolution method and confidence
SELECT hmm.method, hmm.confidence,
       count(*) AS item_rows,
       round(sum(ci.amount_num), 0) AS dollars
FROM senate_contribution_items ci
JOIN honoree_member_map hmm ON hmm.honoree_name = ci.honoree_name
WHERE hmm.bioguide = 'S001195'
  AND ci.contribution_type = 'feca'
GROUP BY hmm.method, hmm.confidence
ORDER BY dollars DESC;

-- q3: Name-resolution diagnostic — is "Jason Smith" unique?
-- All honoree entries mapping to S001195, and check for any other Smith resolution
SELECT honoree_name, bioguide, method, confidence
FROM honoree_member_map
WHERE honoree_name IN ('Jason Smith', 'JASON SMITH', 'jason smith');

-- (Also run: are there other members named Smith who could be confused?)
SELECT bioguide, first, last, official_full, last_party, last_state
FROM members
WHERE last = 'Smith'
ORDER BY last_party, last;

-- q4: Smith's FECA by filing year (gavel-year spike check)
SELECT cf.filing_year AS yr,
       count(*) AS rows,
       round(sum(ci.amount_num), 0) AS dollars
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
JOIN honoree_member_map hmm ON hmm.honoree_name = ci.honoree_name
WHERE hmm.bioguide = 'S001195'
  AND hmm.confidence >= 0.9
  AND ci.contribution_type = 'feca'
GROUP BY yr
ORDER BY yr;

-- q5: Smith's committee roles
SELECT c.name, mc.title, mc.side, mc.rank,
       c.parent_committee_id IS NULL AS is_full_committee
FROM member_committees mc
JOIN committees c ON c.committee_id = mc.committee_id
WHERE mc.bioguide = 'S001195'
ORDER BY is_full_committee DESC, mc.rank;

-- q7: Smith's rank and z-score across all LD-203 contribution types (salience-inflation check)
WITH by_type AS (
  SELECT p.contribution_type,
         p.bioguide,
         mt.party,
         mt.type AS chamber,
         sum(p.total_amount) AS total
  FROM derived_member_contribution_panel p
  JOIN (
    SELECT bioguide, party, type,
           row_number() OVER (PARTITION BY bioguide ORDER BY start DESC) AS rn
    FROM member_terms
  ) mt ON mt.bioguide = p.bioguide AND mt.rn = 1
  GROUP BY p.contribution_type, p.bioguide
),
ranked AS (
  SELECT *,
         row_number() OVER (PARTITION BY contribution_type ORDER BY total DESC) AS rnk,
         count(*) OVER (PARTITION BY contribution_type) AS type_n,
         avg(total) OVER (PARTITION BY contribution_type, chamber, party) AS peer_mu,
         avg(total*total) OVER (PARTITION BY contribution_type, chamber, party) -
           avg(total) OVER (PARTITION BY contribution_type, chamber, party) *
           avg(total) OVER (PARTITION BY contribution_type, chamber, party) AS peer_var
  FROM by_type
)
SELECT contribution_type,
       round(total, 0) AS smith_total,
       rnk AS smith_rank,
       type_n AS total_members,
       round(peer_mu, 0) AS gop_house_peer_mean,
       round((total - peer_mu) / CASE WHEN peer_var > 0 THEN sqrt(peer_var) ELSE NULL END, 2) AS z_score
FROM ranked
WHERE bioguide = 'S001195'
ORDER BY smith_total DESC;

-- q8: Gavel-transition spike test — 2022 vs 2023 FECA for all current R House full-committee chairs
-- (screen chair-transition-contribution-spike, run 10)
WITH chairs AS (
  SELECT mc.bioguide
  FROM member_committees mc
  JOIN committees c ON c.committee_id = mc.committee_id
  JOIN members m ON m.bioguide = mc.bioguide
  WHERE mc.title IN ('Chairman','Chair','Chairwoman')
    AND length(mc.committee_id) <= 4
    AND m.last_party = 'Republican'
    AND m.last_type = 'rep'
),
panel AS (
  SELECT p.bioguide, m.official_full, c.name AS committee,
         sum(CASE WHEN p.filing_year = 2022 THEN p.total_amount ELSE 0 END) AS feca_2022,
         sum(CASE WHEN p.filing_year = 2023 THEN p.total_amount ELSE 0 END) AS feca_2023,
         sum(CASE WHEN p.filing_year = 2024 THEN p.total_amount ELSE 0 END) AS feca_2024,
         sum(CASE WHEN p.filing_year = 2025 THEN p.total_amount ELSE 0 END) AS feca_2025
  FROM derived_member_contribution_panel p
  JOIN chairs ch ON ch.bioguide = p.bioguide
  JOIN members m ON m.bioguide = p.bioguide
  JOIN member_committees mc ON mc.bioguide = p.bioguide
    AND mc.title IN ('Chairman','Chair','Chairwoman')
  JOIN committees c ON c.committee_id = mc.committee_id
    AND length(c.committee_id) <= 4
  WHERE p.contribution_type = 'feca'
  GROUP BY p.bioguide
)
SELECT official_full, committee,
       round(feca_2022, 0) AS feca_2022,
       round(feca_2023, 0) AS feca_2023,
       round(feca_2024, 0) AS feca_2024,
       round(feca_2025, 0) AS feca_2025,
       round(feca_2023 / nullif(feca_2022, 0), 2) AS spike_23_vs_22,
       round((feca_2023 + feca_2024) / 2.0 / nullif(feca_2022, 0), 2) AS avg_post_vs_pre
FROM panel
WHERE feca_2022 > 0
ORDER BY spike_23_vs_22 DESC;

-- q9: Neal vs Smith year-by-year FECA — the gavel-flip quasi-experiment
-- Neal=Chair 2022, Ranking Member 2023+; Smith=Ranking Member 2022, Chair 2023+
SELECT p.filing_year,
       round(sum(CASE WHEN p.bioguide='N000015' THEN p.total_amount END), 0) AS neal_feca,
       round(sum(CASE WHEN p.bioguide='S001195' THEN p.total_amount END), 0) AS smith_feca
FROM derived_member_contribution_panel p
WHERE p.bioguide IN ('N000015','S001195')
  AND p.contribution_type = 'feca'
GROUP BY p.filing_year
ORDER BY p.filing_year;

-- q6: Prior W&M chairs — total FECA in panel and data coverage
SELECT m.official_full, m.last_party,
       min(cf.filing_year) AS first_yr,
       max(cf.filing_year) AS last_yr,
       count(*) AS rows,
       round(sum(ci.amount_num), 0) AS dollars
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
JOIN honoree_member_map hmm ON hmm.honoree_name = ci.honoree_name
JOIN members m ON m.bioguide = hmm.bioguide
WHERE hmm.bioguide IN ('B000755', 'C000071', 'N000015', 'R000570', 'S001195')
  AND ci.contribution_type = 'feca'
  AND hmm.confidence >= 0.9
GROUP BY hmm.bioguide
ORDER BY dollars DESC;
