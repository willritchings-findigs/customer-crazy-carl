"""Weekly client-health refresh: HubSpot pulls via api.hubapi.com.
(a) all companies with findigs_company_id set -> hs_findigs_companies.json
(b) all companies churned=true -> hs_churned_0908.json
Usage: python3 hubspot_pull.py https://api.hubapi.com
"""
import json, sys, urllib.request, time

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://api.hubapi.com'
ENV = "C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/T-tools/API Keys and Access/.env"

def find_token():
    cands = []
    with open(ENV) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            low = line.lower()
            if 'hubspot' in low and ':' in line:
                cands.append(line.split(':', 1)[1].strip().strip('"').strip("'"))
    for tok in cands:
        req = urllib.request.Request(
            BASE + '/crm/v3/objects/companies?limit=1',
            headers={'Authorization': 'Bearer ' + tok})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return tok
        except Exception:
            continue
    raise SystemExit('no working hubspot token found in .env')

TOKEN = find_token()
print('token OK (len %d)' % len(TOKEN))

PROPS = ["name", "domain", "findigs_company_id", "total_units_all",
         "account_status__c", "churned", "churn_date", "churn_reason",
         "churn_lost_to", "segment", "client_health_score_override",
         "client_health_rating", "client_health_score", "client_health_detail"]

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
            headers={'Authorization': 'Bearer ' + TOKEN,
                     'Content-Type': 'application/json'},
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
    with open(outfile, 'w') as f:
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
           'hs_churned_0908.json')
print('total churned=true:', len(b))
