# Query recipes for db/gain.db

Ready cross-source SQL. All verified against the built database. Specialize the
literals (issue codes, names, dates) to your lead. FTS uses SQLite FTS5 syntax
(`'"exact phrase" OR term'`, `term*` for prefixes).

## 1. A topic's footprint across all three corpora

The fastest way to size a lead: where is this issue being lobbied and talked about?

```sql
SELECT 'senate_lobbying' src, count(*) FROM senate_activities_fts WHERE senate_activities_fts MATCH '"pharmacy benefit"';
SELECT 'house_lobbying'  src, count(*) FROM house_activities_fts  WHERE house_activities_fts  MATCH '"pharmacy benefit"';
SELECT 'press'           src, count(*) FROM press_fts             WHERE press_fts             MATCH '"pharmacy benefit"';
```

## 2. Who lobbies on an issue, with client and spend (Senate)

```sql
SELECT r.name AS registrant, c.name AS client,
       count(DISTINCT f.filing_uuid) filings, sum(f.income_amt) reported_income
FROM senate_lobbying_activities a
JOIN senate_filings f     ON f.filing_uuid = a.filing_uuid
JOIN senate_registrants r ON r.id = f.registrant_id
JOIN senate_clients c     ON c.id = f.client_id
WHERE a.general_issue_code = 'HCR'          -- or: a.activity_id IN (SELECT activity_id FROM senate_activities_fts WHERE senate_activities_fts MATCH 'insulin')
GROUP BY r.id, c.id ORDER BY filings DESC LIMIT 25;
```

## 3. A registrant's footprint in BOTH chambers (the bridge)

```sql
WITH reg AS (SELECT id, name FROM senate_registrants WHERE name LIKE 'BROWNSTEIN HYATT%')
SELECT reg.name,
       (SELECT count(*) FROM senate_filings WHERE registrant_id = reg.id) senate_filings,
       (SELECT count(*) FROM house_filings  WHERE senate_registrant_id = reg.id) house_filings
FROM reg;

-- clients lobbied via this registrant in each chamber, to spot discrepancies
WITH reg AS (SELECT id FROM senate_registrants WHERE name LIKE 'BROWNSTEIN HYATT%')
SELECT 'senate' chamber, c.name client FROM senate_filings f
JOIN senate_clients c ON c.id=f.client_id WHERE f.registrant_id=(SELECT id FROM reg)
UNION ALL
SELECT 'house', client_name FROM house_filings WHERE senate_registrant_id=(SELECT id FROM reg);
```

## 4. Revolving door — lobbyists who disclose a prior government post

```sql
SELECT l.first_name, l.last_name, al.covered_position, count(*) n
FROM senate_activity_lobbyists al
JOIN senate_lobbyists l ON l.id = al.lobbyist_id
WHERE al.covered_position IS NOT NULL
  AND al.covered_position NOT IN ('N/A','See prior filing','Legislative Consultant','Self','None')
GROUP BY al.lobbyist_id, al.covered_position
ORDER BY n DESC LIMIT 30;

-- target a specific office (free-text match on the disclosed position)
SELECT DISTINCT l.first_name, l.last_name, al.covered_position
FROM senate_activity_lobbyists al JOIN senate_lobbyists l ON l.id=al.lobbyist_id
WHERE al.covered_position LIKE '%Ways and Means%';
-- House equivalent: house_filing_lobbyists.covered_position (name-only, no id)
```

## 5. Biggest lobbying clients by reported spend (Senate)

```sql
SELECT c.name, sum(f.income_amt) total_income, count(*) filings
FROM senate_filings f JOIN senate_clients c ON c.id=f.client_id
WHERE f.income_amt IS NOT NULL AND f.filing_year = 2025
GROUP BY c.id ORDER BY total_income DESC LIMIT 25;
```

## 6. Contributions by honoree (member-directed money)

```sql
SELECT honoree_name, sum(amount_num) total, count(*) n
FROM senate_contribution_items
WHERE honoree_name IS NOT NULL
  AND honoree_name NOT IN ('N/A','None')
  AND honoree_name NOT LIKE '%PAC%' AND honoree_name NOT LIKE '%Committee%'
  AND honoree_name NOT IN ('NRSC','DSCC','NRCC','DCCC')   -- party committees
GROUP BY honoree_name ORDER BY total DESC LIMIT 30;

-- who gave to a given honoree
SELECT i.date, r.name registrant, i.contributor_name, i.amount_num
FROM senate_contribution_items i
JOIN senate_contribution_filings cf ON cf.filing_uuid = i.filing_uuid
JOIN senate_registrants r ON r.id = cf.registrant_id
WHERE i.honoree_name LIKE '%Mike Flood%' ORDER BY i.amount_num DESC;
```

**Trap: LD-203 filer copies double-count contributions.** The same
contribution appears on the registrant's *organization* filing AND on each
listed lobbyist's *individual* LD-203 (SpaceX: 9 org + 45 lobbyist filings;
raw summing inflated one member's total 2.3×). Before summing, reduce to
DISTINCT (contributor_name, payee_name, date, amount_num) tuples per
honoree — lobbyists' own personal contributions survive that dedup as
distinct contributors, which is correct. Same discipline as the $118M
quarterly-duplicates episode, new channel (2026-07-06, triangle screen).

## 7. Foreign influence

```sql
SELECT fe.name foreign_entity, fe.country, c.name client,
       fe.ownership_percentage, fe.contribution_amt
FROM senate_filing_foreign_entities fe
JOIN senate_filings f ON f.filing_uuid = fe.filing_uuid
JOIN senate_clients c ON c.id = f.client_id
WHERE fe.country NOT IN ('US') ORDER BY fe.contribution_amt DESC NULLS LAST LIMIT 30;
-- House side: house_foreign_entities JOIN house_filings.
```

## 8. Lobbyists with disclosed criminal convictions

```sql
SELECT l.first_name, l.last_name, cv.date, cv.description, f.filing_document_url
FROM senate_filing_conviction_disclosures cv
JOIN senate_filings f ON f.filing_uuid = cv.filing_uuid
LEFT JOIN senate_lobbyists l ON l.id = cv.lobbyist_id
ORDER BY cv.date DESC;
```

Legal basis: the JACK Act (eff. 2019-01-03) requires the disclosure on every
LD-1 and every LD-2 listing the lobbyist, for any prior conviction of an
enumerated predicate, with no lookback limit —
`investigations/jack-act-blind-spots/sources/jack-act-notice.md`.

**Trap: the disclosed text/date may not be the court conviction.** Filers
sometimes paste an *administrative* charging document and its date instead of
the criminal judgment (Hanson/VVA discloses the 2013 BIS settlement order
verbatim — 15-yr export-privilege denial, not a conviction — while his actual
JACK predicate is a 2009 §1001 guilty plea, D.D.C. 1:09-cr-00071). Before
calling anything a conviction, verify the underlying court case; `cv.date`
is self-reported and can be the wrong instrument's date. Post-conviction gap
math (`derived_convicted_lobbyist_register`) inherits this caveat.

## 9. A member's press releases over time / on a topic

```sql
SELECT date, title FROM press_releases
WHERE bioguide_id = 'C001059' ORDER BY date;

SELECT p.date, p.member_name, p.party, p.title
FROM press_fts f JOIN press_releases p ON p.release_id = f.release_id
WHERE press_fts MATCH 'insulin OR "drug prices"' ORDER BY p.date DESC LIMIT 50;
```

## 10. Money to members, joined to committee + press volume (the closed loop)

The crosswalk (`honoree_member_map` → `members`) closes the money↔member link.
Filter `confidence >= 0.9` for high-trust matches.

```sql
SELECT mem.official_full, mem.last_party, mem.last_state,
       round(sum(i.amount_num)) received,
       (SELECT count(*) FROM press_releases p WHERE p.bioguide_id=mem.bioguide) releases,
       (SELECT c.name FROM member_committees mc JOIN committees c ON c.committee_id=mc.committee_id
        WHERE mc.bioguide=mem.bioguide AND c.parent_committee_id IS NULL
        ORDER BY mc.rank LIMIT 1) top_committee
FROM senate_contribution_items i
JOIN honoree_member_map hm ON hm.honoree_name = i.honoree_name AND hm.confidence >= 0.9
JOIN members mem ON mem.bioguide = hm.bioguide
GROUP BY mem.bioguide ORDER BY received DESC LIMIT 20;
```

## 11. "Say vs. pay" for one member on one issue

The lead: a member who is loud on an issue while funded/lobbied on it. Pick a
member (`bioguide`), an issue (FTS terms), and compare.

```sql
-- (a) their rhetoric on the issue
SELECT p.date, p.title FROM press_releases p JOIN press_fts f ON f.release_id=p.release_id
WHERE p.bioguide_id = :bio AND press_fts MATCH 'pharmaceutical OR PBM OR insulin';

-- (b) money honoring them, by the lobbyist/registrant who filed it (via crosswalk)
SELECT r.name registrant, i.contributor_name, sum(i.amount_num) total
FROM senate_contribution_items i
JOIN honoree_member_map hm ON hm.honoree_name=i.honoree_name AND hm.bioguide = :bio
JOIN senate_contribution_filings cf ON cf.filing_uuid=i.filing_uuid
JOIN senate_registrants r ON r.id=cf.registrant_id
GROUP BY r.id, i.contributor_name ORDER BY total DESC;

-- (c) committees they sit on (where that industry has business before them)
SELECT c.name, mc.title FROM member_committees mc
JOIN committees c ON c.committee_id=mc.committee_id WHERE mc.bioguide = :bio;

-- (d) lobbying on the issue aimed at their chamber, same period
SELECT r.name registrant, cl.name client, a.description
FROM senate_lobbying_activities a
JOIN senate_filings f ON f.filing_uuid=a.filing_uuid
JOIN senate_registrants r ON r.id=f.registrant_id
JOIN senate_clients cl ON cl.id=f.client_id
JOIN senate_activity_government_entities ge ON ge.activity_id=a.activity_id
JOIN ref_government_entities g ON g.id=ge.government_entity_id
WHERE a.activity_id IN (SELECT activity_id FROM senate_activities_fts WHERE senate_activities_fts MATCH 'PBM')
  AND g.name = (CASE WHEN (SELECT last_type FROM members WHERE bioguide=:bio)='sen'
                     THEN 'SENATE' ELSE 'HOUSE OF REPRESENTATIVES' END);
```

The contrast — loud public stance vs. who funds/lobbies them on the same issue —
is the lead. Always confirm the honoree match (`method`/`confidence`) and cite
each source record (`filing_uuid`, `url`).
