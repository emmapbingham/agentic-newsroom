# The surfacing gates: filter before the editor pays attention

## Contents
- Gate order (cheapest first): 1. template collapse · 2. actor test ·
  3. boring explanation first · 4. novelty-lite
- Drill moves that earn their cost (pair-grain and entity leads)
- The disposition feedback loop

The pipeline was built to guarantee surfaced leads are *true and traceable*.
These gates add the missing test: *worth the editor's time*. A story needs four
things — a real deviation, truth, novelty, and a named actor with stakes. SQL
tests deviation; the case-level verifier tests truth. Without these gates,
novelty gets tested **after** verification (the most expensive ordering
possible) and actor/stakes never gets tested at all.

The gates run at surfacing time, inside the go-fish loop, on the top of a
screen's shortlist — never inside the screen's SQL. Screens stay dumb and
complete: they are the multiple-comparisons ledger, and editorial taste leaking
into the ranking query is a selection effect you can no longer count.
Everything a gate suppresses still gets a `leads` row with a `suppressed-*`
disposition — filtered is not the same as unrecorded.

## Gate order (cheapest first)

### 1. Template collapse

If the top-N candidates instantiate one story template over N entities, they
are **one lead** (the pattern) with an exemplar table — not N rows.

*Worked example:* the 2026-07-06 `client-press-mention-gap` run surfaced five
separate leads — Gilead ($13.6M lobbying income, ~0 press mentions), Fluor,
Emergent BioSolutions, RELX, Omeros — all reading "Company X reported $NM in
Senate lobbying income but was never named in congressional press releases."
Zero were promoted. That cost the editor five reads to render one judgment
("this pattern isn't a story as surfaced"). One pattern-lead with a 5-row
exemplar table costs one read.

### 2. Actor test (route by screen grain)

Every screen carries a `grain`:

- **actor** — shortlist rows name a registrant/member/client/lobbyist. Surface
  as a lead only if the actor *did something*: filed, paid, surged, went
  quiet, switched sides. "Entity X has property Y" with no choice behind it is
  a pattern observation wearing an actor's name.
- **structure** — rows are issue/committee/code-level patterns. Never surface
  the category observation raw. Spend one cheap drill pass first: *"who are
  the top 3 actors inside this anomaly, and does any have a motive?"* Surface
  the actor-grain result; keep the structural finding as context.

*Worked example:* the `quiet-issue-quadrant` family surfaced 19 issue-grain
leads for 3 promotions. Its best outcome — the Sunland Park case — was **not**
the surfaced lead ("tribal gaming is quiet"); it appeared only after a
drilldown found a single named racetrack paying a lobbyist every year since
2022 to oppose a rival's casino bill. The drill pass moves that conversion
from case-time (expensive, after promotion) to surfacing-time (one query and
a paragraph).

### 3. Boring explanation first

Write `boring_explanation` **before** `story`, not after. Written after, it is
documentation of a decision already made (the historical record: 58/58 leads
had the field filled and it filtered nothing). Written first, it is a
hypothesis test: if the innocent account beats the story, log the row with
`disposition='suppressed-boring'` and move on.

### 4. Novelty-lite (bounded prior-coverage check)

One bounded web search on the candidate's core claim (1–2 queries,
cheap-model tier is fine).

- **Decisive hit** — a dated article making the same finding: log the row with
  `disposition='suppressed-covered'` and the citation in `disposition_reason`.
  Don't render it to the editor.
- **Miss** — neutral. Surface the lead, and never describe it as "novel":
  hits are strong evidence, misses are weak (recall, phrasing, paywalls).

This is a *filter*, not a verdict. The case-level novelty scan
(`track-investigation/reference/prior-art.md`) still runs after verification,
on the exact verified claim, and owns the `coverage` vocabulary
(novel / under-reported / well-covered). The two share the firewall: news
never enters a claim's evidence chain.

*Worked example:* the `ways-means-chair-money-magnet` case consumed a full
builder→skeptic→judge verification pass — the numbers held — and was then
killed by a February 2023 Roll Call article naming Jason Smith's fundraising
explicitly. One search at surfacing time would have caught it before any
verification spend. This gate exists because that happened.

## Drill moves that earn their cost (pair-grain and entity leads)

Three cheap checks, run in this order, before writing any story:

1. **Read the titles.** For any lead built on document matches (press mentions,
   filing descriptions), pull every matched title/first-line — at N≤20 this is
   one query and one read, and it is the cheapest tone instrument that exists.
   Direction (advocacy / attack / announcement / form-letter / name-collision)
   is usually visible in titles alone, and it reorders candidates more than
   any score column. (Caught: a rank-1 "mention" pair that was a word
   collision; a $37k pair whose mentions were two form letters.)
2. **Check the innocent tie.** For (member, company) pairs: is the company a
   district/state employer? Is the member on the committee the company's
   issues run through? Is the pairing exactly what the member's known public
   profile predicts? Any yes = the boring explanation has a head start and
   the story must clear it explicitly.
3. **Audit the sum's provenance shape.** Before believing any ranked dollar
   figure, GROUP BY the raw tuple underneath it and look for exact copies —
   ask *who files this record and how many times does one event get filed*.
   (Caught: LD-203 contributions duplicated across registrant + per-lobbyist
   filer copies, inflating a pair 2.3×.)

## The disposition feedback loop

Gates suppress with `suppressed-covered` / `suppressed-boring`; the editor
triages survivors with `pass-boring` / `pass-covered` / `duplicate-of` /
`artifact` / `promoted` (one line of `disposition_reason` each). Before
surfacing anything, read the last ~15 dispositions — they are the editor's
taste, recorded. If the same shape keeps drawing `pass-boring`, stop surfacing
that shape; if a screen's leads draw only passes across ≥3 runs, flag the
screen for deprioritization in posture.
