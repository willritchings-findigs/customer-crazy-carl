"""Pre-flight contract check: do Base44, Sigma, and HubSpot still look the way config.json expects?

Usage: python3 contract_check.py https://api.hubapi.com --run-date YYYY-MM-DD --scratch <dir>

Expects in <scratch>:
  baseline_<MMDD>.json              raw Base44 GET of the target record
  sigma_probe_<element>_<MMDD>.json result of the probe query from `sigma_verify.py probes`
                                    (preferred: Sigma itself proves every column exists), or
  sigma_describe_<element>.json     raw Sigma `describe` output (fallback)
Fetches HubSpot company property names itself. Exits non-zero on any failure, listing every
failure at once, so the run stops before computing anything.
"""
import json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, SKILL_DIR
import ch_secret
from contract_cols import query_columns, documented as documented_cols, wanted


RUN, ns = parse_run("Client health contract check", [(("base",), {"nargs": "?", "default": "https://api.hubapi.com"})])
CFG = RUN.cfg
fails, notes = [], []

# Credentials: every one resolves (names and sources only, never values)
for n_, src in ch_secret.check():
    if src:
        notes.append(f"credential {n_}: {src}")
    else:
        fails.append(f"credential {n_}: missing (set {ch_secret.SECRETS[n_][0]} on the cloud environment)")

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
WANT = wanted(CFG)
for key, el in CFG["sigma"]["elements"].items():
    undocumented = sorted(QCOLS.get(key, set()) - documented_cols(el))
    if undocumented:
        fails.append(f"Sigma {key}: queries use columns not documented in config.json {undocumented}")
    want = WANT[key]
    probe = RUN.path(f"sigma_probe_{key}_{RUN.mmdd}.json")
    if os.path.exists(probe):
        try:
            d = json.load(open(probe, encoding="utf-8"))
            assert isinstance(d.get("columns"), list) and isinstance(d.get("rows"), list)
        except Exception as e:
            fails.append(f"Sigma {key}: probe result unreadable ({type(e).__name__}); re-run the probe query")
            continue
        notes.append(f"Sigma {key}: {len(want)} columns OK (probe query ran)")
        continue
    fn = f"sigma_describe_{key}.json"
    if not os.path.exists(RUN.path(fn)):
        fails.append(f"Sigma {key}: neither sigma_probe_{key}_{RUN.mmdd}.json nor {fn} saved")
        continue
    raw = open(RUN.path(fn), encoding="utf-8").read()
    try:
        ddl = json.loads(raw).get("ddl", raw)
    except (json.JSONDecodeError, AttributeError):
        ddl = raw
    if f'"{el["id"]}"' not in ddl:
        fails.append(f"Sigma {key}: describe output is not for element {el['id']}")
        continue
    gone = [w for w in want if w not in ddl]
    if gone:
        fails.append(f"Sigma {key}: columns not found {gone}")
    else:
        notes.append(f"Sigma {key}: {len(want)} columns OK (describe)")

# HubSpot company properties
try:
    req = urllib.request.Request(ns.base + "/crm/v3/properties/companies", headers=ch_secret.auth_headers("hubspot"))
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
