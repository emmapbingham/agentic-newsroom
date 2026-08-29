"""Ranking step for the committee-lobby-press-lead-lag screen.

Reads derived_committee_quarter_press JOIN derived_issue_quarter_volume_press
(via committee_issue_jurisdiction, weight='primary' pairs only, db/gain.db,
read-only), z-scores each committee-issue pair's quarterly committee-press
volume and lobbying-activity volume, and ranks pairs by how much the best
lagged correlation (lag -3..+3 quarters) beats the zero-lag correlation.
Positive lag = press leads lobbying; negative = lobbying leads press.

This is the committee-anchored successor to
scripts/screen_issue_lobby_press_lead_lag.py, which ranked all 79 generic
issue codes with no institutional anchor and turned out to be mostly a
multiple-comparisons artifact at n=17 quarters. Anchoring to 60 pre-specified
committee-issue pairs (weight='primary' only) cuts the search space, but
does NOT fix the small-n problem -- n=17 quarters per pair is still short.
Treat correlations here as illustrative/directional, not statistically
significant findings. Use this ranking to pick ONE candidate for a direct,
named-series read (the way TAR was resolved directly, not via the ranked
table, in the 2026-07-02 tariff case note) -- not as a trustworthy leaderboard
on its own.

organizing_gap quarters (no committee roster existed yet -- new Congress not
organized, or subcommittee didn't exist) are excluded from the input, which
means each pair's time index has REAL, meaningful gaps (not just edge
truncation) -- reindexed and left as NaN/interpolation-free rather than
silently compressed, so a correlation computed across a gap doesn't
pretend two non-adjacent quarters are adjacent.

DETRENDING (added after the first run flagged a real problem): several top
hits by raw-level correlation (e.g. Senate Veterans' Affairs / VET) turned
out to be two series climbing together over 4 years, not a timing
relationship -- raw-level correlation on co-trending series is high at
EVERY lag regardless of true timing. Reports BOTH raw-level and
first-differenced (quarter-over-quarter change) correlation for every pair.
A pair whose correlation survives detrending (raw and diff both strong, at
the same lag) is a real lead-lag candidate; a pair where diff correlation
collapses relative to raw is a trend artifact, not a timing signal -- flag
it as such, don't report it as a finding.
"""
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "db/gain.db"


def load():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """
        SELECT cqp.committee_id, cqp.committee_name, cqp.issue_code, cqp.issue_name,
               cqp.year, cqp.quarter,
               cqp.n_topic_releases AS committee_press,
               iqp.total_activities AS lobby_activities
        FROM derived_committee_quarter_press cqp
        JOIN derived_issue_quarter_volume_press iqp
          ON iqp.issue_code = cqp.issue_code AND iqp.year = cqp.year AND iqp.quarter = cqp.quarter
        WHERE cqp.weight = 'primary'
          AND cqp.organizing_gap = 0
        ORDER BY cqp.committee_id, cqp.issue_code, cqp.year, cqp.quarter
        """,
        con,
    )
    con.close()
    df["t"] = (df["year"] - 2022) * 4 + df["quarter"]
    return df.sort_values(["committee_id", "issue_code", "t"])


def zscore(s):
    sd = s.std()
    return (s - s.mean()) / sd if sd > 0 else s * 0


def best_lag_corr(lz, pz, observed, lags=range(-3, 4), min_n=6):
    """Best-|corr| lag and its stats, plus lag-0, over only genuinely
    observed (non-gap-filled) paired quarters."""
    best = None
    for lag in lags:
        if lag >= 0:
            a, b = lz[lag:], pz[: len(pz) - lag]
            obs_a, obs_b = observed[lag:], observed[: len(observed) - lag]
        else:
            a, b = lz[:lag], pz[-lag:]
            obs_a, obs_b = observed[:lag], observed[-lag:]
        mask = obs_a.values & obs_b.values
        a, b = a.values[mask], b.values[mask]
        if len(a) < min_n:
            continue
        corr = np.corrcoef(a, b)[0, 1]
        if best is None or abs(corr) > abs(best[1]):
            best = (lag, corr, len(a))
    mask0 = observed.values
    lag0 = np.corrcoef(lz.values[mask0], pz.values[mask0])[0, 1] if mask0.sum() >= min_n else np.nan
    return best, lag0


def rank(df, min_lobby=200, min_press=50, min_quarters=10):
    rows = []
    for (cid, code), g in df.groupby(["committee_id", "issue_code"]):
        # organizing_gap quarters are already excluded from input -- reindex
        # over the OBSERVED t-range only (don't fabricate quarters this
        # committee-issue pair has no data for at all, e.g. a subcommittee
        # created mid-window)
        g = g.set_index("t").sort_index()
        if len(g) < min_quarters:
            continue
        if g["lobby_activities"].sum() < min_lobby or g["committee_press"].sum() < min_press:
            continue
        # reindex to the CONTIGUOUS range so gaps (organizing_gap quarters we
        # dropped) show up as NaN, not silently skipped -- then require the
        # lag comparison to only use pairs of quarters that are genuinely
        # t and t-lag apart (handled by the observed mask in best_lag_corr)
        full_index = range(g.index.min(), g.index.max() + 1)
        g = g.reindex(full_index)
        lobby, press = g["lobby_activities"], g["committee_press"]
        observed = g["lobby_activities"].notna() & g["committee_press"].notna()

        # -- raw levels --
        lz = zscore(lobby.fillna(lobby.mean()))
        pz = zscore(press.fillna(press.mean()))
        best_raw, lag0_raw = best_lag_corr(lz, pz, observed)
        if best_raw is None:
            continue

        # -- first-differenced (quarter-over-quarter change) --
        # a NaN-gap gets a NaN diff on both sides of the gap, correctly
        # excluding those pairs from the diff series too (via observed_diff)
        dlobby = lobby.diff()
        dpress = press.diff()
        observed_diff = observed & observed.shift(1).fillna(False).astype(bool)
        dlz = zscore(dlobby.fillna(dlobby.mean()))
        dpz = zscore(dpress.fillna(dpress.mean()))
        best_diff, lag0_diff = best_lag_corr(dlz, dpz, observed_diff)

        rows.append(
            {
                "committee_id": cid,
                "committee_name": g["committee_name"].dropna().iloc[0] if g["committee_name"].notna().any() else None,
                "issue_code": code,
                "issue_name": g["issue_name"].dropna().iloc[0] if g["issue_name"].notna().any() else None,
                "raw_best_lag": best_raw[0],
                "raw_best_corr": best_raw[1],
                "raw_best_n": best_raw[2],
                "raw_lag0_corr": lag0_raw,
                "diff_best_lag": best_diff[0] if best_diff else None,
                "diff_best_corr": best_diff[1] if best_diff else None,
                "diff_best_n": best_diff[2] if best_diff else None,
                "diff_lag0_corr": lag0_diff,
                "total_lobby": int(lobby.sum()),
                "total_committee_press": int(press.sum()),
            }
        )
    res = pd.DataFrame(rows)
    if res.empty:
        return res
    res["raw_lag_advantage"] = res["raw_best_corr"].abs() - res["raw_lag0_corr"].abs()
    # trend_survives requires BOTH: (a) the differenced series' own best lag
    # agrees with the raw series' best lag (not just "some lag has a strong
    # diff correlation" -- a different lag winning on diff means the raw
    # result and the diff result are telling two different, contradictory
    # stories, which is disqualifying, not confirming), and (b) the diff
    # correlation at that agreed lag is still substantial (>=0.5 magnitude).
    # A pair that fails either check is flagged as trend-driven / unstable,
    # not a real timing candidate.
    res["trend_survives"] = (
        (res["raw_best_lag"] == res["diff_best_lag"])
        & (res["diff_best_corr"].abs() >= 0.5)
    )
    return res.sort_values("raw_lag_advantage", ascending=False)


if __name__ == "__main__":
    df = load()
    res = rank(df)
    pd.set_option("display.width", 200)
    cols = ["committee_id", "issue_code", "raw_best_lag", "raw_best_corr", "raw_best_n",
            "raw_lag0_corr", "diff_best_lag", "diff_best_corr", "diff_lag0_corr",
            "trend_survives", "total_lobby", "total_committee_press"]
    print(res[cols].head(25).to_string(index=False))
