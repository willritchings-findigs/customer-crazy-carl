# How to read your Client Health scores

**For:** account managers and CSAs. A practical guide and training resource.
**The dashboard:** [Findigs Hub › Client Health](https://findigs-growth-hub.base44.app/cx/client-health). It refreshes every Monday morning (results around 9:30–9:45 ET).
**Technical details:** see [Client Health Dashboard: how it works](https://app.notion.com/p/416335d59add81748f99db6050a3b77b).

---

## The one-minute version

Every account gets a color each week:

| Color | What it means | What to do |
|---|---|---|
| 🟢 **Green** | Healthy across the board. | Keep doing what you're doing. Look for expansion. |
| 🟡 **Yellow** | Something specific needs attention. Often one weak area, not the whole account. | Open the account, find the weak area (it's named), and act on that one thing. |
| 🔴 **Red** | Several areas are weak, or the churn-risk flag is Red. | Treat as at-risk. Make a plan this week. |
| ⚪ **Churned** | The account has left (confirmed in HubSpot, no live units, no activity). | Not scored. |

The color is a summary. **The reasons under it are what you act on.**

---

## What goes into the color

Each account is scored on three areas:

1. **Platform & Product (50%)**: is Findigs working for them? Decision speed, approval rate, overrides, QA, support load, escalations, volume trend, PMS integration.
2. **Strategic Alignment & Relationship (30%)**: is our relationship with the right people healthy? Business reviews, exec sponsor, meeting cadence, how many people we know there, and your churn-risk flag.
3. **Client Sentiment (20%)**: how do they sound? Their Slack channel and Gong calls, and open support friction in Pylon.

Each item inside an area gets its own Green, Yellow or Red. Then:

- **One Red item makes its whole area Yellow. Two Red items make it Red.**
- **One Red area makes the account Yellow. Two Red areas make it Red.**
- **An account is Green only if all three areas are Green.**
- **Your churn-risk flag set to Red makes the whole account Red**, whatever else is true.
- **A HubSpot client-health override**, if someone has set one, replaces the score.

That's why an account that feels healthy can still be Yellow: a single Red item somewhere is enough. The card tells you which one.

**Full-Screen accounts** are scored on your churn-risk flag alone. Platform metrics don't apply to them, so keeping the flag accurate is the whole score.

---

## Reading an account card

- **Band and prior band:** this week's color and last week's. A change means it moved.
- **Weeks Red:** how many Mondays in a row it has been Red.
- **Pillar scores:** each area's color and a value out of 100. The "why" text names the items pulling it down.
- **Metrics:** each number with its color and the window it covers (the last 90 days).
- **Context (not scored):** revenue by quarter, live vs sold units, application completion rate, groups submitted vs expected. Useful for conversations; they don't change the color.
- **Band history:** the trend over past weeks.

---

## What you can influence, and how

| Item | What moves it | What you can do |
|---|---|---|
| **Churn-risk flag** | Your Salesforce/HubSpot churn-risk value | Keep it current. It's the single most powerful input: Red forces the account Red, and it is the entire score for Full-Screen accounts. |
| **Performance review cadence** | A business review on Gong in the last 90 days | Hold regular reviews, and title them clearly (see below). |
| **Executive sponsor** | A client exec on a Gong call in the last 90 days | Get the client's decision-makers on calls. |
| **Client sentiment** | What the client says in their `#p-` Slack channel and on Gong calls | Address concerns where they're raised. The read reflects the last 90 days. |
| **Support friction** | Open property-manager tickets in Pylon: 0 = Green, 1–2 = Yellow, 3+ = Red | Help get open tickets resolved and closed. |
| **Platform metrics** | Real product usage | Not directly, but a Red here (e.g. slow decisions, high overrides) is a great reason to call the client. |

### Getting credit for your meetings (Gong)

<!-- BEGIN GENERATED: gong_tips -->
- **Business reviews count when the Gong call title says so.** A call counts as a review if its title contains one of: “QBR”, “EBR”, “business review”, “quarterly review”, “exec review”, “account review”, “performance review”. A great QBR titled “Weekly sync” doesn't count.
- **Exec titles that count** (client attendees only, as written in Gong): CEO, CFO, COO, CTO, Chief, President, Founder, Owner, Principal, VP, EVP, SVP, Managing Director, Managing Partner, Director. Coordinators, managers and specialists don't count.
- **Invite client attendees with their work email.** Calls are matched to your account by the client's company email domain. A client on a personal Gmail address, or a dial-in with no email, may not be credited.
- **Findigs attendees never count**, including our own executives.
<!-- END GENERATED: gong_tips -->

---

## The Monday Slack posts in `#p-account-health`

<!-- BEGIN GENERATED: alert_rules -->
- **Individual alert** (pings the owner) when an account moves: Green → Yellow, Yellow → Red, Green → Red, new → Red, scored → Churned.
- **Kudos card** when an account improves: Red → Yellow, Yellow → Green, Red → Green.
- **Still Red:** one grouped digest listing every account that stayed Red, with how many weeks; nobody is re-pinged individually.
- Everything posts to #p-account-health, and only after a successful run.
<!-- END GENERATED: alert_rules -->

**When you're pinged:** open the account, read the drivers in the alert (they name the weak items), and decide on one action this week. If the data looks wrong, tell Will (see below).

If the refresh has a problem, nothing is posted that week: the channel only shows successful runs. No post on a Monday means the dashboard still shows last week's scores.

---

## Common misreads

- **"It's Yellow but the client is happy."** One Red item is enough for Yellow. Check which one; it's often a single metric or a stale relationship row.
- **"It improved to Yellow, so we're fine."** Not always. A Yellow can come from the rules rather than a real recovery (for example, a Red item clearing for lack of new data). Read the reasons.
- **"Meeting cadence and multi-threading haven't changed in months."** Right. Those two items are currently frozen from a one-time pull (May–August 2026) until a weekly source is agreed. Don't read week-to-week meaning into them.
- **"Exec sponsor is Red, but our CEO joined the call."** Findigs attendees never count. The item measures whether *the client's* decision-makers are engaged.
- **"Business goals and KPIs show nothing."** There's no data source for those yet; they're skipped and don't hurt the score.

---

## If something looks wrong

Message Will Ritchings with the account name and what you expected to see. Common causes: the client's email domain is missing from HubSpot (so Gong calls can't be matched), a parent company uses a different domain, an account was renamed, or the churn-risk flag is out of date. Fixes go into the rules by a reviewed change, so the next Monday's run picks them up.
