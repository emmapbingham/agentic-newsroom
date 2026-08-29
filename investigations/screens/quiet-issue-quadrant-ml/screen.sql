-- quiet-issue-quadrant-ml screen
-- ML-classifier sibling of quiet-issue-quadrant (see that screen for the
-- keyword-based version). Ranks issue codes by lobby-to-press ratio vs
-- corpus mean, using derived_issue_quarter_volume_press_ml (press volume
-- from the M0 classifier / derived_press_issue_labels) instead of
-- ISSUE_KEYWORDS. Same shape, DIFFERENT method -- not a replacement.
--
-- KNOWN LIMITATION: M0 is confirmed recall-weak vs. keyword matching
-- (16.2% recall of INS's own narrow keyword set -- see
-- investigations/insurance-jurisdiction-no-press-lift/evidence.md E6) and
-- systematically ratchets every code's ratio UP relative to the keyword
-- version (fewer press hits counted almost everywhere), so a code ranking
-- "quiet" here may just mean M0 under-recalls its press vocabulary, not
-- that lobbying-vs-press attention genuinely diverges more than the
-- keyword screen already shows. Read a lead surfaced ONLY by this screen
-- (not also flagged by quiet-issue-quadrant) with extra skepticism, and
-- always hand-check a sample of the code's flagged/unflagged releases
-- before treating a divergence as real.
--
-- Run against db/gain.db. Requires: derived_issue_quarter_volume_press_ml.

WITH
baseline AS (
  SELECT issue_code, issue_name,
    SUM(total_activities)         AS acts_2224,
    SUM(total_income_apportioned) AS income_2224,
    SUM(n_press_releases)         AS press_2224
  FROM derived_issue_quarter_volume_press_ml
  WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code, issue_name
),
with_ratio AS (
  SELECT *,
    CAST(acts_2224 AS REAL)   / press_2224 AS act_per_press,
    CAST(income_2224 AS REAL) / press_2224 AS inc_per_press
  FROM baseline WHERE press_2224 >= 20
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
  ROUND((r.inc_per_press - s.mean_ipp) / s.sd_ipp, 2) AS z_inc,
  -- cross-reference: same code's keyword-based ratio, for comparison
  (SELECT ROUND(CAST(SUM(kw.total_activities) AS REAL) / SUM(kw.n_press_releases), 2)
   FROM derived_issue_quarter_volume_press kw
   WHERE kw.issue_code = r.issue_code AND kw.year BETWEEN 2022 AND 2024
     AND kw.n_press_releases > 0) AS keyword_act_per_press
FROM with_ratio r, stats s
ORDER BY z_act DESC;
