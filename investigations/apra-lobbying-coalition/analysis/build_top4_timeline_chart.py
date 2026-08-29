#!/usr/bin/env python3
"""E12: timeline chart for the top 4 press-release members (Schakowsky,
Trahan, Moran, DelBene) -- one lane per member, in-house LD-203
contributions as circles (sized by amount), APRA-related press releases as
triangles, and bill milestones as vertical reference lines.

Reads derived/top4_inhouse_contribution_timeline.csv (E11) and
derived/apra_press_releases.csv (filtered to non-UNVERIFIED rows for these
4 members, same "confirmed on-topic" set used for the 2026-07-08 member
ranking). Bill milestone dates were web-sourced 2026-07-08 (NOT corpus
evidence -- see log.md) and are marked as such in the chart caption:
  - 2022-06-21: ADPPA (H.R. 8152) introduced
  - 2024-04-08: APRA discussion draft released (matches corpus press dates)
  - 2024-06-25: APRA (H.R. 8818) formally introduced
  - 2024-06-27: markup canceled ("killed")
  - 2025-01-03: 118th Congress ends, bill formally expires

Re-run: python3 investigations/apra-lobbying-coalition/analysis/build_top4_timeline_chart.py
Requires derived/top4_inhouse_contribution_timeline.csv and
derived/apra_press_releases.csv (both already built). Writes
derived/top4_timeline_chart.png.
"""
import csv
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent.parent / "derived"
CONTRIB_CSV = BASE / "top4_inhouse_contribution_timeline.csv"
PRESS_CSV = BASE / "apra_press_releases.csv"
OUT_PNG = BASE / "top4_timeline_chart.png"

MEMBERS = ["Schakowsky", "Trahan", "Moran", "DelBene"]
COLORS = {
    "Schakowsky": "#1b9e77",
    "Trahan": "#d95f02",
    "Moran": "#7570b3",
    "DelBene": "#e7298a",
}
Y = {m: i for i, m in enumerate(MEMBERS)}

MILESTONES = [
    ("2022-06-21", "ADPPA (H.R. 8152)\nintroduced"),
    ("2024-04-08", "APRA discussion\ndraft released"),
    ("2024-06-25", "APRA (H.R. 8818)\nformally introduced"),
    ("2024-06-27", "Markup canceled\n(“killed”)"),
    ("2025-01-03", "118th Congress ends\n(bill expires)"),
]

MEMBER_NAME_MAP = {
    "Janice D. Schakowsky": "Schakowsky",
    "Lori Trahan": "Trahan",
    "Jerry Moran": "Moran",
    "Suzan K. DelBene": "DelBene",
}


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d")


def load_contributions():
    rows = list(csv.DictReader(CONTRIB_CSV.open()))
    out = []
    for r in rows:
        out.append({
            "member": r["member"],
            "date": parse_date(r["contribution_date"]),
            "amount": float(r["amount_num"]),
        })
    return out


def load_press():
    rows = list(csv.DictReader(PRESS_CSV.open()))
    out = []
    for r in rows:
        member = MEMBER_NAME_MAP.get(r["member_name"])
        if member is None:
            continue
        if r["confidence_note"].startswith("UNVERIFIED"):
            continue
        out.append({"member": member, "date": parse_date(r["date"]), "title": r["title"]})
    return out


def main():
    contributions = load_contributions()
    press = load_press()

    fig, ax = plt.subplots(figsize=(20, 8))

    # lane background bands for readability
    for m in MEMBERS:
        ax.axhspan(Y[m] - 0.45, Y[m] + 0.45, color=COLORS[m], alpha=0.05, zorder=0)

    # contributions: circles, area scaled by amount (sqrt scaling so a 10x
    # amount doesn't look 10x the AREA, which would overwhelm the eye)
    for m in MEMBERS:
        pts = [c for c in contributions if c["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        # small deterministic vertical jitter (seeded by date ordinal) so
        # same-day/near-day contributions in dense lanes (Moran, DelBene)
        # don't stack into a single unreadable blob
        rng = np.random.default_rng(42)
        jitter = rng.uniform(-0.12, 0.12, size=len(pts))
        ys = np.full(len(pts), Y[m], dtype=float) + jitter
        # size by magnitude -- a handful of LD-203 items are negative
        # (refund/redesignation corrections, e.g. one DelBene/Aflac -$2,500
        # row 2025-10-20); size by abs(amount) so the point still renders,
        # and mark refunds with an 'x' instead of a filled circle below.
        sizes = np.array([10 + 2.5 * (abs(p["amount"]) ** 0.5) for p in pts], dtype=float)
        is_refund = np.array([p["amount"] < 0 for p in pts])
        if (~is_refund).any():
            ax.scatter(
                [x for x, r in zip(xs, is_refund) if not r],
                ys[~is_refund],
                s=sizes[~is_refund], color=COLORS[m], alpha=0.35, zorder=3,
                edgecolors="none",
            )
        if is_refund.any():
            ax.scatter(
                [x for x, r in zip(xs, is_refund) if r],
                ys[is_refund],
                s=200, color="black", alpha=1.0, zorder=5,
                marker="x", linewidths=2.5,
            )

    # press releases: triangles, fixed size, slightly offset above the lane
    # center so they don't visually collide with contribution circles
    for m in MEMBERS:
        pts = [p for p in press if p["member"] == m]
        if not pts:
            continue
        xs = [p["date"] for p in pts]
        ys = [Y[m] + 0.34] * len(pts)
        ax.scatter(xs, ys, marker="^", s=90, color=COLORS[m], alpha=0.95,
                   zorder=4, edgecolors="black", linewidths=0.5)

    # bill milestones: vertical reference lines spanning the whole chart.
    # Three of the five land within an 80-day window in Apr-Jun 2024, so
    # stagger label vertical position (two rows below the chart) and give
    # the close-together ones distinct horizontal nudges so the text
    # doesn't overlap.
    # NOTE: y-axis is inverted (Schakowsky at y=0 plotted at the visual top),
    # so the visual TOP of the chart is the small/negative y end.
    label_rows = [0, 1, 0, 1, 0]
    ha_nudge = ["center", "right", "center", "left", "center"]
    for (date_str, label), row, ha in zip(MILESTONES, label_rows, ha_nudge):
        d = parse_date(date_str)
        ax.axvline(d, color="#555555", linestyle="--", linewidth=1, zorder=1, alpha=0.7)
        y_pts = 8 + row * 15
        ax.annotate(
            label, xy=(d, -0.6), xytext=(0, y_pts), textcoords="offset points",
            rotation=0, va="bottom", ha=ha, fontsize=7.3, color="#333333",
            annotation_clip=False,
        )

    ax.set_yticks([Y[m] for m in MEMBERS])
    ax.set_yticklabels(MEMBERS, fontsize=11)
    ax.set_ylim(-0.6, len(MEMBERS) - 0.1)
    ax.invert_yaxis()
    fig.subplots_adjust(top=0.80)

    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(parse_date("2021-10-01"), parse_date("2026-06-01"))
    ax.grid(axis="x", which="major", color="#dddddd", linewidth=0.8, zorder=0)

    ax.set_title(
        "APRA/ADPPA coalition case: in-house LD-203 contributions vs.\n"
        "APRA-related press releases, by member (2022–2026)",
        fontsize=13, pad=48,
    )

    # legend: marker meaning (size/shape), not member color (that's the y-axis)
    size_legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", alpha=0.6,
               markersize=4.5, label="Contribution, ~$1,000"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", alpha=0.6,
               markersize=10, label="Contribution, ~$10,000"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="gray",
               markeredgecolor="black", markersize=9, label="Press release"),
        Line2D([0], [0], marker="x", color="gray", markersize=9,
               linewidth=0, markeredgewidth=1.5, label="Refund/correction (negative amount)"),
    ]
    ax.legend(handles=size_legend, loc="upper left", fontsize=8.5, framealpha=0.9)

    fig.text(
        0.01, 0.01,
        "Contributions: in-house registrants only (company lobbies for itself), from LD-203 filings, "
        "derived/top4_inhouse_contribution_timeline.csv (E11).  Press releases: bill-name or fork-verified "
        "on-topic rows only, derived/apra_press_releases.csv.  Bill milestone dates web-sourced 2026-07-08, "
        "NOT corpus evidence -- see log.md.",
        fontsize=6.5, color="#666666",
    )

    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT_PNG, dpi=200)
    print(f"wrote {OUT_PNG}")


if __name__ == "__main__":
    main()
