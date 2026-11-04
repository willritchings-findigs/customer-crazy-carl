import json, re

with open('verify_live_phase3.json') as f:
    d = json.load(f)
accts = d['accounts']

def norm(s):
    if not s: return ''
    s = s.lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    for suf in [' parent company',' parent',' llc',' inc',' incorporated',' corp',' corporation',' company',' co ',' group',' properties',' property management',' realty',' management',' llp',' lp',' ltd']:
        s = s.replace(suf, ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

CHURNED_APPLY = {
    norm('Elme Communities'): {
        'churn_date': '2026-08-04',
        'churn_reason': 'Elme listed themselves for sale, properties are actively being purchased. (lost to: Sold Assets)',
        'source': "HubSpot churned=true, account_status__c=Disqualified (no contradiction).",
    },
    norm('Ebner Properties'): {
        'churn_date': '2026-04-06',
        'churn_reason': 'Lost to Appfolio',
        'source': "HubSpot churned=true, account_status__c=Prospect (no contradiction); zero Sigma product activity this quarter, consistent with churned.",
    },
    norm('Sound City Realty, LLC'): {
        'churn_date': '2026-06-01',
        'churn_reason': 'Dissatisfaction with Product/Service (lost to: Appfolio)',
        'source': "HubSpot churned=true + direct Slack channel confirmation (#p-sound-city-realty: customer explicitly requested churn, integration locked, offboarding playbook initiated). Note: HubSpot account_status__c still reads Live -- offboarding likely still in progress, hasn't been flipped yet.",
    },
    norm('Real Property Management - North Point'): {
        'churn_date': None,
        'churn_reason': 'Switched to a competitor citing simplicity over product quality; prior integration failures and PMS migration issues created friction.',
        'source': "NOT YET reflected in HubSpot's churned flag (checked directly: churned is unset, account_status__c=Live) -- confirmed churned via direct Slack channel read (#p-northpoint) only. Recommend someone update HubSpot's churned flag for this account so other systems relying on it catch up.",
    },
}

FLAGGED_NOT_APPLIED = [
    "Evernest -- HubSpot churned=true/churn_date 2025-09-29 ('Merged/Acquired', 'Acquired by another Findigs Customer'), but account_status__c=Live AND 14 real recent Gong calls in-window AND this is the account Alex just discussed 9/2 as a live, currently-at-risk account. Churned flag looks stale/wrong for this record -- did not apply.",
    "Real Property Management - Agile -- HubSpot churned=true/churn_date 2025-12-15, but account_status__c=Live, no corroborating evidence either way. Contradicted, did not apply.",
    "Real Property Management Three Bridges -- HubSpot churned=true/churn_date 2025-08-14 (over a year old), but account_status__c=Onboarding, and Slack read describes an active win-back/re-onboarding in progress. Reads as mid-re-engagement, not currently churned. Did not apply.",
    "West USA Realty -- HubSpot churned=true/churn_date 2023-04-15 ('Pre-2026'), but Slack channel shows current, active, expanding engagement (Positive classification, multi-year relationship, recent integration). Stale/wrong flag. Did not apply.",
    "33 Realty Management -- HubSpot churned=true/churn_date 2025-11-10, but churn_lost_to field itself says 'Still using Findigs as of 12/29/25' -- self-contradictory record. Did not apply.",
    "Morgan Property Management -- HubSpot churn_date is 2026-12-31, in the future relative to today -- clearly a placeholder/bad data value, not a real churn date. Did not apply.",
    "Peak Property Management -- matches 2 different HubSpot company records ('Peak Management' and 'Peak Management LLC', different domains) -- already flagged as an ambiguous HubSpot match in an earlier phase of this project. Did not apply.",
]

PILLAR_WEIGHTS = {'platform_product_metrics': 50, 'strategic_alignment_governance': 30, 'client_sentiment': 20}
PILLAR_LABELS = {
    'platform_product_metrics': 'Platform & Product Metrics',
    'strategic_alignment_governance': 'Strategic Alignment, Governance & Relationship',
    'client_sentiment': 'Client Sentiment',
}

METHODOLOGY_NOTE = (
    "REBUILT 2026-09-03 per the 2026-09-02 Alex/Emma meeting decision: the overall composite is now a "
    "two-level rollup instead of one flat 19-row weighted average. Each of the 3 pillars already computes "
    "its own value/band from its own rows (unchanged -- see pillar_scores). The overall band is now a "
    "weighted roll-up of the 3 pillars' VALUES at Platform & Product Metrics 50% / Strategic Alignment, "
    "Governance & Relationship 30% / Client Sentiment 20% (Emma's corrected weights from the meeting -- "
    "'let's try that and we can both think about this a little more,' not yet formally final), "
    "re-normalized to whichever pillars have real (non-null) data. "
    "Overall BAND floor rule, mirroring the same floor-gate philosophy already used at the row level and "
    "pillar level everywhere else in this rubric (and the Gong+Slack most-negative-wins combination): any "
    "single Red pillar forces the overall band to at least Yellow; 2 or more Red pillars forces Red; a "
    "Green overall requires ALL included pillars to be Green -- a Green-heavy weighted average alone is "
    "not enough, deliberately, so one weak pillar can't get diluted into invisibility by two good ones. "
    "The CSM Churn Risk Flag (qualitative_pillars.strategic_alignment_governance.csm_qualitative_risk_flag) "
    "is kept as an explicit hard override forcing the overall band to Red regardless of the pillar math, "
    "per Alex's explicit instruction on the call to keep it 'forcing Red on its own.' The displayed VALUE "
    "is always the true weighted average of the 3 pillar values, never flattened to match a forced band, "
    "per the existing 2026-08-19 design principle (value = severity/triage signal, band = categorical gate). "
    "This replaces the prior flat-19-row-weighted-average-with-global-floor-gate composite; that computation "
    "is preserved below under old_flat_composite_for_reference for anyone comparing before/after."
)

n_churned = 0
n_rolled_up = 0
n_fs_untouched = 0
n_skipped_no_pillar_data = 0

for a in accts:
    name = a.get('resolved_name_sigma') or a.get('input_name')
    key = norm(name)

    if key in CHURNED_APPLY:
        info = CHURNED_APPLY[key]
        a['composite_score_partial'] = {
            'value': None,
            'band': 'Churned',
            'churn_date': info['churn_date'],
            'churn_reason': info['churn_reason'],
            'source': info['source'],
            'methodology': (
                "Account confirmed churned -- excluded from health scoring entirely, not scored Red/Yellow/Green "
                "and not left as a stale/wrong old band, per the 2026-09-02 Alex/Emma decision ('any account "
                "marked Churned within the trailing 90 days should show status = Churned outright, not unscored "
                "or a stale red/wrong band'). A churned account isn't a healthy-vs-at-risk question, it's "
                "already a lost one -- same treatment already established for Renters Warehouse in an earlier "
                "phase of this project."
            ),
        }
        n_churned += 1
        continue

    if not a.get('is_decision_assist_enabled'):
        n_fs_untouched += 1
        continue

    ps = a.get('pillar_scores') or {}
    pillars = {k: ps.get(k) for k in PILLAR_WEIGHTS}
    included = {k: v for k, v in pillars.items() if v and v.get('band') is not None and v.get('value') is not None}

    if not included:
        n_skipped_no_pillar_data += 1
        continue

    wsum = sum(PILLAR_WEIGHTS[k] for k in included)
    rolled_value = round(sum(v['value'] * PILLAR_WEIGHTS[k] for k, v in included.items()) / wsum, 1)
    red_count = sum(1 for v in included.values() if v['band'] == 'Red')
    green_count = sum(1 for v in included.values() if v['band'] == 'Green')
    total_included = len(included)

    if red_count >= 2:
        rolled_band = 'Red'
        floor_rule = '2plus_red_pillars'
    elif red_count == 1:
        rolled_band = 'Yellow'
        floor_rule = '1_red_pillar_forces_yellow'
    elif green_count == total_included:
        rolled_band = 'Green'
        floor_rule = 'unanimous_green'
    else:
        rolled_band = 'Yellow'
        floor_rule = 'not_unanimous_green_forces_yellow'

    csm_flag = None
    try:
        csm_flag = a['qualitative_pillars']['strategic_alignment_governance']['csm_qualitative_risk_flag']['value']
    except (KeyError, TypeError):
        pass
    hard_override = (csm_flag == 'Red')
    if hard_override:
        rolled_band = 'Red'
        floor_rule = 'csm_hard_override'

    why_parts = []
    for k in ['platform_product_metrics', 'strategic_alignment_governance', 'client_sentiment']:
        v = pillars.get(k)
        label = PILLAR_LABELS[k]
        if v and v.get('band') is not None:
            why_parts.append(f"{label} ({PILLAR_WEIGHTS[k]}%): {v['band']} ({v['value']})")
        else:
            why_parts.append(f"{label}: unscored, excluded from rollup")
    why = ' | '.join(why_parts)
    if hard_override:
        why += ' | OVERRIDE: CSM Churn Risk Flag = Red forces overall Red regardless of pillar math'

    red_reasons = []
    for k, v in included.items():
        if v['band'] == 'Red':
            red_reasons.append({
                'row': k,
                'label': PILLAR_LABELS[k],
                'detail': f"pillar value {v['value']}/100 -- {v.get('why','')}",
                'gates_floor': True,
            })
    if hard_override:
        red_reasons.append({
            'row': 'csm_qualitative_risk_flag',
            'label': 'CSM Churn Risk Flag',
            'detail': 'Red -- hard override, forces overall Red regardless of pillar rollup math',
            'gates_floor': True,
        })

    old_composite = a.get('composite_score_partial') or {}

    a['composite_score_partial'] = {
        'value': rolled_value,
        'band': rolled_band,
        'pillar_weights_used': dict(PILLAR_WEIGHTS),
        'pillars_included': list(included.keys()),
        'floor_rule_applied': floor_rule,
        'red_reasons': red_reasons,
        'why': why,
        'segment_used': old_composite.get('segment_used'),
        'methodology': METHODOLOGY_NOTE,
        'old_flat_composite_for_reference': {
            'value': old_composite.get('value'),
            'band': old_composite.get('band'),
        },
    }
    n_rolled_up += 1

print('churned accounts patched:', n_churned)
print('DA accounts rolled up via new pillar-weighted composite:', n_rolled_up)
print('FS accounts left untouched (churn-risk-anchored composite unchanged):', n_fs_untouched)
print('DA accounts skipped (no real pillar data to roll up, left as-is):', n_skipped_no_pillar_data)
print('total accounts:', len(accts))

with open('base44_phase4.json', 'w') as f:
    json.dump(d, f, indent=2)

print()
print('FLAGGED, NOT AUTO-APPLIED (for Emma review):')
for line in FLAGGED_NOT_APPLIED:
    print(' -', line)
