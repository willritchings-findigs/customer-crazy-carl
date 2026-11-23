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

## Incident and decisions (2026-11-23)

**What broke.** The Monday run stopped at step 1: Client Health was 7 days old (its own run failed at
pre-flight when the Sigma and Pylon connectors didn't attach), and the churn run hard-stopped on that.
Separately, a second writer had appeared. A Base44 workflow in the Findigs Hub app, **"Daily Churn
Cache Refresh"** (id `6b00a2b2875125e5d4e78261`, function `refreshChurnCache`, created 2026-11-20,
daily 06:00 ET, three runs by 11/23), rebuilt `ChurnCache.accounts` from HubSpot each morning. Its
comment says it "replaces the old external cache writer". On 11/23 at 11:03 UTC it wrote 458 rows
(256 Churned, 180 Failure to Launch, 22 At Risk) and left the stored KPIs and breakdowns alone. It
dropped 16 vetted churned accounts ($935K) whose HubSpot status is Live, and it re-added Bluewater
(the confirmed false positive). It name-matched At Risk, so 10 of 22 At Risk rows had no ACV
($4.92M fell to $1.08M), and it read ACV from `acv__c`, a frozen Salesforce snapshot. The app was
created by Asaf Raz, who was deactivated on 11/23. The same build added `churn_date` and
`account_status` to the stored row schema, and Base44 now returns null for a row that omits them.

**Decisions (Will, 2026-11-23).**

| Topic | Decision |
|---|---|
| Who writes ChurnCache | This skill only, with the vetted list and its rules. The Base44 workflow is to be set **inactive** (Findigs Hub, Workflows tab, "Daily Churn Cache Refresh", toggle off). Claude was not permitted to change it through the API. |
| Foreign writes | `guard.py` (step 0.4) compares the live accounts with the newest archived readback. If they differ, it saves the live copy as `foreign_<MMDD>.json`, rebuilds from the vetted record, restores it at the push, and alerts `#gtm-automation-log`. Each run also reports whether the workflow is still active. |
| FTL source | HubSpot **Account Status** decides, now that it is populated (180 companies are Failure to Launch, 247 are Churned). A churned row with status Failure to Launch is FTL and is stored with status `Failure to Launch` (the label the page has read since 11/20). A row with status Churned is true churn. Any other status leaves the row as it is and is reported. More than `validation.max_ftl_flips` (10) moves in one run are held and flagged. On 11/23 nothing moved: all 114 page FTL rows already had the FTL status. The 66 FTL-status companies not on the page stay propose-only. |
| Stale Client Health | No longer a stop. At Risk is carried over unchanged and flagged, and the rest of the refresh runs. |
| New-churn pool | churned=true **or** Account Status Churned (the checkbox may be retired). Reason = Churn Category, else churn_reason, mapped through `taxonomy.reason_aliases` (the one-to-one renames from `churn_category_migration_plan.md`), so the planned picklist migration doesn't block adds. |
| Stored row fields | Every row now carries `churn_date` (= effective churn date for churned rows) and `account_status` (HubSpot), so the page works whether it reads the old fields or the new ones. |

**Restore run (2026-11-23, run by hand from Will's machine).** The guard caught the foreign write and
rebuilt from the 11/18 readback. Two churns passed the existing rule: Harbor Group Management (converted
from At Risk; HubSpot status Churned and category Tech Stack Consolidation, $1,282,842.20, churned 11/05;
this is the account from Alex's 11/17 question) and McCaw Property Management ($79,868.40, churned 11/16).
At Risk was carried over (Client Health stale). True churn 264 to 266, $10.36M to $11.72M ($5.62M YTD);
At Risk 22 to 21, $3.63M. The first PUT's readback failed on the two new schema fields (null vs
missing) and nothing else; the build now fills them, and the second PUT read back with PASS. A simulated
11/30 run against the restored record passed every gate with no changes.

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

- **Set the Base44 "Daily Churn Cache Refresh" workflow inactive** (a Findigs Hub admin, Workflows tab). Until then it overwrites the page every morning at 06:00 ET, and the Monday run restores it and alerts.
- Client Health routine: list Sigma and Pylon explicitly in its connectors so it stops failing at pre-flight; At Risk only syncs once it runs again.
- Harbor Group: find the HubSpot workflow that resets Account Status from Churned to Prospect (enrollments 1800424495809 and 1800424481497).
- Client Health keeps scoring HubSpot-churned accounts (Weiss Parent and Evernest are Red with `hs_churned_any=true`); decide whether it should drop them.
- Base44 page: the Churn by Segment (YTD) drill-down should filter to Churned with a churn date in the year.
- The 66 Failure-to-Launch-status companies not on the page (propose-only) and the older churned=true candidates need a human pass before any are approved.
- The 22 churned-but-Live/Onboarding/Pilot accounts (the in-app writer dropped the 16 Live ones) still need the deal-level evidence standard from the 9/24 review.
- The sub-reason ACV overlap display note (Emma's 10/5 builder prompt) is still not pasted.
