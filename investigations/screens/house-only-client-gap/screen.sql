-- Screen: house-only-client-gap  (contrast: source-vs-source / absence)
-- Baseline: a registrant that files in BOTH chambers should disclose roughly
--   the same client roster to each. Reads derived_cross_chamber_engagements.
-- Ranks dual-chamber registrants by (house_only - senate_only) engagement-
--   quarters, 2022-2025 — i.e. clients shown to the House but not the Senate.
-- NOTE (verified 2026-06-13): in aggregate this asymmetry is ~3.4x, not the 65x
--   the sweep's name-join reported; this screen names the registrants driving it.
WITH dual AS (
  SELECT registrant_id
  FROM derived_cross_chamber_engagements
  GROUP BY registrant_id
  HAVING sum(presence = 'both') > 0
)
SELECT
  t.registrant_name,
  t.registrant_id,
  sum(t.presence = 'house_only')  AS house_only,
  sum(t.presence = 'senate_only') AS senate_only,
  sum(t.presence = 'both')        AS both,
  sum(t.presence = 'house_only') - sum(t.presence = 'senate_only') AS score
FROM derived_cross_chamber_engagements t
WHERE t.registrant_id IN (SELECT registrant_id FROM dual)
  AND t.filing_year BETWEEN 2022 AND 2025
GROUP BY t.registrant_id, t.registrant_name
HAVING house_only > 0
ORDER BY score DESC
LIMIT 50;
