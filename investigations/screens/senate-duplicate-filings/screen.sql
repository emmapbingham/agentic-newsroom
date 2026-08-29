-- Screen: senate-duplicate-filings  (contrast: source-vs-source / data-vs-law)
-- Baseline: a registrant should file exactly one ORIGINAL quarterly report per
--   (client, quarter). A second filing of the SAME original quarterly type
--   (filing_type IN Q1..Q4) under a different UUID with identical >0 income is a
--   true duplicate. Amendments (1A/2A/3A/4A) and year-end (Y) are SEPARATE filing
--   types and are NOT duplicates — excluded here (an independent verifier showed
--   that counting them inflated this screen ~3x; see the lead memo). ~90% of the
--   survivors are same-day double-submissions.
-- Ranks registrants by total double-counted dollars; UUIDs carried for sourcing.
WITH dup_groups AS (
  SELECT
    f.registrant_id,
    sc.client_id              AS client_group_id,
    f.filing_year,
    f.filing_period,
    f.filing_type,
    f.income_amt,
    count(DISTINCT f.filing_uuid)        AS n_uuids,
    group_concat(DISTINCT f.filing_uuid) AS uuids
  FROM senate_filings f
  JOIN senate_clients sc ON sc.id = f.client_id
  WHERE f.filing_type IN ('Q1','Q2','Q3','Q4')
    AND f.income_amt IS NOT NULL AND f.income_amt > 0
  GROUP BY 1,2,3,4,5,6
  HAVING count(DISTINCT f.filing_uuid) >= 2
)
SELECT
  r.name                                   AS registrant_name,
  d.registrant_id,
  count(*)                                 AS dup_groups,
  sum(d.n_uuids - 1)                       AS excess_filings,
  round(sum((d.n_uuids - 1) * d.income_amt), 0) AS score   -- double-counted $
FROM dup_groups d
JOIN senate_registrants r ON r.id = d.registrant_id
GROUP BY d.registrant_id, r.name
ORDER BY score DESC
LIMIT 50;
