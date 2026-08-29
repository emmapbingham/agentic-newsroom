-- probe: ART code masks two very different stories -- Live Nation/ticketing (loud) vs NEA/NEH riders (quiet)
SELECT count(*) FROM press_fts WHERE press_fts MATCH '"Live Nation" OR Ticketmaster';
SELECT c.name AS client, count(*) AS n_acts
FROM senate_filings f
JOIN senate_clients c ON c.id = f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid = f.filing_uuid
WHERE a.general_issue_code='ART'
GROUP BY c.name ORDER BY n_acts DESC LIMIT 10;
