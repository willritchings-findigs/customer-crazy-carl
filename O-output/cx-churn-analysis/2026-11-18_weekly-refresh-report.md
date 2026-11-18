# Churn Analysis weekly refresh: 2026-11-18

Client Health record used: computed 2026-11-16T15:05:52Z (22 Red).

## Headline numbers

| Metric | Before | Now |
|---|---|---|
| True churn accounts | 264 | 264 |
| True churn ACV | $10,357,706.61 | $10,357,706.61 |
| True churn ACV, YTD | $4,258,464.25 | $4,258,464.25 |
| At Risk accounts | 22 | 22 |
| At Risk ACV | $4,917,289.50 | $4,917,289.50 |
| Total ACV tracked | $19,550,424.67 | $19,550,424.67 |

Failure to Launch (shown live on the page from is_ftl): 114 accounts, $4,275,428.56.

## At Risk changes (synced to Client Health Red)

- None left
- None added

## New churns

- None added this week

## Churn date updates (1)

Effective churn dates re-synced to HubSpot's churn date field (config.hubspot.churn_date_fields).

- Chroma Property Management: 2026-07-31 -> 2026-10-27 (HubSpot churn_date)

## Candidates not added (74)

HubSpot says churned=true but the page doesn't list them as Churned. To add one, put its HubSpot ID in `config.new_churns.approved_additions` (with a note) by commit. Ones marked *on the page as At Risk* stay At Risk until they pass the rule or are approved.

- Harbor Group Management (335497258711): churn date 2026-11-05, status Prospect: churn_reason 'moved to Yardi' is not in the taxonomy *(on the page as At Risk (Client Health Red))*
- Weiss Entities (166553684666): churn date 2026-11-04, status Onboarding: status is Onboarding; churn_reason 'Charges were never configured to post to their ledger. UAT was marked complete in Jira before it was actually finalized. Their Yardi “Apply Now” links stopped redirecting to Findigs, so Findigs received only one application. Refunds, fee discrepancies, and income-verification and fraud-threshold questions piled up in September. Their main contact was out of office for about two weeks and slow to respond. They skipped the 10/16 sync and didn’t answer the reschedule request.' is not in the taxonomy *(on the page as At Risk (Client Health Red))*
- Evernest (345640538863): churn date 2025-09-29, status Live: churn date 2025-09-29 is older than 30 days *(on the page as At Risk (Client Health Red))*
- McCaw Property Management (158245221098): churn date 2026-11-16, status Onboarding: status is Onboarding; churn_reason 'Consolidating leasing tech under Boom.' is not in the taxonomy
- MJW Investments (166645268173): churn date 2026-11-09, status Onboarding: status is Onboarding; churn_reason 'Misunderstanding of how the product could work with their existing process and expectations. They had no internal alignment on their SOP and that lead to further issues with how Findigs works for them.' is not in the taxonomy
- Volker (178672381645): churn date 2025-12-05, status Disqualified: churn date 2025-12-05 is older than 30 days
- Jaqua Realtors (153993774785): churn date 2025-11-25, status Prospect: churn date 2025-11-25 is older than 30 days
- Stone Oak Property Management (158187403996): churn date 2025-11-25, status Prospect: churn date 2025-11-25 is older than 30 days
- Park Creek Apartment (158238046961): churn date 2025-10-16, status Disqualified: churn date 2025-10-16 is older than 30 days
- Dix Road Property Management, LLC (333146986199): churn date 2025-10-02, status Prospect: churn date 2025-10-02 is older than 30 days
- Long & Foster Real Estate (166631863006): churn date 2025-09-26, status Prospect: churn date 2025-09-26 is older than 30 days
- La Colonia Mobile Home Park (166656636657): churn date 2025-09-26, status Prospect: churn date 2025-09-26 is older than 30 days
- United Metro Properties (154088720120): churn date 2025-09-15, status Prospect: churn date 2025-09-15 is older than 30 days
- Britt Lake Apartments (158404824776): churn date 2025-09-15, status Prospect: churn date 2025-09-15 is older than 30 days
- Carden Springs (158404824800): churn date 2025-09-15, status Disqualified: churn date 2025-09-15 is older than 30 days
- Hall of Fame apartments (158226768577): churn date 2025-09-15, status Prospect: churn date 2025-09-15 is older than 30 days
- Carolina Moves (164080213704): churn date 2025-09-03, status Prospect: churn date 2025-09-03 is older than 30 days
- Real Property Management Three Bridges (166658673379): churn date 2025-08-14, status Onboarding: churn date 2025-08-14 is older than 30 days
- APG Living (166656538298): churn date 2025-08-13, status Prospect: churn date 2025-08-13 is older than 30 days
- Sullivan Property Management (166571693759): churn date 2025-07-30, status Prospect: churn date 2025-07-30 is older than 30 days
- Hoban Management (163992148690): churn date 2025-07-29, status Disqualified: churn date 2025-07-29 is older than 30 days
- Bennett Property Management - acquired by PURE (166645194467): churn date 2025-07-29, status Prospect: churn date 2025-07-29 is older than 30 days
- Augusta Rental Homes (166644757196): churn date 2025-07-16, status Prospect: churn date 2025-07-16 is older than 30 days
- VRG Management (166664123107): churn date 2025-07-07, status Prospect: churn date 2025-07-07 is older than 30 days
- Lautrec (166554034879): churn date 2025-07-02, status Disqualified: churn date 2025-07-02 is older than 30 days
- ...and 49 more, all listed in plan_1118.json in the history folder

## Failure-to-Launch candidates (propose-only): 0

- None

## Standing data checks (not changed automatically)

- Churned on the page but HubSpot status is Live/Onboarding/Pilot: 22
- Churned on the page but no longer churned=true in HubSpot: 0

## Flags

- None

## Gates

- ok   recompute reproduces the live record from its own accounts
- ok   churned 378 -> 378 (+0 added, +0 from At Risk, none removed)
- ok   churn date updates applied to churned rows: 1 of 1
- ok   At Risk 22 = Client Health Red 22
- ok   At Risk moved by 0 (limit 8)
- ok   no duplicate HubSpot company IDs 
