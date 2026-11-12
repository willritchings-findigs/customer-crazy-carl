"""Pull every HubSpot implementation record and the owner list.

Usage: python3 pull.py https://api.hubapi.com --run-date D --scratch S
Writes hs_impl_<MMDD>.json (records with config.hubspot.properties) and hs_owners_<MMDD>.json.
"""
import json, sys, time, urllib.error, urllib.request
import im_common as C
import ch_secret

RUN, ns = C.parse_run("Pull HubSpot implementations", [(("base",), {"nargs": "?", "default": "https://api.hubapi.com"})])
H = ch_secret.auth_headers("hubspot")
HS = RUN.cfg["hubspot"]


def get(url):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            sys.exit(f"STOP: HubSpot GET -> HTTP {e.code}")


def paged(url):
    out = []
    while url:
        d = get(url)
        out += d.get("results", [])
        url = d.get("paging", {}).get("next", {}).get("link")
    return out


if __name__ == "__main__":
    recs = paged(f"{ns.base}/crm/v3/objects/{HS['object_type']}?limit=100&properties={','.join(HS['properties'])}")
    rows = [{"id": r["id"], **r["properties"]} for r in recs]
    owners = {str(o["id"]): (f"{o.get('firstName') or ''} {o.get('lastName') or ''}".strip() or o.get("email"))
              for o in paged(f"{ns.base}/crm/v3/owners?limit=200")}
    json.dump(rows, open(RUN.path(f"hs_impl_{RUN.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(owners, open(RUN.path(f"hs_owners_{RUN.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(rows)} implementation records, {len(owners)} owners")
