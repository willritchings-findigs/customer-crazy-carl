# Churn Analysis weekly refresh: 2026-11-16

Client Health record used: computed 2026-11-16T15:05:52Z (22 Red).

## Headline numbers

| Metric | Before | Now |
|---|---|---|
| True churn accounts | 264 | 264 |
| True churn ACV | $10,357,706.61 | $10,357,706.61 |
| True churn ACV, YTD | $4,258,464.25 | $4,258,464.25 |
| At Risk accounts | 21 | 22 |
| At Risk ACV | $4,917,289.50 | $4,917,289.50 |
| Total ACV tracked | $19,550,424.67 | $19,550,424.67 |

Failure to Launch (shown live on the page from is_ftl): 114 accounts, $4,275,428.56.

## At Risk changes (synced to Client Health Red)

- None left
- Added: Sentral ($0.00; HubSpot 159374131925 via Client Health match (A-exact); 9 Closed Won deals summing $308,218.80; AM Natalie Jamnik)

## New churns

- None added this week

## Candidates not added (70)

HubSpot says churned=true but the page doesn't list them. To add one, put its HubSpot ID in `config.new_churns.approved_additions` (with a note) by commit.

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
- Hershey Real Estate (166658707175): churn date 2025-06-24, status Prospect: churn date 2025-06-24 is older than 30 days
- New Horizons Housing (166647377656): churn date 2025-06-03, status Prospect: churn date 2025-06-03 is older than 30 days
- Sunrise Fountains Apartments (166598847221): churn date 2025-05-28, status Prospect: churn date 2025-05-28 is older than 30 days
- Cross Properties (166682192621): churn date 2025-05-22, status Prospect: churn date 2025-05-22 is older than 30 days
- ...and 45 more, all listed in plan_1116.json in the history folder

## Failure-to-Launch candidates (propose-only): 0

- None

## Standing data checks (not changed automatically)

- Churned on the page but HubSpot status is Live/Onboarding/Pilot: 22
- Churned on the page but no longer churned=true in HubSpot: 0

## Flags

- At Risk Sentral: 9 Closed Won deals summing $308,218.80; pushed as $0 until approved (add 159374131925 to config.at_risk_acv_overrides)

## Gates

- ok   recompute reproduces the live record from its own accounts
- ok   churned 378 -> 378 (+0 added, none removed)
- ok   At Risk 22 = Client Health Red 22
- ok   At Risk moved by 1 (limit 8)
- ok   no duplicate HubSpot company IDs 
