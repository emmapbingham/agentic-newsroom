-- Screen: committee-lobby-press-lead-lag
-- Baseline: stable co-movement (near-zero cross-correlation at all lags)
-- between a committee's own lobbying-issue volume and that committee's own
-- members' press volume on the matching topic, per quarter.
--
-- This is the committee-anchored successor to issue-lobby-press-lead-lag
-- (which ran 2026-07-02 across all 79 issue codes with no institutional
-- anchor and turned out to be mostly a multiple-comparisons artifact at
-- n=17 quarters -- see that screen's notes). Anchoring to a specific
-- committee's own jurisdiction and own members' press cuts the search space
-- from 79 generic codes to 60 pre-specified, editorially-grounded
-- committee-issue pairs (committee_issue_jurisdiction, weight='primary'
-- only), and uses each committee's ACTUAL seated roster per quarter
-- (member_committees_history), not today's roster applied retroactively.
--
-- Still n=17 quarters per pair -- this does NOT fix the small-n problem,
-- it fixes the "no institutional anchor, unlimited multiple comparisons"
-- problem. Treat any single pair's correlation as illustrative/directional,
-- not a p<.05 claim. See scripts/screen_committee_lobby_press_lead_lag.py
-- for the actual ranking computation (SQLite has no correlation function).
--
-- Source tables: derived_committee_quarter_press (committee's own members'
-- press volume, correct-roster) x derived_issue_quarter_volume_press
-- (Senate+House lobbying volume, kept separate -- see docs/derived_db.md
-- for why summing them would double-count ~97% of dual-chamber engagements)
-- joined via committee_issue_jurisdiction (weight='primary' rows only).

SELECT
    cqp.committee_id, cqp.committee_name, cqp.issue_code, cqp.issue_name,
    cqp.year, cqp.quarter,
    cqp.n_committee_members, cqp.n_total_releases, cqp.n_topic_releases,
    iqp.senate_activities, iqp.house_activities, iqp.total_activities
FROM derived_committee_quarter_press cqp
JOIN derived_issue_quarter_volume_press iqp
  ON iqp.issue_code = cqp.issue_code AND iqp.year = cqp.year AND iqp.quarter = cqp.quarter
WHERE cqp.weight = 'primary'
  AND cqp.organizing_gap = 0
ORDER BY cqp.committee_id, cqp.issue_code, cqp.year, cqp.quarter;
