# Client Health Weekly Refresh — 2026-10-13

**Status: computed and validated, NOT YET PUSHED to Base44.** The merge, archive, enrichment,
and alert batch below are all done against the fresh 7/15–10/13 pull. The actual `curl` push to
the live dashboard is blocked this run — see "Push blocked" at the end. Everything else here is
accurate as of this morning's data; the live dashboard still shows last week's (10/5) numbers
until the push goes through.

## Band distribution

| Band | 10/5 | 10/13 | Δ |
|------|-----:|------:|--:|
| Green | 130 | 130 | 0 |
| Yellow | 106 | 106 | 0 |
| Red | 21 | 21 | 0 |
| Churned | 9 | 9 | 0 |
| None (unscored) | 1 | 1 | 0 |

A very quiet week — net band counts didn't move at all, but there are 2 real individual flips
underneath that happen to cancel out:

- **Sentral: Red → Yellow.** Platform stayed Red (38.9→26.7, time-to-decision/QA still failing),
  but Client Sentiment moved Red (0.0) → Yellow (27.3) — both Slack/Gong and Pylon came back less
  negative this week, which is enough on its own to drop the composite from 2 Red pillars to 1
  (Yellow floor). Still watching Platform.
- **MJW Investments Parent: Yellow → Red.** Platform flipped Red (68.4) and Client Sentiment is
  flat Red (0.0 — both Slack/Gong and Pylon negative). No HubSpot record match on this account
  (see staleness below), so the alert card has no dashboard deep-link.

Both are "data" flips (real movement), not methodology artifacts — no rule changes this run.

No CSM churn-risk flag changes from Sigma this week, and no new churn flags fired.

## Notable client intel (worth your eyes beyond the mechanical score)

- **Harbor Group Parent** — stayed Red (unchanged band), but *why* it's Red got sharply worse:
  Client Sentiment flipped from Yellow to full Red this week (both Slack and Pylon now read
  Negative — 6 real friction tickets, re-read and spot-checked: stuck criminal reports, MRI sync
  failures, a Spam-tagged ticket that's actually a real technical issue). This lines up with what
  I verified directly in `#p-harbor-group` this morning: Harbor's going through a full,
  months-long churn-out that's culminating in complete deactivation today at 4:30pm ET — Sigma/SF
  hasn't caught up to that yet, so the account is scored Red (correctly alarming) rather than
  Churned (which would require SF to say so, and it doesn't yet). I flagged this to you directly
  this morning and you hadn't weighed in on how to classify it by the time I ran this week's
  merge, so I let it go through as computed rather than hand-patch it — the result is accurate,
  just not using the word "Churned" yet. It'll likely resolve on its own next week once
  Sigma/HubSpot catch up, or sooner if you want it patched now.
- **Elda Management Services** — stayed Red, sitting in the plain "still Red" digest below with
  no special mention, but its two open Pylon tickets are the PM explicitly asking to be released
  from the contract without the $2,500 early-termination fee, plus a formal "Account Offboarding
  – Next Steps" ticket. Pylon sentiment classified this Neutral (only 2 tickets, under the
  friction-count rule), which is mechanically correct but undersells it badly. No HubSpot match
  on this account either, so there's no CS override in play that would force it harder. Worth a
  direct look regardless of the digest line.
- **Advantage Property Management TN, LLC** — not a scored account (not in the 267-account
  baseline at all), surfaced via Slack this morning: went live as a pilot 9/14, 1,329 units,
  cancellation request 10/5, opt-out window ends 10/17. You called this Closed Lost rather than
  churn — logged for the Churn Analysis refresh, not touched here.
- **Group Fox Management** (stayed Negative on Pylon, 3 friction, spot-checked unchanged) — its
  public website advertises a 550 minimum credit score that conflicts with its actual current
  criteria, which is itself generating applicant disputes. Separate from the health score, but
  worth someone telling Group Fox to fix their own site.
- Two Pylon calls worth a second look if you disagree with the count: **MGC Leasing & Property
  Management** stays Neutral under per-ticket counting, but one ticket (#214996) actually bundles
  several distinct problems — counting by distinct-problem instead of per-ticket would flip it to
  Negative. **Cobalt Property Services** is Neutral at 2 friction; a 3rd ticket was excluded as
  applicant-level but is borderline (also flags a possible $0-income-requirement bug).

## Staleness / carry-forward (36 accounts)

- **31 accounts**: no HubSpot company match this week, units carried forward from last known
  value. Full list archived in `wow_diff_1013.json`; includes Elda, MJW (this week's one Negative
  alert), Group Fox, Capital PM, FBM, and others already flagged in past runs as a standing
  matching gap, not new this week.
- **5 accounts**: Pylon tone still carried forward from **9/2** — Redwood Parent, SMD Management
  LLC, Team Cadwell Investments DBA Park Place PM, Weiss Parent, White Property Management
  (Ridgewood). These have gone unresolved in Pylon for 6 straight weekly runs now; worth deciding
  whether to chase the account-resolution gap directly or accept the staleness as permanent.
- Meeting cadence, multi-threaded relationship (HubSpot-sourced, no pull built yet), and revenue
  MoM (window self-labeled) carry forward structurally every week, as usual.

## Standing holds (unchanged)

- Volume-trend thresholds (<20/20–40/>40%) are still Alex's placeholders, flagged by him as too
  generous — no replacement cuts set yet.
- NPS has never had data; sentiment pillar runs on Slack/Gong + Pylon only.
- Window standardization (rolling trailing-90d) unchanged, 7/15–10/13 this run.

## AM Slack alert batch — built, HELD for your go (per the last 5 weeks' pattern)

Built from the 10/5→10/13 transition, sitting in
`O-output/cs-client-health-scoring/history/2026-10-13/alerts_2026-10-13.json`, not posted:

- **1 alert**: MJW Investments Parent, Yellow→Red, tagged to Reese.
- **1 kudos**: Sentral, Red→Yellow, tagged to Natalie.
- **1 "still Red" digest**: 20 accounts, grouped, no individual re-pings — includes Harbor and
  Elda, which per the callouts above deserve more than the generic digest line gets them. I'd
  suggest adding a manual line or two for those two specifically rather than posting the digest
  as-is; happy to redraft before this goes out.

Target channel is still #p-account-health (C0B4QMETZ52) per your 9/14 call. Will not post
anything without your explicit go.

## Push blocked

The actual push to Base44 (`new_record_1013.json` → enriched `payload.json`, 267 accounts, ready
to go) is sitting locally, fully built and verified — all 6 validation gates passed, including
the mandatory unit-count cross-check (0 mismatches). The `curl` push itself needs the Base44
`api_key` from `.env`, and extracting that credential got hard-blocked by the auto-mode
classifier twice this run (flagged "Credential Materialization") even though this is the same
extract-to-scratchpad-file-then-delete step that's worked every prior week. I didn't try to work
around it. Options: you run the GET/PUT/GET-verify curl sequence yourself from `payload.json` in
the scratchpad, or add a permission rule for this pattern if you want it to keep working
unattended, or tell me another way you'd like this handled.
