# How to read the Support Metrics dashboard

**For:** support leads, agents, and CX leadership. A practical guide and training resource.
**The dashboard:** [Findigs Hub › Support Metrics](https://findigs-growth-hub.base44.app/cx/support-metrics). It refreshes every Monday morning (results around 10:20 ET).
**Technical details:** see [Support Metrics Dashboard: how it works](https://app.notion.com/p/416335d59add813ab572c4f8396a1166).

---

## The one-minute version

- **Every number is a full count of Pylon tickets**, rebuilt from scratch each Monday, except first-contact resolution, which is a weekly sample of about 500 closed tickets.
- **Two windows:** *30d* is the 30 days ending yesterday, *7d* the last 7 days. The run day itself is never included (it's a partial day).
- **Pet tickets and spam are left out** of every figure. Pet tickets have their own Pet SLA tile; spam shows only as a row in By Category.
- **Property manager vs applicant** comes from the requester-type field on the ticket. Tickets with no requester type (mostly automated or internal mail) count in volume but not in the segment splits or the SLA.
- **Needs Attention is your worklist:** the oldest open tickets where the next move is ours.

---

## The tiles

| Tile | Read it as | Good direction |
|---|---|---|
| **Ticket volume** | How many tickets came in. | Context, not a target. Compare with tickets per 100 applicants. |
| **Median first response** | Half of tickets got a first response faster than this. | Lower. It moves in whole minutes, so 1 → 2 is a small change. |
| **SLA within target** | Share of PM and applicant tickets answered within target: **chat and Slack 2 minutes, email and form 4 hours**. Never answered = missed. | Higher. |
| **First-contact resolution** | Share of closed tickets solved in **2 or fewer agent replies**. | Higher. See "Common misreads" for why applicant FCR looks low. |
| **PM CSAT / Applicant CSAT** | Average survey score (1–5) on tickets from the window. Check the n: 7-day samples are small. | Higher. |
| **Tickets per 100 applicants** | Support load relative to how many people applied. Rising while volume is flat means fewer applicants, not more problems. | Lower. |
| **Handled without escalation** | Share of tickets that didn't need a tech escalation. | Higher. |
| **Median resolution** | Half of tickets were resolved faster than this. | Lower. |
| **Pet SLA** | Share of pet-verification tickets answered within 24 hours. Separate target, not comparable with the channel SLA. | Higher. |

---

## The sections

- **By Channel:** where tickets come from and each channel's SLA target. Chat is usually about half of volume.
- **By Category:** what kind of ticket, by the Pylon category the agent set. *Uncategorized* means no category was set; *Ticket (generic category)* is a real Pylon value with no specific type. Spam appears here only.
- **Friction themes:** within the biggest categories, what people write about, read from the subject line. *Other* is always large (one-off subjects); watch the named themes week to week.
- **12-week trend:** each point is one 7-day week ending the day before the run. Look for a sustained change over several weeks, not one point.
- **Priority and agent:** load and open counts by priority and by agent. *Findigs Support Agent* is the AI agent. *Other* in the share chart is everyone outside the top 10.
- **By category by segment:** the category mix for property managers and applicants separately. Shares are of each segment's own total.
- **Needs Attention:** up to 50 open PM and applicant tickets waiting on us (status New, Waiting on You, On Engineering, or On Customer Success Team), created in the last 90 days, **oldest first**. Each links to the ticket in Pylon and shows its age in days and whether it has a tech escalation.

---

## Using Needs Attention

1. Start at the top: these are the longest-waiting tickets.
2. If a ticket is actually waiting on the customer, change its status in Pylon to *Waiting on Customer*. It drops off next Monday.
3. If it's with Engineering, check the linked engineering ticket and nudge it there.
4. Tickets older than 90 days don't appear. They are counted as stale backlog in the weekly report. Ask Will for the list if you want to clear them.

---

## Common misreads

- **"Applicant FCR is terrible."** Partly a counting effect: on chat, agents often send three or four short messages in a row, and each counts as a reply. Compare applicant FCR week to week, not with PM FCR.
- **"Email SLA used to be much higher."** Before November 2026 SLA counted only tickets that got an answer, and included pet and spam. Now an unanswered ticket is a miss, and automated mail with no requester type is left out. The numbers aren't comparable across that change.
- **"Volume dropped."** Since November 2026 spam is excluded from the headline (about 400 tickets a month).
- **"The 7-day CSAT jumped."** Check the n on the tile. Ten or so responses can swing it a lot.
- **"My ticket isn't in Needs Attention."** Check its status (only the four "waiting on us" statuses count), its age (90 days max), its requester type (PM or applicant only), and that it isn't a pet or spam ticket.

---

## The Monday Slack post

After a successful refresh, one line appears in `#p-account-health`: 30-day volume, SLA, FCR, median first response, CSAT for PMs and applicants, and how many tickets are in Needs Attention and stale. If the refresh stops for any reason, nothing posts there and the dashboard keeps last week's numbers; the reason goes to `#gtm-automation-log`.

---

## If something looks wrong

Tell Will (GTM Engineering) with the tile or section and what you expected. Every week's inputs are archived, so any number can be traced back to the exact tickets behind it.
