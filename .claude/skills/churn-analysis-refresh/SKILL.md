---
name: churn-analysis-refresh
description: Run the weekly CX Churn Analysis dashboard refresh end-to-end — sync At Risk to this week's Client Health Red list, add newly churned HubSpot companies under the auto-add rule, list everything else as candidates, recompute every total from the account list, gate it, push to Base44 ChurnCache, verify the readback, archive, and post to Slack. Use on every scheduled routine run or when Will says "run the churn refresh".
---

# Churn Analysis weekly refresh

Procedure only. Every ID, rule and threshold lives in `config.json` and `scripts/`. Why, decisions
and the incident log: `T-tools/02-workflows/churn-analysis-weekly-refresh.md`.

**Never publish the Base44 app builder.** Data goes through the API only.
**Never remove a churned account or change a reason by hand.** The run only syncs At Risk and adds
churns that pass the rule in `config.new_churns`; everything else is a candidate in the report.
**Slack:** success posts to `config.slack.success_channel_id`; any stop or failure posts the step
and the error to `config.slack.failure_channel_id` instead. Never DM anyone.

Run every script from this skill folder as `python3 scripts/<name>.py ... --run-date <date>
--scratch <dir>` (`<date>` = today UTC, `<MMDD>` its month and day).

## 0. Pre-flight

1. **Connectors.** Slack answers one cheap call (find tools by server name, `+Slack` or exact
   `select:` names; if missing, wait ~20 seconds and retry up to 3 times). If Slack is down, send
   the failure note as a push notification.
2. **Credentials.** HubSpot and Base44 come from network secrets when `CH_PROXY_AUTH` lists them
   (send no `Authorization` header). Otherwise write the Base44 token with
   `python3 ../client-health-refresh/scripts/ch_secret.py base44 <scratch>/.b44` and send
   `-H "Authorization: Bearer $(cat <scratch>/.b44)"`; delete the file after the final verify.
   Never print a credential. Base44 calls start with `curl`.
3. **Baseline and Client Health.** `curl` GET
   `<api_base>/apps/<app_id>/entities/<entity>/<record_id>` for `config.target` into
   `baseline_<MMDD>.json`, and for `config.health_source` into `health_<MMDD>.json`.

## 1. Plan

`python3 scripts/sync.py https://api.hubapi.com`. It stops if Client Health is older than
`config.health_source.max_age_days` (run Client Health first). It writes `plan_<MMDD>.json`:
At Risk removals and additions (with HubSpot ID, ACV and how each was found), new churns that pass
the auto-add rule or are in `approved_additions`, candidates not added and why, Failure-to-Launch
candidates (propose-only), and flags.

## 2. Build and gate

`python3 scripts/build_record.py`. It first proves the recompute reproduces the live record from
its own accounts, then applies the plan and checks: no churned account removed, At Risk equals
Client Health Red, At Risk moved by no more than `config.validation.max_at_risk_change`, no
duplicate HubSpot IDs. Any FAIL: stop and post the failing lines to the failure channel.

## 3. Push and verify

1. `python3 scripts/push_verify.py payload` writes `put_body_<MMDD>.json`.
2. `curl -X PUT -H "Content-Type: application/json" --data-binary @put_body_<MMDD>.json` to the
   `config.target` record URL.
3. **A 200 is not proof.** `curl` GET the record into `readback_<MMDD>.json`; `python3
   scripts/push_verify.py verify` must PASS. On FAIL: post the output to the failure channel and
   stop; do not re-push blindly.
4. Delete the token file.

## 4. Report, archive, Slack

1. `python3 scripts/report.py` writes `O-output/cx-churn-analysis/<date>_weekly-refresh-report.md`,
   archives the run under `O-output/cx-churn-analysis/history/<date>/`, and writes
   `slack_success_<MMDD>.txt`.
2. Commit the report and history folder (no credentials) and push.
3. Post the Slack text, unchanged, to the success channel.

Dry run: stop after step 2 and run `python3 scripts/report.py --dry-run`.
