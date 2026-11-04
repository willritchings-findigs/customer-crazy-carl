# Client Health Weekly Refresh — 2026-09-14 (second scheduled run)

> **Post-publish corrections, same day (per Emma):** Morgan Property Management is now
> **Churned** (HubSpot churn_date 2026-12-31 is the contract end; reason "Dissatisfaction with
> Product/Service", moving to BoomPay — Emma overrode the future-dated hold), and the
> **Real Property Management umbrella row was removed** from the record entirely (the individual
> RPM franchises remain scored as their own accounts — don't resurrect the umbrella). Live
> record is now **267 accounts: G132 / Y94 / R32 / Churned 8 / Unscored 1** (PF Holdings is the
> sole remaining unscored — see the child-level breakdown appended at the bottom). Re-pushed
> 15:50 UTC, snapshot record updated to match, both verified.

Pushed live 2026-09-14 14:24 UTC (HTTP 200, GET-verified). Window: trailing 90d,
2026-06-16 → 2026-09-14. Baseline for deltas: the 2026-09-08 record. First true
apples-to-apples week (both runs rolling trailing-90).

## Band distribution

| Band | 9/8 | 9/14 | Δ |
|------|-----|------|---|
| Green | 132 | 132 | 0 |
| Yellow | 95 | 94 | −1 |
| Red | 31 | 32 | +1 |
| Churned | 7 | 7 | 0 |
| Unscored (None) | 3 | 3 | 0 |

A quiet week structurally — 13 composite flips, all data-driven (no methodology changes), and
**zero SF churn-risk flag changes** (last week's CSM book review has settled).

## Flips — worsened (6)

- **Sentral stays Red** is the headline non-flip: the scan agent initially had it improving to
  Yellow, but direct Pylon verification found 59 open in-window issues and 5 real platform
  frictions — "Unable to Submit Applications – Joinery 2" (9/1) and "URGENT: Joinery Findigs"
  (9/4) still open, a Yardi application-status issue, and two lead-attribution problems that
  match the Slack complaints (client asked about rollback options). Red, verified.
- **Beztak (Yellow → Red)**, **Oakwood (Yellow → Red)**, **Benjamin H Realty (Yellow → Red)**,
  **CRI Property (Yellow → Red)** — all four land Red via the same mechanics: platform pillar
  already Red, and the sentiment pillar became *all-Neutral*, which scores 50/100 → value-band
  Red. **Methodology artifact worth Alex's review**: a pillar with one Negative row gets
  count-lifted to Yellow, but a pillar that's all-Neutral bands Red — so Beztak's Pylon read
  *improving* from Negative (5 frictions) to Neutral (2) actually *worsened* its composite.
  This behavior predates this run (10 accounts in the 9/8 baseline band the same way) so I
  left it untouched, but it's now producing counterintuitive flips. Proposed fix if wanted:
  all-Neutral pillars band Yellow. Needs sign-off — not changed.
- **TPG Management (Yellow → Red)** — platform genuinely weak (TTD Red, QA Red, TES Red) plus
  the same single-Neutral-row sentiment artifact.
- **Howard Management, Realty Solutions (Green → Yellow)** — fresh Neutral sentiment reads
  where last week had Positive/no data; not unanimous Green anymore.

## Flips — improved (7)

- **Hudson Homes (Yellow → Green, 96.0)** — Slack Positive + Pylon friction cleared (1→0).
- **Harbor Property Mgmt, Neighborhood Revival, RPM Piedmont (Red → Yellow)** — Pylon friction
  cleared (1→0 each), lifting the sentiment pillar out of the all-Neutral-Red state.
- **MJW Investments (Red → Yellow)** — Slack turned Positive post-launch; sentiment pillar all-Green.
- **White PM – Ridgewood (Yellow → Green)** — volume trend recovered (−25% → −18.2%).
- **Sentral note above; RPM Rental Solutions stayed Yellow but improved** (TTD Red → Yellow).

## Client intel needing AM eyes (from verified Slack/Gong/Pylon scans)

- **Harbor Group (Yellow, 67.7): churn in progress.** 25 properties offboarded 8/10, the
  remaining ~40 planned for offboarding 10/1, and a $210k outstanding invoice flagged 8/4.
  Composite Yellow understates this — the CSM flag is not set Red in SF (zero flag changes
  this week). Strong candidate for a manual flag review.
- **Evernest (Red, hard override): Boom trial expanding to ~50% of portfolio** — TN week of
  10/1, GA 10/7, VA 10/14, ~60-day parallel evaluation. Metrics actually fine (TTD 42.8h
  Green-side, approval 55.9%) but TES 8.4% Red, volume −29.9%, Q3 revenue pacing at less than
  half of Q1 (94k vs 183k). Pylon now Negative (4 verified frictions incl. an outage thread).
- **Bryten (Yellow): asked to pause/turn off Findigs 9/9** after weeks of unresponsiveness.
- **Modern City (Red): "very high risk"** per CSM 8/4 — client expressed regrets about
  Findigs; workflow pain points; churn language in an 8/11 call.
- **Cooper Zadeh (Yellow): exploring alternative vendors** (6/25 API discovery call).
- **Rent Appeal (Yellow): compliance-flavored escalation 8/26** — missed eviction records on
  a screened applicant; client asked why. Worth a UW/compliance follow-up.
- **Elda Management (Red): "high churn risk"** per CSM 6/23 — expectation misalignment on
  what DA does. (Its HubSpot units also vanished from the 507-company pull — record may have
  been renamed; units carried forward.)
- **Legacy Invest (Yellow): CSM marked high churn risk 7/17** — client not processing
  applications; SF flag currently Yellow after last week's downgrade from Red.

## Contradictions to resolve (humans)

- **Out Fast PM: composite Green 100 (FS, flag-anchored) vs Slack saying they churned to
  RentEngine on 7/9.** Same contradiction as last week, now with an in-window churn message.
  The SF flag says Green; someone needs to pick a truth.
- **RPM Rental Solutions: HubSpot churned=true dated 2026-07-27** while the account is highly
  active (152 submissions t90, live units on file). Auto-churn correctly did NOT fire (zero-
  activity guard), but the HubSpot record needs cleanup or the churn is partial/mis-dated.
- **Renters Warehouse / PF Holdings / RPM umbrella** — standing mixed-rollup holds unchanged.
  PF/RPM parked methodology text corrected this run (it wrongly said "no platform activity";
  PF has 16 t90 submissions — the real reason is the mixed child statuses).

## Data corrections this run (units/matching)

Last week's HubSpot name-matcher silently summed multiple fuzzy-matched records; rebuilt as a
staged matcher (`scripts/match_hs_accounts.py`) with a hand-adjudicated alias/block table.
229 of 233 matched accounts' units are identical week-over-week. The 4 changes are corrections:
- **Harbor Group Parent 22,955 → 21,655** and **Harbor Property Mgmt 22,955 → 1,300** (last
  week both got Harbor Group's + Harbor PM's units summed).
- **Peak Property Mgmt 6,081 → 2,410** (was a sum of three different "Peak" companies).
- **Rental Management Group 370 → 200** (HubSpot-side edit, exact record).
Highmark still renders "— / —" (HubSpot units=0, pilot). 17 accounts carry forward with notes.

## Revenue movers (Q3 partial through 9/13, contextual/unscored)

- **Highmark $257k Q3 vs $46k Q2** — pilot ramp is real money now.
- **McKinley $317k Q3** — highest on the book this quarter, ahead of full-quarter Q2 ($257k).
- **Evernest declining: $183k → $164k → $94k** (Q1→Q3) — consistent with the Boom-trial story.
- SFR3 $277k and Maymont $179k pacing below Q2.

## Verification log (subagent QA — the reason several numbers moved)

- 17 scan agents (8 Slack, 5 Gong, 4 Pylon). Window discipline enforced ≥ 2026-06-16.
- **7 Slack overrides**: Benjamin H, CORE, KCP, InveServe, TruHome (+ Woodlake reclassified) —
  classifications had been built on pre-window events; direct channel reads showed empty or
  thin windows. Lynco was too large for its agent — I read the channel directly (Neutral;
  expanding + referred Winfield to DA, but LRO blocked applications 8/20 and a 7/31
  missing-records complaint).
- **3 Pylon Negatives overturned on direct verification** (Western Wealth, Oakwood — meeting
  invites and launch-coordination threads had been counted as friction; one cited title didn't
  exist on the account) and **1 Neutral restored to Negative** (Sentral, undercounted). Counts
  spot-verified exact: WW 23, Evernest 25, Oakwood 38, Sentral 59.
- One merge bug caught pre-push: the Pylon results' found-flag name changed and every Pylon
  row was silently skipped on first merge; fixed, engine + skill patched.

## Storage (Emma's ask this week: running red/yellow/green + why repo)

1. **`O-output/cs-client-health-scoring/history/` is the system of record**, now with whys:
   every slim per-account row in `wow_history.json`/`.csv` carries `why` (composite),
   `platform_why` / `strategic_why` / `sentiment_why`, and compact `red_reasons` — and the
   9/4 + 9/8 entries were backfilled from their archived full records, so the whole history
   has whys, not just from today. CSV pivots straight into Sheets.
2. **Yes, it's in Base44 too**: a slim `health_snapshot_2026-09-14` record (~330 KB) was
   POSTed to AccountHealthCache after the main push (id `6aa803f18aa521a2fe43ec9b`), and the
   overview was re-PUT afterward so it stays the latest-updated record — the dashboard renders
   correctly whether it binds by cache_key or recency (LIST-verified: 2 records, overview
   newest). Each Monday now appends one snapshot record. If in-dashboard trend views are
   wanted, the data's already there — display is a builder prompt away (I'll draft it on ask).

## Still with humans

- Volume-trend thresholds: Alex's replacements still pending (<20/20–40/>40 in force).
- **New for Alex/Emma: the all-Neutral sentiment pillar → Red artifact** (see Flips).
- Out Fast truth-pick; Harbor Group flag review; RPM Rental Solutions HubSpot churn cleanup.
- AM Slack alerts: build is next (channel #client-health-alerts pending creation by Emma;
  first batch will be shown for review before anything posts).

## Appendix: PF Holdings, child by child (why it's the last unscored account)

Sigma rollup "PF Holdings" = a parent + 10 child entities, all RentManager, single-family,
Natalie Jamnik's book, live since Oct–Dec 2022. HubSpot side: "PF Holdings LLC", status Live,
5,531 booked units, domain aloftmgt.com (they operate as Aloft Management).

| Child entity | SF flag | Status | Live units (Sep) |
|---|---|---|---|
| Granada Gardens | Green | Live | 941 |
| Highland Woods | Green | Live | 800 |
| Multi Family – Clarkwood Greens | Green | Live | 568 |
| Dorchester Village Apartments | Green | Live | 468 |
| The Perch on Lake | Green | Live | 240 |
| White Pond Villa | Green | Live | 173 |
| Latitude / Apex University / Brittany Village | Green | Live | (no counts logged) |
| **Landmark Square Apartments** | **Churned** (2023-03-23) | Prospect | 0 |

The entire "mixed rollup" problem is **Landmark Square** — a prospect child that churned in
March 2023 and never went live. Its lone "Churned" value concatenates into the rollup's flag
string ("Churned, Green") and status string ("Live, Prospect"), and the 9/4 methodology parks
any mixed "Churned, X" rollup as unscoreable. Every entity that actually runs on Findigs is
flagged Green.

**If unparked**, PF is a Full-Screen account (DA off everywhere) → flag-anchored score → all
live children Green → it would band **Green 100**. Before doing that, know what Green would be
papering over — the trailing-90 usage is collapsing:
- submissions 69 → **16** vs the prior 90 days (−77%)
- revenue $5,576 (Q1) → $2,416 (Q2) → **$100** (Q3 through 9/13)
- 4 decisions in the window, median TTD **149 hours**
- funnel 63 starts → 16 submits

Two options: (a) rule tweak — ignore churned children's flag values when a rollup has live
units → PF scores as FS-Green next run; or (b) keep it parked. Either way this pattern reads
like quiet disengagement, not a healthy Green — worth Natalie eyeballing the flag before we
let it anchor a score.
