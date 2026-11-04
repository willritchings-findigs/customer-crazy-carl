import json, re, glob

with open('verify_live_phase4.json') as f:
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

# ---------- 1. Quarterly revenue ----------
with open('revenue_quarterly.json') as f:
    rev = json.load(f)
rev_by_norm = {}
for r in rev:
    rev_by_norm.setdefault(norm(r['rollup_company_name']), r)

REV_SOURCE = ("Sigma Core (Data Model) Revenue Actual BI -- SUM(FINDIGS_REVENUE_AMOUNT) grouped by rollup company "
    "and calendar quarter. Quarterly dollars shown as CONTEXT, not scored (band null), per the 2026-09-02 meeting "
    "('quarterly, with actual dollar figures shown' / 'let's remove the weights'). Q3 2026 is partial, through "
    "2026-09-02. QoQ% compares the two most recent COMPLETE quarters (Q1 vs Q2) to avoid a misleading "
    "full-vs-partial comparison. Supersedes revenue_trend_mom_pct for display; that field is retained for "
    "reference only.")

rev_matched = 0
rev_unmatched = []
for a in accts:
    m = a.get('metrics')
    if not isinstance(m, dict):
        continue
    name = a.get('resolved_name_sigma') or a.get('input_name')
    r = rev_by_norm.get(norm(name))
    if r:
        m['revenue_trend_quarterly'] = {
            'band': None,
            'scored': False,
            'q1_2026_findigs_revenue': r['Q1_2026'],
            'q2_2026_findigs_revenue': r['Q2_2026'],
            'q3_2026_partial_findigs_revenue': r['Q3_2026_partial_thru_sep2'],
            'q3_partial_through': '2026-09-02',
            'qoq_q1_to_q2_pct': r['Q1_to_Q2_qoq_pct'],
            'status': 'computed',
            'source': REV_SOURCE,
        }
        rev_matched += 1
    else:
        m['revenue_trend_quarterly'] = {
            'band': None, 'scored': False,
            'q1_2026_findigs_revenue': None, 'q2_2026_findigs_revenue': None,
            'q3_2026_partial_findigs_revenue': None, 'q3_partial_through': '2026-09-02',
            'qoq_q1_to_q2_pct': None,
            'status': 'no_revenue_rows_matched',
            'source': REV_SOURCE + ' No Revenue Actual BI rows matched this rollup company for 2026 -- '
                      'either genuinely zero revenue transactions this year or a rollup-name mismatch.',
        }
        rev_unmatched.append(name)

# ---------- 2. PMS integration depth: Slack signal ----------
slack_rationale = {}
for fn in sorted(glob.glob('slack_batches/batch*.json')):
    with open(fn) as f:
        for row in json.load(f):
            if row.get('channel_found') and row.get('rationale'):
                slack_rationale[norm(row['account_name'])] = {
                    'rationale': row['rationale'], 'channel': row.get('channel_name')}

INTEG_KW = ['sync', 'syncing', 'integration', 'mapping', 'endpoint', 'rentcafe', 'rent cafe', 'pms']
NEG_KW = ['issue', 'issues', 'problem', 'fail', 'error', 'stall', 'block', 'friction', 'investigat',
          'unresolved', 'locked', 'not syncing', 'discrepanc', 'incorrect', 'bug', 'workaround', 'returns']

def has_integration_friction(text):
    t = text.lower()
    return any(k in t for k in INTEG_KW) and any(k in t for k in NEG_KW)

pms_flagged = []
for a in accts:
    qp = a.get('qualitative_pillars')
    if not isinstance(qp, dict):
        continue
    pms = qp.get('pms_integration_depth')
    if not isinstance(pms, dict):
        continue
    name = a.get('resolved_name_sigma') or a.get('input_name')
    key = norm(name)
    sig = slack_rationale.get(key)
    manual_kairos = ('kairos' in key)
    if (sig and has_integration_friction(sig['rationale'])) or manual_kairos:
        if manual_kairos and not (sig and has_integration_friction(sig['rationale'])):
            note = ("RentCafe/PMS sync issue surfaced in the account's Slack channel week of 2026-08-31, "
                    "confirmed live on the 2026-09-02 Emma/Alex call ('there was an issue with the rent cafe "
                    "sink this week'), plus ~4 other client-pinged issues raised directly in Slack.")
            channel = '#p-kairos'
        else:
            note = sig['rationale']
            channel = sig['channel']
        pms['slack_integration_signal'] = {
            'found': True,
            'channel': channel,
            'note': note,
            'source': ("Added 2026-09-03 per the 2026-09-02 meeting ('I'll pull from slack and see if we can "
                       "get that feeding into this as well'): integration/sync friction mentioned in the "
                       "account's dedicated Slack channel. Annotation/flag layered on top of the platform-based "
                       "band per Emma's standing PMS rule -- does NOT change the band by itself."),
        }
        band = pms.get('band') or pms.get('overall_band')
        if isinstance(band, str) and band.strip().lower() == 'green':
            for bk in ('band', 'overall_band'):
                if isinstance(pms.get(bk), str) and pms[bk].strip().lower() == 'green':
                    pms[bk] = 'Green (flagged)'
        pms_flagged.append((name, channel))

# ---------- 3. Highmark pilot flag ----------
pilot_set = False
for a in accts:
    name = a.get('resolved_name_sigma') or a.get('input_name')
    if 'highmark' in (name or '').lower():
        a['pilot_phase'] = {
            'active': True,
            'note': ("Pilot phase -- per Alex Schaper on the 2026-09-02 Account Health Finalization call "
                     "('They're still in a pilot phase. I think that's important to call out here'). Metric "
                     "volatility (approval rate, volume, ticket mix) is expected ramp behavior, read scores "
                     "with that context. Went live ~Q2 2026 per revenue history ($0 in Q1)."),
            'source': 'Granola meeting 2026-09-02, Emma + Alex Schaper',
        }
        pilot_set = True

print('revenue quarterly: matched', rev_matched, '| unmatched', len(rev_unmatched))
print('unmatched sample:', rev_unmatched[:12])
print()
print('PMS slack-signal flagged accounts:', len(pms_flagged))
for n, c in pms_flagged:
    print('  -', n, c)
print()
print('highmark pilot flag set:', pilot_set)

with open('base44_phase5.json', 'w') as f:
    json.dump(d, f, indent=2)
