"""Ranking step for the issue-lobby-press-lead-lag screen.

Reads derived_issue_quarter_volume_press (db/gain.db, read-only), z-scores
each issue code's quarterly lobbying-activity and press-release series, and
ranks codes by how much the best lagged correlation (lag -3..+3 quarters)
beats the zero-lag correlation. Positive lag = press leads lobbying.

At n=17 quarters this is a multiple-comparisons trap: most ranked codes are
noise. Use the output to pick a candidate for direct inspection of the raw
series, not as a trustworthy ranking on its own.
"""
import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "db/gain.db"


def load():
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        """
        SELECT issue_code, issue_name, year, quarter,
               total_activities, total_income_apportioned, n_press_releases
        FROM derived_issue_quarter_volume_press
        ORDER BY issue_code, year, quarter
        """,
        con,
    )
    con.close()
    df["t"] = (df["year"] - 2022) * 4 + df["quarter"]
    return df.sort_values(["issue_code", "t"])


def zscore(s):
    sd = s.std()
    return (s - s.mean()) / sd if sd > 0 else s * 0


def rank(df, min_lobby=100, min_press=100, min_quarters=15):
    rows = []
    for code, g in df.groupby("issue_code"):
        g = g.set_index("t").reindex(range(g["t"].min(), g["t"].max() + 1))
        if len(g) < min_quarters:
            continue
        if g["total_activities"].sum() < min_lobby or g["n_press_releases"].sum() < min_press:
            continue
        lobby, press = g["total_activities"].fillna(0), g["n_press_releases"].fillna(0)
        lz, pz = zscore(lobby), zscore(press)
        best = None
        for lag in range(-3, 4):
            a, b = (lz[lag:], pz[: len(pz) - lag]) if lag >= 0 else (lz[:lag], pz[-lag:])
            a, b = a.reset_index(drop=True), b.reset_index(drop=True)
            if len(a) < 8:
                continue
            corr = np.corrcoef(a, b)[0, 1]
            if best is None or abs(corr) > abs(best[1]):
                best = (lag, corr)
        if best is None:
            continue
        lag0 = np.corrcoef(lz.fillna(0), pz.fillna(0))[0, 1]
        rows.append(
            {
                "issue_code": code,
                "issue_name": g["issue_name"].iloc[0],
                "best_lag": best[0],
                "best_corr": best[1],
                "lag0_corr": lag0,
                "total_lobby": int(lobby.sum()),
                "total_press": int(press.sum()),
            }
        )
    res = pd.DataFrame(rows)
    res["lag_advantage"] = res["best_corr"].abs() - res["lag0_corr"].abs()
    return res.sort_values("lag_advantage", ascending=False)


if __name__ == "__main__":
    df = load()
    res = rank(df)
    pd.set_option("display.width", 140)
    print(res.head(20).to_string(index=False))
