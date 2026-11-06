# CS/CX cloud environment and credentials

Decided 2026-11-05 (Will): one dedicated cloud environment for every CS/CX routine in this
repo, holding only CS/CX credentials, with freshly issued keys. Other routines (GTM dashboard,
HubSpot hygiene) keep their own environment and never see these keys.

Source for how cloud environments behave: Claude Code docs, "Cloud environments"
(https://code.claude.com/docs/en/cloud-environments.md), checked 2026-11-06. Scheduled tasks
are a research preview, so re-check this page if something stops working.

## How credentials reach a run

Order of preference, implemented in `.claude/skills/client-health-refresh/scripts/ch_secret.py`:

1. **Network secret (preferred).** Stored on the environment; the cloud proxy adds the
   `Authorization` header to requests for the secret's hosts *after* they leave the session.
   The key is never in the session's environment, files, or transcript, so nothing the agent
   reads (Pylon tickets, Gong calls, Slack) can trick it into leaking the key. Values cannot be
   viewed after saving. Services handled this way are listed in the environment variable
   `CH_PROXY_AUTH`; for those, scripts and `curl` calls send no `Authorization` header.
2. **Environment variable (fallback).** Readable by the agent and by anyone who uses the
   environment. Use only where a network secret doesn't fit (possibly Gong, see below).
3. **Local `.env`** (`Label: value` format). Local runs on Will's machine only.

`python3 scripts/ch_secret.py --check` reports where each credential comes from, never the
value. The contract check (pre-flight) runs the same check and stops on anything missing.

## Environment setup (Will, in the claude.ai UI)

claude.ai/code → environment selector → **New environment**. Keep it **personal** (not
shared): anyone who uses an environment can read its environment variables.

- **Name:** `customer-crazy-carl (CS/CX)`
- **Network access:** Custom, with "Also include default list" checked (GitHub, package
  installs), plus:
  ```
  api.hubapi.com
  api.gong.io
  findigs-growth-hub.base44.app
  ```
  Sigma, Pylon, Slack, Notion, and HubSpot reads through connectors go through claude.ai
  connectors, not this list.
- **Network secrets** (one per service, exact hosts so they never overlap):

  | Secret | Host | Type | Value |
  |---|---|---|---|
  | HubSpot | `api.hubapi.com` | Bearer (header `Authorization`, prefix `Bearer`) | new HubSpot key |
  | Base44 | `findigs-growth-hub.base44.app` | Bearer | new Base44 token |
  | Gong | `api.gong.io` | Username and password: username = access key ID, password = secret | new Gong key |

  Gong uses Basic auth (`base64(key:secret)`). The docs don't confirm that the "Username and
  password" type produces exactly that, so it is verified in the smoke test below. If it
  fails, delete the Gong network secret and use the fallback variables instead.
- **Environment variables:**
  ```
  CH_PROXY_AUTH=hubspot,gong,base44
  ```
  Gong fallback only (and then drop `gong` from `CH_PROXY_AUTH`):
  ```
  GONG_ACCESS_KEY=...
  GONG_ACCESS_SECRET=...
  ```

## Keys to issue (fresh, owned by Will or a Findigs service account)

The handoff keys in The Reserve's `.env` may belong to Emma's accounts and stop working when
her access is removed. Issue new ones; don't copy the old ones into the cloud.

| Service | Where | Scope |
|---|---|---|
| HubSpot | Private app / service key in portal 243635806 | Read only: `crm.objects.companies.read`, `crm.schemas.companies.read` (property check) |
| Gong | Gong admin → API → access key | Read. Check whether Gong offers a read-only key; if not, the key has full API access, which is one more reason to use a network secret. |
| Base44 | The Findigs Growth Hub app's own Settings → API → Create access token | Must come from this app (a token made elsewhere 403s with a workspace-membership error). Check whether it can be limited to this app. |

Record each key's owner and creation date here (never the value):

| Service | Owner | Issued | Rotated |
|---|---|---|---|
| HubSpot | | | |
| Gong | | | |
| Base44 | | | |

## Smoke test (one cloud session in the new environment, before the first scheduled run)

Read-only. Each must pass:

1. `python3 scripts/ch_secret.py --check` → every credential `PASS`, sources as expected.
2. `python3 scripts/gong_pull.py https://api.gong.io probe --run-date <today> --scratch <dir>`
   → `gong auth OK` (proves the Gong secret type).
3. HubSpot: `python3 scripts/hubspot_pull.py https://api.hubapi.com ...` auth line →
   `hubspot auth OK (network secret)`.
4. Base44: `curl` GET of the record with **no** `Authorization` header → 200 and the record.

The first real PUT is proven by the run's own read-back verify (§3 of the skill).

## After the first successful cloud run

1. Update the local `.env` with the new keys (for local runs), or point `CH_ENV_FILE` at a new
   file outside The Reserve.
2. Revoke the old handoff keys in HubSpot, Gong, and Base44.
3. Rotate a key if its owner leaves, or at least yearly: replace the network secret value;
   nothing in the repo changes.
