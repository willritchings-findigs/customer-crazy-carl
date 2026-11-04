# Client Health Weekly Refresh — 2026-09-14

**Final state:** 267 accounts — **Green 132 · Yellow 107 · Red 19 · Churned 8 · Unscored 1** (PF Holdings, mixed rollup, intentionally unscored).
Last week (9/8): Green 132 · Yellow 95 · Red 31 · Churned 7 · Unscored 3.
Dashboard re-pushed 16:09 UTC; weekly snapshot record updated to match.

---

## Scoring change adopted this week: "no Red without a Red row"

**What changed.** A pillar can no longer band Red unless at least one row inside it is actually Red. Before today, a pillar with zero Red rows fell through to raw value cutoffs (<60 = Red), so two Neutral sentiment reads — nobody unhappy, just nobody gushing — scored 50 and painted the pillar Red. Same trap hit Strategic pillars with a single Yellow row. Now a zero-red pillar caps at Yellow. The rules when Reds exist are untouched: 1 Red row still forces Yellow, 2+ still force Red.

**Why.** Neutral is the absence of a negative signal, not a negative signal — quiet accounts were defaulting to Red, which diluted what Red means. Worse, the old math could invert improvements: Beztak's Pylon tone improving Negative→Neutral moved its sentiment pillar *Yellow→Red*, because one real Red row triggers the Yellow floor but two Neutrals fell through to the value band. Signed off by Emma 2026-09-14; engine rule `0-red-rows-caps-at-yellow` in `merge_refresh.py`.

**Impact of the fix (same-day rescore + re-push):**
- 26 pillar bands corrected: 17 Client Sentiment, 9 Strategic. No pillar worsened.
- 13 composites moved Red → Yellow, no other composite changed: Benjamin H Realty, Beztak, Cobalt, CRI, Charleston, FBM, Modern City, MS Coast, Oakwood, Redwood, Stevens Realty, TPG, Woodlake.
- These are formula corrections, not account improvement — they're tagged `methodology-0red-cap` in the week's diff, excluded from Slack kudos, and the pre-rule record is archived (`new_record_0914_pre_0redcap.json`) for audit.
- **Heads-up for Alex:** 13 accounts he may have seen Red on the dashboard are now Yellow as of ~16:00 UTC today.

## Real account movement (9/8 → 9/14, data-driven)

**Worsened (2):**
- **Howard Management Group Parent** — Green → Yellow. Client Sentiment dipped (Slack/Gong now Neutral, 71.4/100).
- **Realty Solutions LLC** — Green → Yellow. Same pattern: Client Sentiment 71.4/100 on Neutral comms.

**Improved (6):**
- **Hudson Homes Management LLC** — Yellow → Green. Sentiment recovered Red → Green; all pillars Green.
- **White Property Management – Ridgewood** — Yellow → Green. Platform metrics back to Green; all pillars Green.
- **Harbor Property Management, Inc.** — Red → Yellow. Sentiment up Red → Yellow; platform still weak (37.3/100).
- **MJW Investments Parent** — Red → Yellow. Sentiment Red → Green; strategic still watching (50/100).
- **Neighborhood Revival** — Red → Yellow. Sentiment up; platform and strategic still borderline.
- **RPM Piedmont** — Red → Yellow. Sentiment up; platform and strategic still borderline.

**Churned (1):** Morgan Property Management — churned now per Emma's call (contract end 12/31, dissatisfaction, moving to BoomPay).

**Watch list — the near-Reds.** Beztak, Oakwood, Benjamin H, CRI, and TPG all slid Yellow-ward this week and would have shown Red under the old rule. Their platform pillars carry *genuinely* red rows (time-to-decision, ticket ratio, QA); they're Yellow because sentiment no longer piles on. These five are the most likely next-Reds if platform metrics don't recover.

**Still Red (19):** Brandywine, Brick and Timber, Bridge Tower, CORE Residential, Elda, Equity Real Estate, Evernest, Exceptional PM, HomeRiver, KAIZEN, Lynco, Remax–Chuck Wartman, Rookwood, Toomey, TruHome, Weiss, 3 Options, MGC Leasing, Sentral. All Red on rows that are actually red — the artifact Reds are gone.

**SF churn-risk flag changes:** none observed this run.

## Slack alerts (#client-health-alerts, C0C1MK83T9U)

First live batch regenerated post-fix, pending Emma's go: **2 alert cards** (Howard, Realty Solutions), **6 kudos cards** (the improvements above), **1 still-Red digest** (19 accounts, first names + weeks-red, no pings). The 8 accounts that left Red via the formula fix get no kudos — noted here instead. After this first approved batch, posting is automatic on future refreshes.

## Standing items

- PF Holdings stays unscored (mixed rollup; activity collapsing — subs 69→16, Q3 revenue $100).
- Volume-trend thresholds still await Alex's call.
- Ownership sheet gaps: TPG, FBM, Capital PM Parent, Ebner, MS Coast, Weiss have no AM listed; "Thomas" → Thomas McCarthy mapping needs Emma's confirm.
