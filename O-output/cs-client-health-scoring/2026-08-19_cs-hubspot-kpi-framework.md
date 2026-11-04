# CS on HubSpot — KPI & Success Metrics Framework

Companion to [2026-08-19_cs-hubspot-company-properties.xlsx](2026-08-19_cs-hubspot-company-properties.xlsx) (the property audit). Live-checked against HubSpot portal 243635806, 2026-08-19.

## Two layers — don't conflate them

**Layer A — Data health:** is the CS team actually putting real data into HubSpot? (adoption of the properties just audited)
**Layer B — Customer outcomes:** is the book of business actually healthy? (the real CS scorecard)

A rollout can hit 100% on Layer A and still tell you nothing about customer health if nobody's filling in real values — and Layer B is only as trustworthy as Layer A underneath it. Track both, separately.

## The denominator rule

The full company portfolio is **12,933 records**, but most of that is dead leads, disqualified SMB, and prospects that never converted. The number that matters for CS is the active book: **lifecyclestage = customer, 303 companies** (checked live 2026-08-19).

This is not a small effect — `csm_owner` fill rate is 2.9% portfolio-wide but **93% (282/303) on the active book.** Every Layer A metric below should be scoped to `lifecyclestage=customer` (or a live/DA-enabled subset, matching whatever the v8 rubric already uses) — reporting the portfolio-wide number will make CS look far worse than it is, and reporting the active-book number is also the more honest test of "is CS doing its job in HubSpot."

## Layer A — Data health KPIs

| KPI | How to compute | Current (active book, n=303) |
|---|---|---|
| CSM/CSA coverage | `csm_owner` HAS_PROPERTY / lifecyclestage=customer | 93% — already strong |
| Go-live tracked | `go_live_date__c` HAS_PROPERTY / active book | Not yet rescoped — 4.2% portfolio-wide, needs a real active-book number before judging |
| Product adoption tracked | `findigs_products__c` HAS_PROPERTY / active book | Not yet rescoped — 3.2% portfolio-wide; cross-check against Sigma's `IS_DECISION_ASSIST_ENABLED` (the more complete source today) |
| Strategic plan on file | `strategic_plan_name` HAS_PROPERTY / active book, and recency of `strategic_plan_date` | Essentially unused — 0.47% portfolio-wide. This is the single biggest "is CS actually documenting plans in HubSpot" gap |
| Churn post-mortem completeness | `churn_reason` + `churn_date` both set / `churned`=true | Not yet cross-tabbed — worth a real check before the next churn review |
| Engagement recency | `hs_last_booked_meeting_date` within last 60/90 days / active book | 14.2% filled portfolio-wide (native, reliable where set) |
| Property staleness | `hs_lastmodifieddate` on churn/strategic-plan fields, active accounts only | Not yet checked |

Re-running this table scoped correctly (active book only, all rows) is a natural next step — I did the CSM Owner one live as proof of concept; the rest are estimated from portfolio-wide numbers and should be re-pulled the same way before anyone treats them as a real baseline.

## Layer B — Customer outcome KPIs

**Don't rebuild what exists.** The [[project_cs_client_health_scoring_v1_rubric|v8 CS Client Health Score rubric]] and its [[project_cs_health_score_quarterly_writeback|quarterly Base44 writeback]] already compute a real weighted composite (Platform & Product Metrics, fully live; Strategic Alignment/Governance and Client Sentiment, mostly not) for 20 DA-enabled accounts. That's the canonical engine — HubSpot company properties are a *feed* into it, not a replacement for it.

For the properties audited today, here's what's real vs. aspirational as a Layer B input:

- **Churn rate** — `churned`=true count / (`churned`=true + `lifecyclestage`=customer), trailing period. Real and computable today, but denominators need the same active-book discipline as above.
- **At-risk count** — `at_risk`=true. **Currently 0% populated portfolio-wide** (re-confirmed today, matches the 8/17 finding from the health-scoring project) — this KPI does not exist yet in practice, only in schema. Don't report it until someone actually starts setting the flag.
- **Time-to-value** — `go_live_date__c` → first `strategic_plan_date` or first QBR. Unmeasurable today given both fields are <5% filled on the same accounts.
- **Expansion signal** — `recent_deal_amount` / `hs_num_active_contracts` trend on active accounts. Real, native, reliable — a decent proxy already sitting unused.
- **Engagement cadence** — `hs_last_booked_meeting_date` recency as an interim proxy. The field that's *supposed* to answer this, `total_touchpoints_cs` ("CSM check-ins, portfolio reviews, success conversations"), exists in schema but **has a value greater than zero for zero companies** — nothing writes to it. This is the one gap most worth fixing, since it's exactly the meeting-cadence input the v8 rubric currently has to reconstruct via a bespoke Gong domain-matching pull.
- **NPS** — does not exist as real data anywhere in HubSpot. `nps_check_box__c` reads 98.7% "filled" but only 0.5% (70 companies) are actually `true` — the rest is a default-false flag, not survey responses. `swan_score` is a different, Swan-sourced score, not NPS. If NPS is wanted as a success metric, it needs new instrumentation (a real survey pipeline), not a property fix.

## What's honestly not measurable yet

Carried forward from the health-scoring project, still true as of this audit — these need new data collection, not more querying:
- Business goals / documented KPIs per account
- QBR/EBR cadence beyond the Gong-derived proxy
- Multi-threaded stakeholder relationship depth (`champion_identified` etc. — 0% populated)
- Gong call sentiment and Pylon ticket tone, scored (both have a validated methodology per Tatiana's account-health-weekly-review doc, just not wired into HubSpot or the composite yet)
- Real NPS

## Naming collision to avoid

HubSpot already has a live, pre-existing **`account_health_label`** — a sales/pipeline formula off the worst open deal, unrelated to CS. If the CS composite score ever gets written into HubSpot (vs. staying in Base44), give it a distinctly-named property (e.g. `cs_health_score`), not "Account Health."

## Recommended cadence

- **Quarterly:** full CS Health Score composite refresh — already the established rhythm (Base44 `AccountHealthCache`, `health_overview` record).
- **Weekly, once populated:** at-risk flag review, churn-reason completeness on newly-churned accounts.
- **Ongoing, low-effort:** re-run this same property fill-rate audit (Layer A) every quarter alongside the health-score refresh — it's a meta-KPI for whether CS is actually adopting HubSpot, and it's cheap to check (the same `HAS_PROPERTY` search pattern used throughout this doc).

## Concrete next steps

1. Resolve the two Open Questions on the property sheet (CSM/CSA-as-owner-at-go-live, CSA/CSM distinction) — both have evidence-backed recommended answers in the xlsx's third tab, but they're policy calls for Emma/leadership, not data questions.
2. Decide what replaces the ~15 frozen Salesforce-snapshot fields marked "No" in the audit (Churn Risk, Churn Category, Total Contract Value, Units latest/live, etc.) — or explicitly sunset them.
3. Wire something into `total_touchpoints_cs` — it's the one dead field that's an exact match for a real, named gap.
4. Decide whether the Strategic Plan field cluster (15 properties, <1% filled) is worth continuing as flat company properties, or should become a lighter structure — `strategic_plan_history` is already trying to cram multiple time-stamped snapshots into one text field, which is a modeling smell, not just a low-fill-rate problem.
