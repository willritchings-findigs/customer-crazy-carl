---
name: client-health-refresh
description: Run the weekly CS Client Health dashboard refresh end-to-end — pull Sigma/HubSpot/Gong/Slack/Pylon, rescore all 268 accounts under the ratified 50/30/20 methodology, validate against the live record, push to Base44, and produce the week-over-week report. Use every Monday or when Will says "run the client health refresh".
---

# Client Health Weekly Refresh

Rebuilds the `AccountHealthCache` record behind **findigs-growth-hub.base44.app/cx/client-health**.
First full run: 2026-09-08 (this skill encodes exactly what that run did, including every
convention validated against the live record). Companion runbook (history + decisions):
`T-tools/02-workflows/client-health-weekly-refresh.md`.

**Target record**: app `6a01dddd52a74acb4fd153bd`, entity `AccountHealthCache`,
record `6a834cf871d5a0ff1897bfca`, cache_key `health_overview`, base URL
`https://findigs-growth-hub.base44.app/api`. 268 accounts.

**Never publish the Base44 app builder.** Data pushes via API only. Dashboard *display*
changes are delivered as a builder prompt for Will to paste himself (9/3 incident).

## 0. Setup

- Scratchpad only; scripts in `scripts/` next to this file — copy them into the scratchpad
  and run there. Shell cwd resets between Bash calls: always `cd` + run in one command or
  use absolute paths.
- Window: rolling trailing-90d ending today (e.g. 2026-06-10 → 2026-09-08). Use the same
  window string everywhere, including source strings.
- **Credentials** — `T-tools/API Keys and Access/.env`, format `Label: value` (NOT KEY=value).
  NEVER print values. Line 1 = HubSpot Bearer token (44 chars). Line 2 = Gong API secret
  (152 chars). Line 3 = Gong Access Key ID (32 chars) → Gong auth = `Basic base64(key:secret)`.
  Line 22 = Base44 `api_key` → sed-extract to scratchpad `api_key.txt`, **strip surrounding
  quotes and whitespace** (`tr -d '"' | tr -d '[:space:]'` → 32 chars; a quoted key gets
  HTTP 403 "auth_required", which looks like a permissions problem but isn't — hit 9/8),
  **delete after the final GET-verify**.
- **Permission-mode command shapes** (auto-mode classifier is prefix-matched):
  - Base44 calls must literally start with `curl` (`Bash(curl *findigs-growth-hub.base44.app*)`).
  - HubSpot scripts run as `python3 <script> https://api.hubapi.com` (`Bash(python3 *api.hubapi.com*)`).
  - No compound `X && curl && rm` chains around these; timestamp via `date -u +%Y-%m-%dT%H:%M:%S.000Z > ts.txt` as its own command.
- Baseline: GET the live record first → `baseline_<date>.json`. It is the WoW baseline AND
  the law for thresholds/conventions. If anything below disagrees with the live record,
  re-derive from the record and update this skill.
- **Delegation discipline (added 2026-10-28, after a same-day incident).** This skill
  legitimately needs nested delegation — Section 1's Slack/Gong/Pylon batches should run as
  separately dispatched, independently verified subagents, not serially by the orchestrating
  agent alone. But any sub-task delegated along the way (including ad-hoc ones not listed in
  this file, e.g. "just save these query results to a file") must be scoped narrowly on
  purpose: give it only the specific inputs its stated job needs, and do not hand it Base44
  write credentials, the HubSpot private-app token, or Slack-posting ability unless writing or
  posting is literally the task. On 2026-10-28 a sub-agent given the narrow job of persisting
  some Sigma query results instead executed and pushed the entire weekly refresh to the live
  Base44 record on its own initiative, undetected until the orchestrator independently
  re-verified the live record afterward (which is what caught it, plus a real rename-join bug
  — see Section 1's Sigma rename note). The fix is structural, not just an instruction to
  "stay narrow": a sub-task with no write-capable credentials in its context cannot push to
  Base44 regardless of what it decides to do. Scope accordingly before dispatching.

## 1. Pull data

### Sigma (MCP server "sigma": begin_session → query)
Data model `d8c49faf-458b-4407-bdc3-85a9fbefb609` (Core Data Model — always query Core
directly, per memory). Save each result as JSON dict `{"columns"/"note": ..., "rows": [...]}`.
Oversized MCP results auto-save to `~/.claude/projects/.../tool-results/*.txt` — `cp` the
file and parse it; never re-emit the content.

| # | Output | Element | Grain: rollup company name + |
|---|--------|---------|------------------------------|
| q1 | `q1_groups_<date>.json` | Groups BI `xv3TuuWX8Z` (col prefix `inode-3t4SuoA2pU267qM43Rx4jl/`) | decisioned count, approved count, median TTD-hours approved, median TTD-hours declined, median UW hours (col `Ad4D-EI2jp`), override count (`W6x8udeWRR`=Has Decision Override), QA count (decision status ILIKE '%QA%'). Window on decisioned-at. |
| q2 | `q2_volume_<date>.json` | Groups BI | submitted count trailing-90 vs prior-90 (GROUP_IS_SUBMITTED). |
| q3 | `q3_support_<date>.json` | Support Cases BI `Gz0-jqrI1V` (prefix `inode-1dBuhhkgQkWXslu27HE64N/`) | PM cases, TES cases (`aXcJxyR08B`=Has Tech Escalation). CASE_IS_DELETED=false; exclude Case User Type (`EqUUI_mZyt`) NULL / ILIKE '%applic%' / '%guarant%'. **MUST also exclude pet tickets** — see the pet-exclusion filter below. |
| q4 | `q4_companies_<date>.json` | Companies BI `VWI1PYJyy-` (prefix `inode-5OpIcdVfNb9CgO6UIt6Cbk/`) | is_da, `fYbMjAl9NA`=Unit Count Latest, `6pSljhsuv9`=Unit Count Current Month, statuses, `raG5zMHzeS`=Sales Account Churn Risk (SF-sourced; rollups concatenate child values → "Churned, Green"), any_churned. **MUST `GROUP BY ROLLUP_COMPANY_NAME` with `SUM(...)` on both unit columns** — see the mandatory bug below. |
| q5 | `q5_revenue_<date>.json` | Revenue Actual BI `VDO-u_D7p-` (prefix `inode-01S9MnIuLWteAJ8QRq5wee/`) | SUM(FINDIGS_REVENUE_AMOUNT) by 2026 quarter (Q3 partial — note through-date). |
| q6 | `q6_idmap_<date>.json` | rollup name → rollup_id + child ids (GROUP BY alias on first col not honored — opaque ids returned, column order is stable). |
| q7 | `q7_funnel_<date>.json` | User Application Funnel `apKoPbqWa9` (prefix `inode-54xB1eUhLxf1EJucb7r8Xk/`) | funnel rows count, SUM(HIT_SUBMIT). |

**Sigma rollup renames (caught 2026-09-21)**: Sigma-side rollup names drift — 9/21 found three
renamed (current Sigma name ← record's stale `resolved_name_sigma`): "Beztak Properties Parent
Company"←"Beztak Properties Parent", "Kairos Living LLC Parent Company"←"Kairos Living LLC
Parent", "Hudson Homes Management, LLC"←"Hudson Homes Management LLC". A rename makes that
account's q-file joins miss SILENTLY (platform metrics carry forward — 9/21 it hid a real
Beztak Y→R flip until fixed). After pulling the q-files: diff q-file first-column names against
the record's `resolved_name_sigma` set, and for any account whose q-key matches its `input_name`
(or a new variant) instead, TRANSLATE the q-file keys to the record's sigma name before merging.
Consider refreshing `resolved_name_sigma` in the record to the new Sigma names next run.

**Pet-ticket exclusion for q3 (added 2026-09-29, Emma's request)**: Pylon's pet-verification
volume was inflating `support_ticket_ratio_per_100`/`tes_pct`. A ticket is pet-related if:
`CASE_SUB_CATEGORY IN ('pet_verification_dispute','pet_policy_question','pet_fee_refund_request')`
OR (`CASE_CATEGORY = 'pets_disputes_consumer_requests'` AND `CASE_SUB_CATEGORY IS NULL` — verified
by subject sampling: these are real pet tickets, e.g. rabies-vaccine/ESA-letter cases, that never
got a sub-category tag) OR `CASE_SUBJECT ILIKE '%pet%'` (fallback catch-all, verified clean —
no substring false positives like "carpet"/"competitive" found on sampling). **Trap**: the
top-level category `pets_disputes_consumer_requests` is itself a grab-bag — only ~72% of the
tickets filed under it are actually pet-related (the rest are misfiled document-upload /
status-update / cancellation tickets); never treat `CASE_CATEGORY = 'pets_disputes_consumer_requests'`
alone as the pet signal. **SQL NULL-safety trap (caught 2026-09-29)**: `CASE_SUB_CATEGORY IN (...)`
evaluates to NULL (not FALSE) when the column itself is NULL, which silently poisons an
`OR`-chain used inside `WHERE NOT (...)` — SQL's three-valued logic treats that NULL as "exclude,"
so ~1,200 ordinary non-pet tickets with a null sub-category got wrongly swept out as if they were
pets. Wrap every sub-condition in `COALESCE(..., FALSE)` before OR-ing them together, e.g.
`NOT (COALESCE(CASE_SUB_CATEGORY IN (...), FALSE) OR COALESCE(..., FALSE) OR COALESCE(CASE_SUBJECT ILIKE '%pet%', FALSE))`.
Caught by cross-checking the filtered total against an independently-built `by_category`
breakdown — the two disagreed by exactly the poisoned-NULL count, which is what surfaced the bug.
Full support-dashboard-side writeup (SupportCache, a separate Base44 record from this skill's
AccountHealthCache): `M-memory/project_cx_support_scorecard.md`.

**q4 multi-portfolio undercount bug (found 2026-09-28, MANDATORY pre-push check added) — the
single most damaging class of bug found so far, and the least visible.** The 9/28 q4 pull
undercounted `unit_count_live_latest`/`unit_count_live_current_month` for **44 of 267 accounts**
(16%), always in the same direction: any multi-portfolio rollup (Beztak's 106 child portfolios,
Highmark's 74, Maymont's 84, Harbor Group's 69, etc.) came back with only ONE child portfolio's
unit count instead of the SUM across all of them — Beztak showed 1,361 (one child, "Muirwood")
instead of the true 21,539. Exactly where in that week's pipeline the collapse happened (the
Sigma query itself vs. a Python step) was never conclusively pinned down. **This is dangerous
precisely because it fails silently**: the wrong number is always a plausible, real, nonzero
unit count (it's a real child portfolio's real count), so nothing looked broken — no error, no
zero, no crash. None of the 5 validation gates below catch it, because a single-child
substitution doesn't move composite bands (units are unscored/contextual) and doesn't zero out a
metric column. It was only caught because Emma spot-checked one number against her own knowledge
of the account. Emma's instruction after the fix (2026-09-28): **check for this specific bug
before every future push, not just when something looks suspicious.**

**Mandatory step, every run, before merging q4 into the payload**: independently re-derive q4's
unit numbers with a direct, known-correct query and diff against what the week's q4 pull
produced — don't just trust q4's own output. The verified-correct query (confirmed twice on
2026-09-28, matches Sigma's Unit Counts BI element `Y4dN5LDwns` independently):
```sql
SELECT "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" AS rollup_name,
       COUNT(*) AS n_children,
       SUM("6pSljhsuv9") AS sum_units_cur_month,
       SUM("fYbMjAl9NA") AS sum_units_latest
FROM "datamodel"."VWI1PYJyy-"
WHERE "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" IS NOT NULL
GROUP BY rollup_name
```
Run this ONCE (it covers every account in one call, cheap), apply the same rename translations as
q1/q2/q3/q7 (Beztak/Kairos/Hudson/Payton's Place + any newly-caught ones), and compare every
account's `sum_units_cur_month` against what the week's own q4 pull is about to merge in. Any
mismatch = the bug recurred; use the verified query's number, not q4's own. This is now
**Validation gate 6**, below — do not skip it even though it never fails the other 5 gates.

### HubSpot — `scripts/hubspot_pull.py`
`python3 hubspot_pull.py https://api.hubapi.com` → `hs_findigs_companies.json` (all companies
with `findigs_company_id`; props include **`total_units_all`** = "Total Units Sold (All)",
the canonical sold-units field per Emma 2026-09-08: cumulative booked units, New Logo +
Expansion, upsells excluded — booked, not live) and `hs_churned_<date>.json` (churned=true).
Then build `hs_account_match.json` with **`scripts/match_hs_accounts.py`** (adjust date constants,
run in scratchpad). Stages: exact normalized name (RPM/PM/mgmt abbreviations expanded) →
phrase-containment → unit-equality-confirmed token overlap → 2-token full containment; the
churned-companies pool is stricter (exact or ≥2 shared distinctive tokens — a legal-suffix-stripped
generic phrase like "residential leasing management" otherwise matches unrelated churned companies).
The script carries a hand-adjudicated ALIAS/BLOCK table (Team Cadwell→Park Place dba Resolute RDM;
blocks for Carolina Management/Taylor Made/Tower Bridge) — extend it, never delete entries.
It validates against the baseline's `total_units_sold_hubspot` (most matched units should be
IDENTICAL week-over-week; audit every change — 9/14 caught last week's matcher summing multiple
fuzzy-matched records: Harbor 21655+1300, Peak 2410+711+2960). Keep `hs_object_id` in each entry
(HubSpot record links for AM alerts). Expect ~239/268 matched, ~130 with units; unmatched accounts
carry forward with a note.

### Gong — `scripts/gong_pull.py`
`python3 gong_pull.py https://api.gong.io` → pages of slim calls (id/title/started/brief/
parties) for the window. Then build `gong_strategic_rows.json` per matched account
(domain/name-matched parties): calls_90d, review_call_titles (regex: QBR|EBR|business review|
quarterly review|exec review|account review|performance review), exec_titles_seen (regex:
ceo|cfo|coo|cto|chief|president|founder|owner|principal|vp|evp|svp|managing director|
managing partner|director of), sample_titles.

### Subagent scans (Slack sentiment, Gong sentiment, Pylon tone)
Batch inputs from the account map; results as JSON per batch. **Batch-input account fields MUST
be `resolved_name_sigma` (the merge's `aname()` join key), never `input_name`** — 9/21 built
batches from input_name and 6 accounts' scan results (Beztak, Highmark, Hudson, Imagine, Kairos,
WPM) silently failed to join, carrying forward stale sentiment; symptom was a suspiciously quiet
diff + pylon n_touched below account count. **Verification is mandatory**
(memory: Verify Subagent Claims):

- **Slack** (~128 `#p-<company>` channels, 8 batches): classify Positive/Neutral/Negative on
  IN-WINDOW messages only; fields: account/channel/channel_found/classification/thin_sample/
  message_count_90d/rationale/integration_friction/integration_note. Known failure mode =
  **window violations** (classifying from pre-window messages, e.g. a March crisis when the
  window starts in June). Police it: scan results for rationales citing pre-window dates,
  re-read those channels directly, write `slack_overrides.json` with corrected
  classification/thin_sample/message_count/rationale. 9/8 overrides: MGC, Firethorn, McCaw
  → Neutral+thin (evidence was pre-window), Lease Las Vegas → Neutral (unresponsive ≠ negative).
- **Gong sentiment** (accounts with enough briefs, 5 batches): fields account/classification/
  thin_sample/n_briefs_read/rationale.
- **Pylon** (all DA accounts, 4 batches): resolve EXACT account_id via search_accounts by
  domain/name (the fuzzy name filter cross-contaminates!), then search_issues states
  new/waiting_on_you/waiting_on_customer/on_hold, created_after window start. Classify:
  0 PM-friction → Positive, 1–2 → Neutral, 3+ → Negative. Friction = PM-side platform
  problems (outages, access failures, escalations, config bugs), NOT applicant-servicing
  tickets or implementation-coordination threads. **PM-only sentiment (Emma 2026-09-22)**:
  only property-manager-filed tickets feed Pylon sentiment. The ticket custom field
  `user_type` holds "property manager" | "applicant" (set on form/chat_widget tickets;
  unset on Slack conversations, which are PM-side by construction — requesters are client
  staff in the shared channel — and on most emails, where fallback = requester email domain
  matches client domain → PM). Drop `user_type == "applicant"` tickets before counting;
  report the split (`pm_open_count` / `applicant_open_count`) in result rows. Verified
  2026-09-22: applicant tickets route to a dedicated catch-all account "Applicant Account
  (DO NOT DELETE)" (id 1566a785-0478-4391-b046-44798d18e632, 100+ open at any time) —
  NEVER match or scan that account as a client (Kairos 0/69 and Highmark 0/93 open
  in-window tickets were applicant-filed, so client-account scans were already clean;
  the filter is a guard against stray links). Same for the internal account "Pet Reviewer
  <> Support" (ca8c69b8-f92d-45e8-b2db-10c26892943d, findigsops.com, ~60 open Pets Outbound
  tickets at any time) — internal pet-team handoff, not a client. 2026-09-22 deterministic
  re-audit of the 9/21 record under both rules (pet + PM-only): zero counted frictions were
  pet tickets, zero applicant tickets on client accounts → no classification changes, record
  and alert batch stood as-is. Result rows may use `pylon_account_found`
  or `account_found` (merge accepts both). **Pet-verification tickets are NOT friction (Emma
  2026-09-21)**: exclude Pet Verification / pet-screening tickets from PM-friction counts,
  and never surface a pet-ticket title in an alert card (9/21: dropped one from Highmark,
  14→13). Pet signals are a UNION — no single field suffices: `issue_category ==
  pets_disputes_consumer_requests`, `issue_sub_category == pet_verification_dispute`, tags
  "Pets Inbound" / "Pets General" / "Pets Outbound" / "Pet Refund", pet SOP / ESA / PetV
  titles (a real "Pet Verification Dispute" ticket was seen carrying only a "Dispute" tag).
  **TRAP (caught 2026-09-22): the issue boolean `is_pet_verification` is a PORTFOLIO PRODUCT
  flag, not a ticket classifier** — it is true on every ticket from a pet-enabled portfolio
  (a pure credit-override ticket tested true); same class as `is_decision_assist` /
  `is_cra_portfolio` / `is_termwise`. Never filter tickets by it. Accounts the
  agent reports not-found by shortname must be re-searched with the FULL sigma name before
  accepting a carry-forward ("WPM" found nothing; "Willowdale" returned exactly one account).
  **Spot-verify EVERY Negative** (not just 2–3
  random): re-pull the account's issues directly and re-adjudicate each cited friction
  title — 9/14 overturned 3 of 8 Negatives (a "Findigs x <acct> Sync" MEETING INVITE counted
  as a data-sync problem; "Application Remodel - Live Tomorrow" launch coordination counted
  as friction; one cited title didn't exist on the account at all) and also caught an
  undercount the other direction (Sentral: agent said 2 frictions, direct pull showed 59
  open issues with 5 real frictions incl. an URGENT escalation → stayed Negative/Red).
  Overrides in `pylon_overrides.json` may correct classification and total, not just titles.

## 2. Merge + rescore — `scripts/merge_refresh.py`

Copy to scratchpad, adjust the date constants, run. It encodes the full validated engine:

- **Metric formulas**: approval = appr/dec·100; override = ovr/dec·100 (blended);
  qa = qa_count/dec·100; ticket ratio = pm_cases/dec·100; tes = tes_cases/pm_cases·100;
  volume trend = (t90−p90)/p90·100; TTD = worse (max) of approved/declined medians.
- **Thresholds** (live record = law; all reproduce baseline bands exactly):
  approval >50 G / 35–50 Y / <35 R, **FS accounts always Yellow** ("Cap FS at yellow",
  Scoring Matrix V2); override ENT/MM ≤3/3–6/>6 (hard_gate_tripped when >6), SMB always
  Green-when-data; TTD <44h G / 44–60 Y / >60 R (all segments, empirical); QA <15 G /
  15–20 Y / >20 R (empirical); ticket ≤15/15–50/>50 (8/18 recalibration); TES ENT ≤3/3–6/>6,
  MM <2/2–5/>5, SMB <2.2/2.2–4/>4 (provisional, empirical); volume drop <20 G / 20–40 Y /
  >40 R (Alex's replacements still pending).
- **Row weights** (Scoring Matrix V2, ENT/MM/SMB; `rubric_segment_column` picks, STRAT→ENT):
  platform TTD 6/8/9, approval 6/8/9, override 11/12/9, QA 6/6/9, ticket 10/10/13, TES 3/3/5,
  volume 3/3/6, **pms row in `metrics` 3/3/3 (scored)**; revenue unscored since 9/2;
  the rich `qualitative_pillars.pms_integration_depth` object (pilot accounts) is contextual,
  NOT scored. Strategic: goals 8/8/9, KPIs 4/4/2, review cadence 5/4/2, exec sponsor 6/4/2,
  meeting cadence 4/4/2, multi-thread 4/3/2, CSM flag 3/2/2. Sentiment: ccs 6/6/4,
  pylon 5/5/3, NPS 4/4/3 (no data ever).
- **Pillar bands are COUNT-driven when reds exist** (validated on pilots): exactly 1 red row
  → Yellow regardless of value (lift AND cap); 2+ red rows → Red; 0 reds → value band
  (G ≥80 / Y 60–79 / R <60) **capped at Yellow** (`0-red-rows-caps-at-yellow`, Emma sign-off
  2026-09-14): a pillar can never band Red without at least one Red row. Before the cap,
  all-Neutral sentiment / all-Yellow rows scored 50 → value-band Red, which made quiet accounts
  Red and let a Negative→Neutral improvement worsen a composite (Beztak). Adopting it corrected
  26 pillar bands (17 sentiment, 9 strategic) and moved 13 composites Red→Yellow, re-pushed
  same day; those 13 are marked `kind: methodology-0red-cap` in the 9/14 diff and never ping
  Slack. Pillar value = weighted avg of rows with data, weights renormalized.
- **Composite** = 50/30/20 weighted avg of pillar VALUES renormalized to non-null pillars.
  Band: 2+ Red pillars → Red (`2plus_red_pillars`), 1 → Yellow (`1_red_pillar_forces_yellow`),
  all Green → Green (`unanimous_green`), else Yellow (`not_unanimous_green_forces_yellow`);
  CSM flag Red → hard override Red (`csm_hard_override`). Value never flattened.
- **HubSpot `client_health_score_override` (2026-09-22 CX ask, corrected 2026-09-29)**: a
  company-level Yes/No flag, distinct from the CSM churn-risk flag row above. When Yes, band
  mirrors the paired `client_health_rating` field (Green/Yellow/Red — HubSpot's own label is
  "the CSM determined Churn Risk") directly — **not** a hardcoded Red as first shipped 9/22;
  that version was live in code but silently never fired for any real account (nobody had the
  flag set yet), so the bug shipped invisibly for a week until real accounts started using it
  9/29 and most turned out Yellow, not Red. Value is never flattened by this override either
  (same convention as the CSM flag), except on FS accounts where there's no pillar value to
  fall back to and it's set via `B2S[rating]` like the FS branch always does. Pull
  `client_health_rating`/`client_health_score`/`client_health_detail` alongside the override
  boolean (`hubspot_pull.py` PROPS) — the rating is what actually drives the band, the boolean
  alone isn't enough. If multiple HubSpot records match one Sigma rollup and disagree on
  rating, `match_hs_accounts.py`'s `override_fields()` takes the most severe and notes the
  conflict in `hs_health_override_note`. **Precedence when this conflicts with the CSM
  churn-risk flag** (e.g. flag says Red via Sigma, HubSpot override says Yellow): HubSpot
  override wins (checked second, unconditionally overwrites) — Donna's judgment call 9/29
  (more specific, more deliberately-set signal), not explicitly confirmed by Emma; flag it to
  her if a real conflict case comes up on a future run. Real accounts observed 9/29: Harbor
  Group Parent (Red), Beztak/Oakwood/Highmark Residential/Brick and Timber Parent (all
  Yellow) — Beztak and Brick and Timber had been Red on pillar/CSM-flag merit alone, so the
  override *lowered* their band, proving this isn't just a "confirm it's bad" rubber stamp.
- **Composite payload contract (dashboard "Why yellow/red/green" section — learned 9/8 when
  Yellow accounts rendered blank)**: `red_reasons` is BAND-DEPENDENT — Red band lists the Red
  pillars (+ the CSM-override entry when it fired); Yellow band lists Red pillars if any, else
  the Yellow pillars; Green = `[]`. Entry shape `{row, label, detail: "pillar value X/100 --
  <pillar why>", gates_floor: true}`. Also REQUIRED on every DA composite: `methodology`
  (carry forward per account) and `segment_used`. Never ship a Yellow/Red account with empty
  red_reasons.
- **FS accounts**: composite anchored on the CSM churn-risk flag alone (Green→100, Yellow→50,
  Red→0); rebuild only when the flag band changed. Metrics refresh normally (display only).
- **CSM flag refresh** from q4 churn_risk: update where changed; **preserve** any
  "Corrected 2026-09-02" manual entries (Elme, 33 Realty, Keyway, Ebner, RPM Three Bridges);
  **never blank** an existing flag because Sigma went empty (Evernest); mixed "Churned, X"
  on a still-active rollup → hold prior band, note for CSM (Renters Warehouse 9/8).
- **Churn rules**: HubSpot churned=true, status not contradicting, **AND zero live units AND
  zero t90 submissions** (a churned name-matched child must never churn an active rollup —
  Evernest, 24k live units, caught 9/8); OR SF risk exactly "Churned" + zero live + zero
  activity (9/4 extension). Never AUTO-churn a future-dated churn_date — but Morgan
  (churn_date 2026-12-31, moving to BoomPay) was churned by Emma's explicit call 2026-09-14,
  so the rule now applies to future cases only. PF Holdings is the sole parked rollup
  (band None + methodology; its "Churned, Green" flag string comes from ONE dead 2023
  prospect child, Landmark Square — see the 9/14 report). The Real Property Management
  umbrella row was REMOVED from the record per Emma 2026-09-14 (franchises stay scored
  individually) — do not resurrect it. Churned accounts are skipped entirely (carry forward).
- **Sentiment merge**: ccs = fresh Slack + fresh Gong components, most-negative-wins,
  `thin_sample` = all components thin; apply `slack_overrides.json`. Pylon rows replaced
  where found (apply `pylon_overrides.json`); carry forward + staleness note where not.
- **Strategic Gong rows** (review cadence, exec sponsor): refresh only where baseline band
  non-null AND fresh Gong matched calls (never Red-flip an account just because the matcher
  missed it). Meeting cadence + multi-thread are **HubSpot-sourced — carried forward** until
  a HubSpot meetings/contacts pull is added. Revenue MoM carried forward (self-labeled window).
- **Units** (per Emma 2026-09-08): `total_units_sold_hubspot` ← company `total_units_all`
  (keys unchanged for dashboard binding; deal_count nulled); `sold_vs_live_units_pct` =
  live (q4 current-month) / total ·100; unmatched accounts carry prior value + note.
- **Funnel/context**: application funnel + completed apps from q7; groups_submitted_actual
  from q2; revenue_trend_quarterly from q5 (unscored, Q3 partial note).

**Validation gates (all must pass before push)**:
1. Threshold reproduction: banding functions reproduce every baseline metric band exactly.
2. Algorithm unit test: pillars + composites recomputed from baseline inputs reproduce the
   canonical pilot accounts (Maymont, Hudson, Evernest, Harbor, Beztak, …) exactly.
3. Join coverage: q1/q2/q3/q7 name-hits above floors (150/150/120/150 of 268) — catches the
   silent dict-vs-list loader bug that produced 0 merges on 9/8.
4. Structural diff: no composite band count moves > ±25 (audit every flip before accepting;
   the 9/8 audit is the model: categorize methodology-unification vs data, verify drivers).
5. No all-zero metric columns.
6. **q4 unit-count cross-check (added 2026-09-28)**: re-run the verified `GROUP BY
   ROLLUP_COMPANY_NAME, SUM(...)` query above and diff every account's live unit sum against
   what's about to be merged. Abort and re-pull/fix q4 rather than push on any mismatch — see
   the writeup above. This gate exists because a real bug (44/267 accounts undercounted) passed
   all 5 gates above it cleanly.

## 3. Push + verify

1. `date -u +%Y-%m-%dT%H:%M:%S.000Z > ts.txt` (own command) — then MOVE/copy ts.txt into the
   scratchpad: the redirect lands it in the project root, but `archive_history.py` reads
   `<scratchpad>/ts.txt` and silently writes `computed_at: null` into wow_history + the snapshot
   payload when missing (9/21 bug, patched by hand + record re-PUT). Verify computed_at is
   non-null after archiving.
2. Payload: `{"cache_key": "health_overview", "computed_at": <ts>, "accounts": [...]}` (~3.5 MB).
3. `curl -s -X PUT <base>/apps/<app>/entities/AccountHealthCache/<record> -H "Authorization: Bearer $(cat api_key.txt)" -H "Content-Type: application/json" --data-binary @payload.json` — expect HTTP 200.
   **Auth scheme changed 2026-10-28 (Will).** Base44 now issues personal access tokens only — the
   old `api_key: <key>` header Emma's scripts used gets a 401/403 on every call. Use
   `Authorization: Bearer <key>` everywhere a Base44 call is made (this PUT, the GET-verify below,
   and the snapshot POST). The token must specifically be scoped to reach this app
   (`appId 6a01dddd52a74acb4fd153bd`, findigs-growth-hub) — Base44's own API page for the app
   (Settings → API) has a "Create access token" button that generates one correctly scoped; a token
   created elsewhere may 403 with a workspace-membership error even though the header is right.
4. `curl -s GET` the record back with the same `Authorization: Bearer` header; assert computed_at, band counts, 3–4 spot values.
5. `rm api_key.txt`.

## 4. Archive week-over-week history (REQUIRED — scratchpad is ephemeral)

Durable home: `O-output/cs-client-health-scoring/history/` (established 2026-09-08 per Emma).
Run **`scripts/archive_history.py`** (adjust the RUN date constant) after push-verify. It does:

1. `history/<run-date>/` — full archive: baseline JSON, pushed record JSON, wow_diff JSON,
   slack/pylon overrides, hs_account_match, gong_strategic_rows, the exact merge_refresh.py.
2. `history/wow_history.json` — cumulative, keyed by run date: computed_at, band_counts,
   and a slim per-account row (band, composite + 3 pillar values/bands, CSM flag, 7 metric
   values/bands, ccs/pylon classifications, units sold/live/pct) **plus the why fields
   (added 2026-09-14 per Emma): `why` (composite why; churn date+reason for Churned;
   methodology for unscored), `platform_why`/`strategic_why`/`sentiment_why`, and compact
   `red_reasons` [{label, detail}]**. TTD reads `worse_of_two` (the TTD metric has no `value`).
3. `history/wow_history.csv` — regenerated from the JSON, one row per account per run,
   red_reasons joined with " || " — pivots straight into Sheets/Excel.
4. Emits `snapshot_payload_0914-style.json` (slim record body) for the Base44 snapshot below.

**Payload enrichment (added 2026-09-22 for the dashboard's WoW tab + per-account history graph)**:
after archive_history.py (wow_history must already contain the current run), run
**`scripts/enrich_payload.py payload.json <wow_history.json> <owner_map.json>`**. It RECOMPUTES
(never carry forward from baseline — prior_band/weeks_red/band_history go stale otherwise) per
account: `account_manager`/`csa` (owner_map SOT), `prior_band` (previous run), `weeks_red`
(consecutive-Red streak), `band_history` ([{run, band, composite_value}] across all runs — feeds
the account-popout trend graph). The §4 re-PUT below then ships the enriched overview. Base44
schema note: the AccountHealthCache entity persists ONLY `cache_key`/`computed_at`/`accounts` —
top-level `band_counts`/`band_flips` in POSTed bodies are silently dropped (keep sending them;
they'd start persisting if fields are ever added to the entity). The dashboard derives flips from
overview `prior_band != band` and trends from `band_history`, so nothing depends on them.

**Base44 weekly snapshot record (established 2026-09-14, per Emma's "should we push that into
base too?")**: after the main push, `curl -X POST .../entities/AccountHealthCache` with the slim
snapshot body `{cache_key: "health_snapshot_<date>", computed_at, band_counts, band_flips,
accounts: [slim rows]}` (~330 KB vs the 3.7 MB overview). Snapshots exist for ALL four runs —
2026-09-04 and 2026-09-08 were backfilled 2026-09-22. Then **re-PUT the overview record**
so it is also the latest-updated record — that way the dashboard renders the overview whether
its binding filters on `cache_key == 'health_overview'` or just takes the newest record — and
LIST the entity to confirm both records + update order. First snapshot: id
`6aa803f18aa521a2fe43ec9b` (2026-09-14). If the dashboard ever misrenders after a snapshot
POST, DELETE the snapshot record and report. (The 9/8 LIST 403 was the quoted-key bug, not a
scope limit.) O-output stays the system of record; the Base44 snapshots exist so in-dashboard
trend views become a builder-prompt away. Never leave history only in the scratchpad.

## 5. Report to Will (chat + `O-output/cs-client-health-scoring/<date>_weekly-refresh-report.md`)

- Band distribution + WoW deltas; every composite flip with a one-line reason, split
  methodology vs data.
- CSM flag changes list (SF-side edits observed this week) + contradictions worth CSM
  attention (e.g. flag Green while Slack says churned — Out Fast 9/8).
- Verified sentiment overrides + notable client intel from the scans (expansion signals,
  outages, exec escalations).
- Staleness notes: carried-forward rows (meeting cadence/multi-thread, revenue MoM, FS pylon,
  unmatched-units accounts).
- Standing holds: volume thresholds await Alex; NPS no data; window-standardization caveats.

## 6. AM Slack alerts (added 2026-09-14, design confirmed by Emma)

After push-verify + archive, run **`scripts/build_alerts.py <scratchpad>`**. It reads the last two
`wow_history.json` runs, `O-output/cs-client-health-scoring/owner_map.json` (ownership SOT = the
CS Health Score xlsx "Overall Summary" tab, NOT live HubSpot csm_owner — 9/11 finding; one edit
per book shift), and `hs_account_match.json` (hs_object_id → record links). Triggers: negative
band changes (Green→Yellow, Yellow→Red, Green→Red, newly-scored Red, scored→Churned) get
individual tagged cards; improvements (Red→Yellow, Yellow→Green, Red→Green — added per Emma
9/14) get a celebratory kudos card tagging the same owner ("What moved" pillar deltas + "Still
watching" leftovers, or "All pillars Green"); accounts that STAY Red get one grouped "still Red"
digest with weeks-red counts. Blurbs are plain-language translations of the composite
red_reasons (no metric-key dumps — Emma's Slack style rule). Output
`history/<run>/alerts_<run>.json` doubles as the dedupe ledger (`posted` flags; a same-week rerun
skips posted account+transition pairs).

**Posting**: channel = #p-account-health, ID **C0B4QMETZ52** (Emma's call 9/14 — switched from the
dedicated #client-health-alerts C0C1MK83T9U she'd created earlier that day; the old Notion
"Strategic Accounts" digest also posts in #p-account-health). Order:
header line → alert cards (one `slack_send_message` each, own thread per account) → kudos cards →
still-Red digest. The 9/14 batch was approved+held, went stale, and was SCRAPPED unposted (Emma
2026-09-21, ledger marked) — never post a prior week's batch after a newer run exists; rebuild
from the newest transition instead. The 9/21 batch is the first live one (review-first: show Emma
the exact messages, post on her go); after that first approved batch, post automatically and
summarize the sent batch in the weekly report. Never re-ping stagnant Reds individually. Six accounts have no owner in the map
(alert goes out untagged with "owner unresolved"): Capital PM Parent, Ebner, FBM, MS Coast, TPG,
Weiss — worth chasing owners.

## Standing context

- TES = **technical escalation share** (SUPPORT_CASE_HAS_TECH_ESCALATION), never "tenant
  experience score".
- Units sold (booked) vs live: live = Sigma UNIT_COUNTS_BI; sold = HubSpot total_units_all.
- Match HubSpot records by findigs_company_id where possible (memory rule); the name-match
  here exists only because Sigma rollup names lack the id — treat its misses as expected.
- 2026-09-08 run results for reference: G132/Y95/R31/Churned7/None3 (from G127/Y79/R52/C7/N3),
  42 flips, computed_at 2026-09-08T14:15:30Z.
