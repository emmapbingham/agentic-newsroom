-- probe: National Flood Insurance Program lobbying volume vs. press, within INS code
SELECT count(*) FROM senate_lobbying_activities WHERE general_issue_code='INS' AND (description LIKE '%National Flood Insurance%' OR description LIKE '%NFIP%');
SELECT count(*) FROM press_fts WHERE press_fts MATCH '"National Flood Insurance" OR NFIP';
