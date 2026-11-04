# Weekly Data Refresh — 2026-09-28

All 4 Base44 dashboards refreshed: client health, churn analysis, implementations, support metrics. Client health window 2026-06-30 → 2026-09-28 (prior 2026-04-01 → 2026-06-30).

## 1. Client health

**Pushed live 14:27 UTC** (overview PUT + GET verified; history archived — 5th consecutive clean weekly run: 9/4, 9/8, 9/14, 9/21, 9/28).

| Band | 9/21 | 9/28 | Δ |
|------|------|------|---|
| Green | 130 | 130 | — |
| Yellow | 108 | 106 | −2 |
| Red | 20 | 22 | +2 |
| Churned | 8 | 8 | — |
| Unscored | 1 | 1 | — (PF Holdings, parked rollup) |

267 accounts. **2 flips, both data-driven, both Yellow → Red:**

- **Cooper Zadeh Property Management, LLC** — Platform Red (50.8): time-to-decision/QA/ticket-ratio red. Strategic Red (50.0): exec-sponsor alignment and meeting cadence red. Sentiment Yellow (71.4).
- **Group Fox Management** — Platform Red (36.8): time-to-decision/QA/ticket-ratio/technical-escalations red. Sentiment Red (0.0): Slack and Pylon both negative (3 verified frictions incl. "Linero Applications 2180-308", "Incorrect Credit Criteria"). Strategic still Green (90.0).

Freshness: platform metrics 249 touched, sentiment (Slack+Gong) 142, Pylon 120, review cadence/exec sponsor 25 each, units switched 228 / carried 15.

### Catches this run

- **A 4th Sigma rollup rename**, previously unseen: "Payton's Place Real Estate, LLC" — fresh Sigma pull used a curly apostrophe (') where the record's stored name uses a straight one ('). Same failure mode as the Beztak/Kairos/Hudson renames from 9/21 (silent join miss, metrics carry forward stale). Caught by the mandatory post-pull name diff, translated across all 6 q-files — 267/267 join coverage.
- **Pylon verification found a systematic undercount pattern**, not just isolated misses: of the 12 Negative-classified accounts, 6 were exactly right, 1 had a wrong-but-immaterial title cited, and **6 were undercounted** — most severely Beztak Properties Parent (5→12 real frictions; the original scan verified only its own 5 cited titles and never swept the other ~155 tickets on the account) and McKinley Companies LLC (6→14; the agent had admitted only 1 of 6 titles was actually checked). No classification changed (all stayed Negative), but the undercounts would have understated friction severity in the pushed `red_reasons` text if not caught. Worth noting for future runs: single-digit-title verification isn't catching everything on high-volume Pylon accounts.
- **Rediscovered a documented HubSpot gotcha** while resolving Cooper Zadeh's ACV for the churn side: the "New logo" pipeline (`2313721535`) uses custom numeric `dealstage` IDs, not the literal strings `closedwon`/`closedlost`. A naive string filter would have silently reported $0 for a genuinely-won $104,677.65 deal. Fixed by matching on the Pipelines API's `isClosed`/`probability` metadata instead.

## 2. Churn analysis

**Pushed live 14:49 UTC**, GET-verified. 379 churned ($14,789,452.39 total ACV) + 22 at-risk ($5,390,349.05 best-effort ACV) = $20,179,801.44 total ACV tracked.

**3 genuinely new churns** (of 447 raw HubSpot `churned=true` candidates — the other 444 were either pre-existing or non-customer shell records without a `findigs_company_id`, or already-known corrected false-positives like Evernest/West USA Realty/Bluewater that stay excluded): First Pacific Group, New Land Enterprises, Sureway. All 3 resolve to $0 ACV (old/small accounts, no HubSpot deal value on record).

**2 new at-risk (Red), matching the client-health flips exactly:**
- Cooper Zadeh Property Management, LLC — $104,677.65 confirmed closed-won ACV (deal "CooperZadeh PM DecisionAssist"). Owner: Reese Ryan.
- Group Fox Management — $0.00 confirmed. Its only substantial deal ("Group Fox Management - New Logo with Pilot Period," $51,448.75) is still open in Trial stage, not closed-won; its other two deals are both Closed Lost. This is a resolved $0, not an unresolved one — the account has real, active usage ($5,800 in Sigma revenue this quarter) but no captured won deal in HubSpot. No AM assigned in the ownership sheet.

**2 bugs caught and fixed before this report** (both now corrected in the live record):
1. **3 duplicate rows.** MBC Group, Desert Canyon Properties (Aloe PM), and First Communities/Asset Living — all legitimate pre-existing FTL-staleness churns with real historical ACV — had each picked up a second, bugged copy (reason forced to "Uncategorized", ACV zeroed) during this week's new-candidate scan, which evidently didn't check for already-churned accounts before appending. Caught via a name-uniqueness check I ran before finalizing; removed the 3 bugged copies, kept the originals untouched.
2. **`reason_source_coverage` was already stale before this week.** Recomputing it fresh from the actual per-account data surfaced 11 rows using `sigma_reason_at_risk` as their source — a real, pre-existing category that the baseline's coverage tile had been silently omitting (its 4-key total happened to still sum to the account count by coincidence, masking the gap). Base44 also turns out to only accept 4 literal keys on this field and silently drops anything else on write, so I folded those 11 into `hubspot_field` (closest semantic match: both are directly-sourced reason signals, vs. "sheet" or "none"). Flagging this bucketing choice in case you'd rather it land differently — it's a judgment call, not a schema constraint I could route around.

## 3. Implementations

**Pushed and verified**, rebuilt from a fresh download of Corinne/Brian's live Google Sheet (7 tabs). Board totals: **Solutions Engineering** 74 tickets (29 ongoing, 45 aging), **CX Operations** 20 (19 ongoing, 1 aging), **Product Engineering** 1 (aging). Stage funnel: Tech scoping 48, Awaiting Kickoff 19, Credentialing & Configuration 8, Hyper-care 5, Testing 2, Training 1, none currently in Ready-to-Launch or Pilot-Launched.

## 4. Support metrics

**Pushed and verified.** Full Sigma census, 12-week trend extended.

- Ticket volume: 4,309 (d7) / 18,131 (d30) — PM 1,474/5,687, Applicant 2,333/10,356, unset 496/2,053.
- Median TTFR: 3.0 min overall (Applicant 2.0 min, PM 6.0 min) — down from 3.5 min last week.
- FCR (≤2 touches, sampled): 16.9% (d7, n=65) / 15.8% (d30, n=114).
- Latest trend week (9/20): SLA 85.1%, PM CSAT 4.52, Applicant CSAT 3.24, 29.7 tickets/100 apps.

## Slack alerts — awaiting your go

Built from the 9/21 → 9/28 transition (all 3 dashboards' independent findings agree on exactly these 2 accounts). Ledger: `history/2026-09-28/alerts_2026-09-28.json`, everything `posted: false`. Per the standing review-first policy, nothing goes to #p-account-health until you say go.

> :stethoscope: **Client health weekly refresh 2026-09-28** — 2 alert(s): 2 newly Red, 0 worsened to Yellow

**🔴 Cooper Zadeh Property Management, LLC — moved Yellow → Red**
Drivers: Strategic Alignment red · Platform & Product red · Client Sentiment yellow
Signals: Executive sponsor alignment, Meeting/touchpoint cadence red / Performance review cadence yellow · time-to-decision, QA rate, support-ticket ratio red
Owner: @Reese Ryan · HubSpot ↗ · Dashboard ↗

**🔴 Group Fox Management — moved Yellow → Red**
Drivers: Client Sentiment red · Platform & Product red
Signals: Slack/Gong negative, Pylon negative · time-to-decision, QA rate, support-ticket ratio, technical escalations red · 3 Pylon friction issues ("Linero Applications 2180-308", "Incorrect Credit Criteria")
Owner: _unresolved — not in the ownership sheet_ · (no HubSpot record matched) · Dashboard ↗

Plus a grouped "still Red" digest for the 20 unchanged accounts (no individual re-pings).

## Addendum: live unit counts were wrong for 44 accounts, now fixed

You asked me to check Beztak's live unit count against the dashboard figure (1,361) — it was badly wrong. Sigma's true current-month figure is 21,539, not 1,361. Root cause: this week's Companies BI pull, for any multi-portfolio rollup, captured only one child portfolio's unit count instead of summing all of them under the rollup name. Small accounts (1-2 portfolios) didn't show it; large ones did, badly.

I audited all 267 accounts directly against fresh Sigma (`GROUP BY ROLLUP_COMPANY_NAME, SUM` on Companies BI) rather than trust the pipeline's own output, and found **44 accounts wrong**, not just Beztak:

| Account | Was | Now |
|---|---|---|
| Beztak Properties Parent | 1,361 | 21,539 |
| Highmark Residential Parent | 844 | 20,885 |
| Maymont Homes | 2,204 | 19,024 |
| Oakwood Parent | 550 | 13,079 |
| Harbor Group Parent | 816 | 12,157 |
| Winfield Property Management, LLC | 4,253 | 8,506 |
| Lynco Properties | 540 | 7,924 |
| ...and 32 more | — | all undercounted the same way |

Plus a separate, smaller issue: 5 single-portfolio accounts (33 Realty Management, Ebner Properties, Foundation Property Management LLC, Keyway Property Management, Sound City Realty LLC) were carrying a stale value from a 2026-09-02/09-04 note that no weekly run since had ever refreshed. Fresh Sigma shows near-zero current activity for all 5 — worth checking whether they're still active clients rather than just a units-panel bug.

All 44 are fixed and re-pushed; `sold_vs_live_units_pct` recomputed for each; re-audited the full 267 against Sigma afterward and confirmed zero remaining mismatches. This is unscored/contextual data (doesn't touch composite bands or the alert that already posted), but it was materially wrong on a live dashboard — glad you caught it. I've noted in the skill memory to spot-check the largest accounts' unit sums against a raw Sigma query before merging in future runs, since this kind of single-child substitution doesn't trip any of the existing validation gates.

## Still with humans

- **Group Fox Management ownership** — no AM on file anywhere (not in the CS Health Score sheet, not in HubSpot `account_manager`). Worth assigning before this becomes a recurring blind spot.
- **`reason_source_coverage` bucketing** (churn analysis, above) — my call to fold `sigma_reason_at_risk` into `hubspot_field` was pragmatic, not authoritative. Say if you want it split differently.
- **PF Holdings**: still the one unscored client-health account (parked multi-entity rollup).
