#!/usr/bin/env python3
"""Timeline chart: the ACU bench (Barr + 9 members drilled in E1-E9), one
lane per member -- ACU LD-203 contributions as circles (sized by amount),
ACU press mentions as triangles, and ACU lobbying-filing quarters naming the
member's bill as gray tick marks along the bottom of each lane.

Bill-introduction dates (from pull_bill_dates.py, Congress.gov API) are drawn
as star markers on each lane -- these are the ONLY dates in this chart not
derived from the corpus itself (gain.db has no bill-status data); flagged as
such in the caption per project convention (see apra chart's bill-milestone
caveat).

Modeled directly on apra-lobbying-coalition/analysis/build_top4_timeline_chart.py.
Reads derived/bench_contributions.csv, derived/bench_press_releases.csv,
derived/bench_lobbying_filings.csv, derived/bench_bill_dates.csv (built by
the four build_bench_*.py / pull_bill_dates.py scripts in this directory).

Re-run: python3 investigations/acu-legislative-bench/analysis/build_bench_timeline_chart.py
Writes derived/bench_timeline_chart.png.
"""
import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent.parent / "derived"
CONTRIB_CSV = BASE / "bench_contributions.csv"
PRESS_CSV = BASE / "bench_press_releases.csv"
LOBBYING_CSV = BASE / "bench_lobbying_filings.csv"
BILL_DATES_CSV = BASE / "bench_bill_dates.csv"
OUT_PNG = BASE / "bench_timeline_chart.png"

# ordered by E0 table (descending FECA $), Barr first as the case's worked exemplar.
# Peters added 2026-07-09 per E13 (editor's call to drop the n_mentions>=2
# construction threshold) -- $20,000, ties with Budd for last, placed after.
MEMBERS = ["Barr", "Britt", "Emmer", "Cramer", "Scott", "Beatty",
           "Fitzgerald", "Gonzalez", "Vargas", "Budd", "Peters"]
COLORS = {
    "Barr": "#e41a1c", "Britt": "#377eb8", "Emmer": "#4daf4a", "Cramer": "#984ea3",
    "Scott": "#ff7f00", "Beatty": "#a65628", "Fitzgerald": "#f781bf",
    "Gonzalez": "#999999", "Vargas": "#66c2a5", "Budd": "#1b9e77", "Peters": "#e6ab02",
}
Y = {m: i for i, m in enumerate(MEMBERS)}


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def load_contributions():
    rows = list(csv.DictReader(CONTRIB_CSV.open()))
    return [{"member": r["member"], "date": parse_date(r["contribution_date"]),
             "amount": float(r["amount_num"])} for r in rows]


def load_press():
    rows = list(csv.DictReader(PRESS_CSV.open()))
    return [{"member": r["member"], "date": parse_date(r["date"]), "title": r["title"]}
            for r in rows if r["date"]]


def load_lobbying():
    rows = list(csv.DictReader(LOBBYING_CSV.open()))
    out = []
    for r in rows:
        if r["description_excerpt"] == "NO MATCHES" or not r["dt_posted"]:
            continue
        # dt_posted looks like an ISO datetime; take the date part
        try:
            d = parse_date(r["dt_posted"][:10])
        except ValueError:
            continue
        out.append({"member": r["member"], "date": d, "bill_label": r["bill_label"]})
    return out


def load_bill_dates():
    rows = list(csv.DictReader(BILL_DATES_CSV.open()))
    out = []
    for r in rows:
        if not r["introduced_date"]:
            continue
        out.append({
            "member": r["member"],
            "date": parse_date(r["introduced_date"]),
            "bill_label": r["bill_label"],
            "congress": r["congress"],
            "number": f"{r['bill_type']}.{r['number']}",
        })
    return out


def main():
    contributions = load_contributions()
    press = load_press()
    lobbying = load_lobbying()
    bill_dates = load_bill_dates()

    fig, ax = plt.subplots(figsize=(20, 10))

    for m in MEMBERS:
        ax.axhspan(Y[m] - 0.45, Y[m] + 0.45, color=COLORS[m], alpha=0.05, zorder=0)

    # lobbying filings: gray tick marks near the bottom of each lane
    for m in MEMBERS:
        pts = [p for p in lobbying if p["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        ys = [Y[m] - 0.20] * len(pts)
        ax.scatter(xs, ys, marker="|", s=140, color="#555555", alpha=0.6,
                   zorder=2, linewidths=1.3)

    # bill-introduction dates: gold stars at the very bottom of each lane
    # (web-sourced via Congress.gov API, NOT corpus evidence -- see caption)
    for m in MEMBERS:
        pts = [p for p in bill_dates if p["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        ys = [Y[m] - 0.40] * len(pts)
        ax.scatter(xs, ys, marker="*", s=150, color="#b8860b", alpha=0.9,
                   zorder=5, edgecolors="black", linewidths=0.4)

    # contributions: circles, sized by sqrt(amount) so 10x $ isn't 10x AREA
    rng = np.random.default_rng(42)
    for m in MEMBERS:
        pts = [c for c in contributions if c["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        jitter = rng.uniform(-0.12, 0.12, size=len(pts))
        ys = np.full(len(pts), Y[m], dtype=float) + jitter
        sizes = np.array([10 + 2.5 * (abs(p["amount"]) ** 0.5) for p in pts], dtype=float)
        ax.scatter(xs, ys, s=sizes, color=COLORS[m], alpha=0.4, zorder=3, edgecolors="none")

    # press mentions: triangles, offset above lane center
    for m in MEMBERS:
        pts = [p for p in press if p["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        ys = [Y[m] + 0.34] * len(pts)
        ax.scatter(xs, ys, marker="^", s=90, color=COLORS[m], alpha=0.95,
                   zorder=4, edgecolors="black", linewidths=0.5)

    ax.set_yticks([Y[m] for m in MEMBERS])
    ax.set_yticklabels(MEMBERS, fontsize=11)
    ax.set_ylim(-0.65, len(MEMBERS) - 0.1)
    ax.invert_yaxis()
    fig.subplots_adjust(top=0.85)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(parse_date("2021-10-01"), parse_date("2026-06-01"))
    ax.grid(axis="x", which="major", color="#dddddd", linewidth=0.8, zorder=0)

    ax.set_title(
        "ACU legislative bench: LD-203 contributions vs. ACU press mentions vs.\n"
        "ACU Senate lobbying filings naming the member's bill, by member (2022-2026)",
        fontsize=13, pad=20,
    )

    size_legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", alpha=0.5,
               markersize=4.5, label="Contribution, ~$1,000"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", alpha=0.5,
               markersize=10, label="Contribution, ~$10,000"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
               markeredgecolor="black", markersize=9, label="ACU press mention"),
        Line2D([0], [0], marker="|", color="#555555", markersize=11,
               linewidth=0, markeredgewidth=1.6, label="ACU lobbying filing naming member's bill"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#b8860b",
               markeredgecolor="black", markersize=12, label="Bill introduced (Congress.gov)"),
    ]
    ax.legend(handles=size_legend, loc="upper left", fontsize=8.5, framealpha=0.9)

    fig.text(
        0.01, 0.01,
        "Contributions: ACU registrant_id=11322 LD-203 FECA items, derived/bench_contributions.csv. "
        "Press mentions: derived_client_press_mentions join (entity 644/645, deduped), derived/bench_press_releases.csv "
        "-- counts match evidence.md's hand-verified E1-E9 totals; see that file for roster-only vs. named-quote detail. "
        "Lobbying: ACU Senate filings matching each member's bill title, derived/bench_lobbying_filings.csv "
        "(dt_posted date). Bill-introduction dates (gold stars): Congress.gov API, derived/bench_bill_dates.csv, "
        "web-sourced 2026-07-08 -- NOT corpus evidence, see log.md. Beatty shows contributions+press but no "
        "lobbying ticks -- the documented E7 triple break.",
        fontsize=6.5, color="#666666",
    )

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT_PNG, dpi=200)
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
