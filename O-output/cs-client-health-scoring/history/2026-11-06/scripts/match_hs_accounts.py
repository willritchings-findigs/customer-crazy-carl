#!/usr/bin/env python3
"""hs_account_match.json v3 — exact / phrase / units-confirmed token / full2; strict churn pool."""
# Usage: python3 match_hs_accounts.py --run-date YYYY-MM-DD --scratch <dir>
import json, os, re, sys, unicodedata
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run

RUN, _ = parse_run("Match Sigma accounts to HubSpot companies")
SCRATCH = RUN.scratch
def load(fn): return json.load(open(os.path.join(SCRATCH, fn)))

GENERIC = {"property","management","properties","realty","real","estate","group","parent","llc","inc",
           "co","company","companies","corp","corporation","homes","home","rental","rentals","residential",
           "services","solutions","team","partners","llp","lp","pllc","pc","the","and","of","dba","fka",
           "incorporated","ltd","realtors","mgmt","holdings","its","a"}
LEGAL = {"llc","inc","incorporated","corp","corporation","ltd","llp","lp","pllc","pc","co","parent"}

def norm(name):
    if not name: return ""
    s = unicodedata.normalize("NFKD", str(name))
    s = s.replace("’","'").replace("‘","'").replace("“",'"').replace("”",'"').lower()
    s = re.sub(r"[.,'\"()&/\[\]]", " ", s).replace("-", " ")
    toks = []
    for t in s.split():
        if t in {"and","the","of","dba","fka"}: continue
        if t == "rpm": toks += ["real","property","management"]
        elif t == "pm": toks += ["property","management"]
        elif t == "mgmt": toks.append("management")
        else: toks.append(t)
    return " ".join(toks)

def phrase(n):
    return " ".join(t for t in norm(n).split() if t not in LEGAL)

def sig_tokens(name):
    return {t for t in norm(name).split() if t not in GENERIC and len(t) >= 2}

# hand-adjudicated 2026-09-14 (see weekly report): force or forbid specific pairings
ALIAS = {  # sigma name -> exact HubSpot record name
    "Team Cadwell Investments DBA Park Place PM": "Park Place Property Management dba Resolute RDM",
    # verified 2026-09-14 (units + name submatch; other "Howard *" records are unrelated brands):
    "Howard Management Group Parent": "Howard Management Group",
    "MJW Investments Parent": "MJW Investments",
}
BLOCK = {  # sigma name -> HubSpot names that must never match it
    "Carolina Management Parent": {"Carolina Management Partners DBA Real Property Management Queen City"},
    "Taylor & Taylor Realty Services LLC": {"Taylor Made Property Management"},
    "Bridge Tower Properties LLC": {"Tower Bridge Property Management"},
    "Place Management LLC": set(),  # keeps exact behavior; listed for documentation
}

base = load(f"baseline_{RUN.mmdd}.json")
def aname(a): return a.get("resolved_name_sigma") or a.get("input_name")
accounts = base["accounts"]
hs_main = load("hs_findigs_companies.json")
hs_churned = load(f"hs_churned_{RUN.mmdd}.json")

def units_of(r):
    try:
        u = float(r.get("total_units_all") or 0)
        return u if u > 0 else None
    except (TypeError, ValueError):
        return None

def contains(a, b):
    return f" {b} " in f" {a} "

def match_pool(pool, nm, base_units, strict):
    if nm in ALIAS:
        hit = [r for r in pool if r.get("name") == ALIAS[nm]]
        if hit:
            return hit, "ALIAS"
    pool = [r for r in pool if r.get("name") not in BLOCK.get(nm, set())]
    k, ph, sig = norm(nm), phrase(nm), sig_tokens(nm)
    exact = [r for r in pool if norm(r.get("name")) == k or phrase(r.get("name")) == ph]
    if exact:
        return exact, "A-exact"
    if not sig:
        return [], "NONE"
    cands = [r for r in pool if sig & sig_tokens(r.get("name"))]
    if not cands:
        return [], "NONE"
    if strict:
        # churn pool: beyond exact, require >=2 shared distinctive tokens with full containment.
        # Phrase containment is NOT enough here -- a legal-suffix-stripped generic phrase like
        # "residential leasing management" is contained in unrelated company names (Avenue leak, 9/14).
        full2 = [r for r in cands if (sig <= sig_tokens(r.get("name")) or sig_tokens(r.get("name")) <= sig)
                 and len(sig & sig_tokens(r.get("name"))) >= 2]
        return (full2, "C-full2") if len(full2) == 1 else ([], "NONE")
    # phrase containment either direction
    phc = [r for r in cands if ph and (contains(phrase(r.get("name")), ph) or contains(ph, phrase(r.get("name"))))]
    if len(phc) == 1:
        return phc, "C-phrase"
    if len(phc) > 1:
        if base_units:
            bu = [r for r in phc if units_of(r) == float(base_units)]
            if len(bu) == 1: return bu, "C-phrase+units"
        live = [r for r in phc if r.get("account_status__c") == "Live"]
        if len(live) == 1: return live, "C-phrase+live"
        return [], f"REJECT-phrase-ambig({[r['name'] for r in phc[:3]]})"
    # units-confirmed token overlap
    if base_units and float(base_units) >= 20:
        bu = [r for r in cands if units_of(r) == float(base_units)]
        if len(bu) == 1:
            return bu, "C-token+units"
    full2 = [r for r in cands if (sig <= sig_tokens(r.get("name")) or sig_tokens(r.get("name")) <= sig)
             and len(sig & sig_tokens(r.get("name"))) >= 2]
    if len(full2) == 1:
        return full2, "C-full2"
    return [], "NONE"

_BAND_SEVERITY = {"Red": 2, "Yellow": 1, "Green": 0}

def override_fields(records):
    """client_health_score_override (2026-09-22 CX ask, corrected 2026-09-29): when set,
    the composite should mirror client_health_rating (the CSM-determined churn risk),
    NOT a hardcoded Red -- most override=true accounts are actually Yellow in practice.
    Picks the most severe rating if multiple matched HubSpot records disagree (rare;
    normally one rollup matches exactly one overridden company) and notes the conflict."""
    overridden = [r for r in records if str(r.get("client_health_score_override")).lower() == "true"]
    if not overridden:
        return {"hs_health_override_any": False, "hs_health_override_rating": None,
                "hs_health_override_score": None, "hs_health_override_detail": None,
                "hs_health_override_note": None}
    valid = [r for r in overridden if r.get("client_health_rating") in _BAND_SEVERITY]
    if not valid:
        return {"hs_health_override_any": False, "hs_health_override_rating": None,
                "hs_health_override_score": None, "hs_health_override_detail": None,
                "hs_health_override_note": f"override set on {[r.get('name') for r in overridden]} but "
                                            f"client_health_rating is blank/invalid -- ran as normal instead"}
    chosen = max(valid, key=lambda r: _BAND_SEVERITY[r["client_health_rating"]])
    ratings = {r["client_health_rating"] for r in valid}
    note = None
    if len(ratings) > 1:
        note = (f"multiple matched HubSpot records disagree on rating "
                f"({[(r.get('name'), r.get('client_health_rating')) for r in valid]}) -- took most severe")
    return {"hs_health_override_any": True, "hs_health_override_rating": chosen["client_health_rating"],
            "hs_health_override_score": chosen.get("client_health_score"),
            "hs_health_override_detail": chosen.get("client_health_detail"), "hs_health_override_note": note}

match, log = {}, defaultdict(list)
for a in accounts:
    nm = aname(a)
    bu = a.get("total_units_sold_hubspot")
    recs, stage = match_pool(hs_main, nm, bu, strict=False)
    crecs, cstage = match_pool(hs_churned, nm, None, strict=True)
    if recs or crecs:
        units_vals = [u for u in (units_of(r) for r in recs) if u]
        match[nm] = {
            "hs_names": [r.get("name") for r in recs] + [c.get("name") for c in crecs
                         if c.get("name") not in {r.get("name") for r in recs}],
            "hs_object_id": recs[0].get("hs_object_id") if recs else crecs[0].get("hs_object_id"),
            "total_units_all": max(units_vals) if units_vals else None,
            "domains": sorted({r.get("domain") for r in recs + crecs if r.get("domain")}),
            "account_status__c": ", ".join(sorted({str(r.get("account_status__c")) for r in recs if r.get("account_status__c")})),
            "hs_churned_any": any(str(r.get("churned")).lower() == "true" for r in recs + crecs),
            **override_fields(recs + crecs),
            "hs_churn_dates": sorted({r.get("churn_date") for r in recs + crecs
                                      if str(r.get("churned")).lower() == "true" and r.get("churn_date")}),
            "hs_churn_reasons": sorted({r.get("churn_reason") for r in recs + crecs
                                        if str(r.get("churned")).lower() == "true" and r.get("churn_reason")}),
            "match_stage": stage if recs else f"churn-only:{cstage}",
        }
    log[stage.split("(")[0] if recs else ("churn-only" if crecs else stage.split("(")[0])].append(nm)

json.dump(match, open(os.path.join(SCRATCH, "hs_account_match.json"), "w"), indent=1)
print("matched:", len(match), "/", len(accounts))
for stage, nms in sorted(log.items()):
    print(f"  {stage}: {len(nms)}")

print("\n-- non-exact main-pool matches (audit) --")
for nm, e in sorted(match.items()):
    if not e["match_stage"].startswith("A-exact"):
        print(f"  [{e['match_stage']}] {nm!r} -> {e['hs_names'][:2]} units={e['total_units_all']}")

print("\n-- churn-pool hits on non-churned baseline accounts (audit) --")
bymap = {aname(a): a for a in accounts}
for nm, e in sorted(match.items()):
    if e["hs_churned_any"]:
        bb = ((bymap[nm].get("composite_score_partial") or {}).get("band"))
        print(f"  {nm!r} (baseline band={bb}) churn_dates={e['hs_churn_dates']} names={e['hs_names'][:2]}")

same = changed = newly = lost = 0
chg, lst = [], []
for a in accounts:
    nm, old = aname(a), a.get("total_units_sold_hubspot")
    new = (match.get(nm) or {}).get("total_units_all")
    if old is not None and new is not None:
        if abs(float(old) - float(new)) < 0.5: same += 1
        else: changed += 1; chg.append((nm, old, new))
    elif new is not None: newly += 1
    elif old is not None: lost += 1; lst.append(nm)
print(f"\nunits vs baseline: same={same} changed={changed} newly={newly} lost={lost}")
print("CHANGED:", *[f"  {c}" for c in chg], sep="\n")
print("LOST (carry-forward):", lst)
