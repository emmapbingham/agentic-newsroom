-- Screen: chair-transition-contribution-spike  (contrast: self-over-time)
-- Baseline: each member's own 2022 FECA total (pre-gavel, when all current
--   Republican House chairs were in the minority). All current R House full-
--   committee chairs took gavels simultaneously in Jan 2023, making 2022 a
--   clean pre-gavel baseline for the whole cohort.
--   score = feca_2023 / feca_2022 (spike ratio). A ratio of 1.0 means no change.
--   Reads derived_member_contribution_panel + member_committees + committees + members.
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
