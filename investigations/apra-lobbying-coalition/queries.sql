-- apra-lobbying-coalition queries
-- Run against db/gain.db (read-only).

-- q1: lobbying activity volume on named federal privacy bills, by year (Senate)
-- Carried over from the fish-for-leads scout pass; re-run to verify E1.
SELECT sf.filing_year, count(*) FROM senate_filings sf
JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
WHERE sla.general_issue_code = 'CPI'
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
  AND sf.filing_year BETWEEN 2022 AND 2026
GROUP BY sf.filing_year
ORDER BY 1;

-- q1b: same, House side
SELECT hf.filing_year, count(*) FROM house_filings hf
JOIN house_activities ha ON ha.house_filing_id = hf.house_filing_id
WHERE ha.issue_area_code = 'CPI'
  AND (
    lower(ha.description) LIKE '%american privacy rights act%'
    OR lower(ha.description) LIKE '%consumer online privacy rights act%'
    OR lower(ha.description) LIKE '%american data privacy%'
    OR lower(ha.description) LIKE '%adppa%'
  )
  AND hf.filing_year BETWEEN 2022 AND 2026
GROUP BY hf.filing_year
ORDER BY 1;

-- q1c: distinct Senate clients on the same match
SELECT c.name, count(*) n FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE sla.general_issue_code = 'CPI'
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
GROUP BY c.name
ORDER BY n DESC;

-- q2: press releases naming the bills directly
SELECT release_id, title, url, date, bioguide_id
FROM press_releases
WHERE lower(text) LIKE '%american privacy rights act%'
   OR lower(text) LIKE '%american data privacy%'
   OR lower(text) LIKE '%adppa%'
ORDER BY date;

-- q2b: broader "federal/comprehensive/national privacy" press search
SELECT release_id, title, url, date, bioguide_id
FROM press_releases
WHERE lower(text) LIKE '%federal data privacy%'
   OR lower(text) LIKE '%comprehensive privacy%'
   OR lower(text) LIKE '%national privacy%'
ORDER BY date;

-- q2c: E2 revision (2026-07-08) -- everything NOT caught by q2/q2b that
-- mentions the bare "data privacy" substring. 327 total minus this filter's
-- 37 overlap = 290 read manually (by a forked agent) for on-topic vs.
-- off-topic; 13 were found genuinely on-topic (see evidence.md E2 revision
-- and derived/e2_revision_ontopic.csv for the list with rationale).
SELECT release_id, title, url, date, bioguide_id
FROM press_releases
WHERE lower(text) LIKE '%data privacy%'
  AND NOT (
    lower(text) LIKE '%american privacy rights act%'
    OR lower(text) LIKE '%consumer online privacy rights act%'
    OR lower(text) LIKE '%data privacy act%'
    OR lower(text) LIKE '%american data privacy%'
    OR lower(text) LIKE '%adppa%'
    OR lower(text) LIKE '%federal data privacy%'
    OR lower(text) LIKE '%comprehensive privacy%'
    OR lower(text) LIKE '%national privacy%'
  )
ORDER BY date;
-- result: 290 rows. Manual read-through found 13 on-topic (see CSV above),
-- 277 off-topic (dominated by 2025 DOGE/Musk data-access fight, reproductive
-- health, TikTok, COPPA/KOSA family -- see evidence.md for full breakdown).

-- q3: advocacy-org full activity text (not keyword-restricted) on CPI
SELECT c.name, sla.description
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE sla.general_issue_code = 'CPI'
  AND c.name IN (
    'ELECTRONIC FRONTIER FOUNDATION',
    'FIGHT FOR THE FUTURE INC.',
    'CENTER FOR HUMANE TECHNOLOGY',
    'DUE PROCESS INSTITUTE',
    'AVAAZ FOUNDATION',
    "DAVID'S LEGACY FOUNDATION",
    'CHILDREN AND SCREENS: INSTITUTE OF DIGITAL MEDIA & CHILD DEVELOPMENT',
    'SANDY HOOK PROMISE ACTION FUND (FKA SANDY HOOK PROMISE FOUNDATION)'
  )
ORDER BY c.name;

-- q4: E5 -- roster entity count, raw client.id vs raw client.name vs
-- manually-deduplicated entity (see analysis/build_roster.py). Confirms the
-- E1 "101 clients" figure was a client_id count, not a distinct-entity count.
SELECT count(DISTINCT c.id)   AS n_client_ids,
       count(DISTINCT c.name) AS n_client_names
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE sla.general_issue_code = 'CPI'
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  );
-- result: 101 client_ids, 84 client_names -> 71 after manual variant-collapsing
-- (analysis/build_roster.py); true distinct-entity count is 71, not 101.

-- q5: E5 -- position-signal keyword scan across the full 509-row roster text.
-- Only 8 raw client names (of 84) contain any of oppose/support/preemption/
-- private right of action/concern/favor language at all; most of those hits
-- are generic pro-business framing unrelated to APRA specifically (see
-- evidence.md E5 for the read-through). Real ADPPA-specific position
-- language found in only 2 deduplicated entities: SIIA and American
-- Advertising Federation.
SELECT c.name, sla.description
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE sla.general_issue_code = 'CPI'
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
  AND (
    lower(sla.description) LIKE '%oppose%'
    OR lower(sla.description) LIKE '%support%'
    OR lower(sla.description) LIKE '%private right of action%'
    OR lower(sla.description) LIKE '%preemption%'
    OR lower(sla.description) LIKE '%preempt%'
    OR lower(sla.description) LIKE '%concern%'
    OR lower(sla.description) LIKE '%favor %'
  );

-- q6: E6 -- scale baseline, corrected method (see evidence.md E6 for why
-- a CPI-issue-code-only filter undercounts). Match on ANY issue code, but
-- require length(description) < 600 to keep only focused bill-specific
-- mentions (excludes omnibus filings that list 50+ unrelated bills in one
-- field). Full script + manual entity-dedup: analysis/build_corrected_roster.py
-- -> derived/roster_corrected_deduplicated.csv.
SELECT count(*) n_activities, count(DISTINCT c.id) n_client_ids,
       count(DISTINCT c.name) n_client_names
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
  AND length(sla.description) < 600;
-- result: 2,545 activities / 399 raw client_names -> 345 verified distinct
-- entities after manual dedup (analysis/build_corrected_roster.py)

-- q6b/c/d: same method applied to three comparison bills (AICOA/Open App
-- Markets Act, KOSA, RESTRICT Act) -- entity counts for these three are
-- still mechanical-normalization estimates, not manually verified like q6.
SELECT count(*) n_activities, count(DISTINCT c.id) n_clients
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE (lower(sla.description) LIKE '%american innovation and choice online act%'
    OR lower(sla.description) LIKE '%open app markets act%')
  AND length(sla.description) < 600;
-- result: 902 activities / ~104 entities (mechanical estimate)

SELECT count(*) n_activities, count(DISTINCT c.id) n_clients
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE (lower(sla.description) LIKE '%kids online safety act%'
    OR lower(sla.description) LIKE '%kosa%')
  AND length(sla.description) < 600;
-- result: 1,292 activities / ~149 entities (mechanical estimate)

SELECT count(*) n_activities, count(DISTINCT c.id) n_clients
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE lower(sla.description) LIKE '%restrict act%'
  AND length(sla.description) < 600;
-- result: 99 activities / ~24 entities (mechanical estimate)

-- q8: E8 -- re-run of E5's position-language keyword scan, now against the
-- FULL corrected roster (any issue code, length < 600 -- E6/E7's filter),
-- not the superseded 71-entity CPI-only roster E5 used.
-- Script: analysis/build_position_read.py -> derived/position_read_candidates.csv
SELECT c.name, sf.filing_year, sla.general_issue_code, sla.description
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_clients c ON c.id = sf.client_id
WHERE length(sla.description) < 600
  AND (
    lower(sla.description) LIKE '%american privacy rights act%'
    OR lower(sla.description) LIKE '%consumer online privacy rights act%'
    OR lower(sla.description) LIKE '%american data privacy%'
    OR lower(sla.description) LIKE '%adppa%'
  )
  AND (
    lower(sla.description) LIKE '%oppose%'
    OR lower(sla.description) LIKE '%support%'
    OR lower(sla.description) LIKE '%private right of action%'
    OR lower(sla.description) LIKE '%preemption%'
    OR lower(sla.description) LIKE '%preempt%'
    OR lower(sla.description) LIKE '%concern%'
    OR lower(sla.description) LIKE '%favor %'
  )
ORDER BY c.name;
-- result: 222 rows / 36 distinct raw client names (up from E5's 8/2).
-- Manual read-through (evidence.md E8) found the 600-char cutoff itself
-- excludes E5's own two headline entities' real position statements: American
-- Advertising Federation's ADPPA position row is 780-1038 chars, SIIA's core
-- CPI-issue-code row is 811 chars -- both over the cutoff, both survived only
-- because SIIA had one shorter cross-posted EDU-code row (589 chars).

-- q8b: does the SAME position-signal keyword match, with NO length cutoff,
-- pull in AAF/SIIA's full statements plus any other verbose position rows
-- that q8's <600 filter silently drops? Not yet run -- needed before E8's
-- entity list can be called complete rather than a lower bound.

-- q6-recheck (2026-07-15, pre-submission audit): re-ran all four comparison
-- bills under the IDENTICAL corrected filter (specific bill-name substrings +
-- length<600, no CPI restriction) so the "largest of four" ranking rests on a
-- consistent method. Results:
--   APRA/ADPPA family : 1,950 activities / 455 raw client_ids (319 manual-dedup entities)
--   KOSA              : 1,292 activities / 220 client_ids
--   AICOA/Open App    :   902 activities / 146 client_ids
--   RESTRICT Act      :    99 activities /  31 client_ids
-- Ranking APRA > KOSA > AICOA > RESTRICT holds cleanly. The old H.R.1165
-- contamination is gone: the fixed filter no longer contains "%data privacy
-- act%", so H.R.1165 ("Data Privacy Act of 2023") no longer qualifies on its
-- own. 145 of the 1,950 APRA activities also name H.R.1165 in a multi-bill
-- list, but each independently qualifies by naming ADPPA/APRA -- legitimate
-- multi-bill filings, not contamination.
