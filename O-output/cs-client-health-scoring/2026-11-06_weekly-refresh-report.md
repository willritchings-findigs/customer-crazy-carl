# Client Health weekly refresh: 2026-11-06

Run date 2026-11-06 (UTC), window 2026-08-08 to 2026-11-06 (90 days). Unattended cloud routine.
Pushed to Base44 `AccountHealthCache` (record `6a834cf871d5a0ff1897bfca`), `computed_at` 2026-11-06T17:48:09Z.
Previous run: 2026-10-28.

## Checks

- Contract check passed: 267 accounts, all Sigma columns, 14 HubSpot properties, credentials.
- All 8 Sigma results (q1 to q7, gate 6) were saved from the tool output and proven against Sigma with `sigma_verify.py`: PASS on every query. q6 auto-saved to a file.
- Validation gates: (1) threshold reproduction, (2) pilot-account unit test, (3) join coverage (q1 253/267, q2 265, q3 233, q7 262) all passed. (4) No band moved more than 25: the largest move was Green +1. (5) No all-zero metric columns. (6) Live units equal the Unit Counts BI cross-check on all 250 accounts present in it.
- Push verified by a fresh GET: `computed_at`, band counts and the full account list match what was sent. The snapshot `health_snapshot_2026-11-06` was posted and the enriched overview re-PUT as the newest record; a LIST confirmed both.

## Band distribution

| Band | 2026-10-28 | 2026-11-06 | Change |
|---|---|---|---|
| Green | 129 | 130 | +1 |
| Yellow | 106 | 105 | -1 |
| Red | 22 | 22 | 0 |
| Churned | 9 | 9 | 0 |
| Unscored | 1 | 1 | 0 |

## Band flips (3, all data-driven; no methodology change)

- Firethorn Realty: Yellow to Red. Platform Red (56.3), Strategic Red (33.3), Sentiment Yellow (71.4).
- MJW Investments Parent: Red to Yellow. Platform Red (57.0), Strategic Yellow (50.0), Sentiment Yellow (21.4). **Needs a human look**: its Slack channel (`#p-mjw-investments`) shows the client lead threatening on 2026-10-07 to turn Findigs off and on 2026-10-19 asking to disconnect and waive the termination fee. Slack came back Negative, but the pillar rules (no Red row in the sentiment pillar) cap the band at Yellow. The score is not hiding it, but the band is.
- Realty Solutions LLC: Yellow to Green. Platform Green (82.5), Strategic Green (83.3), Sentiment Green (100).

## CSM flag changes and contradictions

None. No new Sigma churn flags.

## Sentiment: verified overrides and client intel

Slack (134 channels read, 1 not found: `#p-propertysourced`), Gong (29 accounts with in-window call briefs), Pylon (257 accounts scanned, 7 not found).
No Slack/Gong overrides were needed. The Slack scan returned 14 Negatives; I re-read three channels against the raw messages (Rent Appeal, Modern City, McCaw) and all matched.
Pylon: all 18 Negatives were independently re-pulled and re-adjudicated by separate verifiers. All 18 stayed Negative. Corrections applied in `pylon_overrides.json` (titles and counts): Maymont (3 to 4), RPM Southland, Group Fox (4 to 3), Imagine Homes, Winfield (8 to 7), Jones and Jones (3 to 5), ResiHome (one title swapped; 3). ResiHome and Point Real Estate sit exactly at the 3-ticket threshold.

Client intel worth an AM's attention (from Slack/Gong, not score-affecting beyond the above):
- GC Realty & Development: Gong call 2026-11-05, client confirmed termination of the service agreement (60-day notice, cost, integrations, UI).
- Kairos Living: Gong shows a loss of trust in automation through early October, constructive since late October.
- Slack Negatives (relayed by Findigs staff): Standard Management (reconciliation issues, churn risk), Real Property Management Advantage (asked to cancel 2026-10-05), Weiss Parent (does not want to continue), McCaw (sent a churn email 2026-10-20, moved to Boom), Evernest (expanding Boom trial, moving TN/GA/VA off Findigs in October), Bryten and Legacy Invest (pause or expected churn), Harbor Group Parent (churning, marked churned in HubSpot 2026-11-05), Sentral (fee dispute), Modern City, Brick and Timber, Rent Appeal.
- Bridge Homes: SFR portfolio deactivated 2026-09-18 after an acquisition (Prospect with zero live units; scored Churned already).

## Staleness and carry-forward notes

157 notes in `wow_diff_1106.json`. The main ones:
- 16 accounts have no HubSpot match this run, so sold-vs-live units carried forward (for example Willowdale, HomeRiver, Above, Amerihome, Standard Management).
- Many accounts had no in-window Slack channel messages and no Gong calls, so `client_communication_sentiment` was cleared (unscored), not carried forward.
- 10 Slack channels had no in-window client messages at all; their Neutral/thin_sample calls are defaults, not evidence. Most `#p-*` channels are Findigs-internal, so the Slack component is relayed sentiment.
- Pylon applicant counts came back 0 everywhere (no `user_type == applicant` on any in-window open issue); these are likely a field-coverage effect, not proof that applicants never filed.

## Standing holds

Unchanged from the workflow doc: Evernest, RPM Agile, RPM Three Bridges, West USA Realty, PF Holdings (parked), Morgan (future churn date 2026-12-31, scored Churned already), RPM umbrella row removed.
HubSpot churn-pool hits on non-churned baseline accounts (audit): Harbor Group Parent (churn date 2026-11-05, but 1,453 submissions in window so not auto-churned), RPM Rental Solutions, Renters Warehouse, West USA Realty, Evernest.

## Method notes

- Rollup rename added to `config.json`: `Payton’s Place Real Estate, LLC` (curly apostrophe in Sigma) to `Payton's Place Real Estate, LLC`. Saved Sigma files were renamed after verification (originals kept as `.orig` in scratch).
- `gong_strategic_rows.json` was built with a scratch script (domain match on `hs_account_match.json`); 29 accounts.
- Sentiment scans ran as read-only sub-tasks without Base44 or HubSpot inputs; sub-tasks can't be stripped of the environment's network secrets, so the live Base44 record was re-read before and after the push. It was unchanged before the push (`computed_at` 2026-10-28T21:13:47Z).
- A failure DM was sent earlier today by an earlier run that stopped because Sigma results arrived inline; this run saved them inline and proved each against Sigma.
