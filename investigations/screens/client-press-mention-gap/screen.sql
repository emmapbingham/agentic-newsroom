-- client-press-mention-gap screen
-- Entity-level "say vs. pay": ranks high-spend Senate lobbying clients by the
-- gap between disclosed lobbying income and how often congressional press
-- releases mention them by name.
--
-- Built via the entity-tracing pipeline (data_manual.md's "Entity graph:
-- Press-release NER -> companies/orgs -> LDA registrants & clients ->
-- government entities lobbied -> committees -> members" lead), taken from
-- the client side rather than full NER: derived_client_alias_index holds
-- alias strings for the 525 Senate clients with >= $1M total 2022-2026Q1
-- income (deterministic suffix-stripping/FKA-splitting, reviewed by 6
-- batched Agent-tool passes -- not raw API calls -- that suggested
-- additional brand/abbreviation aliases and flagged 159 entities'
-- name-spaces as too generic to safely FTS-match, e.g. Apple, Target,
-- Oracle, Delta Air Lines). derived_client_press_mentions holds every
-- (entity, press release) FTS phrase-match hit from the non-generic
-- candidate aliases (9,992 mentions across 264 entities).
--
-- CAVEAT: "quiet" here means "no literal name match in press text," not
-- "no coverage" -- a member could discuss a company's issue (e.g. "Big
-- Tech," "foreign chipmakers") without naming it, and this screen can't see
-- that. High-mention entities like universities (Penn, Northwestern-style
-- institutions) will show press noise for many reasons unrelated to
-- lobbying, so read mention volume as an upper bound on salience, not a
-- clean lobbying-specific signal, especially for entities that are also
-- newsy for other reasons (universities, sports leagues, big consumer
-- brands).
--
-- Run against db/gain.db. Requires: derived_client_alias_index,
-- derived_client_press_mentions.

WITH entity_income AS (
  SELECT entity_id, canonical_name, max(total_income) AS total_income
  FROM derived_client_alias_index
  WHERE status = 'candidate'
  GROUP BY entity_id
),
entity_mentions AS (
  SELECT entity_id, count(*) AS n_mentions,
    count(DISTINCT bioguide_id) AS n_distinct_members,
    max(date) AS most_recent_mention
  FROM derived_client_press_mentions
  GROUP BY entity_id
)
SELECT
  ei.canonical_name,
  ei.total_income,
  coalesce(em.n_mentions, 0)          AS n_mentions,
  coalesce(em.n_distinct_members, 0)  AS n_distinct_members,
  em.most_recent_mention,
  ROUND(ei.total_income / 1000000.0, 2) AS income_millions
FROM entity_income ei
LEFT JOIN entity_mentions em ON em.entity_id = ei.entity_id
WHERE ei.total_income >= 1000000
ORDER BY ei.total_income DESC, n_mentions ASC;
