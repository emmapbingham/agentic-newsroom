# Closing out a case

Every case ends one of two ways. Both are terminal frontmatter states; neither
one deletes evidence, log entries, or queries — the whole point of this
skill's file discipline is that a closed case stays exactly as re-derivable as
an open one.

Status vocab: `open → supported → refuted → parked → killed | closed`.
`supported`/`refuted` are verification-pass verdicts on the *claim* — a case
can sit at `supported` for a while before someone decides to close it out.
`killed`/`closed` are decisions about the *case* (do we keep working it).

## Path 1 — Kill it

Use when the data stopped supporting the hypothesis: the skeptic's
refutation held, a key evidence item collapsed under scrutiny, or a
`refuted` verdict from the builder→skeptic→judge pass is the final word and
nobody expects new data to change that.

Checklist:
1. **Write the rationale directly into `case.md`**, as a fenced paragraph
   under the Verdict section (don't bury it in `log.md` only — `case.md` is
   what a future reader opens first). State plainly: what was claimed, what
   killed it, which evidence item (`evidence.md` E#) forced the call. This is
   mandatory, not optional — a case file that just says "killed" with no
   reason is worse than not closing it at all, because it looks like
   abandonment rather than a verdict.
2. Set frontmatter `status: killed`. Leave `confidence` as whatever the
   evidence actually supports (usually `low`, but state it, don't blank it).
3. `log.md` final entry: `did` = the kill decision, `found` = pointer to the
   evidence that did it, `NEXT` = literally "none — case killed, see Verdict
   in case.md" (so a future session doesn't waste a resume-check).
4. Do **not** delete `evidence.md`, `queries.sql`, or prior log entries. A
   killed case is itself sometimes a story ("we checked, it's boring, here's
   the receipts") or at minimum protects against re-running the same dead
   end later. If the `boring_explanation` from the original lead is what
   killed it, say so explicitly — that's the multiple-comparisons ledger
   working as intended.

## Path 2 — Close it out (still newsworthy, done with research for now)

Use when the builder→skeptic→judge pass returned `supported` (or the
evidence is otherwise as strong as it's going to get without new data
sources) and the next step is editorial/publication work, not more
querying.

Checklist:
1. **Condense the Verdict section in `case.md` to a single current
   paragraph.** Over the life of a case this section tends to accrete a new
   paragraph after every evidence update (E5 said X, then E8 revised it,
   then E9 added Y...) — that history is valuable but belongs in `log.md`
   (append-only, that's its job), not in `case.md`. Rewrite Verdict as what
   you'd want a busy editor to read once: the claim, the confidence, the one
   or two things still open before publication. This is the artifact — there
   is no separate closing report per case.
2. **Confirm frontmatter matches reality**, not just the Verdict prose:
   - `status` → `closed`
   - `confidence` → what the judge actually rendered (don't leave a stale
     `low` from before verification, per the pattern this checklist exists to
     prevent)
   - `coverage` → the actual novelty-scan verdict (`novel` /
     `under-reported` / `well-covered`), not a leftover `unscanned` from
     before the scan ran. This is the single most common staleness bug in
     practice — the frontmatter line doesn't get touched when the prose
     below it does, because nothing forces it to.
3. **List pre-publication line items explicitly** — anything that doesn't
   block the core claim but should be checked before anything ships (an
   unreconciled dollar figure, a name whose position is inferred rather than
   quoted, an active-candidate/legal-risk sensitivity). Put these in Sources
   / legal-risk notes, not buried in a log entry — that's the section an
   editor or lawyer actually reads.
4. **`log.md` final entry**: `did` = the closeout, `found` = pointer to
   whatever prompted closing now (verification pass, editorial call,
   deadline), `NEXT` = the actual next step if there is one (usually
   "publication," or a named follow-on case/thread if the case spawned one).
5. Closed cases stay queryable and citable exactly as before — closing is a
   status change, not an archive/deletion step. A cross-case findings report
   reads closed cases' Verdict + Prior coverage sections directly rather than
   each case producing its own report file.

## What NOT to do in either path

- Don't delete or rewrite `evidence.md` entries to "clean up" a killed case
  — the refuting evidence is exactly what makes the kill decision legible
  later.
- Don't leave frontmatter unchanged while updating prose (the bug this
  checklist exists to prevent) — frontmatter is what's scanned across many
  cases at once; stale frontmatter silently breaks that.
- Don't write a new report file per case. If the findings report needs case
  content, it pulls from `case.md`'s Verdict/Prior-coverage sections — adding
  a parallel `report.md` per case creates a second place for the verdict to
  drift out of sync with the evidence.
