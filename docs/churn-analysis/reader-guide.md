# How to read the Churn Analysis dashboard

**For:** account managers, CSAs and CX leadership. A practical guide and training resource.
**The dashboard:** [Findigs Hub › Churn](https://findigs-growth-hub.base44.app/cx/churn). It refreshes every Monday around 11:05 ET, after Client Health.
**Technical details:** see [Churn Analysis Dashboard: how it works](https://app.notion.com/p/416335d59add81948d09f872988a5bf1).

---

## The one-minute version

- **Two groups of accounts.** *Churned*: customers who have left. *At Risk*: current customers whose Client Health score is Red this week.
- **The headline is true churn.** Churned revenue and the churned count leave out **Failure to Launch** accounts (signed but never went live). Those have their own FTL card. They're still in every chart below.
- **ACV** is the sum of the customer's Closed Won deals in HubSpot.
- **At Risk follows Client Health.** When an account turns Red on Monday morning, it shows up here the same morning; when it leaves Red, it drops off.
- **Nothing is removed by the system.** A churned account stays unless a person decides otherwise. New churns are added only when HubSpot shows a clear, recent churn; anything uncertain goes to Will for review.

---

## The tiles

| Tile | Read it as |
|---|---|
| **Churned ACV (total)** | All-time revenue lost to true churn (FTL excluded). |
| **Churned ACV YTD / this month** | True churn with a churn date this calendar year / this month, up to today. A churn with a future date (notice given, contract not ended) is left out until the date passes; the caption names it. |
| **Accounts churned** | Count of true-churn accounts. |
| **FTL card** | Accounts that churned without ever going live, and their ACV. |
| **At Risk** | Current Red accounts and their combined ACV. The caption says how many ACVs are confirmed by a Closed Won deal, and names any that aren't. |
| **Total ACV tracked** | True churn + FTL + At Risk. |

---

## The charts

- **By reason:** why accounts left. Click a reason to see the accounts behind it, and its sub-reasons. An account can have more than one sub-reason, so sub-reason totals can add up to more than the reason itself.
- **By product:** DecisionAssist, Full-Screen, or Unclassified (HubSpot's Findigs Products field is blank for about a quarter of churned accounts).
- **By segment / segment this year:** STRAT, MM + ENT, SMB and SMB (<250), with a DA / Full-Screen split.
- **Reason source:** where each true-churn reason came from (HubSpot's churn-reason field, the 2026 hand-tagged sheet, or none). A large *none* share means reasons aren't being recorded.

These charts include FTL accounts, so they add up to true churn **plus** FTL, not to the headline count.

---

## What you can influence

| You see | What it means | What you can do |
|---|---|---|
| Your account appears in **At Risk** | It's Red in Client Health this week | Open its Client Health card: the reasons are there. Fix those, and it leaves At Risk the Monday it stops being Red. |
| An At Risk account shows **$0 ACV** | No HubSpot match, no Closed Won deal, or many deals that need a check | Tell Will the right ACV; he approves it in the configuration. |
| A churned account has **Uncategorized** reason | No reason was recorded | Set the **Churn reason** in HubSpot when an account churns; new churns pick it up automatically. Use one of the reasons on the page. |
| A customer who left **isn't on the page** | Its HubSpot churn date is missing or older than 30 days, or its status still says Live / Onboarding / Pilot, or it has a recent Closed Won deal | Make sure HubSpot has **churned = true, a churn date, a churn reason**, and a non-live status. Or ask Will to approve it. |
| A churned account is actually still a customer | Possible win-back | Tell Will with the evidence (a new Closed Won deal or a written correction). The system never removes a churn on its own. |

---

## Common misreads

- **"Churned revenue dropped."** Since 2026-10-29 the headline is true churn only; FTL moved to its own card. Totals before and after that date aren't comparable.
- **"The reason chart doesn't match the churned count."** The charts include FTL accounts; the headline doesn't.
- **"At Risk changed but nothing happened to the account."** At Risk mirrors Client Health Red; check what moved in the account's Client Health score.
- **"This month shows $0."** It's early in the month or no true churn is dated this month yet. Future-dated churns count only once their date passes.

---

## The Monday Slack post

After a successful refresh, one line appears in `#p-account-health`: true churn and YTD, At Risk and how it moved since last week, how many new churns were added, and how many flags are in the report. If the refresh stops, nothing posts there and the page keeps last week's data; the reason goes to `#gtm-automation-log`.

---

## If something looks wrong

Tell Will (GTM Engineering) with the account and what you expected. Each week's report lists every change with its evidence, and every candidate that wasn't added and why.
