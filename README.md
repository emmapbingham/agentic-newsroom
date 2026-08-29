# agentic-newsroom (GAIN Entry)

Our entry for the [Agentic AI in Investigative Journalism Challenge](https://generative-ai-newsroom.com/announcing-the-winners-of-the-agentic-ai-investigative-challenge-76f119cc35ca) hosted by Northwestern GAIN. 

**Team:** Emma Bingham and Ian Clester.

**Corpus:** House + Senate lobbying disclosures (LDA filings and LD-203
contributions) joined with congressional press releases, 2022 – 2026 Q1, built
into one SQLite database (`db/gain.db`) where every row keeps its source
record's ID or URL.

## Human remarks
This is Emma. (The rest of the README and findings-report are written by Claude with my assistance.) My team set out to develop an LLM-forward discovery engine that could surface interesting stories from a hitherto-unknown dataset under the direction and judgement of a human collaborator. The intention was to explore maximally what LLMs could do in this context, whether they could be used across the full data research pipeline. We envisioned a virtual newsroom of little Claudes that go out and try to collect leads and evidence and bring it back for human judgment. 

At times, we found that the LLM produced more than a human could reasonably keep up with and evaluate, and at these points we had to intervene and revise skills to make them more human-collaborator-friendly. At other times, the LLM surprised us with unique insights or strange fixations. We found that the LLM was an unreliable judge of what made an interesting story, confusing methodology for stories, giving us overused or odd narratives, or getting stuck on one person or topic. However, it was of course tireless and always ready to surface more leads or push on our open investigations.

Some of our findings have more of a 'hook' than others. Our top findings are the first two in findings-report.md, on the JACK Act and a Texas gaming bill. The others are interesting, but not necessarily ready for primetime as 'stories'. 

Overall, I think our final skills package is nothing if not fun to use — the fish-for-leads skill especially feels a bit like playing the claw machine in an arcade or, yes, fishing.

From Ian: We strove to make the system robust and useful. We designed everything for reproducibility, as a chain of transformations and inferences ultimately rederivable from the original data. As we worked (with Emma doing the bulk of the work with Claude on investigating leads), we found that we had a surfeit of machine time and tokens relative to human time and attention. Much time was spent reviewing leads or asking questions that Claude (via Opus or later Fable) could probably have come up with itself, adversarially. Thus, we tried to find ways to redesign the workflow to benefit from additional LLM inference without relinquishing human judgement: ways to generally "make progress" without forgetting what a human signed off on vs. what Claude thought was worthwhile, and ways to make the most of limited human attention by allowing Claude to autonomously promote or prioritize leads for when a human was available to dig into the weeds of a story. We only started to shift in this direction towards the end of the competition period, and we expect that there is still more to be done to develop adaptable workflows that can make the most of whatever combination of resources (human or machine) is available in different teams, projects, and environments.

## What's in this repo

| Path | What it is |
|---|---|
| `findings-report.md` | The findings report: five findings + two method demonstrations |
| `.claude/skills/` | Seven MIT-licensed Agent Skills (spec-validated with `agentskills validate`) |
| `docs/beat_book.md` | The corpus **beat book** for this dataset — schema map, bridges, data traps, SQL recipes |
| `scripts/` | The deterministic DB build pipeline: schemas, ingesters, validators, derived-table builders |
| `investigations/` | Full investigation working state — every case file, plus the `newsroom.db` editorial ledger |
| `REPRODUCING.md` | How to rebuild the database and re-derive every number in the report |
| `figures/` | Interactive D3 timeline for the ACU method demo (self-contained HTML + PNG) |
| `docs/` | Per-source database manuals |
| `sources/` | External-data provenance manifests (source, license, retrieval date) |
| `*.ipynb` | Orientation + exploration notebooks over the built database |
| `LICENSE` | MIT |

### Using the skills

The seven skills are the most reusable artifact here. To use them in your own
project, copy them into your skills directory:

```bash
cp -r .claude/skills/* ~/.claude/skills/      # user-level, available everywhere
# or, project-level:
cp -r .claude/skills/* /path/to/project/.claude/skills/
```

Four are corpus-agnostic (`profile-dataset`, `ingest-to-sqlite`,
`orient-sqlite-corpus`, `explore-sqlite-corpus`) and work on any structured
dataset. The other three (`sweep-for-screens`, `fish-for-leads`,
`track-investigation`) encode the newsroom workflow and assume a sourced
SQLite corpus plus the `newsroom.db` ledger (schema at
`scripts/schema_newsroom.sql`).

Those last three also ask you to supply a **beat book** — the doc holding your
corpus's schema, bridges, and data traps. This repo's is
[`docs/beat_book.md`](docs/beat_book.md); it is corpus-specific project
documentation rather than a reusable skill, so it lives in `docs/`.

### A note on the investigation files

`investigations/` ships the complete working state, including cases that were
**killed** or are still **open** — hypotheses that named real people and did
not survive scrutiny. That is deliberate: a methodology that only shows its
wins isn't evaluable. Only `findings-report.md` represents concluded work.
See [`investigations/README.md`](investigations/README.md) before quoting
anything from a case file.

## The skills, in the order you'd use them

### Getting from raw files to a database you can trust

We first built skills that let Claude take an unfamiliar, semi-structured data
dump and turn it into a relational database a journalist can query and cite:

- **profile-dataset** — scans raw JSON/JSONL/XML/CSV at a high level: what
  fields exist, what could serve as a key, and whether an ID is a clean join
  key or needs entity resolution.
- **ingest-to-sqlite** — ingests the data into SQLite with a
  verifiability-first methodology: source IDs preserved as keys, money stored
  raw *and* parsed, every fact row stamped with its source record, and row
  counts reconciled against the raw files by a bundled verifier script.
- **orient-sqlite-corpus** — generates a Jupyter notebook that answers "what
  is in this database, how complete is it, and where should we be cautious?"
  with live, re-runnable queries.
- **explore-sqlite-corpus** — generates a blank-canvas exploration notebook
  (connection, helpers, plot style, no pre-written queries) so a
  domain-knowledgeable human can drive.

### The agentic data newsroom

On top of the database, three skills hand off to each other in sequence and
share a small ledger database (`newsroom.db`) that records every screen, run,
lead, and decision — so both the human and the agent can always inspect what
was proposed, what was tried, what was discarded, and why:

- **sweep-for-screens** — the rare, expensive step: fans agents out over
  the corpus with a taxonomy of deliberately dataset-agnostic prompts
  ("who surged?", "who went quiet?", "what's lobbied but never talked
  about?") and registers the promising ones as *screens* — deterministic,
  re-runnable SQL ranking queries. The human can also just propose a screen
  directly.
- **fish-for-leads** — the everyday loop: pick a screen (or let Claude pick by
  priority), run it, and surface up to five *leads* — each a short plain-
  language story with the main players, the evidence, and the strongest
  innocent explanation. Candidate leads pass cheap gates first (is there a
  named actor? does a boring explanation win? has someone already covered
  this?), and everything — surfaced or suppressed — is logged with a reason.
  The human interrogates the leads in chat; the agent answers with checkable
  queries.
- **track-investigation** — when the human promotes a lead, this skill owns
  the case: a structured case file, an evidence log where every claim carries
  its query and source records, and a running activity log. It includes a
  novelty scan (is this already covered?) and a builder → skeptic → judge
  verification pass that builds the strongest version of the finding, tries
  to tear it down, and renders a verdict before anything is called supported.

The human journalist is present throughout: evaluating surfaced evidence,
asking questions, redirecting, and making every promote/kill/publish call.
Nothing reaches this report without a human-acknowledged decision chain, which
is how we satisfy the challenge's human-review requirement for claims about
named people.

## Skills → findings → cases

All five findings and both method demos were produced by the same pipeline —
screens designed via **sweep-for-screens**, surfaced by **fish-for-leads**,
investigated and verified under **track-investigation** — over the database
built with the four foundation skills. Each finding's case directory holds its
hypothesis log, evidence journal, and reproducible queries.

| Finding (in `findings-report.md`) | Case (`investigations/`) |
|---|---|
| The JACK Act's blind spots | jack-act-blind-spots |
| A New Mexico casino vs. a Texas tribal-gaming bill | sunland-park-ysleta-opposition |
| Three provisions Congress passed with no public pressure | invisible-provisions |
| How a federal privacy bill died (APRA) | apra-lobbying-coalition |
| Amazon's PAC money didn't buy silence | amazon-money-without-praise |
| Method demo: sizing a trade association's "legislative bench" | acu-legislative-bench |
| Method demo: a base-rate discipline for "critic takes money" leaderboards | critics-take-health-money |

## Reproducing the database and the findings

`scripts/` contains the complete deterministic build pipeline (schemas,
ingesters, validators — `python scripts/build_gain_db.py --validate` rebuilds
`db/gain.db` from the challenge data in ~7 minutes with row counts reconciled
against the raw source). Per finding, the exact SQL that reproduces the
report's numbers is in `investigations/<case>/queries.sql`, verified
2026-07-15. Start at [`REPRODUCING.md`](REPRODUCING.md), which also covers
where to get the corpus (`data/` is not redistributed here).

The newsroom ledger schema is at `scripts/schema_newsroom.sql`, and also ships
inside the fish-for-leads skill
(`.claude/skills/fish-for-leads/assets/schema_newsroom.sql`).

## Outside data (disclosure)

Everything below informs *context or verification*; lobbying/press claims in
the findings rest on the challenge corpus itself. Full manifests with
licenses and retrieval dates are in the [`sources/`](sources/) directory.

- **`unitedstates/congress-legislators`** (public domain) — the
  member↔bioguide crosswalk that links contribution honorees and press
  releases to members. Ingested into the database; every name-dependent claim
  carries the crosswalk's match method and confidence.
- **congress.gov API** (public domain) — bill status, cosponsorship, and
  action dates, used in the Amazon, credit-union, Sunland Park, and
  invisible-provisions cases.
- **Public oversight documents** — GAO lobbying-compliance audits (2020–2026)
  and a CRS report, load-bearing in the JACK Act finding; a Federal Register
  order and OpenSanctions used to characterize one lobbyist's conviction
  instrument correctly; CBO cost estimates and CMS documents (public domain)
  for the dollar figures in the invisible-provisions finding.
- **News coverage** — used to check novelty (is this already reported?) and
  to nominate areas to screen; never cited as evidence for a claim about the
  lobbying or press corpus. Where an article carries a load-bearing
  contextual fact outside the corpus (e.g. the 2026 Texas runoff result, or
  Wired's list of APRA opponents), the finding cites it explicitly.

## Conflicts of interest

None. Neither team member has a financial, professional, or personal
relationship with any individual or organization named in the findings.

Lobbying and political contributing are lawful, disclosed activities. Entries
state what the public records show, not motive, and no entry alleges unlawful
conduct. Where an entry's own caveats bound what it claims, they are stated in
that entry.

## License

Everything in this repo is MIT-licensed (see [`LICENSE`](LICENSE)); each skill
also declares `license: MIT` in its frontmatter.

Two exceptions to note, neither ours to license: the challenge corpus itself
(not redistributed here — see [`REPRODUCING.md`](REPRODUCING.md)), and the
third-party government documents under
`investigations/jack-act-blind-spots/sources/` (GAO reports, a CRS report, and
a Federal Register order — all US Government works in the public domain).
