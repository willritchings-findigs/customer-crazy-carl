# Implementations weekly refresh: why, decisions, incident log

Skill: `.claude/skills/implementations-refresh/`. Dashboard:
https://findigs-growth-hub.base44.app/cx/implementations, record `ImplementationsCache /
implementations_ops` (`6aa833ac3d25aa397d5f6ba7`). Owner: Will Ritchings. Built 2026-11-12 from
Emma's handoff (`The Reserve/O-output/implementations-dashboard/`: `pull_implementations_ops.py`,
the builder prompts, three reports).

## Background

The 10/29 page had two halves. The HubSpot half (stage funnel, triage queue, hygiene) came from the
custom implementation object (`2-230996902`). The other half (ongoing worklist, aging, recently
completed, capacity Gantt and weekly load, Jira board totals, PDE follow-ups) came from the
"Existing Launches" Google Sheet, which was a Jira SE / CX / PDE export. The sheet has had no edits
since October. Will and Maggie agreed on 2026-11-06 that HubSpot is the system of record for
implementation status, and Christian and Alex's team are moving their tracking there. A Monday.com
board mirrors into the same HubSpot object every morning (`monday_*` fields).

## Decisions (2026-11-12, Will)

| Topic | Decision |
|---|---|
| Source | Every section comes from the HubSpot implementation object. Fields HubSpot doesn't have are left blank and counted in the report's gaps; the run never fills them in. |
| Jira sections | Board totals and the PDE follow-up list have no HubSpot source and are sent empty. |
| Stages | Build on today's 12-stage pipeline with the stage list in `config.json`. Alex proposed a new board on 2026-11-03 (Closed-Won/Awaiting Kick-Off, Kick-Off, Implementation In Progress, Launched-Hypercare, Won-Active, FTL); when HubSpot changes, update config by commit. An unknown stage stops the run. |

## Definitions

- **Open** = one of the 8 open stages (Tech scoping … Hyper-care). Test records (zz canary, cv test,
  test N) are excluded, as before.
- **Needs triage** = open with no HubSpot owner. **Active** = open with an owner.
- **Activity** = days in the current stage (`hs_v2_date_entered_current_stage`). Last-modified is
  useless here: the Monday mirror touches most records every morning.
- **Aging** = open and 30+ days in the current stage. **Recently completed** = entered Live or
  Hyper-care in the last 30 days.
- **Go-live** = expected, else desired, else actual go-live date. **Start** = kickoff date, else
  created date. **Overdue** = go-live date in the past while still open.
- **Capacity** = active records spanning each week (4 weeks back to 12 ahead), by owner, plus
  go-lives that week. Priority, commit status, effort and churn risk were sheet columns with no
  HubSpot field; they are blank.

## First dry run (2026-11-12)

All gates passed. 228 records; 112 open, 23 of them test records; 89 real open: 71 need triage,
18 owned. 69 of the 89 have been in their current stage 30+ days, most since 2026-07-10, the day
records were bulk-imported (they haven't moved stage in HubSpot since). Nothing entered Live or
Hyper-care in the last 30 days (Highmark's 10/30 phase launch, for example, isn't reflected).
Gaps: 10 of 18 owned have no go-live date, 16 no kickoff date; 30 open have no segment.

## Display changes needed (Base44 builder prompt, Will runs it)

The page's captions still describe the sheet: "sourced from the tracked ops sheet" on Active
Implementations, the "HubSpot owners vs ops-sheet rows" reconciliation line, and the Jira caption on
Board Totals. Draft: `O-output/cx-implementations/base44_builder_prompt_2026-11-12_hubspot_source.md`.

## Open items

- HubSpot data entry: owners on 71 open records, go-live and kickoff dates, segment.
- Hypercare exit criteria (what moves a record to Live) are not defined yet (Alex).
- Alex's new pipeline stages, when HubSpot changes.
