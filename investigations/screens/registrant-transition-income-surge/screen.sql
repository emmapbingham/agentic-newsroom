-- Screen: registrant-transition-income-surge  (contrast: self-over-time)
-- Baseline: a registrant's own Q4-2024 income. Ranks firms by Q4-2024 -> Q1-2025
--   income jump (the presidential transition quarter). Reads
--   derived_registrant_income_panel (deduped, latest-posted). Volume floor:
--   Q4-2024 income >= $200k, so the % is not a small-base artifact.
-- Maps to lead trump-transition-access-surge.
WITH q AS (
  SELECT registrant_id, registrant_name,
         max(CASE WHEN filing_year=2024 AND quarter='Q4' THEN income_sum END) AS q4_2024,
         max(CASE WHEN filing_year=2025 AND quarter='Q1' THEN income_sum END) AS q1_2025
  FROM derived_registrant_income_panel
  WHERE (filing_year=2024 AND quarter='Q4') OR (filing_year=2025 AND quarter='Q1')
  GROUP BY registrant_id, registrant_name
)
SELECT
  registrant_name,
  registrant_id,
  q4_2024,
  q1_2025,
  round(q1_2025 - q4_2024, 0)                       AS abs_gain,
  round(100.0 * (q1_2025 - q4_2024) / q4_2024, 0)   AS score   -- pct QoQ
FROM q
WHERE q4_2024 >= 200000 AND q1_2025 IS NOT NULL
ORDER BY score DESC
LIMIT 50;
