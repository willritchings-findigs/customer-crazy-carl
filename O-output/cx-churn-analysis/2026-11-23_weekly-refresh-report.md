# Churn Analysis weekly refresh: 2026-11-23

**At Risk NOT synced:** Client Health record computed 2026-11-16T15:05:52Z is too old or unreadable; At Risk carried over unchanged.

## Headline numbers

| Metric | Before | Now |
|---|---|---|
| True churn accounts | 264 | 266 |
| True churn ACV | $10,357,706.61 | $11,720,417.21 |
| True churn ACV, YTD | $4,258,464.25 | $5,621,174.85 |
| At Risk accounts | 22 | 21 |
| At Risk ACV | $4,917,289.50 | $3,634,447.30 |
| Total ACV tracked | $19,550,424.67 | $19,630,293.07 |

## Foreign write restored

The live record had been rewritten outside this skill (computed 2026-11-23T11:03:33.301Z, updated 2026-11-23T11:03:33.605000): 458 accounts {'Churned': 256, 'Failure to Launch': 180, 'At Risk (Client Health Red)': 22} vs 400 {'Churned': 378, 'At Risk (Client Health Red)': 22} in the last vetted record (O-output/cx-churn-analysis/history/2026-11-18/readback_1118.json). It dropped 16 vetted churned accounts. This run rebuilt from the vetted record and restored it. Most likely source: the Base44 "Daily Churn Cache Refresh" workflow (see the workflow doc). The live copy is archived as foreign_<MMDD>.json.

Failure to Launch (shown live on the page from is_ftl): 114 accounts, $4,275,428.56.

## At Risk changes (synced to Client Health Red)

- None left
- None added

## New churns

- Added: McCaw Property Management (churned 2026-11-16, $79,868.40, Tech Stack Consolidation; churned=true, churn date within 30 days)
- Converted from At Risk (Harbor Group Parent): Harbor Group Management (churned 2026-11-05, $1,282,842.20, Tech Stack Consolidation; churned=true, churn date within 30 days)

## Churn date updates (0)

Effective churn dates re-synced to HubSpot's churn date field (config.hubspot.churn_date_fields).

- None

## Candidates not added (8)

HubSpot says churned=true but the page doesn't list them as Churned. To add one, put its HubSpot ID in `config.new_churns.approved_additions` (with a note) by commit. Ones marked *on the page as At Risk* stay At Risk until they pass the rule or are approved.

- Weiss Entities (166553684666): churn date 2026-11-04, status Onboarding: status is Onboarding *(on the page as At Risk (Client Health Red))*
- Evernest (345640538863): churn date 2025-09-29, status Live: churn date 2025-09-29 is older than 30 days *(on the page as At Risk (Client Health Red))*
- MJW Investments (166645268173): churn date 2026-11-09, status Onboarding: status is Onboarding
- Real Property Management Three Bridges (166658673379): churn date 2025-08-14, status Onboarding: churn date 2025-08-14 is older than 30 days
- Advanced Property Management (166684186348): churn date 2023-12-26, status Churned: churn date 2023-12-26 is older than 30 days
- West USA Realty (338238217958): churn date 2023-04-15, status Live: churn date 2023-04-15 is older than 30 days
- PF Holdings - Landmark Square Apartments (166645513918): churn date 2023-03-23, status Churned: churn date 2023-03-23 is older than 30 days
- Bluewater Property Management (166598771396): churn date 2022-08-18, status Churned: rejected: Bluewater Property Management: confirmed false positive 2026-09-24 (churn stamp cleared 2026-08-07; HubSpot flag never fixed); churn date 2022-08-18 is older than 30 days

## FTL updates from HubSpot Account Status (0 applied, 0 held)

- None applied

## Failure-to-Launch candidates (propose-only): 66

- Jaqua Realtors (153993774785)
- United Metro Properties (154088720120)
- Block Real Estate Services (154307748553)
- Block Multifamily Group (154294967003)
- Britt Lake Apartments (158404824776)
- Carden Springs (158404824800)
- Hall of Fame apartments (158226768577)
- Park Creek Apartment (158238046961)
- Stone Oak Property Management (158187403996)
- Hoban Management (163992148690)
- Twin Cities Home Rental (163768201918)
- Intempus Property Management (164080213695)
- Carolina Moves (164080213704)
- Alliance Property Management (owned by PURE) (163912020696)
- Structure Properties (163995723494)
- Desert Canyon Properties (Aloe PM) (165994911425)
- Liberty Management Inc (166644820676)
- Silver River Property Management (166656834255)
- Long & Foster Real Estate (166631863006)
- Scotia Group Management (166631892701)
- Sullivan Property Management (166571693759)
- GID Investment Advisors (166658658000)
- Bennett Property Management - acquired by PURE (166645194467)
- Augusta Rental Homes (166644757196)
- The Bergen Grand (166644920022)
- Real Property Management Rental Direction (166664085240)
- Western States Lodging & Management (166645206716)
- The PEAK Group Inc (166553648838)
- Cross Properties (166682192621)
- Schroeder Management (166598817496)
- Bertram (166664347380)
- Sunrise Fountains Apartments (166598847221)
- Divvy Homes - acquired by Maymont (166684219121)
- Dix Road Property Management, LLC (333146986199)
- Hershey Real Estate (166658707175)
- The Klotz Group of Companies (166645513920)
- Peacock Capital (166658707188)
- WestMark Realtors (166631946972)
- CWS Capital Partners LLC (166656635616)
- APG Living (166656538298)
- Airport Center Office Building (166682233551)
- Poplar Homes (166647376599)
- DBC Communities (166684220136)
- Willner Realty & Development Co (WRDC) (166631946992)
- Timber Pointe Apartment Homes (166664122100)
- Best Rental Services (166684220146)
- The Prager Group (166658708189)
- 480RealtyPM (166598848243)
- Zendoor (166647377600)
- Boutique Apartments (166658708199)
- Apartments by Tonti (166647377620)
- VRG Management (166664123107)
- MBC Group (166684221134)
- Oakloop Properties (166645514941)
- La Colonia Mobile Home Park (166656636657)
- New Horizons Housing (166647377656)
- Lautrec (166554034879)
- GEM Management, LLC (166721054422)
- Peak Capital (166763642574)
- Wood Partners LLC (166726917848)
- Ameritex Property Management - acquired by HRG (166721131214)
- Altman Companies (Acquired by RAM Partners) (166726917852)
- Buckingham Property Management (166721131219)
- Pangea Real Estate (166752662225)
- Echelon Property Group (166728804071)
- Volker (178672381645)

## Standing data checks (not changed automatically)

- Churned on the page but HubSpot status is Live/Onboarding/Pilot: 22
- Churned on the page but no longer churned=true in HubSpot: 0

## Flags

- At Risk NOT synced this run: Client Health record computed 2026-11-16T15:05:52Z (7 days old, limit 2). The 22 At Risk accounts are carried over unchanged; re-run after Client Health refreshes to sync them.

## Gates

- ok   recompute reproduces the live record from its own accounts
- ok   churned 378 -> 380 (+1 added, +1 from At Risk, none removed)
- ok   Account Status FTL updates applied to churned rows: 0 of 0; 114 rows relabelled Churned / Failure to Launch from is_ftl
- ok   churn date updates applied to churned rows: 0 of 0
- ok   At Risk 21 = Client Health Red 22 less 1 already churned
- ok   At Risk moved by 1 (limit 8)
- ok   no duplicate HubSpot company IDs 
