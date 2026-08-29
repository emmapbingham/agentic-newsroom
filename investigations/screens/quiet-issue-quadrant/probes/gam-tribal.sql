-- probe: GAM sub-cluster split by keyword-tagged description text
SELECT
  CASE
    WHEN description LIKE '%tribal%' OR description LIKE '%Tribe%' OR description LIKE '%Indian gaming%' OR description LIKE '%trust land%' OR description LIKE '%fee-to-trust%' THEN 'tribal'
    WHEN description LIKE '%sports%betting%' OR description LIKE '%sports wagering%' OR description LIKE '%prediction market%' OR description LIKE '%sportsbook%' THEN 'sports_betting_prediction'
    WHEN description LIKE '%WIRE Act%' OR description LIKE '%online gambling%' OR description LIKE '%internet gaming%' OR description LIKE '%mobile gaming%' OR description LIKE '%online wagering%' THEN 'online_igaming'
    ELSE 'other_commercial_casino'
  END AS cluster,
  count(*) AS n_acts
FROM senate_lobbying_activities
WHERE general_issue_code = 'GAM'
GROUP BY cluster ORDER BY n_acts DESC;
-- press cross-check:
SELECT 'tribal gaming' AS topic, count(*) FROM press_fts WHERE press_fts MATCH '"tribal gaming" OR "Indian gaming" OR "gaming compact"'
UNION ALL SELECT 'sports betting/prediction markets', count(*) FROM press_fts WHERE press_fts MATCH '"sports betting" OR "sports wagering" OR "prediction market"';
