-- Screen: member-contribution-peer-outlier  (contrast: outlier-vs-peers)
-- Baseline: chamber x party mean & stddev of total FECA receipts among current
--   members present in the contribution panel. score = z = (feca - cell_mean)/cell_sd.
--   Flags members raising anomalously much FECA vs same-chamber, same-party peers.
--   Reads derived_member_contribution_panel + member_terms (chamber via `type`).
WITH money AS (
  SELECT bioguide, max(member_name) AS member_name, sum(total_amount) AS feca
  FROM derived_member_contribution_panel
  WHERE contribution_type='feca'
  GROUP BY bioguide
),
cp AS (  -- most-recent term: chamber + party
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
ORDER BY score DESC
LIMIT 60;
