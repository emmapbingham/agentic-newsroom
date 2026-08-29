-- Imported verbatim from barr-credit-union-cfpb-loop/queries.sql, relabeled
-- q-barr1..q-barr9 to match this case's EBarr1-9. Re-run before citing.
-- See that file for the canonical/original copy (left unchanged there).

-- q-barr1 (EBarr1): the pair from screen run 36 (deduped money + mention count)
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

-- q-barr1b (EBarr1): the three ACU-citing releases (row-level, with urls)
SELECT release_id, date, title, url FROM derived_client_press_mentions
WHERE member_name='Andy Barr' AND canonical_name LIKE 'CREDIT UNION NATIONAL%'
GROUP BY release_id ORDER BY date;

-- q-barr2 (EBarr2): dated timeline with filing_uuids
SELECT ci.date, ci.amount_num, ci.payee_name, ci.filing_uuid, cf.filer_type
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
JOIN members m ON m.bioguide=h.bioguide
WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0
  AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND cf.filer_type='organization'
ORDER BY ci.date;

-- q-barr3 (EBarr3): all credit-union registrants honoring Barr (deduped)
SELECT r.name, sum(d.amount_num) usd FROM (
  SELECT DISTINCT cf.registrant_id rid, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  JOIN members m ON m.bioguide=h.bioguide
  WHERE m.official_full='Andy Barr' AND ci.contribution_type='feca' AND ci.amount_num>0) d
JOIN senate_registrants r ON r.id=d.rid
WHERE r.name LIKE '%CREDIT UNION%' GROUP BY r.id;

-- q-barr4 (EBarr4): base rate — ACU's full honoree footprint
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

-- q-barr4b (EBarr4): base-rate distribution stats
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

-- q-barr4c (EBarr4): Barr's rank within that footprint
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
WHERE m.official_full='Andy Barr';

-- q-barr5 (EBarr5): every registrant honoring Barr, ranked + dated around 2025-02-20
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

-- q-barr6 (EBarr6): does ACU's lobbying name Barr's bills?
SELECT f.filing_year, f.filing_period, a.general_issue_code_display, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%UDAAP%' OR a.description LIKE '%TABS%' OR a.description LIKE '%Barr%');

-- q-barr5b (EBarr5): every LD-203 row to an "...FOR SENATE..." payee honoring Barr, by date
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

-- q-barr6b (EBarr6): the named-bill snippet in ACU's 2025 Senate lobbying activity descriptions
SELECT substr(a.description, instr(a.description,'Support Taking Account')-40, 380) AS bills
FROM senate_lobbying_activities a JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.filing_uuid='579f0209-4eac-4933-b277-3978e56896a8' AND a.description LIKE '%UDAAP%' LIMIT 1;

-- q-barr7 (EBarr7): full text of the three ACU-citing releases (endorsement quotes)
SELECT date, title, text FROM press_releases WHERE url IN (
  'https://barr.house.gov/press-releases?ID=B168D678-0C8F-4766-B711-1C51D5C74372',
  'https://barr.house.gov/press-releases?ID=0BF254FA-1F21-4097-9427-787F8B587593',
  'https://barr.house.gov/press-releases?ID=137CFE45-CC34-4094-9E40-1A491C1059A0') ORDER BY date;

-- q-barr8 (EBarr8): exact ingested Barr rows in the pivot filing
SELECT ci.date, ci.amount, ci.payee_name, ci.honoree_name, ci.contribution_type, ci.contributor_name
FROM senate_contribution_items ci
WHERE ci.filing_uuid='6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4'
  AND (ci.payee_name LIKE '%BARR%' OR ci.honoree_name LIKE '%Barr%') ORDER BY ci.date;
-- E8 outside verify: curl https://lda.senate.gov/api/v1/contributions/6acc01c1-ff04-4b65-bbbb-84b5ea0d57c4/
-- E9 outside verify: https://api.open.fec.gov/v1/committee/C00467571/?api_key=DEMO_KEY

-- ============ New queries for this case start here (per-member replication) ============

-- q1 (E-scout source, not yet independently re-derived): screen run 36 full result
-- see investigations/screens/client-mention-honoree-triangle/screen.sql

-- q1 (E0): corrected screen re-derivation, CSV mode, ACU entity only (see E0 caveat re: -mode column bug)
-- (full query in evidence.md E0 — canonical form; re-run in `sqlite3 -csv -header`, never -mode column with .width)

-- === Per-member replication (E1-E9). Money queries follow the q-barr1/q-barr2 template
-- with h.bioguide swapped and cf.registrant_id = 11322 (ACU) instead of a LIKE match.

-- q-cramer1 (E1 money):
SELECT DISTINCT ci.contributor_name, ci.payee_name, ci.date, ci.amount_num, ci.filing_uuid
FROM senate_contribution_items ci
JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
WHERE h.bioguide='C001096' AND ci.contribution_type='feca' AND ci.amount_num>0
  AND cf.registrant_id=11322 ORDER BY ci.date;

-- q-cramer2 (E1 lobbying): named-bill text, S.3992 -> S.2486 renumbering
SELECT f.filing_uuid, f.filing_year, f.filing_period,
  substr(a.description, max(1,instr(a.description,'Protecting Access to Credit')-40), 200) snippet
FROM senate_lobbying_activities a JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND a.description LIKE '%Protecting Access to Credit for Small Businesses%'
ORDER BY f.filing_year, f.filing_period;

-- q-scott1 (E2 money): same template as q-cramer1, h.bioguide='S001184'
-- q-scott2 (E2 lobbying): same as q-cramer2 (shared bill)

-- q-britt1 (E3 money): same template, h.bioguide='B001319'
-- q-britt2 (E3 lobbying):
SELECT f.filing_uuid, f.filing_year, f.filing_period FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND a.description LIKE '%Community Bank Relief%';

-- q-emmer1 (E4 money): same template, h.bioguide='E000294'
-- q-emmer2 (E4 lobbying):
SELECT f.filing_uuid, f.filing_year, f.filing_period FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND a.description LIKE '%Anti-CBDC Surveillance State%';

-- q-fitz1 (E5 money): same template, h.bioguide='F000471'
-- q-fitz2 (E5 lobbying, 3 bills):
SELECT f.filing_uuid, f.filing_year, f.filing_period, 'CFPB Accountable' bill FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid WHERE f.registrant_id=11322 AND a.description LIKE '%CFPB Accountable%'
UNION ALL
SELECT f.filing_uuid, f.filing_year, f.filing_period, 'HUMPS (Uncertain Methods and Practices)' FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid WHERE f.registrant_id=11322 AND a.description LIKE '%Uncertain Methods and Practices%'
UNION ALL
SELECT f.filing_uuid, f.filing_year, f.filing_period, 'Expanding Access to Lending Options' FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid WHERE f.registrant_id=11322 AND a.description LIKE '%Expanding Access to Lending Options%';

-- q-budd1 (E6 money): same template, h.bioguide='B001305'
-- q-budd2 (E6 lobbying): reuses q-cramer2 (shared SBA bill); debit/Fed bill NOT isolated
--   (search terms "debit"/"Federal Reserve"/"interchange" too generic vs. ACU boilerplate; unconfirmed not refuted)

-- q-beatty1 (E7 money): same template, h.bioguide='B001281'
-- q-beatty2 (E7 lobbying, NEGATIVE result — zero rows each):
SELECT count(*) FROM senate_lobbying_activities a JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND (a.description LIKE '%Fair Hiring%' OR a.description LIKE '%5911%' OR a.description LIKE '%justice-involved%');
-- also checked NAFCU-legacy registrant (id via: SELECT id FROM senate_registrants WHERE name LIKE '%FEDERALLY-INSURED CREDIT UNIONS%'), zero hits there too.

-- q-vargas1 (E8 money): same template, h.bioguide='V000130'
-- q-vargas2 (E8 lobbying):
SELECT f.filing_uuid, f.filing_year, f.filing_period FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND a.description LIKE '%Credit Union Board Modernization%'
ORDER BY f.filing_year, f.filing_period;

-- q-gonzalez1 (E9 money): same template, h.bioguide='G000581'
-- q-gonzalez2 (E9 lobbying):
SELECT f.filing_uuid, f.filing_year, f.filing_period FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id=11322 AND a.description LIKE '%Veterans Member%Business Loan%'
ORDER BY f.filing_year, f.filing_period;

-- q-rank1 (E10, the kill query): full screen-36 population, un-filtered by client,
-- ranked by count of distinct members showing the money+mention pattern
WITH ent_reg AS (
  SELECT DISTINCT a.entity_id, a.canonical_name, r.id AS registrant_id
  FROM derived_client_alias_index a
  JOIN senate_registrants r
    ON UPPER(replace(replace(r.name,'.',''),',','')) = a.alias
  WHERE a.status <> 'rejected_too_generic'
),
money AS (
  SELECT entity_id, canonical_name, bioguide, sum(amount_num) AS feca_usd
  FROM (
    SELECT DISTINCT er.entity_id, er.canonical_name, h.bioguide,
           ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
    FROM ent_reg er
    JOIN senate_contribution_filings cf ON cf.registrant_id = er.registrant_id
    JOIN senate_contribution_items ci ON ci.filing_uuid = cf.filing_uuid
    JOIN honoree_member_map h ON h.honoree_name = ci.honoree_name AND h.confidence >= 0.9
    WHERE ci.contribution_type = 'feca' AND ci.amount_num > 0
  )
  GROUP BY entity_id, bioguide
),
ment AS (
  SELECT entity_id, bioguide_id, count(*) AS n_mentions
  FROM derived_client_press_mentions WHERE bioguide_id IS NOT NULL
  GROUP BY entity_id, bioguide_id
),
full_screen AS (
  SELECT mo.canonical_name, mo.bioguide, mo.feca_usd, me.n_mentions
  FROM money mo JOIN ment me ON me.entity_id = mo.entity_id AND me.bioguide_id = mo.bioguide
  WHERE me.n_mentions >= 2
)
SELECT canonical_name, count(DISTINCT bioguide) AS n_members, sum(feca_usd) total_usd,
       RANK() OVER (ORDER BY count(DISTINCT bioguide) DESC) rnk
FROM full_screen GROUP BY canonical_name ORDER BY rnk;

-- q-rank2 (E10, Barr's second bench): Barr's own pairs across all clients, not just ACU
-- (uses same CTEs as q-rank1, filtered WHERE bioguide = 'B001282' on full_screen)

-- q-e12 (E12): full ACU honoree population vs. mention population -- the counterfactual
WITH acu_money AS (
  SELECT DISTINCT h.bioguide, ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM senate_contribution_items ci
  JOIN senate_contribution_filings cf ON cf.filing_uuid=ci.filing_uuid
  JOIN honoree_member_map h ON h.honoree_name=ci.honoree_name AND h.confidence>=0.9
  WHERE ci.contribution_type='feca' AND ci.amount_num>0
    AND cf.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
),
paid AS (
  SELECT bioguide, sum(amount_num) usd, count(*) n_items FROM acu_money GROUP BY bioguide
),
mentions AS (
  SELECT bioguide_id AS bioguide, count(*) n_mentions
  FROM derived_client_press_mentions
  WHERE entity_id IN (644,645) AND bioguide_id IS NOT NULL
  GROUP BY bioguide_id
)
-- (a) summary counts: mentioned-at-all (27) vs. never-mentioned (500)
SELECT
  count(*) AS n_paid_total,
  sum(CASE WHEN mentions.bioguide IS NOT NULL THEN 1 ELSE 0 END) AS n_paid_with_any_mention,
  sum(CASE WHEN mentions.bioguide IS NULL THEN 1 ELSE 0 END) AS n_paid_zero_mentions
FROM paid LEFT JOIN mentions ON mentions.bioguide = paid.bioguide;
-- (b) top unmentioned-but-paid members (swap WHERE clause to mentions.bioguide IS NOT NULL for the
--     27-member mentioned list, or add AND mentions.n_mentions=2 to find the 2 non-bench >=2 pairs)
-- SELECT m.official_full, m.last_party, m.last_state, paid.usd, mentions.n_mentions
-- FROM paid JOIN members m ON m.bioguide=paid.bioguide
-- LEFT JOIN mentions ON mentions.bioguide=paid.bioguide
-- WHERE mentions.bioguide IS NULL ORDER BY paid.usd DESC;

-- q-e12-huizenga (E12): spot check -- is Huizenga (Vargas's E8 cosponsor) mentioned or paid?
SELECT bioguide_id, entity_id, count(*) FROM derived_client_press_mentions
WHERE bioguide_id = (SELECT bioguide FROM members WHERE official_full LIKE '%Huizenga%')
GROUP BY entity_id;
SELECT p.date, p.title, p.url FROM press_releases p
WHERE p.bioguide_id = (SELECT bioguide FROM members WHERE official_full LIKE '%Huizenga%')
ORDER BY p.date;

-- q-e12b (E12, caveat only -- NOT a safe source without per-bill Congress-session resolution):
-- raw bill-number token extraction from ACU's own lobbying-activity text (168 distinct H.R./S.
-- tokens found; bill numbers repeat across Congresses, unfiltered here -- see E12 caveats)
-- run via python3, not SQL: extract regex \b(H\.?R\.?\s?\d{1,5}|S\.?\s?\d{1,5})\b from
-- `SELECT DISTINCT description FROM senate_lobbying_activities a JOIN senate_filings f
--  ON f.filing_uuid=a.filing_uuid WHERE f.registrant_id IN (SELECT id FROM senate_registrants
--  WHERE name LIKE 'CREDIT UNION NATIONAL%')`

-- q-e13 (E13): should Peters/Young be added to the bench? -- deduped mention count first
-- (repeats E0's dedup, which E12's quick query skipped -- this is the correct count)
SELECT bioguide_id, count(DISTINCT url) AS n_mentions_deduped
FROM derived_client_press_mentions
WHERE entity_id IN (644,645)
  AND bioguide_id IN ('P000595','Y000064')  -- Peters, Young
GROUP BY bioguide_id;

-- q-e13b: Peters -- ACU lobbying text names his flagship bill?
SELECT f.dt_posted, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%housing financial literacy%' OR a.description LIKE '%Housing Financial Literacy%');
-- 4 filings name "Housing Financial Literacy Act of 2021 (H.R. 1395)" verbatim

-- q-e13c: Young -- ACU lobbying text names his flagship bill? (zero matches)
SELECT count(*) FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%IRS%surveillance%' OR a.description LIKE '%taxpayer privacy%'
       OR a.description LIKE '%Prevent Weaponization%');

-- q-e15 (E15): resolve Vargas/Gonzalez's apparent pre-bill lobbying -- what bill number does
-- ACU's EARLIEST lobbying filing for each actually cite?
SELECT f.dt_posted, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND a.description LIKE '%Credit Union Board Modernization%'
ORDER BY f.dt_posted LIMIT 1;
-- excerpt around "Credit Union Board Modernization" in the earliest row names "H.R. 6889" --
-- a 117th-Congress number, NOT the 118th H.R.582 already in bench_bill_dates.csv (E8).
-- CORRECTED 2026-07-09 verify pass: same filing separately names "H.R. 7003, Expanding
-- Financial Access to Underserved Communities Act" -- a different, unrelated bill; an
-- earlier pass here misread H.R.7003 as the Credit Union Board Modernization Act's number.
SELECT f.dt_posted, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%Veterans Member%Business Loan%' OR a.description LIKE '%Veterans Members%Business Loan%')
ORDER BY f.dt_posted LIMIT 1;
-- earliest row (2022-04-20) names "Veterans Member Business Loan Act" in 117th-era company
-- (S.2857/S.3715/S.3813 neighbors) -- 117th bill number not yet resolved via Congress.gov (E9 gap)

-- q-e14 (E14): Peters added to the bench -- bill-lineage resolution (not SQL, Congress.gov API)
-- run via python3: paginate member/P000595/sponsored-legislation (913 bills total, limit=250,
-- offset 0/250/500/750) filtering congress==118 and title containing "housing" to find S.4542
-- (his 2024 press release's actual bill); bill/117/hr/1395/relatedbills confirms S.1490 (117th,
-- Peters-sponsored) is the Senate companion to Beatty's H.R.1395 -- NOT the same bill as Peters'
-- 2024 release, despite an identical short title. Requires CONGRESS_GOV_API_KEY in .env.
-- ACU lobbying-text re-check against the corrected lineage: same q-e13b query, confirms 4 filings
-- (2022 Q2 - 2023 Q1, i.e. S.1490's life) and zero filings naming/dated to S.4542's life (2024+).

-- q-e7-correction (E7, revised 2026-07-09): Beatty's second bill, editor-identified --
-- ACU lobbying text names it (unlike Fair Hiring in Banking Act, q-beatty2's zero-match bill)
SELECT f.dt_posted, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND (a.description LIKE '%Mentor Prot%g%' OR a.description LIKE '%3709%');
-- 1 match: 2026 Q1 filing (posted 2026-04-14) states "Support Advancing the Mentor-Protege
-- Program for Small Financial Institutions Act (H.R. 3709)" verbatim.
-- Press-release full text confirms a genuine named ACU quote (Jim Nussle, ACU President/CEO),
-- not a roster mention -- pull via: SELECT text FROM press_releases WHERE bioguide_id='B001281'
-- AND date='2025-06-05' (text column, not just title/url -- E7's original pass only checked title).
-- Bill confirmed via Congress.gov: 119th HR.3709, sole sponsor Beatty, introduced 2025-06-04
-- (one day before her press release, matching the bench's dominant same-day/next-day pattern).

-- q-e16 (E16): systematic pass -- every press release with no bill within +/-7 days, across all
-- 11 members (run via python3, not SQL, against the derived CSVs -- computes min date-gap per
-- release against bench_bill_dates.csv; then pull full press_releases.text for each flagged one)
-- SELECT text FROM press_releases WHERE bioguide_id=? AND date=? -- for each of the 6 flagged rows

-- q-e16b (E16): Budd's new bill -- ACU lobbying text names the Secure Payments Act?
SELECT f.dt_posted, a.description FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
WHERE f.registrant_id IN (SELECT id FROM senate_registrants WHERE name LIKE 'CREDIT UNION NATIONAL%')
  AND a.description LIKE '%Secure Payments Act%'
ORDER BY f.dt_posted;
-- 3 matches (2024 Q3-Q4), citing "Secure Payments Act (H.R. 7531; S. 4570)" verbatim.
-- Bill confirmed via Congress.gov: 118th S.4570, sole sponsor Budd, introduced 2024-06-18 --
-- same day as his press release. House companion H.R.7531 sponsored by Rep. Luetkemeyer (not
-- a bench member) -- confirms the same-day pattern from the Senate side, which is the bench's
-- own chamber of record (ACU's lobbying filings searched here are Senate LD-1 filings).

-- q-e17 (E17): Britt's conditional endorsement -- pull the full quote text, not just title/url
SELECT text FROM press_releases WHERE bioguide_id='B001319' AND date='2026-02-13'
  AND title LIKE '%Protect Community Banks%';
-- contains Scott Simpson (ACU President/CEO) quote: "This legislation is an important step
-- forward. But the only real long-term solution is full repeal of the Durbin Amendment..."
-- Systematic check: did ANY other bench member's press release carry similar qualifying language?
-- (run via python3 against bench_press_releases.csv joined to press_releases.text, searching for
-- "important step"/"long-term solution"/"full repeal"/"falls short"/"doesn't go far enough" --
-- Britt's is the only hit across all 28 releases / 11 members.)

-- q-e18 (E18): full-text read of all 28 press releases -- run via python3, not SQL:
-- for each row in bench_press_releases.csv, pull press_releases.text via
-- (bioguide_id, date, url), search for "America's Credit Unions"/"America’s Credit Unions"/
-- "ACU"/"CUNA" substrings, print the surrounding ~450-char window for each hit. Confirms Britt's
-- E17 caveat is the only qualified/conditional quote in the bench (17 other quotes, all
-- unqualified support); surfaces the "Scott Simpson" name collision (ACU's national President/CEO
-- vs. the California/Nevada Credit Union Leagues' President/CEO, same name, different orgs, in
-- Britt/Gonzalez's releases vs. Vargas's 2025-02-05 release respectively); confirms Fitzgerald's
-- 2025-02-26 two-bill release only has an ACU quote for the already-tracked bill (SOPRA, the
-- second bill in that release, gets no ACU mention and isn't credit-union subject matter).

-- q-e16c (E16): Vargas's uncredited cosponsorship -- confirmed via Congress.gov API, not SQL:
-- bill/118/hr/6933/cosponsors lists Vargas as an ORIGINAL cosponsor, sponsorshipDate=2024-01-10,
-- same day as his 2024-01-10 press release. H.R.6933 is Fitzgerald's Expanding Access to Lending
-- Options Act (already tracked, E5) -- ACU's 9 lobbying filings for this bill were already
-- counted under Fitzgerald; this confirms Vargas has a real, second bill-relationship via the
-- same shared bill, not a new bill number to add to the corpus.
