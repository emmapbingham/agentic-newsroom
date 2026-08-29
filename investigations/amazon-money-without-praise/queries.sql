-- amazon-money-without-praise
--
-- Money/press-linked entity: entity_id=125 in derived_client_alias_index ->
-- registrant_id=54494, "AMAZON.COM SERVICES LLC", self-filed (in-house).
-- This is the entity screen 40 actually reaches (in-house filers only, via
-- exact entity<->registrant name match) and the one tied to E1's honoree
-- money and press mentions. CORRECTED 2026-07-08: q1/q2 originally (wrongly)
-- used client_id IN (184204, 210237) = "AMAZON.COM SERVICES, INC." as a
-- *client* of outside registrants AVOQ LLC / Endgame Strategies LLC -- a
-- real but different Amazon lobbying channel, not reachable by screen 40.
-- q5 pulls that outside-firm channel separately, kept for reference /
-- possible "total footprint" framing but NOT the basis for E2/E3.

-- q1: top issue codes by activity count, correct in-house filer
SELECT a.general_issue_code_display, count(*) n
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE f.registrant_id = 54494
GROUP BY a.general_issue_code_display
ORDER BY n DESC;

-- q2: antitrust / warehouse-worker activity descriptions with filing_uuid + period
SELECT f.filing_uuid, f.filing_year, f.filing_period, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE f.registrant_id = 54494
  AND (a.description LIKE '%Warehouse Worker%'
       OR a.description LIKE '%American Innovation and Choice%'
       OR a.description LIKE '%American Choice and Innovation%'
       OR a.description LIKE '%Competition and Antitrust Law Enforcement%')
ORDER BY f.filing_year, f.filing_period;

-- q3: confirm registrant identity / self-filing
SELECT DISTINCT r.name, f.client_id, c.name AS client_name
FROM senate_filings f
JOIN senate_registrants r ON r.id = f.registrant_id
JOIN senate_clients c ON c.id = f.client_id
WHERE f.registrant_id = 54494;

-- q4: all issue-code descriptions, correct filer (re-derive E2/E3 detail on demand)
SELECT a.general_issue_code_display, a.description, f.filing_uuid, f.filing_year, f.filing_period
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE f.registrant_id = 54494
ORDER BY a.general_issue_code_display, f.filing_year, f.filing_period;

-- q5 (reference only, NOT used in E2/E3): the outside-firm channel
-- (AVOQ LLC / Endgame Strategies LLC representing "AMAZON.COM SERVICES,
-- INC." as client) -- a real, separate lobbying channel not reachable by
-- screen 40's in-house-only bound. Kept in case a "total Amazon footprint"
-- framing is wanted later.
SELECT a.general_issue_code_display, count(*) n
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE f.client_id IN (184204, 210237)
GROUP BY a.general_issue_code_display
ORDER BY n DESC;

-- q6 (E6): press-declared bill support beyond formal cosponsorship.
-- Search the 39 Amazon-money members' OWN press releases for the bill
-- names/numbers directly -- a lower-cost, earlier signal than cosponsorship.
-- bioguide list comes from derived/cosponsorship_crosswalk.json (the 39
-- money+press-mention members from screen 40, entity_id=125).
-- Run via Python (see analysis/pull_cosponsors.py's member list) since the
-- bioguide IN (...) list is 39 values; SQL form for one bill family shown:
SELECT release_id, bioguide_id, member_name, date, title
FROM press_releases
WHERE bioguide_id IN (
  'W000805','R000122','K000384','W000779','M001163','B001230','B001292',
  'C001108','K000383','H000874','P000034','S000148','S001190','H001046',
  'S001194','K000400','C000880','G000574','M001153','S001181','B001257',
  'C001098','C001119','S000168','T000193','C001095','G000585','D000622',
  'M001213','R000618','B001305','C001075','V000128','L000590','L000603',
  'H001068','N000188','S001218','S001203'
)
AND (
  text LIKE '%Warehouse Worker Protection Act%' OR text LIKE '%S.4260%'
  OR text LIKE '%S. 4260%' OR text LIKE '%H.R.8639%' OR text LIKE '%H.R. 8639%'
  OR text LIKE '%S.2613%' OR text LIKE '%S. 2613%'
  OR text LIKE '%American Innovation and Choice Online Act%'
  OR text LIKE '%American Choice and Innovation Online Act%'
  OR text LIKE '%S.2992%' OR text LIKE '%S. 2992%'
  OR text LIKE '%H.R.3816%' OR text LIKE '%H.R. 3816%'
)
ORDER BY bioguide_id, date;

-- q7 (E7): committee-stage action + Judiciary membership check.
-- Amazon-money members who sat on House/Senate Judiciary (jurisdiction for
-- AICOA) per member_committees_history (earliest snapshot 2022-01-04 --
-- covers S.2992's 2022-01-20 markup, does NOT cover H.R.3816's 2021-06-23/24
-- markup -- flagged caveat in evidence.md E7).
SELECT bioguide, committee_id, side, rank, title, min(valid_from) AS earliest
FROM member_committees_history
WHERE committee_id IN ('HSJU','SSJU')
AND bioguide IN (
  'W000805','R000122','K000384','W000779','M001163','B001230','B001292',
  'C001108','K000383','H000874','P000034','S000148','S001190','H001046',
  'S001194','K000400','C000880','G000574','M001153','S001181','B001257',
  'C001098','C001119','S000168','T000193','C001095','G000585','D000622',
  'M001213','R000618','B001305','C001075','V000128','L000590','L000603',
  'H001068','N000188','S001218','S001203'
)
GROUP BY bioguide, committee_id;
-- committee actions/markup dates for AICOA/WWPA pulled via congress.gov
-- /bill/.../actions and /bill/.../committees (see sources/congress-gov-bills.md);
-- not a gain.db query, no SQL form.

-- q8 (E8): Gallego's top donors by dollar amount, deduped (same pattern as
-- screen 40's `money` CTE -- distinct contributor/payee/date/amount tuples
-- per registrant, avoids raw-summing inflation).
SELECT r.id AS registrant_id, r.name AS registrant_name,
       sum(amount_num) AS feca_usd, count(*) AS n
FROM (
  SELECT DISTINCT cf.registrant_id, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
  WHERE ci.honoree_name IN (
    SELECT honoree_name FROM honoree_member_map
    WHERE bioguide = 'G000574' AND confidence >= 0.9
  )
  AND ci.contribution_type = 'feca' AND ci.amount_num > 0
) t
JOIN senate_registrants r ON r.id = t.registrant_id
GROUP BY r.id, r.name
ORDER BY feca_usd DESC;

-- q9 (E8): press mentions of a named corporate donor in Gallego's own
-- releases -- swap the LIKE term per donor checked. Pinnacle West Capital
-- Corp trades as "APS" (Arizona Public Service) in its own press language --
-- the registrant name doesn't appear verbatim, only the trade name does.
-- CAUTION: 'APS' is short enough to substring-match inside other words
-- (e.g. "gaps") -- use word-boundary punctuation, verify hits by hand
-- before citing (this caught a real bug during E8: an earlier '%APS %'
-- pattern matched "g APS " inside "gaps" via a LIKE quirk).
SELECT release_id, date, title
FROM press_releases
WHERE bioguide_id = 'G000574'
  AND (text LIKE '% APS.%' OR text LIKE '% APS,%' OR text LIKE '% APS''s%'
       OR text LIKE 'APS %' OR text LIKE '%Pinnacle West%'
       OR text LIKE '%Arizona Public Service%')
ORDER BY date;

-- q10 (E9): contribution-level detail (contributor_name, filer_type), not
-- just the honoree-level dollar aggregate used elsewhere in this case.
-- Reveals whether "Amazon money" is the corporate PAC or an individual
-- lobbyist's personal SELF-attributed contribution disclosed on the same
-- LD-203 filing.
SELECT ci.item_id, ci.contributor_name, ci.payee_name, ci.honoree_name,
       ci.amount, ci.date, cf.filer_type, cf.lobbyist_id
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
WHERE cf.registrant_id = 54494
AND ci.honoree_name IN (
  SELECT honoree_name FROM honoree_member_map
  WHERE bioguide IN ('N000188','S001203','G000574') AND confidence >= 0.9
)
AND ci.contribution_type = 'feca' AND ci.amount_num > 0
ORDER BY ci.date;

-- q11 (E9): Arizona-employer boring explanation check -- does Amazon PAC
-- give to Mark Kelly (AZ's other senator) too? Zero rows = no.
SELECT ci.payee_name, ci.amount_num, ci.date
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
WHERE cf.registrant_id = 54494
AND ci.contributor_name = 'AMAZON.COM SERVICES LLC SEPARATE SEGREGATED FUND (AMAZON PAC)'
AND ci.honoree_name IN (
  SELECT honoree_name FROM honoree_member_map
  WHERE bioguide = 'K000377' AND confidence >= 0.9
);

-- q12 (E9): dollar distribution of the 39-member set by chamber, to check
-- whether Gallego's $11,000 is an outlier (it isn't -- it's the Senate
-- median). Run against derived/cosponsorship_crosswalk.json in Python, not
-- gain.db directly (feca_usd field already computed there).

-- q13 (E10, skeptic pass): SELF/individual-lobbyist trap checked across the
-- FULL 39-member set (E9 only checked Norcross/Smith/Gallego). Independent
-- re-derivation, not read from prior evidence blocks. Catches Angie Craig
-- ($6,200, entirely SELF/lobbyist_id=56820, same trap as Smith).
SELECT hm.bioguide, m.official_full, ci.contributor_name, cf.filer_type,
       sum(ci.amount_num) tot
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid = ci.filing_uuid
JOIN honoree_member_map hm ON hm.honoree_name = ci.honoree_name AND hm.confidence >= 0.9
JOIN members m ON m.bioguide = hm.bioguide
WHERE cf.registrant_id = 54494
AND hm.bioguide IN (
  'W000805','R000122','K000384','W000779','M001163','B001230','B001292',
  'C001108','K000383','H000874','P000034','S000148','S001190','H001046',
  'S001194','K000400','C000880','G000574','M001153','S001181','B001257',
  'C001098','C001119','S000168','T000193','C001095','G000585','D000622',
  'M001213','R000618','B001305','C001075','V000128','L000590','L000603',
  'H001068','N000188','S001218','S001203'
)
AND ci.contribution_type = 'feca' AND ci.amount_num > 0
GROUP BY hm.bioguide, ci.contributor_name
ORDER BY hm.bioguide, tot DESC;

-- q14 (E10, skeptic pass): press mentions for the 4 WWPA_HR cosponsors not
-- previously checked against E1's genuine-critic list (Pallone, Thompson,
-- Gomez, Stansbury -- E5 only cross-checked the AICOA_S side, Warner/Reed).
SELECT dcm.bioguide_id, p.release_id, p.date, p.title
FROM derived_client_press_mentions dcm
JOIN press_releases p ON p.release_id = dcm.release_id
WHERE dcm.entity_id = 125
AND dcm.bioguide_id IN ('P000034','T000193','G000585','S001218')
ORDER BY dcm.bioguide_id, p.date;
