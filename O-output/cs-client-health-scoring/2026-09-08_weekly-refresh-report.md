# Client Health Weekly Refresh — 2026-09-08 (first scheduled run)

Pushed live 2026-09-08 14:15 UTC (HTTP 200, GET-verified). Window: trailing 90d,
2026-06-10 → 2026-09-08. Baseline for deltas: the 2026-09-04 record.

## Band distribution

| Band | 9/4 | 9/8 | Δ |
|------|-----|-----|---|
| Green | 127 | 132 | +5 |
| Yellow | 79 | 95 | +16 |
| Red | 52 | 31 | **−21** |
| Churned | 7 | 7 | 0 |
| Unscored (None) | 3 | 3 | 0 |

**Why Red shrank by 21 — three drivers, all itemized below:**
1. **Methodology unification (8 accounts, no data change).** This is the first run that rescored
   every account under the one ratified engine. The 8/26 build had left two inconsistencies in
   ~half the portfolio: the PMS row and the later-added Pylon tone rows weren't folded into some
   accounts' pillar values. Those accounts moved without any underlying data changing
   (Garden City, Habitue, KCP, Schambs*, White PM, Yancey, iProperties, Chicago Turnkey*).
2. **SF churn-risk flag updates (23 changes observed in Sigma/Salesforce).** CSMs appear to have
   done a book review — flags moved in both directions (e.g. Legacy Invest, MJW, Modern City,
   Specialized, Team Cadwell, Out Fast downgraded from Red; 3 Options escalated to Red; MGC newly
   set Red). Flag = hard override, so several composites followed.
3. **Sentiment window turnover.** The trailing-90 window now starts 2026-06-10, so spring-crisis
   Slack chatter aged out for several accounts; fresh reads are calmer. (Same discipline applied
   to my own subagents — four classifications were overridden after direct channel verification
   because they cited pre-window events: MGC, Firethorn, McCaw → Neutral/thin-sample; Lease Las
   Vegas → Neutral.)

## New Reds — need CSM attention

- **Sentral (Yellow → Red).** Platform pillar 30/100 + sentiment 0/100. Verified directly in
  Pylon: 43 open tickets in 90d incl. "Unable to Submit Applications – Joinery 2" (9/1),
  "URGENT: Joinery Findigs" (9/4), and two screening-turnaround escalations (9/7). Slack negative.
- **MGC Leasing (Yellow → Red).** SF churn-risk flag newly set **Red** → hard override.
  Note the divergence: in-window Slack is actually mildly positive (new-office walkthrough, "we
  do not need a new contract") — the Red is the CSM's judgment call, presumably from the spring
  ticket crisis. Worth a CSM confirm.
- **FBM Real Estate (Yellow → Red)** — flag Green→Yellow plus metric deterioration.
- **Harbor Property Management (Yellow → Red)**, **RPM Piedmont (Yellow → Red)**,
  **Redwood Parent (Yellow → Red)** — fresh sentiment/Pylon signals (Redwood: 8 open tickets,
  1 friction) plus metric moves.
- **3 Options Realty (Yellow → Red)** — SF flag escalated to Red.

## Contradiction to verify (human)

- **Out Fast PM: Red → Green** purely because the SF flag flipped Red→Green. But an in-window
  Slack claim said they churned to RentEngine (unverified). Composite is now Green 100 (FS,
  flag-anchored). Someone should confirm which is true.
- **Renters Warehouse**: Sigma churn-risk now reads "Churned, Green" (mixed multi-entity read)
  while the account shows live units/activity — band HELD at Green per the parked-rollup
  methodology; flagged for CSM review.

## Evernest (STRAT anchor account)

- Stays **Red** (CSM flag hard override; Sigma churn-risk column went empty — flag preserved
  from HubSpot churn_risk__c rather than blanked).
- A churn guard I added caught a false churn: a name-matched HubSpot child record has
  churned=true, but the rollup has 24,000 live units — churn rules now require zero live units
  AND zero trailing-90 activity on every path.
- Fresh metrics: TTD improved to 41.4h (Green), TES worsened 6.4→8.4% (Red), volume −30%
  (Yellow), 2,279 decisioned groups in window. Sentiment now Negative (AppFolio integration
  issues; churn-risk context). Composite value 63.9.
- Intel: Boom trial expanding to ~50% of portfolio — TN Oct 1, GA Oct 7, VA Oct 14 (~60-day trial).

## Units source switch (per Emma, 9/8)

`total_units_sold_hubspot` now = HubSpot company property **`total_units_all`** ("Total Units
Sold (All)" = cumulative booked units, New Logo + Expansion) on **236 accounts**; JSON keys
unchanged so the dashboard tile binds as before; the deal-count sub-stat is nulled (no longer
deal-derived). 9 accounts carry the prior deal-based value (no HubSpot company matched via
findigs_company_id); ~23 more have no units value from either source. Live units still =
Sigma current-month unit counts; sold-vs-live % recomputed everywhere.

## Verified subagent corrections (window discipline + evidence quality)

- Slack: MGC, Firethorn, McCaw → Neutral + thin_sample (agents had classified from pre-window
  events; verified windows are near-empty); Lease Las Vegas → Neutral (client unresponsive but
  zero escalations; QBR invite out).
- Pylon: Maymont + Sentral kept Negative but with corrected evidence — the agents cited
  implementation threads; the real in-window friction is access/outage/config tickets
  (Maymont: "Urgent: RBAC Access Denied", "FinDigs- Down- BTR", "Promo Codes Not Working",
  API throttling). Counts spot-verified exact against Pylon (31 / 43 / 8).

## Carried forward (staleness notes)

- Meeting/touchpoint cadence + multi-threaded relationship rows (HubSpot-sourced; no HubSpot
  meetings/contacts pull this run — windows self-documented in each row's source).
- Revenue MoM (July vs June label unchanged); quarterly revenue refreshed with Q3 partial
  through 9/7 (unscored context).
- Standard Management's Pylon tone (account not found in Pylon this run).
- Window note: the 9/2 build measured ≥ 2026-07-01; this run is rolling trailing-90 — some
  value moves are window-driven, not behavior-driven. Next week is apples-to-apples.

## Storage (new this week, per Emma)

Week-over-week history now archives to `O-output/cs-client-health-scoring/history/`:
- `wow_history.json` + `wow_history.csv` — cumulative slim snapshot per account per run
  (seeded with 9/4 baseline + 9/8), pivot-ready for trend charts.
- `history/2026-09-08/` — full pushed record, baseline, diff, overrides, and the exact
  scoring script that ran.
Base44-side snapshot records aren't possible with the current record-scoped api_key (entity
list returns 403); if in-dashboard trends are wanted, that's a builder change (new
`AccountHealthSnapshot` entity) — prompt available on request.

## Still with humans

- Volume-trend thresholds: Alex's replacement numbers (current <20/20–40/>40 flagged too generous).
- AM goals due 9/11 (Slack ping needs a channel).
- HubSpot churn-flag cleanup: RPM North Point + Foundation backfill, contradicting statuses.
- Out Fast churn verification; MGC flag-vs-Slack divergence.

## Pipeline packaging

The entire refresh is now the `/client-health-refresh` skill
(`.claude/skills/client-health-refresh/` — SKILL.md + the validated scripts). It encodes the
empirically validated thresholds (incl. the FS approval Yellow-cap, SMB TES cuts, TTD 44/60,
QA 15/20), the count-driven pillar floor rules, the 50/30/20 rollup with CSM hard override,
churn guards, subagent verification protocol, join-coverage gates, and the push/verify/report/
archive procedure. Runbook updated to point at it.
