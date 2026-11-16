"""Weekly client-health refresh: HubSpot pulls via api.hubapi.com.
(a) all companies with findigs_company_id set -> <scratch>/hs_findigs_companies.json
(b) all companies churned=true -> <scratch>/hs_churned_<MMDD>.json
Usage: python3 hubspot_pull.py https://api.hubapi.com --run-date YYYY-MM-DD --scratch <dir>
"""
import json, sys, os, urllib.request, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run
import ch_secret

RUN, ns = parse_run("HubSpot company pulls", [(("base",), {"nargs": "?", "default": "https://api.hubapi.com"})])
BASE = ns.base

AUTH = ch_secret.auth_headers('hubspot')

def check_auth():
    req = urllib.request.Request(BASE + '/crm/v3/objects/companies?limit=1', headers=AUTH)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status == 200:
                return
    except Exception as e:
        raise SystemExit(f'HubSpot auth failed ({type(e).__name__}: {e})')
    raise SystemExit('HubSpot auth failed')

check_auth()
print('hubspot auth OK (%s)' % ('network secret' if not AUTH else 'token'))

PROPS = RUN.cfg["hubspot"]["company_properties"]

def search(filters, outfile):
    results, after = [], None
    while True:
        body = {"filterGroups": [{"filters": filters}],
                "properties": PROPS, "limit": 100}
        if after:
            body["after"] = after
        req = urllib.request.Request(
            BASE + '/crm/v3/objects/companies/search',
            data=json.dumps(body).encode(),
            headers={**AUTH, 'Content-Type': 'application/json'},
            method='POST')
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
        for row in data.get('results', []):
            p = row.get('properties', {})
            p['hs_object_id'] = row.get('id')
            results.append(p)
        paging = data.get('paging', {}).get('next', {})
        after = paging.get('after')
        print(f'  {outfile}: {len(results)} so far (total reported {data.get("total")})')
        if not after:
            break
        time.sleep(0.25)
    with open(RUN.path(outfile), 'w') as f:
        json.dump(results, f)
    return results

print('pull (a): companies with findigs_company_id set')
a = search([{"propertyName": "findigs_company_id", "operator": "HAS_PROPERTY"}],
           'hs_findigs_companies.json')
print('total with findigs_company_id:', len(a))
n_units = sum(1 for p in a if p.get('total_units_all') not in (None, ''))
print('  of those, total_units_all set:', n_units)

print('pull (b): churned=true companies')
b = search([{"propertyName": "churned", "operator": "EQ", "value": "true"}],
           f'hs_churned_{RUN.mmdd}.json')
print('total churned=true:', len(b))
