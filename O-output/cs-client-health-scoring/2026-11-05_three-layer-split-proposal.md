# Client Health: three-layer split proposal (2026-11-05)

Branch: `draft/client-health-three-layer`. Nothing on `main` has changed. Nothing ran
against Base44, Sigma, HubSpot, or Slack.

## What changed

| Layer | File | Change |
|---|---|---|
| 1. Procedure | `.claude/skills/client-health-refresh/SKILL.md` | Rewritten: order of operations, gates, and step rules only. Every ID, threshold, and weight is now a `config.<path>` pointer. New §0 contract check. |
| 2. Logic + config | `.claude/skills/client-health-refresh/config.json` | **New.** Every ID, column, threshold, weight, formula, filter, validation floor, pilot list, Slack channel, and routing rule. |
| 3. Context + history | `T-tools/02-workflows/client-health-weekly-refresh.md` | Unchanged. Still holds the why and the incident log. |

Old `SKILL.md` is still on `main` (and `ARCHIVE_SKILL_2026-10-29_pre-split.md` is unchanged).

## How it was verified

1. **Config values vs. what actually ran.** Values were taken from the 2026-10-28 run's
   `merge_refresh.py`, then compared programmatically: all weight tables, pillar weights,
   band-to-score, pilot list, join floors, and the structural-diff limit match exactly. All 11
   band functions (approval, TTD, QA, ticket, volume, override ×3 segments, TES ×3 segments)
   produce identical bands to config on 2,500 test values each.
2. **Nothing lost from the old skill.** Every backtick token and identifier in the old
   `SKILL.md` was checked against the new skill + config + runbook + scripts. The check caught
   about 15 real rules dropped in the first draft (metric formulas, Pylon `user_type` fallback,
   friction definition, owner-map source of truth, gate-6 SQL, Slack scan fields, others); all
   were restored. What remains unmatched is ordinary prose wording.

## Drift found while drafting (why this matters)

- **The canonical `scripts/merge_refresh.py` is stale.** It is still the 2026-09-08 version.
  Each week's real script is a hand-edited copy saved in `history/<date>/`, differing by 90–220
  lines. Real logic exists only in those copies: the 6-state Pylon filter, Q2→Q3 revenue
  logic, a no-fresh-data sentiment branch, and a dynamic account count in join coverage. The
  next run, following the skill, would start from the stale copy.
- **The skill and code already disagree.** The old skill says 4 Pylon open states; the 10/28
  run used 6. Config follows what ran (6).
- **Source-string text disagrees with code.** The TES `source` string written into the
  record says "MM & SMB <2/2-5/>5"; the code bands SMB at <2.2/≤4.0. Display-only, but
  misleading on the dashboard.
- **Date constants are hand-edited every run** (`W_DATE`, `RUN`, Gong `FROM = '2026-06-10'`).

## Open decisions for Will

1. **Structural-diff limit: 25 or 20?** It was raised 20 → 25 on 2026-09-08 "for this run
   only" and then copied forward every week. Config keeps 25 so behavior doesn't change.
2. **First-alert-batch review gate.** The old skill required a review-first for the first
   alert batch under a new operator. Dropped per your 2026-11-04 decision to match the other
   routines (channel on success, DM on any failure). Revisit after the first cloud run.
3. **Dead reference.** The old skill pointed to `M-memory/project_cx_support_scorecard.md`,
   which was never in the handoff. Dropped; the pet-exclusion SQL is now fully in config.

## Not done yet (this branch is not runnable)

The new `SKILL.md` describes the target state. Before it can run, the scripts must catch up:

1. Promote the 2026-10-28 `merge_refresh.py` to `scripts/` as the canonical version.
2. Make every script read `config.json` instead of its own hardcoded constants.
3. Replace hand-edited dates with a `--run-date` argument (merge, archive, Gong pull, matcher).
4. Add the §0 contract checks (Sigma `describe`, Base44 GET, HubSpot property check).
5. Equivalence test: re-run the new scripts on the 10/28 archived inputs and confirm output
   matches `history/2026-10-28/new_record_1028.json`. The q1–q7 Sigma files were not archived
   that week, so this needs one fresh dry run instead (pull + merge, no push).

## Where Notion fits

Nothing in this design reads Notion at runtime. Recommended Notion role: a human-facing
methodology page for CSMs and leadership (what each band means, what the pillars measure),
written from `config.json`, not read by the job.
