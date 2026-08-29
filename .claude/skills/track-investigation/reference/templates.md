# Case-file templates

Copy these when promoting a lead to `investigations/<slug>/`. Keep them terse —
they're a working record, not prose. Status vocab: `open → supported → refuted
→ parked → killed | closed` (the last two are terminal — see
`reference/closeout.md`). Confidence: `low | medium | high`.

## Promoting a lead

When opening a case from a `leads` row in `newsroom.db`:
1. Read the lead's `story`, `claim`, `probe_sql`, `scout_number`,
   `boring_explanation`.
2. Seed `case.md` from `story` (→ why newsworthy) and `claim` (→ hypothesis).
3. Add the `scout_number` to `evidence.md` E1 tagged "unverified — re-derive."
4. `log.md` first entry: "promoted from leads (slug=<slug>, screen_run_id=<id>)."
5. Set `promoted_at` + `case_slug` in `newsroom.db` `leads` table.

## `case.md`

```markdown
# <Title of the case>

- **slug:** <slug>
- **status:** open
- **confidence:** low
- **coverage:** unscanned   ← novelty-scan verdict: novel | under-reported | well-covered
- **opened:** YYYY-MM-DD   **last updated:** YYYY-MM-DD

## Hypothesis
<The single falsifiable claim being tested, in one or two sentences. From the lead's claim field.>

## Why it's newsworthy
<Who is affected / what norm is in tension / why a reader should care. From the lead's story field — in plain language, not stats.>

## What would confirm it / what would kill it
- Confirms: <observable evidence that would support the claim>
- Refutes: <the innocent explanation / the lead's boring_explanation — what we'd expect if it's nothing>

## Verdict
<One line: the current verdict + confidence. Updated as it moves. No re-summary of evidence — that lives only in evidence.md.>

## Prior coverage
<Novelty-scan verdict and its evidence. Cite + date outside reporting here — a fenced provenance class, never cited as evidence for a Claim above. For under-reported/well-covered, name what the coverage already established and what our records add. novel reads "no coverage found in a bounded search.">

## Sources / legal-risk notes
<Named individuals/orgs; anything an editor or lawyer must review before publication.>
```

## `evidence.md`

One block per piece of evidence. The query/script + source ids are mandatory.
Headline numbers live **only here** — do not restate them in `case.md` or copy
them into `log.md`.

```markdown
## E1 — <one-line claim this evidence establishes>
- **query/script:** `queries.sql#q1`  (or `analysis/panel.py`)
- **result:** <the number/rows, summarized>
- **source records:** filing_uuid abc… (https://lda.gov/filings/public/filing/abc…/print/
  for lobbying filings, or https://lda.gov/filings/public/contribution/abc…/print/
  for LD-203 contribution filings — different path per record type),
  press url …, house_filing_id …
- **caveats:** <honoree confidence; sparse money; base rate; etc.>
- **verdict:** supports | refutes | neutral | needs-follow-up
```

## `log.md`

Append-only journal. Records what was done and decided — not the numbers
themselves. Point to evidence blocks by id; don't copy their figures.

```markdown
## YYYY-MM-DD
- did: <what I queried/built/checked>
- found: see E# in evidence.md
- dead ends: <what didn't pan out, so we don't repeat it>
- open questions: <…>
- NEXT: <the single next step — the resume point>
```

## `queries.sql`

Plain SQL, one labeled block per query, so every cited number reruns.

```sql
-- q1: <what this answers>
SELECT ...;

-- q2: <...>
SELECT ...;
```
