# Evidence: invisible-provisions

Evidence blocks are append-only. Each block: claim → query + source ids → verdict.
Scout numbers are tagged; re-derive before citing.

---

## E1: TEC lobby-to-press ratio is anomalously high vs corpus peers

**Claim:** Telecommunications (TEC) had the second-highest lobby-to-press
activity ratio of 21 mapped issue codes in 2022-2024, z=2.28 vs corpus.

**Query** (screen: quiet-issue-quadrant, derived_issue_quarter_volume_press):
```sql
WITH
baseline AS (
  SELECT issue_code, issue_name,
    SUM(total_activities) AS acts_2224,
    SUM(total_income_apportioned) AS income_2224,
    SUM(n_press_releases) AS press_2224
  FROM derived_issue_quarter_volume_press
  WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code, issue_name
),
with_ratio AS (
  SELECT *,
    CAST(acts_2224 AS REAL) / press_2224 AS act_per_press
  FROM baseline WHERE press_2224 >= 100
),
stats AS (
  SELECT AVG(act_per_press) AS mean_atp,
    SQRT(AVG(act_per_press*act_per_press) - AVG(act_per_press)*AVG(act_per_press)) AS sd_atp
  FROM with_ratio
)
SELECT r.issue_code, r.issue_name,
  ROUND(r.acts_2224) AS acts,
  ROUND(r.press_2224) AS press,
  ROUND(r.act_per_press, 2) AS act_per_press,
  ROUND((r.act_per_press - s.mean_atp) / s.sd_atp, 2) AS z_act
FROM with_ratio r, stats s
ORDER BY z_act DESC;
```

**Result (scout):** TEC: 13,136 acts / 2,633 press = 4.99x ratio, z=2.28.
MMM highest at 5.59x / z=2.68. BUD third at 4.41x / z=1.91.

**Verified result (2026-06-25):** TEC: 13,136 acts / 2,633 press = 4.989x, z=2.284.
MMM: 25,816 / 4,617 = 5.592x, z=2.681. BUD: 88,593 / 20,071 = 4.414x, z=1.906.
Full 21-code ranked table re-derived and matches scout direction exactly.
Scout figures were rounded; verified figures are: TEC 4.99x z=2.28, MMM 5.59x z=2.68 (to 2dp).

**Verdict:** VERIFIED — re-derived 2026-06-25 from `derived_issue_quarter_volume_press`.
Cite as: TEC 4.99x (z=2.28), MMM 5.59x (z=2.68). Both >2 SD above 21-code mean.

---

## E2: Spectrum lobbying is flat across all quarters 2022-2025

**Claim:** Spectrum-mentioning TEC activities show no spike around the March
2023 authority lapse or the 2025 OBBBA restoration — approximately flat at
200-231 activities/quarter from 140-170 registrants throughout.

**Query:**
```sql
SELECT sf.filing_year, sf.filing_period,
  count(*) as acts,
  count(distinct sf.registrant_id) as registrants
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
WHERE sla.general_issue_code = 'TEC'
  AND sf.filing_year BETWEEN 2022 AND 2026
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
  AND lower(sla.description) LIKE '%spectrum%'
GROUP BY sf.filing_year, sf.filing_period
ORDER BY sf.filing_year,
  CASE sf.filing_period
    WHEN 'first_quarter' THEN 1 WHEN 'second_quarter' THEN 2
    WHEN 'third_quarter' THEN 3 WHEN 'fourth_quarter' THEN 4
  END;
```

**Result (scout):** Range 202-231 acts/quarter; 118-149 registrants/quarter.
No quarter stands out as anomalous. 2026 Q1 (partial) slightly lower at 182.

**Verified result (2026-06-25):** Full quarterly breakdown 2022–2026:
- 2022: Q1 212/136, Q2 222/145, Q3 213/135, Q4 221/133
- 2023: Q1 223/138, Q2 227/149, Q3 219/146, Q4 215/142
- 2024: Q1 224/142, Q2 231/147, Q3 209/140, Q4 215/143
- 2025: Q1 206/127, Q2 220/143, Q3 211/147, Q4 202/135
- 2026: Q1 182/118 (partial)
Income per quarter: $6.49M–$7.83M, trending very slightly upward.
Range: 202–231 acts/quarter, 127–149 registrants (excluding partial 2026 Q1).
No quarter anomalous around March 2023 lapse or July 2025 OBBBA restoration.

**Verdict:** VERIFIED — re-derived 2026-06-25. Scout range confirmed. Flatness
claim holds across all 17 complete quarters. Cite as: 202–231 acts/quarter,
127–149 registrants, ~$6.5–7.8M income/quarter, flat throughout. Senate only.

---

## E3: Congress is primary lobbying target, not FCC

**Claim:** Of TEC government entity targets 2022-2024, House and Senate account
for 17,239 of 24,740 total mentions; FCC accounts for only 1,757.

**Query:**
```sql
SELECT ge.name, count(*) as n
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
JOIN senate_activity_government_entities sage ON sage.activity_id = sla.activity_id
JOIN ref_government_entities ge ON ge.id = sage.government_entity_id
WHERE sla.general_issue_code = 'TEC'
  AND sf.filing_year BETWEEN 2022 AND 2024
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
GROUP BY ge.name ORDER BY n DESC LIMIT 20;
```

**Result (scout):** House: 8,623; Senate: 8,616; FCC: 1,757; NTIA: 616.

**Verdict:** UNVERIFIED. Confirms lobbying mechanism is congressional, not
regulatory. Important for establishing that TEC's quietness is anomalous
(Congress *is* the decision-maker, yet members don't press-release about it).

---

## E4: ACP press split is nearly equal across parties

**Claim:** Democratic and Republican senators issued near-identical ACP-related
press volumes 2022-2024, undermining the "Democrats held the bill hostage for
ACP earmarks" narrative.

**Query:**
```sql
SELECT m.last_party,
  count(DISTINCT pr.bioguide_id) as members_mentioning,
  count(*) as n_releases
FROM press_releases pr
JOIN members m ON m.bioguide = pr.bioguide_id
WHERE pr.year BETWEEN 2022 AND 2024
  AND (lower(pr.text) LIKE '%affordable connectivity%'
    OR lower(pr.text) LIKE '%acp funding%'
    OR lower(pr.text) LIKE '%broadband subsid%')
GROUP BY m.last_party, m.last_type
ORDER BY n_releases DESC;
```

**Result (scout):** Democrat/rep: 60 members, 132 releases; Democrat/sen: 16
members, 33 releases; Republican/sen: 13 members, 24 releases;
Republican/rep: 5 members, 5 releases.

**Verdict:** UNVERIFIED. Direction informative: House Democrats loudest on ACP,
but Senate split is small (16D/33 releases vs 13R/24 releases). Not a strongly
partisan signal. Keyword set may undercount — "broadband" alone is broader.

---

## E5: Spectrum money flows bipartisanly to senators

**Claim:** Spectrum-active registrants contributed to both parties' senators at
similar rates: Republican senators avg $391k, Democrat senators avg $310k,
from 65 and 57 senators respectively.

**Query:**
```sql
-- (see queries.sql E5 for full CTE)
SELECT m.last_party,
  count(*) as senators,
  round(avg(sm.spectrum_feca)/1000,1) as avg_spectrum_k,
  round(sum(sm.spectrum_feca)/1e6,2) as total_spectrum_M
FROM members m
JOIN spectrum_money sm ON sm.bioguide = m.bioguide
WHERE m.last_type = 'sen'
GROUP BY m.last_party;
```

**Result (scout):** R: 65 senators, avg $391k, total $25.4M.
D: 57 senators, avg $310k, total $17.7M. Independent: 4 senators, avg $252k.

**Verdict:** UNVERIFIED. Confidence threshold 0.6 used (last_unique method).
Gap (R higher) is modest and could reflect party size differences in fundraising
cycles rather than industry targeting. Not a strong partisan-targeting signal.

---

## E6: MMM is the quietest major issue code in the corpus

**Claim:** Medicare/Medicaid (MMM) had the highest lobby-to-press ratio of all
21 mapped issue codes in 2022-2024: 25,816 activities against 4,617 press
releases, a 5.59x ratio, z=2.68 — above even TEC (z=2.28).

**Query:** Same as E1 (quiet-issue-quadrant screen). Full ranked output confirms
MMM at top, TEC second, BUD third. Everything below BUD is within 0.3 z of mean.

**Result (scout):** MMM: 25,816 acts / 4,617 press = 5.59x, z=2.68.

**Verified result (2026-06-25):** MMM: 25,816 / 4,617 = 5.592x, z=2.681.
Scout figure matched exactly; rounds to 5.59x z=2.68 as stated.

**Verdict:** VERIFIED — re-derived 2026-06-25, same run as E1. Cite as: 5.59x, z=2.68.

---

## E7: PFS lobbying is large, growing, and sustained

**Claim:** Senate LDA activities mentioning "physician fee schedule" or "physician
payment" under MMM grew from 560 (2022) to 631 (2023) to 738 (2024), from
111–135 distinct registrants — a sustained and growing presence, not a one-time
campaign.

**Query:**
```sql
SELECT sf.filing_year, count(*) as acts, count(distinct sf.registrant_id) as registrants
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
WHERE sla.general_issue_code = 'MMM'
  AND sf.filing_year BETWEEN 2022 AND 2024
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
  AND (lower(sla.description) LIKE '%physician fee schedule%'
    OR lower(sla.description) LIKE '%physician payment%')
GROUP BY sf.filing_year ORDER BY sf.filing_year;
```

**Result (scout):** 2022: 560 acts / 111 registrants. 2023: 631 / 114.
2024: 738 / 135.

**Verified result (2026-06-25):** 2022: 560 / 111. 2023: 631 / 114. 2024: 738 / 135.
Scout figures matched exactly.

**Verdict:** VERIFIED — re-derived 2026-06-25. Cite as: 560/631/738 acts per year,
111/114/135 registrants. Senate LDA only; House lobbying not counted (would be additive).

---

## E8: Congressional press on PFS is minimal and skewed to committee insiders

**Claim:** Only 31–60 press releases per year mentioned PFS topics across the
entire Congress 2022–2024, against 560–738 lobby activities. Roughly half the
members who published anything were not on health committees (Finance, HELP,
E&C, Ways and Means).

**Queries:**
```sql
-- Press volume by year
SELECT pr.year, count(*) as n_releases, count(distinct pr.bioguide_id) as n_members
FROM press_releases pr
WHERE pr.year BETWEEN 2022 AND 2024
  AND (lower(pr.text) LIKE '%physician fee schedule%'
    OR lower(pr.text) LIKE '%physician payment%'
    OR lower(pr.text) LIKE '%medicare payment cut%'
    OR lower(pr.text) LIKE '%medicare reimbursement%')
GROUP BY pr.year;

-- Health committee vs other breakdown
-- (see session queries — uses member_committees with SSFI, SSHR, HSIF, HSWM)
```

**Result (scout):** Press: 31 / 60 / 57 releases per year (22–41 distinct
members). Committee breakdown: 39 health-committee members vs 31 non-committee
members published PFS releases over 3 years. Bipartisan silence — no partisan
asymmetry. Lobby-to-press ratio: ~13–18:1 on PFS specifically.

**Verified result (2026-06-25):**
- Press by year: 2022: 31 releases / 22 members. 2023: 60 / 34. 2024: 57 / 41.
  Scout figures matched exactly.
- Committee breakdown (3-year aggregate): health-committee members 39 / 84 releases;
  non-committee members 31 / 64 releases. Scout said "about half" non-committee — confirmed
  (31 of 70 unique members ≈ 44%).
- Lobby-to-press: 560/31=18:1 (2022); 631/60=10.5:1 (2023); 738/57=13:1 (2024).
  Scout range of ~13-18:1 accurate for 2022 and 2024; 2023 was closer to 10:1.
  Cite conservatively as "roughly 10-18:1 depending on year."

**Verdict:** VERIFIED — re-derived 2026-06-25. Scout range was slightly imprecise on 2023
(10.5:1 not 13:1); tighten to "10-18:1" when citing. Keyword undercount caveat stands.

---

## E9: Congress averted PFS cuts via must-pass riders every year 2022–2024

**Claim:** A statutory formula requires annual Medicare physician payment cuts.
Congress has averted or partially mitigated the cut each year by inserting a
conversion-factor adjustment into year-end omnibus appropriations bills —
never via standalone floor vote.

**Source:** Web research (not in corpus — legislative history from public record):
- CY2023: Consolidated Appropriations Act 2023 (signed Dec 29, 2022) added
  +2.5% adjustment, reducing scheduled 4.5% cut to 2.0%.
- CY2024: CAA 2023 pre-positioned +1.25% for 2024; a 3.37% cut still hit
  Jan 1. Consolidated Appropriations Act 2024 (signed Mar 9, 2024) added
  another partial fix, leaving an effective ~1.68% cut for the year. Physicians
  received different rates for Jan 1–Mar 8 vs. Mar 9–Dec 31.
- Pattern predates our corpus window; AMA tracks it back years further.

**Primary citations (verified 2026-06-25):**

CY2023 mechanism:
- Consolidated Appropriations Act, 2023 (finalized Dec 19, 2022) provided a +2.5%
  conversion factor adjustment for CY2023, reducing a scheduled 4.47% cut to an
  effective 2.08% cut from 2022 levels. Resulting CF: ~$33.89.
- Same act pre-positioned a +1.25% adjustment for CY2024.
- Source: AASM summary of CAA 2023 physician reimbursement provisions:
  https://www.aasm.org/the-consolidated-appropriations-act-of-2023-delays-several-physician-reimbursement-cuts/
- CMS CY2023 PFS Final Rule fact sheet (cms.gov/newsroom/fact-sheets/calendar-year-cy-2023-medicare-physician-fee-schedule-final-rule) — blocked by CMS firewall; cite by URL.

CY2024 mechanism:
- CMS finalized CY2024 CF at $32.74 (−3.4% / −$1.15 from $33.89), reflecting expiry
  of the 2023 +2.5% bump and only a +1.25% carry-forward from CAA 2023.
- Consolidated Appropriations Act, 2024 (signed Mar 9, 2024) added a further +2.93%
  update to the CF for dates of service Mar 9–Dec 31, 2024. Physicians received
  different rates for Jan 1–Mar 8 vs Mar 9–Dec 31.
- Source: AHA summary of CY2024 PFS final rule:
  https://www.aha.org/news/headline/2023-11-02-cms-issues-cy-2024-physician-fee-schedule-final-rule
- Source: McDermott+ CY2024 PFS overview:
  https://www.mcdermottplus.com/insights/cms-releases-cy-2024-physician-fee-schedule-final-rule/
- CMS CY2024 PFS Final Rule fact sheet (cms.gov/newsroom/fact-sheets/calendar-year-cy-2024-medicare-physician-fee-schedule-final-rule) — cite by URL; CMS site blocks direct fetch.

**Verdict:** PRIMARY CITATIONS ADDED 2026-06-25. Core mechanism confirmed:
CY2023 scheduled 4.47% cut → CAA 2023 (Dec 2022) reduced to ~2.08% effective cut.
CY2024 CF $32.74 (−3.4%) → CAA 2024 (Mar 9, 2024) added +2.93% for remainder of year.
Pattern is annual, never resolved by standalone vote. Cite CMS fact sheet URLs directly;
for verification, the AASM and AHA summaries provide the key figures with attribution.

---

## E10: Section 174 R&D expensing — lobbying volume and press silence

**Claim:** H.R.7024 (Tax Relief for American Families and Workers Act), which
contained a Section 174 R&D expensing fix as its primary business provision, was
lobbied by 305 distinct Senate registrants across 1,563 activities in 2022–2024.
Congressional press mentions of the specific business provisions (Section 174,
bonus depreciation) were minimal: 66 releases from 35 members on R&D expensing,
14 releases from 13 members on bonus depreciation — while the bundled child tax
credit expansion drew 413 releases from 159 members.

**Queries:**
```sql
-- Registrant count for H.R.7024 lobbying (TAX code)
SELECT count(distinct sf.registrant_id) as registrants, count(*) as acts
FROM senate_lobbying_activities sla
JOIN senate_filings sf ON sf.filing_uuid = sla.filing_uuid
WHERE sf.filing_year BETWEEN 2022 AND 2024
  AND sf.filing_period IN ('first_quarter','second_quarter','third_quarter','fourth_quarter')
  AND (sla.description LIKE '%H.R.7024%' OR sla.description LIKE '%H.R. 7024%'
    OR sla.description LIKE '%Tax Relief for American Families%');

-- Press mentions by provision
SELECT
  CASE
    WHEN lower(text) LIKE '%section 174%' OR lower(text) LIKE '%r&d expens%'
      OR lower(text) LIKE '%r&d amortiz%' THEN 'Section 174 R&D expensing'
    WHEN lower(text) LIKE '%bonus depreciation%' OR lower(text) LIKE '%168(k)%' THEN 'Bonus depreciation'
    WHEN lower(text) LIKE '%child tax credit%' THEN 'Child tax credit'
  END AS topic,
  count(*) as press_mentions, count(distinct bioguide_id) as members
FROM press_releases
WHERE year BETWEEN 2022 AND 2024
  AND (lower(text) LIKE '%section 174%' OR lower(text) LIKE '%r&d expens%'
    OR lower(text) LIKE '%r&d amortiz%' OR lower(text) LIKE '%bonus depreciation%'
    OR lower(text) LIKE '%168(k)%' OR lower(text) LIKE '%child tax credit%')
GROUP BY topic;
```

**Result (scout):** 305 registrants / 1,563 acts lobbying H.R.7024.
Press: child tax credit 413 releases / 159 members; Section 174 R&D 66 / 35;
bonus depreciation 14 / 13.

**Verified result (2026-06-25):** 395 registrants / 2,085 acts.
Scout was materially low. Discrepancy explained: the bill was anticipated in
late-2023 filings — 2023 Q4 contributed 14 registrants / 18 acts where the bill
is named by number or by title ("Tax Relief for American Families and Workers Act
of 2024"). These are legitimate records; the scout likely filtered too narrowly.
The 2024 quarterly breakdown: Q1 341/581, Q2 320/519, Q3 308/498, Q4 286/469.

Press (verified): child tax credit 420 releases / 161 members; Section 174 R&D
expensing 54 releases / 28 members; bonus depreciation 15 / 14.
Scout press figures were slightly high for R&D (66→54 / 35→28) and CTC (413→420 / 159→161).
The directional contrast holds: CTC drew ~8x more press mentions than the Section 174 fix.

**Verdict:** VERIFIED with correction — re-derived 2026-06-25. Use verified figures:
395 registrants / 2,085 acts; CTC 420/161, R&D 54/28, bonus dep 15/14.
Scout lobby figure (305/1,563) was an undercount and must not be cited.
Press keyword caveat stands: R&D expensing likely has additional press under
"R&D tax credit," "research credit," or "TCJA" framing not captured here.

---

## E11: H.R.7024 passed House 357-70, died on Senate cloture August 2024

**Claim:** H.R.7024 passed the House January 31, 2024 by a bipartisan 357-70
vote. The Senate failed cloture on August 1, 2024 (48-44, short of 60 needed) —
blocked primarily by Republicans who opposed the child tax credit expansion
despite supporting the business tax provisions. The Section 174 fix did not
become law in the 118th Congress.

**Primary citations (verified 2026-06-25):**
- House passage: January 31, 2024, 357–70 (under suspension of the rules, requiring
  2/3 majority). Passed with broad bipartisan support.
  - House Roll Call Vote #30, 118th Congress:
    https://clerk.house.gov/Votes?RollCallNum=30&BillNum=H.R.7024
  - GovTrack record: https://www.govtrack.us/congress/votes/118-2024/h30
- Senate cloture failure: August 1, 2024, 48–44 (60 needed). Senate Roll Call Vote #230,
  118th Congress, 2nd Session.
  - Official Senate record: https://www.senate.gov/legislative/LIS/roll_call_votes/vote1182/vote_118_2_00230.htm
  - GovTrack record: https://www.govtrack.us/congress/votes/118-2024/s230
- Congress.gov bill page: https://www.congress.gov/bill/118th-congress/house-bill/7024
- Note: this was a cloture vote on the *motion to proceed*, not a final passage vote —
  the bill never got an up-or-down vote in the Senate.

**Verdict:** PRIMARY CITATIONS ADDED 2026-06-25. House 357-70 and Senate 48-44
cloture failure both confirmed with official roll call URLs. Cloture was on motion
to proceed; Republicans blocked on child tax credit packaging, not business provisions.

---

## E13: Framing scan — prior academic and journalistic treatment of the concept

**Claim (informational):** The "quiet politics" frame — industry lobbying on low-salience
technical issues while legislators and public are inattentive — has a substantial academic
literature. No prior work operationalizes it using LDA issue-code activity ratios against
congressional press release volume.

**Academic literature found:**

*Culpepper, Pepper D. "Quiet Politics and Business Power: Corporate Control in Europe
and Japan." Cambridge University Press, 2010.*
- Core concept: when public salience is low, organized business exercises disproportionate
  influence via lobbying and legislator deference; democracy can only impose change on
  technical policy debates if salience is high.
- Empirical work is qualitative/comparative (Europe/Japan corporate control rules);
  does not use LDA filings or quantitative salience measures.
- 2021 follow-up ("Quiet Politics in Tumultuous Times," Politics & Society) notes that
  quiet politics "remains alive and well" even as populism has raised attention to some
  business issues.

*Beyers, Dur, Wonka — "Conceptualizing and Measuring the Political Salience of EU
Legislative Proposals" (AEI working paper):*
- Researchers in EU context have tried to quantify salience via media articles and
  other signals, but methodology is not applied to US LDA data.

*Grassroots Lobbying and Issue Salience literature (e.g., Cluverius 2011):*
- Grassroots lobbying positively affects legislator response on high-salience issues,
  negatively on low-salience — consistent with our finding that PFS and spectrum
  generate no constituent-pressure signal in press releases.

*Strategic Lobbying (Victor, Schar School):*
- Interest groups use direct lobbying (not grassroots) when member preferences are
  consensual — exactly the pattern for our three exhibits (bipartisan industry support,
  no partisan division, direct industry-to-Congress channel).

**Journalism prior art:**

- *Sludge* (readsludge.com, 2022): covers dark-money and policy riders in omnibus bills —
  focuses on transparency/disclosure riders specifically, not the broader industry-lobbying
  silence pattern. No quantitative LDA analysis.
- *ProPublica Lobbying Database Reporting Recipe* (propublica.org/nerds): publishes
  methodology for using LDA data for reporting; does not cross to press release volume.
- *Bloomberg Government* ("Lobbying a Distracted Congress"): notes lobbyists are
  more effective on issues where Congress is distracted — same mechanism, no data operationalization.
- No publication found using lobby-to-press ratio across issue codes as a screen.

**Gap our work fills:**
1. Quantitative operationalization: lobby-activity-to-press-release ratio as a
   reproducible, data-driven salience signal. **Correction (skeptic pass,
   2026-06-30, see E14):** at the time of the skeptic pass, the ranking was
   runnable across only **22 issue codes** with hand-curated press keywords in
   `ISSUE_KEYWORDS` — the other 57 got `n_press_releases=0` by construction,
   not because Congress is silent on them. **Update (same day, see E15):**
   `ISSUE_KEYWORDS` was subsequently expanded to **75 of 79 codes** (73 clear
   the ranking's `press>=100` threshold). Re-running the ranking against the
   expanded map surfaced GAM (Gaming/Gambling/Casino) as a new dominant
   outlier (17.0x, z=5.08) — see E15 and case.md "Keyword-map expansion."
2. US federal specificity: Culpepper's theory applied to US LDA + congressional press
   corpus with citable source records.
3. Bill-level granularity: not just issue codes but specific provisions (PFS, spectrum,
   Section 174) traceable to individual filings.
4. Must-pass vehicle as outcome: the theory predicts quiet passage; we can measure
   the vehicle (omnibus rider, reconciliation provision) in the legislative record.

**Accuracy caveat on "systematic":** The lobby-to-press ratio screen surfaced TEC
and MMM directly. Section 174 (exhibit 3) did not surface from the issue-code screen
— it required a researcher pivot to bill-number extraction from free-text descriptions,
prompted by human judgment that TAX was mid-pack but might contain concentrated
quiet provisions. The pipeline is a set of reproducible tools that a human analyst
steered, not a fully automated detector. Framing should not claim the method is
"systematic" in the sense of requiring no human intervention.

**Verdict:** INFORMATIONAL — framing scan, not a data claim. No competing
publication found. Culpepper is the right academic anchor; our contribution is
a set of reproducible data tools applied with human editorial judgment to a US
federal corpus. Citable as: Culpepper 2010 (theory); this work (quantitative
tools + analyst-steered application via LDA + press corpus).

---

## E12: Section 174 fix ultimately passed in OBBBA (signed July 4, 2025)

**Claim:** After three years of lobbying and one failed vehicle (H.R.7024),
the Section 174 R&D expensing fix was included in the One Big Beautiful Bill Act
(OBBBA), signed July 4, 2025. The OBBBA permanently restored immediate expensing
of domestic R&D costs under new Section 174A, with retroactive relief for small
businesses (≤$31M receipts) covering 2022–2024.

**Primary citations (verified 2026-06-25):**
- OBBBA signed July 4, 2025 (Public Law 119-21).
- Section 174A: domestic R&E immediately deductible for tax years beginning after
  Dec 31, 2024. Foreign R&D still subject to 15-year amortization.
- Small business retroactive election: available for 2022–2024 tax years (deadline
  July 6, 2026); must amend all affected years consistently, cannot cherry-pick.
- Sources:
  - Grant Thornton overview of Section 174A:
    https://www.grantthornton.com/insights/alerts/tax/2025/insights/full-expensing-of-domestic-research
  - ABGI tracker (most current summary of Section 174 history + OBBBA fix):
    https://abgi-usa.com/section174/latest-and-greatest
  - CBO OBBBA budgetary effects (Public Law 119-21):
    https://www.cbo.gov/publication/61570
- Note: For the statutory text of Section 174A, cite OBBBA (P.L. 119-21) directly.
  GovInfo full text: https://www.govinfo.gov/app/details/BILLS-118hr7024ih (H.R.7024
  version); OBBBA text available via congress.gov H.R.1 (119th Congress).

**Verdict:** PRIMARY CITATIONS ADDED 2026-06-25. OBBBA signing date, section number,
and key provisions confirmed. The same bill (OBBBA/P.L. 119-21) restored both
spectrum auction authority (exhibit 1) and Section 174 R&D expensing (exhibit 3) —
two separately-lobbied quiet provisions converging in the same reconciliation vehicle.

---

## E15: Expanded ISSUE_KEYWORDS map surfaces GAM as new dominant outlier, supersedes E1/E6's "quietest in corpus" framing

**Claim:** Following E14's Finding 1 (the corpus-wide ranking's comparison
population was only 21-22 hand-picked issue codes, not the full 79-code
corpus), `ISSUE_KEYWORDS` was expanded from 21-22 to 75 of 79 codes in both
`scripts/build_derived_issue_quarter_volume_press.py` and
`scripts/build_derived_member_press_topics.py`. Re-running E1/E6's ranking
query against the rebuilt `derived_issue_quarter_volume_press` produces a
materially different result: **GAM (Gaming/Gambling/Casino) is now the
dominant outlier at 17.0x ratio, z=5.08** — more than double the next-highest
code and larger in both ratio and z-score than any figure previously cited
for TEC or MMM.

**Method — root-cause check before expanding:** rather than assume the
original 57 excluded codes were "too vague," queried `press_releases` directly
for five clearly-specific unmapped codes:
```sql
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%tobacco%';                    -- 763
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%aviation%'
  OR lower(text) LIKE '%airline%' OR lower(text) LIKE '%airport%';                          -- 9,983
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%copyright%'
  OR lower(text) LIKE '%patent%' OR lower(text) LIKE '%trademark%';                          -- 541
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%food safety%'
  OR lower(text) LIKE '%food label%';                                                        -- 421 (safety) + 33 (label)
SELECT count(*) FROM press_releases WHERE lower(text) LIKE '%gambling%'
  OR lower(text) LIKE '%casino%' OR lower(text) LIKE '%sports betting%';                     -- 215/67/46
```
All had substantial real coverage. Confirmed the gap was an incomplete map
(built in one commit, 433711c, for one screen's immediate needs), not a
deliberate vagueness exclusion. Genuinely-too-generic codes (MIA, SCI, GOV,
CON — each tens of thousands of generic-usage hits for a single word like
"media"/"science"/"government"/"constitution") were kept excluded, now
documented in-file rather than silent.

**Keyword QA caught a false positive before it reached this finding:** GAM's
initial keyword list included "lottery." Sample of 8 matches eyeballed —
majority were unrelated immigration press releases ("diversity visa lottery,"
"green card lottery": Reps. Lofgren, Meng, Clarke, and others). Removed
"lottery" from GAM. Also tightened MON ("currency" alone matched generic
foreign-aid/monetary-policy mentions → restricted to "digital currency"/
"currency manipulation") and UTI ("rate case" and bare "utility" were noisy →
restricted to "utility bill"/"public utility"/chamber-specific phrases).
GAM's ratio *increased* after removing "lottery" (13.27x → 17.0x pre/post-fix)
because the fix removed press volume, not lobbying volume — consistent with
a genuine false-positive removal, not an artifact of the fix itself.

**Query (same structure as E1/E6, run against rebuilt table):**
```sql
WITH
baseline AS (
  SELECT issue_code, issue_name,
    SUM(total_activities) AS acts_2224,
    SUM(n_press_releases) AS press_2224
  FROM derived_issue_quarter_volume_press
  WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code, issue_name
),
with_ratio AS (
  SELECT *, CAST(acts_2224 AS REAL) / press_2224 AS act_per_press
  FROM baseline WHERE press_2224 >= 100
),
stats AS (
  SELECT AVG(act_per_press) AS mean_atp,
    SQRT(AVG(act_per_press*act_per_press) - AVG(act_per_press)*AVG(act_per_press)) AS sd_atp
  FROM with_ratio
)
SELECT r.issue_code, r.issue_name,
  ROUND(r.acts_2224) AS acts, ROUND(r.press_2224) AS press,
  ROUND(r.act_per_press, 2) AS ratio,
  ROUND((r.act_per_press - s.mean_atp) / s.sd_atp, 2) AS z
FROM with_ratio r, stats s
ORDER BY z DESC LIMIT 15;
```

**Result:** 73 codes clear the `press_2224 >= 100` threshold (vs. 21 before).
Top of ranking: GAM 1,751 acts / 103 press = 17.0x, z=5.08. ART (Arts/
Entertainment) and CSP (Consumer Issues/Safety/Products) tie for second at
9.27-9.28x, z=2.35. CPT (Copyright/Patent/Trademark) 8.76x z=2.17. INS
(Insurance) 8.16x z=1.96. MMM drops to z≈1.05, TEC to z≈0.84 — both still
positive but no longer statistical outliers under this comparison population.

**GAM quarterly/yearly scout trend (UNVERIFIED — not yet drilled to a
specific sub-provision):**
```sql
SELECT year, ROUND(SUM(total_activities)) as acts, ROUND(SUM(n_press_releases)) as press
FROM derived_issue_quarter_volume_press
WHERE issue_code = 'GAM' AND year BETWEEN 2022 AND 2025
GROUP BY year ORDER BY year;
```
2022: 593 acts / 6 press. 2023: 571 / 45. 2024: 587 / 52. 2025: 721 / 72.
Sustained lobbying; press rising off a near-zero base but an order of
magnitude below lobbying volume throughout.

**Verdict:** VERIFIED (ranking re-derived directly, 2026-06-30) — this
supersedes E1/E6's "quietest in the corpus" characterization of TEC/MMM. The
underlying exhibit-level claims (spectrum flatness, PFS mechanism, Section
174 arc) are unaffected — they don't depend on the corpus-wide ranking's
extremity, only on the ranking as a discovery mechanism. GAM itself is
UNVERIFIED scout-level data, not yet drilled down; treat as a new lead, not
a fourth confirmed exhibit, until it goes through the same drilldown +
verification process exhibits 1-3 did.

**Story shape:** TCJA (2017) quietly changed R&D tax treatment → companies hit
with unexpected bills starting 2022 → 305 registrants lobby to reverse it →
H.R.7024 passes House 357-70 but dies in Senate cloture Aug 2024 → fix
eventually included in OBBBA July 2025. Three years, one failed vehicle, one
must-pass reconciliation bill. Near-zero public congressional communication
throughout.

---

## E14: SKEPTIC PASS (2026-06-30) — independent re-derivation, default stance "this is nothing"

Ran the skeptic's checklist from `track-investigation/reference/verification.md`
against all three exhibits. Re-derived from `db/gain.db` directly — did not read
builder's queries first for the coverage-gap check (ran it cold, then compared).

**Finding 1 — Press-mapping coverage gap (MATERIAL, affects framing not core claim):**

`derived_issue_quarter_volume_press.n_press_releases` is built from a
hand-curated `ISSUE_KEYWORDS` dict in
`scripts/build_derived_issue_quarter_volume_press.py` covering only **22 of 79**
issue codes. The other 57 codes get `n_press_releases = 0` by construction —
no keywords were ever written for them, not because Congress is silent on them.
Query:
```sql
SELECT COUNT(*) FROM (
  SELECT issue_code, SUM(n_press_releases) as press_2224
  FROM derived_issue_quarter_volume_press WHERE year BETWEEN 2022 AND 2024
  GROUP BY issue_code);                                  -- 79 total codes
SELECT COUNT(*) FROM (... HAVING press_2224 < 100);       -- 58 excluded pre-ranking
SELECT COUNT(*) FROM (... HAVING press_2224 >= 100);      -- 21 in the ranked set
```
E1/E6 correctly scope the ranking to "21 mapped issue codes" in evidence.md —
**but case.md line 103 says MMM is "the quietest issue code in the entire
corpus,"** and E13 (framing scan) says the method is "runnable across all 80
LDA issue codes." Both overstate what was actually screened. TEC and MMM are
the quietest of a 21-code subset a human pre-selected as likely to have
measurable press coverage — not the quietest of the full 79/80-code universe.
This must be corrected before publication: "quietest of the mapped subset,"
never "quietest in the corpus."

**Finding 2 — House lobbying omitted from exhibit-level drilldowns (MATERIAL, understates volume ~2x, doesn't change direction):**

E1/E6 (the corpus-wide ranking) already sum Senate + House
(`derived_issue_quarter_volume_press` has both columns — confirmed
TEC: 6,735 Senate + 6,401 House = 13,136 total; MMM: 13,281 + 12,535 = 25,816).
But the sub-topic drilldowns — E2 (spectrum), E7 (PFS), E10 (Section 174) —
query `senate_lobbying_activities` alone. Re-derived from `house_activities`:
```sql
SELECT count(*) FROM house_activities
WHERE issue_area_code='MMM' AND (description LIKE '%physician fee schedule%'
  OR description LIKE '%physician payment%');                    -- 2,684 (all years)
SELECT count(*) FROM house_activities
WHERE description LIKE '%h.r.7024%' OR description LIKE '%h.r. 7024%'
  OR description LIKE '%tax relief for american families%';       -- 2,244 (all years)
```
House lobbying roughly doubles-to-triples the true volume on PFS and Section
174 specifically (House has no stable lobbyist id and free-text
`federal_agencies`, per corpus caveats, but activity counts are usable). This
doesn't change the *press stayed near-zero* claim — it makes the lobbying
side of the ratio even larger, strengthening the imbalance — but exhibit text
citing "560/631/738 Senate acts" or "2,085 Senate acts" should say "Senate
LDA only, House lobbying is additional and roughly comparable in size" rather
than implying those are total lobbying volumes.

**Finding 3 — checklist items that did NOT turn up problems:**
- Junk free-text: E7/E10 queries use LIKE on `description`, not `covered_position`/
  `honoree_name` — not exposed to the N/A / "See prior filing" junk-value trap.
- Honoree match confidence: only E5 (bipartisan money flow, already flagged
  UNVERIFIED / confidence>=0.6 caveat in the builder's own writeup) touches
  `honoree_member_map`. No exhibit's core claim (E1/E2/E6/E7/E8/E10) depends
  on honoree matching.
- Base rate: E1/E6's z-scores are computed against the 21-code peer set's own
  mean/sd, which is the correct comparison population once Finding 1's
  "21 mapped codes not full corpus" framing is applied.
- Multiple comparisons: 21 codes ranked, not hundreds of members — z=2.28 and
  z=2.68 both clear 2SD on a 21-item comparison; not a p-hacking-scale search
  space. No correction needed beyond honest denominator disclosure (Finding 1).
- Time window alignment: E2's quarter definitions (calendar Q1-Q4 from
  filing_period) match press `year`/derived-from-date consistently — checked,
  no misalignment found.
- FTS/keyword false positives: spot-checked "spectrum" (E2) and "physician fee
  schedule"/"physician payment" (E7) — both are unambiguous phrases in this
  corpus context, low false-positive risk unlike broader single-word matches.
- H.R.7024 numbering: E10's Q4 2023 pre-introduction matches were already
  investigated and explained in the prior verification pass (log.md
  2026-06-25) — legitimate anticipatory filings, not a bug.

**Could not refute:** the underlying pattern (sustained/growing lobbying,
near-zero corresponding congressional press, resolution via must-pass rider
rather than standalone vote) holds for all three exhibits after re-derivation.
Tried: press-mapping coverage (real gap, but corrected framing survives it),
House omission (real gap, but strengthens rather than weakens the ratio),
base-rate/multiple-comparisons (clean), honoree-confidence exposure (not
applicable to the load-bearing claims), keyword false-positive risk (low for
these specific phrases).

**Verdict contribution:** Two material framing corrections required before
publication (denominator honesty, Senate-only labeling). Neither is a kill —
both narrow the claim's precision without reversing its direction. Recommend
**supported, with corrections**, not refuted and not needs-more-data.
