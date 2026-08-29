-- client-mention-honoree-triangle
-- Baseline: a member naming a company in press releases and that company's
-- LD-203 filings reporting FECA contributions honoring that member are each
-- common alone; their co-occurrence at scale on the same (member, company)
-- pair is the deviation being ranked. Most pairs have one channel or the
-- other, not both.
-- Requires: derived_client_press_mentions + derived_client_alias_index
--   (entity->registrant via exact normalized name match = in-house filers
--   only; consultants' clients are NOT reachable this way and that bound is
--   logged, not silent).
-- score = FECA dollars honoring the member from the company's own filings,
-- filtered to pairs the member mentioned >= 2 times.
WITH ent_reg AS (
  SELECT DISTINCT a.entity_id, a.canonical_name, r.id AS registrant_id
  FROM derived_client_alias_index a
  JOIN senate_registrants r
    ON UPPER(replace(replace(r.name,'.',''),',','')) = a.alias
  WHERE a.status <> 'rejected_too_generic'
),
money AS (
  -- DEDUPED: the same LD-203 contribution appears on the registrant's
  -- organization filing AND each lobbyist's individual filing; sum distinct
  -- (contributor, payee, date, amount) tuples per (entity, member) instead
  -- of raw rows (caught 2026-07-06: raw summing inflated SpaceX->Fong
  -- $22.5k to $52.5k). Lobbyists' own personal contributions survive the
  -- dedup as distinct contributor_name tuples — by design.
  SELECT entity_id, canonical_name, bioguide,
         sum(amount_num) AS feca_usd, count(*) AS n_contribs,
         min(date) AS first_contrib, max(date) AS last_contrib
  FROM (
    SELECT DISTINCT er.entity_id, er.canonical_name, h.bioguide,
           ci.contributor_name, ci.payee_name, ci.date, ci.amount_num
    FROM ent_reg er
    JOIN senate_contribution_filings cf ON cf.registrant_id = er.registrant_id
    JOIN senate_contribution_items ci ON ci.filing_uuid = cf.filing_uuid
    JOIN honoree_member_map h
      ON h.honoree_name = ci.honoree_name AND h.confidence >= 0.9
    WHERE ci.contribution_type = 'feca' AND ci.amount_num > 0
  )
  GROUP BY entity_id, bioguide
),
ment AS (
  SELECT entity_id, bioguide_id, count(*) AS n_mentions,
         min(date) AS first_mention, max(date) AS last_mention,
         max(url) AS sample_url
  FROM derived_client_press_mentions
  WHERE bioguide_id IS NOT NULL
  GROUP BY entity_id, bioguide_id
)
SELECT
    mo.canonical_name || ' -> ' || m.official_full AS pair,
    mo.feca_usd AS score,
    me.n_mentions,
    mo.n_contribs,
    m.official_full AS member,
    m.last_party AS party, m.last_state AS state, m.last_type AS chamber,
    m.is_current,
    mo.first_contrib, mo.last_contrib,
    me.first_mention, me.last_mention,
    me.sample_url,
    mo.entity_id, mo.bioguide
FROM money mo
JOIN ment me ON me.entity_id = mo.entity_id AND me.bioguide_id = mo.bioguide
JOIN members m ON m.bioguide = mo.bioguide
WHERE me.n_mentions >= 2
ORDER BY score DESC;
