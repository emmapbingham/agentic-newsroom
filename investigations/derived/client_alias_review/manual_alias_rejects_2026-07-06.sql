-- Manual alias-level rejections, 2026-07-06 (session: mention-money triangle
-- gate catch). Apply AFTER build_derived_client_alias_index.py +
-- apply_client_alias_llm_review.py, BEFORE build_derived_client_press_mentions.py:
--   sqlite3 db/gain.db < investigations/derived/client_alias_review/manual_alias_rejects_2026-07-06.sql
--
-- The entity-level LLM review flags whole entities as generic; these are
-- alias-level collisions where the company is real but ONE bare-token alias
-- collides with common congressional-press vocabulary or sitting members'
-- surnames. Multi-word aliases for the same entities remain active, so real
-- mentions are still caught (recall traded for precision; bound is logged).
-- Discovered when the triangle screen's rank-1 pair (VISA -> Daines, $97.5k)
-- turned out to be immigration-visa releases.

UPDATE derived_client_alias_index
SET status = 'rejected_too_generic',
    review_note = coalesce(review_note || ' | ', '')
      || 'manual alias-level reject 2026-07-06: '
      || CASE alias
         WHEN 'VISA'      THEN 'immigration-visa collision (Daines false positive)'
         WHEN 'Miller'    THEN 'sitting-member surname (Reps. Mary/Max/Carol Miller); 3.2k false hits'
         WHEN 'Goldman'   THEN 'sitting-member surname (Rep. Dan Goldman)'
         WHEN 'Schneider' THEN 'sitting-member surname (Rep. Brad Schneider)'
         WHEN 'SEMI'      THEN 'semi-automatic / semiconductor prefix collision'
         WHEN 'Shell'     THEN 'shell companies/corporations collision'
         WHEN 'Penn'      THEN 'ambiguous (Penn State, surnames)'
         WHEN 'Chevron'   THEN 'Chevron-deference doctrine collision (post-Loper releases)'
         WHEN 'INTEL'     THEN 'intel-as-intelligence collision'
         END
WHERE alias IN ('VISA','Miller','Goldman','Schneider','SEMI','Shell','Penn','Chevron','INTEL')
  AND status <> 'rejected_too_generic';
