# GAO Lobbying Disclosure compliance reports, 2019-2024 (JACK Act methodology cross-check)

- **What:** all six prior annual GAO LDA compliance reports, covering the JACK
  Act's first full year of applicability (2019) through 2024 — the years
  preceding `gao-jack-act-enforcement-2026.md`'s GAO-26-108486 (2025 report).
  Fetched to answer: does GAO always use the same random-sample methodology
  for JACK Act compliance, or did GAO-26-108486's approach change?
- **Sources fetched** (via WebFetch, then extracted locally with `pypdf` —
  GAO's CDN blocks direct `curl`; same obstacle logged for the 2026 report):

  | Year covered | Report # | File |
  |---|---|---|
  | 2019 | GAO-20-449 | `gao-20-449-2019-lobbying-disclosure.pdf` |
  | 2020 | GAO-21-375 | `gao-21-375-2020-lobbying-disclosure.pdf` |
  | 2021 | GAO-22-105181 | `gao-22-105181-2021-lobbying-disclosure.pdf` |
  | 2022 | GAO-23-105989 | `gao-23-105989-2022-lobbying-disclosure.pdf` |
  | 2023 | GAO-24-106799 | `gao-24-106799-2023-lobbying-disclosure.pdf` |
  | 2024 | GAO-25-107523 | `gao-25-107523-2024-lobbying-disclosure.pdf` |

  All fetched and cross-checked 2026-07-07.
- **Used by:** the enforcement-vacuum pillar of the systemic claim (Hunter +
  Hanson + enforcement context) — extends E-GAO from one year to the full
  post-JACK-Act series. Outside data, disclosed; legal/context standard only,
  never evidence for a filing-level claim about Hunter or Hanson specifically.

## Answer: yes — same methodology, every year, same result

**Sampling methodology is unchanged across all 7 reports (2019-2025 coverage
years, published as GAO-20-449 through GAO-26-108486):** a stratified random
sample of roughly 95-100 quarterly LD-2 disclosure reports per review period
(2 quarters), yielding somewhere between ~160 and ~270 *individual lobbyists*
once every lobbyist named on those LD-2s is counted. None of the six reports
describes a methodology change; each states findings are "generally consistent
with GAO's findings since [year]" (the phrase recurs, incrementing).

**JACK Act finding is identical in every single year: zero.**

| Coverage period | Individual lobbyists in sample | Disclosed a conviction | Report |
|---|---|---|---|
| 2019 Q1-Q2 | 165 (161 successfully identified) | 0 | GAO-20-449 |
| 2019 Q3-Q4 + 2020 Q1-Q2 | 210 | 0 | GAO-21-375 |
| 2020 Q3-Q4 + 2021 Q1-Q2 | 245 | 0 | GAO-22-105181 |
| 2021 Q3-Q4 + 2022 Q1-Q2 | 256 | 0 | GAO-23-105989 |
| 2022 Q3-Q4 + 2023 Q1-Q2 | 268 | 0 | GAO-24-106799 |
| 2023 Q3-Q4 + 2024 Q1-Q2 | 258 | 0 | GAO-25-107523 |
| 2024 Q3-Q4 + 2025 Q1-Q2 | 247 | 0 | GAO-26-108486 (already filed, see companion note) |

Every year: "None of the lobbyists in our sample... disclosed any convictions
in the reports." The verification method is consistent too — GAO researches
the sampled individuals (background/website searches; from 2026 onward,
explicitly Accurint/CLEAR criminal-background databases) to confirm the
self-reported "no conviction" is accurate, not to check whether a *known*
convicted lobbyist disclosed correctly. The population sampled is never
conditioned on conviction status — this is the same base-rate-artifact
structure identified in the 2026 report, holding across all 7 years.

**One near-miss worth flagging (GAO-22-105181, covering 2020 Q3/Q4 + 2021
Q1/Q2):** "While we found information relevant to the JACK Act for one
lobbyist, we could not locate any relevant court records" (p.18) — the only
year across the series where GAO's own text acknowledges finding a lead on a
possible undisclosed conviction, and it dead-ends on records access, not
resolution. GAO does not name the lobbyist or the outcome. Not usable as
evidence for any claim (no named individual, no resolution) but useful color:
even GAO's own reviewers hit the same records-access wall this case's Hanson
docket-pull did.

**Enforcement-resource and referral figures, all seven years (for context,
not the case's core claim):** the USAO's referral count is a cumulative
running total, not incident-specific to JACK Act — 4,220 referrals (2019
report, cumulative 2009-2019) down through fluctuating totals to the
2026 report's 12,391 (cumulative since 2016, different start year across
reports as GAO's window rolls forward). Every year's report describes the
same failure-to-file trigger mechanism (60-day non-response after LD-2/LD-203
non-filing) with no textual change describing a mechanism for a filed-but-
incomplete report. No report in the 2019-2024 series, nor the 2025/2026
report, describes any JACK-Act-specific civil or criminal enforcement action
ever having been taken.

## Caveats for case use

- This strengthens E-GAO's "structural, not one-off" framing: the base-rate-
  artifact critique isn't a one-year quirk of the 2026 report, it's the
  methodology's designed behavior across the JACK Act's entire lifespan to
  date (2019-2025 coverage, 7 annual reports).
- Same rule as E-GAO: never write "GAO reviewed and found no violations" as a
  compliance finding — every year's zero is a function of sampling ~160-270
  lobbyists from a pool where predicate convictions are rare (this corpus's
  own convicted-lobbyist register: ~18 total), not evidence about
  known-convicted filers' disclosure behavior specifically.
- The GAO-22-105181 near-miss is not evidence for the Hunter/Hanson claims —
  it is a different, unnamed lobbyist. Cite only as context on GAO's own
  records-access friction, if at all.
