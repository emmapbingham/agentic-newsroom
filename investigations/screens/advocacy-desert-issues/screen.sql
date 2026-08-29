-- advocacy-desert-issues screen
-- For each issue code, counts distinct 2025 Senate lobbying clients that are
-- confirmed public-interest/consumer/environmental advocacy registrants vs.
-- everyone else. Flags issue codes with heavy registered-lobbying volume and
-- near-zero (or zero) advocacy presence -- a K-Street-vs-public imbalance.
--
-- Origin: built ad hoc in the maha-gras-capture case (evidence.md E8) as a
-- generalization of the GRAS/MAHA finding that industry lobbying on GRAS
-- reform has ~25 registered clients vs. 3 advocacy-side registrants, and zero
-- MAHA-branded ones. Promoted to a reusable screen 2026-07-02.
--
-- Contrast type: population-structure (composition of who lobbies, not volume
-- or trend). Baseline: presence of a manually-curated advocacy roster.
--
-- IMPORTANT -- the advocacy list is a hand-verified roster, NOT a name-pattern
-- match. A first attempt used keywords ("coalition"/"foundation"/"center for")
-- and failed: it caught industry-funded groups with advocacy-sounding names
-- ("Data Center Coalition," "Coalition of Manufacturers of Smoking
-- Alternatives") at least as often as genuine public-interest orgs. Extend
-- this list only with orgs you can personally verify are not industry-funded
-- astroturf -- e.g. "Diabetes Patient Advocacy Coalition" and "Federation of
-- Americans for Consumer Choice" both sound like patient/consumer groups but
-- are industry trade associations on closer inspection (see maha-gras-capture
-- evidence.md E8 caveats).
--
-- What this screen can and cannot show:
--   CAN show: which issue codes have heavy lobbying with near-zero registered
--     public-interest counter-presence (a lead-generation signal).
--   CANNOT show: whether "the public" won or lost any fight in that area --
--     public pressure that never registers as LDA lobbying (protest, media
--     pressure, constituent calls, administrative action) is structurally
--     invisible to this data. Each flagged issue code needs its own
--     case-style outcome drilldown (bill text/status via web research)
--     before any capture claim can be made -- this screen only locates
--     candidates, it does not verify them.
--
-- Run against db/gain.db.

CREATE TEMP TABLE advocacy_orgs(name TEXT);
INSERT INTO advocacy_orgs VALUES
  ('AMERICAN CIVIL LIBERTIES UNION'),('AMERICAN PUBLIC HEALTH ASSOCIATION'),
  ('CENTER FOR RESPONSIBLE LENDING'),('CENTER FOR SCIENCE IN THE PUBLIC INTEREST'),
  ('COMMON CAUSE'),('CONSUMER FEDERATION OF AMERICA'),('CONSUMER REPORTS'),
  ('EARTHJUSTICE'),('ENVIRONMENTAL DEFENSE ACTION FUND'),('ENVIRONMENTAL DEFENSE FUND'),
  ('ENVIRONMENTAL WORKING GROUP'),('NATURAL RESOURCES DEFENSE COUNCIL'),
  ('PUBLIC CITIZEN'),('SIERRA CLUB'),('THE GOOD FOOD INSTITUTE'),('UNION OF CONCERNED SCIENTISTS');

SELECT
  sla.general_issue_code,
  ric.name AS issue_name,
  COUNT(DISTINCT sf.client_id) AS n_clients_total,
  COUNT(DISTINCT CASE WHEN c.name IN (SELECT name FROM advocacy_orgs) THEN sf.client_id END) AS n_advocacy,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.name IN (SELECT name FROM advocacy_orgs) THEN sf.client_id END)
    / COUNT(DISTINCT sf.client_id), 2) AS pct_advocacy
FROM senate_filings sf
JOIN senate_clients c ON c.id = sf.client_id
JOIN senate_lobbying_activities sla ON sla.filing_uuid = sf.filing_uuid
JOIN ref_issue_codes ric ON ric.value = sla.general_issue_code
WHERE sf.filing_year = 2025
GROUP BY sla.general_issue_code
HAVING n_clients_total >= 200
ORDER BY n_advocacy ASC, n_clients_total DESC;
