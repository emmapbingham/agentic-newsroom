-- quiet-issue-quadrant screen
-- Ranks all issue codes by lobby-to-press ratio vs corpus mean.
-- Baseline: BUD ~4.4x (corpus anchor). Flag codes ≥2σ above mean.
-- Run against db/gain.db. Requires: derived_issue_quarter_volume_press.

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
    AVG(act_per_press)  AS mean_atp,
    AVG(inc_per_press)  AS mean_ipp,
    SQRT(AVG(act_per_press*act_per_press) - AVG(act_per_press)*AVG(act_per_press)) AS sd_atp,
    SQRT(AVG(inc_per_press*inc_per_press) - AVG(inc_per_press)*AVG(inc_per_press)) AS sd_ipp
  FROM with_ratio
)
SELECT
  r.issue_code, r.issue_name,
  ROUND(r.acts_2224)            AS acts,
  ROUND(r.press_2224)           AS press,
  ROUND(r.act_per_press, 2)     AS act_per_press,
  ROUND(r.inc_per_press/1e6, 3) AS inc_per_press_M,
  ROUND((r.act_per_press - s.mean_atp) / s.sd_atp, 2) AS z_act,
  ROUND((r.inc_per_press - s.mean_ipp) / s.sd_ipp, 2) AS z_inc
FROM with_ratio r, stats s
ORDER BY z_act DESC;
