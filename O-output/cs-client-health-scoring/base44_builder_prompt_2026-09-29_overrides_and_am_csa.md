# Base44 builder prompt — Client Health: show AM/CSA + a HubSpot Overrides section (2026-09-29)

Paste this into the Findigs Hub AI builder, on the Client Health page. This is display-only —
every field it needs (`account_manager`, `csa`, `composite_score_partial.band`,
`composite_score_partial.floor_rule_applied`, `composite_score_partial.red_reasons`) already
exists on each account record. No new schema fields needed.

**Important: only change what's described below. Don't touch the sidebar navigation, any
other page, or anything on this page not explicitly mentioned here.**

---

## 1. Show Account Manager and CSA

**Rating Detail tab**: add two columns to the account table — **Account Manager** (from
`account_manager`) and **CSA** (from `csa`). Most accounts have an Account Manager; CSA is
only set on a handful of accounts — show an em dash (—) when `csa` is blank. Place both
columns after "Service type" and before "Units Live".

**Account detail popout** (opens from Rating Detail, Segment Detail, or WoW Movement): add
an **Account Manager** line (from `account_manager`) and a **CSA** line (from `csa`, only
shown when it has a value — omit the row entirely rather than showing a blank/dash here) to
the top info block, alongside the existing Segment / Service Type / Resolution Status rows.

## 2. New section: "HubSpot Score Overrides"

Add a new section on the **Rating Detail tab**, above the existing "By Rating"/"Flat" toggle,
titled **"HubSpot Score Overrides"**. Show it collapsed by default with a count in its header
(e.g. "HubSpot Score Overrides (5)"), expandable like the Rating Detail band groups already
are.

Filter to accounts where `composite_score_partial.floor_rule_applied` equals exactly
`"hubspot_health_score_override"`. For each, show a row with:
- **Account** (name)
- **Account Manager** (`account_manager`)
- **CSA** (`csa`, em dash if blank)
- **Overridden Rating** — `composite_score_partial.band` as a colored badge (Green/Yellow/Red,
  same badge style used everywhere else on this page)
- **Why** — the `detail` text from the `red_reasons` entry whose `row` equals
  `"hubspot_health_score_override"` (a short sentence naming the HubSpot company and rating)

If no accounts currently match the filter, show a muted one-line "No accounts are currently
overridden in HubSpot" instead of an empty table — this list will grow and shrink over time as
AMs set/unset the flag in HubSpot, so it needs to render sensibly at zero too.

Add one small caption line under the section title: "These accounts' dashboard score is set
directly from the Account Manager's Churn Risk rating in HubSpot (`client_health_score_override`
= Yes), overriding the usual metric-based scoring for the band only — the underlying metrics
below still compute normally."
