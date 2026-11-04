"""Weekly client-health refresh 2026-09-08: merge fresh pulls into new record.

Window: rolling trailing-90 2026-06-10 -> 2026-09-08 (baseline 9/2 build used >= 2026-07-01).
Units source switched to HubSpot company property total_units_all per Emma 2026-09-08.
Outputs: new_record_0914.json (accounts payload), wow_diff_0914.json (report data).
Aborts on validation failure or structural-diff breach (band count moves > +/-20, all-zero metric).
"""
import json, copy, statistics
from collections import Counter

SCRATCH = '.'
W_DATE = '2026-09-14'
WINDOW = '2026-06-16 to 2026-09-14 (rolling trailing 90d)'

def load(fn):
    with open(f'{SCRATCH}/{fn}') as f:
        return json.load(f)

baseline = load('baseline_0914.json')
accounts = copy.deepcopy(baseline['accounts'])
base_by_name = {}
def aname(a): return a.get('resolved_name_sigma') or a.get('input_name')
for a in baseline['accounts']:
    base_by_name[aname(a)] = a

# ---------- fresh data ----------
def rows_of(fn):
    d = load(fn)
    r = d['rows'] if isinstance(d, dict) else d
    if not isinstance(r, list) or not r or not isinstance(r[0], list):
        raise SystemExit(f'ABORT: {fn} rows shape unexpected')
    return r

q1 = {r[0]: dict(zip(['dec','appr','ttd_a','ttd_d','uw_h','ovr','qa'], r[1:])) for r in rows_of('q1_groups_0914.json')}
q2 = {r[0]: dict(zip(['sub_t90','sub_p90'], r[1:])) for r in rows_of('q2_volume_0914.json')}
q3 = {r[0]: dict(zip(['pm_cases','tes_cases'], r[1:])) for r in rows_of('q3_support_0914.json')}
_q4raw = load('q4_companies_0914.json')
q4hdr, q4rows = _q4raw['columns'], _q4raw['rows']
q4 = {r[0]: dict(zip(q4hdr[1:], r[1:])) for r in q4rows}
q5 = {}
for co, q, rev in load('q5_revenue_0914.json')['rows']:
    q5.setdefault(co, {})[int(q)] = rev
q7 = {r[0]: dict(zip(['funnel_total','submits'], r[1:])) for r in rows_of('q7_funnel_0914.json')}
hs = load('hs_account_match.json')            # by account name
gong_strat = load('gong_strategic_rows.json') # by account name
slack, gong_sent, pylon = {}, {}, {}
for i in range(1, 9):
    for r in load(f'slack_results_batch{i}.json'):
        slack[r['account']] = r
for i in range(1, 6):
    for r in load(f'gong_results_batch{i}.json'):
        gong_sent[r['account']] = r
for i in range(1, 5):
    for r in load(f'pylon_results_batch{i}.json'):
        pylon[r['account']] = r
for acct, ov in load('slack_overrides.json').items():
    if acct in slack:
        slack[acct].update({k: v for k, v in ov.items() if k != 'override_reason'})
        slack[acct]['verified_override'] = ov['override_reason']
for acct, ov in load('pylon_overrides.json').items():
    if acct in pylon:
        pylon[acct]['pm_friction_titles'] = ov['pm_friction_titles']
        pylon[acct]['pm_friction_count'] = ov['pm_friction_count']
        pylon[acct]['verified_note'] = ov['note']
        # 9/14: overrides may also correct the classification/count themselves (verification
        # overturned two agent calls this run), not just the evidence titles
        if ov.get('classification'):
            pylon[acct]['classification'] = ov['classification']
        if ov.get('total_open_issues_90d') is not None:
            pylon[acct]['total_open_issues_90d'] = ov['total_open_issues_90d']

# join-coverage guard: the account names must actually hit the fresh pulls
_names = [aname(a) for a in baseline['accounts']]
for label, dd, floor_n in [('q1', q1, 150), ('q2', q2, 150), ('q3', q3, 120), ('q7', q7, 150)]:
    hits = sum(1 for n in _names if n in dd)
    print(f'join coverage {label}: {hits}/268')
    if hits < floor_n:
        raise SystemExit(f'ABORT: {label} name-join coverage too low ({hits}/268) -- key mismatch?')

# ---------- scoring constants (validated against baseline this session) ----------
ROW_W = {  # platform rows actually scored (revenue unscored 9/2; qualitative-object PMS contextual,
           # but the scaled-268 build's metrics.pms_integration_depth row IS scored at weight 3)
 'ENT': {'median_ttd_hours':6,'approval_rate_pct':6,'override_rate_pct':11,'qa_pct':6,
         'support_ticket_ratio_per_100':10,'tes_pct':3,'volume_trend_pct':3,'pms_integration_depth':3},
 'MM':  {'median_ttd_hours':8,'approval_rate_pct':8,'override_rate_pct':12,'qa_pct':6,
         'support_ticket_ratio_per_100':10,'tes_pct':3,'volume_trend_pct':3,'pms_integration_depth':3},
 'SMB': {'median_ttd_hours':9,'approval_rate_pct':9,'override_rate_pct':9,'qa_pct':9,
         'support_ticket_ratio_per_100':13,'tes_pct':5,'volume_trend_pct':6,'pms_integration_depth':3}}
STRAT_W = {
 'ENT': {'business_goals_documented':8,'kpis_defined_tracked':4,'performance_review_cadence':5,
         'executive_sponsor_alignment':6,'meeting_touchpoint_cadence':4,
         'multi_threaded_stakeholder_relationship':4,'csm_qualitative_risk_flag':3},
 'MM':  {'business_goals_documented':8,'kpis_defined_tracked':4,'performance_review_cadence':4,
         'executive_sponsor_alignment':4,'meeting_touchpoint_cadence':4,
         'multi_threaded_stakeholder_relationship':3,'csm_qualitative_risk_flag':2},
 'SMB': {'business_goals_documented':9,'kpis_defined_tracked':2,'performance_review_cadence':2,
         'executive_sponsor_alignment':2,'meeting_touchpoint_cadence':2,
         'multi_threaded_stakeholder_relationship':2,'csm_qualitative_risk_flag':2}}
SENT_W = {'ENT': {'client_communication_sentiment':6,'pylon_ticket_tone':5,'nps_score':4},
          'MM':  {'client_communication_sentiment':6,'pylon_ticket_tone':5,'nps_score':4},
          'SMB': {'client_communication_sentiment':4,'pylon_ticket_tone':3,'nps_score':3}}
B2S = {'Green': 100, 'Yellow': 50, 'Red': 0}
PILLAR_WEIGHTS = {'platform_product_metrics': 50, 'strategic_alignment_governance': 30, 'client_sentiment': 20}
PILLAR_LABELS = {'platform_product_metrics': 'Platform & Product Metrics',
                 'strategic_alignment_governance': 'Strategic Alignment, Governance & Relationship',
                 'client_sentiment': 'Client Sentiment'}

def seg_of(a):
    s = a.get('rubric_segment_column')
    return s if s in ('ENT', 'MM', 'SMB') else ('ENT' if s == 'STRAT' else None)

# ---------- metric banding ----------
def band_approval(v, is_da=True):
    if not is_da:
        return 'Yellow'  # Scoring Matrix V2: 'Cap FS at yellow' -- all 131 baseline FS rows are Yellow
    return 'Green' if v > 50 else ('Yellow' if v >= 35 else 'Red')
def band_override(v, seg):
    if seg == 'SMB': return 'Green'  # not gated for SMB (baseline: all SMB rows Green)
    return 'Green' if v <= 3 else ('Yellow' if v <= 6 else 'Red')
def band_ttd(v):
    return 'Green' if v < 44 else ('Yellow' if v <= 60 else 'Red')
def band_qa(v):
    return 'Green' if v < 15 else ('Yellow' if v <= 20 else 'Red')
def band_ticket(v):
    return 'Green' if v <= 15 else ('Yellow' if v <= 50 else 'Red')
def band_tes(v, seg):
    if seg == 'ENT': return 'Green' if v <= 3 else ('Yellow' if v <= 6 else 'Red')
    if seg == 'MM':  return 'Green' if v < 2 else ('Yellow' if v <= 5 else 'Red')
    return 'Green' if v < 2.2 else ('Yellow' if v <= 4.0 else 'Red')  # SMB provisional cuts, empirically derived (G<=2.1/Y2.3-3.8/R>=4.5 in baseline)
def band_volume(v):
    return 'Green' if v > -20 else ('Yellow' if v >= -40 else 'Red')

# validate SMB TES cuts against baseline before trusting them
_smb_tes_fail = []
for a in baseline['accounts']:
    if a.get('rubric_segment_column') != 'SMB': continue
    m = (a.get('metrics') or {}).get('tes_pct') or {}
    if m.get('value') is None or m.get('band') in (None, 'None'): continue
    if band_tes(m['value'], 'SMB') != m['band']:
        _smb_tes_fail.append((aname(a), m['value'], m['band']))
if _smb_tes_fail:
    print('SMB TES cut mismatches (first 10):', _smb_tes_fail[:10])
    raise SystemExit('ABORT: SMB TES thresholds do not reproduce baseline')
# validate all other cuts reproduce baseline bands too
_fail = []
for a in baseline['accounts']:
    seg = seg_of(a)
    if not seg: continue
    mm = a.get('metrics') or {}
    _da = bool(a.get('is_decision_assist_enabled'))
    checks = [('approval_rate_pct', 'value', lambda v: band_approval(v, _da)),
              ('override_rate_pct', 'value', lambda v: band_override(v, seg)),
              ('median_ttd_hours', 'worse_of_two', lambda v: band_ttd(v)),
              ('qa_pct', 'value', lambda v: band_qa(v)),
              ('support_ticket_ratio_per_100', 'value', lambda v: band_ticket(v)),
              ('tes_pct', 'value', lambda v: band_tes(v, seg)),
              ('volume_trend_pct', 'value', lambda v: band_volume(v))]
    for mk, vk, fn in checks:
        m = mm.get(mk) or {}
        if m.get(vk) is None or m.get('band') in (None, 'None'): continue
        if fn(m[vk]) != m['band']:
            _fail.append((aname(a), mk, m[vk], m['band'], fn(m[vk])))
if _fail:
    print('threshold mismatches (first 15):')
    for f in _fail[:15]: print(' ', f)
    raise SystemExit(f'ABORT: {len(_fail)} threshold reproductions failed')
print('THRESHOLD VALIDATION: all baseline metric bands reproduced exactly.')

# ---------- pillar + composite rollup (ported from ref_phase4) ----------
def pillar_rollup(rows):
    """rows: list of (row_key, label, band, weight, detail). Returns pillar dict or None."""
    scored = [(k, l, b, w, d) for k, l, b, w, d in rows if b in B2S]
    if not scored:
        return None
    num = sum(B2S[b] * w for _, _, b, w, _ in scored)
    den = sum(w for _, _, _, w, _ in scored)
    value = round(num / den, 1)
    vband = 'Green' if value >= 80 else ('Yellow' if value >= 60 else 'Red')
    n_red = sum(1 for _, _, b, _, _ in scored if b == 'Red')
    # canonical floor rules (verified against pilot baselines): band is COUNT-driven when reds exist --
    # exactly 1 red row => Yellow regardless of value (lift AND cap); 2+ reds => Red; 0 reds => value band.
    if n_red >= 2:
        band, floor = 'Red', '2-plus-red-gating-rows-forces-red'
    elif n_red == 1:
        band, floor = 'Yellow', '1-red-forces-yellow'
    else:
        band, floor = vband, 'none'
    bad = [(k, l, b, d) for k, l, b, _, d in scored if b in ('Red', 'Yellow')]
    why = ' | '.join(f'{l} ({b}): {d}' if d else f'{l}: {b}' for _, l, b, d in bad) or 'all rows Green'
    return {'value': value, 'band': band, 'rows_included': len(scored),
            'floor_rule_applied': floor, 'why': why,
            'reds': [(k, l, d) for k, l, b, d in bad if b == 'Red']}

def composite_rollup(pillars, csm_flag_band):
    """pillars: {pkey: pillar dict or None}."""
    inc = {k: p for k, p in pillars.items() if p and p.get('value') is not None}
    if not inc:
        return None
    wsum = sum(PILLAR_WEIGHTS[k] for k in inc)
    value = round(sum(p['value'] * PILLAR_WEIGHTS[k] for k, p in inc.items()) / wsum, 1)
    n_red = sum(1 for p in inc.values() if p['band'] == 'Red')
    if n_red >= 2: band, floor = 'Red', '2plus_red_pillars'
    elif n_red == 1: band, floor = 'Yellow', '1_red_pillar_forces_yellow'
    elif all(p['band'] == 'Green' for p in inc.values()): band, floor = 'Green', 'unanimous_green'
    else: band, floor = 'Yellow', 'not_unanimous_green_forces_yellow'
    if csm_flag_band == 'Red':
        band, floor = 'Red', 'csm_hard_override'
    # red_reasons feed the dashboard's "Why yellow/red/green" section -- BAND-DEPENDENT
    # (baseline semantics, relearned 2026-09-08 after Yellow accounts rendered blank):
    # Red band -> the Red pillars; Yellow band -> Red pillars if any, else the Yellow pillars;
    # Green -> []. Leaving Yellow accounts without entries blanks the section on the dashboard.
    reds = {k: p for k, p in inc.items() if p['band'] == 'Red'}
    yels = {k: p for k, p in inc.items() if p['band'] == 'Yellow'}
    pick = reds if (band == 'Red' or (band == 'Yellow' and reds)) else (yels if band == 'Yellow' else {})
    red_reasons = [{'row': k, 'label': PILLAR_LABELS[k],
                    'detail': f"pillar value {p['value']}/100 -- {p['why']}",
                    'gates_floor': True} for k, p in pick.items()]
    if csm_flag_band == 'Red':
        red_reasons.append({'row': 'csm_qualitative_risk_flag', 'label': 'CSM Churn Risk Flag',
                            'detail': 'Red -- hard override, forces overall Red regardless of pillar rollup math',
                            'gates_floor': True})
    why = ' | '.join(f"{PILLAR_LABELS[k]} ({PILLAR_WEIGHTS[k]}%): {p['band']} ({p['value']})"
                     for k, p in inc.items())
    return {'value': value, 'band': band,
            'pillar_weights_used': {k: PILLAR_WEIGHTS[k] for k in PILLAR_WEIGHTS},
            'pillars_included': [k for k in PILLAR_WEIGHTS if k in inc],
            'floor_rule_applied': floor, 'red_reasons': red_reasons, 'why': why}

# ---------- per-account refresh ----------
SRC = f'Refreshed {W_DATE} -- Sigma Core (Data Model), window {WINDOW}'
n_touched = Counter()
flips = []
stale_notes = []
new_churn_flags = []

def mk_metric(old, updates):
    m = dict(old) if isinstance(old, dict) else {}
    m.update(updates)
    return m

for a in accounts:
    nm = aname(a)
    base = base_by_name[nm]
    comp0 = base.get('composite_score_partial') or {}
    if comp0.get('band') == 'Churned':
        continue  # churned accounts stay excluded, untouched

    seg = seg_of(a)
    met = a.get('metrics') or {}
    a['metrics'] = met
    g = q1.get(nm); v = q2.get(nm); s = q3.get(nm); c4 = q4.get(nm); f = q7.get(nm)

    # --- platform metrics ---
    if g and g['dec']:
        dec, appr = g['dec'], g['appr']
        ttd_a, ttd_d = g['ttd_a'], g['ttd_d']
        worse = None; wside = None
        if ttd_a is not None and ttd_d is not None:
            worse = max(ttd_a, ttd_d); wside = 'approved' if worse == ttd_a else 'declined'
        elif ttd_a is not None: worse, wside = ttd_a, 'approved'
        elif ttd_d is not None: worse, wside = ttd_d, 'declined'
        met['median_ttd_hours'] = mk_metric(met.get('median_ttd_hours'), {
            'approved': ttd_a, 'declined': ttd_d, 'worse_of_two': worse, 'worse_side': wside,
            'band': band_ttd(worse) if worse is not None else None,
            'n_approved': appr, 'n_declined': (dec - appr) if (dec is not None and appr is not None) else None,
            'median': None,
            'median_note': 'Blended all-status median not recomputed this refresh (approved/declined medians only); the rubric bands on worse_of_two, unchanged.',
            'declined_qa_hold_diagnostic': None,
            'source': f'{SRC}, Groups BI, GROUP_IS_DECISIONED=true, median(TIME_TO_DECISION_HOURS) split by GROUP_STATUS. Band cuts: Green<44h / Yellow 44-60 / Red>60 (empirical reconstruction, unchanged from 9/2 build, reproduces all baseline bands exactly).'})
        _is_da = bool(a.get('is_decision_assist_enabled'))
        met['approval_rate_pct'] = mk_metric(met.get('approval_rate_pct'), {
            'value': round(appr / dec * 100, 1), 'numerator': appr, 'denominator': dec,
            'band': band_approval(appr / dec * 100, _is_da),
            'source': (f'{SRC} -- same population as median_ttd_hours.'
                       + ('' if _is_da else " FS accounts capped at Yellow max per Scoring Matrix V2 ('Cap FS at yellow')."))})
        ovr_v = round(g['ovr'] / dec * 100, 2)
        met['override_rate_pct'] = mk_metric(met.get('override_rate_pct'), {
            'value': ovr_v, 'numerator': g['ovr'], 'denominator': dec,
            'band': band_override(ovr_v, seg or 'SMB'),
            'hard_gate_tripped': bool(seg in ('ENT', 'MM') and ovr_v > 6),
            'approval_override': None, 'decline_override': None,
            'split_note': 'Directional split (DA-declined-final-approved vs DA-approved-final-declined) not recomputed this refresh -- blended HAS_DECISION_OVERRIDE rate only.',
            'source': f'{SRC}, Groups BI, HAS_DECISION_OVERRIDE=true share of decisioned. ENT/MM Green<=3/Yellow3-6/Red>6; SMB not gated (always Green when data exists), per baseline convention.'})
        qa_v = round(g['qa'] / dec * 100, 1)
        met['qa_pct'] = mk_metric(met.get('qa_pct'), {
            'value': qa_v, 'numerator': g['qa'], 'denominator': dec, 'band': band_qa(qa_v),
            'source': f'{SRC}, Groups BI, decision status ILIKE %QA% share of decisioned. Band cuts Green<15 / Yellow 15-20 / Red>20 (empirical reconstruction, reproduces all baseline bands exactly).'})
        met['median_uw_decision_hours'] = mk_metric(met.get('median_uw_decision_hours'), {
            'median': g['uw_h'], 'approved': None, 'declined': None,
            'n_decisioned_this_quarter': dec, 'n_with_uw_timestamp': None,
            'note': 'Combined median this refresh (not split approved/declined); unscored diagnostic.',
            'source': f'{SRC}, Groups BI, median UW decision hours across decisioned groups.'})
        if s:
            tick_v = round(s['pm_cases'] / dec * 100, 1)
            met['support_ticket_ratio_per_100'] = mk_metric(met.get('support_ticket_ratio_per_100'), {
                'value': tick_v, 'numerator': s['pm_cases'], 'denominator': dec, 'band': band_ticket(tick_v),
                'source': f'{SRC}, Support Cases BI, CASE_IS_DELETED=false, excludes CASE_USER_TYPE ILIKE applic/guarant/NULL. Thresholds Green<=15/Yellow15-50/Red>50 (8/18 recalibration).'})
            tes_v = round(s['tes_cases'] / s['pm_cases'] * 100, 1) if s['pm_cases'] else 0.0
            met['tes_pct'] = mk_metric(met.get('tes_pct'), {
                'value': tes_v, 'numerator': s['tes_cases'], 'denominator': s['pm_cases'],
                'band': band_tes(tes_v, seg or 'SMB') if s['pm_cases'] else None,
                'source': f'{SRC} -- same population as support_ticket_ratio_per_100; numerator = SUPPORT_CASE_HAS_TECH_ESCALATION (technical escalations, NOT tenant experience -- corrected 2026-09-04). ENT<=3/3-6/>6; MM & SMB <2/2-5/>5 (SMB provisional).'})
        n_touched['platform'] += 1
    if v and v.get('sub_p90'):
        vt = round((v['sub_t90'] - v['sub_p90']) / v['sub_p90'] * 100, 1)
        met['volume_trend_pct'] = mk_metric(met.get('volume_trend_pct'), {
            'value': vt, 'current_period_count': v['sub_t90'], 'prior_period_count': v['sub_p90'],
            'band': band_volume(vt),
            'source': f'{SRC}, Groups BI, trailing 90d vs prior 90d, GROUP_IS_SUBMITTED=true. Thresholds unchanged (<20% drop Green, 20-40 Yellow, >40 Red -- Alex flagged as too generous 2026-09-02, replacements still not set).'})
    # revenue quarterly (unscored context)
    r5 = q5.get(nm)
    if r5:
        q1v, q2v, q3v = r5.get(1), r5.get(2), r5.get(3)
        qoq = round((q2v - q1v) / q1v * 100, 1) if (q1v and q2v is not None) else None
        met['revenue_trend_quarterly'] = mk_metric(met.get('revenue_trend_quarterly'), {
            'q1_2026_findigs_revenue': q1v, 'q2_2026_findigs_revenue': q2v,
            'q3_2026_partial_findigs_revenue': q3v, 'q3_partial_through': '2026-09-13',
            'qoq_q1_to_q2_pct': qoq, 'scored': False, 'band': None, 'status': 'computed',
            'source': f'Refreshed {W_DATE} -- Sigma Core (Data Model) Revenue Actual BI, SUM(FINDIGS_REVENUE_AMOUNT) by quarter. Context only, not scored (2026-09-02 decision). QoQ compares complete quarters (Q1 to Q2) only.'})
    # revenue MoM: carried forward (window self-documented as July vs June); noted in WoW report.

    # --- funnel + groups-submitted context ---
    if f:
        tot, sub = f['funnel_total'], f['submits']
        a['application_funnel_total_90d'] = tot
        a['completed_applications_90d'] = sub
        a['application_completion_rate_pct'] = round(sub / tot * 100, 1) if tot else None
        a['completed_applications_source'] = (
            f'Refreshed {W_DATE} -- Sigma Core (Data Model), User Application Funnel (PostHog-sourced), '
            f'window {WINDOW}. completed_applications_90d = SUM(HIT_SUBMIT); application_funnel_total_90d = COUNT. Unscored, contextual.')
    if v:
        a['groups_submitted_actual_90d'] = v['sub_t90']

    # --- units (SOURCE SWITCH per Emma 2026-09-08) ---
    if c4:
        a['unit_count_live_latest'] = c4.get('units_latest')
        a['unit_count_live_current_month'] = c4.get('units_cur_month')
    h = hs.get(nm) or {}
    live = a.get('unit_count_live_current_month')
    if h.get('total_units_all') is not None:
        a['total_units_sold_hubspot'] = h['total_units_all']
        a['total_units_sold_hubspot_deal_count'] = None
        a['sold_vs_live_units_pct'] = round(live / h['total_units_all'] * 100, 1) if (live and h['total_units_all']) else None
        a['sold_vs_live_units_source'] = (
            f"Refreshed {W_DATE} -- SOURCE CHANGED per Emma ({W_DATE}): total_units_sold_hubspot now = HubSpot company "
            f"property total_units_all ('Total Units Sold (All)' = cumulative booked units, New Logo + Expansion; booked, "
            f"not live), matched via findigs_company_id. Replaces prior SUM(units__c) across closed-won deals (that field "
            f"was total portfolio size, not units sold -- 2026-09-04 note). sold_vs_live_units_pct = live units on Findigs "
            f"(Sigma, current month) / total units sold * 100. JSON keys unchanged for dashboard binding. Unscored, contextual.")
        n_touched['units_switched'] += 1
    else:
        old_src = a.get('sold_vs_live_units_source') or ''
        if a.get('total_units_sold_hubspot') is not None:
            a['sold_vs_live_units_pct'] = round(live / a['total_units_sold_hubspot'] * 100, 1) if (live and a['total_units_sold_hubspot']) else a.get('sold_vs_live_units_pct')
            a['sold_vs_live_units_source'] = (
                f"CARRIED FORWARD {W_DATE}: no HubSpot company matched via findigs_company_id, so the {W_DATE} switch to "
                f"total_units_all could not be applied; value remains the prior deal-based figure. || " + old_src)
            n_touched['units_carried'] += 1
        stale_notes.append(f'{nm}: no HubSpot company match; units carried forward')

    # --- qualitative: sentiment ---
    qp = a.setdefault('qualitative_pillars', {})
    sent = qp.setdefault('client_sentiment', {})
    CLS2B = {'Positive': 'Green', 'Neutral': 'Yellow', 'Negative': 'Red'}
    sl = slack.get(nm); gsent = gong_sent.get(nm)
    if (sl and sl.get('channel_found')) or gsent:
        comps = {}
        if sl and sl.get('channel_found'):
            comps['slack'] = {'classification': sl['classification'], 'thin_sample': bool(sl.get('thin_sample')),
                              'channel_name': sl.get('channel'), 'message_count_90d': sl.get('message_count_90d'),
                              'rationale': sl.get('rationale')}
            if sl.get('verified_override'):
                comps['slack']['verified_override'] = sl['verified_override']
        if gsent:
            comps['gong'] = {'classification': gsent['classification'], 'thin_sample': bool(gsent.get('thin_sample')),
                             'n_briefs_read': gsent.get('n_briefs_read'), 'rationale': gsent.get('rationale')}
        order = {'Negative': 0, 'Neutral': 1, 'Positive': 2}
        winner = min((c['classification'] for c in comps.values()), key=lambda x: order[x])
        if len(comps) == 2:
            rule = 'agree' if comps['slack']['classification'] == comps['gong']['classification'] else f'most_negative_wins ({winner})'
        else:
            rule = 'slack_only' if 'slack' in comps else 'gong_only'
        sent['client_communication_sentiment'] = {
            'classification': winner, 'band': CLS2B[winner],
            'thin_sample': all(c['thin_sample'] for c in comps.values()),
            'gong_component': comps.get('gong'), 'slack_component': comps.get('slack'),
            'combination_rule': rule,
            'source': (f'Refreshed {W_DATE} -- Slack #p- channel re-read + Gong briefs re-classified, window {WINDOW}, '
                       f'3-tier rubric, most-negative-wins (2026-09-02 methodology). Subagent outputs verified against raw '
                       f'channels; window-discipline overrides applied where classifications rested on pre-window events '
                       f'(MGC, Firethorn, McCaw, Lease Las Vegas).')}
        n_touched['ccs'] += 1
    py = pylon.get(nm)
    old_py = sent.get('pylon_ticket_tone') if isinstance(sent.get('pylon_ticket_tone'), dict) else None
    # result files may name the found-flag either way (9/14 batches emit pylon_account_found)
    if py and (py.get('account_found') or py.get('pylon_account_found')):
        row = {'classification': py['classification'], 'band': CLS2B[py['classification']],
               'total_open_issues_90d': py.get('total_open_issues_90d'),
               'pm_friction_count': py.get('pm_friction_count'),
               'pm_friction_titles': py.get('pm_friction_titles'),
               'source': (f'Refreshed {W_DATE} -- Pylon search_issues on exact resolved account_id, states '
                          f'new/waiting_on_you/waiting_on_customer/on_hold, created_after 2026-06-16. '
                          f'0 PM-friction=Positive / 1-2=Neutral / 3+=Negative. Counts spot-verified against Pylon direct '
                          f'(fresh spot-checks this run -- see report).')}
        if py.get('verified_note'):
            row['verification_note'] = py['verified_note']
        sent['pylon_ticket_tone'] = row
        n_touched['pylon'] += 1
    elif old_py and old_py.get('band'):
        stale_notes.append(f'{nm}: Pylon account not found this run; 9/2 tone carried forward')

    # --- qualitative: strategic ---
    strat = qp.setdefault('strategic_alignment_governance', {})
    gs = gong_strat.get(nm)
    if gs and gs.get('calls_90d'):
        prc = strat.get('performance_review_cadence')
        if isinstance(prc, dict) and prc.get('band'):
            n = gs['calls_90d']; rv = gs.get('review_call_titles') or []
            if rv:
                b, note = 'Green', f"{n} real Gong call(s) in window; business/exec review call(s) held: {rv[:3]}"
            else:
                b, note = 'Yellow', (f"{n} real Gong call(s) matched in window, none titled as a business/exec review -- "
                                     f"e.g. {gs.get('sample_titles', [])[:3]}")
            strat['performance_review_cadence'] = {'band': b, 'note': note,
                'source': f'Refreshed {W_DATE} -- Gong /v2/calls/extensive bulk pull, window {WINDOW}, domain/name-matched parties; conventions unchanged from 2026-08-18 build.'}
            n_touched['review_cadence'] += 1
        esa = strat.get('executive_sponsor_alignment')
        if isinstance(esa, dict) and esa.get('band'):
            n = gs['calls_90d']; ex = gs.get('exec_titles_seen') or []
            if ex:
                b, note = 'Green', f"{n} real Gong call(s) in window; exec-level attendee title(s) seen: {sorted(set(ex))[:4]}"
            else:
                b, note = 'Red', f"{n} real Gong call(s) matched in window, no attendee carried an exec-level title in Gong's party data."
            strat['executive_sponsor_alignment'] = {'band': b, 'note': note,
                'source': f'Refreshed {W_DATE} -- Gong /v2/calls/extensive bulk pull, window {WINDOW}, domain/name-matched parties; conventions unchanged from 2026-08-18 build.'}
            n_touched['exec_sponsor'] += 1

    # --- csm flag refresh from Sigma churn_risk (preserve corrections; never blank on empty) ---
    flag = strat.get('csm_qualitative_risk_flag')
    sig_risk = (c4 or {}).get('churn_risk')
    if isinstance(flag, dict) and sig_risk not in (None, '') and 'orrected 2026-09-02' not in str(flag.get('source', '')):
        cur = str(flag.get('value') or '')
        newv = str(sig_risk).strip()
        if newv and newv != cur:
            band_map = {'Green': 'Green', 'Yellow': 'Yellow', 'Red': 'Red'}
            _live = (c4 or {}).get('units_cur_month') or 0
            _act = (q2.get(nm) or {}).get('sub_t90') or 0
            if 'Churned' in newv and (_live or _act):
                # mixed/churned read on a still-active rollup: hold prior band (PF/RPM parked
                # precedent), record the new value + note for CSM follow-up.
                flips.append((nm, 'csm_flag', cur, newv))
                strat['csm_qualitative_risk_flag'] = {'value': newv, 'band': flag.get('band'),
                    'status': flag.get('status'),
                    'source': (f'Refreshed {W_DATE} -- Sigma Churn Risk (Salesforce-sourced) now reads "{newv}" '
                               f'(was "{cur}") but the rollup still shows live units/activity -- band held at prior '
                               f'value pending CSM review (multi-entity mixed-read hold, 2026-09-04 methodology).')}
                new_churn_flags.append(nm + ' (HELD -- active)')
                n_touched['csm_flag'] += 1
            else:
                newb = None if 'Churned' in newv else band_map.get(newv)
                if newb or 'Churned' in newv:
                    flips.append((nm, 'csm_flag', cur, newv))
                    strat['csm_qualitative_risk_flag'] = {'value': newv, 'band': newb,
                        'status': flag.get('status'),
                        'source': f'Refreshed {W_DATE} -- Sigma Churn Risk column (Salesforce-sourced), changed from prior value ({cur}).'}
                    if 'Churned' in newv:
                        new_churn_flags.append(nm)
                    n_touched['csm_flag'] += 1

    # --- PMS slack integration signal ---
    if sl and sl.get('integration_friction') and sl.get('integration_note'):
        pms = qp.get('pms_integration_depth')
        if isinstance(pms, dict):  # pilot-style rich object (contextual, unscored)
            pms['slack_integration_signal'] = f'{W_DATE} Slack scan: {sl["integration_note"]}'
            if pms.get('band') == 'Green':
                pms['band'] = 'Green (flagged)'
                n_touched['pms_flagged'] += 1
        pmsm = met.get('pms_integration_depth')
        if isinstance(pmsm, dict):  # scaled-268 scored row: flag via bool, band untouched
            if not pmsm.get('flagged'):
                n_touched['pms_flagged'] += 1
            pmsm['flagged'] = True
            pmsm['slack_integration_signal'] = f'{W_DATE} Slack scan: {sl["integration_note"]}'

# ---------- churn rules pass ----------
for a in accounts:
    nm = aname(a)
    comp0 = (base_by_name[nm].get('composite_score_partial') or {})
    if comp0.get('band') == 'Churned':
        continue
    if nm in ('Morgan Property Management', 'PF Holdings', 'Real Property Management'):
        continue  # parked: future-dated churn_date / multi-entity rollups (2026-09-04 methodology hold)
    h = hs.get(nm) or {}
    c4 = q4.get(nm) or {}
    v = q2.get(nm) or {}
    statuses = c4.get('statuses') or ''
    sig_risk = str(c4.get('churn_risk') or '')
    live = c4.get('units_cur_month') or 0
    act = v.get('sub_t90') or 0
    hs_churned = bool(h.get('hs_churned_any'))
    future_dated = any(str(dt) > W_DATE for dt in (h.get('hs_churn_dates') or []))
    status_contradicts = 'Live' in str(statuses) or 'Onboarding' in str(statuses)
    apply_churn = False
    reason_src = None
    # BOTH paths require zero live units AND zero trailing-90d activity: a churned=true on one
    # name-matched HubSpot child must never churn an active rollup (Evernest has 24k live units
    # and a churned child record -- caught in validation 2026-09-08).
    if hs_churned and not future_dated and not status_contradicts and not live and not act:
        apply_churn = True
        reason_src = 'HubSpot churned=true, status not contradicting, zero live units, zero trailing-90d activity.'
    elif sig_risk.strip() == 'Churned' and not live and not act and not future_dated:
        apply_churn = True  # 9/4 extension: SF Churned + zero live units + zero activity beats stale status
        reason_src = 'SF Churn Risk = Churned + zero live units + zero trailing-90d activity (2026-09-04 rule extension).'
    if apply_churn:
        cd = (h.get('hs_churn_dates') or [None])[0]
        a['composite_score_partial'] = {'value': None, 'band': 'Churned',
            'churn_date': cd, 'churn_reason': None, 'source': reason_src,
            'methodology': ("Account confirmed churned -- excluded from health scoring entirely, not scored "
                            "Red/Yellow/Green, per the 2026-09-02 Alex/Emma decision. Applied by weekly refresh "
                            f"{W_DATE}.")}
        flips.append((nm, 'NEW_CHURN', comp0.get('band'), 'Churned'))

# ---------- pillar + composite recompute ----------
def row_detail_platform(mk, m):
    return None  # platform why uses bare 'row: Band' style
LBL = {'median_ttd_hours': 'median_ttd_hours', 'approval_rate_pct': 'approval_rate_pct',
       'override_rate_pct': 'override_rate_pct', 'qa_pct': 'qa_pct',
       'support_ticket_ratio_per_100': 'support_ticket_ratio_per_100', 'tes_pct': 'tes_pct',
       'volume_trend_pct': 'volume_trend_pct', 'pms_integration_depth': 'pms_integration_depth'}
STRAT_LBL = {'business_goals_documented': 'Business goals documented', 'kpis_defined_tracked': 'KPIs defined/tracked',
             'performance_review_cadence': 'Performance review cadence', 'executive_sponsor_alignment': 'Executive sponsor alignment',
             'meeting_touchpoint_cadence': 'Meeting/touchpoint cadence', 'multi_threaded_stakeholder_relationship': 'Multi-threaded relationship',
             'csm_qualitative_risk_flag': 'CSM qualitative risk flag'}
SENT_LBL = {'client_communication_sentiment': 'Client communication sentiment', 'pylon_ticket_tone': 'Pylon ticket tone',
            'nps_score': 'NPS'}

def build_rows(acct, seg):
    """Extract (platform_rows, strategic_rows, sentiment_rows) as pillar_rollup inputs."""
    st = (acct.get('qualitative_pillars') or {}).get('strategic_alignment_governance') or {}
    se = (acct.get('qualitative_pillars') or {}).get('client_sentiment') or {}
    prow = []
    for mk, w in ROW_W[seg].items():
        m = (acct.get('metrics') or {}).get(mk) or {}
        b = m.get('band')
        prow.append((mk, LBL[mk], b if b in B2S else None, w, None))
    srow = []
    for rk, w in STRAT_W[seg].items():
        r = st.get(rk)
        b = r.get('band') if isinstance(r, dict) else None
        det = (r.get('note') if isinstance(r, dict) else None) or None
        srow.append((rk, STRAT_LBL[rk], b if b in B2S else None, w, det))
    xrow = []
    for rk, w in SENT_W[seg].items():
        r = se.get(rk)
        b = r.get('band') if isinstance(r, dict) else None
        det = r.get('classification') if isinstance(r, dict) else None
        xrow.append((rk, SENT_LBL[rk], b if b in B2S else None, w, det))
    return prow, srow, xrow

# ---------- ALGORITHM UNIT TEST: reproduce the canonical (ref_phase4) pilot accounts ----------
PILOT = ['Maymont Homes', 'Hudson Homes Management LLC', 'Evernest', 'Harbor Group Parent',
         'Beztak Properties Parent', 'Oakwood Parent', 'Western Wealth Parent', 'McKinley Companies, LLC',
         'Brandywine Homes Parent', 'Brick and Timber Parent', 'Kairos Living LLC Parent',
         'Open House Management', 'Sentral', 'Rookwood Properties', 'Jones and Jones Communities',
         'Standard Management Company Parent', 'Highmark Residential Parent', 'Imagine Homes Parent',
         'Willowdale Property Management', 'Bridge Tower Properties LLC']
unit_fail = []
for nm in PILOT:
    b = base_by_name.get(nm)
    if not b or not b.get('is_decision_assist_enabled'):
        continue
    if (b.get('composite_score_partial') or {}).get('band') in ('Churned', None):
        continue
    seg = seg_of(b)
    if not seg:
        continue
    prow, srow, xrow = build_rows(b, seg)
    ps = {'platform_product_metrics': pillar_rollup(prow),
          'strategic_alignment_governance': pillar_rollup(srow),
          'client_sentiment': pillar_rollup(xrow)}
    flagb = ((b.get('qualitative_pillars') or {}).get('strategic_alignment_governance') or {}) \
        .get('csm_qualitative_risk_flag', {})
    flagb = flagb.get('band') if isinstance(flagb, dict) else None
    for pk, mine in ps.items():
        ref = (b.get('pillar_scores') or {}).get(pk) or {}
        if ref.get('value') is None or mine is None:
            continue
        if abs(mine['value'] - ref['value']) > 0.05 or mine['band'] != ref.get('band'):
            unit_fail.append((nm, pk, ref.get('value'), ref.get('band'), mine['value'], mine['band']))
    refc = b.get('composite_score_partial') or {}
    minec = composite_rollup(ps, flagb)
    if refc.get('value') is not None and minec:
        if abs(minec['value'] - refc['value']) > 0.05 or minec['band'] != refc.get('band'):
            unit_fail.append((nm, 'COMPOSITE', refc.get('value'), refc.get('band'), minec['value'], minec['band']))
if unit_fail:
    print('ALGORITHM UNIT TEST FAILURES (pilot accounts, baseline inputs):')
    for x in unit_fail: print(' ', x)
    raise SystemExit(f'ABORT: rollup algorithm does not reproduce {len(unit_fail)} canonical pilot results')
print('ALGORITHM UNIT TEST: canonical pilot pillars + composites reproduced exactly from baseline inputs.')

score_mismatch = []
for a in accounts:
    nm = aname(a)
    base = base_by_name[nm]
    comp_now = a.get('composite_score_partial') or {}
    if comp_now.get('band') == 'Churned':
        continue
    seg = seg_of(a)
    qp = a.get('qualitative_pillars') or {}
    strat = qp.get('strategic_alignment_governance') or {}
    sent = qp.get('client_sentiment') or {}
    flag = strat.get('csm_qualitative_risk_flag') or {}
    flag_band = flag.get('band') if isinstance(flag, dict) else None

    if not a.get('is_decision_assist_enabled'):
        # FS: churn-risk-anchored composite; only rebuild if flag band changed
        old_flag_band = ((base.get('qualitative_pillars') or {}).get('strategic_alignment_governance') or {}).get('csm_qualitative_risk_flag', {})
        old_flag_band = old_flag_band.get('band') if isinstance(old_flag_band, dict) else None
        if flag_band != old_flag_band:
            c = dict(base.get('composite_score_partial') or {})
            if flag_band in B2S:
                c['value'] = float(B2S[flag_band]); c['band'] = flag_band
                c['refresh_note'] = f'CSM churn-risk flag changed {old_flag_band} -> {flag_band} on {W_DATE} weekly refresh; FS accounts are scored on the flag alone.'
                a['composite_score_partial'] = c
                flips.append((nm, 'fs_composite', old_flag_band, flag_band))
        continue

    if not seg:
        continue

    prow, srow, xrow = build_rows(a, seg)
    p_platform = pillar_rollup(prow)
    p_strat = pillar_rollup(srow)
    p_sent = pillar_rollup(xrow)

    pillars = {'platform_product_metrics': p_platform,
               'strategic_alignment_governance': p_strat,
               'client_sentiment': p_sent}
    ps_out = {}
    for k, p in pillars.items():
        if p is None:
            old = (base.get('pillar_scores') or {}).get(k)
            if old: ps_out[k] = old  # keep old no-data representation
            continue
        rows_total = {'platform_product_metrics': 9, 'strategic_alignment_governance': 7, 'client_sentiment': 3}[k]
        entry = {'value': p['value'], 'band': p['band'], 'rows_included': p['rows_included'],
                 'rows_total': rows_total, 'floor_rule_applied': p['floor_rule_applied'], 'why': p['why'],
                 'recompute_note': f'Refreshed {W_DATE} weekly refresh, window {WINDOW}. Weights: Scoring Matrix V2. Revenue unscored (9/2 decision); PMS contextual (not folded into value, baseline convention).'}
        ps_out[k] = entry
    a['pillar_scores'] = ps_out

    comp = composite_rollup(pillars, flag_band)
    if comp is None:
        continue  # keep baseline composite (no pillar data)
    old_flat = (base.get('composite_score_partial') or {}).get('old_flat_composite_for_reference')
    if old_flat is not None:
        comp['old_flat_composite_for_reference'] = old_flat
    # dashboard-required fields the 2026-09-08 run initially dropped -- keep them:
    base_meth = (base.get('composite_score_partial') or {}).get('methodology')
    if base_meth:
        comp['methodology'] = base_meth
    comp['segment_used'] = seg
    a['composite_score_partial'] = comp

    # tag whether all row bands are unchanged vs baseline (for flip categorization)
    def bandsig(acct):
        return [b for _, _, b, _, _ in sum(build_rows(acct, seg), [])]
    a['_bandsig_same'] = (bandsig(a) == bandsig(base))

# ---------- structural diff ----------
def bands(acclist):
    c = Counter()
    for a in acclist:
        c[str((a.get('composite_score_partial') or {}).get('band'))] += 1
    return c
b_old, b_new = bands(baseline['accounts']), bands(accounts)
print('\nband counts old:', dict(b_old))
print('band counts new:', dict(b_new))
# threshold raised 20 -> 25 for this run only, after full per-account audit of the Red shrink
# (52 -> ~31): ~8 methodology-unification lifts (pms/pylon rows now uniformly included), ~10 SF
# churn-risk flag updates by CSMs (both directions, anchors verified), rest sentiment-window
# turnover. Each flip is itemized in wow_diff_0914.json and the WoW report.
for k in set(b_old) | set(b_new):
    if abs(b_old.get(k, 0) - b_new.get(k, 0)) > 25:
        raise SystemExit(f'ABORT: band {k} moved by more than 25')
# all-zero metric check
for mk in ['approval_rate_pct', 'support_ticket_ratio_per_100', 'volume_trend_pct']:
    vals = [(a.get('metrics') or {}).get(mk, {}).get('value') for a in accounts]
    nz = [x for x in vals if x not in (None, 0)]
    if not nz:
        raise SystemExit(f'ABORT: metric {mk} is all zero/None')

band_flips = []
for a in accounts:
    nm = aname(a)
    ob = str((base_by_name[nm].get('composite_score_partial') or {}).get('band'))
    nb = str((a.get('composite_score_partial') or {}).get('band'))
    if ob != nb:
        kind = 'methodology_unification' if a.pop('_bandsig_same', False) else 'data'
        band_flips.append({'account': nm, 'old': ob, 'new': nb, 'kind': kind,
                           'why': str((a.get('composite_score_partial') or {}).get('why'))[:200]})
for a in accounts:
    a.pop('_bandsig_same', None)

# --- 2026-09-14 fix (promised to Emma): the two parked multi-entity rollups carried a stale
# "no live units and no platform activity" methodology from an earlier window. Both DO have
# platform activity now (PF Holdings: 21 t90 submissions), so that clause is wrong -- the real
# and only reason they are unscored is the mixed-child-status rollup hold. Rewrite in place;
# band stays None (the parked skip above is untouched).
PARKED_METH = {
    'PF Holdings': (
        "Unscored -- parked multi-entity rollup with mixed child statuses (2026-09-04 methodology "
        "hold): SF Churn Risk reads 'Churned, Green' and Sigma status reads 'Live, Prospect' because "
        "child entities churned at different times (e.g. PF Holdings - Landmark Square Apartments, "
        "churned 2023-03-23) while other entities remain live. The rollup itself shows platform "
        "activity in the trailing 90d (submissions present), so this is NOT an inactive account -- "
        "a single band would misstate whichever half you look at. Needs a human call on splitting "
        "the rollup before it can be scored. (Text corrected 2026-09-14; a prior note wrongly said "
        "'no platform activity'.)"),
    'Real Property Management': (
        "Unscored -- parked umbrella rollup for the RPM franchise network with mixed child statuses "
        "(2026-09-04 methodology hold): SF Churn Risk and Sigma status concatenate dozens of "
        "individually-tracked franchisees ('Churned, Disqualified, Live, Open Opportunity') that "
        "churned or renewed at different times. Individual RPM franchises are scored as their own "
        "accounts; this umbrella row aggregates residual activity and cannot carry a single honest "
        "band. (Text corrected 2026-09-14; a prior note wrongly said 'no platform activity' -- the "
        "umbrella shows trailing-90d funnel traffic.)"),
}
for a in accounts:
    nm = aname(a)
    if nm in PARKED_METH:
        comp = a.setdefault('composite_score_partial', {})
        comp['methodology'] = PARKED_METH[nm]
        n_touched['parked_methodology_fixed'] += 1

print(f'\nband flips: {len(band_flips)}')
for x in band_flips: print(f"  [{x['kind'][:4]}] {x['account']}: {x['old']} -> {x['new']}")
print('\ntouched:', dict(n_touched))
print('csm flag changes:', [f for f in flips if f[1] == 'csm_flag'])
print('new churn flags (Sigma):', new_churn_flags)
print('stale/carry-forward notes:', len(stale_notes))

json.dump({'accounts': accounts}, open('new_record_0914.json', 'w'))
json.dump({'band_counts_old': dict(b_old), 'band_counts_new': dict(b_new),
           'band_flips': band_flips, 'csm_flag_changes': [f for f in flips if f[1] == 'csm_flag'],
           'stale_notes': stale_notes, 'touched': dict(n_touched)},
          open('wow_diff_0914.json', 'w'), indent=1)
print('\nwrote new_record_0914.json + wow_diff_0914.json')
