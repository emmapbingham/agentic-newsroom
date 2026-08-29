-- Screen: issue-lobby-press-lead-lag
-- Baseline: stable 2022-2024 co-movement (TAR: ~440 activities/yr, ~10.6 press/month;
-- expected cross-correlation near zero at all lags).
-- Contrast type: self-over-time
-- Ranks issue codes by how much a lagged cross-correlation between quarterly lobbying
-- volume and press-release volume beats the zero-lag (contemporaneous) correlation.
-- Z-scores each series per issue code, then compares corr(lobby, press) at lag -1/0/+1
-- (lag k means lobby activity in quarter t vs press in quarter t-k; positive k = press led).
--
-- NOTE: with only 17 quarters (2022 Q1 - 2026 Q1) per issue code, and 79 codes each
-- tested at multiple lags, most correlations here are noise (|r|<0.48 isn't even
-- nominally significant at n=17, p<.05) -- this is a multiple-comparisons trap by
-- construction. Use this screen to find candidates for a *visual* read of a single
-- series (like TAR below), not to trust the ranked correlation table at face value.
--
-- Source table: derived_issue_quarter_volume_press (see docs/derived_db.md)
-- This screen's ranking step is NOT SQL -- SQLite has no correlation function.
-- Pull the base series with this query, then compute z-scored lagged correlation
-- in Python (see scripts/screen_issue_lobby_press_lead_lag.py for the exact method
-- used in the 2026-07-02 run).

SELECT issue_code, issue_name, year, quarter,
       total_activities, total_income_apportioned, n_press_releases
FROM derived_issue_quarter_volume_press
ORDER BY issue_code, year, quarter;
