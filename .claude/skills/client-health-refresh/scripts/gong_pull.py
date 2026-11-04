"""Weekly refresh: bulk Gong pull via api.gong.io raw REST (Basic auth from .env).
Pulls all calls 2026-06-10 -> now via /v2/calls/extensive with parties + brief,
saves pages to gong_calls_p<N>.json. Usage: python3 gong_pull.py https://api.gong.io [probe]
"""
import json, sys, base64, urllib.request, time

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://api.gong.io'
PROBE = len(sys.argv) > 2 and sys.argv[2] == 'probe'
ENV = "C:/Users/Will Ritchings/Desktop/Claude/GTM_ENG/The Reserve/T-tools/API Keys and Access/.env"

# .env line 2 = 'Gong API Key: <152-char secret>', line 3 = 'Access Key ID: <32-char key>'
# Basic auth = base64(access_key_id:secret) -- verified HTTP 200 on 2026-09-08.
envlines = open(ENV).read().splitlines()
secret = envlines[1].split(':', 1)[1].strip()
key = envlines[2].split(':', 1)[1].strip()
TOK = base64.b64encode(f'{key}:{secret}'.encode()).decode()
req = urllib.request.Request(BASE + '/v2/users?limit=1',
                             headers={'Authorization': 'Basic ' + TOK})
with urllib.request.urlopen(req, timeout=30) as r:
    assert r.status == 200
print('gong auth OK')
if PROBE:
    raise SystemExit(0)

FROM = '2026-06-10T00:00:00Z'
TO = '2026-09-08T23:59:59Z'
cursor, page, total = None, 0, 0
while True:
    body = {
        "filter": {"fromDateTime": FROM, "toDateTime": TO},
        "contentSelector": {
            "context": "None",
            "exposedFields": {
                "parties": True,
                "content": {"brief": True}
            }
        }
    }
    if cursor:
        body["cursor"] = cursor
    req = urllib.request.Request(BASE + '/v2/calls/extensive',
                                 data=json.dumps(body).encode(),
                                 headers={'Authorization': 'Basic ' + TOK,
                                          'Content-Type': 'application/json'},
                                 method='POST')
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    calls = data.get('calls', [])
    page += 1
    total += len(calls)
    slim = []
    for c in calls:
        meta = c.get('metaData', {})
        slim.append({
            'id': meta.get('id'),
            'title': meta.get('title'),
            'started': meta.get('started'),
            'brief': (c.get('content') or {}).get('brief'),
            'parties': [
                {'email': p.get('emailAddress'), 'title': p.get('title'),
                 'affiliation': p.get('affiliation'), 'name': p.get('name')}
                for p in (c.get('parties') or [])
            ],
        })
    with open(f'gong_calls_p{page}.json', 'w') as f:
        json.dump(slim, f)
    rec = data.get('records', {})
    print(f'page {page}: {len(calls)} calls (cum {total} of {rec.get("totalRecords")})')
    cursor = rec.get('cursor')
    if not cursor:
        break
    time.sleep(0.5)
print('DONE pages:', page, 'calls:', total)
