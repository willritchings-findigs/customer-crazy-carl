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

## Scripts wired to config (done 2026-11-05)

1. The 2026-10-28 `merge_refresh.py` is now the canonical `scripts/merge_refresh.py`.
2. Every script reads `config.json`: weights, band rules, floors, limits, pilot list, batch
   counts, HubSpot properties, Slack channel, portal, dashboard URL.
3. No hand-edited dates. Every script takes `--run-date` and `--scratch` (`scripts/ch_common.py`).
   Window, file suffixes, Gong pull range, and source-string dates all derive from the run date.
4. Credentials via `scripts/ch_secret.py`: environment variables first, local `.env` second.
   Works for either storage option still under discussion.
5. `scripts/contract_check.py` runs the §0 checks and lists every failure at once.
6. `archive_history.py` stops if `ts.txt` is missing (was: silently wrote `computed_at: null`),
   dropped the one-time 9/14 backfill, and archives the exact `config.json` + scripts per run.
7. `merge_refresh.py` stops with a clear message once the run date leaves Q4 2026, because the
   revenue quarter fields (Q2→Q3 complete, Q4 partial) are also dashboard field names.

**Verification:**
- **Equivalence:** the old 10/28 script and the new wired script ran on identical inputs
  (rebuilt from the 10/28 baseline's own numerators/denominators). Both passed join coverage,
  threshold reproduction, and the pilot unit test. Their outputs were **byte-identical**: the
  3.5 MB record, the WoW diff, and stdout.
- **Config is live:** changing one TTD threshold in a copy of the config made the merge abort
  at threshold validation (10 reproductions failed), as it should.
- **Quarter guard:** a 2027-01-05 run date stops with the revenue message.
- **Chain:** archive → enrich → alerts ran end to end against a temporary copy of the history
  folder (real history untouched). Archive refused to run without `ts.txt`.
- **Contract check, live:** run against the 10/28 baseline with a real HubSpot property read.

## Found by the contract check on its first live run

- **`churn_lost_to` does not exist in HubSpot.** The real property is `churn_lost_to__c`.
  The pull has requested a nonexistent field every week; HubSpot silently ignores unknown
  property names, so it always came back empty. Nothing downstream reads it. Fixed in config.
- **The live record has 267 accounts, not 268.** Confirmed by a read-only GET of the live
  record (computed 2026-10-28). Config updated to 267.
- **`gong_pull.py` had a fixed 6/10–9/08 window.** A run following the old canonical script
  would have pulled two-month-old calls. Now derived from the run date.

## Still to do before the first cloud run

1. ~~Save the q1–q7 SQL as files.~~ **Done 2026-11-05.** Recovered from the 10/28 run's
   transcripts into `queries/`; rendering for 10/28 reproduces that SQL exactly; every column
   confirmed live in Sigma; 12 previously undocumented columns added to the pre-flight
   check. Review items logged in the runbook's "Sigma queries" section.
2. **One fresh dry run** (pull + contract check + merge, no push) to prove the queries and
   the contract check against live Sigma.
3. Credentials storage decision (env vars on the cloud environment vs. per routine).

## Where Notion fits

Nothing in this design reads Notion at runtime. Recommended Notion role: a human-facing
methodology page for CSMs and leadership (what each band means, what the pillars measure),
written from `config.json`, not read by the job.
