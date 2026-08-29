-- insurance-jurisdiction-no-press-lift: cited queries
-- All numbers in evidence.md trace back to a query here or to
-- analysis/ins_committee_press_share.py (which wraps several of these
-- with the case-local BROAD_INS_KEYWORDS override -- see case.md
-- Methodology section for why the override exists).

-- q1: bare-word "insurance" count corpus-wide (the recall-bug denominator)
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%insurance%';

-- q2: narrow (shared, in-production) ISSUE_KEYWORDS['INS'] match count
SELECT count(*) FROM press_releases
WHERE lower(text) LIKE '%insurance industry%'
   OR lower(text) LIKE '%insurance regulation%'
   OR lower(text) LIKE '%insurer%'
   OR lower(text) LIKE '%insurance premium%';

-- q3: broad (case-local override) INS keyword match count
SELECT count(*) FROM press_releases
WHERE lower(text) LIKE '%insurance industry%' OR lower(text) LIKE '%insurance regulation%'
   OR lower(text) LIKE '%insurer%' OR lower(text) LIKE '%insurance premium%'
   OR lower(text) LIKE '%insurance compan%' OR lower(text) LIKE '%insurance market%'
   OR lower(text) LIKE '%insurance rate%' OR lower(text) LIKE '%homeowners insurance%'
   OR lower(text) LIKE '%property insurance%' OR lower(text) LIKE '%auto insurance%'
   OR lower(text) LIKE '%flood insurance%' OR lower(text) LIKE '%life insurance%'
   OR lower(text) LIKE '%disability insurance%' OR lower(text) LIKE '%title insurance%'
   OR lower(text) LIKE '%casualty insurance%';

-- q4: recall-audit method, generalized -- see scripts/audit_issue_keyword_recall.py
-- for the full 26-code run. Single-code version:
-- SELECT
--   (SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%<bare_word>%') as bare_n,
--   (SELECT count(*) FROM press_releases WHERE <keyword LIKE clauses OR'd together>) as matched_n;

-- q5: committee roster-attributed press releases, point-in-time (NOT
-- member_committees, which is current-Congress-only and would misattribute
-- pre-2025 releases to members who weren't seated on the committee then)
SELECT p.text
FROM press_releases p
JOIN member_committees_history h ON h.bioguide = p.bioguide_id
WHERE h.committee_id = ?  -- 'HSBA04' or 'SSBK04'
  AND h.valid_from <= p.date AND (h.valid_to IS NULL OR h.valid_to > p.date);

-- q6: the committee's other primary jurisdiction issue code (for the
-- within-committee contrast) -- committee_issue_jurisdiction, weight='primary'
SELECT committee_id, issue_code, weight
FROM committee_issue_jurisdiction
WHERE committee_id IN ('HSBA04', 'SSBK04') AND weight = 'primary';

-- q7: INS lobbying scale (money side of the say-vs-pay contrast)
SELECT sum(total_income_apportioned) as income, sum(total_activities) as activities
FROM derived_issue_quarter_volume_press
WHERE issue_code = 'INS';

-- q8: dollar-normalized press-per-$1M-lobbied, for the "is insurance just
-- inherently quiet" boring-explanation check -- issue codes with >$50M
-- apportioned income, ranked by press-releases-per-million-dollars-lobbied
SELECT issue_code, issue_name, sum(total_income_apportioned) as income
FROM derived_issue_quarter_volume_press
WHERE issue_code NOT IN ('GOV','SCI')  -- GOV catch-all, SCI has no press keyword coverage
GROUP BY issue_code
HAVING income > 50000000
ORDER BY income DESC;
-- (press count per code computed separately per-code's own ISSUE_KEYWORDS,
-- except INS which uses the broad override -- see analysis script)
