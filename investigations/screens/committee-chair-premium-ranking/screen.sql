-- Screen: committee-role-contribution-premium  (contrast: population-structure)
-- Baseline: within a full committee, the chair should raise about the same FECA
--   money as the rank-and-file. Ranks full committees by chair / member-mean
--   ratio. Reads derived_member_contribution_panel + member_committees.
-- Maps to lead chair-power-premium. NB member_committees = current Congress
--   (temporal mismatch with 2022-26 money); subcommittees excluded (id len<=4).
WITH money AS (
  SELECT bioguide, sum(total_amount) AS feca
  FROM derived_member_contribution_panel
  WHERE contribution_type='feca' GROUP BY bioguide
),
roled AS (
  SELECT mc.committee_id,
         CASE WHEN mc.title IN ('Chairman','Chair','Chairwoman') THEN 'chair' ELSE 'member' END AS role,
         coalesce(money.feca, 0) AS feca
  FROM member_committees mc
  LEFT JOIN money ON money.bioguide = mc.bioguide
  WHERE length(mc.committee_id) <= 4
    AND (mc.title IS NULL OR mc.title NOT IN ('Ex Officio','Ranking Member','Vice Chair','Vice Chairman'))
)
SELECT
  c.name AS committee,
  r.committee_id,
  round(max(CASE WHEN r.role='chair' THEN r.feca END), 0)  AS chair_feca,
  round(avg(CASE WHEN r.role='member' THEN r.feca END), 0) AS member_mean,
  round(max(CASE WHEN r.role='chair' THEN r.feca END)
        / nullif(avg(CASE WHEN r.role='member' THEN r.feca END), 0), 1) AS score  -- ratio
FROM roled r
JOIN committees c ON c.committee_id = r.committee_id
GROUP BY r.committee_id
HAVING chair_feca IS NOT NULL AND member_mean > 0
ORDER BY score DESC
LIMIT 50;
