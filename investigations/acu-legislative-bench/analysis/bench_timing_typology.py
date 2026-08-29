"""E11 typology: money's timing relative to bill introduction and press, per bench member.

Reads the four derived/bench_*.csv files (must already exist -- run the
build_bench_* scripts first) and prints three tables cited in evidence.md E11:
  (a) nearest bill/contribution gap for every press release
  (b) contribution $ before vs. after first bill introduction, bucketed
  (c) 45-day "responsiveness" test -- does any bill/press event fall in the
      45 days immediately before a contribution -- plus raw gap-length audit
"""
import csv
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "derived"
MEMBERS = ["Barr", "Britt", "Emmer", "Cramer", "Scott", "Beatty",
           "Fitzgerald", "Gonzalez", "Vargas", "Budd"]


def parse(s):
    return datetime.strptime(s, "%Y-%m-%d")


def load():
    contrib = list(csv.DictReader((BASE / "bench_contributions.csv").open()))
    press = list(csv.DictReader((BASE / "bench_press_releases.csv").open()))
    bills = list(csv.DictReader((BASE / "bench_bill_dates.csv").open()))
    return contrib, press, bills


def table_a_press_gaps(contrib, press, bills):
    print("=== (a) press -> nearest bill / nearest contribution ===")
    for m in MEMBERS:
        c = sorted(parse(r["contribution_date"]) for r in contrib if r["member"] == m)
        p = sorted(parse(r["date"]) for r in press if r["member"] == m and r["date"])
        b = sorted(parse(r["introduced_date"]) for r in bills if r["member"] == m and r["introduced_date"])
        if not p or not b:
            continue
        print(f"\n{m}:")
        for pd in p:
            nearest_bill = min(b, key=lambda bd: abs((bd - pd).days))
            nearest_c = min(c, key=lambda cd: abs((cd - pd).days)) if c else None
            gap_bill = (pd - nearest_bill).days
            gap_c = (pd - nearest_c).days if nearest_c else None
            print(f"  press {pd.date()}: nearest bill-intro {nearest_bill.date()} "
                  f"(press{gap_bill:+d}d)  |  nearest contrib "
                  f"{nearest_c.date() if nearest_c else 'n/a'} (press{gap_c:+d}d)"
                  if nearest_c else f"  press {pd.date()}: nearest bill-intro "
                                     f"{nearest_bill.date()} (press{gap_bill:+d}d)")


def table_b_before_after(contrib, bills):
    print("\n=== (b) contribution $ before/after first bill introduction ===")
    print(f"{'member':<11} {'n_before':>8} {'$before':>10} {'$after_0-30d':>13} "
          f"{'$after_30-180d':>15} {'$after_180d+':>13} {'%after':>7}")
    for m in MEMBERS:
        c = sorted((parse(r["contribution_date"]), float(r["amount_num"]))
                   for r in contrib if r["member"] == m)
        b = sorted(parse(r["introduced_date"]) for r in bills if r["member"] == m and r["introduced_date"])
        if not b or not c:
            continue
        first_bill = b[0]
        before = [(d, amt) for d, amt in c if d < first_bill]
        after = [(d, amt) for d, amt in c if d >= first_bill]
        a30 = [x for x in after if (x[0] - first_bill).days <= 30]
        a180 = [x for x in after if 30 < (x[0] - first_bill).days <= 180]
        a180p = [x for x in after if (x[0] - first_bill).days > 180]
        usd_before = sum(a for _, a in before)
        usd_after = sum(a for _, a in after)
        pct_after = 100 * usd_after / (usd_before + usd_after) if (usd_before + usd_after) else 0
        print(f"{m:<11} {len(before):>8} {usd_before:>10.0f} {sum(a for _,a in a30):>13.0f} "
              f"{sum(a for _,a in a180):>15.0f} {sum(a for _,a in a180p):>13.0f} {pct_after:>6.0f}%")


def table_c_responsiveness(contrib, press, bills):
    print("\n=== (c) 45-day responsiveness test + raw contribution gaps ===")
    for m in MEMBERS:
        c = sorted(parse(r["contribution_date"]) for r in contrib if r["member"] == m)
        b = [parse(r["introduced_date"]) for r in bills if r["member"] == m and r["introduced_date"]]
        p = [parse(r["date"]) for r in press if r["member"] == m and r["date"]]
        events = sorted(b + p)
        if not c or not events:
            continue
        responsive = sum(1 for cd in c if any(0 <= (cd - e).days <= 45 for e in events))
        gaps = [(c[i + 1] - c[i]).days for i in range(len(c) - 1)]
        print(f"{m:<11} n_contribs={len(c):>2}  responsive(45d)={responsive:>2} "
              f"({100*responsive/len(c):.0f}%)  gaps={gaps}")


if __name__ == "__main__":
    contrib, press, bills = load()
    table_a_press_gaps(contrib, press, bills)
    table_b_before_after(contrib, bills)
    table_c_responsiveness(contrib, press, bills)
