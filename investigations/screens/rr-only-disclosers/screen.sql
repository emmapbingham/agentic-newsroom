-- Screen: rr-only-disclosers
-- Baseline (corrected 2026-07-02, see docs/derived_db.md): a covered position
-- disclosed on a lobbyist's initial registration (RR) is expected, per LDA
-- guidance, to persist on subsequent filings for that lobbyist-registrant
-- pair. Verified corpus rate: 81.8% of RR-disclosed pairs (3,328/4,070) ARE
-- redisclosed on >=1 later filing. The 18.2% that are never redisclosed on
-- ANY later filing, despite having plenty of chances to, are the anomaly.
--
-- (The screen's original baseline claimed 62.1% vs 25-27% -- disclosure
-- decay. That number does not reconcile with this table and its derivation
-- is unknown; do not use it. See docs/derived_db.md.)
--
-- Source: derived_lobbyist_rr_disclosure (built by
-- scripts/build_derived_lobbyist_revolving_door.py)

SELECT lobbyist_name, registrant_name, rr_covered_position, rr_filing_year,
       n_subsequent_quarterlies, n_subsequent_with_disclosure, redisclosed_ever
FROM derived_lobbyist_rr_disclosure
WHERE redisclosed_ever = 0
  AND n_subsequent_quarterlies >= 4     -- had ample opportunity to redisclose
ORDER BY n_subsequent_quarterlies DESC;
