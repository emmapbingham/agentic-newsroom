# Fleet run-economics (sweeps)

Rules for sweep spending. Numbers come from the first full grid sweep (26 scouts
+ synthesis + clerk: 2.2M tokens, ~2h wall clock, 2,568 tool calls — 4× the
wall-clock estimate).

Go-fish (one screen → 3–5 leads) is deskside-free. These rules apply to fleet
sweeps only.

## The cost model

- **Deskside deterministic work is free**: derived table builds, screen runs,
  config curation. This is the default mode.
- **Screens are free forever** once their derived table exists — run them weekly.
- **Fan-outs are priced by fleet size × per-agent thoroughness.** Model tier
  matters 3×; an uncapped brief can matter 10×. Both are set in the brief.
- **Sweeps are capital expenditure.** A good one yields weeks of new screens;
  don't re-run until the prior slate is exhausted. Re-sweeps target only thin or
  mispruned cells.

## Hard rules

1. **Never launch a fleet on an unflown brief.** Pilot exactly one agent,
   measure tokens + tool calls + output quality, then fan out. One ~85k-token
   pilot revealing "this brief produces ~100 tool calls per agent" pays for
   itself the moment the fleet exceeds two agents.
2. **Probe budgets in every brief.** Write: "verify with at most N queries;
   prefer cheap COUNT/EXISTS probes; marking something unverified is
   acceptable." Thoroughness should be a dial you set, not a temperament you
   discover.
3. **Output ceilings.** "2–5 proposals" yields 5 from nearly every agent. Ask
   for "your best 2, plus one-line runners-up" — halves downstream synthesis
   input.
4. **Tier models by fleet size, not task dignity.** Cheap tier earns its place in
   fan-outs (×N multiplies the savings); a single-agent step can afford the
   better model (×1 multiplies nothing, and failure costs more than the savings).
   Put the expensive model where judgment concentrates: synthesis, adjudication.
5. **Subagents inherit the parent model by default** — set the model explicitly
   on every fan-out call or pay the flagship rate × N.
6. **Hard token ceiling on every workflow** — a miscalibrated brief should stop
   itself, not eat the usage window.
7. **Verify `args` reach the script** (log them first thing) before launching
   the fleet; a silent fallback corrupts every downstream label.
8. **Minimal reading lists.** N agents × redundant docs = the dominant input
   cost. Point agents at one doc (or a condensed cheatsheet).
9. **Concurrency is capped by cores** (≈ cores − 2, max 16). Estimate wall
   clock in waves, not agents.
10. **Probes need timeouts; fleets need a post-run process sweep.** Briefs
    should say "wrap probes in `timeout 60`"; after any fleet run, check for
    leftover processes (`pgrep -af 'sqlite3|python'`).

## Editorial-attention economics

- Everything that reaches the editor is pre-verified and carries provenance.
- The reaction loop: direction in (one line), artifacts out (files + DB rows),
  judgment in between. Completed agents return cached — "kill, tweak, resume"
  does not re-bill finished work.
- Visibility = views over canonical artifacts (Datasette over newsroom.db);
  never a separate reporting channel agents must remember to feed.
