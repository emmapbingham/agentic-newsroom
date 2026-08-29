# The novelty scan: news never in the evidence middle

Reporting touches a case at exactly one point after verification, reading the
news for one purpose, and **never** enters the evidence chain. (Two separate,
earlier touchpoints exist upstream: using reporting to choose *where to point
the corpus* is a screen-design-time concern — see
`sweep-for-screens/reference/beat-nomination.md` — and a bounded
**novelty-lite filter** runs at lead-surfacing time — see
`fish-for-leads/reference/lead-gates.md`. All three share one firewall:
**direction in, novelty out, news never in the evidence middle.**)

## Novelty-lite (surfacing) vs the novelty scan (case) — not the same step

The surfacing-time check is a *filter*: one bounded search per candidate lead,
where a decisive hit suppresses the lead (recorded with its citation as a
`suppressed-covered` disposition) so obviously-reported candidates never cost
editor attention or a verification pass. It renders no verdict, and a lead
having *passed* it means nothing here.

The case-level novelty scan below is a *verdict*: it runs after verification,
on the exact verified claim (which usually differs from the surfaced story),
and it alone assigns the durable `coverage` value. Never skip it because
novelty-lite came up empty at surfacing — a miss in one bounded search is weak
evidence, and the claim has changed shape since.

## The novelty scan

After a finding is `verified` (true-in-data) and before it is promoted to
report-grade, one bounded agent (web search, capped queries, structured output)
adjudicates **discovery**. This separates two claims the pipeline otherwise
conflates:

- **"Is it true?"** — ours, and after verification we stand behind it at 100%.
  Coverage never weakens this.
- **"Is it new?"** — not ours to assert; the scan decides. Surrendering the
  discovery claim does **not** soften the verification claim.

Record a `coverage` verdict in the case's `case.md` frontmatter.

### Verdict vocabulary (a durable provenance attribute, not a kill switch)

- **`novel`** — no coverage found. *Always hedged* (see asymmetry). Highest
  scoop value.
- **`under-reported`** — covered, but our records add a dimension the coverage
  asserted-but-didn't-show, or missed (a named actor, an exact count/dollar, a
  mechanism). The sweet spot: the reporting validates the direction; the gap is
  our angle.
- **`well-covered`** — extensively reported; we add nothing the coverage lacks.

### The evidence is asymmetric

A *hit* ("here is the article, dated X") is strong, reliable evidence. A *miss*
("we found nothing") is weak — bounded by search recall, query phrasing,
paywalls, framing. So `novel` must always read **"no coverage found in a bounded
search,"** never "this is new." Be confident on hits; humble on misses. A miss
never licenses a stronger publication claim than the data alone supports.

### Date the coverage against the data window

Note whether coverage predates, is contemporaneous with, or postdates the corpus
window. If the records flag something *before/independently of* when reporting
picked it up, the **lead-lag itself is a finding** ("the filings showed this N
months before it was reported").

News citations go in a fenced "Prior coverage" section in `case.md` — **never**
in the evidence chain for any claim.

## Well-covered ≠ wasted — it's a precision exhibit

For a methods challenge (judged on capability/verifiability, not scoops), a
pipeline that **independently rediscovered a real story major outlets ran —
deterministically, from primary records, with the full data trail** is a
*stronger* demonstration than an unfalsifiable scoop. `well-covered` findings are
demoted as scoops but **kept, even foregrounded, as validation exhibits**: "our
newsroom surfaced X from filings alone; [outlets] reported the same — here are
the records." Calibration against ground truth is capability evidence.
