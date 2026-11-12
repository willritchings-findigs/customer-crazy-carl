# Base44 builder prompt: Implementations page now sourced from HubSpot (2026-11-12)

Paste into the Base44 builder for the Findigs Growth Hub app. Display-only changes: no schema
change, no new fields. Run it before or right after the first HubSpot-sourced push.

```
Update the Implementations page (cache_key "implementations_ops" on ImplementationsCache). Text and
empty-state changes only. Do not change the data schema, the page structure, sorting, filters, or
styling beyond what is listed here.

1. Header stat "Active Implementations": change any helper text that says it is sourced from the
   ops sheet to: "Open implementations with an owner in HubSpot."

2. Header stat "Aging / Stalled": helper text "Open implementations that haven't changed stage in
   30+ days."

3. Data Hygiene footnote: remove the reconciliation line that compares HubSpot owners with
   ops-sheet rows. Replace it with: "Source: HubSpot implementation object. Blank cells are fields
   not yet filled in HubSpot."

4. Board Totals: if board_totals is empty, hide the whole section (heading and caption included).

5. Follow-up: if follow_up is empty, hide the whole section.

6. Ongoing Worklist: rename the "Last Updated" column to "In stage since" and "Days Since Activity"
   to "Days in stage". Rename the "Notes" column to "Health". Keep showing "—" for empty cells.

7. Aging Worklist and Recently Completed: same two column renames as in 6. If recently_completed is
   empty, show "Nothing reached Live or Hyper-care in the last 30 days."

8. Capacity Gantt: keep as is. In the tooltip, omit any line whose value is empty (commit status,
   priority, churn risk are not tracked in HubSpot). Color bars by risk_flag only when
   commit_status is empty.

9. In the weekly capacity chart, skip any series whose values are all empty (active_priority_a,
   active_committed, weighted_effort_load); keep active_total, go_lives_count and the by-owner list.

No editing controls anywhere on this page.
```
