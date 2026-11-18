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

## Decisions (2026-11-18, Will)

Prompted by Alex Schaper's 11/17 question: Harbor Group had been marked churned in HubSpot but the
page still showed it At Risk.

| Topic | Decision |
|---|---|
| Churned or not | HubSpot's `churned` checkbox decides. An At Risk account whose checkbox is true is treated like any other churned=true company: it converts to Churned (replacing its At Risk row) when it passes the auto-add rule or is in `approved_additions`; otherwise it is listed as a candidate marked "on the page as At Risk". Before this the sync skipped every HubSpot ID already on the page, so an At Risk account that churned was never surfaced. |
| Churn date | HubSpot's `churn_date` (Company information group, written by the CRM UI and workflows since 2026-07). `churn_date__c` is the 2025 Salesforce import, read only when `churn_date` is blank; the code used to prefer it. Order in `config.hubspot.churn_date_fields`. Every run re-syncs each churned account's `effective_churn_date` to it and lists changes in the report. First run changed one account (Chroma Property Management, 2026-07-31 -> 2026-10-27, the date a person set in HubSpot on 10/27). |
| Failure to Launch | Will asked for Account Status = "Failure to Launch". On 2026-11-18 no company carries that status (the option exists; automations overwrite statuses with Prospect/Disqualified), the `failure_to_launch` checkbox is on 108 companies (101 churned; 95 of the page's 114 FTL accounts), and the page's `is_ftl` comes from a blank go-live date. Switching to the status as-is would empty the FTL card and move 114 accounts ($4.28M) into the true-churn headline. **Not changed; pending Will's call** between the status (once populated), the checkbox, and the go-live rule. |

What the 11/18 check found about Harbor Group (HubSpot 335497258711): `churned` set 2026-11-05 by a
workflow, `churn_date` 2026-11-05, `churn_reason` "moved to Yardi" (not in the taxonomy; the
matching value is Tech Stack Consolidation), Account Status reverted from Churned to Prospect by a
HubSpot workflow within seconds each time Alex set it (enrollments 1800424495809 and
1800424481497). Client Health still scores it Red (HubSpot health override). Two other At Risk
accounts are churned=true: Weiss Entities (2026-11-04, status Onboarding, free-text reason) and
Evernest (2025-09-29, status Live). All three are now candidates in the report. Also from Alex: the
page's "view in table" on Churn by Segment (YTD) lists At Risk accounts because the Base44 page
filters the drill-down by segment only; the stored table is right (STRAT 0 / $0). That is a page
fix in the builder, not a data fix.

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

## First live cloud run (one-off test, run date 2026-11-10, fired 2026-11-12)

Ran end to end in 2m13s with no stops and no fixes: credentials from network secrets, both Base44
GETs, the HubSpot sync, all five gates, PUT 200, readback PASS, report and history committed
(8ea80c8), success posted to `#p-account-health`. At Risk 22 -> 21 ($5.30M -> $4.92M), churn
unchanged. Checked afterwards: the live record equals the run's build and the local dry run field
for field, and recomputing from the live accounts reproduces every total. The archive also held a
3.5 MB copy of the Client Health record; later runs no longer copy it.

## Open items

- FTL source: Account Status (empty today), the `failure_to_launch` checkbox, or the go-live rule. Will to decide; see 2026-11-18.
- Harbor Group: fix `churn_reason` in HubSpot to a taxonomy value (or approve by ID) so it converts; find the HubSpot workflow that resets Account Status.
- Client Health keeps scoring HubSpot-churned accounts (Harbor Group Parent, Weiss Parent, Evernest are Red with `hs_churned_any=true`); decide whether it should drop them.
- Base44 page: the Churn by Segment (YTD) drill-down should filter to Churned with a churn date in the year.
- The 69 older churned=true companies need a human pass before any are approved.
- The 22 churned-but-Live accounts need the deal-level evidence standard from the 9/24 review.
- The sub-reason ACV overlap display note (Emma's 10/5 builder prompt) is still not pasted.
