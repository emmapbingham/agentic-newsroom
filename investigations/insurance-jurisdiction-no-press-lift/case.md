# Insurance jurisdiction, no press lift

- **slug:** insurance-jurisdiction-no-press-lift
- **status:** open
- **confidence:** low
- **coverage:** unscanned
- **opened:** 2026-07-02   **last updated:** 2026-07-02

## Hypothesis

Members of the two Senate/House subcommittees with formal jurisdiction over
insurance regulation (House Financial Services — Housing and Insurance;
Senate Banking — Securities, Insurance and Investment) show no meaningful
press-release attention lift on insurance relative to the chamber-wide
baseline, even though the same members show a real messaging lift on their
committee's *other* assigned jurisdiction (housing, financial markets) and
even though insurance is a real, substantial lobbying target ($137M
apportioned Senate income, 2022–2026).

## Why it's newsworthy

Committee jurisdiction is supposed to be where a member's public voice and
their institutional power line up — the member who sits on Housing talks
about housing, the member who sits on Financial Services talks about
finance. That pattern holds for every jurisdiction checked in this corpus
except insurance. A member can sit on the committee that writes insurance
policy, take testimony from the industry, and vote on insurance bills,
while saying almost nothing about it to their own constituents — even
though the industry itself is spending real money lobbying that same
committee. If this holds up, it's a "say vs. pay" gap specific to one
industry's committee relationship, not a general finding about Congress
being quiet on insurance (which — see E5 — it isn't an outlier; it's
moderately quiet in line with the lower-middle of comparably-sized
industries, not silenced).

## What would confirm it / what would kill it

- **Confirms:** the committee-vs-baseline gap holds for INS specifically
  while not holding for the same committees' other jurisdiction; the gap
  survives a corrected (non-buggy) keyword measurement; the gap isn't
  explained by "insurance is inherently unnewsworthy" (dollar-normalized
  press volume is not abnormally low for insurance corpus-wide).
- **Refutes / innocent accounts to clear:**
  - *Keyword measurement artifact* — the shared `ISSUE_KEYWORDS['INS']` map
    undercounts. **Tested (E1–E2): confirmed real and isolated to INS, fixed
    with a broadened case-local keyword set; the gap survives the fix.**
    **Further tested (E6): a completely independent, non-keyword ML
    classifier — with its own different failure modes — reproduces the
    same qualitative no-lift finding, further reducing the odds this is a
    measurement artifact specific to LIKE-based keyword matching.**
  - *Insurance is just an inherently quiet/boring topic* — nobody talks
    about it, committee or not. **Tested (E5): mostly ruled out** —
    insurance's press volume normalized by its own lobbying-dollar size
    ranks 14th-quietest of 53 comparably-sized industries (26th
    percentile) — moderately quiet, but well above the genuinely silent
    codes (GAM, SPO, CPT, CPI, CSP all rank markedly lower), not a
    standout outlier.
  - *Insurance is harder to message on than housing/banking* (technical
    density, not silence) — **not yet tested.** Needs a comparison
    committee with similarly technical, non-emotional subject matter (e.g.
    Copyright/Patent/Trademork, `CPT`, also scored low on the
    dollar-normalized list — see E5) to see if *that* committee also shows
    a jurisdiction-vs-baseline gap. If it does, "technical topics don't get
    committee-driven messaging lift" generalizes and this isn't
    insurance-specific. If it doesn't, insurance is the outlier.
  - *Committee tenure* — members who just joined the subcommittee
    wouldn't be expected to show elevated topic share yet; the roster
    history only resolves cleanly back to 2022-01-04 (see the Methodology
    section's roster-join caveat). Not yet checked per-member.

## Verdict

**Open, low confidence.** The core comparison (E3–E4) is real and survived
two adversarial re-checks (E1–E2, the keyword bug; E6, an independent ML
classifier cross-check) and one boring-explanation test (E5, "insurance is
inherently quiet" — ruled out). It has NOT yet been through
builder→skeptic→judge verification, and the remaining boring explanation
(technical-density messaging difficulty) is untested. Small N (2
committees) — this is a suggestive pattern, not yet a statistically robust
one.

## Prior coverage

Unscanned — novelty scan not yet run.

## Methodology (reusable — reapply to a different committee/topic without re-deriving)

Two reusable techniques came out of building this case. Both are meant to
be picked up again for a different committee-topic pair, not re-invented.

### 1. The keyword-recall audit (catch a broken `ISSUE_KEYWORDS` entry)

**The problem:** every derived table that measures "press attention to
topic X" (`derived_issue_quarter_volume_press`,
`derived_committee_quarter_press`, `derived_member_press_topic_panel`) uses
the same shared `ISSUE_KEYWORDS` map (in
`scripts/build_derived_issue_quarter_volume_press.py`) — a hand-curated
list of LIKE-match phrases per LDA issue code. If one code's keyword list
is too narrow, every downstream "X is quiet" finding for that code is
built on undercounted data, and a real silence claim becomes indistinguishable
from a measurement artifact.

**The diagnostic:** for any issue code with an obvious single bare-word
anchor (e.g. "insurance" for `INS`, "bank" for `BAN`), compare:

```sql
SELECT
  (SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%<bare_word>%') AS bare_n,
  (SELECT count(*) FROM press_releases WHERE <the code's ISSUE_KEYWORDS OR'd together>) AS matched_n;
```

A well-built keyword set usually **exceeds** its own bare-word count
(because it includes related terms beyond the single word — e.g. `BAN`
also catches "loan," "mortgage," "credit union" without the word "bank").
A keyword set that recalls **well under 100%** of its own bare word,
*and* is a clear outlier against other codes' ratios, is a red flag.

**Saved as a shared, reusable script:** `scripts/audit_issue_keyword_recall.py`
runs this across every code with a hand-picked bare anchor in its
`BARE_ANCHORS` dict (26 of 75 codes as of this case). Add a code's bare
anchor to that dict and re-run to audit a new code.

**What this case found:** `INS` scored 0.23 (only 23% recall); every other
audited code scored 1.29–13.74. INS is an isolated bug, not a systemic
problem — see E1–E2.

**Before trusting ANY "topic X is quiet" finding in this corpus:** run this
audit on X first if it has a natural bare-word anchor. If it's not been
audited yet (49 of 75 codes are unaudited as of this case), don't assume it's
fine — assume it's unknown.

### 2. Broadening a narrow keyword set without over-matching (the disambiguation step)

Once a code's recall is confirmed low, the fix is NOT "just match the bare
word" — that over-matches. For `INS`, matching bare "insurance" would sweep
in ~4,700 releases about *health* insurance (HCR's topic) and *unemployment*
insurance (UNM's topic), corrupting three codes' numbers at once instead of
fixing one.

**The method used here:** pull a random sample of bare-word matches
(`ORDER BY random() LIMIT 15` is enough to see the pattern), read them, and
identify the phrases that specifically signal the LDA code's actual
subject — for INS, that meant insurance-AS-A-REGULATED-INDUSTRY language
(insurer, insurance company/companies, insurance market/rate, and the named
product lines: homeowners/property/auto/flood/life/disability/title/casualty
insurance) as opposed to insurance-AS-A-BENEFIT language (health insurance,
unemployment insurance — which dominate the bare-word count but belong
elsewhere).

**Verify the fix doesn't over-correct:** the broadened set's match count
should land somewhere between the old (too-narrow) count and the bare-word
count — NOT at or above the bare-word count, unless you have a specific
reason every bare mention truly belongs to this code (rare). For INS: old
1,422 → broadened 2,406 → bare word 6,159. Landing well short of the bare
word, with a documented reason (health/unemployment insurance excluded), is
the sign of a disciplined fix, not a rubber-stamped one.

**Status:** this broadened set is a case-local override
(`BROAD_INS_KEYWORDS` in `analysis/ins_committee_press_share.py`), not yet
promoted into the shared `ISSUE_KEYWORDS['INS']`. Promoting it would mean
rebuilding `derived_issue_quarter_volume_press` and
`derived_committee_quarter_press`, and re-verifying `quiet-issue-quadrant`'s
existing INS ranking (which currently rests on the narrow, broken set) —
flagged as an open task, not done as part of this case.

### 3. Point-in-time committee-roster attribution (avoid misattributing press to the wrong Congress)

**The problem:** `member_committees` (built by `scripts/ingest_members.py`)
is a snapshot of the *current* roster only — using it to attribute a 2022
or 2023 press release to "the committee this member sits on" would
misattribute any member who has changed committees since.

**The fix:** join through `member_committees_history` instead (point-in-time
rosters, `valid_from`/`valid_to` windows, built 2026-07-02 — see
`docs/members_db.md`), filtering on the release's own date:

```sql
SELECT p.text
FROM press_releases p
JOIN member_committees_history h ON h.bioguide = p.bioguide_id
WHERE h.committee_id = ?
  AND h.valid_from <= p.date
  AND (h.valid_to IS NULL OR h.valid_to > p.date);
```

**Caveat carried forward:** roster snapshots resolve cleanly from
2022-01-04 onward (the earliest pulled snapshot); a handful of
newer-created subcommittees (e.g. `SSBK13` Digital Assets, created 2025)
have no roster before their creation date — see `organizing_gap` in
`derived_committee_quarter_press` for the flag that distinguishes this from
a real data gap.

## Sources / legal-risk notes

No allegation of wrongdoing. This is a pattern in what members choose to
say publicly vs. their institutional jurisdiction and the money flowing to
that jurisdiction — not a claim that any member did anything improper.
Named entities so far: no individual members named, only committee-level
aggregates (`HSBA04`, `SSBK04`). If individual members are named later
(e.g. checking committee tenure per-member), re-assess this section.
