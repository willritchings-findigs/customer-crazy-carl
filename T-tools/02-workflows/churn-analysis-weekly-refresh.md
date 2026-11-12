# Churn Analysis weekly refresh: why, decisions, incident log

Skill: `.claude/skills/churn-analysis-refresh/`. Dashboard:
https://findigs-growth-hub.base44.app/cx/churn, record `ChurnCache / churn_overview`
(`6ab534b48e57beb0fc0155b4`). Owner: Will Ritchings. Built 2026-11-12 from Emma's handoff
(`The Reserve/O-output/churn-analysis/`: the 10/29 push script, data dictionary, reports).

## Cloud routine

"Churn Analysis Refresh" (`trig_01BBKL3QwcNTXcNoF7b8L1Bp`), Mondays 11:00 ET, Default environment,
connector Slack (HubSpot and Base44 via network secrets). Runs two hours after Client Health so the
At Risk sync uses this week's Red list; if Client Health didn't refresh, the run stops and posts to
`#gtm-automation-log`.

## How the page's data works

The `accounts` list is a vetted population, not a live HubSpot query. HubSpot's `churned` flag has
known false positives (Bluewater, cleared then re-set) and a 2026-07-12 Salesforce sync reset ~104
flags. So the run never rebuilds the list from HubSpot. It keeps the list, syncs At Risk, adds
churns that pass a narrow rule, and recomputes every total from the list. The recompute reproduces
the live 10/30 record exactly (every number; only two caption texts reworded), and each run checks
that again before changing anything.

## Decisions (2026-11-12, Will)

| Topic | Decision |
|---|---|
| New churns | Auto-add a HubSpot company with churned=true and a churn date in the last 30 days, unless it is on the rejected list, its status is Live / Onboarding / Pilot, it has a Closed Won deal after the churn date, its segment is unmapped, or its churn_reason isn't in the taxonomy. Everything else is listed as a candidate. Older ones are added only through `config.new_churns.approved_additions`, by commit. Nothing is ever removed automatically. |
| At Risk | Synced automatically to the Client Health Red list each week. HubSpot ID from Client Health's match file (fallback: one exact company-name match). ACV = sum of Closed Won New Logo + Upsell deals. No match, no Closed Won deal, or more than 2 deals: pushed at $0 and flagged; an approved ACV goes in `config.at_risk_acv_overrides`. |
| FTL staleness rule | Propose-only. Failure-to-Launch companies not on the page are listed; none convert automatically. |
| Schedule | Mondays 11:00 ET, after Client Health (9:00). Stops if Client Health is more than 2 days old. |
| Slack | Success to `#p-account-health`; any stop to `#gtm-automation-log`. |

Earlier decisions still in force (from Emma's handoff): FTL accounts stay in `accounts` with
`is_ftl=true`, excluded from the four true-churn KPIs and shown live on the page from `is_ftl`
(2026-10-29, Alex's proposal, Will's sign-off); `reason_source_coverage` keeps its 4-key schema
with `sigma_reason_at_risk` counted under `none`; no new stored fields (Base44 drops them).

## First dry run (run date 2026-11-10, against the 11/09 Client Health)

All gates passed. At Risk 22 -> 21 ($5.30M -> $4.92M): MJW Investments Parent and Sentral left
Red, Firethorn Realty joined ($9,630, one Closed Won deal). No new churns: 451 companies are
churned=true in HubSpot, 69 aren't on the page, and none has a churn date in the last 30 days.
22 churned accounts on the page show a Live/Onboarding/Pilot status in HubSpot (reported, not
changed). A name-only join wrongly swapped MGC Leasing (page name vs Client Health name differ);
the join now uses the HubSpot ID first.

## Open items

- The 69 older churned=true companies need a human pass before any are approved.
- The 22 churned-but-Live accounts need the deal-level evidence standard from the 9/24 review.
- The sub-reason ACV overlap display note (Emma's 10/5 builder prompt) is still not pasted.
