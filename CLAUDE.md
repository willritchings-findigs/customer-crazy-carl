# customer-crazy-carl: CS/CX automation

Owner: Will Ritchings (will.ritchings@findigs.com). Taken over from Emma Kyber's GTM
Engineering handoff (2026-10). See `README.md` for what's in the repo.

## Rules

- **Never commit credentials.** No API keys, tokens, or `.env` files. `.gitignore`
  blocks `.env`, but check before every commit anyway.
- **A Base44 200 does not mean it saved.** Every push is followed by a fresh GET and a
  field-by-field diff. Base44 silently drops field names that aren't in the entity's
  original schema. Never invent new stored fields; derive new views from existing ones.
- **Base44 auth** is `Authorization: Bearer <token>`. The old `api_key:` header fails.
- **Cloud credentials** live on the Default cloud environment (shared with the other
  routines), as network secrets where possible (the proxy adds the key; the session never
  sees it). Setup, scopes,
  and key owners: `T-tools/02-workflows/cs-cx-cloud-environment.md`.
- **Don't trust a "done" from a script or sub-task.** Verify the result independently.
- **Delegation discipline:** a sub-task gets only the inputs its job needs. Never hand
  it Base44 write credentials, HubSpot tokens, or Slack posting unless that is the job.
- **Three layers per skill.** `SKILL.md` = procedure only. `config.json` + `scripts/` +
  `queries/` = every number, ID, and SQL statement, changed only by commit. The workflow doc in
  `T-tools/02-workflows/` = why, incident log, open items. Never put a threshold, ID, or query
  in a `SKILL.md`, and never let a run rewrite a query on the fly.
- **Every refresh starts with a contract check** (credentials, Base44 fields, Sigma columns,
  HubSpot properties) and stops on any drift.
- Scripts run in place and take `--run-date` / `--scratch`; paths resolve from the repo.
- **Small fixes during an unattended run are allowed** (Will, 2026-11-12). A run may fix a script
  that fails to run for a mechanical reason (syntax or Python-version compatibility, an import,
  a path, a typo) when the fix changes no logic. It must not touch queries, config values,
  thresholds, gates, scoring, labels, or account data, and must never edit a check to make it
  pass. Every gate and the readback verify still have to pass afterwards. Commit the fix as its
  own commit saying what broke and why the change is logic-free, and post that note to
  `#gtm-automation-log` even when the run succeeds. Anything bigger: stop and post the failure.

## Slack routing (all refreshes)

- Successful run: post to the workstream's channel (Client Health, Support Metrics, Churn Analysis, Implementations: `#p-account-health`).
- Any stop, drift, or failure: post to `#gtm-automation-log` (`C0CJ1P9D0HE`) instead, with the step and
  the error (Will, 2026-11-12: this channel replaces every failure DM). Success channels only ever
  see successful runs. If Slack is down, send a push notification.

## Documentation

- Client Health: `docs/client-health/` (published to Notion; see its README). After any
  `config.json` change, run `python3 docs/client-health/build_docs.py` and republish.
- Support Metrics: `docs/support-metrics/`; Churn Analysis: `docs/churn-analysis/` (both published to
  Notion, hand-written: after a rule change in a skill's `config.json`, update the matching doc line in
  the same commit and republish).

## Skills

- `client-health-refresh`: weekly CS Client Health rescore and push to `AccountHealthCache`.
  Decision history: `T-tools/02-workflows/client-health-weekly-refresh.md`.
- `support-metrics-refresh`: weekly CX Support Metrics rebuild and push to `SupportCache`.
  Decision history: `T-tools/02-workflows/support-metrics-weekly-refresh.md`.
- `churn-analysis-refresh`: weekly CX Churn Analysis sync (At Risk, new churns) and push to `ChurnCache`.
  Decision history: `T-tools/02-workflows/churn-analysis-weekly-refresh.md`.
- `implementations-refresh`: weekly CX Implementations rebuild from the HubSpot implementation object,
  push to `ImplementationsCache`. Decision history: `T-tools/02-workflows/implementations-weekly-refresh.md`.
