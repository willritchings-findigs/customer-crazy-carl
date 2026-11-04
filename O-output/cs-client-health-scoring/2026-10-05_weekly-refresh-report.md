# Weekly Data Refresh — 2026-10-05

## 1. Client health

The delegated background run on this one went bad enough that I took it over and ran it
myself in the foreground: its q4 (company/units/status) pull was a 97-byte stub, q7 (funnel)
was empty, and all three sentiment batches (Slack, Gong, Pylon) were unusable — Slack scraped
the wrong channel entirely (the alert-output channel itself, not per-account channels), Gong
came back 100% "Neutral" with zero differentiation across 78 companies, and Pylon only
analyzed 7 of 83 target accounts. None of that went into scoring — sentiment carries forward
untouched this week with honest staleness notes (153 of them, almost all "Pylon account not
found this run; prior tone carried forward" — expected, since I fed it empty batches rather
than fabricate anything).

I re-pulled q1/q2/q3/q4/q5/q7 fresh from Sigma myself and found two real bugs on the way:

- **merge_refresh.py's own pilot-account unit test** didn't pass the HubSpot
  `client_health_score_override` rating into its test call, so it flagged Harbor Group Parent,
  Beztak, and Brick and Timber Parent as "failures" even though the underlying pillar math was
  byte-for-byte correct — it just wasn't applying the override the same way the real per-account
  loop does. One-line fix, re-ran clean.
- **My own first q2 (submission-volume) pull silently dropped Bridge Homes** and swapped in two
  unrelated accounts, landing on the same total row count so nothing looked obviously wrong.
  Caught it because Bridge Homes almost auto-churned on a false "zero activity" signal — a direct
  Sigma re-query showed 470 real trailing-90d submissions (last one 9/21). Re-pulled q2 cleanly,
  confirmed against q1's decisioned-count for the same account, re-ran.

Ran the full gate suite, including the gate added 9/28 specifically because a unit-count bug
(44/267 accounts undercounted) passed every other gate cleanly: independently re-queried the 10
largest rollups by child-company count and diffed against what was about to ship. All 10 matched
exactly (Beztak 21,539, Highmark 20,885, Oakwood 13,198, Harbor 11,909, etc.) — no recurrence.

**Result: 267 accounts, G130 / Y107 / R21 / Churned 8 / None 1 — unchanged from this morning's
baseline.** Zero new computational flips this run. Pushed, enriched (account_manager/csa/
prior_band/weeks_red/band_history), GET-verified, archived to permanent history
(`history/2026-10-05/`), and the weekly Base44 snapshot record posted (id `6ac3b2a30d759bec62a2a2b3`).

### Catches this run
- **Bridge Homes was marked churned/acquired in HubSpot on 9/29** ("Bridge was acquired"), but
  had real platform activity through 9/21 (470 submissions) and zero live units right now. The
  same guardrail that protects against false-churning an active rollup (it requires *both* zero
  live units *and* zero activity, not either alone) correctly declined to auto-churn it — it's
  carrying forward in its real FS/CSM-flag band (Yellow) instead. Worth a quick CSM gut-check
  given the acquisition is real, but I didn't force a status change on a single ambiguous signal.
- **Support Metrics' `computed_at` was stale** (stuck on 9/29 even though the KPI values
  themselves — ticket volume, resolution time, CSAT — were genuinely fresh from today's pull, I
  checked the actual numbers against the agent's claimed before/after and they reconciled
  exactly). The push script just never touched the timestamp field. Patched it directly;
  no data was wrong, just the "last computed" label. See §4.

### Slack alerts — awaiting your go
`build_alerts.py` compared against the last *properly archived* snapshot (9/28 — the real
calendar-week comparison, as opposed to this morning's baseline which already had Monday's
HubSpot-override patch baked in, which is why the pipeline itself shows 0 flips but the alert
system still has content):

- 🔴 **1 new Red** — Harbor Group Parent (Yellow→Red), owner Thomas, CSA Ashley
- 📈 **2 kudos** — Beztak Properties Parent and Brick and Timber Parent, both Red→Yellow
- ⚪ **20-account still-Red digest**, no individual pings

All three cards have resolved owners (no ownerless holds this week). Saved to
`history/2026-10-05/alerts_2026-10-05.json`, not posted — same as every prior week, I'd like
your go before anything lands in #p-account-health.

## 2. Churn analysis

All three builder prompts from the Oct 2 call review are confirmed live (you pasted them into
Base44 and it built them):
- Sub-reason overlap caption (the "Dissatisfaction with Product/Service" $300K oversum is now
  explained in place, no totals changed)
- Custom date-range picker alongside the existing Time Period presets
- Chart segments and Churn-by-Segment rows now click through to a pre-filtered account table

The builder flagged three honest scope gaps rather than guessing, worth knowing about:
- Sub-reason rows have no click-through yet — the Account Detail table has no Sub-Reason filter
  to point at. Separate ask if you want it.
- Churn-by-Product clicks route through the existing page-level Product pill (labels differ —
  DecisionAssist/Full-Screen/Unclassified vs. DA/FS/Unknown — the builder mapped them).
- No CSM/owner-concentration chart exists on this page today, so that part of the original ask
  has nothing to attach to.

The data dictionary for Will is written and includes the pending Failure-to-Launch proposal and
the DA/FS reconciliation finding — see `O-output/churn-analysis/data_dictionary_2026-10-05.md`.

## 3. Implementations

Refreshed and pushed (record `6aa833ac3d25aa397d5f6ba7`, computed 13:31 UTC today). Confirmed
directly in the pull script that `ongoing_worklist`/`aging_worklist`/`capacity_gantt`/
`capacity_weekly`/`follow_up`/`board_totals` all come from the Google Sheet ("Existing
Launches"), not HubSpot or Sigma — per your instruction. Also fixed a real security issue in
the pull script itself: it had the HubSpot token and Base44 key hardcoded in plaintext; both now
read from `.env`.

## 4. Support metrics

Refreshed and pushed (record `6ab2a47fe51f717a0cccd58d`). Ticket volume down ~5% both d7/d30
(16,378 d30, within normal week-to-week variance), resolution time and escalation rate flat,
CSAT essentially stable (PM 4.40, applicant 3.50 d30). Pet-exclusion NULL-safety re-verified —
two independently-phrased filter versions reconcile exactly.

Carried forward, not refreshed this week (on a slower cadence, unchanged from 9/22–9/29):
`fcr_pct` (needs a dedicated Pylon pagination pass), `trend_12wk`, `friction_themes`,
`priority_breakdown`, `agent_breakdown`, `by_priority`, `by_category_by_segment`.

## Still with humans

- **Failure-to-Launch ACV exclusion** (Alex's proposal, 10/2 call) — exact before/after headline
  numbers already given to you in chat; not shipped, needs your explicit go since it changes a
  board-facing figure.
- **Whether to rebuild the 11-account FTL bucket using a "churned before go-live" test** — your
  own question from earlier. My investigation: the existing auto-detection rule (6+ months
  stale) has 2 confirmed false positives and 2 ambiguous cases on spot-check; the human-tagged
  accounts (Sigma + hand-sheet) are mostly right (5 clean / 1 wrong). No HubSpot field already
  captures this distinction cleanly — written up in the data dictionary §5, flagged as pending,
  not auto-applied.
- **5 HubSpot-status-drift accounts** ($283,180.22 combined ACV) flagged earlier — still sitting
  in ChurnCache as Churned/FTL; whether to pull them out is your call, not made yet.
- **Bridge Homes** (§1 above) — real HubSpot acquisition, real recent activity, currently
  carrying forward Yellow. Worth a CSM check-in, not something I auto-resolved.
