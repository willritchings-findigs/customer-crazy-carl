# customer-crazy-carl

Findigs Customer Success / Customer Experience automation. Home for the Findigs Hub
(Base44) CS/CX dashboard refreshes and future CS work: churn, support, renewals,
upsell/expansion, client health.

## Status

| Workstream | Dashboard (Base44 entity) | In this repo | Cloud routine |
|---|---|---|---|
| Client Health | `AccountHealthCache` | Yes | Routine "Client Health Refresh" (`trig_013GADddMEg9RbhmMmdZK5LZ`), Mondays 9:00 ET, Default environment. Enabled 2026-11-06 after the first successful cloud run |
| Implementations | `ImplementationsCache` | Yes | Routine "Implementations Refresh" (`trig_01DFjSC1CTbLSncfQLvJ5y8o`), Mondays 11:30 ET, Default environment. HubSpot-sourced since 2026-11-12 (first live push by hand) |
| Support Metrics | `SupportCache` | Yes | Routine "Support Metrics Refresh" (`trig_01PHatwxRHLEMvLiwe7CrCfB`), Mondays 10:00 ET, Default environment. First live refresh 2026-11-12 (run by hand); first scheduled run 2026-11-16 |
| Churn Analysis | `ChurnCache` | Yes | Routine "Churn Analysis Refresh" (`trig_01BBKL3QwcNTXcNoF7b8L1Bp`), Mondays 11:00 ET, Default environment. Dry-run tested 2026-11-12; first live run 2026-11-16 |

## Layout

- `.claude/skills/<name>/SKILL.md`: the runnable procedure for each refresh.
- `O-output/<project>/`: scripts, reference data, weekly reports, and run history.
- `T-tools/02-workflows/`: decision history and incident logs behind each skill.

Paths match the original local project ("The Reserve") so skills run unchanged.
Run scripts from the repo root, or set `REPO_ROOT`.

## Secrets

No credentials are stored here. See `CLAUDE.md` and `T-tools/02-workflows/cs-cx-cloud-environment.md`.
