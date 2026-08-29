-- probe: NFIP press coverage clusters at lapse/deadline moments, near-silent otherwise,
-- while lobbying volume stays flat and steady year-round -- this is the sharper
-- invisible-provisions framing (crisis-only coverage, not "unknown" coverage).
SELECT strftime('%Y-%m', date) AS month, count(*) AS n
FROM press_releases
WHERE press_releases.rowid IN (SELECT rowid FROM press_fts WHERE press_fts MATCH '"National Flood Insurance" OR NFIP')
GROUP BY month ORDER BY month;

SELECT f.filing_year, count(*) AS n_acts
FROM senate_filings f
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
WHERE a.general_issue_code='INS' AND (a.description LIKE '%National Flood Insurance%' OR a.description LIKE '%NFIP%')
GROUP BY f.filing_year ORDER BY f.filing_year;
