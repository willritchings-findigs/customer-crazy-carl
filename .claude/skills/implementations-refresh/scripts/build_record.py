"""Build the ImplementationsCache record from this run's HubSpot pull.

Usage: python3 build_record.py --run-date D --scratch S
Reads hs_impl_<MMDD>.json, hs_owners_<MMDD>.json and baseline_<MMDD>.json (the live record).
Writes impl_record_<MMDD>.json and build_summary_<MMDD>.json only if every gate passes.

Every section comes from the HubSpot implementation object (system of record since 2026-11-06).
A field HubSpot doesn't have is left null and counted in the summary's gaps, never filled in.
"""
import datetime as dt, json, re, sys
import im_common as C


def num(v):
    if v in (None, ""):
        return None
    try:
        f = float(v)
        return int(f) if f == int(f) else f
    except (TypeError, ValueError):
        return None


def day(s):
    return dt.date.fromisoformat(s[:10]) if s else None


if __name__ == "__main__":
    run, _ = C.parse_run("Build the ImplementationsCache record")
    cfg, HS, R = run.cfg, run.cfg["hubspot"], run.cfg["rules"]
    rows = run.load(f"hs_impl_{run.mmdd}.json")
    owners = run.load(f"hs_owners_{run.mmdd}.json")
    base = C.one(run.load(f"baseline_{run.mmdd}.json"))
    today = run.date
    gates, fails = [], []

    def check(ok, msg):
        (gates if ok else fails).append(("ok   " if ok else "FAIL ") + msg)

    stages = HS["stages"]
    unknown = sorted({r.get("hs_pipeline_stage") for r in rows} - set(stages))
    check(not unknown, f"every record is in a known stage {unknown or ''}")
    check(len(rows) >= cfg["validation"]["min_records"], f"{len(rows)} records >= {cfg['validation']['min_records']}")

    junk_re = [re.compile(p, re.I) for p in HS["junk_name_patterns"]]
    is_junk = lambda n: bool(n) and any(p.search(n) for p in junk_re)
    url = lambda rid: f"https://app-na2.hubspot.com/contacts/{HS['portal_id']}/record/{HS['object_type']}/{rid}"
    open_labels = HS["open_stage_order"]
    label = lambda r: stages.get(r.get("hs_pipeline_stage"))
    open_raw = [r for r in rows if label(r) in open_labels]
    junk = [r for r in open_raw if is_junk(r.get("company_name"))]
    active = [r for r in open_raw if not is_junk(r.get("company_name"))]
    owned = [r for r in active if r.get("hubspot_owner_id")]
    unowned = [r for r in active if not r.get("hubspot_owner_id")]
    owner_name = lambda r: owners.get(str(r.get("hubspot_owner_id"))) if r.get("hubspot_owner_id") else None
    entered = lambda r: day(r.get("hs_v2_date_entered_current_stage")) or day(r.get("hs_createdate"))
    days_in_stage = lambda r: (today - entered(r)).days if entered(r) else None
    go_live = lambda r: r.get("impl_expected_go_live") or r.get("impl_desired_go_live") or r.get("impl_go_live")
    start = lambda r: r.get("impl_kickoff_date") or (r.get("hs_createdate") or "")[:10] or None
    pipeline_days = lambda r: num(r.get("impl_days_in_pipeline")) if r.get("impl_days_in_pipeline") else (
        (today - day(r["hs_createdate"])).days if r.get("hs_createdate") else None)

    stage_funnel = [{"stage": s, "count": sum(label(r) == s for r in active)} for s in open_labels]

    triage = []
    for r in unowned:
        created = day(r.get("hs_createdate"))
        dsc = (today - created).days if created else None
        triage.append({"hs_id": r["id"], "company_name": r.get("company_name"), "stage": label(r),
                       "segment": r.get("impl_segment"), "units": num(r.get("impl_units")), "tcv": num(r.get("impl_tcv_handoff")),
                       "pms": r.get("impl_pms"), "product": r.get("impl_product"),
                       "target_go_live": r.get("impl_go_live") or r.get("impl_expected_go_live"), "hubspot_url": url(r["id"]),
                       "days_since_created": dsc, "is_stale": bool(dsc and dsc > R["triage_stale_days"])})
    triage.sort(key=lambda x: (x["tcv"] or 0, x["units"] or 0), reverse=True)

    def overdue(r):
        g = day(go_live(r))
        return (today - g).days if g and g < today else None

    ongoing = [{"key": r["id"], "customer": r.get("company_name"), "start_date": start(r), "go_live_date": go_live(r),
                "commit_status": None, "time_in_pipeline_days": pipeline_days(r), "total_units": num(r.get("impl_units")),
                "status": label(r), "im_owner": owner_name(r), "last_updated": str(entered(r)) if entered(r) else None,
                "days_since_activity": days_in_stage(r), "pms": r.get("impl_pms"),
                "tech_scoping_complete": "No" if label(r) == open_labels[0] else "Yes", "effort": None, "priority": None,
                "notes": r.get("impl_project_health"), "days_overdue": overdue(r)} for r in owned]
    ongoing.sort(key=lambda x: (x["days_overdue"] is None, -(x["days_overdue"] or 0)))

    mini = lambda r: {"key": r["id"], "customer": r.get("company_name"), "status": label(r), "im_owner": owner_name(r),
                      "last_updated": str(entered(r)) if entered(r) else None, "days_since_activity": days_in_stage(r)}
    recent = [mini(r) for r in rows if label(r) in HS["completed_stages"] and not is_junk(r.get("company_name"))
              and entered(r) and (today - entered(r)).days <= R["recently_completed_days"]]
    recent.sort(key=lambda x: x["days_since_activity"])
    aging = [mini(r) for r in active if (days_in_stage(r) or 0) >= R["aging_days_in_stage"]]
    aging.sort(key=lambda x: -(x["days_since_activity"] or 0))

    gantt = [{"key": r["id"], "customer": r.get("company_name"), "segment": r.get("impl_segment"), "units": num(r.get("impl_units")),
              "commit_status": None, "start_date": start(r), "go_live_date": go_live(r), "effort": None, "score": None,
              "scoping_complete": "No" if label(r) == open_labels[0] else "Yes", "priority": None,
              "risk_flag": r.get("impl_project_health") in HS["at_risk_health"], "churn_risk": None, "im_owner": owner_name(r)}
             for r in owned]
    gantt.sort(key=lambda x: x["start_date"] or "9999")

    monday = today - dt.timedelta(days=today.weekday())
    weeks = [monday + dt.timedelta(weeks=k) for k in range(-R["capacity_weeks_back"], R["capacity_weeks_ahead"] + 1)]
    weekly = []
    for w in weeks:
        w_end = w + dt.timedelta(days=6)
        act = [g for g in gantt if day(g["start_date"]) and day(g["start_date"]) <= w_end
               and (not day(g["go_live_date"]) or day(g["go_live_date"]) >= w)]
        by_owner = {}
        for g in act:
            if g["im_owner"]:
                by_owner[g["im_owner"]] = by_owner.get(g["im_owner"], 0) + 1
        weekly.append({"week_start": w.isoformat(), "active_total": len(act), "active_priority_a": None, "active_committed": None,
                       "active_scoping_incomplete": sum(g["scoping_complete"] == "No" for g in act), "weighted_effort_load": None,
                       "active_by_owner": by_owner,
                       "go_lives_count": sum(1 for g in gantt if day(g["go_live_date"]) and w <= day(g["go_live_date"]) <= w_end)})

    n_t = len(triage)
    pct = lambda n: round(100 * n / n_t, 1) if n_t else None
    hygiene = {"total_all_records": len(rows), "total_active_open_stage": len(open_raw), "excluded_test_junk_count": len(junk),
               "triage_queue_count": n_t, "triage_queue_total_tcv": sum(x["tcv"] or 0 for x in triage),
               "triage_queue_total_units": sum(x["units"] or 0 for x in triage), "already_owned_in_hubspot_count": len(owned),
               "ongoing_worklist_count": len(ongoing), "aging_worklist_count": len(aging), "follow_up_count": 0,
               "recently_completed_count": len(recent),
               "pct_missing_health": pct(sum(not r.get("impl_project_health") for r in unowned)),
               "pct_missing_segment": pct(sum(not r.get("impl_segment") for r in unowned)),
               "pct_missing_tcv": pct(sum(not r.get("impl_tcv_handoff") for r in unowned))}

    check(sum(s["count"] for s in stage_funnel) == len(active) == len(triage) + len(ongoing),
          f"funnel {len(active)} = triage {len(triage)} + ongoing {len(ongoing)}")
    live_open = (base.get("hygiene") or {}).get("total_active_open_stage")
    if live_open:
        ch = 100.0 * (len(open_raw) - live_open) / live_open
        check(abs(ch) <= cfg["validation"]["max_open_change_pct"],
              f"open records {live_open} -> {len(open_raw)} ({ch:+.1f}%, limit +/-{cfg['validation']['max_open_change_pct']}%)")

    gaps = {"open_without_owner": len(unowned), "owned_without_go_live_date": sum(not go_live(r) for r in owned),
            "owned_without_kickoff_date": sum(not r.get("impl_kickoff_date") for r in owned),
            "owned_without_project_health": sum(not r.get("impl_project_health") for r in owned),
            "open_without_units": sum(num(r.get("impl_units")) is None for r in active),
            "open_without_segment": sum(not r.get("impl_segment") for r in active),
            "no_source_on_hubspot": ["board_totals (Jira)", "follow_up (Jira PDE)", "commit_status", "effort", "priority", "churn_risk"]}
    record = {"computed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"), "hygiene": hygiene,
              "stage_funnel": stage_funnel, "triage_queue": triage, "board_totals": {}, "ongoing_worklist": ongoing,
              "recently_completed": recent, "aging_worklist": aging, "capacity_gantt": gantt, "capacity_weekly": weekly, "follow_up": []}
    summary = {"run_date": run.iso, "gates": gates + fails, "failed": bool(fails), "gaps": gaps,
               "before": {k: (base.get("hygiene") or {}).get(k) for k in hygiene}, "after": hygiene,
               "owners_on_open": sorted({owner_name(r) for r in owned if owner_name(r)})}
    print("\n".join(summary["gates"]))
    if fails:
        print(f"\nSTOP: {len(fails)} gate(s) failed; no record written.")
        sys.exit(1)
    json.dump(record, open(run.path(f"impl_record_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(summary, open(run.path(f"build_summary_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nwrote impl_record_{run.mmdd}.json; gaps {gaps}")
