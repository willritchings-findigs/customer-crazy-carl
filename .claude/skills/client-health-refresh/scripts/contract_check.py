"""Pre-flight contract check: do Base44, Sigma, and HubSpot still look the way config.json expects?

Usage: python3 contract_check.py https://api.hubapi.com --run-date YYYY-MM-DD --scratch <dir>

Expects in <scratch>:
  baseline_<MMDD>.json            raw Base44 GET of the target record
  sigma_describe_<element>.json   raw Sigma `describe` output for each config.sigma.elements key
Fetches HubSpot company property names itself. Exits non-zero on any failure, listing every
failure at once, so the run stops before computing anything.
"""
import json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, SKILL_DIR
import ch_secret


def query_columns(cfg):
    """Every quoted column identifier each element's query files use: {element_key: set of '"ident"'}."""
    out = {}
    for name, q in cfg["sigma"]["queries"].items():
        el = cfg["sigma"]["elements"][q["element"]]
        sql = open(os.path.join(SKILL_DIR, "queries", name + ".sql"), encoding="utf-8").read()
        ids = {f'"{i}"' for i in re.findall(r'"([^"]+)"', sql) if i not in ("datamodel", el["id"])}
        out.setdefault(q["element"], set()).update(ids)
    return out

RUN, ns = parse_run("Client health contract check", [(("base",), {"nargs": "?", "default": "https://api.hubapi.com"})])
CFG = RUN.cfg
fails, notes = [], []

# Base44 record
try:
    rec = RUN.load(f"baseline_{RUN.mmdd}.json")
    t = CFG["target"]
    missing = [k for k in t["persisted_fields"] if k not in rec]
    if missing:
        fails.append(f"Base44: record missing fields {missing}")
    if rec.get("cache_key") != t["cache_key"]:
        fails.append(f"Base44: cache_key is {rec.get('cache_key')!r}, expected {t['cache_key']!r}")
    n = len(rec.get("accounts") or [])
    if n != t["expected_account_count"]:
        fails.append(f"Base44: {n} accounts, config expects {t['expected_account_count']} (confirm, then update config)")
    else:
        notes.append(f"Base44: {n} accounts, fields OK")
except FileNotFoundError as e:
    fails.append(f"Base44: baseline file not found ({e.filename})")

# Sigma columns: everything config documents, plus everything the query files actually use
QCOLS = query_columns(CFG)
for key, el in CFG["sigma"]["elements"].items():
    fn = f"sigma_describe_{key}.json"
    if not os.path.exists(RUN.path(fn)):
        fails.append(f"Sigma {key}: {fn} not saved")
        continue
    raw = open(RUN.path(fn), encoding="utf-8").read()
    try:
        ddl = json.loads(raw).get("ddl", raw)
    except (json.JSONDecodeError, AttributeError):
        ddl = raw
    if f'"{el["id"]}"' not in ddl:
        fails.append(f"Sigma {key}: describe output is not for element {el['id']}")
        continue
    prefix = el.get("column_prefix", "")
    documented = {f'"{cid}"' for cid in el.get("columns", {}).values()} | {f'"{prefix}{c}"' for c in el.get("named_columns", [])}
    undocumented = sorted(QCOLS.get(key, set()) - documented)
    if undocumented:
        fails.append(f"Sigma {key}: queries use columns not documented in config.json {undocumented}")
    want = sorted(documented | QCOLS.get(key, set()))
    gone = [w for w in want if w not in ddl]
    if gone:
        fails.append(f"Sigma {key}: columns not found {gone}")
    else:
        notes.append(f"Sigma {key}: {len(want)} columns OK")

# HubSpot company properties
try:
    tok = ch_secret.get("hubspot")
    req = urllib.request.Request(ns.base + "/crm/v3/properties/companies", headers={"Authorization": "Bearer " + tok})
    with urllib.request.urlopen(req, timeout=60) as r:
        have = {p["name"] for p in json.load(r).get("results", [])}
    gone = [p for p in CFG["hubspot"]["company_properties"] if p not in have]
    if gone:
        fails.append(f"HubSpot: company properties not found {gone}")
    else:
        notes.append(f"HubSpot: {len(CFG['hubspot']['company_properties'])} properties OK")
except Exception as e:
    fails.append(f"HubSpot: property check failed ({type(e).__name__}: {e})")

for n_ in notes:
    print("PASS", n_)
for f in fails:
    print("FAIL", f)
if fails:
    raise SystemExit(f"CONTRACT CHECK FAILED: {len(fails)} problem(s). DM Will; do not continue.")
print("CONTRACT CHECK PASSED")
