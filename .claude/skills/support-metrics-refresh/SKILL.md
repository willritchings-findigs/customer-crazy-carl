---
name: support-metrics-refresh
description: Run the weekly CX Support Metrics dashboard refresh end-to-end — pull Sigma (Support Cases BI, User Application Funnel) and a Pylon FCR sample, prove every saved result against Sigma, build the SupportCache record, gate it, push to Base44, verify the readback, archive, and post to Slack. Use on every scheduled routine run or when Will says "run the support metrics refresh".
---

# Support Metrics weekly refresh

Procedure only. Every number, ID, threshold, and SQL statement lives in `config.json`,
`queries/`, `scripts/`, and `shared/sql/`. Why things are the way they are, decisions, and the
incident log: `T-tools/02-workflows/support-metrics-weekly-refresh.md`.

**Never publish the Base44 app builder.** Data goes through the API only.
**Slack:** success posts to `config.slack.success_channel_id`; any stop, drift, or failure posts to
`config.slack.failure_channel_id` (`#gtm-automation-log`) instead, with the step and the error. Channels only see successes.

Run every script from this skill folder as `python3 scripts/<name>.py ... --run-date <date>
--scratch <dir>` (`<date>` = today UTC, `<MMDD>` its month and day). Paths resolve from the repo.

## 0. Pre-flight

1. **Connectors live.** Sigma, Pylon, Slack each answer one cheap call. Find tools by server
   name (ToolSearch `+Sigma`, `+Pylon`, `+Slack`, or exact `select:` names), never by keyword.
   If one is missing, wait ~20 seconds and search again, up to 3 tries. If Slack is down, send
   the failure note as a push notification.
2. **Base44 credential.** If `CH_PROXY_AUTH` includes `base44`, send no `Authorization` header and
   skip the token file. Otherwise `python3 ../client-health-refresh/scripts/ch_secret.py base44
   <scratch>/.b44` and use `-H "Authorization: Bearer $(cat <scratch>/.b44)"`. Never print it.
   Delete the file after the final verify. Base44 calls start with `curl`.
3. **Baseline.** `curl` GET `<api_base>/apps/<app_id>/entities/<entity>/<record_id>`
   (`config.target`) into `baseline_<MMDD>.json`. It must be the `config.target.cache_key` record.
4. **Sigma columns.** `scripts/verify.py probes`, send each `sigma_probe_<key>_<MMDD>.sql` to
   Sigma exactly as written (data model `config.sigma.data_model_id`), save each result under
   its name. A rejected probe = a missing or renamed column: stop.

## 1. Sigma pulls

1. `scripts/render.py` writes `<name>_<MMDD>.sql` for every query in `config.sigma.queries`.
2. Send each file's SQL to Sigma exactly as written. Save each result, exactly as returned, as
   `<name>_<MMDD>.json` (`{"columns": [...], "rows": [...]}`). Large results land in a
   tool-results file: copy that file, never retype it. If Sigma returns a column name that is
   not the query's alias, stop and fix the query (wrap it in a CTE); never rename by hand.
3. **Prove the copies.** `scripts/verify.py checks`, send each `<name>_<MMDD>_check.sql`
   verbatim, save its one-row result as `<name>_<MMDD>_check.json`, then `scripts/verify.py
   compare` must PASS every query. A FAIL means the saved file is wrong: re-save from Sigma and
   re-check. Never edit a check file. This step may be delegated to a sub-task (Sigma read
   access only).

## 2. FCR sample (Pylon)

1. `scripts/fcr_sample.py plan` prints one `search_issues` call per sampled day.
2. Make each call exactly as printed. Each result is saved to a tool-results file: copy it to
   the printed `fcr_page_<k>_<MMDD>.json`. Do not read the page into the conversation.
3. `scripts/fcr_sample.py build` writes `fcr_<MMDD>.json`. It stops if a page is missing or is
   not the planned call.

## 3. Build and gate

`scripts/build_record.py --live <scratch>/baseline_<MMDD>.json`. It prints every gate
(reconciliation of all views to one headline, unknown categories or channels, unclassified
requester share, volume floor, week-over-week change, Needs Attention length) and writes
`support_record_<MMDD>.json` + `build_summary_<MMDD>.json` only if all pass. Any FAIL: stop,
post the failing lines to the failure channel. A new Pylon category stops the run until it is labelled in
`config.categories` by commit.

## 4. Push and verify

1. `scripts/push_verify.py payload` writes `put_body_<MMDD>.json`.
2. `curl -X PUT` that file (`-H "Content-Type: application/json" --data-binary @<file>`) to the
   record URL from step 0.3.
3. **A 200 is not proof.** `curl` GET the record again into `readback_<MMDD>.json`, then
   `scripts/push_verify.py verify` must PASS (every managed field exactly as sent, nothing else
   changed). On FAIL: post the output to the failure channel and stop; do not re-push blindly.
4. Delete the token file.

## 5. Report, archive, Slack

1. `scripts/report.py` writes `O-output/cx-support-metrics/<date>_weekly-refresh-report.md`,
   archives the run under `O-output/cx-support-metrics/history/<date>/`, and writes
   `slack_success_<MMDD>.txt`.
2. Post that text, unchanged, to `config.slack.success_channel_id`.
3. Commit the report and history folder (no credentials, no `.b44`).

For a dry run, stop after step 3 and run `scripts/report.py --dry-run` (no push, no archive,
no Slack).
