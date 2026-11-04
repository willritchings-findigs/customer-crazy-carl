# Base44 builder prompt — Churn Analysis: segment×product YTD view + click-to-drilldown (2026-09-29)

Paste this into the Findigs Hub AI builder, on the Churn Analysis page. This asks for three
schema additions plus their display. The underlying data for all three is already computed
and ready to push via API the moment the schema exists — right now it silently gets dropped
on write because these fields aren't in the ChurnCache schema yet.

**Important: only change what's described below. Don't touch the sidebar navigation, any
other page, or anything on this page not explicitly mentioned here.**

---

## 1. New section: "Churn by Segment (YTD)"

Add a new field to the `ChurnCache` entity schema: `churn_by_segment_ytd`, an array of
objects, one per segment, shape:
```
{ segment: string, count_total: number, acv_total: number,
  count_da_fs: number, acv_da_fs: number,
  count_da: number, acv_da: number,
  count_fs: number, acv_fs: number,
  count_unclassified: number, acv_unclassified: number }
```

Add a new section on the Churn Analysis page, below the existing "Churn by Product" section,
titled **"Churn by Segment (YTD)"**. Show one row per segment (same 4 segments as the
existing segment filter buttons: STRAT, MM + ENT, SMB, SMB (<250)), with count and ACV. Add a
3-way toggle above the table — **DA & FS** / **DA** / **FS** — that switches which
count/acv pair each row displays (`count_da_fs`/`acv_da_fs`, `count_da`/`acv_da`, or
`count_fs`/`acv_fs`). This is a fixed YTD view, not tied to the page's existing "All
Time/YTD/Last 12 Months/..." filter buttons.

## 2. Click-to-drilldown on "Churn by Reason"

Add a new field to each item in the existing `churn_by_reason` array, and to each item in
its nested `sub_reasons` array: `accounts`, an array of objects, shape:
```
{ name: string, acv: number, churn_date: string, hubspot_url: string }
```

On the existing "Churn by Reason" section, when a sub-reason row is expanded (or clicked),
show the list of accounts from its `accounts` field below it — account name (linking out via
`hubspot_url`), ACV, and churn date. Same behavior for a top-level reason row's own
`accounts` field when there are no sub-reasons to expand into first.

## 3. Click-to-drilldown on "Churn by Product"

Add a new field to each item in the existing `by_product_breakdown` array: `accounts`, same
shape as above. Make each bar (DecisionAssist / Full-Screen / Unclassified) clickable to
expand and show that segment's account list the same way.

---

Once all three schema fields exist, tell me and I'll push the actual data (already computed,
verified against the existing counts) via the API — no further builder work needed after that.
