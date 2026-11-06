"""Weekly refresh: bulk Gong pull via api.gong.io raw REST (Basic auth).
Pulls all calls in the run window via /v2/calls/extensive with parties + brief, saves pages to
<scratch>/gong_calls_p<N>.json.
Usage: python3 gong_pull.py https://api.gong.io [probe] --run-date YYYY-MM-DD --scratch <dir>
"""
import json, sys, os, base64, urllib.request, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run
import ch_secret

RUN, ns = parse_run("Gong bulk pull", [(("base",), {"nargs": "?", "default": "https://api.gong.io"}),
                                       (("mode",), {"nargs": "?", "default": None})])
BASE = ns.base
PROBE = ns.mode == 'probe'

# Basic auth = base64(access_key_id:secret) -- verified HTTP 200 on 2026-09-08.
# With a network secret (CH_PROXY_AUTH includes gong) the proxy adds the header instead.
AUTH = ch_secret.auth_headers('gong')
req = urllib.request.Request(BASE + '/v2/users?limit=1', headers=AUTH)
with urllib.request.urlopen(req, timeout=30) as r:
    assert r.status == 200
print('gong auth OK')
if PROBE:
    raise SystemExit(0)

FROM = f'{RUN.window_start_iso}T00:00:00Z'
TO = f'{RUN.iso}T23:59:59Z'
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
                                 headers={**AUTH, 'Content-Type': 'application/json'},
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
    with open(RUN.path(f'gong_calls_p{page}.json'), 'w') as f:
        json.dump(slim, f)
    rec = data.get('records', {})
    print(f'page {page}: {len(calls)} calls (cum {total} of {rec.get("totalRecords")})')
    cursor = rec.get('cursor')
    if not cursor:
        break
    time.sleep(0.5)
print('DONE pages:', page, 'calls:', total)
