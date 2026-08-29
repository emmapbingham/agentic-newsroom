-- probe: CPT sub-cluster split -- music licensing is far quieter than drug-patent or
-- patent-procedure reform threads in the same issue code
SELECT
  CASE
    WHEN description LIKE '%march-in%' OR description LIKE '%Bayh-Dole%' OR description LIKE '%biosimilar%' OR description LIKE '%Affordable Prescriptions%' OR description LIKE '%drug pric%' OR description LIKE '%generic%' THEN 'drug_patent_pricing'
    WHEN description LIKE '%DMCA%' OR description LIKE '%anti-piracy%' OR description LIKE '%counterfeit%' OR description LIKE '%SHOP SAFE%' OR description LIKE '%site blocking%' THEN 'piracy_counterfeit'
    WHEN description LIKE '%PTAB%' OR description LIKE '%Patent Trial and Appeal%' OR description LIKE '%patent eligibility%' OR description LIKE '%PERA%' OR description LIKE '%PREVAIL%' OR description LIKE '%Standard Essential Patent%' OR description LIKE '%patent thicket%' THEN 'patent_procedure_reform'
    WHEN description LIKE '%music%' OR description LIKE '%sound recording%' OR description LIKE '%radio%' OR description LIKE '%SoundExchange%' OR description LIKE '%performance right%' THEN 'music_licensing'
    ELSE 'other'
  END AS cluster, count(*) AS n_acts
FROM senate_lobbying_activities WHERE general_issue_code = 'CPT'
GROUP BY cluster ORDER BY n_acts DESC;
-- press cross-check
SELECT 'music licensing' AS topic, count(*) FROM press_fts WHERE press_fts MATCH '"music licensing" OR "performance right" OR SoundExchange OR "American Music Fairness"'
UNION ALL SELECT 'drug patent pricing', count(*) FROM press_fts WHERE press_fts MATCH '"march-in" OR "Bayh-Dole" OR biosimilar OR "drug pricing"';
-- top music-licensing filers (radio side vs. label/artist side)
SELECT c.name, count(*) AS n_acts
FROM senate_filings f JOIN senate_clients c ON c.id=f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
WHERE a.general_issue_code='CPT' AND (a.description LIKE '%music%' OR a.description LIKE '%sound recording%' OR a.description LIKE '%radio%' OR a.description LIKE '%SoundExchange%' OR a.description LIKE '%performance right%')
GROUP BY c.name ORDER BY n_acts DESC LIMIT 15;
