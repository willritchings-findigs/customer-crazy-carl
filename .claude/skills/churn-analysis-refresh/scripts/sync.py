"""Work out this week's changes to the Churn page, with evidence. Changes nothing itself.

Usage: python3 sync.py https://api.hubapi.com --run-date D --scratch S
Reads (in --scratch): baseline_<MMDD>.json (ChurnCache GET), health_<MMDD>.json (AccountHealthCache
GET), and the newest Client Health hs_account_match.json from history.
Pulls from HubSpot: every company with churned=true, every Failure-to-Launch company, and the
deals of each company it needs an ACV for.
Writes plan_<MMDD>.json:
  remove_at_risk  At Risk accounts that are no longer Client Health Red
  add_at_risk     new Red accounts, with HubSpot ID, segment, AM, ACV and how it was found
  add_churned     new churns that meet the auto-add rule, or are in config approved_additions
  candidates      churned=true companies not on the page that were NOT added, with the reason
  ftl_candidates  Failure-to-Launch companies not on the page (propose-only, never added)
  flags           anything a person should look at
Stops (exit 1) if the Client Health record is older than config.health_source.max_age_days.
"""
import datetime as dt, json, sys, time, urllib.request
import cr_common as C
import ch_secret

RUN, ns = C.parse_run("Churn sync plan", [(("base",), {"nargs": "?", "default": "https://api.hubapi.com"})])
BASE, CFG = ns.base, RUN.cfg
H = ch_secret.auth_headers("hubspot")
HS = CFG["hubspot"]
TX = CFG["taxonomy"]
NC = CFG["new_churns"]


def api(path, body=None):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={**H, "Content-Type": "application/json"}, method="POST" if body is not None else "GET")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit(f"STOP: HubSpot {path} -> HTTP {e.code}")


def search_companies(filters):
    out, after = [], None
    while True:
        body = {"filterGroups": [{"filters": filters}], "properties": HS["company_properties"], "limit": 100}
        if after:
            body["after"] = after
        d = api("/crm/v3/objects/companies/search", body)
        for x in d["results"]:
            p = x["properties"]
            p["id"] = x["id"]
            out.append(p)
        after = d.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out
        time.sleep(0.2)


def deals_of(cid):
    a = api(f"/crm/v4/objects/companies/{cid}/associations/deals?limit=500")
    ids = [str(x["toObjectId"]) for x in a.get("results", [])]
    out = []
    for i in range(0, len(ids), 100):
        d = api("/crm/v3/objects/deals/batch/read", {"properties": ["dealname", "amount", "pipeline", "dealstage", "closedate"],
                                                    "inputs": [{"id": x} for x in ids[i:i + 100]]})
        out += [x["properties"] for x in d["results"]]
    return out


def closed_won(deals):
    cw = HS["closed_won_stages"]
    return [d for d in deals if cw.get(d.get("pipeline")) == d.get("dealstage")]


_owners = {}


def owner_name(oid):
    if not oid:
        return None
    oid = oid.split(";")[0]
    if oid not in _owners:
        try:
            o = api(f"/crm/v3/owners/{oid}")
            _owners[oid] = " ".join(x for x in (o.get("firstName"), o.get("lastName")) if x) or None
        except SystemExit:
            _owners[oid] = None
    return _owners[oid]


def product(p):
    v = p.get("findigs_products__c") or ""
    return "DA" if "DecisionAssist" in v else "FS" if "Screening" in v else "Unknown"


def main():
    base = C.one(RUN.load(f"baseline_{RUN.mmdd}.json"))
    health = C.one(RUN.load(f"health_{RUN.mmdd}.json"))
    st = TX["statuses"]
    flags = []
    hc = C.pdate(health["computed_at"])
    age = (RUN.date - hc).days
    if age > CFG["health_source"]["max_age_days"]:
        sys.exit(f"STOP: Client Health record computed {health['computed_at']} ({age} days old, limit "
                 f"{CFG['health_source']['max_age_days']}); run Client Health first")
    mfile = C.latest_match_file(CFG)
    match = json.load(open(mfile, encoding="utf-8"))

    accts = base["accounts"]
    in_cache = {a["hubspot_company_id"] for a in accts if a.get("hubspot_company_id")}
    churned_ids = {a["hubspot_company_id"] for a in accts if a["status"] == st["churned"]}
    risk_now = {a["name"]: a for a in accts if a["status"] == st["at_risk"]}
    red = {x["input_name"]: x for x in health["accounts"]
           if (x.get("composite_score_partial") or {}).get("band") == CFG["health_source"]["red_band"]}

    # Join on HubSpot company ID first (names drift: "MGC Leasing & Property Management" on the page
    # is "MGC Leasing &Property Management, LLC" in Client Health), then on exact name.
    red_ids = {(match.get(n) or {}).get("hs_object_id"): n for n in red if (match.get(n) or {}).get("hs_object_id")}
    risk_ids = {a.get("hubspot_company_id") for a in risk_now.values() if a.get("hubspot_company_id")}
    remove_at_risk = sorted(n for n, a in risk_now.items() if n not in red and a.get("hubspot_company_id") not in red_ids)
    add_at_risk = []
    for name in sorted(n for n in red if n not in risk_now and (match.get(n) or {}).get("hs_object_id") not in risk_ids):
        x = red[name]
        m = match.get(name) or {}
        cid = m.get("hs_object_id")
        how = f"Client Health match ({m.get('match_stage')})" if cid else None
        if not cid:
            hits = search_companies([{"propertyName": "name", "operator": "EQ", "value": name}])
            if len(hits) == 1:
                cid, how = hits[0]["id"], "HubSpot exact company name"
            else:
                flags.append(f"At Risk {name}: no HubSpot company ({len(hits)} exact-name matches); ACV set to $0")
        if cid and cid in churned_ids:
            flags.append(f"At Risk {name}: HubSpot {cid} is already on the page as Churned; not added as At Risk")
            continue
        acv, resolved, deal_note = 0.0, False, "no HubSpot company"
        if cid:
            cw = closed_won(deals_of(cid))
            total = C.r2(sum(float(d.get("amount") or 0) for d in cw))
            if not cw:
                deal_note = "no Closed Won deal"
                flags.append(f"At Risk {name}: no Closed Won deal in HubSpot; ACV $0")
            elif len(cw) > HS["max_deals_before_flag"]:
                deal_note = f"{len(cw)} Closed Won deals summing ${total:,.2f}"
                override = {k: v for k, v in CFG.get("at_risk_acv_overrides", {}).items() if not k.startswith("_")}.get(cid)
                if override is not None:
                    acv, resolved = float(override), True
                    deal_note += f"; ACV ${acv:,.2f} from config.at_risk_acv_overrides"
                else:
                    flags.append(f"At Risk {name}: {deal_note}; pushed as $0 until approved "
                                 f"(add {cid} to config.at_risk_acv_overrides)")
            else:
                acv, resolved = total, True
                deal_note = f"{len(cw)} Closed Won deal(s)"
        seg = CFG["health_source"]["segment_map"].get(x.get("rubric_segment_column"))
        if not seg:
            flags.append(f"At Risk {name}: rubric segment {x.get('rubric_segment_column')!r} unmapped; segment left blank")
        add_at_risk.append({
            "entry": {"name": name, "hubspot_company_id": cid, "status": st["at_risk"], "acv": acv, "segment": seg,
                      "product_segment": None, "reason": None, "sub_reasons": [], "reason_source": "account_health_cache",
                      "effective_churn_date": None, "csm": x.get("account_manager"), "hubspot_url": C.hs_url(cid),
                      "acv_resolved": resolved, "is_ftl": None},
            "evidence": {"weeks_red": x.get("weeks_red"), "company_from": how, "deals": deal_note}})

    hs_churned = search_companies([{"propertyName": "churned", "operator": "EQ", "value": "true"}])
    json.dump(hs_churned, open(RUN.path(f"hs_churned_{RUN.mmdd}.json"), "w"))
    cutoff = RUN.date - dt.timedelta(days=NC["auto_add_window_days"])
    add_churned, candidates = [], []
    for p in hs_churned:
        cid = p["id"]
        if cid in in_cache:
            continue
        cdate = C.pdate(p.get("churn_date__c") or p.get("churn_date"))
        approved = cid in NC["approved_additions"]
        why = []
        if cid in NC["rejected_company_ids"]:
            why.append("rejected: " + NC["rejected_company_ids"][cid])
        if not approved and (not cdate or cdate < cutoff):
            why.append(f"churn date {cdate or 'blank'} is older than {NC['auto_add_window_days']} days")
        if cdate and cdate > RUN.date + dt.timedelta(days=366):
            why.append(f"churn date {cdate} is far in the future")
        if why and not approved:
            candidates.append({"hubspot_company_id": cid, "name": p.get("name"), "churn_date": str(cdate) if cdate else None,
                               "account_status": p.get("account_status__c"), "why_not_added": "; ".join(why)})
            continue
        seg = HS["segment_map"].get(p.get("segment"))
        reason_raw = (p.get("churn_reason") or "").strip()
        reason, rsrc = ("Uncategorized", "none") if not reason_raw else (reason_raw, "hubspot_field")
        deals = deals_of(cid)
        cw = closed_won(deals)
        later = [d for d in cw if cdate and C.pdate(d.get("closedate")) and C.pdate(d["closedate"]) > cdate]
        if p.get("account_status__c") in NC["contradicting_statuses"]:
            why.append(f"status is {p.get('account_status__c')}")
        if later:
            why.append(f"Closed Won deal after the churn date ({later[0].get('dealname')}, {later[0].get('closedate', '')[:10]})")
        if not seg:
            why.append(f"segment {p.get('segment')!r} unmapped")
        if reason not in TX["reason_order"]:
            why.append(f"churn_reason {reason_raw!r} is not in the taxonomy")
        if cid in NC["rejected_company_ids"]:
            why.append("rejected")
        if why:
            candidates.append({"hubspot_company_id": cid, "name": p.get("name"), "churn_date": str(cdate) if cdate else None,
                               "account_status": p.get("account_status__c"), "why_not_added": "; ".join(why)})
            continue
        acv = C.r2(sum(float(d.get("amount") or 0) for d in cw))
        add_churned.append({
            "entry": {"name": p.get("name"), "hubspot_company_id": cid, "status": st["churned"], "acv": acv, "segment": seg,
                      "product_segment": product(p), "reason": reason, "sub_reasons": [], "reason_source": rsrc,
                      "effective_churn_date": str(cdate), "csm": owner_name(p.get("csm_owner")), "hubspot_url": C.hs_url(cid),
                      "acv_resolved": True if cw else None, "is_ftl": not p.get("go_live_date__c")},
            "evidence": {"rule": "approved_additions" if approved else f"churned=true, churn date within {NC['auto_add_window_days']} days",
                         "churn_date_field": "churn_date__c" if p.get("churn_date__c") else "churn_date",
                         "closed_won_deals": len(cw), "account_status": p.get("account_status__c")}})
        if len(cw) > HS["max_deals_before_flag"]:
            flags.append(f"New churn {p.get('name')}: {len(cw)} Closed Won deals summed to ${acv:,.2f}; check the ACV")

    ftl = search_companies([{"propertyName": "account_status__c", "operator": "EQ", "value": "Failure to Launch"}])
    ftl_candidates = [{"hubspot_company_id": p["id"], "name": p.get("name"), "churned": p.get("churned")}
                      for p in ftl if p["id"] not in in_cache]
    status_by_id = {p["id"]: p.get("account_status__c") for p in hs_churned}
    still_live = sorted(a["name"] for a in accts if a["status"] == st["churned"]
                        and status_by_id.get(a["hubspot_company_id"]) in NC["contradicting_statuses"])
    not_flagged = sorted(a["name"] for a in accts if a["status"] == st["churned"] and a["hubspot_company_id"] not in status_by_id)
    plan = {"run_date": RUN.iso, "health_computed_at": health["computed_at"], "match_file": mfile,
            "red_count": len(red), "remove_at_risk": remove_at_risk, "add_at_risk": add_at_risk,
            "add_churned": add_churned, "candidates": candidates, "ftl_candidates": ftl_candidates,
            "churned_on_page_but_hubspot_status_live": still_live,
            "churned_on_page_but_hubspot_not_churned": not_flagged, "flags": flags}
    json.dump(plan, open(RUN.path(f"plan_{RUN.mmdd}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"Client Health computed {health['computed_at']} ({age}d old); {len(red)} Red")
    print(f"At Risk: -{len(remove_at_risk)} {remove_at_risk}  +{len(add_at_risk)} {[x['entry']['name'] for x in add_at_risk]}")
    print(f"New churns added: {len(add_churned)} {[x['entry']['name'] for x in add_churned]}; candidates not added: {len(candidates)}")
    print(f"FTL candidates (propose-only): {len(ftl_candidates)}")
    for f in flags:
        print("FLAG", f)


if __name__ == "__main__":
    main()
