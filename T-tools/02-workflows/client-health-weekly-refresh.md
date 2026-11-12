# Client Health Weekly Refresh — Runbook

> **⚡ 2026-09-08: this pipeline is now packaged as a skill — invoke `/client-health-refresh`**
> (`.claude/skills/client-health-refresh/SKILL.md`, with the validated scripts in its `scripts/`
> folder: `merge_refresh.py` scoring engine + validation gates, `hubspot_pull.py`, `gong_pull.py`).
> The skill is the executable spec (incl. the empirically validated thresholds, the count-driven
> pillar floor rules, the FS approval Yellow-cap, the metrics-row PMS at weight 3, join-coverage
> guards, and the churn zero-activity guard). **This runbook is the decision history + context —
> every incident, who decided what and why, and the worked examples that justify each rule.**
> If you're executing the refresh, read the skill. If you're trying to understand *why* a rule
> exists, or recalibrating a threshold, read here.
> **Units source changed 2026-09-08 per Emma:** `total_units_sold_hubspot` now = HubSpot company
> property `total_units_all` ("Total Units Sold (All)" = cumulative booked units, New Logo +
> Expansion), replacing the deal-level `units__c` sum described in item 7 below.
> **AM Slack alerts (2026-09-14 per Emma):** negative band flips + new Reds alert the owning AM
> in #p-account-health (**C0B4QMETZ52** — Emma switched from the dedicated channel same day);
> improvements get a kudos card (same owner tag); stagnant Reds get one grouped digest.
> Owner SOT = CS Health Score xlsx via `O-output/cs-client-health-scoring/owner_map.json`.
> Builder: skill `scripts/build_alerts.py`; first batch review-first, then auto-post.
> **WoW history archive (2026-09-08 per Emma):** every run stores full record + diff + a slim
> per-account snapshot in `O-output/cs-client-health-scoring/history/` (`wow_history.json`/`.csv`).
> **Base44 auth scheme changed 2026-10-28 (Will):** Base44 now issues personal access tokens
> only, sent as `Authorization: Bearer <token>` — the old `api_key: <key>` header every script
> originally used now 401s/403s. See "Base44 auth scheme change" below for the full incident.
> **Delegation discipline added 2026-10-28 (Will), after an incident the same day** — see
> "Delegation discipline incident" below. Any sub-task delegated during a run must be scoped
> narrowly: no write-capable credentials unless writing is literally its job.

**Cadence:** every Monday morning. Will (or a scheduled nudge) kicks it off in a Claude Code session in The Reserve with: *"run the weekly client health refresh"* → invoke the `/client-health-refresh` skill.

**Cloud routine (2026-11-06):** "Client Health Refresh" (`trig_013GADddMEg9RbhmMmdZK5LZ`), repo
`customer-crazy-carl` branch `main`, Default environment, Mondays 9:00 ET (an hour after GTM
Dashboard Update and hubspot-hygiene-scan). Connectors named explicitly: Sigma, Pylon, Slack,
HubSpot. First cloud run succeeded 2026-11-06 (pushed, verified, posted); schedule enabled the same day, first scheduled run Monday 2026-11-09. No human review gates (Will, 2026-11-06):
the validation gates and read-back verify are the only checks; success posts straight to the
channel, any stop posts to `#gtm-automation-log` (replaced the failure DM, Will 2026-11-12). On success it pushes, commits
history and the report to `main`, and posts to `#p-account-health`; any stop posts to `#gtm-automation-log`
(push notification if Slack is down). Credentials: `cs-cx-cloud-environment.md`.
**Target:** Base44 `AccountHealthCache` (app `6a01dddd52a74acb4fd153bd`, record `6a834cf871d5a0ff1897bfca`, base URL `https://findigs-growth-hub.base44.app/api`). The live dashboard is `findigs-growth-hub.base44.app/cx/client-health` — it renders whatever this record holds; display logic lives in the Base44 builder, never in this pipeline.
**Established:** 2026-09-03, per Emma ("set to re run every monday") after Alex assumed on the 9/2 call that the hub "refreshes." Reference implementations of the scoring rules live in `O-output/cs-client-health-scoring/` (`ref_phase4_rollup_and_churn.py`, `ref_phase5_contextual_fields.py`).

## What refreshes weekly (data only — never methodology)

1. **Platform & Product Metrics rows** (DA accounts): median TTD, UW decision time, approval rate, override rate (DA-only), QA%, support ticket ratio, TES%, volume trend (trailing-90 vs prior-90, `GROUP_IS_SUBMITTED=true`) — all from Sigma Core (Data Model), direct `datamodel` queries (never the QBR workbook workaround). Groups BI element `xv3TuuWX8Z`, Support Cases BI `Gz0-jqrI1V`, Companies BI `VWI1PYJyy-`. Known query gotchas: QA filter is `ILIKE '%QA%'` (not `'%-QA'`); ticket ratio excludes `CASE_USER_TYPE ILIKE '%applic%'/'%guarant%'/NULL`; resolve companies via ILIKE-pattern mapping on `ROLLUP_COMPANY_NAME`, never exact-string IN() (trimmed-suffix accounts drop silently). Any metric reading 0% for everyone = query bug until proven otherwise (3+ past occurrences).
2. **Revenue Trend (quarterly, contextual, unscored)**: Revenue Actual BI (dataModel `d8c49faf-458b-4407-bdc3-85a9fbefb609`, element `VDO-u_D7p-`), `SUM(FINDIGS_REVENUE_AMOUNT)` by rollup company by `DATE_TRUNC('quarter', REVENUE_AT)`. Write into `metrics.revenue_trend_quarterly` (current + prior quarters; label the in-progress quarter partial with its through-date; QoQ% compares the two most recent COMPLETE quarters only). `band` stays null forever — revenue trend does not factor into scoring (Emma, 9/3; Alex, 9/2).
3. **Pylon ticket tone** (DA accounts): exact `account_id` via `search_accounts` (never name-partial search — cross-contamination), states new/waiting_on_you/waiting_on_customer/on_hold, trailing 90d, PM-friction title/tag filter, 0=Positive / 1-2=Neutral / 3+=Negative. Two per-Emma exclusions (details + field traps in the skill): **PM-only sentiment (2026-09-22)** — only property-manager-filed tickets count (`user_type` field; applicant tickets route to the internal "Applicant Account (DO NOT DELETE)" catch-all, never scan it or "Pet Reviewer <> Support"); **pet-verification tickets are never friction (2026-09-21)** — identify by issue category/sub-category/Pets tags/titles, NOT the `is_pet_verification` boolean (that's a portfolio product flag, true on every ticket from pet-enabled clients).
4. **Slack component of client_communication_sentiment**: re-read each matched account's `#p-*` channel (match list + channel IDs cached inside each account's `client_communication_sentiment.slack_component`; full original match set in the 2026-09-02 session batches). Parallel subagents fine — but verify a sample of their claims against raw channel content before merging (standing rule: subagents have fabricated/skipped before; validate counts, spot-read 2-3).
5. **Gong component**: domain-matched calls, trailing 90d, classify from Gong's own AI `content.brief` (3-tier), never keyword matching. Combine with Slack via **most-negative-wins** into `client_communication_sentiment` (Negative < Neutral < Positive). Gong/Pylon/Slack sentiment is scored for DA accounts ONLY — FS accounts get the field as context, never in their composite.
6. **Churn status**: pull HubSpot companies `churned=true` (paginate to `total`), normalized-name match against the 268. Apply `band: "Churned"` ONLY where `account_status__c` does not contradict (Live/Onboarding = contradiction → flag for Emma, don't apply). Rule extension (2026-09-04, per Emma): the SF Churn Risk column (Sigma Findigs Customers workbook, surfaces as `csm_qualitative_risk_flag` = "Churned") ALSO counts as a churn source when the account has zero live units AND zero trailing-90 platform activity — that combination outweighs a stale "Live" status or an old "still using" note. Two hard exceptions: a FUTURE-dated churn_date is never auto-churned until the date passes (Morgan, 2026-12-31), and multi-entity rollups with mixed child statuses (flag reads "Churned, Green") are never single-banded (PF Holdings; the Real Property Management franchise umbrella). Currently applied: Elme Communities, Ebner Properties, Sound City Realty, RPM North Point (Slack-sourced; HubSpot flag still unset), 33 Realty Management (2025-11-10), Keyway Property Management (2025-01-01, Merged/Acquired — HubSpot record is "Meybohm Bridges DBA Keyway"), Foundation Property Management (SF-flag-only, no HubSpot churn record — churn-process owner should backfill date/reason). Parked for humans: Evernest, RPM Agile, RPM Three Bridges (flag Churned but mid win-back, scored Yellow — intentional), West USA Realty, PF Holdings (mixed rollup — one churned 2023 prospect child, Landmark Square, pollutes the flag string; 9 live Green children). Resolved 2026-09-14 per Emma: Morgan → Churned now (contract-end date 12/31, moving to BoomPay); RPM umbrella row removed from the record entirely (franchises still scored individually — don't resurrect); Peak resolved by the staged matcher (exact record, 2,410 units).
7. **Contextual fields**: total-vs-live units (HubSpot closed-won `units__c` via findigs_company_id match ÷ Sigma live units — NOTE, corrected 2026-09-04 per Emma: `units__c` is the account's TOTAL portfolio unit count, not incremental units sold; the pct = share of portfolio live on Findigs; >100% means a stale HubSpot total or rollup-scope mismatch; the JSON keys still say "sold" for frontend-binding compatibility, read them as "total"), application completion, groups submitted vs expected, PMS `slack_integration_signal` annotations (flag/annotation layer only — never changes the platform-based PMS band).

## Scoring invariants — do NOT change without Emma/Alex sign-off

- Row scoring: Green=100 / Yellow=50 / Red=0, weighted average per pillar, weights from the v8 rubric xlsx (`O-output/cs-client-health-scoring/2026-08-11_v1-client-health-scoring-rubric_v8.xlsx`), re-normalized to rows with real data. Pillar floor gates: 1 red row → pillar Yellow, 2+ → pillar Red; **0 red rows → value band capped at Yellow** (adopted 2026-09-14, Emma sign-off: a pillar can't be Red without a Red row — kills the all-Neutral-sentiment→Red artifact that let a Negative→Neutral improvement worsen a composite; 26 pillar bands + 13 composites corrected and re-pushed same day). Null/missing data = unscored/excluded, never Red (business goals, KPIs, NPS stay unscored portfolio-wide).
- Overall composite (`composite_score_partial`): two-level rollup. Value = weighted average of pillar VALUES at Platform 50 / Strategic 30 / Sentiment 20 (re-normalized to non-null pillars); never flattened to match the band. Band: 2+ Red pillars → Red; 1 Red pillar → Yellow; Green requires ALL included pillars Green; otherwise Yellow. `csm_qualitative_risk_flag` = Red is a hard override → overall Red regardless. FS accounts: composite stays churn-risk-anchored only; platform pillar unscored until documented account goals exist.
- Volume trend bands: current thresholds (drop <20 Green / 20-40 Yellow / >40 Red) are flagged too generous — pending Alex's call on the proposed <10/10-25/>25. Whichever is in the live data's methodology notes at run time is the law.
- Churned accounts: `{value: null, band: "Churned", churn_date, churn_reason, source, methodology}` — no pillar rollup.
- **HubSpot `client_health_score_override` precedence (2026-09-22 CX ask, corrected 2026-09-29).** A company-level Yes/No flag, distinct from the CSM churn-risk flag row. When Yes, band mirrors the paired `client_health_rating` field directly — not a hardcoded Red as first shipped 9/22 (that version was live in code but silently never fired for any real account, since nobody had the flag set yet, so the bug shipped invisibly for a week until real accounts started using it 9/29, and most turned out Yellow, not Red). When this conflicts with the CSM churn-risk flag (e.g. flag says Red via Sigma, HubSpot override says Yellow), HubSpot override wins — Donna's judgment call 9/29 (more specific, more deliberately-set signal), not explicitly confirmed by Emma; flag a real conflict case to her if one comes up. Real accounts observed 9/29: Harbor Group Parent (Red), Beztak/Oakwood/Highmark Residential/Brick and Timber Parent (all Yellow) — Beztak and Brick and Timber had been Red on pillar/CSM-flag merit alone, so the override *lowered* their band, proving this isn't just a "confirm it's bad" rubber stamp.
- **Canonical pilot accounts** for validation gate 2 (algorithm unit test): Maymont, Hudson, Evernest, Harbor, Beztak, and others accumulated as edge cases are found — recomputing pillars + composites from baseline inputs must reproduce these exactly.

## Push + verify (every run)

1. Recompute locally against a fresh GET of the live record; **structural diff before pushing** — only expected fields may change.
2. Abort and report to Will WITHOUT pushing if: overall band distribution moves more than ±25 accounts (`config.validation.structural_diff_max_band_move`; ±25 confirmed as the standard 2026-11-05) in any color vs last run; any account's data looks like a query bug (all-zero metric, 2x+ population swing); or a subagent verification fails.
3. Push: `PUT /entities/AccountHealthCache/6a834cf871d5a0ff1897bfca`, header `Authorization: Bearer <token>` (see "Base44 auth scheme change" below — this was `api_key:` before 2026-10-28). Bash command must START with `curl` (settings.json allowlist is prefix-matched: `Bash(curl *findigs-growth-hub.base44.app*)`).
4. Verify with a GET: account count, `computed_at`, spot-check 3 accounts (one DA, one FS, one Churned).
5. Report to Will: distribution + week-over-week deltas, band flips with one-line reasons, anomalies flagged (not fixed), data-source failures skipped (a failed source means carry forward last week's values for those rows with a staleness note — never zero them out).

## Sigma queries

**Where they live.** `.claude/skills/client-health-refresh/queries/*.sql`: q1–q7 plus the
gate-6 cross-check. Dates are placeholders (`{window_start}`, `{window_end}`, `{prior_start}`,
`{prior_end}`, `{revenue_year}`, `{month_start}`, `{next_month_start}`). `scripts/render_queries.py --run-date <date>` fills them in.
Before 2026-11-05 the queries were never saved; each run's agent rewrote them from prose.

**Provenance.** Recovered on 2026-11-05 from the 2026-10-28 run's sub-agent transcripts. Each
query ran 3–6 times that day with one identical SQL text, so these are exactly what produced
the 10/28 numbers. Verified: rendering the templates for 2026-10-28 reproduces that SQL
token-for-token for all eight queries. Every column they use was confirmed present in live
Sigma on 2026-11-05.

**Changing a query.**
1. Edit the `.sql` file. Keep placeholders; no hardcoded dates.
2. Document any new column in `config.json` (`sigma.elements.<key>.named_columns`, or
   `columns` for opaque IDs). `contract_check.py` fails any run whose queries use an
   undocumented column, and fails any run where a documented column has disappeared.
3. Run one no-push dry run and compare the affected metric against the prior week.
4. Note the change and its expected effect on the dashboard in the weekly report.

**Window boundaries.** The window is `>= window_start AND <= window_end` against timestamp
columns. A date literal compares as midnight, so the run date itself is excluded and each
window is exactly 90 × 24 hours. The prior window ends the day before `window_start` with the
same edge, so the trend comparison is like for like. The gap day (`prior_end` itself) is not
counted in either window.

### Review decisions (Will, 2026-11-05)

| # | Item | Evidence | Decision |
|---|---|---|---|
| 1 | **Gate 6 was not independent of q4.** Same element, same `SUM`, same `GROUP BY`, so they could not disagree. | One-time comparison on 2026-11-05: Unit Counts BI (`Y4dN5LDwns`), November rows summed by rollup, matched q4's current-month units on all 692 rollups (388,457 units both sides). | **Switched.** `gate6_unit_crosscheck.sql` now reads Unit Counts BI for the run month (`{month_start}` to `{next_month_start}`). No rows means the month hasn't loaded: stop and post the failure to `#gtm-automation-log`. |
| 2 | **q3 had no case-system filter**; the Support Metrics dashboard filters to Pylon (`"dyE5lEXjiZ" = 'pylon'`). | Re-checked 2026-11-05 for the 10/28 window: one value, `pylon`, 17,448 cases, 382 TES. | **Filter added.** No score change today; keeps the two dashboards aligned if another system appears. |
| 3 | **q7 cohort = first event in the window**, not submission in the window. | 92,814 completed vs 94,808 by submit date (+2.1%); 3,105 submitters started before the window. | **Kept.** Same group in numerator and denominator, so the completion rate is a true rate; matches every past run. |
| 4 | **q6 is large** (~222K characters, one row per child company) and always overflows the tool output limit. | Every 10/28 execution auto-saved to a file. | Works as is; aggregate to one row per rollup only if it becomes a problem. |
| 5 | **Window edge** (see above). | Run date excluded; prior windows have the same edge. | Accepted as consistent; documented only. |
| 6 | **Structural-diff limit ±20 vs ±25.** 25 began as a one-run exception on 2026-09-08 and was copied forward. | — | **±25 is the standard.** Runbook and config agree. |

## Standing context

- **TES = technical escalation share**: % of PM support tickets with `SUPPORT_CASE_HAS_TECH_ESCALATION=true` (Support Cases BI), segment-aware thresholds per the v8 rubric (ENT ≤3 / 3–6 / >6; MM <2 / 2–5 / >5). It is NOT "tenant experience score" — if any label expands it that way, the label is wrong.
- Kairos Pylon raw open-count drifts from fresh pulls (21 vs 40 same-day) — count methodology inconsistency; classification is robust to it, number is soft.
- PMS card (and its Slack annotation) exists on only ~28 hand-built accounts.
- Highmark: `pilot_phase` flag active (Alex 9/2); no closed-won deal in HubSpot so sold-vs-live renders "— / —".
- Renters Warehouse + Bridge placeholders are intentionally out of scoring; SFR OpCo removed by Emma's instruction. Don't resurrect.
- 2026-09-08 run results for reference: G132/Y95/R31/Churned7/None3 (from G127/Y79/R52/C7/N3), 42 flips, computed_at 2026-09-08T14:15:30Z.

## Incident log

Chronological record of bugs found, decisions made, and why each standing rule in the skill
exists. If you're recalibrating something or wondering "why does it do it this way," start here.

**2026-11-12 — Gong strategic rows: committed builder; Findigs staff never count.** No builder
for `gong_strategic_rows.json` was ever committed; every run since 9/14 had a sub-agent rewrite
the call-to-account matching. Matched accounts went 57, 60, 51, **0** (10/05: every account's
review-cadence and exec-sponsor bands silently carried forward), 35, 34, 27, 29, 29, although
the Gong window was fixed at 6/10–9/08 until 10/28, so most swings were logic changes, not
calls. The 10/28 version also credited exec titles of Findigs attendees, and Monday 11/09's
version credited non-exec titles ("Project Coordinator") from another company on Maymont's
calls. Decision (Will and Alex Schaper, 2026-11-12): Findigs employees are never counted or
scored; the row measures whether Findigs' account team is engaging the client's
decision-makers. Fix: `scripts/build_gong_strategic.py`, rules in `config.gong`; safety stop
on zero matches or a drop below half of the prior run. Gong's party "affiliation" is
Internal/External/Unknown, not a company name, so earlier "name matching" never matched
anything: matching is by HubSpot company email domain, plus `account_domain_aliases`.
Verified: on the 11/06 and 11/09 windows it matches the same 29 accounts as those runs and
changes no dashboard band (the Findigs CEO attended two matched accounts' calls; both already
had client execs).

Same day: the exec-title pattern in config had no word boundaries, so "coo" matched
"Coordinator" and "cto" matched "Director"; coordinators earned exec credit (from at least
11/06). Fixed to whole words; any "Director" title now counts (was only "director of"). Effect on
the dashboard: Aulder Property Management's exec-sponsor band goes Green -> Red on the next run
(its only "exec" was an Operations Coordinator). Aliases added (Will): Maymont Homes <-
brookfieldproperties.com (parent company), Western Wealth Parent <- westernwealthcapital.com.

Still open (with Alex, not decided): count-based exec rule (2+ distinct client execs = Green),
a weekly Gong-based multi-threaded score (that row is frozen from a one-time HubSpot pull), and
expiry for bands that carry forward when no calls match (9 exec-sponsor bands still date from
9/28). `client_attendees` / `exec_attendees` counts are already in the rows for that decision.

**2026-11-06 — Sigma results were always hand-copied; now proven against Sigma.** The first
cloud run stopped safely before pushing: the Sigma connector returns results under its size
limit inline, so saving q1–q5, q7 and gate 6 meant the agent retyping ~200 rows each, which it
refused to do. Checking the 10/28 transcripts showed every past local run had done exactly that
(a helper agent wrote q1 as 19K characters by hand) with no check against Sigma. The `describe`
files for the contract check were hand-condensed for the same reason. Fix:
`scripts/sigma_verify.py`. For every saved file Sigma computes a one-row fingerprint (row
count, non-null and distinct counts, lengths, a character fingerprint of every text value,
sums, true counts, each value tied to its account) and the script compares it with the same
fingerprint computed from the file. Tests: an untouched auto-saved file passes; a dropped row,
one changed character, two accounts' values swapped, a +1 on one number, a flipped boolean,
and a blanked value all fail. Column checks now use `LIMIT 0` probe queries (Sigma rejects a
missing column by name; no data returned), so nothing is retyped there either. Comparing the
10/28 files against Sigma today fails, but only because Sigma's data has moved since (row and
name terms match; counts drifted), so those copies could not be proven after the fact.

**2026-09-08 — silent dict-vs-list loader bug.** A merge-time type mismatch produced 0 merges
across the whole run with no error raised. This is why validation gate 3 (join coverage floors)
exists — it would have caught this immediately.

**2026-09-08 — Yellow accounts rendered blank on the dashboard.** The composite payload didn't
carry `red_reasons` consistently band-to-band, so the dashboard's "Why yellow/red/green" section
had nothing to show for some Yellow accounts. Fixed by making `red_reasons` contract
band-dependent (see the skill's §2 "Composite payload contract") and requiring it non-empty on
every Yellow/Red account.

**2026-09-14 — HubSpot matcher summed multiple fuzzy-matched records onto one account.**
Caught by the "validate against baseline, audit every change" rule: Harbor showed
21655+1300 combined, Peak showed 2410+711+2960 combined, both wrong. This is why
`hs_account_match.json` validates against the prior week's matched units and treats any
week-over-week change as something to audit, not accept silently.

**2026-09-14 — the 0-red-rows-caps-at-Yellow pillar rule, and why it was needed.** Before this
rule, all-Neutral sentiment or all-Yellow metric rows could score 50 and land in a value-band
Red, which made quiet (not actually bad) accounts render Red, and could make a real
Negative→Neutral sentiment *improvement* worsen a composite (this happened to Beztak).
Emma's sign-off adopted "a pillar can never band Red without at least one actual Red row."
Adopting it corrected 26 pillar bands (17 sentiment, 9 strategic) and moved 13 composites
Red→Yellow in one re-push; those 13 are marked `kind: methodology-0red-cap` in that day's diff
and were intentionally excluded from triggering Slack alerts (a methodology correction, not a
real-world change).

**2026-09-14 — Pylon Negative overturn audit.** A spot-check re-adjudication overturned 3 of 8
Negative classifications from one subagent batch: a "Findigs x <acct> Sync" MEETING INVITE had
been counted as a data-sync problem; "Application Remodel - Live Tomorrow" launch coordination
had been counted as friction; one cited title didn't exist on the account at all. The same pass
also caught an undercount the other direction — Sentral: the agent reported 2 frictions, a
direct pull showed 59 open issues with 5 real frictions including an urgent escalation, and the
account correctly stayed Negative/Red. This incident is why the skill requires spot-verifying
EVERY Negative, not a 2-3 account sample.

**2026-09-21 — subagent batches built from `input_name` instead of `resolved_name_sigma`.** 6
accounts' Slack/Gong/Pylon scan results (Beztak, Highmark, Hudson, Imagine, Kairos, WPM)
silently failed to join into the merge. The only visible symptom was a suspiciously quiet diff
and a pylon `n_touched` count below the account count — nothing crashed. This is why batch
inputs must use `resolved_name_sigma` as the join key, always.

**2026-09-21 — Sigma rollup rename hid a real band flip.** Three rollups had been renamed on
the Sigma side (see the skill's §1 Sigma rename note for the current mapping) without the
record's `resolved_name_sigma` being updated, so that week's q-file joins silently missed those
three accounts and carried forward stale platform metrics — including a real Beztak Yellow→Red
flip that didn't show up until the rename was found and fixed. This is why every run diffs
q-file names against the record's `resolved_name_sigma` set before merging.

**2026-09-21 — the 9/14 AM alert batch was approved, went stale, and was scrapped unposted.**
A newer run existed by the time anyone went to post it. Posting a stale batch after a newer run
exists would ping AMs about a week-old state that's already been superseded — this is why the
rule is "rebuild from the newest transition, never post a prior week's batch."

**2026-09-21/22 — Pylon sentiment false positives: pet tickets and applicant tickets.** Pet
Verification / pet-screening tickets were being counted as PM friction (dropped one from
Highmark, 14→13, once excluded) and applicant-filed tickets were polluting PM-sentiment counts.
Fixed by the PM-only sentiment rule (`user_type` field) and the pet-signal union described in
the skill's §1 Pylon section. A follow-up deterministic re-audit on 2026-09-22 found zero
counted frictions were actually pet tickets and zero applicant tickets had leaked onto client
accounts, confirming the fix held — no classification changes, that week's record and alert
batch stood as-is.

**2026-09-22 — the `is_pet_verification` boolean trap.** This field looked like it should mean
"this ticket is about pet verification," but it's actually a portfolio-level product flag —
true on every ticket from any pet-enabled portfolio, including a pure credit-override ticket
that had nothing to do with pets. Same trap class as `is_decision_assist` / `is_cra_portfolio` /
`is_termwise`. Never filter tickets by it.

**2026-09-28 — q4 multi-portfolio undercount, the most damaging bug class found.** That week's
q4 pull undercounted `unit_count_live_latest`/`unit_count_live_current_month` for 44 of 267
accounts (16%), always the same way: a multi-portfolio rollup came back with only ONE child
portfolio's unit count instead of the SUM across all of them — Beztak showed 1,361 (just its
"Muirwood" child) instead of the true 21,539. Exactly where in the pipeline the collapse
happened (the Sigma query itself vs. a Python step) was never conclusively pinned down. It's
dangerous specifically because it fails silently: the wrong number is always a real, plausible,
nonzero count, so nothing looked broken, and none of validation gates 1-5 catch it (a
single-child substitution doesn't move composite bands since units are unscored/contextual, and
doesn't zero out a metric column). It was only caught because Emma spot-checked one number
against her own knowledge of the account. Her instruction after the fix: check for this
specific bug before every future push, not just when something looks suspicious — which is now
validation gate 6, mandatory every run regardless of whether anything looks wrong. The verified
cross-check query was confirmed twice, and independently matches Sigma's own Unit Counts BI
element `Y4dN5LDwns` — a useful second reference if the GROUP BY query itself is ever in doubt.

**2026-09-29 — pet-ticket SQL NULL-safety trap.** `CASE_SUB_CATEGORY IN (...)` evaluates to
NULL (not FALSE) when the column itself is NULL, which silently poisons an `OR`-chain used
inside `WHERE NOT (...)` under SQL's three-valued logic (NULL is treated as "exclude"). This
wrongly swept ~1,200 ordinary non-pet tickets with a null sub-category out of the count as if
they were pet tickets. Caught by cross-checking the filtered total against an independently
built `by_category` breakdown — the two disagreed by exactly the poisoned-NULL count. Fixed by
wrapping every sub-condition in `COALESCE(..., FALSE)` before OR-ing them together.

**2026-10-28 — Base44 auth scheme change.** Base44 stopped accepting the `api_key: <key>`
header every script had used since this pipeline's first run (2026-09-08) and now requires
`Authorization: Bearer <personal access token>` on every call. Discovered when Will's first
replacement Base44 credential (a personal access token, format-correct) got a 401 under the old
header but worked cleanly as a Bearer token — meaning the auth *scheme* itself had changed, not
just the specific key. A second credential swap then hit a different failure (403,
workspace-membership) because the token hadn't been generated from the specific target app's
own API settings screen, which is apparently required for a token to be properly scoped to
reach that app. All three push/verify/snapshot calls in the skill now use `Authorization:
Bearer` as the standing convention.

**2026-10-28 — delegation discipline incident.** During the first live run under Will, the
orchestrating agent delegated a narrow sub-task — "persist these Sigma query results to files"
— to a forked helper agent. The helper instead executed and pushed the *entire* weekly refresh
to the live Base44 record on its own initiative, well outside its assigned scope, and this went
undetected until the orchestrator independently re-verified the live record afterward (which is
also what caught the 2026-09-21-style Sigma rename bug recurring that same week — see above).
The fix adopted is structural, not just an instruction to "stay narrow": a sub-task given no
write-capable credentials in its context cannot push to Base44 regardless of what it decides to
do on its own. Scope every delegated sub-task's inputs and credentials to exactly what its
stated job requires, nothing more.
