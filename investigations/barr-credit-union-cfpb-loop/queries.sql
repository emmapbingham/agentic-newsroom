-- q1: the pair from screen run 36 (deduped money + mention count)
-- (full screen: investigations/screens/client-mention-honoree-triangle/screen.sql)
SELECT * FROM (
  SELECT DISTINCT er.canonical_name, h.bioguide,
         ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM (SELECT DISTINCT a.entity_id, a.canonical_name, r.id AS registrant_id
        FROM derived_client_alias_index a
        JOIN senate_registrants r
          ON UPPER(replace(replace(r.name,'.',''),',','')) = a.alias
        WHERE a.status <> 'rejected_too_generic'
          AND a.canonical_name LIKE 'CREDIT UNION NATIONAL%') er
  JOIN senate_contribution_filings cf ON cf.registrant_id = er.registrant_id
  JOIN senate_contribution_items ci ON ci.filing_uuid = cf.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name = ci.honoree_name AND h.confidence >= 0.9
  WHERE ci.contribution_type='feca' AND ci.amount_num > 0
    AND h.bioguide = (SELECT bioguide FROM members WHERE official_full='Andy Barr'));

-- q1b: the three ACU-citing releases (row-level, with urls)
SELECT release_id, date, title, url FROM derived_client_press_mentions
WHERE member_name='Andy Barr' AND canonical_name LIKE 'CREDIT UNION NATIONAL%'
GROUP BY release_id ORDER BY date;

-- q2: dated timeline with filing_uuids (E2)
SELECT ci.date, ci.amount_num, ci.payee_name, ci.filing_uuid, cf.filer_type
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
JOIN members m ON m.bioguide=h.bioguide
WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0
  AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND cf.filer_type='organization'
ORDER BY ci.date;

-- q3: all credit-union registrants honoring Barr (deduped)
SELECT r.name, sum(d.amount_num) usd FROM (
  SELECT DISTINCT cf.registrant_id rid, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  JOIN members m ON m.bioguide=h.bioguide
  WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0) d
JOIN senate_registrants r ON r.id=d.rid
WHERE r.name LIKE '%CREDIT UNION%' GROUP BY r.id;

-- q4 (RUN 2026-07-07 → E4): base rate — ACU's full honoree footprint; is Barr top-tier or median?
WITH d AS (
  SELECT DISTINCT h.bioguide, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  WHERE ci.contribution_type='feca' AND ci.amount_num>0
    AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%'))
SELECT m.official_full, m.last_party, m.last_state, sum(d.amount_num) usd
FROM d JOIN members m ON m.bioguide=d.bioguide
GROUP BY d.bioguide ORDER BY usd DESC;

-- q5 (RUN 2026-07-07 → E5): every registrant honoring Barr, ranked + dated around 2025-02-20
--            (the full financial-sector pivot stack)
SELECT r.name, sum(d.amount_num) usd,
       sum(CASE WHEN d.date >= '2025-02-20' THEN d.amount_num ELSE 0 END) usd_after_pivot,
       min(CASE WHEN d.date >= '2025-02-20' THEN d.date END) first_after_pivot
FROM (
  SELECT DISTINCT cf.registrant_id rid, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  JOIN members m ON m.bioguide=h.bioguide
  WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0) d
JOIN senate_registrants r ON r.id=d.rid
GROUP BY r.id ORDER BY usd DESC;

-- q6 (RUN 2026-07-07 → E6): does ACU's lobbying name Barr's bills? (activity descriptions)
SELECT f.filing_year, f.filing_period, a.general_issue_code_display, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%UDAAP%' OR a.description LIKE '%TABS%' OR a.description LIKE '%Barr%');

-- ============ E4-E9 supporting queries (run 2026-07-07) ============

-- q4b (E4): base-rate distribution stats over ACU's honoree footprint
WITH d AS (
  SELECT DISTINCT h.bioguide, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  WHERE ci.contribution_type='feca' AND ci.amount_num>0
    AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')),
per AS (SELECT bioguide, sum(amount_num) usd FROM d GROUP BY bioguide)
SELECT count(*) n_members, sum(usd) total_usd, avg(usd) mean_usd,
  (SELECT usd FROM per ORDER BY usd LIMIT 1 OFFSET (SELECT count(*)/2 FROM per)) median_approx,
  max(usd) max_usd FROM per;
-- → 527 members; $6,208,500 total; mean $11,781; median ~$10,000; max $50,000

-- q4c (E4): Barr's rank within that footprint
WITH d AS (
  SELECT DISTINCT h.bioguide, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  WHERE ci.contribution_type='feca' AND ci.amount_num>0
    AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')),
per AS (SELECT bioguide, sum(amount_num) usd FROM d GROUP BY bioguide),
ranked AS (SELECT bioguide, usd, RANK() OVER (ORDER BY usd DESC) rnk, count(*) OVER () n FROM per)
SELECT r.rnk, r.n, r.usd, m.official_full FROM ranked r JOIN members m ON m.bioguide=r.bioguide
WHERE m.official_full='Andy Barr';   -- → rank 5 of 527, $40,000

-- q5b (E5): every LD-203 row to an "...FOR SENATE..." payee honoring Barr, by date
--           (the "day-one" test — who was on Barr for Senate before ACU's 2025-02-20?)
SELECT r.name, d.date, d.amount_num, d.payee_name
FROM (
  SELECT DISTINCT cf.registrant_id rid, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  JOIN members m ON m.bioguide=h.bioguide
  WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0) d
JOIN senate_registrants r ON r.id=d.rid
WHERE d.payee_name LIKE '%SENATE%' ORDER BY d.date;
-- → 5 registrants reported to "ANDY BARR FOR SENATE, INC." BEFORE ACU (2025-02-20):
--   Cresco Labs 01-31, Nationwide 02-04, Indep. Insurance Agents 02-10,
--   Huntington Bancshares 02-13, UPS 02-17. ACU is the 6th.

-- q6b (E6): the named-bill snippet in ACU's 2025 Senate lobbying activity descriptions
SELECT substr(a.description, instr(a.description,'Support Taking Account')-40, 380) AS bills
FROM senate_lobbying_activities a JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.filing_uuid='579f0209-4eac-4933-b277-3978e56896a8' AND a.description LIKE '%UDAAP%' LIMIT 1;
-- → "...Support Taking Account of Bureaucrats Spending Act (H.R. 654)
--      Support Rectifying UDAAP Act (H.R. 1652)..."  (Barr's TABS + UDAAP bills by number)

-- q7 (E7): full text of the three ACU-citing releases (endorsement quotes)
SELECT date, title, text FROM press_releases WHERE url IN (
  'https://barr.house.gov/press-releases?ID=B168D678-0C8F-4766-B711-1C51D5C74372',
  'https://barr.house.gov/press-releases?ID=0BF254FA-1F21-4097-9427-787F8B587593',
  'https://barr.house.gov/press-releases?ID=137CFE45-CC34-4094-9E40-1A491C1059A0') ORDER BY date;

-- q8 (E8): exact ingested Barr rows in the pivot filing (compared to source LDA filing)
SELECT ci.date, ci.amount, ci.payee_name, ci.honoree_name, ci.contribution_type, ci.contributor_name
FROM senate_contribution_items ci
WHERE ci.filing_uuid='6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4'
  AND (ci.payee_name LIKE '%BARR%' OR ci.honoree_name LIKE '%Barr%') ORDER BY ci.date;
-- E8 outside verify: curl https://lda.senate.gov/api/v1/contributions/6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4/
--   (368 items; row 2025-02-20 $5000.00 "ANDY BARR FOR SENATE, INC." honoree "Rep. Andy Barr" feca — matches)
-- E9 outside verify: https://api.open.fec.gov/v1/committee/C00467571/?api_key=DEMO_KEY
--   ("ANDY BARR FOR SENATE, INC."; candidate_ids H0KY06104 (House KY-06) + S6KY00286 (Senate KY);
--    first_file_date 2009-09-28 — original House cmte redesignated to Senate for 2026)
