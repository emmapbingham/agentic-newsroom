# Workflow patterns

Skeleton for the sweep — the one fleet moment in the newsroom pipeline. The
everyday go-fish operation is too simple to need a workflow skeleton; it lives
in SKILL.md. This pattern assumes the Workflow tool (deterministic JS harness
around schema-forced subagents; `agent()` spawns one, `parallel()` fans out,
`phase()` groups progress, `log()` narrates); it is **user-triggered** (spawns
many agents, is billed). Adapt the prompts; keep the structure. **No Workflow
harness?** Run the same shape with plain parallel subagents — one scout per
cell, then a single synthesis pass, then a filing pass — and enforce the brief
essentials below manually. The structure is the point, not the harness.
(The `no Date.now` rule below is a harness constraint: scripts must be
deterministic so a resumed run replays identically — pass timestamps in.)

## Grid sweep (capability expansion)

One scout per taxonomy cell → synthesis barrier → clerk. The barrier between
scout and synthesis is genuine (dedup needs *all* cells); everywhere else
prefer pipeline.

```js
export const meta = { name: 'grid-sweep', description: '…',
  phases: [{ title: 'Scout', model: 'sonnet' }, { title: 'Synthesize' },
           { title: 'File', model: 'haiku' }] }   // meta must be a pure literal

const MID_TIER = 'sonnet', CHEAP_TIER = 'haiku'  // bind to your stack's mid/cheap
                                                // models; mirror them in meta above
const DATE = (args && args.date) || 'undated'   // pass the date in args (no Date.now in scripts)
log(`args date=${DATE}`)                        // verify args plumbing BEFORE the fleet runs

const CELLS = [ /* pruned contrast × grain list, literal and reviewable */ ]

phase('Scout')
const scouts = (await parallel(CELLS.map(c => () =>
  agent(scoutPrompt(c), { label: `scout:${c.contrast}×${c.grain}`,
    phase: 'Scout', model: MID_TIER, schema: SCOUT_SCHEMA })
))).filter(Boolean)

phase('Synthesize')   // genuine barrier: dedup/rank needs every cell's output
const synth = await agent(synthPrompt(scouts), { schema: SYNTH_SCHEMA })

phase('File')         // clerk: write the JSON artifact FIRST (canonical), then
                      // parameterized inserts into the ledgers (never string-interpolated SQL)
const filed = await agent(clerkPrompt(synth), { model: CHEAP_TIER })
return { summary: synth.summary, filed }
```

Brief essentials (see `run-economics.md` for why): probe budget ("at most N
read-only queries, `mode=ro` always"), output ceiling ("best 2 + one-line
runners-up"), the baseline requirement ("no baseline, not a screen"), "stay in
your cell," and a minimal reading list. Scout output schema forces: screens
(name/baseline/description/derived_table_needed), table proposals
(name/answers/builder_script/feasibility), notes.

After the run: the editor writes (or commissions) a human-readable sweep report
next to the JSON — story engines, build slate, conflicts to adjudicate, run
economics. Mark everything scout-reported / editor-unverified.

## Operational notes

- **Pilot first** — fly one scout via a single subagent before any fan-out (rule
  1 in `run-economics.md`).
- **Stop/edit/resume**: workflows resume with completed agents cached — edit
  the persisted script and relaunch with the prior run id rather than re-paying
  finished work.
- **Live visibility**: agents write ledger rows and files as they finish — a
  Datasette over newsroom.db is already a live board; workflow `log()` lines
  narrate in-run.
