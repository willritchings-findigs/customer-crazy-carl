# Client Health weekly refresh: 2026-11-16

Run date 2026-11-16 (UTC), window 2026-08-18 to 2026-11-16 (90 days). Unattended cloud routine (scheduled 14:05 UTC, started 14:08).
Pushed to Base44 `AccountHealthCache` (record `6a834cf871d5a0ff1897bfca`), `computed_at` 2026-11-16T15:05:52Z.
Previous run: 2026-11-09.

## Checks

- Contract check passed: 267 accounts, all Sigma columns (6 probe queries), 14 HubSpot properties, credentials (all network secrets).
- All 8 Sigma results (q1 to q7, gate 6) were saved and proven against Sigma with `sigma_verify.py`: PASS on every query. q6 auto-saved to a file; the other seven were written out from the inline tool output.
- **Sigma data moved during the run.** The first compare failed on q1, q2, q4, q5 and gate 6. Every difference traced to a source change between the pull and the check, not to transcription: Maymont Homes units 18,899 to 18,953 live / 19,793 to 19,847 latest (q4 and gate 6 moved together); seven q1 rows (HomeRiver, Hudson, Kairos, McKinley, Open House, Open Management, Western Wealth: one decision more or fewer each, medians shifted); six q2 rows one submission lower each (HomeRiver, Maymont, McKinley, Open Management, ResiHome, TruHome); seven accounts' Q4 revenue up $339.40 in total (Beztak, CrestCore, Highmark, ResiHome, SFR OpCo, SFR3, Stevens). I re-pulled the five queries and their fingerprints in one batch, re-saved exactly those rows, and all eight then passed. Untouched copies of the verified Sigma files are in the scratch `sigma_raw/` folder.
- **Rollup renames were applied this run and had not been applied to the metrics merge on 2026-11-09.** The baseline's Beztak Properties Parent, Kairos Living LLC Parent, Hudson Homes Management LLC and Payton's Place Real Estate, LLC still carried metric sources dated 2026-11-06, so last week their platform metrics silently carried forward. This run translated the four names in every q-file before the merge (join coverage q1 253/267, q2 265, q3 227, q7 262; last week q1 was 249). No new renames found; config unchanged. Recommendation: add the rename step to a script so it cannot be skipped.
- Validation gates: (1) threshold reproduction, (2) pilot-account unit test, (3) join coverage all passed. (4) No band moved by more than 1. (5) No all-zero metric columns. (6) Live units equal the Unit Counts BI cross-check for all 247 accounts with units.
- Push verified by a fresh GET after the first PUT: `computed_at`, band counts and all 267 accounts matched field by field (0 differences). Snapshot `health_snapshot_2026-11-16` posted (id `6afb1c0246c2ea2bebe61adb`), the enriched overview re-PUT as the newest record, LIST confirmed both, enriched fields read back identical.

## Band distribution

| Band | 2026-11-09 | 2026-11-16 | Change |
|---|---|---|---|
| Green | 130 | 129 | -1 |
| Yellow | 106 | 106 | 0 |
| Red | 21 | 22 | +1 |
| Churned | 9 | 9 | 0 |
| Unscored | 1 | 1 | 0 |

## Band flips (2, both data-driven; no methodology change)

- **Sentral: Yellow to Red.** Platform Red (26.7), Strategic Green (88.6), Sentiment Yellow 22.7 to Red 0.0. Pylon tone went Neutral (2) back to Negative: the verifier confirmed 5 distinct friction issues (#252929 ledger payment discrepancy, #249932 NSF entries when refunding, #239164, #237529, #225633; #254707 dropped as a content request). Slack stays Negative (2026-09-03 rollback request, 2026-10-23 leadership weighing removal of hold/admin-fee properties). Last week's Yellow rested on a borderline 2-vs-3 call; this week the count is 5 and the strictest clustering still gives 3.
- **Realty Solutions LLC: Green to Yellow.** Sentiment pillar 100 to 50: Slack and Pylon tone both moved Positive to Neutral (Pylon #206343 counted as 1 friction; Slack channel Neutral on a thin sample). Platform and Strategic unchanged (Green). Composite 86.2 to 76.2.

## CSM flag changes and contradictions

Two Sigma churn-risk flags now read "Churned" on rollups that still show activity, so both are HELD at the prior band pending CSM review: **Elda Management Services** (was Red; 782 live units, 19 submissions in window) and **MJW Investments Parent** (was Yellow; 0 live units but 33 submissions in window). HubSpot also marks MJW churned (churn_date 2026-11-09) with status Onboarding, so the auto-churn rule did not fire (status contradicts, activity > 0). Gong confirms MJW's deactivation (2026-10-19) and "not a good fit" close-out (2026-11-05). **MJW should be moved to Churned by hand once the activity stops; it scores Yellow (47.8) today.**

## Sentiment: verified overrides and client intel

Slack (144 channels found of 258 active accounts, 98 with zero in-window messages), Gong (29 accounts with in-window call briefs, same count as 11/09; new BVW and MJW, dropped HNN Atlanta and JMAX), Pylon (258 scanned, 251 found, 7 not found).
No Slack or Gong overrides were needed (validator found no out-of-window dates in any rationale). Slack returned 20 Negatives and Gong 5. I re-read two Slack channels against the raw messages (FBM, Point Real Estate) and both matched; I re-read the GC Realty and Kairos briefs and both Negative calls are supported.
Pylon: all 18 scanner Negatives were independently re-pulled and re-adjudicated by three separate verifiers, every cited ticket body read. **Six were overturned to Neutral**, all on the same-incident rule or a ticket that turned out to be working-as-designed: Group Fox (3 to 2), Winfield (3 to 2), Point Real Estate (3 to 2), Evernest (3 to 2), MJW (3 to 2), Imagine Homes (3 to 1). Twelve stand: Kairos 14, Highmark 10, McKinley 7, Sentral 5, Standard Management 4, Lynco 4, Beztak 4, Oakwood 4, Kotarides 4, Brick and Timber 4, Jones and Jones 3, Maymont 3. All 18 corrections (titles, counts, totals) are in `pylon_overrides.json`. After verification Pylon stands at 12 Negative, 32 Neutral, 207 Positive.
Fragile calls (one ticket from flipping): Jones and Jones and Maymont sit exactly at 3; Beztak's 4 includes two tickets Findigs partly attributes to Yardi/Knock; Standard Management's 4 would be 3 if the two Yardi ledger clusters are one defect; Point, Evernest, MJW, Group Fox and Winfield sit at 2 and return to Negative if a follow-up ticket is counted separately.

Client intel worth an AM's attention (mostly not score-affecting):
- **FBM Real Estate (Yellow, 49.0) wants to cancel.** 2026-11-13 CSM note in Slack: consolidating onto Rentengine, income-verification and paystub-calculation problems, applicants find the process too intense. Two-year contract, about $114k term fee at stake, meeting set for Monday. New this week; its Pylon account was not found so Pylon tone carries forward.
- **CORE Residential (Red) filed Pylon ticket #254119 "Ending Our Partnership" on 2026-11-12.** Not counted as friction (billing/contract), but it is a churn notice.
- **Cobalt Property Services (Pylon #250726)** contains a written notice of non-renewal dated 2026-11-11, service through 2027-01-31.
- **GC Realty & Development still scores Green (100.0)** although the 2026-11-05 Gong call confirmed termination (60-day notice) and Pylon #245745 asks about the transition to a new provider. Same situation as last week; needs a human look.
- **MJW Investments Parent**: see CSM flag section; effectively churned.
- **Highmark Residential**: Slack Positive (112-property rollout commitment 2026-09-18, waves to 129 properties/37.6k units, Starwood VP praise 2026-10-14) but Gong Negative (2026-09-09 "significant frustration with support and data accuracy") and Pylon Negative (10 verified, mostly Yardi sync failures). Most-negative-wins keeps the combined Slack/Gong row Negative. Also asked in #250868 how to take Red Road Commons off Findigs.
- **McKinley Companies**: Slack Negative (daily TransUnion delayed-report escalations 2026-11-03, client "not budging" on checkout redesign), Pylon 7 verified frictions with three confirmed outages; Gong notes the client skipped three scheduled calls and the CSM felt "ghosted" for two months.
- **Kairos Living**: Gong Negative through 2026-10-08 ("loss of trust in Findigs' automation"), calmer and operational from 2026-10-22; Pylon 14 verified frictions.
- Still-churning or paused per Slack: Evernest (Boom trial expanding, TN/GA/VA moving off), Harbor Group (deactivated, HubSpot churned 2026-11-05, still scored Red because of in-window submissions), Weiss Parent (does not want to continue, 2026-11-03), Yancey (owner selling the business), Bryten (pause during refinance, unreachable), Legacy Invest (integration failing, likely churn), McCaw (churn email 2026-10-20, moved to Boom), RPM Advantage (asked to cancel 2026-10-05).
- Positives: Western Wealth (Gong, "positive outlook on ongoing partnership", new interface launch agreed), Beztak (Gong, LIHTC pilot agreed 2026-11-13 and six-property launch), Jones and Jones (customer reference), KENCO (client-initiated expansion to two more properties), Mutual (upsell live across 2,800 units 2026-10-15), Excalibur.
- Integration friction flagged by the Slack scan on 21 accounts (mostly Yardi): Maymont (MRI portfolio change), Highmark, Weiss, Brick and Timber, Kotarides, Group Fox, Real Capital (AppFolio), Bryten, Legacy, MJW, Beztak, Sentral, Equity (Buildium), Point (Yardi/RentCafe pricing), Oakwood, Capital PM (AppFolio widget), Redwood, Western Wealth, McKinley, Standard Management, Aulder.

## Gong strategic rows

`build_gong_strategic.py` matched 29 accounts (153 calls assigned, 4 with a review call, 13 with a client exec); 29 on 11/09, so no safety stop. Outside domains seen on client calls, for Will to decide on `account_domain_aliases`: growthholdings.us, otonomushotel.com, jonahdigital.com (Sentral calls); findings.com (Maymont; probably a typo of findigs.com); ballast.com (Brick and Timber; the verifier notes ballast.com is B&T's parent-company systems manager); yardi.com (MJW); dreamlivinghomes.com (10X).

## Staleness and carry-forward notes

142 notes in `wow_diff_1116.json`:
- 108 accounts had no in-window Slack channel or Gong call, so `client_communication_sentiment` was cleared (unscored), not carried forward (122 last week; 11 more channels were found this run).
- 32 notes for accounts with no HubSpot company match; sold-vs-live units carried forward. HubSpot matched 238 of 267 (173 exact); matched units identical to baseline for all 234 accounts that had them, 0 changed.
- 7 Pylon accounts not found, prior tone carried forward where one existed: Taylor & Taylor, ICR Consulting, MIG Management, Renters Warehouse (regional offices only), FBM Real Estate (candidate "FBM Properties" not confirmed), First Place Management, MS Coast Property Management II (candidate "Mississippi Coast Property Management" not confirmed; neither candidate appears in the HubSpot pull). Weiss, Capital PM, HomeRiver and Carolina Management were found this week after not being found on 11/09.
- 115 of 144 Slack channels were thin samples (98 with zero in-window messages); their Neutral calls are defaults, not evidence.
- Pylon `user_type == applicant` was 0 on every account again; the field is sparsely populated, so applicant counts are not evidence that applicants filed nothing.

## Standing holds

Unchanged from the workflow doc: Evernest, RPM Agile, RPM Three Bridges, West USA Realty, PF Holdings (parked), Morgan (future churn date 2026-12-31, scored Churned already).
HubSpot churn-pool hits on non-churned baseline accounts (audit): Evernest (2025-09-29), Harbor Group Parent (2026-11-05; in-window submissions, not auto-churned), MJW Investments Parent (2026-11-09; status Onboarding and in-window submissions, not auto-churned), RPM Rental Solutions, Renters Warehouse, West USA Realty, RPM Three Bridges, RPM Agile.

## Method notes

- No new rollup renames; config.json unchanged. The four existing renames were applied to the q-files before the merge (see Checks).
- Sentiment scans (17 sub-tasks: 8 Slack, 5 Gong, 4 Pylon) and 3 Pylon verifier tasks ran read-only with no Base44 or HubSpot inputs; Gong sub-tasks worked from pre-extracted brief files (domain match identical to `build_gong_strategic.py`), not the Gong API. Every output file was validated against its input (keys, counts, no extras, no duplicates, in-window dates only).
- Base44 is a network secret, so no token file was written.
- No scripts were changed this run.
