# Client Health weekly refresh: 2026-11-09

Run date 2026-11-09 (UTC), window 2026-08-11 to 2026-11-09 (90 days). Unattended cloud routine (scheduled for 14:06 UTC, started 14:10).
Pushed to Base44 `AccountHealthCache` (record `6a834cf871d5a0ff1897bfca`), `computed_at` 2026-11-09T14:42:04Z.
Previous run: 2026-11-06.

## Checks

- Contract check passed: 267 accounts, all Sigma columns, 14 HubSpot properties, credentials (all network secrets).
- All 8 Sigma results (q1 to q7, gate 6) were saved and proven against Sigma with `sigma_verify.py`: PASS on every query. q6 auto-saved to a file; the other seven were written out from the inline tool output.
- **Sigma data moved during the run.** The first compare failed on q1, q2, q4, gate 6 and q5. I traced each difference to a real source change, not only transcription: Maymont Homes units 18,912 to 19,500 live / 19,806 to 20,394 latest (q4, gate 6); Open House Management decisioned 1,434 to 1,433 and median UW hours 14.39 to 14.4 (q1); GC Realty, Lacy and Open House submitted counts one lower each (q2); and seven accounts' Q4 revenue rose by exactly $381.59 in total (q5: Highmark, Maymont, Oakwood, ResiHome, Rookwood, SFR3, Vision). I re-saved those rows from fresh Sigma pulls, and the fingerprint then passed on all eight. One genuine copy error of mine was also caught and fixed (Morgan Property Management `any_churned`, true).
- Validation gates: (1) threshold reproduction, (2) pilot-account unit test, (3) join coverage (q1 249/267, q2 261, q3 229, q7 258) all passed. (4) Only one band moved: no color moved more than 1. (5) No all-zero metric columns. (6) Live units equal the Unit Counts BI cross-check for every account (247 accounts with live units, applying the rollup renames).
- Push verified by a fresh GET after the first PUT: `computed_at`, band counts and all 267 accounts matched field by field (0 differences). The snapshot `health_snapshot_2026-11-09` was posted and the enriched overview re-PUT as the newest record; a LIST confirmed both, and the enriched fields (account manager, CSA, prior band, weeks red, band history) read back identical.

## Band distribution

| Band | 2026-11-06 | 2026-11-09 | Change |
|---|---|---|---|
| Green | 130 | 130 | 0 |
| Yellow | 105 | 106 | +1 |
| Red | 22 | 21 | -1 |
| Churned | 9 | 9 | 0 |
| Unscored | 1 | 1 | 0 |

## Band flips (1, data-driven; no methodology change)

- Sentral: Red to Yellow. Platform Red (26.7), Strategic Green (88.6), Sentiment Red 0.0 to Yellow 22.7. The sentiment pillar moved because the Pylon ticket tone went from Negative to Neutral after verification. **This flip rests on a borderline call**: the verifier counted 2 friction tickets (#249932, #225633) and left #239164 out; counting it makes 3 and Negative, which would put Sentral back at Red. Slack for Sentral is still Negative (rollback request 2026-09-03; leadership weighing removal of properties with hold/admin fees, 2026-10-23). Treat the improvement as soft.

## CSM flag changes and contradictions

None. No new Sigma churn flags.

## Sentiment: verified overrides and client intel

Slack (133 channels read, none missing), Gong (29 accounts with in-window call briefs), Pylon (258 accounts scanned; 13 not found initially, 2 resolved on re-search).
No Slack or Gong overrides were needed. Slack returned 19 Negatives and Gong 4. I re-read three Slack channels against the raw messages (Harbor Group, Modern City, McCaw) and all matched; I re-read the Gong briefs behind GC Realty, SFR3 Operator, Kairos and Highmark and all four classifications are supported (SFR3 rests on a single brief).
Pylon: all 15 initial Negatives were independently re-pulled and re-adjudicated by separate verifiers; Standard Management Company Parent was resolved on re-search and pulled the same way. After verification Pylon stands at 14 Negative, 31 Neutral and 202 Positive among the 247 accounts found. Two Negatives changed: **Sentral** (Neutral, 2) and **Western Wealth Parent** (Neutral, 2). Corrections to titles and counts for the rest are in `pylon_overrides.json`: Maymont (4 to 3), Oakwood (4 to 3), Beztak (4 to 8), Kotarides (3 to 4), Jones and Jones (3 to 5), Kairos (18, three titles swapped), RPM Southland (3, one swapped), Winfield (4), McKinley (8, one swapped). Highmark (10 listed, about 10 more), Brick and Timber (5) and Standard Management (10) are clearly Negative.
Accounts sitting exactly at the 3-ticket threshold (fragile): Maymont, Oakwood, Imagine Homes, Lynco, RPM Southland. Oakwood falls to 2 if two tickets for the same incident are counted as one; RPM Southland the same.

Client intel worth an AM's attention (Slack/Gong, mostly not score-affecting):
- **GC Realty & Development scores Green (100.0)** even though the Gong call on 2026-11-05 confirmed termination of the service agreement (60-day notice; cost, integration and UI). Slack/Gong sentiment is Negative, but the pillar rules do not move the band. **Needs a human look.**
- **MJW Investments Parent** is Yellow (47.8) with Slack Negative: the client threatened on 2026-10-07 to turn Findigs off and asked on 2026-10-19 to disconnect. Same situation as last week's report.
- Kairos Living: Gong shows repeated frustration and loss of trust in automation (September to 2026-10-08), more collaborative since late October; Slack shows the 2026-09-21 "right fit" comment and an opt-out of Task Service.
- SFR3 Operator: Gong 2026-08-27 quarterly review, client raised possible churn over the application overhaul and voucher handling (one brief).
- Slack Negatives (mostly Findigs staff relaying the client): Standard Management (reconciliation, "churn risk" 2026-10-30), Real Property Management Advantage (wants to cancel, 2026-10-05), Weiss Parent (does not want to continue, 2026-11-03), McCaw (churn email 2026-10-20, moved to Boom), Evernest (Boom trial expanding), Bryten and Legacy Invest (pause / expected churn; PMS integration failing), Yancey (selling the business), Harbor Group Parent (deactivated 2026-10-13, HubSpot churned 2026-11-05), Bridge Homes (acquired, deactivated), MJW, McKinley, Oakwood, Brick and Timber, Beztak (borderline), Sentral, Modern City (one message), Rent Appeal.
- Highmark Residential: Gong Negative (September frustration with support and data accuracy) while Slack is Neutral.

## Staleness and carry-forward notes

159 notes in `wow_diff_1109.json`. The main ones:
- 32 notes for accounts with no HubSpot company match, where sold-vs-live units are carried forward.
- 122 accounts had no in-window Slack channel or Gong call, so `client_communication_sentiment` was cleared (unscored), not carried forward.
- 11 Pylon accounts were not found and carry the prior tone forward: Taylor & Taylor, Weiss Parent, Capital Property Management Parent (two Pylon accounts share the name), ICR Consulting, MIG Management, Carolina Management Parent, HomeRiver Group Holdings (candidate "HomeRiver Group LLC", not exact), Renters Warehouse (only regional branches), FBM Real Estate, First Place Management, MS Coast Property Management II. Five of these (HomeRiver, Capital, FBM, MS Coast, Weiss) generated an explicit stale note; the rest had no prior tone to carry.
- 78 of 133 Slack channels had zero in-window messages (97 are thin samples); their Neutral/thin_sample calls are defaults, not evidence. Most `#p-*` channels are Findigs-internal, so the Slack component is relayed sentiment.
- Pylon applicant counts came back 0 everywhere (`user_type == applicant` is populated on only about 5% of tickets); this is a field-coverage effect, not proof that applicants never filed.
- Unconfirmed channel mappings from the Slack scan: Carolina Management maps to `#rpm-queen-city`, and ICR Consulting to `#p-remax-haven-realty` (both zero or near-zero in-window messages).

## Standing holds

Unchanged from the workflow doc: Evernest, RPM Agile, RPM Three Bridges, West USA Realty, PF Holdings (parked), Morgan (future churn date 2026-12-31, scored Churned already).
HubSpot churn-pool hits on non-churned baseline accounts (audit): Evernest (churn date 2025-09-29), Harbor Group Parent (churn date 2026-11-05; still Red and scored, not auto-churned because of in-window submissions), RPM Rental Solutions, Renters Warehouse, West USA Realty, Real Property Management Three Bridges, Real Property Management - Agile.

## Method notes

- No new rollup renames this run (config unchanged).
- `gong_strategic_rows.json` was built with a scratch script (domain match on `hs_account_match.json`); the same 29 accounts as 2026-11-06.
- Sentiment scans (17 sub-tasks: 8 Slack, 5 Gong, 4 Pylon) and 3 Pylon verifier tasks ran read-only with no Base44 or HubSpot inputs. One Pylon sub-task reported finding about 60 foreign entries in its output file; I checked every output file against its input afterwards (keys, counts, no extras, no duplicates) and found no contamination.
- Base44 is a network secret, so no token file was written.
