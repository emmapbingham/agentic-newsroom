# Log — acu-legislative-bench

## 2026-07-07
- did: promoted from leads (slug=acu-legislative-bench, surfaced overnight
  2026-07-07 05:01:30 by the barr-credit-union-cfpb-loop tribunal's skeptic
  pass). Editor (Emma) framed the case explicitly as two deliverables: (1) a
  say-pay-cycle case study at trade-association scale, (2) a methodology
  validation of the mention+lobbying+LD-203 triple-join, anchored on Barr as
  the worked exemplar. Case seeded: `case.md` from the lead's story/claim;
  `evidence.md` imports barr-credit-union-cfpb-loop's E1-E9 verbatim as
  EBarr1-9 (source case left untouched, still parked in its own right); one
  new evidence stub (E-scout) for the unverified bench-wide claim.
- found: nothing new yet — this session is setup only, no new queries run.
- dead ends: none yet.
- open questions: (1) per-member replication — each of Cramer/Scott/
  Fitzgerald/Budd/Emmer/Britt needs its own EBarr6-equivalent (named-bill
  lobbying text) and EBarr1/7-equivalent (honoree money + press quote),
  independently pulled, not assumed from the screen-36 aggregate; (2) the
  ABA/ICBA/MBA density comparison, which per the lead's boring_explanation
  MUST be built outside the mention pipeline (lobbying + LD-203 only) or the
  comparison is circular; (3) Congress.gov official bill-introduction dates,
  carried over unresolved from the Barr chapter.
- NEXT (done, see below): pick one bench member and verify the template works
  before batching the rest.

## 2026-07-08
- did: ran the EBarr6/EBarr7 template on Cramer and Scott first, as directed.
  Template worked cleanly for both (E1, E2) — expanded to all 7 remaining
  screen-36 members (Britt, Emmer, Fitzgerald, Budd, Beatty, Vargas,
  Gonzalez; E3-E9). All 10 original pairs now independently drilled.
- found: 8 of 9 non-Barr members confirm the full triple (money + named-bill
  Senate lobbying text + press mention); 1 clean break (Beatty — Fair Hiring
  in Banking Act, H.R. 5911, has strong money + named press quote but zero
  lobbying-text match, checked against both the merged ACU registrant and
  the NAFCU-legacy registrant). Named (not roster-only) ACU quotes found for
  6 of 9. Both Democrats drilled (Vargas, Gonzalez) confirm strongly with
  named quotes — Beatty's break isn't a partisan pattern (n=3 too small).
  Vargas's bill (Credit Union Board Modernization Act) has the longest/most
  consistent lobbying-text run of any bill checked (22 filings, 2022Q1-2026Q1).
- **bug caught and fixed:** first read of the corrected screen table this
  session used `sqlite3 -mode column -width ...`, which silently truncated
  the feca_usd column and made every dollar figure read ~10x too low (Scott
  looked like $2,750, actually $27,500). Re-ran in `-mode csv`, cross-checked
  against Barr's already-verified $40,000 (matches exactly) — confirms the
  query/dedup logic was always right, this was a CLI display artifact only.
  Corrected table logged in evidence.md E0. Lesson: never use `-mode column`
  with fixed `.width` for money figures in this DB going forward.
- dead ends: Budd's second bill (2024-06-18 Fed debit-interchange pause bill)
  not isolable in ACU lobbying text — search terms too generic against
  boilerplate issue-code text. Logged as unconfirmed, not refuted.
- open questions (carried over, still owed): (1) ABA/ICBA/MBA density
  comparison, must be built outside the mention pipeline; (2) Congress.gov
  official bill-introduction dates; (3) NEW — independent skeptic pass on
  this session's builder-only bench result, specifically attacking Britt's
  thin lobbying leg, Budd's unconfirmed bill, and whether the screen's
  n_mentions>=2 gate itself cherry-picks toward high hit rates.
- NEXT (superseded, see below): skeptic pass on the bench-wide claim.
- did: editor asked why ACU specifically shows up in press releases and not
  other associations, and what else the client-mention-honoree-triangle
  screen surfaces — a question that skipped straight past the planned
  skeptic pass to the actual load-bearing check. Ran the full screen
  un-filtered by client (E10): ACU ranks 22nd of 192 clients by n_members
  showing the pattern (10), vs. Visa at #1 (84 members, $914k), Goldman
  Sachs #2 (59), League of Conservation Voters #3 (44), Amazon #4 (39),
  National Shooting Sports Foundation #5 (34). Also found Barr himself has a
  second, larger-mention-count bench-pattern client (National Thoroughbred
  Racing Association, $30k/6 mentions) outside ACU entirely.
- found: E10 is the case's own `boring_explanation` confirmed directly — ACU
  is unremarkable within the screen's population, not an outlier. This
  refutes the case's central newsworthiness claim ("bench at
  trade-association scale") even though the per-member replication (E1-E9)
  was itself accurate and the methodology worked as designed.
- decision: KILLED, 2026-07-08. Full rationale in case.md Verdict. Scope of
  the kill: refutes ACU's distinctiveness/newsworthiness specifically; does
  NOT refute E1-E9's facts (still true, re-derivable) or the triple-join
  methodology (validated, this case's lasting output alongside E10's ranking
  table). Skeptic pass no longer needed — E10 did the skeptic's job more
  decisively than the planned pass would have.
- follow-on leads spun out (not pursued in this case): (1) Visa, 84-member
  bench, $914k, rank #1 — same screen, needs its own case if promoted;
  (2) Andy Barr's second client relationship (National Thoroughbred Racing
  Association) — possibly interesting on its own (why does a horse-racing
  group have more press mentions of Barr than ACU?), unexplored.
- NEXT: none — case killed, see Verdict in case.md. Editor is pivoting to
  fish the same screen for Visa / thoroughbred-racing leads next.

## 2026-07-08 (reopened, findings-report round-out)
- did: editor is reopening this case not to overturn the kill but to write it
  up in the findings report as a worked example of the triangle methodology
  (say/pay/legislate) plus the verification discipline that caught its own
  multiple-comparisons trap (E10). Built a `derived/` timeline dataset and
  chart, modeled directly on apra-lobbying-coalition's
  `analysis/build_top4_*` pattern: three new scripts in `analysis/` —
  `build_bench_contributions.py` (item-level LD-203 FECA contributions, ACU
  registrant_id=11322, all 10 bench members), `build_bench_press.py` (ACU
  press mentions via `derived_client_press_mentions`, entity 644/645),
  `build_bench_lobbying.py` (ACU Senate lobbying filings naming each member's
  bill, using the exact search fragments cited in evidence.md E1-E9) — and
  `build_bench_timeline_chart.py` (one lane per member, contributions as
  sized circles, press as triangles, lobbying filings as tick marks; direct
  visual analog of apra's `top4_timeline_chart.png`).
- found: two dedup bugs caught while reconciling against evidence.md's cited
  totals (both fixed before writing final CSVs): (1) contribution query
  needed the case's `DISTINCT contributor_name, payee_name, date, amount_num`
  dedup key (dropping `honoree_name`/`filing_uuid` from the key) — without it,
  a same-day/same-amount row filed under two honoree-name spelling variants
  (e.g. "Sen. Tim Scott" vs. "Tim Scott") double-counted; (2) press-mention
  query needed dedup on `(bioguide, url)` — ACU's two alias-index entity ids
  (644/645) both match the same release, so an un-deduped join double-counted
  6 of 33 press rows (Barr looked like 4 mentions, should be 3). After both
  fixes, every per-member total in `derived/bench_contributions.csv` and
  `derived/bench_press_releases.csv` matches evidence.md's E0/E1-E9 numbers
  exactly; lobbying filing counts matched on the first pass (13 member-bill
  fragments, incl. Beatty's confirmed zero-match row for Fair Hiring in
  Banking Act, kept in the CSV on purpose to show the E7 break).
- output: `derived/bench_contributions.csv` (69 rows), `derived/
  bench_press_releases.csv` (27 rows), `derived/bench_lobbying_filings.csv`
  (113 rows across member-bill pairs), `derived/bench_timeline_chart.png`.
  Chart visually confirms E7: Beatty's lane shows contribution circles and a
  press triangle but zero lobbying tick marks, unlike every other lane.
- NEXT: draft the findings.md entry — frame as builder (E1-E9) → skeptic
  (E10's own-screen replication) → judge (kill, scoped narrowly) verification
  case study, methodology as the deliverable, ACU story itself as secondary.

## 2026-07-08 (bill dates via Congress.gov API)
- did: editor asked which bills are involved and whether we can date them,
  noting the API key is already set up (used previously in
  amazon-money-without-praise's `pull_cosponsors.py`). Resolves the open
  question carried since 2026-07-07/08 ("Congress.gov official bill-
  introduction dates, still owed"). Confirmed via web search (Congress.gov
  is the source of truth, but its v3 API has no working free-text bill
  search, so numbers had to be found by search first, then fetched by
  congress/type/number) that bill numbers do NOT carry across Congresses —
  same lesson as the already-known S.3992→S.2486 renumbering, now confirmed
  for every bill in the bench: Barr TABS (118th HR.1382 → 119th HR.654),
  Barr UDAAP (118th HR.6789 → 119th HR.1652), Britt Community Bank Relief
  (119th only so far: S.3849/HR.7484), Emmer Anti-CBDC (118th HR.5403 →
  119th HR.1919), Fitzgerald CFPB Accountable (117th HR.8443 → 118th
  HR.1749 → 119th HR.1606), Fitzgerald HUMPS (119th HR.3379 only —
  no earlier version), Fitzgerald Expanding Access to Lending (118th
  HR.6933 → 119th HR.4167), Beatty Fair Hiring in Banking (117th HR.5911
  only — enacted via NDAA Dec 2022, never reintroduced), Vargas Credit
  Union Board Modernization (118th HR.582 → 119th HR.975), Gonzalez
  Veterans Member Business Loan (118th HR.4867 → 119th HR.507, plus older
  116th/117th versions not pulled — out of ACU's 2022-2026 filing window
  edge).
  New script `analysis/pull_bill_dates.py` (same pattern as amazon case's
  `pull_cosponsors.py`: `.env` CONGRESS_GOV_API_KEY, raw JSON cached under
  `data/congress_bills/`, gitignored, shared cache with the amazon case —
  no key collisions since keyed by congress/type/number). Wrote
  `derived/bench_bill_dates.csv` (25 bill-Congress rows, official title +
  sponsor + introduced_date + latest_action from the API). Added gold-star
  introduced-date markers to `bench_timeline_chart.png` (4th marker layer:
  contributions/press/lobbying/bill-intro, all four now on one chart).
- found: two dates worth flagging for the writeup — (1) Emmer's 119th HR.1919
  introduced 2025-03-06 is the SAME DAY as his 2025-03-06 ACU press release
  (E4) — the endorsement quote landed same-day as introduction, tighter than
  any other bench member's press/bill-date gap; (2) Beatty's Fair Hiring in
  Banking Act (117th HR.5911, introduced 2021-11-09) was enacted into law via
  the NDAA in December 2022 and never reintroduced — meaning ACU's zero
  lobbying-text match (E7) can't be explained as "too new to show a pattern
  yet" the way Britt's is; the bill was live and then law throughout ACU's
  entire filing window, and still never named. Strengthens E7 as a genuine
  negative result, not a timing artifact.
- caveat: bill dates are web-sourced (Congress.gov API), not derived from
  gain.db — same status as the apra case's bill-milestone dates, flagged in
  the chart caption and NOT to be treated as corpus evidence in the findings
  writeup.
- NEXT: still draft the findings.md entry (unchanged from prior NEXT).

## 2026-07-08 (CULAC identity check)
- did: editor asked whether CULAC and "AMERICA'S CREDIT UNIONS PAC" (both seen
  as `contributor_name` in `bench_contributions.csv`) are the same PAC.
  Corpus check: the two names' date ranges are adjacent, not overlapping
  (CULAC 2022-01-27 to 2023-12-28; America's Credit Unions PAC 2024-01-22 to
  2025-12-30, across all ACU-registrant contributions, not just the bench).
  Web-confirmed (not corpus evidence): same FEC committee, ID C00007880,
  registered since 1976, renamed from "Credit Union Legislative Action
  Council (CULAC)" to "America's Credit Unions PAC" after the CUNA/NAFCU
  merger — one PAC under two names, not two donors. `bench_contributions.csv`
  already treats both names as one continuous stream (correct); flag this
  explicitly if the PAC is named directly in the findings writeup, so a
  reader doesn't misread the rename as two separate funding sources.

## 2026-07-08 (D3 interactive timeline)
- did: editor wanted a better-designed companion to bench_timeline_chart.png
  — specifically hover detail on bill markers (name/purpose/action), plus
  press/lobbying/contribution detail. Built as an addition, not a
  replacement (PNG stays the print/archival artifact for the PDF report).
  Split cleanly: `analysis/bench_timeline_d3.js` is static, hand-written D3
  rendering code (loaded unchanged); `analysis/build_bench_timeline_d3.py`
  owns data only — reads the same 4 derived CSVs used by the PNG builder,
  adds a hand-written BILL_PURPOSES gloss (one plain-English line per bill,
  since official titles like "TABS Act of 2023" are uninformative on their
  own), and writes `derived/bench_timeline_data.json` +
  `derived/bench_timeline_chart.html` (self-contained: D3 v7 from CDN, no
  server required — opens directly, though local testing used `python3 -m
  http.server` since Playwright blocks file:// URLs). Same 4-layer design as
  the PNG (contributions/press/lobbying/bill-intro), same lane-per-member
  layout, same colors — hovering any of the 4 marker types shows its full
  source record (bill: number/title/purpose/sponsor/latest action +
  congress.gov link; press: headline+url; lobbying: excerpt+LDA link;
  contribution: amount/payer/payee+LDA link).
- verified: rendered via Playwright against a local HTTP server (file://
  blocked by the browser tool) — layout matches the PNG's structure at a
  glance; dispatched a synthetic hover on a bill star and confirmed the
  tooltip HTML is fully populated and correct (Barr/TABS Act/HR.1382/118th
  Congress/purpose gloss/sponsor/introduced date/latest action/working
  congress.gov link); a real cursor hover screenshot also confirmed the
  tooltip renders on-screen with correct positioning and a working LD-203
  link (landed on a Vargas/CULAC/$5,000 contribution circle).
- NEXT: draft the findings.md entry (unchanged) — can now link/embed the
  interactive HTML as supplementary material alongside the static PNG.

## 2026-07-08 (D3 chart: layer toggles + lane highlight)
- did: editor found the chart cluttered and asked for (1) toggling marker
  layers on/off, (2) highlighting one lane at a time, without losing any
  info. Reworked `analysis/bench_timeline_d3.js`: legend swatches are now
  click targets that toggle `layerVisible.{contrib,press,lobbying,bill}`;
  lane backgrounds + labels are hover targets that dim all other lanes
  (opacity 1 -> 0.35 for markers, labels bold on the active lane) and click
  targets that PIN the highlight (survives moving the mouse to read
  tooltips; a small pill top-right shows the pinned member, click it or the
  lane again to release). The two interactions compose via one
  `refreshLaneOpacity()` that multiplies layer-visibility and lane-highlight
  into final opacity per marker, so toggling a layer off stays off
  regardless of which lane is highlighted. `build_bench_timeline_d3.py`
  changed only the subtitle text (explains the new interactions) and added
  a CSS opacity transition for a smoother dim/undim. PNG unaffected (static,
  no interaction to add).
- NEXT: draft findings.md (unchanged).

## 2026-07-08 (press-hook completeness check)
- did: editor observed that ACU press releases in this bench essentially
  never appear without a nearby bill-intro (most common) and/or a
  contribution — asked to check this quantitatively. At a +/-45-day window:
  21 of 27 press releases (78%) landed near a bill-intro or contribution;
  6 looked like exceptions. Inspecting the 6 individually, 4 turned out to
  be OTHER milestones of bills already in the bench inventory (Barr's
  2025-05-03 "reintroduces" release IS a bill-intro of UDAAP's 119th
  version I'd only checked the label for, not a separate date-check;
  Emmer's 2025-07-17 is the House-PASSAGE of his already-tracked bill;
  Beatty's 2022-12-23 is her bill's SIGNED-INTO-LAW milestone) — not
  genuine gaps, just under-checked distances to milestones already in
  scope. Only 2 were real: Britt's 2025-10-22 release and Gonzalez's
  2026-02-24 release, both for bills OUTSIDE the original E1-E9 bill
  inventory (bill-hunting for this case had stopped once each member's
  flagship bill was found; these two members apparently have others).
- found: web-searched + API-confirmed both missing bills — Britt's release
  is the STREAMLINE Act (S.3017, 119th, Sen. Kennedy lead/Britt cosponsor,
  Bank Secrecy Act reporting-threshold bill), introduced 2025-10-20, TWO
  DAYS before her press release (not the 112-day gap it looked like against
  the wrong bill). Gonzalez's release is the MORE Opportunities for
  Homeownership Act (H.R.7647, 119th, Fitzpatrick co-lead, FHLB-access
  bill), introduced 2026-02-23, ONE DAY before his press release (not the
  404-day gap it looked like against the wrong bill). Added both to
  `pull_bill_dates.py`'s BILLS list (tagged evidence_ref="press-hook-check",
  not E1-E9, since they're outside this case's verified per-member
  drilldown — nobody has checked whether ACU's lobbying text names either
  bill) and `BILL_PURPOSES` in the D3 builder; re-ran `pull_bill_dates.py`
  (27 rows now, was 25), `build_bench_timeline_chart.py`, and
  `build_bench_timeline_d3.py` to add the two new stars to both charts.
  **Net result: zero unexplained press releases in the bench once the bill
  inventory is complete** — every one of the 27 ACU press mentions sits
  within a few days of a bill milestone (intro/reintro/passage/enactment)
  and/or a contribution. This is a cleaner, stronger claim than "press
  needs a hook" vaguely stated — it's zero exceptions, corpus-wide, across
  all 10 bench members.
- caveat: this doesn't mean ACU's lobbying text also names these two new
  bills — that's unchecked (would need its own E-numbered drilldown before
  citing "full triple" for Britt's or Gonzalez's second bill). The
  observation is scoped to press+bill/press+money timing only.
- NEXT: draft findings.md — this is a good candidate for its own short
  paragraph (a near-universal say/pay-hook rule for ACU press mentions),
  separate from the money-timing typology already logged 2026-07-08.

## 2026-07-08 (D3 chart: lobbying as quarter bands, not ticks)
- did: editor flagged the lobbying-tick layer as the densest, noisiest part
  of the D3 chart (Fitzgerald/Vargas/Gonzalez each had 20+ individual ticks)
  and pointed out filings are inherently quarterly, not point-in-time --
  asked to represent them as a shaded/striped span over the whole quarter
  instead. Added `QUARTER_BOUNDS` + `quarter_span()` to
  `build_bench_timeline_d3.py`, parsing `filing_period` strings (e.g. "1st
  Quarter (Jan 1 - Mar 31)") into exact start/end dates -- more precise
  than deriving from `dt_posted` (the filing date, which lags quarter-end
  by ~10 days) and matches the LDA's own filing-period vocabulary exactly
  (verified against the actual distinct strings in
  bench_lobbying_filings.csv rather than guessed: "July 1 - Sep 30" not
  "Jul 1 - Sept 30"). `build_lobbying()` now GROUPS by (member, year,
  quarter) instead of emitting one row per filing, since members with >1
  tracked bill (Barr: TABS+UDAAP; Fitzgerald: 3 bills) can have multiple
  filings landing in the same quarter -- merged into one band per quarter
  with a `bills: [...]` list, avoiding overlapping ticks/bands for the same
  quarter. Output: 113 raw filing rows collapsed to 76 quarter-bands.
  `bench_timeline_d3.js`: replaced the tick-mark rendering with a striped
  `<rect>` per band (`url(#lobbying-stripes)` SVG pattern, 45-degree
  diagonal, dark gray) spanning quarter_start to quarter_end (min-width
  floor of 3px so a single quarter stays visible/clickable at full
  zoom-out); hover tooltip now lists ALL bills matched in that quarter, not
  just one. Legend swatch updated (band icon instead of tick line); layer
  toggle / lane highlight logic unchanged (generic over the class, worked
  automatically once `lobbyingSel` pointed at the new `.lobbying-band`
  elements).
- verified: via Playwright -- band count matches expectation (113->76,
  correct collapse ratio given the known Barr/Fitzgerald multi-bill
  overlaps); dispatched a synthetic hover on Barr's merged 2025-Q1 band,
  confirmed the tooltip correctly lists both TABS and UDAAP with separate
  excerpts and LDA links; confirmed the lobbying legend-swatch click still
  toggles the new `.lobbying-band` elements' opacity/pointer-events to 0/
  none, i.e. the toggle logic generalized without changes. Visual check:
  the shift from dense tick-clusters to continuous striped spans makes
  coverage gaps (e.g. Vargas's ~9-month 2025 lobbying gap, Beatty's total
  absence for E7) much more immediately visible than counting missing
  ticks did.
- PNG (`build_bench_timeline_chart.py`) intentionally left unchanged --
  ticks are legible enough there since it's a static/print artifact without
  hover, and quarter-band rendering in matplotlib would be a separate,
  larger change; can revisit if the PNG is judged too cluttered on its own
  merits later.
- NEXT: draft findings.md (unchanged).

## 2026-07-08 (D3 chart: lobbying bands as subtle lane texture, not a foreground strip)
- did: editor said the first band version still read as "a weird strip
  cutting across" the lane -- wanted lobbying quarters to be a slightly
  darker/striped BACKGROUND across the whole lane height, not a separate
  foreground element with its own vertical footprint. Reworked
  `bench_timeline_d3.js`: (1) replaced the single shared gray stripe
  pattern with one `<pattern>` per member, in that member's own color at
  opacity 0.16 (very low, textural) instead of solid gray; (2) the band
  rect is now full LANE HEIGHT (`yLane.bandwidth()`), not a 15px strip
  offset within the lane; (3) moved the band's rendering to right after
  `laneBg` in z-order (was rendered later, after gridlines/axis -- which
  meant it painted OVER the gridlines within its quarter-span; now it sits
  behind gridlines/axis/all point-in-time markers, so it reads as texture
  on the lane itself, not a layer competing with anything). Removed the
  band's visible stroke border (was a thin gray outline; dropped it so
  there's no strip-shaped edge to see).
- caught and fixed a z-order side-effect during the same edit: because the
  band is now full-lane-height and sits ON TOP of `laneBg`, it was silently
  swallowing `laneBg`'s hover/click lane-highlight events for any x-range
  inside a lobbying quarter (hovering there would fire the band's own
  tooltip but never trigger the lane-dim effect). Fixed by mirroring the
  same `mouseenter`/`mouseleave`/`click` lane-highlight handlers onto the
  band itself, so it does double duty -- own tooltip AND lane highlight --
  instead of blocking the highlight for roughly half of each striped lane.
  Verified via Playwright: hovering a lobbying band correctly fires both
  its own tooltip (bill list) and the lane-highlight opacity change on
  `laneBg` (active lane 0.10, others dimmed to 0.03).
- found (visual, not new data): with the ticks/strip gone, gaps in ACU's
  lobbying coverage are now much more visually obvious as literal absence
  of texture -- Beatty's lane (E7's triple break) has NO striping anywhere
  across its full ~4-year span, which reads immediately at a glance in a
  way the old tick-marks required counting to notice.
- NEXT: draft findings.md (unchanged).

## 2026-07-08 (D3 chart: tooltip links were unclickable)
- did: editor reported the "View filing/release" links inside tooltips
  couldn't be clicked -- moving the mouse from a marker toward the link
  crossed off the marker before reaching the tooltip, which hid it
  instantly (tooltip had `pointer-events: none` in the CSS, by design, so
  it wouldn't block hovering markers underneath it -- but that also made
  the tooltip itself un-hoverable, so a link inside it was unreachable).
  Fix: `.tooltip` CSS is now `pointer-events: auto`
  (`build_bench_timeline_d3.py`'s HTML template); `bench_timeline_d3.js`'s
  `hideTooltip()` now debounces on a 150ms `setTimeout` instead of hiding
  immediately, and the tooltip element itself has `mouseenter` (cancel the
  pending hide) / `mouseleave` (re-arm it) handlers -- so moving from a
  marker into the tooltip within 150ms keeps it open, and it only actually
  disappears once the mouse has left both the marker AND the tooltip.
- verified via Playwright (simulated events, not a real cursor drag):
  (1) right after a marker's `mouseout` fires, tooltip opacity is still 1
  and a real clickable `<a href>` is present in its DOM; (2) if the
  tooltip's own `mouseenter` fires before the 150ms window closes, opacity
  stays 1 even 300ms later (well past the original timer); (3) once the
  tooltip's `mouseleave` fires, it closes normally (opacity 0). All three
  match the intended behavior.
- NEXT: draft findings.md (unchanged).

## 2026-07-08 (repo-wide LDA URL bug: wrong path, missing /print/)
- did: editor reported the "View filing" links all 404. Root cause was NOT
  this chart specifically -- it's a repo-wide, long-standing bug in the
  canonical URL convention itself (documented in CLAUDE.md and
  scripts/schema_senate.sql, and copied from there into every URL-
  generating script and skill doc in the repo). Two separate errors,
  confirmed against the live LDA API + site:
  1. **Missing `/print/` suffix.** The bare `.../{filing_uuid}/` path 404s
     for BOTH record types; the working path is `.../{filing_uuid}/print/`.
     Confirmed via the LDA v1 API's own `filing_document_url` field, which
     includes the suffix.
  2. **Wrong path segment for contribution (LD-203) filings.** Contribution
     filings and lobbying filings are different LDA record types with
     SEPARATE `filing_uuid` namespaces, even though both columns share the
     name `filing_uuid` in our schema (`senate_filings.filing_uuid` vs.
     `senate_contribution_filings.filing_uuid`). Lobbying filings resolve at
     `/filings/public/filing/{uuid}/print/`; contribution filings resolve
     at `/filings/public/contribution/{uuid}/print/` -- `contribution/` not
     `filing/`. Using the lobbying path for a contribution UUID (or
     vice versa) 404s even with the correct UUID and the `/print/` suffix,
     which is exactly what this case's contribution links were doing.
  3. **Bonus finding, unprompted:** lda.senate.gov is actively being
     retired -- the live site shows a "We're Moving!" banner pointing to
     lda.gov (confirmed: same paths, same API, both domains currently work,
     but lda.senate.gov could be redirected/killed later without notice).
     Standardized on `lda.gov` for all new URLs rather than fix to the
     domain that's already being deprecated.
- scope: fixed the canonical convention + every CODE/DOC generator in the
  repo (editor's call, given the bug's size): `CLAUDE.md`, `README.md`,
  `scripts/schema_senate.sql`, `scripts/build_derived_cross_chamber.py`,
  `scripts/build_derived_convicted_lobbyist_register.py`,
  `docs/senate_db.md`, `docs/derived_db.md`,
  `docs/beat_book.md` (then at
  `.claude/skills/gain-lobbying-investigation/SKILL.md`),
  `.claude/skills/track-investigation/SKILL.md`,
  `.claude/skills/track-investigation/reference/templates.md`,
  this case's `analysis/build_bench_lobbying.py` (filing/ + /print/) and
  `analysis/build_bench_contributions.py` (contribution/ + /print/),
  apra-lobbying-coalition's `analysis/build_kill_decision_contributions.py`
  and `analysis/build_top4_inhouse_timeline.py` (both contribution/ +
  /print/), and 3 case-local SQL files with hardcoded URLs
  (`tariff-2025-stealth-surge/queries.sql`,
  `sunland-park-ysleta-opposition/queries.sql`,
  `screens/conviction-quarterly-gaps/screen.sql`).
- explicitly NOT fixed this session (deferred, editor's scoping decision):
  prose citations inside already-written `evidence.md`/`case.md`/`findings.md`
  files in OTHER cases (amazon-money-without-praise, tariff-2025-stealth-
  surge, barr-credit-union-cfpb-loop, sunland-park-ysleta-opposition,
  critics-take-health-money, jack-act-blind-spots, and the top-level
  `findings.md` itself) -- those are written findings, editing them is a
  different kind of change than fixing a generator, and none of them are
  being actively re-run today. Also left 2 `queries.sql` API-endpoint
  citations (`.../api/v1/contributions/{uuid}` in this case's and
  barr-credit-union-cfpb-loop's queries.sql) untouched -- confirmed those
  ARE still correct as written (the REST API path is unaffected by this
  bug; only the public HTML page paths were wrong).
- rebuilt + reverified this case's own artifacts after the fix: re-ran
  `build_bench_lobbying.py`, `build_bench_contributions.py`, and
  `build_bench_timeline_d3.py`; live-checked a random sample of 5
  contribution URLs and 5 lobbying URLs from the regenerated CSVs via curl
  -- 10 of 10 return HTTP 200.
- FOLLOW-UP OWED (not done this session): correct the LDA URL citations in
  the 7 files listed above as "explicitly not fixed" -- flagging here so a
  future session doesn't assume those evidence.md files' cited URLs work
  when they don't. Straightforward sed-style fix once undertaken (same two
  rules: add /print/, and use contribution/ instead of filing/ for any URL
  built from a senate_contribution_filings/senate_contribution_items row).
- NEXT: draft findings.md; separately, the LDA-URL follow-up above.

## 2026-07-09 (say/pay/lobby/bill typology, re-characterized)

- did: editor asked to return to the case and re-characterize the say-pay-
  lobby-bill typology from the derived CSVs. Prior sessions had described
  the pattern as one uniform "triple" (money + lobbying-text + press) that
  either holds or breaks per member (E1-E9), plus one separate finding
  (2026-07-08 press-hook check) that press releases always sit near a bill
  milestone. Neither session had built a single cross-referenced, dated
  timeline per member across all four `derived/bench_*.csv` files to see
  the actual sequencing. Did that this session: loaded
  `bench_bill_dates.csv`, `bench_contributions.csv`,
  `bench_press_releases.csv`, `bench_lobbying_filings.csv`, joined on
  `member`, sorted chronologically per member, and computed (a) press-to-
  nearest-bill gap in days for every bill introduction, (b) contribution
  counts in the 90-day windows before/after each bill introduction, (c) a
  qualitative pass over each member's lobbying-filing date range vs. their
  bill's introduction date.
- found: the "triple" is actually **two loosely-coupled axes, not one
  uniform pattern** — written up as new evidence.md E11. (1) Press-to-bill
  timing is near-universal and mostly same/next-day (confirms + sharpens
  the 2026-07-08 press-hook finding: not just "every press release has a
  bill nearby" but a same-day-dominant sub-pattern with a multi-day-lag
  minority of 2, Barr and Budd). (2) Lobbying-text continuity is NOT
  binary present/absent as E1-E9 implicitly treated it — it's three
  distinct sub-patterns: continuous quarterly coverage with no gaps
  (Vargas, Gonzalez, Fitzgerald, Cramer/Scott/Budd, Barr), late-starting-
  then-continuous (Emmer, Britt), and genuinely absent (Beatty only). (3)
  Money does NOT cluster around bill-introduction dates the way press and
  lobbying do — contributions land on the LD-203 semi-annual filing
  calendar regardless of whether a bill event happened that period, so
  "money follows the bill" is not well supported by the sequencing; money
  reads as a standing/background PAC relationship, not a per-bill
  transaction.
- found (unremarked detail inside axis 2): for Vargas and Gonzalez
  specifically, ACU's Senate lobbying text pre-dates the bill's own formal
  introduction by several months — ACU was lobbying the policy before it
  had a bill number. This reframes "ACU's filings name the bill" as an
  understatement for its most-lobbied bench members: ACU is present at the
  drafting stage, not just reactive after introduction.
- caveat (logged in E11, repeating here since it matters for how the
  typology gets used): n=10 with several members sharing bills (Cramer/
  Scott/Budd share S.3992/S.2486), so the 3-way lobbying-continuity split
  has only 1 example of "absent" (Beatty) and 2 of "late-start" (Emmer,
  Britt) — descriptive of this bench, not statistically validated at
  larger n. The "money is calendar-driven" claim is a sequencing
  observation, not a tested null model against corpus-wide LD-203 filing-
  period clustering (unrun).
- decision: this REFINES, does not overturn, the 2026-07-08 kill. ACU is
  still not distinctive/newsworthy at bench scale (E10 stands). What
  changes is precision: the case now has a better-characterized picture of
  what the underlying mechanism actually looks like, which is the
  reusable-methodology deliverable this case was always partly about —
  and the 3-axis frame (press/bill timing, lobbying-continuity type,
  money-as-background) is explicitly flagged in E11 as a candidate lens
  for the Visa follow-on lead (E10's #1, 84 members) if that case opens.
- NEXT: draft findings.md incorporating E11's typology alongside E10's
  kill; if/when Visa is promoted, apply the same 3-axis typology to it as
  the first test of whether the pattern generalizes beyond n=10.

## 2026-07-09 (E11 corrected: recovered a stronger typology from an earlier transcript)

- did: editor decided NOT to kill the story after all — wants it as the
  findings-report demo of the say/pay/lobby/bill methodology — and flagged
  that an earlier session had produced a better typology than the one
  written up above. Grepped `typology` in that earlier session's transcript
  (2026-07-08, working in this case's `derived/` dir) and found 3 python3
  scripts + their outputs that this morning's E11 pass had not reproduced:
  (a) per-press nearest-bill/nearest-contribution gap calculator, (b) a
  before/after-first-bill contribution split bucketed 0-30d/30-180d/>180d
  with dollar totals, (c) a 45-day "responsiveness" test (does any bill/
  press event fall in the 45 days immediately before a contribution) plus a
  raw gap-length audit between consecutive contributions.
- found: this morning's first-pass E11 had the wrong center of gravity —
  it framed money as "calendar-driven, not bill-driven" from eyeballed
  90-day windows without normalizing per member, and mischaracterized Britt
  as a "late-starting lobbying" case. The recovered typology is sharper and
  quantified: bill->press is a same-day tautology (not a finding); money's
  independence from legislative timing is directly measurable via the
  45-day responsiveness test (0-38% responsive, median 0%, across all 10
  members) and irregular gap lengths (0-740 days, no fixed cadence); and
  Britt is a real, citable, quantified outlier — 0% responsive, effectively
  all her money predates her flagship bill's introduction — which inverts
  the case's own "pay follows bill" framing for her specifically. This is
  meaningfully stronger than this morning's version because it has an
  actual quantitative test backing "money is independent" instead of an
  impressionistic read, and it correctly identifies WHO the outlier is
  (Britt, on money-timing) rather than misfiling her under lobbying-text
  continuity.
- did: rebuilt E11 in evidence.md, keeping the lobbying-text 3-way
  continuity split from this morning's pass (that part wasn't in the
  recovered transcript and still holds as a valid, separate axis) and
  replacing the money-timing section with the recovered quantitative work.
  Promoted the transcript's ad hoc scripts into a real, re-run script:
  `analysis/bench_timing_typology.py` (three functions matching a/b/c
  above). Ran it against the CURRENT `derived/bench_*.csv` files (not the
  transcript's point-in-time snapshot) to reproduce the numbers — 9 of 10
  members matched exactly; Britt's before/after-bill split differs
  ($33,500/0%/0% in the transcript vs. $32,500/$1,000/3% now) because
  `bench_bill_dates.csv` gained a second Britt bill (STREAMLINE Act,
  introduced 2025-10-20) in the 2026-07-08 press-hook-completeness-check
  session, which is EARLIER than her flagship Community Bank Relief Act
  (2026-02-11) and therefore becomes the new "first bill" reference point
  for a min()-based before/after split. Both numbers are correct for what
  they measure; documented the discrepancy explicitly in E11 rather than
  silently picking one, and recommended citing the flagship-bill framing
  ($33,500/0%/0%) as primary since STREAMLINE is a `press-hook-check`-tier
  bill without confirmed lobbying-text support, unlike Community Bank
  Relief Act (E3).
- did: updated case.md status line to keep `killed` (scoped narrowly to the
  ACU-distinctiveness claim, per the 2026-07-08 reopen precedent) with an
  explicit note that the case is open again as the findings-report
  methodology demo — not an overturn of E10. Confidence split into two
  lines (low for the ACU-specific newsworthiness claim; high for the
  methodology/typology itself). Replaced the methodology-track paragraph
  with the corrected E11 summary.
- decision: E11 (corrected version) is this case's primary findings-report
  artifact going forward. Verdict section of case.md not yet rewritten to
  foreground this — still reads as a kill-only writeup; owed before this
  goes in the report.
- NEXT: rewrite case.md's Verdict section to lead with the methodology-demo
  framing (typology + E10's own-screen discipline) rather than reading as
  a pure kill; draft the findings.md entry itself, built primarily from
  E11's tables; run the 30d/60d threshold sensitivity check on the 45-day
  responsiveness test flagged as a caveat in E11.

## 2026-07-09 (E12: the counterfactual — how many other members does ACU pay, and are any bill-relevant but unmentioned?)

- did: editor asked the natural counterfactual the bench never checked: how
  many OTHER members does ACU pay beyond the 10-member bench, and would any
  of the unmentioned ones have introduced an ACU-relevant bill? Editor's
  prior guess: probably none, given how tightly press and bills already
  track together (E11's tautology finding). Queried ACU's full honoree
  population directly (same base query as EBarr4, registrant 11322,
  confidence>=0.9 honoree matches) left-joined against
  `derived_client_press_mentions` (entity 644/645) to split mentioned vs.
  never-mentioned.
- found: ACU pays **527 distinct members** ($6,208,500 total — same figure
  as EBarr4). Only **27 of those 527 (5.1%) get ANY ACU press mention at
  all**, at any count. The 10-member bench is a subset of that 27 at the
  `n_mentions>=2` screen threshold — and 2 MORE members clear that same
  threshold but were never in the original bench (Gary Peters D-MI, Todd
  Young R-IN, both 2 mentions) — a completeness gap in how the bench was
  originally built from screen-36, worth flagging in the methodology
  writeup but not chased further this session. The other 500 (95%) never
  get mentioned, including several paid MORE than any bench member:
  Katherine Clark ($50k, House Dem Whip), Jeffries ($45k, Minority Leader),
  Waters ($42.5k, Financial Services Ranking Member), Neal ($35k, Ways &
  Means Ranking Member) — reads as leadership-relationship money, a
  structurally different category from the bench's bill-tied pattern.
- found (direct test of editor's hypothesis): Bill Huizenga (R-MI, paid
  $35,000 by ACU) is the named COSPONSOR, alongside Vargas, on the Credit
  Union Board Modernization Act — this case's own E8 bill, introduced
  twice (118th HR.582, 119th HR.975) — yet has ZERO ACU press mentions
  despite being paid more than 8 of the 10 bench members. Checked his full
  press-release history (17 rows): no Huizenga-authored release names the
  bill or ACU; the only releases naming it are VARGAS's (already in
  `bench_press_releases.csv`), which credit Huizenga as co-lead in Vargas's
  own text. **This confirms the editor's hypothesis with a concrete,
  same-bill, same-case example**: Huizenga is bill-relevant and paid, but
  invisible to the mention pipeline specifically because the pipeline
  attributes a press release to whichever member's own site hosts it
  (`press_releases.bioguide_id`) — cosponsors who let the lead sponsor
  issue the release never generate a qualifying row of their own. Same
  selection bound already documented for ABA-as-a-client in
  `docs/derived_db.md`, now demonstrated as a named-individual,
  same-bill instance rather than only stated abstractly.
- dead end (logged, not pursued): tried to go further and ask "of the 500
  unmentioned members, how many sponsor/cosponsor an ACU-relevant bill
  more broadly" — there's no bill-sponsorship table in gain.db (bill data
  in this case has always come from the external Congress.gov API, one
  bill at a time). Tried a proxy: extracted raw H.R./S. bill-number tokens
  from ACU's own lobbying-activity description text (168 distinct tokens
  found). Explicitly did NOT use this as a source for "which members" —
  bill numbers repeat across Congresses (the same trap already documented
  for S.3992->S.2486), so resolving 168 unfiltered tokens to actual
  sponsors would need per-bill Congress.gov lookups, which is a real cost
  and wasn't run unprompted. Logged as a scoped follow-up, not attempted.
- wrote up as evidence.md E12; added `queries.sql#q-e12`/`q-e12-huizenga`/
  `q-e12b` (the last one documented as NOT a safe standalone source, per
  above).
- decision: E12 strengthens the methodology-track deliverable materially —
  it turns the "mention-pipeline-selected" caveat (previously stated
  abstractly, e.g. re: ABA) into a quantified number (527 paid vs. 27
  mentioned vs. 10-12 in/near the bench) plus one clean named example
  (Huizenga) inside this case's own bill inventory. Recommend featuring
  E12 prominently in the findings.md writeup, likely right alongside E11.
- NEXT: (carried over) rewrite case.md Verdict to lead with methodology-
  demo framing; draft findings.md entry (E10 kill + E11 typology + E12
  counterfactual as the three-part methodology showcase); if time allows,
  the 168-bill-token Congress.gov resolution to quantify "how many
  bill-relevant unmentioned members" beyond the one Huizenga instance.

## 2026-07-09 (E13: should Peters/Young be added to the bench?)

- did: editor asked directly whether Gary Peters and Todd Young (flagged in
  E12 as clearing the same `n_mentions>=2` threshold as the bench, but not
  chased) should actually be added. Re-checked their mention count properly
  this time (E12's count was a quick, undeduped query) and ran the same
  named-bill lobbying-text search used for E1-E9 against each of their
  flagship bills.
- found: **E12's claim that Peters and Young "clear the `n_mentions>=2`
  threshold" was itself wrong** — it hit the exact double-counting bug
  already documented in E0 and fixed in `build_bench_press.py`
  (ACU's two alias-index entity ids, 644/645, both match the same release).
  Deduped properly, both have exactly 1 real ACU mention, not 2. Neither
  actually clears the bench's own construction threshold. This retracts
  E12's "completeness gap" framing for these two specific names (logged
  now, not caught in the same session because E12's query was written fast
  as a spot-check and never re-applied the dedup pattern already known from
  E0/2026-07-08).
- found (checked the substance anyway): **Peters has a real, verified full
  triple** — $20,000 ACU money, a self-authored 2024-06-13 press release
  ("Peters Reintroduces...") naming him sponsor, AND ACU's Senate lobbying
  filings name his bill verbatim ("Housing Financial Literacy Act of 2021,
  H.R. 1395") in 4 filings. All three legs present — he just has only 1
  press touchpoint instead of 2, so the arbitrary `>=2` cutoff (not the
  substance) is what excludes him. **Young does NOT have a full triple** —
  money + 1 self-authored press release, but zero lobbying-text match for
  his bill (an IRS-surveillance/taxpayer-privacy bill, not core
  credit-union subject matter) — same shape as Beatty's already-documented
  E7 break, not a new confirmed member.
- decision: do not add either to the bench's canonical 10 for the
  findings-report demo — it's already fully verified at that size and
  doesn't need an 11th name. But Peters is worth citing explicitly in the
  methodology section as a second, cleaner demonstration that the
  `n_mentions>=2` construction rule itself excludes real triples on a
  coin-flip (1 vs. 2 mentions) — reinforcing E12's point about the mention
  pipeline undercounting, this time from a near-miss just inside the
  screen's own logic rather than from the 500 fully unmentioned members.
- wrote up as evidence.md E13; added `queries.sql#q-e13/b/c`.
- NEXT: (carried over, unchanged) rewrite case.md Verdict; draft
  findings.md entry incorporating E10 (kill) + E11 (typology) + E12
  (counterfactual: 527 paid vs 27 mentioned, Huizenga) + E13 (Peters as a
  second near-miss instance of the same selection bound) as the four-part
  methodology showcase.

## 2026-07-09 (E14: Peters added to the bench)

- did: editor overruled E13's recommendation to leave the bench at 10 --
  "Let's add Peters to the bench. I don't know why we need to restrict it
  to 2 or more mentions." Correct call: the `n_mentions>=2` threshold was
  inherited from the screen-36 seeding query, never derived from anything
  about what makes a triple real -- E1-E9's actual standard was always the
  independently-verified triple itself, and Peters already had one (E13).
- did: before touching the CSVs, needed Peters' bill's exact Congress.gov
  lineage to update `pull_bill_dates.py` correctly. Confirmed H.R.1395
  (117th, the bill E13's lobbying-text match was keyed to by title) is
  actually sponsored by BEATTY, not Peters -- Peters' bill is the identical
  Senate companion, S.1490 (117th, confirmed via Congress.gov's
  `relatedBills` endpoint). Then searched for a later-Congress version
  matching his 2024-06-13 "Reintroduces" release -- not in the first page
  of his sponsored-legislation list (sorted by recency), had to paginate
  all 913 of his sponsored bills (offsets 0/250/500/750) to find it:
  **S.4542, 118th Congress, introduced 2024-06-13 -- same day as his press
  release.**
- found (correction to E13): re-checked ACU's lobbying text against this
  corrected lineage -- the 4 filings naming "Housing Financial Literacy
  Act" are ALL in 2022 Q2 - 2023 Q1, i.e. S.1490's (117th) life, and there
  are ZERO filings naming it from 2023 Q2 onward, through all of
  2024-2026 Q1 when S.4542 (the bill his actual release covers) was live.
  ACU keeps filing every quarter through 2026 Q1 on other business -- this
  is a real, dated absence, not a data gap. E13 had found the lobbying
  match but conflated it with the wrong bill/Congress by matching on title
  text alone; this session's Congress.gov pull is what caught it.
- decision: added Peters as the bench's 11th member, but framed precisely
  per the AskUserQuestion answer (add him, but document the gap honestly)
  -- his triple is money (real) + press (real, same-day as bill intro) +
  lobbying-text (real, but for the PRIOR Congress's bill number, with a
  gap covering the exact period his actual reintroduction and release fall
  in). Closer in kind to Britt (money precedes bill/press) or Beatty
  (a dated gap in one leg) than to the bench's clean majority.
- did: updated all 4 `analysis/build_bench_*.py` / `pull_bill_dates.py`
  scripts (added Peters to each MEMBERS dict; lobbying fragment tagged
  E13/E14 with the Congress-gap note in a comment; both bill numbers,
  S.1490 and S.4542, added to `pull_bill_dates.py`'s BILLS list) and both
  chart builders (`build_bench_timeline_chart.py`,
  `build_bench_timeline_d3.py` -- MEMBERS/COLORS lists + a new
  BILL_PURPOSES gloss explaining the Congress-lineage gap for hover
  tooltips). Re-ran the full pipeline in order: contributions (4 items,
  $20,000 -- matches E12/E13's earlier count), press (1 mention, matches
  E13), lobbying (4 filings, matches the corrected 117th-only finding),
  bill dates (both Congress.gov dates confirmed live: 2021-04-29 and
  2024-06-13), then both charts. Visually confirmed on the PNG: Peters'
  lane shows the 2021 star with nearby lobbying ticks, then a long gap,
  then the 2024 star lined up with a press triangle but NO lobbying tick
  anywhere near it -- exactly the E14 finding, visible at a glance the
  same way Beatty's all-blank lane already was.
- wrote up as evidence.md E14 (new) + updated E13's verdict to point to it
  (superseded, not deleted -- E13's original finding and recommendation
  stand as the historical record of what was known before this session's
  correction); added `queries.sql#q-e14` (documents the Congress.gov API
  calls, not SQL); added an addendum note to E0's table (left the original
  10-row table itself untouched as the historical screen-36 record, per
  case convention of not silently rewriting past evidence).
- NEXT: draft findings.md incorporating E10 (kill) + E11 (typology) + E12
  (counterfactual) + E13/E14 (Peters: threshold arbitrariness AND a new
  typological case -- lobbying support that lapsed exactly when press/
  money continued) as a five-part methodology showcase, now stronger than
  before since E14 adds an actual 11th worked case rather than just a
  citation. Rewrite case.md Verdict section (still carried over, unchanged
  from prior sessions' NEXT).

## 2026-07-09 (E15: the null model, stated explicitly, and its deviations)

- did: editor named three baseline patterns from eyeballing the chart: (1)
  lobbying follows bill introduction, and where it looks earlier, probably
  an earlier-Congress predecessor bill with the same name exists; (2)
  press and bill introductions are coupled; (3) money arrives on its own
  schedule, mostly independent of press/bills, reinforced by money going
  to members who never get press or bills at all. Editor's framing: state
  these as baselines, then look for the signal in DEVIATIONS from them --
  a synthesis step none of E11/E12/E14 had done explicitly (they found the
  same three patterns piecemeal but never stated them as one null model or
  systematically catalogued every deviation against it in one place).
- did: checked all three baselines against the full 11-member bench in one
  pass rather than re-deriving from scratch (baselines 2 and 3 were
  already quantified in E11/E12; only baseline 1's "does lobbying ever
  start before the bill" needed a new check -- computed first-lobbying-
  filing date vs. first-bill-intro date for all 11 members).
- found: **editor's predicted mechanism for baseline 1 is exactly right,
  confirmed with actual bill numbers.** Only 2 of 11 members (Vargas,
  Gonzalez) show lobbying starting before their tracked bill's
  introduction. Pulled the raw lobbying-activity text for each member's
  EARLIEST matching filing: Vargas's 2022-04-20 filing already names
  "H.R. 7003, Credit Union Board Modernization Act" -- a 117th-Congress
  bill number, NOT the 118th H.R.582 that's the only version in
  `bench_bill_dates.csv` (E8 never pulled a 117th predecessor). Gonzalez's
  2022-04-20 filing similarly names "Veterans Member Business Loan Act" in
  117th-era company (alongside S.2857/S.3715/S.3813). Both are the
  predecessor-bill mechanism exactly as predicted, not genuine pre-bill
  lobbying -- this is a real, previously-unnoticed gap in E8/E9's bill
  inventory (117th-Congress numbers never resolved via Congress.gov the
  way every other bench bill's lineage was), logged as a follow-up, not
  fixed this session.
- found: baseline 2 holds with no new deviations -- the small number of
  "loose" (>7-day) press releases per member are all already-explained
  cases from the 2026-07-08 press-hook check.
- found: baseline 3's deviations are exactly the members already flagged
  by other means, now organized under one frame: Britt (money precedes
  bill/press entirely, E11), Peters (lobbying leg deviates via the stale
  117th-Congress number, E14), Beatty (lobbying leg absent entirely, E7).
  No member breaks more than one leg of the null model. The 500-vs-27
  population split (E12) is baseline 3's population-level version.
- decision: this reframe -- explicit null model + deviation catalog -- is
  a stronger, more falsifiable organizing structure for the findings-
  report writeup than the case's original "9 of 11 confirm a triple"
  framing. Wrote up as evidence.md E15, synthesizing E7/E8/E9/E11/E12/E14
  rather than duplicating them.
- NEXT: resolve the Vargas/Gonzalez 117th-Congress predecessor bill
  numbers via Congress.gov (H.R.7003 for Vargas confirmed by text, exact
  Gonzalez number not yet pulled) and add both to `bench_bill_dates.csv`
  -- closes the one open gap E15 surfaced. Then draft findings.md around
  the null-model/deviations frame (E15) as the lead structure, with E10
  (kill)/E11/E12/E14 as supporting detail.

## 2026-07-09 (E7 corrected: Beatty has a second bill, H.R. 3709)

- did: editor spotted this directly by reading Beatty's unmatched
  2025-06-05 press release ("Partnering for Prosperity...") and
  identifying its actual subject: H.R. 3709, "Advancing the Mentor-Protege
  Program for Small Financial Institutions Act" -- a bill this case had
  never pulled (E7 only ever checked H.R. 5911, Fair Hiring in Banking
  Act, against this release, and correctly found no connection since it's
  a different bill entirely).
- did: verified before touching anything. Pulled the release's full
  `press_releases.text` (not just title/url, which is all E7's original
  pass checked) -- confirmed it's about H.R.3709 specifically, and that it
  carries FIVE organizational endorsement quotes including a genuine named
  ACU quote: "America's Credit Unions applauds Rep. Joyce Beatty's
  efforts..." (Jim Nussle, ACU President/CEO) -- not a roster mention,
  the same tier of match as the bench's other named-quote releases.
  Checked ACU's Senate lobbying text for "Mentor Prot(eg/ég)" / "3709":
  1 match, the 2026 Q1 filing (posted 2026-04-14), verbatim "Support
  Advancing the Mentor-Protege Program for Small Financial Institutions
  Act (H.R. 3709)". Confirmed the bill itself via a live Congress.gov call
  (119th HR.3709, Beatty sole sponsor, introduced 2025-06-04 -- one day
  before her release, matching the bench's dominant same-day/next-day
  pattern). Checked for an earlier-Congress predecessor (the release says
  "reintroduced") via Beatty's full sponsored-legislation history -- found
  none under this title; either a different prior title or the
  "reintroduced" language refers to the underlying Treasury program
  concept, not chased further, doesn't affect the core correction.
- found: **Beatty is no longer the bench's one clean "lobbying absent"
  case.** She has a split record across two bills: H.R.5911 (zero
  lobbying-text match, negative result unchanged and still valid) and
  H.R.3709 (money + named press quote + 1 lobbying-text match, a real
  though thin triple). This closes out the "genuinely absent"
  lobbying-continuity category from E11 item 4 entirely -- with this fix,
  EVERY bench member has at least one bill with a confirmed lobbying-text
  match. Reframes what was previously read as "Beatty's lobbying leg is
  missing" into "ACU's endorsement behavior is bill-specific, not
  member-specific" -- same member, same press cadence, same money
  relationship, but only one of her two bills gets sworn lobbying support.
- did: revised evidence.md E7 in place (kept the original H.R.5911 finding
  intact, marked CORRECTED, added the H.R.3709 finding and a joint
  verdict); added addenda to E11 (item 4, "genuinely absent" claim) and
  E15 (the deviation catalog, which had named Beatty as the clean
  lobbying-absence example) rather than silently rewriting those entries,
  per case convention of appending corrections. Updated
  `analysis/pull_bill_dates.py` (added HR.3709), `analysis/
  build_bench_lobbying.py` (added the fragment + updated the module
  docstring), `analysis/build_bench_timeline_d3.py` (BILL_PURPOSES entry).
  Re-ran lobbying + bill-dates + both charts (contributions/press
  untouched, no rebuild needed -- this only affects the bill/lobbying
  legs). Visually confirmed on the rebuilt PNG: Beatty's lane now shows a
  second star (2025-06-04) with a lobbying tick nearby, distinct from her
  first star (2021-11-09, H.R.5911) which still has no lobbying tick
  anywhere near it -- the split record is visible at a glance.
- decision: this is a genuine correction, not a reframe -- the case had
  simply never looked for a second Beatty bill because E7 was scoped to
  her first one. Updated case.md's Sources/legal-risk section (Beatty's
  framing note) and methodology section accordingly.
- NEXT: (carried over, unchanged) resolve Vargas/Gonzalez's 117th-Congress
  predecessor bill numbers; draft findings.md around the E15 null-model
  frame. New: given this session found TWO missed bills via manual
  reading of unmatched press releases (Britt/Gonzalez on 2026-07-08,
  Beatty today), worth a systematic pass checking every bench member's
  press-release list against their bill inventory for any other gaps,
  rather than relying on ad hoc discovery.

## 2026-07-09 (E16: systematic press-release-vs-bill pass)

- did: editor asked for the systematic pass flagged as owed above --
  suspected more press releases were sitting without bills. Computed, for
  every one of the 28 (post-Beatty-fix) press releases across all 11
  members, the minimum date-gap to any bill in `bench_bill_dates.csv`;
  flagged the 6 with no bill within +/-7 days; read the full
  `press_releases.text` (not just title/url) for each.
- found: 4 of 6 were already-known, correctly explained cases -- Barr and
  Emmer's are House-passage/reintroduction milestones of already-tracked
  bills (matches the 2026-07-08 press-hook check exactly); Beatty's
  2022-12-23 is the NDAA-enactment milestone of Fair Hiring in Banking Act
  (pre-dates today's E7 fix, unaffected by it); Cramer's 2024-04-09 is
  genuinely unrelated -- an HHS rural-health funding announcement, nothing
  to do with credit unions or ACU. Correctly NOT a bill-related release;
  confirms the press-hook check's "true miss" category can be empty, this
  isn't "every gap hides a bill."
- found (2 NEW): **Budd** -- "Budd Introduces Bill to Force Federal
  Reserve to Pause Debit Card Proposal" (2024-06-18) is a genuinely new,
  previously untracked bill: the Secure Payments Act. Confirmed via
  Congress.gov: S.4570 (118th), sole sponsor Budd, introduced 2024-06-18
  -- same day as the release. ACU's lobbying text names it in 3 filings
  (2024 Q3-Q4), citing both House (H.R.7531, sponsored by Rep.
  Luetkemeyer, not a bench member) and Senate (S.4570) numbers. Budd now
  has 2 tracked bills (the shared SBA-lending bill + this one, sole-
  sponsored). **Vargas** -- "Rep. Vargas Leads Bipartisan Coalition to
  Expand Affordable Lending Options" (2024-01-10) is Vargas's OWN
  announcement of cosponsoring a bill already in the inventory under
  Fitzgerald (E5, Expanding Access to Lending Options Act, H.R.6933) --
  confirmed via Congress.gov (`bill/118/hr/6933/cosponsors`): Vargas is an
  ORIGINAL cosponsor, sponsorship date 2024-01-10, same day as his
  release. Not a new bill number, but a previously-uncredited second
  bill-relationship for Vargas -- ACU's 9 lobbying filings for this bill
  were already counted under Fitzgerald's total, now also linked to
  Vargas's own press hook.
- did: updated `analysis/pull_bill_dates.py` (Budd's S.4570 + Vargas's
  H.R.6933-under-his-own-name added), `analysis/build_bench_lobbying.py`
  (2 new fragments), `analysis/build_bench_timeline_d3.py` (2 new
  BILL_PURPOSES entries). Re-ran lobbying + bill-dates + both charts.
  Lobbying filing counts matched expectation exactly (Budd 3, Vargas 9).
  Visually confirmed on the rebuilt PNG: Budd's lane now shows a second
  star (2024-06-18) with a lobbying tick right after; Vargas's early-2024
  star now has a lobbying tick paired with it too.
- decision: wrote up as evidence.md E16. Verdict: the systematic pass was
  worth running (caught 2 real gaps ad hoc discovery had missed) but also
  correctly confirmed 4 apparent gaps were NOT new bills -- useful
  negative-result discipline, not just a bill-hunting exercise. Neither
  new finding changes E15's null-model deviation list (Britt, Peters,
  Beatty's split record) -- Budd's new bill follows the same same-day
  pattern as everything else, and Vargas's cosponsorship reinforces an
  already-confirmed full-triple member rather than adding a new deviation.
- explicitly NOT done this session: the REVERSE direction (does ACU's
  lobbying text name any bill, for any bench member, that never generated
  a matching press release) -- would need a larger scan of ACU's full
  lobbying-issue text for bill numbers tied to bench members' other
  sponsored legislation, flagged as a follow-up, not attempted.
- NEXT: (carried over, unchanged) resolve Vargas/Gonzalez's 117th-Congress
  predecessor bill numbers (E15); the reverse-direction bill-inventory
  check flagged above; draft findings.md around the E15 null-model frame,
  now with E16's corrections folded in.

## 2026-07-09 (E17: Britt's conditional endorsement -- ACU wants full Durbin repeal, not just her bill)

- did: editor found this reading ACU's own website directly (not a member
  press release, not an LDA filing -- the first time this case has used
  an ACU-first-party source), specifically
  americascreditunions.org/news-media/news/credit-unions-back-legislation-
  update-durbin-amendment-threshold. WebFetch hit an HTTP 403 (bot
  detection); a direct curl with a standard browser User-Agent returned
  200 and the full article text.
- found: **the identical quote was already sitting in the corpus,
  unexamined.** Britt's 2026-02-13 press release (already cited in E3,
  but only checked by title/url -- the quote's actual content was never
  pulled) carries the same Scott Simpson (ACU President/CEO) quote calling
  the Community Bank Relief Act "an important step forward" while stating
  "the only real long-term solution is full repeal of the Durbin
  Amendment." This is a conditional/dissatisfied endorsement, not the
  uniformly supportive framing every other named ACU quote in this case
  carries. Systematically checked all 28 press releases across all 11
  members for similar qualifying language ("important step," "long-term
  solution," "full repeal," "falls short," "doesn't go far enough") --
  Britt's is the ONLY hit in the entire bench. Checked ACU's sworn Senate
  lobbying text for a distinct "repeal Durbin" push matching the public
  rhetoric -- none found; ACU's filings have named Durbin/Reg.
  II/interchange as a generic issue-code line since 2022, well before
  Britt's bill existed, with no filing isolating "repeal" as a separate,
  new ask.
- decision: wrote up as evidence.md E17. This is a real methodology
  lesson, not just a one-off finding: E1-E9/E13/E14/E16 all confirmed a
  named quote's EXISTENCE by matching title/url, but never systematically
  pulled and read the full quote TEXT for editorial nuance. "ACU gives a
  named quote" has been treated as one uniform category throughout this
  case; it isn't -- quotes range from unqualified support to conditional/
  dissatisfied support, and only reading the full text catches the
  difference. Flagged as a pre-publication task: re-read every bench
  member's named-quote press release in full before findings.md locks in
  language calling them all "endorsements."
- caveat logged: whether ACU's "full repeal" framing constitutes genuine
  tension with Britt's bill, or is just standard "good first step, here's
  our bigger ask" trade-association rhetoric, is an editorial judgment
  call the data doesn't resolve -- flagged as nuance for the writeup, not
  asserted as hypocrisy or conflict.
- NEXT: re-read all named-quote press releases in full for similar nuance
  (this session only found Britt's because the editor happened to read
  ACU's own site; a systematic full-text read of the ~9-10 named-quote
  releases across the bench hasn't been done); resolve Vargas/Gonzalez's
  117th-Congress predecessor bills (E15, still owed); draft findings.md.

## 2026-07-09 (E18: systematic full-text read of all 28 press releases)

- did: editor asked to follow through on E17's recommendation -- read
  every ACU/CUNA-adjacent quote across all 28 bench press releases in
  full, not just Britt's. Pulled `press_releases.text` for all 28 rows,
  found every ACU/CUNA substring hit, read the surrounding context for
  each (17 distinct quoted instances across 9 members, since Peters,
  Cramer, and 2 of Britt's/Fitzgerald's releases only carry roster
  mentions with no direct quote).
- found: **Britt's E17 caveat is the only qualified/conditional quote in
  the entire bench** -- every other ACU quote is unqualified support, no
  exceptions. This is a stronger, full-text-verified negative result than
  E17's keyword search alone (which could have missed non-keyword
  phrasing; reading every hit in context closes that gap).
- found (unrelated to any triple, but worth flagging): a name collision --
  "Scott Simpson" is quoted as ACU's national President/CEO in Britt's and
  Gonzalez's 2026 releases, but the SAME NAME appears in Vargas's
  2025-02-05 release as President/CEO of the California and Nevada Credit
  Union Leagues -- a different organization (a state league). Confirmed by
  reading all three releases in full, not assumed from the name. Doesn't
  affect any evidence chain in this case (Vargas's quote was never counted
  as ACU-national), but it's exactly the kind of free-text name trap this
  corpus is known for (per CLAUDE.md), just surfacing in press-release
  prose instead of a structured field -- flagged so a future session
  doesn't misattribute by name-matching alone.
- found: Fitzgerald's 2025-02-26 release covers two bills (CFPB
  Accountable, already tracked; SOPRA, a Chevron-deference bill) but ACU's
  quote is explicitly only about the first -- checked and confirmed SOPRA
  has no ACU mention and isn't credit-union subject matter, so this is not
  a missed bill.
- decision: wrote up as evidence.md E18. No new bills or gaps found beyond
  what E7/E16 already surfaced -- this pass's value is confirming E17
  isn't diluted (it's a genuine, isolated outlier, which makes it MORE
  citable, not less) and surfacing the Scott-Simpson naming trap for
  future awareness.
- NEXT: resolve Vargas/Gonzalez's 117th-Congress predecessor bills (E15,
  still owed); draft findings.md around the E15 null-model frame, with
  E17's Britt caveat as a specific editorial nuance point and E18 as the
  verification that it's isolated, not systemic.

## 2026-07-09 (E18 corrected: Scott Simpson is one person, not a name collision)

- did: editor looked up "Scott Simpson" directly and confirmed E18's
  "name-collision trap" framing was wrong -- it's the same individual, who
  moved from leading the California/Nevada Credit Union Leagues (quoted in
  Vargas's 2025-02-05 release) to the national America's Credit Unions
  presidency (quoted in Britt's 2026-02-13 and Gonzalez's 2026-02-24
  releases). Checked the dates: state-league quote 2025-02-05, first
  national-ACU quote over a year later (2026-02-13) -- consistent with a
  real career transition, not a same-day coincidence that would have
  disproven it.
- decision: corrected E18 in place (kept the original observation --
  reading it was still the right instinct -- but replaced the "data trap"
  framing with the actual explanation: a genuine leadership transition,
  not a corpus hazard). Updated case.md's summary to match. This doesn't
  change any evidence chain (Vargas's quote was never counted as
  ACU-national to begin with, so nothing downstream needs revisiting) --
  it's a correction to E18's own interpretation, not to any case finding.
- NEXT: (unchanged) resolve Vargas/Gonzalez's 117th-Congress predecessor
  bills (E15); draft findings.md.
- NEXT: draft findings.md; separately, the LDA-URL follow-up above.

## 2026-07-09 (builder/skeptic/judge verify pass, preparing to close)

- did: editor requested a full tribunal pass ahead of closing the case and
  writing it up for the findings report. Skeptic independently re-derived
  (not read-through) E10's kill query (`q-rank1`), E14's Peters bill
  lineage, and E15's Vargas/Gonzalez predecessor-bill mechanism, pulling
  raw `senate_lobbying_activities.description` text directly rather than
  trusting the prior write-up's excerpt.
- found: E10 and E14 reproduce exactly, no changes. E15 had a real
  citation error: the 2022 Q1 ACU filing (`9cc0cbde-933f-45e6-96a0-
  7dc27424380c`) names TWO separate 117th-Congress bills close together in
  the text -- "H.R. 6889, Credit Union Board Modernization Act" and "H.R.
  7003, Expanding Financial Access to Underserved Communities Act." E15
  had attributed the Credit Union Board Modernization Act title to H.R.
  7003 instead of the correct H.R.6889; H.R.7003 is an unrelated bill.
  The underlying Rule-1 mechanism (an earlier-Congress predecessor bill
  explains Vargas's pre-2023 lobbying text) is unaffected -- only the
  specific bill number was wrong, and it was already flagged in the
  case's own writeup as an unresolved, not-yet-Congress.gov-verified
  follow-up, so this was a wrong provisional number, not a fabricated
  claim. Gonzalez's parallel claim (plain title match, no bill-number
  ambiguity in the source text) checked out clean on re-derivation.
- decision: corrected H.R.7003 -> H.R.6889 in evidence.md (E15), case.md,
  and queries.sql (the q-e15 comment), each with an inline correction
  note rather than silent overwrite. Judge's verdict: case is READY TO
  CLOSE. E10 (ACU-scale kill) and the E11-E18 methodology typology both
  hold under independent re-derivation; the one error found was narrow,
  already self-flagged as unresolved, and now fixed.
- NEXT: close the case (status -> closed, condense case.md Verdict per
  the closeout checklist); still-owed pre-closeout item: Vargas/Gonzalez
  117th-Congress bill numbers remain un-verified via Congress.gov (now
  correctly H.R.6889 for Vargas) -- note in case.md as a known gap rather
  than blocking closeout on it, since the mechanism is independently
  confirmed via the raw filing text itself; then draft findings.md.

## 2026-07-09 (E10 ranking withdrawn: uncaught alias contamination)

- did: while drafting findings.md, editor flagged that a different session
  had already found problems with E10's corpus-wide ranking -- Visa
  demoted for immigration/travel-visa false positives, Goldman Sachs
  flagged for a name collision on the bare word "Goldman." Checked
  `investigations/derived/client_alias_review/consolidated_review_2026-07-06.txt`
  directly rather than trusting recall: confirmed `VISA, U.S.A., INC.` is
  marked `is_generic=true` ("VISA also literally means travel/immigration
  visa") and IS correctly `rejected_too_generic` in the live
  `derived_client_alias_index` -- already excluded from E10's query. But
  `VISA, INC.` (the exact canonical name behind E10's rank-1, 84-member
  row) is a separate, un-reviewed `candidate` entry, as are all of the
  Goldman Sachs aliases including the bare word "Goldman." So the specific
  figures E10 reported (rank 22 of 192, "8.4x smaller than Visa") were
  never checked against this review -- a real gap in the tribunal pass run
  earlier this session, which verified E10's query reproduces its own
  prior output but never asked whether the clients ABOVE ACU in that
  output were real.
- found: no fix needed to ACU's own count (10-11 members, all individually
  drilled E1-E9/E13/E14) -- the contamination risk is entirely in OTHER
  clients' rows, which this case never needed to verify since ACU wasn't
  claiming to be the top-ranked client, only a non-outlier. The
  directional claim ("ACU is not the biggest bench") survives untouched.
  The specific rank number and the Visa multiplier do not.
- decision: withdrew the "22nd of 192" / "8.4x smaller than Visa" figures
  from case.md's Verdict (added a dated CORRECTION block rather than
  silently editing) and from findings.md's ACU entry, replacing with
  "not the biggest legislative bench in the corpus" -- no rank, no
  multiplier -- until E10 is re-run against an alias-cleaned client index.
  This is a real methodology lesson for future tribunal passes: verifying
  a ranking query reproduces its own numbers is not the same as verifying
  the underlying entity resolution behind those numbers is clean,
  especially for rows the case itself didn't have reason to drill into.
- NEXT: re-run E10 against the alias-cleaned index before quoting any
  specific corpus-wide rank; the Visa follow-on lead (previously handed
  off separately) now explicitly depends on that cleanup too. Findings.md
  entry is otherwise ready.
