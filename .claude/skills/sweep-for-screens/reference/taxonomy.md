# The contrast taxonomy

## Why a taxonomy

You cannot grep for "interesting." But interestingness decomposes: every lead
is **"X, compared against baseline Y."** Enumerating the kinds of comparison
turns open-ended idea generation into systematic coverage — and prevents a
fleet of agents from all converging on the obvious first idea. Partition the
idea space; don't roll the same dice N times.

## The six contrast types (the sweep checklist)

| Type | A lead of this type means… | Baseline |
|---|---|---|
| **outlier-vs-peers** | an entity is extreme on some distribution | the peer group's distribution |
| **self-over-time** | an entity suddenly changes | the entity's own history |
| **source-vs-source** | two parts of the corpus contradict each other about the same fact | the other source |
| **absence** | something expected is conspicuously missing | what comparable entities do, or what one signal implies another should show |
| **data-vs-law** | records violate the regime's own rules, formats, or norms | the legal/format requirement |
| **population-structure** | a systematic pattern across a whole class, not a one-off | a null model of no structure |

Notes from use:
- *source-vs-source* leads are born verified — the contradiction is the finding.
- *absence* leads are underexplored (hard to grep for, trivial once a complete
  panel exists) but are the most exposed to coverage artifacts — a gap in the
  scraper's collection looks exactly like a meaningful silence. Always carry
  coverage flags.
- *data-vs-law* finds cheap, named, fully-sourced leads.
- *population-structure* leads are the most statistically defensible and hardest
  to red-team away.

## Grains

The corpus's natural units of analysis — what a row of a derived table is
*about*. For this corpus: member, registrant/firm, client, lobbyist, issue,
committee. Time is not a grain — it is folded into contrast types
(*self-over-time* is the temporal contrast; any grain can carry a month/quarter
axis).

## Building the sweep grid

1. Cross contrast types × grains (6 × G cells).
2. Prune cells that are nonsensical *for this corpus* (no second source for that
   grain; no stable id to track over time). Record the pruned list — independently
   demanded pruned cells have been wrong before.
3. One scout per cell; "your beat is *<contrast>* at the *<grain>* grain — stay
   in your cell; depth beats breadth."

The grid also enumerates the derived-data space: for each cell, does a derived
table exist that makes its contrast computable? The gaps, ranked by how many
screens they'd serve, are the table-proposal space.
