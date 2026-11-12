# HubSpot implementation board: change to Alex's stages

Status: **blocked on the Monday bridge** (2026-11-12): HubSpot is to own the stage, and the bridge that mirrors Monday into HubSpot has to stop writing stages first. Object: Implementations (`2-230996902`), pipeline
`2346115798`. Proposal: Alex Schaper, 2026-11-03. Decisions: Will, 2026-11-12.

## Target board

| # | New stage | Built from | Records moved in |
|---|---|---|---|
| 1 | Closed-Won / Awaiting Kick-Off | rename **Awaiting Kickoff** (`3823191786`) | Tech scoping (`3920961246`): 66 (52 real, 14 test) |
| 2 | Kick-Off | **new stage** | — |
| 3 | Implementation In Progress | rename **Credentialing & Configuration** (`3965879023`) | Testing (`3965666037`): 2, Training (`3965183698`): 1, Ready to Launch (`3965927159`): 0 |
| 4 | Launched / Hypercare | rename **Hyper-care** (`3965183699`) | Pilot Launched (`3966156487`): 0 |
| 5 | Won / Active | rename **Live** (`3823191787`) | — |
| 6 | FTL | rename **Failure to Launch** (`3823159004`) | — |
| 7 | Churned | keep (`3965747922`) | — |
| 8 | Stalled - Back to Sales | keep (`3966156488`) | — |

Retired after they are empty: Tech scoping, Testing, Training, Ready to Launch, Pilot Launched.

**Pilot vs non-pilot** is a field, not a stage: the existing `sales_process` property (direct /
pilot / opt_out; set on 42 of 228 records today).

**Why rename instead of a new pipeline:** these workflows point at stage IDs, and renaming keeps the
IDs, so they keep working without edits:

| Workflow | Stage it uses | After the change |
|---|---|---|
| Implementation outcome (W3) `4392592064` | Live, Failure to Launch | fires on Won / Active, FTL |
| Implementation Success loop (W7) `4512093939` | Live | fires on Won / Active |
| Go Live Push to Slack `4918708924` | Live | fires on Won / Active (= exit from Hypercare, the 11/6 go-live definition) |
| Impl: Scoping done → Handoff (Slack #2) `4523138787` | Awaiting Kickoff | fires on Closed-Won / Awaiting Kick-Off. None of the 66 moved records has all five scoping fields, so the move sends no alerts. |
| Impl: Handoff gate detect-and-revert `4522924736` | Awaiting Kickoff → sets Tech scoping | **turn off first**: it would bounce moved records back into Tech scoping, and Tech scoping is being retired (scoping moves into the sales handoff) |

## Steps

| # | Who | Step |
|---|---|---|
| 0 | Claude | Snapshot every record's stage and stage history, and the current workflow list, into the repo (rollback record). |
| 1 | Will (HubSpot › Automation) | Turn off *Impl: Handoff gate detect-and-revert*. |
| 2 | Will or Claude | Rename the five stages, add *Kick-Off* after stage 1, put the order as in the table. (Claude can do it through the pipelines API only if the HubSpot key has the pipeline-write scope; otherwise Settings › Objects › Implementations › Pipelines.) |
| 3 | Claude (HubSpot connector) | Move the 69 records out of Tech scoping, Testing and Training; read every one back. |
| 4 | — | **Monday.com mirror check** (see below) before anything is deleted. |
| 5 | Will | Delete the five empty stages. |
| 6 | Claude | Update `implementations-refresh/config.json` (stage names and order), re-run the refresh, update the runbook and docs. |
| 7 | Will | Tell the implementation team; Alex trains on the new stages. |

Rollback before step 5: rename stages back and move records back from the step 0 snapshot. After
step 5 the old stage IDs are gone; records can still be moved, but workflows that referenced a
deleted stage would need re-pointing (none do, per the table).

## Side effects to expect

- Moved records get a new "entered current stage" date, so the Implementations dashboard's
  "days in stage" and Aging count reset for those 69 records on the next refresh.
- The dashboard's stage funnel shows the new names after step 6; the refresh stops on any stage it
  doesn't know until then, so do step 6 the same day as step 2.

## Blocker: the Monday.com mirror drives stages (found 2026-11-12)

The team still works in Monday (Will, 2026-11-12). A Monday.com integration (HubSpot app
`37243702`) writes into these records every morning, and it **writes the stage**, overriding
changes made in HubSpot. Stage changes since 2026-08-15 by source: 46 automation (new records
created in Tech scoping), 24 Monday integration, 14 HubSpot UI, 2 HubSpot mobile. This week:

| Record | Changed in HubSpot | Then the Monday mirror set |
|---|---|---|
| Weiss Entities (new) | Churned, 11/3 (UI) | Credentialing & Configuration, 11/4 |
| Exit Realty-Realty Place | Live, 11/9 (UI) | Credentialing & Configuration, 11/10 |
| Group Fox Management - Pilot | Live, 11/9 (mobile) | Training, 11/10 |

The mirror also writes owner, project health, units and company name. Its code and its
Monday-status → HubSpot-stage mapping aren't in any repo.

What this means for the board change:
- Renaming stages is safe for the mirror only if it writes stage **IDs** (renames keep IDs).
- Moving records out of Tech scoping / Testing / Training won't stick: the mirror moves them back to
  whatever their Monday status maps to.
- Deleting a stage the mirror still maps to will make its writes fail or land on the wrong stage.
- So the Monday board's status column and the mirror's mapping have to change in the same step as
  the HubSpot pipeline, or stage-writing has to be turned off in the mirror.

**How it was designed (Notion, "🛠️ Implementation", 2026-08-07):** a "bridge" automation connects
HubSpot and Monday. When an AE moves a record to Awaiting Kickoff, the bridge builds the Monday
Handoff Hub item (board `8556863573`), a pipeline item on the Implementation Pipeline board
(`8553153795`), the customer task board and the scoping doc, and announces in `#t-onboarding`. The
implementation team's Gate (Approved / Declined) on the Hub item sends declined records back to Tech
scoping. **"Your board is the source of truth; HubSpot mirrors it ... Stage changes on the pipeline
board mirror to HubSpot nightly ... Nobody edits the mirror on the HubSpot side."** The page names
the automation's owner only as whoever watches `#t-onboarding`; Asaf announced the sync on 2026-07-12
and the Gate escalation goes to Mary and Asaf.

**Decision (Will, 2026-11-12): HubSpot owns the implementation stage.** That reverses the August
design, so the bridge has to change before the board does: stop it writing `hs_pipeline_stage`
(keep the other fields and the handoff build), and decide where the Gate's decline lands now that
Tech scoping is retired. The bridge's owner has to make that change.

It is also a live data problem today, independent of the board change: implementation status set in
HubSpot is being reverted daily, against the 2026-11-06 agreement that HubSpot is the system of
record. Weiss Entities' churn, for example, is no longer shown in its implementation record.
