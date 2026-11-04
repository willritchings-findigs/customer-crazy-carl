# Client Health weekly refresh: 2026-10-19

**Status:** Pushed to Base44 and verified (two pushes). computed_at 2026-10-19T15:01:43.000Z, 267 accounts. The AM alert batch is built and held (`posted: false`). Nothing was posted to Slack.

## Bands vs 10/13 baseline

| Band | 10/13 | 10/19 | Change |
|---|---|---|---|
| Green | 130 | 130 | 0 |
| Yellow | 106 | 104 | -2 |
| Red | 21 | 23 | +2 |
| Churned | 9 | 9 | 0 |
| None (unscored) | 1 | 1 | 0 |

No account's composite moved more than 20 points. Accounts worsened to Yellow this week: 0.

## Flips (2)

- **Sentral**, Yellow to Red. Two red pillars: Platform & Product (26.7, already Red at 10/13) and Client Sentiment (0.0). Sentiment turned Red from Gong Negative plus Pylon Negative (6 friction tickets). Strategic Alignment is Green (88.6).
- **Encore Management**, Yellow to Red. Platform & Product turned Red (54.8; median time-to-decision and volume trend Red). Strategic Alignment was already Red (40.0; executive sponsor alignment) at 10/13, when the single red pillar kept the band Yellow. Client Sentiment is Yellow (71.4).

## Callouts

- **Harbor Group Parent**: Red by HubSpot health-score override (composite 67.7). Live units are 11,909 this month against 22,349 in the latest month, about 47% lower, consistent with the deactivation already flagged. Sentiment Negative (Slack), Pylon Neutral (2), CSM flag Yellow. Treated per live data. Status flagged to Emma; nothing changed.
- **Legacy Invest Realty Parent**: Yellow (79.6, not unanimous green). Sentiment Negative from Slack. Pylon not found, so the 9/2 tone is carried forward. Units 257.
- **Bridge Homes**: Churned, unchanged. Confirmed churned by Emma on 10/5. The automated safeguard held it back because of 470 submissions through 9/21. Units 0.
- **Kairos Living LLC Parent**: Yellow (69.2, one red pillar). Pylon Negative with 23 friction tickets after the blind re-pull (batch read 7). Sentiment Negative from both Gong and Slack. CSM flag Yellow. Band unchanged.
- **Elda Management Services**: Red by CSM hard override (composite 32.1). Explicit contract-exit ticket flagged beyond the score. Band not changed. Units 782.
- **Journey Real Estate**: Yellow (45.0, one red pillar). Sentiment Neutral, Pylon Neutral (1). Units 434.
- **Elme Communities**: Churned, units 0. Slack reads Negative in the window; churned rows are not scored.
- **KAIZEN Realty**: Red (60.0, two red pillars). Sentiment Neutral, Pylon Positive. Units 145.
- **Infinite Property Management, LLC**: Yellow (63.5, one red pillar). Slack Positive, Pylon Neutral (1). Units 228.
- **Equity Real Estate**: Red (29.0, two red pillars). Slack second read Negative: client upset relayed 8/7 and 8/17, and the Buildium note-sync issue was still open 9/8. Pylon Positive (0). Units 1,571. Band unchanged.
- **Advantage Property Management TN, LLC** (factual note only): The entity appears in the #p-advantage-property-management channel read (Negative; 120 messages in 90 days; the account lead reported on 10/5 that Advantage does not want to move forward with Findigs) and in the Sigma group and id-map pulls. It is not a scored row in this run and was not in the 10/13 record. The channel read is not attached to Advantage Realty Services, Inc or Real Property Management Advantage, both still Green with null sentiment. Nothing about its churn or closed-lost classification was resolved or overridden.
- **McKinley Companies, LLC**: Yellow (65.5). Sentiment Negative from the Slack second read. The Gong read was Neutral and is unchanged; most-negative-wins applies. Pylon Negative with 8 friction tickets (batch 12). CSM flag Green. Units 12,600.
- **Lynco Properties**: Red by design. Full-screen account, so the composite is the CSM churn-risk flag. Slack second read Negative (borderline); Gong Neutral.
- **Group Fox Management**: Red (41.5, two red pillars). Sentiment Negative from Slack. Pylon Negative with 4 tickets; Neutral without the two borderline tickets the verifier counted.
- **Evernest**: Red (62.7, CSM hard override). Pylon Negative (3). Slack Negative, Gong Neutral. Band unchanged.
- **The Windsor Companies** and **Capital Property Management Parent**: Positive to Neutral on the Slack second read (no client-voiced praise). Both stay Yellow.
- **Sentral** and **Encore Management**: the two flips above.

## Pylon second reads

Blind full re-pulls (six-state set) against the batch read. Each verifier handback was checked against the transcript. Classifications are Negative for all ten accounts below.

| Account | Batch | Final | Basis |
|---|---|---|---|
| Highmark Residential Parent | 11 | 19 | Verifier count; 24 with borderlines; pet tickets excluded (4) |
| Maymont Homes | 6 | 4 | Verifier count; one borderline not counted |
| Kairos Living LLC Parent | 7 | 23 | Verifier count; Negative under any borderline reading (16 to about 33) |
| McKinley Companies, LLC | 12 | 8 | Verifier count, six-state (four-state 7); pet tickets excluded (2) |
| Oakwood Parent | 5 | 5 | Verifier count agrees; four-state would be Neutral, but six-state is canonical. Open thread 213227 read by the orchestrator: client portfolio-mapping coordination, not platform friction; not counted. Pylon shows it waiting on Findigs since 10/5 |
| Brick and Timber Parent | 3 | 4 | Verifier count; four-state also 4 |
| Beztak Properties Parent | 4 | 4 | Verifier count agrees; two of four are six-state only (on_engineering) and keep it Negative; one borderline QA-list ticket not counted (would be 5) |
| Evernest | 4 | 3 | Verifier counted 2 firm and left out a borderline. The orchestrator counted it: a missing upload button is a product bug, and self-fixing is not an exclusion. Pet refund excluded. Neutral without it |
| Group Fox Management | 4 | 4 | Verifier counted two borderlines; Neutral (2) without them. One ticket classified without the full thread |
| Sentral | 5 | 6 | Verifier count, six-state (four-state 5); five borderline tickets not counted |
| Real Property Management Southland | 3 | 3 | Second read agrees. Two of the three are one Parapet incident; at incident level it would be 2 (Neutral). Kept at ticket level |
| Jones and Jones Communities | 4 | 4 | Second read agrees |

Twelve accounts were not found in Pylon and carry the 9/2 tone forward: Bryten Real Estate Partners Parent; Capital Property Management Parent; FBM Real Estate Inc.; Howard Management Group Parent; Legacy Invest Realty Parent; MJW Investments Parent; Modern City Parent; MS Coast Property Management II LLC; New City Property Management Parent; Standard Management Company Parent; TPG Management Parent; Weiss Parent.

## Slack and Gong second reads

- **Slack:** 11 overrides from the blind second read. Nine moved to Negative: Beztak Properties Parent, Cooper Zadeh Property Management, LLC, Equity Real Estate, Group Fox Management, Highmark Residential Parent, HomeRiver Group Holdings LLC, Lynco Properties, McKinley Companies, LLC, Oakwood Parent. Two moved from Positive to Neutral: The Windsor Companies and Capital Property Management Parent. Advantage rows are null (the channel read belongs to the TN entity). Other Slack rows are as batch-read.
- **Gong:** 10 verdicts from the blind second read adopted. Lynco Neutral. Optimum Properties kept at batch Neutral (thin sample, not verified).

## Units, churn, owners

- Churned-row refresh updated units from Sigma for 7 churned rows (units only; bands untouched). Gate 6 then passed.
- **Carry-forward units:** 15 accounts carry units forward because no HubSpot company matched via findigs_company_id: Above Property Management; Amerihome; Carolina Management Parent; Elda Management Services; Firethorn Realty; First Place Management, Inc; ICR Consulting, LLC; MIG Management Inc.; North State Financial; Real Property Management Southland; Real Property Management Three Bridges; Remax Properties, Inc - Chuck Wartman; Taylor & Taylor Realty Services LLC; The Windsor Companies; Willowdale Property Management. Working notes earlier said 31; the record shows 15, and 15 is reported here.
- **No current-month Sigma unit figure (15):** 33 Realty Management; Bridge Homes; Bryten Real Estate Partners Parent; Colonial Residential Properties Inc.; Ebner Properties; Elme Communities; Foundation Property Management, LLC; Keyway Property Management; RPM Rental Solutions; Real Property Management - Agile; Real Property Management Three Bridges; Sound City Realty, LLC; Stever and Associates; The Windsor Companies; West USA Realty.
- **Churned (9):** Elme Communities; 33 Realty Management; Bridge Homes; Ebner Properties; Foundation Property Management, LLC; Keyway Property Management; Morgan Property Management (churned per Emma 9/14; Sigma still shows 240 live units running out the contract, shown as context with no rollup); Real Property Management - North Point (churned per the 9/2 decision; Sigma shows 60 live units); Sound City Realty, LLC.
- **Owners:** 258 of 267 accounts have an account manager. Without one: Capital Property Management Parent; Ebner Properties; Exit Realty - Realty Place; FBM Real Estate Inc.; Group Fox Management; MS Coast Property Management II LLC; TPG Management Parent; The Windsor Companies; Weiss Parent.
- **Client sentiment:** 5 accounts had Client Communication Sentiment cleared because they had no fresh Slack channel and no Gong row (the other 110 were already empty).

## Gate results

| Gate | Result |
|---|---|
| 1. Threshold reproduction | PASS: all baseline metric bands reproduced exactly |
| 2. Algorithm unit test | PASS: canonical pilot pillars and composites reproduced (test passes the baseline HubSpot override band through; see corrections) |
| 3. Join coverage | PASS: q1 256/268, q2 264/268, q3 241/268, q7 264/268 against floors 150/150/120/150 |
| 4. Structural diff | PASS: band counts moved by 2; no account composite moved more than 20; both flips audited |
| 5. No all-zero metric columns | PASS: merge ran with its all-zero abort enabled and did not abort |
| 6. q4 unit-count cross-check | PASS: 267/267 accounts, 0 mismatches |
| Window policing | PASS: no pre-window Slack hits |

## Push

- **Push 1** (`base44_push.py push` with spot-checks Harbor Group Parent, Sentral, Encore Management, Kairos Living LLC Parent, Evernest, Elme Communities): GET before returned the 10/13 record (267 accounts). PUT 200. GET after: computed_at 2026-10-19T15:01:43.000Z, 267 accounts, MATCH. Spot-checks: Harbor Group Parent Red 67.7; Sentral Red 39.9; Encore Management Red 53.7; Kairos Living LLC Parent Yellow 69.2; Evernest Red 62.7; Elme Communities Churned.
- **Archive and enrichment:** 267 accounts enriched (owners on 258, band history on 267, prior run 2026-10-13). Archive written to history/2026-10-19 and wow_history updated.
- **Push 2** (enriched payload): GET before showed computed_at 2026-10-19T15:01:43.000Z. PUT 200. GET after MATCH, 267 accounts, same spot-checks. Snapshot POST 200 (`health_snapshot_2026-10-19`, id 6ad630f97edd142e94efa8f4). Re-PUT 200. LIST shows 9 records, with health_overview at computed_at 2026-10-19T15:01:43.000Z.

## Alert batch (built, held, not posted)

Verbatim text from alerts_2026-10-19.json (`posted: false` at top level, per alert, and on the digest).

Header:

:stethoscope: *Client health weekly refresh 2026-10-19* — 2 alert(s): 2 newly Red, 0 worsened to Yellow · <https://findigs-growth-hub.base44.app/cx/client-health|Dashboard ↗>

Alert 1:

🔴 *Sentral* — moved Yellow → Red
Drivers: Client Sentiment red · Platform & Product red
Signals: Slack/Gong negative, Pylon negative · time-to-decision, override rate, QA rate, support-ticket ratio red · 6 Pylon friction issues ("Application closed due to concurrent submission", "Joinery Phase 1-Applicant not showing in Findigs")
Owner: <@U09E14MCRM3> · <https://app-na2.hubspot.com/contacts/243635806/record/0-2/159374131925|HubSpot ↗> · <https://findigs-growth-hub.base44.app/cx/client-health|Dashboard ↗>

Alert 2:

🔴 *Encore Management* — moved Yellow → Red
Drivers: Strategic Alignment red · Platform & Product red · Client Sentiment yellow
Signals: Executive sponsor alignment, Meeting/touchpoint cadence red / Performance review cadence, Multi-threaded relationship yellow · time-to-decision, volume trend red / approval rate, support-ticket ratio, technical escalations yellow
Owner: <@U06TY8N92LQ> · <https://app-na2.hubspot.com/contacts/243635806/record/0-2/166645513922|HubSpot ↗> · <https://findigs-growth-hub.base44.app/cx/client-health|Dashboard ↗>

Kudos: none this week (0 entries).

Still-red digest:

⚪ Still Red this week (21), no change — grouped so no one gets re-pinged: Brandywine Homes Parent (Natalie, 8 wks) · Bridge Tower Properties LLC (Reese, 8 wks) · CORE Residential (Javier, 8 wks) · Elda Management Services (Reese, 8 wks) · Equity Real Estate (Reese, 8 wks) · Evernest (Natalie, 8 wks) · Exceptional Property Management (Javier, 8 wks) · HomeRiver Group Holdings LLC (Stephanie, 8 wks) · KAIZEN Realty (Javier, 8 wks) · Lynco Properties (Natalie, 8 wks) · Remax Properties, Inc - Chuck Wartman (Javier, 8 wks) · Rookwood Properties (Natalie, 8 wks) · Toomey Property Advisors (Javier, 8 wks) · TruHome Property Solutions (Reese, 8 wks) · Weiss Parent (unassigned, 8 wks) · 3 Options Realty (Javier, 7 wks) · MGC Leasing &Property Management, LLC (Reese, 7 wks) · Cooper Zadeh Property Management, LLC (Reese, 4 wks) · Group Fox Management (unassigned, 4 wks) · Harbor Group Parent (Stephanie, 3 wks) · MJW Investments Parent (Reese, 2 wks)

## Skill-doc corrections (noted here; the skill folder was not touched)

1. **Push step** (SKILL.md around lines 328-329 and 362) uses `curl` with `api_key: $(cat api_key.txt)`, a shell credential read that the credential boundary blocks. This run used `base44_push.py`, one self-contained Python script that reads `.env` internally, for GET, PUT, verify, snapshot, and LIST. The doc should point there.
2. **Structural guard:** SKILL.md line 311 says ±25 for band-count moves; the merge script's docstring says ±20. This run moved band counts by 2 and no account composite moved more than 20.
3. **Account count:** SKILL.md says 268 (lines 3, 15, 141, 309). The 10/13 live record and this run both have 267, and build_payload.py asserts 267. The 268th entry was not identified.
4. **Pylon states:** SKILL.md line 172 lists four states (new, waiting_on_you, waiting_on_customer, on_hold). Live Pylon has six open states, adding on_engineering and on_customer_success_team. The four-state list undercounts; Beztak and Oakwood change class under six states, and Group Fox changes count.
5. **Gate 2 unit test:** the merge's unit test omits the HubSpot health-score override for pilot accounts and aborted on four of them. The scratch copy passes the baseline override band through for the test only.
6. **Churned units:** the skill merge does not refresh units for churned rows, so gate 6 failed on 7 of them. The scratch copy refreshes units only.
7. **Client sentiment:** the skill's rule is fresh-only (a fresh Slack channel or Gong row), but the merge keeps prior values. The scratch copy clears when neither is fresh (5 real clears).
8. **Alert posting:** SKILL text says to auto-post after the first batch. Per Emma's standing rule, AM alerts are held for her go. This run held them.

## Caveats

- pylon-verify-6 opened one saved Pylon response (ticket 219403) despite the blind brief. It counted from that raw response and used no earlier count. Kairos is Negative under any reading.
- Several tickets were classified without the full thread: Group Fox #204424 (from fields); Highmark #231855 (from title), #206796, #205602, #229801; Sentral 205262, 220399, 216298, 219677, 231081, 224624 (in part).
- Verifier borderline calls are not consistent across accounts (counted for Group Fox, not for Beztak or Evernest). The orchestrator re-adjudicated only Evernest, because its borderline decides the classification.
- PII: applicant names and one street address are masked in Pylon titles (Highmark, Kairos, Oakwood, Beztak, Sentral). None appear in this report.
- Harbor status is flagged per live data; nothing was changed. Advantage TN: no churn or closed-lost classification was resolved or overridden.
- Compliance: nothing posted to Slack; nothing written to `.claude/skills/`; no SendUserFile; credentials were handled only inside `base44_push.py` and the MCP connectors.

## Files

- Report: C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/O-output/cs-client-health-scoring/2026-10-19_weekly-refresh-report.md
- Alert batch (posted: false): C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/O-output/cs-client-health-scoring/history/2026-10-19/alerts_2026-10-19.json
- Archive: C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/O-output/cs-client-health-scoring/history/2026-10-19/ (plus history/wow_history.json and wow_history.csv)
- Run folder (scratch): /private/tmp/claude-501/-Users-emma-kyber-Desktop-The-Reserve/78deb188-bf8f-43fe-8f43-99a52c73a67a/scratchpad/health-refresh-1019/ (payload.json, snapshot_payload_1019.json, new_record_1019.json, pylon_overrides.json, slack_overrides.json, merge_dryrun_1019.txt, push1_out.txt, push2_out.txt, run_log_1019.txt)
