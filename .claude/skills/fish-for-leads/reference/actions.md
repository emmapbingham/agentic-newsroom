# The actions journal: provisional autonomy with editorial review

Every newsroom state change is an **action**: recorded in `actions`
(newsroom.db) with an actor, a basis, a priority, and a review state. Agents
act **provisionally** — including promoting leads, opening cases, and killing
them — and the editor reviews *afterward*, sampling from a ranked queue.
Safety comes from recording and reversibility, not from blocking: nothing in
the newsroom is ever deleted, kills carry rationale, evidence is append-only,
and overturning is always one action away.

**The one hard gate:** nothing crosses the system boundary — the findings
report, a comment request to a named person, anything published — unless its
action chain is **transitively acknowledged** by a human. "Report-grade =
every action in the object's chain is `acknowledged`." This is also how the
newsroom satisfies rules requiring human review of claims about named people.

## Actors (and how to know which you are)

- `editor` — the human made the call. Born `acknowledged` (reviewed_at = at,
  `reviewed_by` = that human).
- `agent-live` — agent-initiated, human present in the session. Reviewable;
  a human being in the room is not the same as having reviewed the action.
  If the editor consumed the output or reacted in-session, note that when
  acknowledging.
- `agent-auto` — unattended run (scheduled, headless, "overnight mode").

Detection rule: default `agent-live` whenever a human is conversing; claim
`agent-auto` only when the run was launched unattended; claim `editor` only
when the human explicitly stated the decision ("promote X", "pass on Y").

## Recording discipline

One row per state change, at the moment it happens. `basis` is one line: the
why, plus pointers (run id, evidence ids, citation). Executions are NOT
actions — screen runs stay in `screen_runs`; builds are actions because they
change what exists. Existing per-object fields (`leads.disposition`,
case frontmatter `status`) remain the object-local materialization; the
actions journal is the cross-object decision record and review queue.

Priorities (deterministic tiers; not vibes):
- **5** — kill / close / promote / verification verdict on report-bound work.
- **4** — promote/open on non-report-bound work; novelty-scan verdicts.
- **3** — derived-table builds, screen registrations, entity-resolution
  changes (they alter what every downstream consumer sees).
- **2** — duplicate-of routings, re-scopes.
- **1** — routine gate suppressions (reviewed as a tally, not one by one).

## Review semantics

- The queue = `unreviewed` actions, **grouped by object**, ranked by max
  priority then age. The editor acknowledges an object's chain in one move
  (`review_note: 'chain ack'` on the head action; mark the rest with the same
  note) — never force atom-by-atom review.
- Every sign-off records **who**: `reviewed_by` (a name from your newsroom's
  reviewer roster — in this newsroom, 'emma' | 'ian') is required whenever
  `review_state` leaves `unreviewed`. The transitive-acknowledgment gate is
  then auditable per person — the report can state exactly who reviewed each
  finding's chain.
- **Overturn** = append a new `editor` action (`action='overturn'`, basis
  says what replaces it) AND set the target row `review_state='overturned'`.
  Then perform the compensating state change (e.g. re-open, un-suppress).
  History is never edited.
- **Ignoring is allowed.** Unreviewed actions stay provisional indefinitely;
  posture shows their count and age so staleness is visible, not hidden.

## Provisional autonomy policy (what agent-auto may do)

Everything internal, in this priority order (closest-to-publication first):
open cases' logged NEXT steps → verification passes → gated fishing →
objective derived-table builds (validator required) → screen design. Including
provisional **promotion** (priority 4–5, recommend-and-open) and provisional
**kill** (priority 5, rationale required). Escalate-only, forever: crossing
the system boundary (above), subjective config tables, and characterizations
of named people beyond what a record states.

Guardrails:
- **K-cap:** an unattended run ends with ≤5 leads awaiting editor triage;
  everything else it generated is self-dispositioned with reasons
  (`suppressed-below-cut` in the basis for gate-passing leads under the line).
- **Budget cap:** a provisional (unacknowledged) promotion authorizes
  drilldown, but expensive stages (fleet verification, large builds) draw
  from a capped per-run budget until the promotion is acknowledged — the
  failure mode isn't a wrong decision, it's compounding spend on an
  unreviewed direction.
- Numbers born in unattended runs are unverified until a verification pass
  — same as scout numbers, same rule, no exceptions.
- Every unattended run pre-answers, per surfaced lead, **the first question
  the editor would ask** (interrogation is the drill layer; batch mode must
  pre-drill the predictable "wait, why?").
