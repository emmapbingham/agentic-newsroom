-- mention-money-timing
-- Baseline: for (member, company) pairs with both press mentions and LD-203
-- honoree money, contribution dates are unrelated to mention dates under the
-- null; money landing within +/-60 days of the member speaking the company's
-- name is the ranked deviation (choreography, not just co-occurrence).
-- Requires: derived_client_press_mentions + derived_client_alias_index
--   (in-house registrant match; consultant clients unreachable — bound logged).
-- Money DEDUPED to distinct (contributor, payee, date, amount) tuples per the
-- beat-book LD-203 filer-copy trap. score = dollars landing in-window.
WITH ent_reg AS (
  SELECT DISTINCT a.entity_id, a.canonical_name, r.id AS registrant_id
  FROM derived_client_alias_index a
  JOIN senate_registrants r
    ON UPPER(replace(replace(r.name,'.',''),',','')) = a.alias
  WHERE a.status <> 'rejected_too_generic'
),
money AS (
  SELECT DISTINCT er.entity_id, er.canonical_name, h.bioguide,
         ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
  FROM ent_reg er
  JOIN senate_contribution_filings cf ON cf.registrant_id = er.registrant_id
  JOIN senate_contribution_items ci ON ci.filing_uuid = cf.filing_uuid
  JOIN honoree_member_map h
    ON h.honoree_name = ci.honoree_name AND h.confidence >= 0.9
  WHERE ci.contribution_type = 'feca' AND ci.amount_num > 0
    AND ci.date IS NOT NULL AND length(ci.date) >= 8
),
nearest AS (
  -- each contribution paired with its nearest mention by the same member
  SELECT mo.entity_id, mo.canonical_name, mo.bioguide,
         mo.date AS contrib_date, mo.amount_num,
         min(abs(julianday(mo.date) - julianday(me.date))) AS gap_days
  FROM money mo
  JOIN derived_client_press_mentions me
    ON me.entity_id = mo.entity_id AND me.bioguide_id = mo.bioguide
  WHERE me.date IS NOT NULL
  GROUP BY mo.entity_id, mo.bioguide, mo.date, mo.amount_num,
           mo.contributor_name, mo.payee_name
)
SELECT
  n.canonical_name || ' -> ' || m.official_full AS pair,
  sum(CASE WHEN n.gap_days <= 60 THEN n.amount_num ELSE 0 END) AS score,
  count(CASE WHEN n.gap_days <= 60 THEN 1 END) AS n_contribs_in_window,
  round(min(n.gap_days), 1) AS tightest_gap_days,
  sum(n.amount_num) AS pair_total_usd,
  count(*) AS n_contribs_total,
  m.official_full AS member, m.last_party AS party, m.last_state AS state,
  n.entity_id, n.bioguide
FROM nearest n
JOIN members m ON m.bioguide = n.bioguide
GROUP BY n.entity_id, n.bioguide
HAVING score > 0
ORDER BY score DESC, tightest_gap_days ASC;
