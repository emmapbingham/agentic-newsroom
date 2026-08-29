-- conviction-quarterly-gaps
-- Baseline: every original quarterly (Q1-Q4) filed after a lobbyist's
-- conviction date should carry the conviction disclosure; expected gap = 0.
-- The register's own population is the empirical baseline: convicted
-- lobbyists re-disclose on post-conviction quarterlies in the overwhelming
-- majority of cases (Burkman 471/471, Wohl 181/182), so missing rows are
-- deviation, not form convention. Post-conviction filter is mandatory
-- (Burkman/Wohl 2022 gaps predate their convictions).
-- Requires: derived_convicted_lobbyist_register
--   (scripts/build_derived_convicted_lobbyist_register.py).
-- score = n_post_missing. Verify any row at
--   https://lda.gov/filings/public/filing/{uuid}/print/ via missing_uuids.
SELECT
    lobbyist_name,
    n_post_missing               AS score,
    n_post_quarterlies,
    n_post_disclosed,
    round(1.0 * n_post_missing / n_post_quarterlies, 3) AS share_missing,
    conviction_date,
    substr(conviction_desc, 1, 120) AS conviction_desc,
    n_filings_disclosed,
    missing_uuids
FROM derived_convicted_lobbyist_register
WHERE n_post_quarterlies > 0
ORDER BY score DESC, share_missing DESC;
