# Log — insurance-jurisdiction-no-press-lift

## 2026-07-02
- did: promoted from `leads` (slug=insurance-jurisdiction-no-press-lift,
  screen_run_id=21 — the lead was surfaced by using
  `derived_committee_quarter_press` standalone, ranking `topic_share` within
  a committee against its own other jurisdiction, not from the
  `committee-lobby-press-lead-lag` screen's actual lead-lag analysis, which
  found no timing signal — see that screen's notes in `newsroom.db`).
- did: wrote `analysis/ins_committee_press_share.py` to re-derive every
  number cleanly from `db/gain.db` (read-only), rather than trust the ad hoc
  session numbers carried over from the lead. Re-derivation numbers differ
  slightly from the lead's scout numbers (e.g. HOU 40.48% vs the lead's
  39.4%) — the method is the same, this is just the clean version.
- found: E1–E5 in `evidence.md`. Core finding (E4) holds: HSBA04 and SSBK04
  show no/minimal INS topic-share lift vs. corpus baseline, while showing
  real lift on their other jurisdiction. Survived two adversarial checks:
  the shared `ISSUE_KEYWORDS['INS']` recall bug (E1–E2 — real, but isolated
  to INS, not systemic) and the "insurance is just inherently quiet" boring
  explanation (E5 — mostly ruled out, INS is moderately-but-not-extremely
  quiet per lobbying dollar).
- did: wrote up the keyword-recall-audit method and the broadened-keyword
  disambiguation method as reusable Methodology sections in `case.md`,
  per editor request — meant to be picked up again for a different
  committee/topic pair without re-deriving from scratch.
- dead ends: none yet — first pass through the lead's own confirm/kill list.
- open questions: (1) the technical-density boring explanation (is insurance
  just harder to message on than housing/banking, independent of
  lobbying/salience) is untested — candidate comparison committee is HSJU
  (House Judiciary) on CPT (Copyright/Patent/Trademark), which also scored
  low in E5's dollar-normalized ranking; (2) committee tenure not checked
  per-member — a recently-seated member wouldn't be expected to show lift
  yet; (3) the shared `ISSUE_KEYWORDS['INS']` fix is still not promoted into
  the actual derived tables, only used as this case's local override.
- NEXT: test the technical-density boring explanation against HSJU/CPT. If
  it also shows a jurisdiction-vs-baseline gap, the pattern generalizes
  beyond insurance and this case's newsworthiness framing needs rethinking;
  if HSJU shows normal lift on CPT, insurance stays the outlier and the
  case is ready for builder→skeptic→judge verification.

## 2026-07-03
- did: ran `analysis/ins_ml_classifier_crosscheck.py`, cross-checking E4
  against the new ML press-topic classifier (`M0`,
  `derived_press_issue_labels`, see
  `docs/press-issue-classifier.md`) as a
  second, structurally independent measurement method.
- found: E6 in `evidence.md`. The classifier is a WORSE instrument than
  the case's hand-disambiguated `BROAD_INS_KEYWORDS` on this code — it
  recalls only 16.2% of even the narrow (already-broken) keyword set, and
  only 25.6% of unambiguous NFIP/flood/property/casualty content, while
  independently reintroducing ACA/health-insurance false positives (the
  same domain-mismatch failure mode the classifier's own plan doc
  documented). Despite that, the committee-level pattern reproduces:
  neither HSBA04 nor SSBK04 shows a meaningful INS jurisdiction lift under
  the classifier either. Two methods with different, uncorrelated failure
  modes agreeing on the qualitative conclusion strengthens confidence the
  core finding isn't a keyword-map artifact.
- dead ends: the classifier is not a usable replacement or improvement for
  this case's INS measurement — noted for anyone tempted to swap
  `BROAD_INS_KEYWORDS` for `derived_press_issue_labels` in a future
  session; don't, without re-checking recall the way this entry did.
- NEXT: unchanged — still need the HSJU/CPT technical-density check, then
  builder→skeptic→judge.
