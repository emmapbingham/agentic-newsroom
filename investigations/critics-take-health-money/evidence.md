# Evidence — critics-take-health-money

## E1 — Full critic+money leaderboard (deduped FECA, q2)
- **query/script:** `queries.sql#q2`
- **result:** 20 members with ≥10 pharma-opposition releases AND health-sector FECA in 2022–2024 (deduped: one registrant counted once per member). Top 14 clearing $500k: Pallone $2.52M/287 registrants, Neal $2.44M/258, Clark $2.16M/272, Hassan $2.14M/290, Kaine $1.92M/290, Crapo $1.78M/234, Heinrich $1.60M/255, Baldwin $1.40M/253, Carter $1.19M/209, Warner $1.03M/173, Grassley $993k/184, Matsui $947k/160, Craig $852k/193, Trahan $762k/177.
- **source records:** derived_member_issue_money_panel + senate_contribution_items + press_releases
- **caveats:** Keyword set for "critical releases" is recall-oriented (drug price / big pharma / insulin price / price gouging / lower drug) — may count releases where criticism is incidental. Carter's 16 in E1-scout grew to 31 when "pbm" added (q7); the 2022–2025 window for press vs. 2022–2024 for FECA is intentional (gives full coverage of legislative activity). Honoree map confidence ≥ 0.9 throughout.
- **verdict:** supports — leaderboard confirmed, numbers re-derived

---

## E2 — Pallone: 25 critical releases + $2.52M deduped health FECA
- **query/script:** `queries.sql#q3` (release count), `queries.sql#q4` (FECA total), `queries.sql#q5` (donors)
- **result:** 25 critical releases 2022–2025 (q3). $2.52M from 287 health-sector registrants 2022–2024 (q4). Top donors include CVS Health ($52.5k across 3 years, lobbies PHA+MMM), Pfizer ($12.5k, 2023, lobbies MMM+HCR), Humana ($12.5k, 2024, lobbies HCR+MMM+PHA), Capitol Counsel LLC ($37.2k, lobbies HCR+MMM+PHA), Elevance Health ($11k, 2023, lobbies HCR+MMM+PHA) (q5).
- **source records:** Press releases at pallone.house.gov (URLs in q3 result). CVS Health filing_uuid: ce31d446-c5f1-49f3-a23c-a21ee3d904c1 (2024). Pfizer filing_uuid: ce25b617-1b18-4143-a0da-b77a4bf2a03b (2023). Humana filing_uuid in q5 result.
- **caveats:** Pallone publicly names PhRMA (June 2023 release on PhRMA lawsuit) and Merck (June 2023 on Merck's Medicare lawsuit) — but neither PhRMA nor Merck appear in the LD-203 donor record for Pallone (q6 → no rows). The tension is with the broader sector, not a single named target giving to him.
- **verdict:** supports — Pallone criticizes the sector publicly while receiving significant money from its members; the most prominent named targets (PhRMA, Merck) are not in his donor record, which *limits* the direct conflict

---

## E3 — Buddy Carter: 31 critical releases + $1.19M health FECA; McKesson is both donor and target
- **query/script:** `queries.sql#q7` (release count), `queries.sql#q8` (FECA total), `queries.sql#q9+q10` (McKesson)
- **result:** 31 critical releases 2022–2025 (incl. PBM reform push) (q7). $1.19M from 209 health-sector registrants 2022–2024 (q8). McKesson gave $20k across 2022–2024 (filing_uuids: 245bb674, 31282006, c73c6fdd) and lobbied PHA, MMM, HCR in those years (q10). Cardinal Health gave $20k (filing_uuids: 6980fc36, 594df58a), also lobbies HCR. Carter named Express Scripts specifically in a June 2024 letter (release: buddycarter.house.gov/news/documentsingle.aspx?DocumentID=12926).
- **source records:** Press release URLs in q7 result. McKesson filing_uuids: 245bb674-7b20-465d-b82e-911ed3ade43c (2024), 31282006-540f-4d69-a310-82d9c29f4ae3 (2022), c73c6fdd-ae78-449a-8a73-38d3e6690ea1 (2023). LD-203 public URLs: https://lda.gov/filings/public/contribution/245bb674-7b20-465d-b82e-911ed3ade43c/print/ etc.
- **caveats:** Carter is a licensed pharmacist — his PBM reform focus is professionally motivated, not necessarily inconsistent with receiving money from drug distributors. McKesson is a distributor, not a PBM; Carter's sharpest criticism targets PBMs (Express Scripts, CVS Caremark). Express Scripts does NOT appear in Carter's donor record. The McKesson/Cardinal donations are real but the rhetorical targets differ from the actual donors.
- **verdict:** supports-with-nuance — there is sector-wide money and sector-critical rhetoric; the specific named targets (PBMs) differ from the actual donor companies (distributors); Carter's pharmacist background is a structural confound

---

## E5 — SKEPTIC: Base-rate test — is committee jurisdiction explaining the leaderboard?
- **query/script:** base-rate query (inline, add to queries.sql as q11)
- **result:** Health-committee House members average $714k health FECA; non-committee House members average $290k. Senate health-committee members average $950k; non-committee senators $586k. Among ALL House Democrats receiving any health FECA (n=289), average is $375k. Among Senate Democrats (n=57), average is $729k.
- **source records:** derived from senate_contribution_items + honoree_member_map + member_committees
- **caveats:** "Other" category includes Appropriations members who control health funding without sitting on health committees — that inflates "other."
- **verdict:** partially refutes — committee jurisdiction explains a substantial portion of the money. Pallone ($2.52M vs. $714k committee-member average = 3.5x) and Neal ($2.44M, 3.4x) are still outliers even within health-committee members. Carter ($1.19M vs. $714k rep-committee average = 1.7x) is less extreme. Hassan/Kaine/Crapo are near the Senate committee-member average ($950k).

## E6 — SKEPTIC: Is "critical release" language genuine opposition or routine bill-promotion?
- **query/script:** Clark releases (q inline)
- **result:** Clark's 10 "critical" releases include State of the Union responses, party whip messaging, and IRA celebration statements — only 2-3 are primarily about drug prices. Her critical-release count is inflated by broad legislative messaging. By contrast, Pallone's 25 releases include specific named-company releases (PhRMA lawsuit, Merck lawsuit) and constituent-facing town halls. Carter's 31 includes detailed PBM reform legislation and FTC report responses — these are substantively critical, not incidental mentions.
- **verdict:** partially refutes for some members (Clark, Hassan, Kaine may be inflated by leadership messaging); supports for Pallone and Carter who have substantive named-entity criticism

## E4 — Grassley: 37 critical releases + $993k health FECA; Cencora donor lobbies PHA
- **query/script:** `queries.sql#q2` (leaderboard), Grassley donor query (inline in session)
- **result:** Grassley had 37 critical releases (2022–2025 window) and $993k deduped health FECA. Cencora (formerly AmerisourceBergen, drug distributor) gave $11.5k in 2022 (filing_uuid: dfaa654d) and lobbies PHA+MMM+HCR. Grassley co-authored opioid transparency legislation with Hassan (2025). His 2022 donor list is heavily lobbying-firm-dominated (K&L Gates, Holland & Knight, Brownstein Hyatt, Faegre Drinker) — large, multi-sector firms that happen to include health in their issue portfolio.
- **source records:** Grassley filing_uuid for Cencora: dfaa654d-3edb-4dd3-b610-71ce3cf41f3d. Public URL: https://lda.gov/filings/public/contribution/dfaa654d-3edb-4dd3-b610-71ce3cf41f3d/print/
- **caveats:** Most of Grassley's health-sector FECA comes from large law/lobbying firms with many clients, not directly from pharma companies. His drug-price criticism is bipartisan and long-standing; the Inflation Reduction Act IRA drug-pricing mechanism is one area where he *opposed* the Biden approach while supporting his own competing bills. More nuanced picture needed.
- **verdict:** needs-follow-up — the broad health-sector FECA is real, but the specific-donor tension is weaker than for Pallone or Carter
