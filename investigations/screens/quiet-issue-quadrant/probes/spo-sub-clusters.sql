-- probe: SPO sub-cluster split -- NIL/college athletics vs Olympics/World Cup vs combat sports/horse racing
SELECT
  CASE
    WHEN description LIKE '%NIL%' OR description LIKE '%Name, Image%' OR description LIKE '%collegiate athlet%' OR description LIKE '%college athlet%' OR description LIKE '%student athlete%' OR description LIKE '%student-athlete%' THEN 'NIL_college_athletics'
    WHEN description LIKE '%Olympic%' OR description LIKE '%FIFA%' OR description LIKE '%World Cup%' THEN 'olympics_world_cup'
    WHEN description LIKE '%horse racing%' OR description LIKE '%Horseracing%' THEN 'horse_racing'
    WHEN description LIKE '%boxing%' OR description LIKE '%mixed martial%' OR description LIKE '%combat sport%' THEN 'combat_sports'
    ELSE 'other'
  END AS cluster, count(*) AS n_acts
FROM senate_lobbying_activities WHERE general_issue_code='SPO'
GROUP BY cluster ORDER BY n_acts DESC;
SELECT 'NIL/college athletics' AS topic, count(*) FROM press_fts WHERE press_fts MATCH 'NIL OR "name image and likeness" OR "college athlet"'
UNION ALL SELECT 'Olympics/World Cup', count(*) FROM press_fts WHERE press_fts MATCH 'Olympic OR FIFA OR "World Cup"';
