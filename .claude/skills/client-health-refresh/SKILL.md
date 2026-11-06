---
name: client-health-refresh
description: Run the weekly CS Client Health dashboard refresh end-to-end — pull Sigma/HubSpot/Gong/Slack/Pylon, rescore every account under the ratified 50/30/20 methodology, validate against the live record, push to Base44, archive history, post AM alerts, and write the week-over-week report. Use every Monday, on every scheduled routine run, or when Will says "run the client health refresh".
---

# Client Health Weekly Refresh

Rebuilds the `AccountHealthCache` record behind the Findigs Hub Client Health page.

**How this skill is organized (three layers):**

| Layer | File | Holds | Changes by |
|---|---|---|---|
| 1. Procedure | this file | order of operations, gates, rules for each step | commit |
| 2. Logic + config | `config.json`, `scripts/`, `queries/` | every ID, threshold, weight, filter, channel, and the exact Sigma SQL | commit |
| 3. Context + history | `T-tools/02-workflows/client-health-weekly-refresh.md` | why each rule exists, incident log | anytime |

This file never contains a number, ID, or threshold. Those live in `config.json` and are
referenced below as `config.<path>`. If this file and `config.json` disagree, stop and DM Will.

**Never publish the Base44 app builder.** Data goes through the API only. Display changes
are delivered as a builder prompt for Will to paste.

## 0. Pre-flight and contract check (stop on any failure)

Run all of these before pulling data. Any failure → DM Will what failed, post nothing, stop.

1. **Run date and window.** Run date = today (UTC). Window = `config.window.trailing_days`
   ending on the run date. Use the identical window string everywhere, including source strings.
2. **Connectors live.** Sigma, HubSpot, Pylon, and Slack each answer one cheap call. Gong API
   answers one probe (`gong_pull.py probe`). Connectors can drop mid-session; re-check before
   each long step.
3. **Save the inputs for the contract check** into the scratch dir:
   - `baseline_<MMDD>.json`: `curl` GET of the `config.target` record (Bearer token). This is
     also the WoW comparison point.
   - `sigma_describe_<key>.json`: raw `describe` output for every key in `config.sigma.elements`.
4. **Run `scripts/contract_check.py https://api.hubapi.com --run-date <date> --scratch <dir>`.**
   It lists every failure at once. Checklist:
   - **Base44:** record has every `config.target.persisted_fields`; `cache_key` matches;
     account count == `config.target.expected_account_count`.
   - **Sigma:** every column in `config.sigma.elements.*.columns` and `*.named_columns` exists
     in that element's describe output, **and** every column any `queries/*.sql` file uses
     exists and is documented in `config.json`. A query using an undocumented column fails
     the check: document it in config in the same commit as the query change.
   - **HubSpot:** every property in `config.hubspot.company_properties` exists on companies.
   - **Credentials:** every one resolves (network secret, environment variable, or local
     file); the check prints sources only, never values.
   A changed account count is not necessarily wrong: stop, ask Will, and update
   `config.json` if confirmed.
5. Config/record agreement is checked again by validation gate 1 inside the merge.

**Setup rules:**
- Every script runs in place from the repo (never copy scripts elsewhere) and takes
  `--run-date YYYY-MM-DD --scratch <dir>`. Pulls and outputs live in the scratch dir; history
  is written to the repo. Dates and file suffixes (`_<MMDD>`) all derive from `--run-date`.
- **Credentials** come from `scripts/ch_secret.py`, in order: network secrets on the cloud
  environment (services listed in `CH_PROXY_AUTH`; the proxy adds the header, so send none),
  environment variables (`HUBSPOT_TOKEN`, `GONG_ACCESS_KEY`, `GONG_ACCESS_SECRET`,
  `BASE44_TOKEN`), then the local `.env` (`Label: value` format). Scripts handle all three.
  For Base44 `curl`: if `CH_PROXY_AUTH` includes `base44`, send no `Authorization` header and
  skip the token file. Otherwise write the token to a scratch file with
  `python3 scripts/ch_secret.py base44 <file>` and delete it after the final verify.
  Setup and key ownership: `T-tools/02-workflows/cs-cx-cloud-environment.md`. Never print a credential or write one into the repo. The Base44
  token must be generated from this app's own API page (Settings → API → Create access
  token); a token made elsewhere 403s with a workspace-membership error.
- **Delegation discipline.** The Slack/Gong/Pylon scans run as separate, independently
  verified sub-tasks. A sub-task gets only the inputs its job needs. Never give a sub-task
  Base44 write credentials, the HubSpot token, or Slack posting unless that is its job.
- **Permission-mode shapes:** Base44 calls start with `curl`; HubSpot scripts run as
  `python3 <script> https://api.hubapi.com`; no compound `X && curl && rm` chains.

## 1. Pull data

### Sigma (`config.sigma`, SQL in `queries/`)
1. `python3 scripts/render_queries.py --run-date <date> --scratch <dir>` writes
   `<name>_<MMDD>.sql` for every query in `config.sigma.queries`, with the window filled in.
2. Send each rendered file's SQL to Sigma **exactly as written** (query type `datamodel`,
   `config.sigma.data_model_id`). Never rewrite or "improve" a query during a run; query
   changes are commits to `queries/`, reviewed like any other logic change.
3. Save each result as `{"columns", "rows"}` JSON under that query's `output` name.
   Oversized results (q6 always) auto-save to a tool-results file: copy and parse it, never
   re-emit it.

| Query file | Element | Returns, per rollup company |
|---|---|---|
| `q1_groups.sql` | `groups_bi` | decisioned, approved, median TTD approved/declined, median UW hours, overrides, QA. Window on decisioned-at. |
| `q2_volume.sql` | `groups_bi` | submitted count in the window vs the equal prior window. |
| `q3_support.sql` | `support_cases_bi` | PM cases and tech escalations, Pylon cases only, with user-type, deleted, and pet exclusions. |
| `q4_companies.sql` | `companies_bi` | is_da, summed unit counts, statuses, churn risk, any_churned. Current state, no window. |
| `q5_revenue.sql` | `revenue_actual_bi` | revenue by quarter of the run year. |
| `q6_idmap.sql` | `companies_bi` | rollup id and child company ids (one row per child; see `config.sigma.q6_note`). |
| `q7_funnel.sql` | `user_application_funnel` | funnel rows and completed applications, for people whose first event is in the window. |
| `gate6_unit_crosscheck.sql` | `unit_counts_bi` | live units per rollup for the run month, from a source independent of q4 (validation gate 6). |

**Rollup renames (every run).** Diff each q-file's names against the record's
`resolved_name_sigma` set. Translate any name in `config.sigma.rollup_renames` (or a new
variant you find) to the record's name before merging. A rename makes joins miss silently.
Add every new rename you find to `config.json` in the same commit as the run.

**Pet exclusion (q3).** The `NOT (...)` clause in `q3_support.sql` is the filter. If it is
ever edited, every sub-condition stays wrapped in `COALESCE(..., FALSE)`: without it, a NULL
sub-category silently excludes ordinary tickets. Never treat the category alone as the pet
signal; it is a grab-bag.

**Gate 6 prep.** Apply the same renames to `gate6_unit_crosscheck` and keep it for
validation gate 6. Never trust q4's own unit output; a multi-portfolio rollup can silently
return one child's count instead of the sum. The cross-check reads Unit Counts BI (one row
per company per month), so it is independent of q4. If it returns no rows, the run month's
unit counts have not loaded yet: stop and DM Will rather than skip the gate.

### HubSpot — `scripts/hubspot_pull.py`, then `scripts/match_hs_accounts.py`
Pull companies with `findigs_company_id` and `config.hubspot.company_properties`, plus
churned=true companies. `total_units_all` = cumulative booked units, New Logo + Expansion,
upsells excluded (booked, not live). Build `hs_account_match.json`. Matching runs in stages
(exact normalized name → phrase containment → unit-confirmed token overlap → 2-token
containment); the churned pool is stricter (exact or ≥2 distinctive shared tokens). The
matcher's ALIAS/BLOCK table is extended, never trimmed. Keep `hs_object_id` per entry. Matched units must be identical to
the baseline's `total_units_sold_hubspot` week over week; audit every change. Match counts
should be near `config.hubspot.expected_matched_*`; unmatched accounts carry forward with a note.

### Gong — `scripts/gong_pull.py`
Pull slim calls for the window, then build `gong_strategic_rows.json` per matched account:
calls_90d, review-call titles (`config.gong.review_call_title_regex`), exec titles seen
(`config.gong.exec_title_regex`), sample titles.

### Sentiment scans (sub-tasks): Slack, Gong, Pylon
Batch inputs use `resolved_name_sigma` as the account key, never `input_name`. Never trust a
sub-task's output at face value: spot-check against the raw source.

- **Slack** (`config.slack_scan`, fields `result_fields`): classify Positive/Neutral/Negative
  from in-window messages only. Police window violations: any rationale citing a pre-window
  date gets the channel re-read and a corrected classification / thin_sample /
  message_count / rationale in `slack_overrides.json`.
- **Gong sentiment:** accounts with enough call briefs; fields `config.gong.sentiment_result_fields`.
- **Pylon** (`config.pylon`): resolve the exact account_id by domain/name (fuzzy name search
  cross-contaminates), then pull issues in `config.pylon.open_states` created in the window.
  - **Friction** = PM-side platform problems: outages, access failures, escalations, config
    bugs. NOT applicant-servicing tickets or implementation-coordination threads.
  - **PM-only:** drop `user_type == "applicant"`. `user_type` is set on form/chat_widget
    tickets; Slack conversations are PM-side by construction; for emails without it, the
    requester's email domain matching the client domain → PM. Report
    `config.pylon.result_split_fields`.
  - Drop every pet ticket (any signal in `config.pylon.pet_signals_union`); never surface a
    pet-ticket title in an alert card. Never filter by `config.pylon.never_filter_by_fields`
    (portfolio product flags, not ticket classifiers). Never scan
    `config.pylon.catch_all_accounts_never_scan`.
  - Band with `config.pylon.friction_bands`. Re-search not-found accounts by full Sigma name
    before accepting a carry-forward. **Re-verify every Negative** by re-pulling the account's
    issues and re-adjudicating each cited title. Corrections (classification and total, not
    just titles) go in `pylon_overrides.json`. Result rows may use either key in
    `config.pylon.result_account_found_keys`.

## 2. Merge and rescore — `scripts/merge_refresh.py --run-date <date>`

The script reads `config.scoring` and applies these rules:

- Metric values from `config.scoring.metric_formulas`; bands from
  `config.scoring.metric_bands`; FS accounts' approval always Yellow. Which rows are scored:
  `config.scoring.scored_notes`.
- Pillar value = weighted average of rows with data, weights renormalized. Pillar band:
  `config.scoring.pillar_red_row_rules` when reds exist; otherwise value band from
  `config.scoring.pillar_value_bands`, capped at Yellow.
- Composite = `config.scoring.pillar_weights` average of pillar values, renormalized; band by
  `config.scoring.composite_rules`. Values are never flattened by overrides.
- **HubSpot override:** when `client_health_score_override` is Yes, the band mirrors
  `client_health_rating`. It wins over the CSM flag; flag a real conflict to Will.
- **`red_reasons`** is band-dependent and never empty for Yellow/Red. Every DA composite
  carries `methodology` and `segment_used`.
- **FS accounts:** composite anchored on the CSM flag (`config.scoring.band_to_score`);
  rebuild only when the flag band changed. Metrics still refresh (display only).
- **CSM flag refresh:** update where changed; preserve "Corrected" entries; never blank a
  flag because Sigma went empty; mixed "Churned, X" on an active rollup → hold, note for CSM.
- **Churn:** HubSpot churned=true, status not contradicting, AND zero live units AND zero
  window submissions (or SF risk exactly "Churned" + zero live + zero activity). A churned
  name-matched child never churns an active rollup. Never auto-churn a future churn_date.
  Mixed-status rollups are parked, not single-banded. Franchise-style umbrella rollups stay
  scored individually. Churned accounts carry forward.
- **Sentiment:** ccs = Slack + Gong, most-negative-wins, `thin_sample` only when every
  component is thin, apply `slack_overrides.json`; Pylon
  replaced where found (apply `pylon_overrides.json`), else carry forward with a staleness note.
- **Strategic Gong rows** refresh only where the baseline band is non-null AND fresh matched
  calls exist. Meeting cadence, multi-thread, and revenue MoM carry forward.
- **Units:** `total_units_sold_hubspot` ← `total_units_all`; sold-vs-live = live / sold ·100.

**Validation gates (all must pass, or stop and DM Will):**
1. Threshold reproduction (also pre-flight step 6).
2. Algorithm unit test: recompute `config.validation.pilot_accounts_unit_test` from baseline
   inputs; must reproduce exactly.
3. Join coverage ≥ `config.validation.join_coverage_floors`.
4. No composite band count moves more than `config.validation.structural_diff_max_band_move`;
   audit every flip as methodology vs data.
5. No all-zero metric columns.
6. Every account's live units equal the gate-6 cross-check sums. On mismatch, use the
   cross-check number and re-pull q4; never push q4's own number.

## 3. Push and verify

1. Write the UTC timestamp to `ts.txt` in the scratch directory (own command). If the
   redirect lands it elsewhere, move it: `archive_history.py` reads the scratch copy and
   silently writes `computed_at: null` without it.
2. Payload: `{"cache_key", "computed_at", "accounts"}` per `config.target`. Only
   `config.target.persisted_fields` survive; extra top-level keys (`band_counts`,
   `band_flips`) are silently dropped. The dashboard derives flips from `prior_band != band`.
3. `curl` PUT to `<api_base>/apps/<app_id>/entities/<entity>/<record_id>` with the Bearer token
   (or no `Authorization` header when Base44 is a network secret).
4. **A 200 is not proof.** GET the record back and diff: computed_at, band counts, and 3–4
   spot values must match what you sent. Any mismatch → DM Will, stop.
5. Delete the token file.

## 4. Archive history (required) — `scripts/archive_history.py --run-date <date>`

Writes `history/<run-date>/` (baseline, pushed record, wow_diff, overrides, matches, Gong
rows, the exact scripts and config used), appends `history/wow_history.json`, regenerates
`wow_history.csv`, and emits the slim snapshot payload. Verify `computed_at` is non-null.

Then `scripts/enrich_payload.py <payload.json> <history/wow_history.json> <owner_map.json>` recomputes `account_manager`/`csa` (owner map), `prior_band`,
`weeks_red`, and `band_history` (never carried forward). POST the snapshot record
(`config.target.snapshot_cache_key_prefix` + date), re-PUT the enriched overview so it is the
newest record, and LIST the entity to confirm both. If the dashboard misrenders after the
snapshot POST, DELETE the snapshot and report.

## 5. Report — `O-output/cs-client-health-scoring/<date>_weekly-refresh-report.md`

Band distribution and WoW deltas; every flip with a one-line reason (methodology vs data);
CSM flag changes and contradictions; verified sentiment overrides and client intel;
staleness notes; standing holds.

## 6. AM Slack alerts — `scripts/build_alerts.py --scratch <dir>`

Uses the last two runs in `wow_history.json`, `config.alerts.owner_source_of_truth`, and
`hs_account_match.json`. The owner map (built from the CS Health Score xlsx "Overall Summary"
tab) is ownership truth, not live HubSpot `csm_owner`. Card blurbs are plain-language
translations of `red_reasons`, never metric-key dumps. Individual cards for `config.alerts.negative_transitions`, kudos
cards for `config.alerts.kudos_transitions`, one still-Red digest. Post to
`config.alerts.slack_channel_id` in order: header → alert cards → kudos → digest. The alerts
file is the dedupe ledger. Never post a prior week's batch after a newer run exists.
Accounts with no owner go out untagged as "owner unresolved".

**Routing:** follow `config.failure_routing`. The channel only ever sees successful runs.

## Standing definitions

- TES = technical escalation share, never "tenant experience score".
- Units sold (booked, HubSpot `total_units_all`) vs live (Sigma current month).
- Match HubSpot by `findigs_company_id` where possible; name matching exists only because
  Sigma rollup names lack the id.
