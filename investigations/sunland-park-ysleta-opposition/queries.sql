-- Case: sunland-park-ysleta-opposition
-- Corpus: db/gain.db (Senate LDA filings). All queries read-only.

-- q1: who filed to support/oppose H.R.2208/S.4196 and its successor H.R.2873/S.1536
-- (Tribal Gaming Regulatory Compliance Act), distinct client/registrant/stance pairs.
-- NOTE: LIKE-matching on bill numbers "2208"/"4196" pulls in false positives from
-- unrelated bills sharing those digits (American Geophysical Union, American Society
-- of Civil Engineers, Chamber of Commerce, Hitachi, Pacific Seafood, Resolutionaries --
-- all confirmed off-topic by reading full description text). Excluded manually below;
-- re-verify this exclusion on every re-run.
WITH tagged AS (
  SELECT DISTINCT c.name AS client, r.name AS registrant,
    CASE WHEN a.description LIKE '%Oppos%' OR a.description LIKE '%oppos%' THEN 'OPPOSE'
         WHEN a.description LIKE '%Advocacy%' OR a.description LIKE '%Support%' OR a.description LIKE '%support%' OR a.description LIKE '%encourage sponsors%' THEN 'SUPPORT'
         ELSE 'unclear' END AS stance
  FROM senate_filings f
  JOIN senate_clients c ON c.id=f.client_id
  JOIN senate_registrants r ON r.id=f.registrant_id
  JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
  WHERE a.description LIKE '%2208%' OR a.description LIKE '%4196%' OR a.description LIKE '%Ysleta%' OR a.description LIKE '%Alabama-Coushatta%'
     OR a.description LIKE '%2873%' OR a.description LIKE '%1536%' OR a.description LIKE '%Tribal Gaming Regulatory Compliance%'
)
SELECT client, registrant, stance, count(*)
FROM tagged
WHERE client NOT IN ('AMERICAN GEOPHYSICAL UNION','AMERICAN SOCIETY OF CIVIL ENGINEERS',
                      'CHAMBER OF COMMERCE OF THE U.S.A.','HITACHI, LTD','PACIFIC SEAFOOD GROUP',
                      'RESOLUTIONARIES')
GROUP BY client, registrant, stance
ORDER BY stance, client;

-- q2: Sunland Park Racetrack & Casino -- every distinct filing_uuid on this issue,
-- with filing_year/period and source URL, to confirm continuity of opposition.
SELECT f.filing_uuid, f.filing_year, f.filing_period_display,
  'https://lda.gov/filings/public/filing/' || f.filing_uuid || '/print/' AS public_url
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
WHERE c.name = 'SUNLAND PARK RACETRACK & CASINO'
GROUP BY f.filing_uuid
ORDER BY f.filing_year, f.filing_period_display;

-- q3: Sunland Park's full activity-description text across all filings on this issue
-- (verbatim opposition language, quarter by quarter).
SELECT f.filing_year, f.filing_period_display, f.filing_uuid, a.description
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
WHERE c.name = 'SUNLAND PARK RACETRACK & CASINO'
ORDER BY f.filing_year, f.filing_period_display;

-- q4: registrant (lobbyist/firm) Sunland Park used, and lobbyist-level detail if available.
SELECT DISTINCT r.name AS registrant
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_registrants r ON r.id=f.registrant_id
WHERE c.name = 'SUNLAND PARK RACETRACK & CASINO';

-- q5: Ysleta del Sur Pueblo Tribe + Alabama-Coushatta Tribe of Texas -- their filing
-- history and registrants, for comparison (who they've paid to push the bill).
SELECT c.name AS client, r.name AS registrant, f.filing_year, f.filing_period_display, f.filing_uuid
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_registrants r ON r.id=f.registrant_id
WHERE c.name IN ('YSLETA DEL SUR PUEBLO TRIBE','ALABAMA-COUSHATTA TRIBE OF TEXAS')
ORDER BY c.name, f.filing_year, f.filing_period_display;

-- q6: press coverage check specific to Sunland Park (not just the
-- bill generally) -- confirms/refutes the "zero press coverage of Sunland Park's role" claim.
-- Ad hoc run for E4; formalized here.
SELECT bioguide_id, date, title FROM press_releases
WHERE press_releases.rowid IN (SELECT rowid FROM press_fts WHERE press_fts MATCH '"Sunland Park"');

-- q7: Sunland Park's registrant (Landon Fulmer) -> Senate<->House bridge id, for E6.
SELECT id FROM senate_registrants WHERE id IN
  (SELECT registrant_id FROM senate_filings WHERE client_id IN
    (SELECT id FROM senate_clients WHERE name = 'SUNLAND PARK RACETRACK & CASINO'));
-- -> 401104304 (MR. LANDON FULMER)

-- q8: Sunland Park's House LD-2 filings, via the bridge, for E6 (continuity check).
SELECT f.filing_year, f.filing_period, f.house_filing_id
FROM house_filings f
WHERE f.senate_registrant_id = 401104304 AND f.client_name = 'Sunland Park Racetrack & Casino'
ORDER BY f.filing_year, f.filing_period;

-- q9: House-side verbatim opposition text, for E6 (corroborate E3 in the second disclosure regime).
SELECT f.filing_year, f.filing_period, f.house_filing_id, a.description
FROM house_filings f
JOIN house_activities a ON a.house_filing_id = f.house_filing_id
WHERE f.client_name = 'Sunland Park Racetrack & Casino'
ORDER BY f.filing_year, f.filing_period;

-- q10: House-side "who else opposes" sweep, mirroring q1's method, for E6.
-- NOTE: same false-positive risk as q1, worse on House data (confirmed via full-text read,
-- e.g. AFGE's "H.R. 2550/S. 2873" hit is the unrelated Protect Americas Workforce Act) --
-- always read full description text before trusting the stance tag.
WITH tagged AS (
  SELECT DISTINCT f.client_name AS client,
    CASE WHEN a.description LIKE '%Oppos%' OR a.description LIKE '%oppos%' THEN 'OPPOSE'
         WHEN a.description LIKE '%Advocacy%' OR a.description LIKE '%Support%' OR a.description LIKE '%support%' THEN 'SUPPORT'
         ELSE 'unclear' END AS stance
  FROM house_filings f
  JOIN house_activities a ON a.house_filing_id = f.house_filing_id
  WHERE a.description LIKE '%2208%' OR a.description LIKE '%4196%' OR a.description LIKE '%Ysleta%'
     OR a.description LIKE '%Alabama-Coushatta%' OR a.description LIKE '%2873%' OR a.description LIKE '%1536%'
     OR a.description LIKE '%Tribal Gaming Regulatory Compliance%'
)
SELECT client, stance FROM tagged ORDER BY stance, client;

-- q11 (open, not yet run): Ysleta/Alabama-Coushatta House filings extend to 2026 Q1,
-- later than the Senate pull in q5 (stops 2025 Q4) -- re-run q5 to check for a matching
-- Senate 2026 Q1 filing before treating this as a House-only extension.

-- q12 (E10, skeptic pass): base rate -- every client/registrant tagged OPPOSE/SUPPORT
-- on any Indian/Native-American-Affairs filing whose description mentions gaming/casino/IGRA
-- (the real tribal-gaming lobbying peer set, not the whole corpus). Confirms only 3 clients
-- in this niche show explicit OPPOSE language at all; Sunland Park's streak (14) dwarfs the
-- next-longest (Cow Creek Band of Umpqua Tribe of Indians, 3, an unrelated intertribal dispute).
SELECT c.name AS client, r.name AS registrant,
  CASE WHEN a.description LIKE '%Oppos%' OR a.description LIKE '%oppos%' THEN 'OPPOSE'
       WHEN a.description LIKE '%Support%' OR a.description LIKE '%support%' OR a.description LIKE '%Advocacy%' THEN 'SUPPORT'
       ELSE 'unclear' END AS stance,
  count(DISTINCT f.filing_uuid) AS n_filings
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_registrants r ON r.id=f.registrant_id
JOIN senate_lobbying_activities a ON a.filing_uuid=f.filing_uuid
WHERE a.general_issue_code_display = 'Indian/Native American Affairs'
  AND (a.description LIKE '%gaming%' OR a.description LIKE '%casino%' OR a.description LIKE '%IGRA%')
GROUP BY c.name, r.name, stance
ORDER BY stance, n_filings DESC;

-- q13 (E10, skeptic pass): is the 2023 Q1 gap a corpus-wide filing lull, or Sunland-Park-specific?
-- It's not corpus-wide -- 2023 Q1 has the highest total filing volume of any 2023 quarter.
SELECT filing_year, filing_period_display, count(*) AS total_filings
FROM senate_filings
WHERE filing_year = 2023
GROUP BY filing_year, filing_period_display
ORDER BY filing_period_display;

-- q14 (E10, skeptic pass): any alternate-spelling Sunland Park filing that would fill the
-- 2023 Q1 gap? No -- also surfaces an unrelated client, "City of Sunland Park" (municipal
-- government via R.R.P. Consulting Engineers), not the casino -- do not conflate the two.
SELECT f.filing_uuid, c.name, f.filing_year, f.filing_period_display
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
WHERE c.name LIKE '%SUNLAND%'
ORDER BY f.filing_year, f.filing_period_display;

-- q15 (E10, skeptic pass): any LD-203 contributions tied to Sunland Park's lobbyist
-- (registrant id 401104304, Landon Fulmer -- confirmed the only registrant record under
-- that name)? Zero rows -- no contribution angle exists, pure disclosure story.
SELECT ci.honoree_name, ci.amount_num, cf.filing_uuid, cf.filing_year
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
JOIN senate_registrants r ON r.id = cf.registrant_id
WHERE r.name LIKE '%FULMER%' OR r.id = 401104304;

-- q16 (E10 follow-up): explains the 2023 Q1 gap -- is it Fulmer-wide (all clients dark
-- that quarter) or Sunland-Park-specific? It's specific: he filed for all 4 other clients
-- in 2023 Q1, just not Sunland Park.
SELECT f.filing_uuid, f.filing_year, f.filing_period_display, c.name AS client, r.name AS registrant
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_registrants r ON r.id=f.registrant_id
WHERE r.id = 401104304 AND f.filing_year = 2023
ORDER BY f.filing_period_display;

-- q17 (E10 follow-up): Sunland Park's filing_type_display sequence -- reveals a
-- Termination (2022 Q4) followed by a Registration - Amendment (2023 Q2), explaining
-- the 2023 Q1 gap as a formal registration lapse, not a missed/skipped filing.
SELECT f.filing_uuid, f.filing_type_display, f.filing_year, f.filing_period_display
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
WHERE c.name = 'SUNLAND PARK RACETRACK & CASINO'
ORDER BY f.filing_year, f.filing_period_display;

-- q18 (E6 base-rate follow-up): is terminate-then-later-re-register (Sunland Park's
-- pattern) unusual corpus-wide, or routine? Distribution of all filing types, then count
-- of distinct client/registrant pairs showing a termination filing followed at any later
-- date by a fresh registration/registration-amendment filing for that same pair.
SELECT filing_type_display, count(*)
FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id
JOIN senate_registrants r ON r.id=f.registrant_id
GROUP BY filing_type_display
ORDER BY count(*) DESC;

WITH term AS (
  SELECT DISTINCT c.id AS client_id, r.id AS registrant_id
  FROM senate_filings f
  JOIN senate_clients c ON c.id=f.client_id
  JOIN senate_registrants r ON r.id=f.registrant_id
  WHERE f.filing_type_display LIKE '%Termination%'
),
reg AS (
  SELECT DISTINCT c.id AS client_id, r.id AS registrant_id
  FROM senate_filings f
  JOIN senate_clients c ON c.id=f.client_id
  JOIN senate_registrants r ON r.id=f.registrant_id
  WHERE f.filing_type_display IN ('Registration', 'Registration - Amendment')
)
SELECT count(DISTINCT term.client_id || '-' || term.registrant_id) AS pairs_that_terminated_and_later_reregistered
FROM term
JOIN reg ON reg.client_id = term.client_id AND reg.registrant_id = term.registrant_id;
