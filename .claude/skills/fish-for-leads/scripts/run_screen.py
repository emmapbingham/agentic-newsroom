#!/usr/bin/env python3
"""Run a registered screen → ranked shortlist + distribution figure + logged run.

A screen is deterministic SQL over gain.db that ranks candidates by deviation
from a baseline. This runner is the deskside half of the newsroom 'screen'
phase: it executes the SQL, writes the full shortlist as CSV, saves a top-N
figure, and records the run in newsroom.db.screen_runs — the
multiple-comparisons ledger ("this lead surfaced out of how many screens?").

Convention for a screen's SQL (investigations/screens/<name>/screen.sql):
  - returns one row per candidate, already ORDER BY the deviation desc
  - has a numeric column named `score` (the ranking / plotted metric)
  - the first TEXT column is used as the bar label

    python scripts/run_screen.py senate-duplicate-filings
    python scripts/run_screen.py house-only-client-gap --top 40
"""
import argparse
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

GAIN = "file:db/gain.db?mode=ro"
NEWSROOM = Path("investigations/newsroom.db")
SCREENS_DIR = Path("investigations/screens")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screen")
    ap.add_argument("--top", type=int, default=30, help="bars in the figure")
    args = ap.parse_args()

    nb = sqlite3.connect(NEWSROOM)
    row = nb.execute(
        "SELECT id, sql_path, baseline FROM screens WHERE name=?", (args.screen,)
    ).fetchone()
    if not row:
        sys.exit(f"screen {args.screen!r} not registered in newsroom.db")
    screen_id, sql_path, baseline = row
    sql_path = sql_path or str(SCREENS_DIR / args.screen / "screen.sql")
    sql = Path(sql_path).read_text()

    # execute read-only against the corpus
    gdb = sqlite3.connect(GAIN, uri=True)
    df = pd.read_sql_query(sql, gdb)
    gdb.close()
    n = len(df)
    if "score" not in df.columns:
        sys.exit("screen SQL must return a numeric `score` column")

    # reserve a run id, lay out its directory, write artifacts
    cur = nb.execute(
        "INSERT INTO screen_runs (screen_id, params, n_candidates) VALUES (?,?,?)",
        (screen_id, f'{{"top":{args.top}}}', n),
    )
    run_id = cur.lastrowid
    run_dir = SCREENS_DIR / args.screen / f"run-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    shortlist = run_dir / "shortlist.csv"
    figure = run_dir / "distribution.png"
    df.to_csv(shortlist, index=False)

    # figure: top-N candidates by score
    label_col = next((c for c in df.columns if df[c].dtype == object), df.columns[0])
    head = df.head(args.top).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9, max(3, 0.32 * len(head))))
    ax.barh(head[label_col].astype(str), head["score"], color="#4060a0")
    ax.set_xlabel("score (deviation from baseline)")
    ax.set_title(f"{args.screen} — top {len(head)} of {n}\nbaseline: {baseline or ''}",
                 fontsize=9)
    fig.tight_layout()
    fig.savefig(figure, dpi=110)
    plt.close(fig)

    nb.execute(
        "UPDATE screen_runs SET shortlist_path=?, figures_path=? WHERE id=?",
        (str(shortlist), str(figure), run_id),
    )
    nb.commit()
    nb.close()

    print(f"screen {args.screen}: {n} candidates  (run {run_id})")
    print(f"  shortlist: {shortlist}")
    print(f"  figure:    {figure}")
    show = df.head(8)[[label_col, "score"]]
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()
