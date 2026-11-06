# customer-crazy-carl

Findigs Customer Success / Customer Experience automation. Home for the Findigs Hub
(Base44) CS/CX dashboard refreshes and future CS work: churn, support, renewals,
upsell/expansion, client health.

## Status

| Workstream | Dashboard (Base44 entity) | In this repo | Cloud routine |
|---|---|---|---|
| Client Health | `AccountHealthCache` | Yes | Not yet |
| Implementations | `ImplementationsCache` | Not yet | Not yet |
| Support Metrics | `SupportCache` | Not yet | Not yet |
| Churn Analysis | `ChurnCache` | Not yet | Not yet |

## Layout

- `.claude/skills/<name>/SKILL.md`: the runnable procedure for each refresh.
- `O-output/<project>/`: scripts, reference data, weekly reports, and run history.
- `T-tools/02-workflows/`: decision history and incident logs behind each skill.

Paths match the original local project ("The Reserve") so skills run unchanged.
Run scripts from the repo root, or set `REPO_ROOT`.

## Secrets

No credentials are stored here. See `CLAUDE.md` and `T-tools/02-workflows/cs-cx-cloud-environment.md`.
