-- ============ Hanson / VVA chapter (carried over, relabeled q-hanson*) ============

-- q-hanson1: Hanson's post-conviction quarterly record + missing filing uuids (EHanson1)
SELECT * FROM derived_convicted_lobbyist_register
WHERE lobbyist_name = 'HANSON, HAROLD';

-- q-hanson1b: the per-filing detail behind q-hanson1
SELECT f.filing_year, f.filing_type, f.filing_uuid,
       EXISTS (SELECT 1 FROM senate_filing_conviction_disclosures d
                WHERE d.filing_uuid = f.filing_uuid AND d.lobbyist_id = 143691) AS has_disclosure
FROM senate_activity_lobbyists al
JOIN senate_lobbying_activities a ON a.activity_id = al.activity_id
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE al.lobbyist_id = 143691 AND f.filing_type IN ('Q1','Q2','Q3','Q4')
GROUP BY f.filing_uuid ORDER BY f.filing_year, f.filing_type;

-- q-hanson2: corpus baseline — post-conviction gap distribution across all
--            convicted lobbyists (EHanson2)
SELECT lobbyist_name, conviction_date, n_post_quarterlies, n_post_disclosed,
       n_post_missing
FROM derived_convicted_lobbyist_register
WHERE n_post_quarterlies > 0
ORDER BY n_post_missing DESC, n_post_quarterlies DESC;

-- q-hanson3: the disclosure text as filed (EHanson3 — BIS settlement text, dated 2013-07-16)
SELECT DISTINCT date, description
FROM senate_filing_conviction_disclosures WHERE lobbyist_id = 143691;

-- q-hanson4: House-side corroboration — same text under the name key (EHanson4)
SELECT house_filing_id, lobbyist_name, date, description
FROM house_convictions WHERE lobbyist_name LIKE '%Hanson%';

-- q-hanson5 (EHanson5): amendment-cure check — precise, period-matched. ALL VVA
--     filings (registrant 40087) in the three gap PERIODS, any filing type;
--     does any carry the JACK disclosure for lobbyist 143691 (or for anyone)?
--     Result: none. 2023 Q3/Q4 have no amendments; 2025 Q1 has a 1A amendment
--     that carries no disclosure and does not even list Hanson.
SELECT f.filing_uuid, f.filing_type, f.filing_year, f.filing_period,
       EXISTS (SELECT 1 FROM senate_filing_conviction_disclosures d
                WHERE d.filing_uuid=f.filing_uuid AND d.lobbyist_id=143691) AS disc_143691,
       (SELECT COUNT(*) FROM senate_filing_conviction_disclosures d
                WHERE d.filing_uuid=f.filing_uuid) AS disc_any_rows,
       EXISTS (SELECT 1 FROM senate_activity_lobbyists al
                JOIN senate_lobbying_activities a ON a.activity_id=al.activity_id
                WHERE a.filing_uuid=f.filing_uuid AND al.lobbyist_id=143691) AS lists_hanson
FROM senate_filings f
WHERE f.registrant_id = 40087
  AND ( (f.filing_year=2023 AND f.filing_period IN ('third_quarter','fourth_quarter'))
     OR (f.filing_year=2025 AND f.filing_period='first_quarter') )
ORDER BY f.filing_year, f.filing_period, f.filing_type;

-- q-hanson7 (EHanson7): House-side flicker (name-keyed). Every VVA House filing
--     (senate_registrant_id=40087 or org name match); does it list Hanson, and
--     does it carry a 'Harold Hanson' house_convictions row? Result: conviction
--     rows only on the four 2024 quarters; same gap as Senate on 2023 Q3/Q4 and
--     2025 Q1 (plus a 2023 Q2 amendment listing without disclosure).
SELECT f.filing_year, f.filing_period, f.doc_type, f.report_type, f.house_filing_id,
       EXISTS(SELECT 1 FROM house_filing_lobbyists hl
               WHERE hl.house_filing_id=f.house_filing_id
                 AND hl.last_name LIKE '%Hanson%') AS lists_hanson,
       EXISTS(SELECT 1 FROM house_convictions hc
               WHERE hc.house_filing_id=f.house_filing_id
                 AND hc.lobbyist_name LIKE '%Harold Hanson%') AS has_conviction
FROM house_filings f
WHERE (f.senate_registrant_id=40087 OR f.organization_name LIKE '%VIETNAM VETERANS%')
ORDER BY f.filing_year, f.filing_period, f.house_filing_id;

-- q-hanson6: what Hanson lobbies on (context for the write-up)
SELECT f.filing_year, a.general_issue_code_display, a.description
FROM senate_activity_lobbyists al
JOIN senate_lobbying_activities a ON a.activity_id = al.activity_id
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
WHERE al.lobbyist_id = 143691 AND f.filing_type IN ('Q1','Q2','Q3','Q4','RR')
GROUP BY f.filing_uuid ORDER BY f.filing_year;

-- ============ Hunter / VALOON chapter (new, this session) ============

-- q-hunter1 (EHunter1): Hunter's register row — 0/6 post-conviction quarterlies disclosed
SELECT * FROM derived_convicted_lobbyist_register
WHERE lobbyist_name = 'HUNTER, DUNCAN';

-- q-hunter1b (EHunter1): all 7 filings listing Hunter as an active lobbyist,
--            with registrant/client, ordered
SELECT f.filing_uuid, f.filing_type, f.filing_year, f.filing_period,
       r.name AS registrant, c.name AS client
FROM senate_filings f
JOIN senate_registrants r ON r.id = f.registrant_id
JOIN senate_clients c ON c.id = f.client_id
WHERE f.filing_uuid IN (
  SELECT filing_uuid FROM senate_activity_lobbyists al
  JOIN senate_lobbying_activities a ON a.activity_id = al.activity_id
  WHERE al.lobbyist_id = 144165
)
ORDER BY f.filing_year, f.filing_period;

-- q-hunter2 (EHunter2): the disclosure text on Hunter's own RR
SELECT d.filing_uuid, f.filing_type, f.filing_year, f.filing_period, d.date, d.description
FROM senate_filing_conviction_disclosures d
JOIN senate_filings f ON f.filing_uuid = d.filing_uuid
WHERE d.lobbyist_id = 144165
ORDER BY d.date;

-- q-hunter3 (EHunter3): preparer identity across all 7 filings (self-filed, no handoff)
SELECT filing_uuid, filing_type, filing_year, filing_period, posted_by_name, dt_posted
FROM senate_filings
WHERE filing_uuid IN (
  'f760418c-a038-48d1-a6b3-d37173508fff', -- RR (disclosed)
  '4ac94cc9-fa1d-498b-84cc-b23c81e7fbda', -- Q1 2023 (missing)
  '5767af8b-a3b8-4a14-9834-e4a3d8dd4e66', -- Q2 2023 (missing)
  'cbbf216d-9264-4121-8fd1-1084ed381f52', -- Q3 2023 (missing)
  'a2ab1e69-04a9-4326-871e-3a5f914c3c76', -- Q4 2023 (missing)
  '11d51df2-e229-4a84-b28c-9c9faa5fb999', -- Q1 2024 (missing)
  '24be134b-6ad1-4010-93ed-aadff7d38aae'  -- Q2 2024 (missing)
)
ORDER BY dt_posted;
-- result: posted_by_name = 'Duncan Hunter' on all 7 rows.

-- ============ Register-wide context (E-register) ============

-- q-register: the full convicted-lobbyist register (context for case scope)
SELECT lobbyist_name, conviction_date, n_post_quarterlies, n_post_disclosed, n_post_missing
FROM derived_convicted_lobbyist_register
ORDER BY n_post_missing DESC, n_post_quarterlies DESC;

-- Rebuild note: derived_convicted_lobbyist_register is not committed as a
-- standing table in db/gain.db as of this session — rebuild via
-- `python3 scripts/build_derived_convicted_lobbyist_register.py` before
-- re-running q-hanson1/2, q-hunter1, or q-register. Verified against a fresh
-- rebuild 2026-07-07 (18 lobbyists; Hunter 0/6, Hanson 3/7 confirmed
-- unchanged from prior session's figures).

-- q-corpuspct (E-corpuspct): corpus-wide missing-disclosure rate, two levels —
--     (a) instance-level: % of all post-conviction original quarterlies,
--         across all 18 register lobbyists, that lack the disclosure;
--     (b) lobbyist-level: how many of the lobbyists with >=1 post-conviction
--         quarterly have ANY gap at all.
SELECT sum(n_post_quarterlies) AS total_post_q,
       sum(n_post_disclosed)   AS total_disclosed,
       sum(n_post_missing)     AS total_missing,
       round(100.0*sum(n_post_missing)/sum(n_post_quarterlies), 2) AS pct_missing_instance_level,
       count(*)                                           AS n_lobbyists_with_post_q,
       count(*) FILTER (WHERE n_post_missing > 0)          AS n_lobbyists_with_any_gap
FROM derived_convicted_lobbyist_register
WHERE n_post_quarterlies > 0;
-- result (2026-07-07): 887 total post-conviction quarterlies, 877 disclosed,
-- 10 missing -> 1.13% instance-level; 3 of 15 lobbyists (20%) have >=1 gap
-- (Hunter, Hanson, Wohl). Excluding Burkman/Wohl (mega-filer autofill
-- population, EHanson9): 234 total, 9 missing -> 3.85%.

--
-- q-hunter-njf (E-hunter-njf): every Senate filing naming Hunter (lobbyist id
-- 144165), with conviction-disclosure status. 10 rows: the disclosed TREX
-- registration, the 6 undisclosed TREX quarterlies, a second VALOON
-- registration (client NJF WORLDWIDE, 6c0afe7d..., posted 2023-12-01) with NO
-- disclosure, and 2 undisclosed termination filings. 1 of 10 carries it.
SELECT DISTINCT f.filing_uuid, f.filing_type_display, f.filing_year,
       f.filing_period_display, date(f.dt_posted) AS posted, c.name AS client,
       CASE WHEN d.filing_uuid IS NOT NULL
            THEN 'DISCLOSED' ELSE 'no disclosure' END AS disclosure
FROM senate_activity_lobbyists al
JOIN senate_lobbying_activities a ON a.activity_id = al.activity_id
JOIN senate_filings f ON f.filing_uuid = a.filing_uuid
JOIN senate_clients c ON c.id = f.client_id
LEFT JOIN senate_filing_conviction_disclosures d ON d.filing_uuid = f.filing_uuid
WHERE al.lobbyist_id = 144165
ORDER BY f.dt_posted;
