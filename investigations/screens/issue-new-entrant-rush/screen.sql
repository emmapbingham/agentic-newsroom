-- Screen: issue-new-entrant-rush  (contrast: self-over-time / population-structure)
-- Baseline: each issue's 2022-2024 average count of first-time registrants.
--   Ranks issues by how much their 2025 first-time-entrant count exceeds that
--   baseline — i.e. where a rush of NEW lobbying registrants appeared in 2025.
--   Reads derived_registrant_issue_panel. Contextualizes the tariff lead: is the
--   entrant rush tariff-specific or a broad transition phenomenon?
WITH first_year AS (
  SELECT registrant_id, issue_code, issue_display, min(filing_year) AS fy
  FROM derived_registrant_issue_panel
  GROUP BY registrant_id, issue_code
),
by_issue AS (
  SELECT issue_code,
         max(issue_display) AS issue_display,
         sum(fy=2022) AS e2022, sum(fy=2023) AS e2023,
         sum(fy=2024) AS e2024, sum(fy=2025) AS e2025
  FROM first_year GROUP BY issue_code
)
SELECT
  issue_code,
  issue_display,
  (e2022+e2023+e2024)/3.0 AS baseline_avg,
  e2025                    AS entrants_2025,
  round(e2025 - (e2022+e2023+e2024)/3.0, 0) AS score   -- excess new entrants
FROM by_issue
WHERE (e2022+e2023+e2024)/3.0 >= 5     -- ignore tiny issues
ORDER BY score DESC
LIMIT 50;
