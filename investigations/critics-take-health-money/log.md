# Log — critics-take-health-money

## 2026-06-23
- did: promoted from leads (slug=critics-take-health-money, screen_run_id=12); opened case files
- found: see E1 (scout numbers, unverified)
- dead ends: none yet
- open questions: (1) Are the $FECA totals triple-counting registrants active in HCR+PHA+MMM? Need deduped registrant-level totals. (2) Which specific registrants are both in the FECA donor list AND named in the critical press releases? (3) Do the named members' voting records align with or contradict their rhetorical posture? (4) Is the critical-release count inflated by releases that mention drug prices in passing vs. as the main frame?
- NEXT: Re-derive the full critic list with deduplicated FECA (one registrant counted once per member, regardless of how many issue codes they lobby). Then pull specific registrant names for the top 3 members and cross-check against their press release targets.

## 2026-06-23 (drilldown)
- did: re-derived full leaderboard with deduped FECA (q2); confirmed Pallone ($2.52M/25 releases) and Carter ($1.19M/31 releases with PBM keywords); pulled donor lists for Pallone, Carter, Grassley; checked whether named press-release targets appear in donor records
- found: see E1 (confirmed leaderboard), E2 (Pallone), E3 (Carter + McKesson), E4 (Grassley + Cencora)
- dead ends: PhRMA and Merck do NOT give to Pallone despite being named in his press releases (q6 → no rows). Express Scripts does NOT give to Carter despite being his PBM reform target. The strongest specific-donor conflict is Carter + McKesson (distributor that lobbies PHA/MMM/HCR).
- open questions: (1) What are the committee memberships of each top-14 member, and do they have jurisdiction over the sectors paying them? (jurisdiction is the main boring explanation to test). (2) For the Carter/McKesson finding: does Carter's legislation actually target distributors or only PBMs? If only PBMs, the distinction matters. (3) Voting record check: did these members vote for or against IRA drug pricing, the 2023 Lowering Drug Costs Act, PBM reform bills?
- NEXT: Run verification — builder has made the case; now run skeptic pass. Key skeptic questions: (a) Is the committee-jurisdiction confound explaining the full leaderboard? (b) Does the Carter/McKesson finding survive "they lobby many sectors, health is incidental"? (c) Is the critical-release language actually signaling opposition or is it routine bill-promotion language?

## 2026-06-23 (skeptic + judge)
- did: ran skeptic pass — base-rate comparison (health-committee avg $714k house / $950k senate vs. critic amounts), release-language quality check on Clark, committee membership audit for all 14 top-list members
- found: see E5 (base-rate), E6 (release-language quality)
- dead ends: broad "14 members" framing doesn't survive the committee-jurisdiction confound — Hassan, Kaine, Crapo are near the senate health-committee average; Clark's critical releases are party messaging, not substantive opposition
- verdict: judge verdict → status: supported / confidence: medium. Case refocused on Pallone + Carter as the two strongest specific findings. See case.md.
- NEXT: Novelty scan — has this been reported? Then decide on: (a) whether to deepen the Pallone story (CVS/Pfizer/Humana giving while Pallone names their peers); (b) whether Carter's pharmacist background and PBM-specific focus narrows the finding enough to still be a story; (c) whether a fleet verification on voting records (IRA, PBM reform bills) would strengthen or weaken the case.

## 2026-06-24 (novelty scan → close)
- did: novelty scan across Pallone/pharma, Carter/PBM money, and general "critic takes pharma money" frame
- found: ground is well-covered — KFF Health News runs a dedicated ongoing "Pharma Cash to Congress" tracker; STAT News (2020) found 72 senators and 302 House members took pharma checks; Fierce Pharma covered top House Democrat leaders pocketing pharma millions; the Pallone angle was raised by RFK Jr. in a June 2025 congressional hearing (C-SPAN). Carter + McKesson connection has prior coverage with a more damaging angle (opioid-distributor context, Carter's own pharmacy). House lawmakers criticizing PBMs while taking their money is already a framed story on a sitting member's website.
- novelty sources: https://kffhealthnews.org/news/campaign/ | https://kffhealthnews.org/news/article/pharma-campaign-cash-delivered-to-key-lawmakers-with-surgical-precision/ | https://www.statnews.com/feature/prescription-politics/federal-full-data-set/ | https://www.c-span.org/clip/house-committee/sec-kennedy-accuses-rep-pallone-of-receiving-2-million-of-contributions-from-pharmaceutical-companies/5166292 | https://schrier.house.gov/media/in-the-news/house-lawmakers-rip-middlemen-over-high-drug-prices-despite-welcoming-donations | https://www.opensecrets.org/members-of-congress/buddy-carter/pacs?cat=H04&catlong=Pharmaceuticals/Health+Products&cid=N00035346&cycle=2022&seclong=Health&sector=H
- verdict: close. The "critic takes money" frame is not novel in health/pharma. Our version does not have the specific named-target-is-also-donor finding that would separate it from existing coverage. Two-member focus is too narrow; broader approach would need cross-sector scope or a more damning direct conflict.
- what to keep: the say-vs-pay derived table and cross-corpus join are reusable infrastructure. The "critic takes money" angle may be worth revisiting at fleet scale (cross-sector, not just health) or with voting-record data as a third leg.
- NEXT: none — case closed. Revisit "critic takes money" as a cross-sector fleet-level screen if the newsroom generates a stronger lead.
