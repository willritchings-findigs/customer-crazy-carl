---
name: implementations-refresh
description: Run the weekly CX Implementations dashboard refresh end-to-end — pull every HubSpot implementation record, build the triage queue, stage funnel, active worklist, aging list, recently completed list and capacity view, report HubSpot data gaps, gate it, push to Base44 ImplementationsCache, verify the readback, archive, and post to Slack. Use on every scheduled routine run or when Will says "run the implementations refresh".
---

# Implementations weekly refresh

Procedure only. Every ID, stage and rule lives in `config.json` and `scripts/`. Why, decisions and the
incident log: `T-tools/02-workflows/implementations-weekly-refresh.md`.

**Never publish the Base44 app builder.** Data goes through the API only.
**Never edit HubSpot.** A missing owner, date or health is a gap to report, not to fill in.
**Slack:** success posts to `config.slack.success_channel_id`; any stop or failure posts the step
and the error to `config.slack.failure_channel_id` instead. Never DM anyone.

Run every script from this skill folder as `python3 scripts/<name>.py ... --run-date <date>
--scratch <dir>` (`<date>` = today UTC, `<MMDD>` its month and day).

## 0. Pre-flight

1. **Slack** answers one cheap call (find tools by server name, `+Slack` or exact `select:` names;
   if missing, wait ~20 seconds and retry up to 3 times). If Slack is down, send the failure note
   as a push notification.
2. **Credentials.** HubSpot and Base44 come from network secrets when `CH_PROXY_AUTH` lists them
   (send no `Authorization` header). Otherwise write the Base44 token with
   `python3 ../client-health-refresh/scripts/ch_secret.py base44 <scratch>/.b44`, send
   `-H "Authorization: Bearer $(cat <scratch>/.b44)"`, and delete the file after the final verify.
   Never print a credential. Base44 calls start with `curl`.
3. **Baseline.** `curl` GET `<api_base>/apps/<app_id>/entities/<entity>/<record_id>` for
   `config.target` into `baseline_<MMDD>.json`.

## 1. Pull

`python3 scripts/pull.py https://api.hubapi.com` writes `hs_impl_<MMDD>.json` and `hs_owners_<MMDD>.json`.

## 2. Build and gate

`python3 scripts/build_record.py`. Gates: every record is in a stage listed in
`config.hubspot.stages` (a new or renamed stage stops the run until config is updated by commit),
at least `config.validation.min_records` records, funnel = triage + active, and the open count
within `config.validation.max_open_change_pct` of the live record. Any FAIL: stop and post the
failing lines to the failure channel.

## 3. Push and verify

1. `python3 scripts/push_verify.py payload` writes `put_body_<MMDD>.json`.
2. `curl -X PUT -H "Content-Type: application/json" --data-binary @put_body_<MMDD>.json` to the
   `config.target` record URL.
3. **A 200 is not proof.** `curl` GET the record into `readback_<MMDD>.json`; `python3
   scripts/push_verify.py verify` must PASS. On FAIL: post the output to the failure channel and stop.
4. Delete the token file.

## 4. Report, archive, Slack

1. `python3 scripts/report.py` writes `O-output/cx-implementations/<date>_weekly-refresh-report.md`,
   archives the run under `O-output/cx-implementations/history/<date>/`, and writes
   `slack_success_<MMDD>.txt`.
2. Commit the report and history folder (no credentials) and push.
3. Post the Slack text, unchanged, to the success channel.

Dry run: stop after step 2 and run `python3 scripts/report.py --dry-run`.
