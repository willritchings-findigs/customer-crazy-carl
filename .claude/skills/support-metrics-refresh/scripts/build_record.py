"""Build the SupportCache record from this run's verified Sigma results (and the FCR sample).

Usage: python3 build_record.py --run-date YYYY-MM-DD --scratch <dir> --live <live_record.json>
Inputs (in --scratch): every config.sigma.queries output, fcr_<MMDD>.json (fcr_sample.py), and the
live record (GET before the run) for the week-over-week gate.
Writes: support_record_<MMDD>.json (managed fields only) and build_summary_<MMDD>.json.
Exits 1, writing nothing, if any reconciliation or validation gate fails. Every number comes from
a saved result file; nothing is typed in.
"""
import datetime as dt, json, sys
import sm_common

R1 = lambda x: None if x is None else round(float(x), 1)
R2 = lambda x: None if x is None else round(float(x), 2)
PCT = lambda a, b: None if not b else round(100.0 * a / b, 1)
PCT2 = lambda a, b: None if not b else round(100.0 * a / b, 2)


def rows(run, name):
    d = run.load(f"{name}_{run.mmdd}.json")
    return [dict(zip(d["columns"], r)) for r in d["rows"]]


class Gate:
    def __init__(self):
        self.fails, self.notes = [], []

    def check(self, ok, msg):
        (self.notes if ok else self.fails).append(("ok   " if ok else "FAIL ") + msg)


def build(run, live, fcr):
    cfg, g = run.cfg, Gate()
    anchor = run.date
    d7s = (anchor - dt.timedelta(days=7)).isoformat()
    d30s = (anchor - dt.timedelta(days=30)).isoformat()
    last = (anchor - dt.timedelta(days=1)).isoformat()
    cats = {k: v for k, v in cfg["categories"].items() if not k.startswith("_")}
    chans = cfg["channels"]
    reported = cfg["segments"]["reported"]
    spam = cfg["spam_category"]

    s1 = {r["segment"]: r for r in rows(run, "s1_kpis_segment")}
    s2 = rows(run, "s2_kpis_all")[0]
    s3 = rows(run, "s3_category_channel")
    s4 = rows(run, "s4_pet_sla")[0]
    s5 = rows(run, "s5_sla_segment")
    s6 = {r["bucket"]: r for r in rows(run, "s6_trend")}
    s7 = {r["bucket"]: r["applicants"] for r in rows(run, "s7_funnel")}
    s8p = rows(run, "s8_priority")
    s8a = rows(run, "s8_agents")
    s9 = rows(run, "s9_category_segment")
    s10 = rows(run, "s10_needs_attention")
    s11 = rows(run, "s11_open_backlog")
    s12 = rows(run, "s12_friction")
    s13 = rows(run, "s13_user_types")

    n30, n7 = s2["n_d30"], s2["n_d7"]
    spam30 = sum(r["n_d30"] for r in s3 if r["category"] == spam)
    spam7 = sum(r["n_d7"] for r in s3 if r["category"] == spam)
    apps7 = s7.get("d7", 0)
    apps30 = apps7 + s7.get("d30_only", 0)

    # ---- reconciliation: every view must add up to the same headline -------------------------
    g.check(sum(r["n_d30"] for r in s1.values()) == n30 and sum(r["n_d7"] for r in s1.values()) == n7,
            f"segments sum to headline ({n30} / {n7})")
    g.check(sum(r["n_d30"] for r in s3) - spam30 == n30 and sum(r["n_d7"] for r in s3) - spam7 == n7,
            f"category x channel minus spam ({spam30} / {spam7}) = headline")
    g.check(sum(r["n_d30"] for r in s9) == sum(r["n_d30"] for r in s3), "category x segment = category x channel")
    g.check(sum(r["n_d30"] for r in s5) == n30 and sum(r["n_d7"] for r in s5) == n7, "SLA base = headline")
    for view in ["all"] + reported:
        want = n30 if view == "all" else s1.get(view, {}).get("n_d30", 0)
        g.check(sum(r["n"] for r in s8p if r["view"] == view) == want, f"priority rows ({view}) = {want}")
        g.check(sum(r["n"] for r in s8a if r["view"] == view) == want, f"agent rows ({view}) = {want}")
    g.check(s6.get("w0", {}).get("ticket_volume") == n7, "trend week 0 = d7 volume")
    g.check(s7.get("w0") == apps7, "funnel week 0 = d7 applicants")
    g.check(len(s6) == 12 and all(f"w{k}" in s6 for k in range(12)), "trend has weeks w0-w11")
    g.check(all(f"w{k}" in s7 for k in range(12)), "funnel has weeks w0-w11")

    # ---- validation gates -------------------------------------------------------------------
    unknown_cats = sorted({r["category"] for r in s3} - set(cats))
    g.check(not unknown_cats, f"no unlabelled categories {unknown_cats or ''}")
    unknown_ch = sorted({r["channel"] for r in s3 if r["category"] != spam} - set(chans))
    g.check(not unknown_ch, f"no unknown channels {unknown_ch or ''}")
    other_share = 100.0 * s1.get("other", {}).get("n_d30", 0) / n30 if n30 else 100
    g.check(other_share <= cfg["segments"]["max_other_share_pct"],
            f"unclassified requester types {other_share:.2f}% <= {cfg['segments']['max_other_share_pct']}%"
            f" (values: {', '.join(f'{r['user_type']} {r['n_d30']}' for r in s13) or 'none'})")
    g.check(n30 >= cfg["validation"]["min_d30_tickets"], f"d30 volume {n30} >= {cfg['validation']['min_d30_tickets']}")
    live_n30 = (live.get("kpis") or {}).get("ticket_volume", {}).get("d30")
    if live_n30:
        wow = 100.0 * (n30 - live_n30) / live_n30
        g.check(abs(wow) <= cfg["validation"]["max_week_over_week_volume_change_pct"],
                f"d30 volume vs live {live_n30}: {wow:+.1f}% (limit +/-{cfg['validation']['max_week_over_week_volume_change_pct']}%)")
    g.check(fcr["d30"]["closed_n"] > 0 and fcr["d7"]["closed_n"] > 0, "FCR sample has d7 and d30 tickets")

    # ---- KPIs -------------------------------------------------------------------------------
    seg = lambda key, f=R1: {s: {"d7": f(s1[s][key.replace("{w}", "d7")]), "d30": f(s1[s][key.replace("{w}", "d30")])}
                             for s in reported if s in s1}
    win_note = (f"Trailing windows: d7 = {d7s} to {last}, d30 = {d30s} to {last} (the run date's partial day "
                f"excluded). Pet-related tickets excluded: Pylon Case Sub Category in pet_verification_dispute / "
                f"pet_policy_question / pet_fee_refund_request, OR Case Category pets_disputes_consumer_requests with "
                f"no sub-category, OR Case Subject mentions 'pet' ({s4['n_d7']:,} pet tickets excluded from d7, "
                f"{s4['n_d30']:,} from d30). Spam excluded everywhere except the By Category list "
                f"({spam7:,} d7 / {spam30:,} d30).")
    sla_rows = lambda pred, w: (sum(r[f"hit_{w}"] for r in s5 if pred(r)), sum(r[f"n_{w}"] for r in s5 if pred(r)))
    sla = lambda pred, w, f=PCT: f(*sla_rows(pred, w))
    sla_note = ("Share of tickets whose first response came within the channel target (chat and Slack 2 min, email "
                "and form 4 h). Pet and spam excluded; a ticket with no first response counts as a miss. Exact census "
                f"from Sigma Support Cases BI, refreshed {run.iso}. Method changed 2026-11-12 (Will): the earlier "
                "figure counted answered tickets only and included pet and spam.")
    kpis = {
        "ticket_volume": {"d7": n7, "d30": n30, "spam_excluded_d7": spam7, "spam_excluded_d30": spam30,
                          "by_segment": {s: {"d7": s1[s]["n_d7"], "d30": s1[s]["n_d30"]} for s in reported if s in s1},
                          "pet_exclusion_note": win_note},
        "median_ttfr_minutes": {"d7": R1(s2["ttfr_med_d7"]), "d30": R1(s2["ttfr_med_d30"]),
                                "by_segment": seg("ttfr_med_{w}"),
                                "note": f"Refreshed {run.iso} from Pylon first response (TICKET_TIME_TO_ASSIGNED_HOURS), "
                                        "pet and spam excluded. The median sits on a whole-minute boundary, so small "
                                        "shifts move it by a full minute."},
        "sla_within_target_pct": {
            "d7": sla(lambda r: True, "d7"), "d30": sla(lambda r: True, "d30"),
            "chat_d7": sla(lambda r: r["channel"] == "chatWidget", "d7"),
            "email_d7": sla(lambda r: r["channel"] == "email", "d7"),
            "by_segment": {**{s: {"d30": sla(lambda r, s=s: r["segment"] == s, "d30", PCT2),
                                  "d7": sla(lambda r, s=s: r["segment"] == s, "d7", PCT2)} for s in reported},
                           "note": "Segment = Pylon requester type, bucketed by shared/sql/support_segment.sql "
                                   "(property_manager includes Landlord / Portfolio Admin variants; applicant "
                                   "includes Guarantor). Tickets with no requester type are in the overall figure only."},
            "last_computed": run.iso, "note": sla_note},
        "fcr_pct": {"d7": PCT(fcr["d7"]["fcr_n"], fcr["d7"]["closed_n"]), "d30": PCT(fcr["d30"]["fcr_n"], fcr["d30"]["closed_n"]),
                    "n_d7": fcr["d7"]["closed_n"], "n_d30": fcr["d30"]["closed_n"],
                    "note": fcr["note"], "methodology": "pylon_sample_scripted", "last_computed": run.iso,
                    "by_segment": {**{s: {"pct": PCT(v["fcr_n"], v["closed_n"]), "n": v["closed_n"]}
                                      for s, v in fcr["by_segment"].items()},
                                   "note": "Same sample, all sampled days pooled, split by Pylon requester type."}},
        "pm_csat": {"d7": R2(s1["property_manager"]["csat_avg_d7"]), "d30": R2(s1["property_manager"]["csat_avg_d30"]),
                    "n_d7": s1["property_manager"]["csat_n_d7"], "n_d30": s1["property_manager"]["csat_n_d30"]},
        "applicant_csat": {"d7": R2(s1["applicant"]["csat_avg_d7"]), "d30": R2(s1["applicant"]["csat_avg_d30"]),
                           "n_d7": s1["applicant"]["csat_n_d7"], "n_d30": s1["applicant"]["csat_n_d30"]},
        "tickets_pct_of_apps": {"d7": PCT(n7, apps7), "d30": PCT(n30, apps30),
                                "applicant_only_d7": PCT(s1["applicant"]["n_d7"], apps7),
                                "note": f"Tickets (pet and spam excluded) per 100 people who started an application in "
                                        f"the same window (User Application Funnel, first event): {apps7:,} in d7, "
                                        f"{apps30:,} in d30. Refreshed {run.iso}."},
        "handled_without_escalation_pct": {"d7": R2(s2["hwe_d7"]), "d30": R2(s2["hwe_d30"]), "by_segment": seg("hwe_{w}", R2)},
        "median_resolution_minutes": {"d7": R1(s2["res_med_d7"]), "d30": R1(s2["res_med_d30"]), "by_segment": seg("res_med_{w}"),
                                      "note": f"Refreshed {run.iso} from TICKET_RESOLUTION_HOURS, pet and spam excluded, "
                                              "same windows as ticket volume."},
        "pet_sla": {"d7": PCT(s4["le24_d7"], s4["n_d7"]), "d30": PCT(s4["le24_d30"], s4["n_d30"]),
                    "n_d7": s4["n_d7"], "n_d30": s4["n_d30"], "target": "within 24h",
                    "median_ttfr_minutes_d30": round(s4["median_min_d30"]) if s4["median_min_d30"] is not None else None,
                    "note": f"Pet-verification tickets get their own target, separate from the channel SLA. Refreshed "
                            f"{run.iso}: {PCT(s4['le24_d30'], s4['n_d30'])}% answered within 24h over 30 days "
                            f"({s4['le24_d30']:,} of {s4['n_d30']:,}; the {s4['null_d30']:,} with no first response "
                            f"count as misses), {PCT(s4['le4_d30'], s4['n_d30'])}% within 4h. Not comparable to the "
                            "chat/email/form SLA figures."},
    }
    csat_note = (f"Refreshed {run.iso}. The 7-day sample is small (PM n={kpis['pm_csat']['n_d7']}, applicant "
                 f"n={kpis['applicant_csat']['n_d7']}): treat d7 as directional. Counts are survey responses to tickets "
                 "created in each window, so they grow as responses arrive.")
    kpis["pm_csat"]["note"] = kpis["applicant_csat"]["note"] = csat_note

    # ---- channel and category ---------------------------------------------------------------
    def tally(rs, key, pred=lambda r: True):
        out = {}
        for r in rs:
            if pred(r):
                o = out.setdefault(r[key], [0, 0])
                o[0] += r["n_d7"]; o[1] += r["n_d30"]
        return out
    ch = tally(s3, "channel", lambda r: r["category"] != spam)
    by_channel = [{"channel": v["label"], "d7": ch.get(k, [0, 0])[0], "d30": ch.get(k, [0, 0])[1],
                   "share_30d_pct": PCT(ch.get(k, [0, 0])[1], n30), "sla_target": v["sla_target"]}
                  for k, v in chans.items()]
    ct = tally(s3, "category")
    tot30 = sum(v[1] for v in ct.values())
    by_category = [{"category": lab, "d7": ct.get(k, [0, 0])[0], "d30": ct.get(k, [0, 0])[1],
                    "share_30d_pct": PCT(ct.get(k, [0, 0])[1], tot30)} for k, lab in cats.items()]
    by_cat_seg = {}
    for s in reported:
        cs = tally(s9, "category", lambda r, s=s: r["segment"] == s)
        st = sum(v[1] for v in cs.values())
        by_cat_seg[s] = [{"category": lab, "d7": cs.get(k, [0, 0])[0], "d30": cs.get(k, [0, 0])[1],
                          "share_30d_pct": PCT(cs.get(k, [0, 0])[1], st)} for k, lab in cats.items()]

    # ---- friction themes --------------------------------------------------------------------
    flabels = {**cats, **{k: v for k, v in cfg.get("friction_category_labels", {}).items() if not k.startswith("_")}}
    friction = []
    for c in [k for k in cfg["friction_themes"] if not k.startswith("_")]:
        rs = [r for r in s12 if r["category"] == c]
        total = sum(r["n_d30"] for r in rs)
        oth = sum(r["n_d30"] for r in rs if r["theme"] == "Other")
        th = sorted((r for r in rs if r["theme"] != "Other"), key=lambda r: (-r["n_d30"], r["theme"]))
        friction.append({"category": c, "category_label": flabels[c], "window_days": 30, "total": total,
                         "themes": [{"theme": r["theme"], "count": r["n_d30"], "pct": PCT(r["n_d30"], total)} for r in th],
                         "other_count": oth, "other_pct": PCT(oth, total)})

    # ---- 12-week trend (oldest first) -------------------------------------------------------
    trend = []
    for k in range(11, -1, -1):
        w = s6[f"w{k}"]
        trend.append({"week_start": (anchor - dt.timedelta(days=7 * (k + 1))).isoformat(),
                      "ticket_volume": w["ticket_volume"], "median_ttfr_min": R1(w["median_ttfr_min"]),
                      "sla_pct": PCT(w["sla_hits"], w["ticket_volume"]), "pm_csat": R2(w["pm_csat"]),
                      "applicant_csat": R2(w["applicant_csat"]),
                      "tickets_per_100_apps": PCT(w["ticket_volume"], s7[f"w{k}"])})

    # ---- priority and agent -----------------------------------------------------------------
    def prio(view):
        rs = sorted((r for r in s8p if r["view"] == view), key=lambda r: -r["n"])
        t = sum(r["n"] for r in rs)
        return rs, t
    prs, pt = prio("all")
    by_priority = [{"priority": r["priority"], "count": r["n"], "open": r["open_n"]} for r in prs]
    pbreak = lambda view: [{"priority": r["priority"], "count": r["n"], "pct": PCT(r["n"], prio(view)[1])} for r in prio(view)[0]]
    top_n = cfg["breakdowns"]["top_agents"]

    def agents(view):
        rs = [r for r in s8a if r["view"] == view]
        named = sorted((r for r in rs if r["agent"] not in ("Other", "Unassigned")), key=lambda r: (-r["n"], r["agent"]))
        return rs, named
    _, named_all = agents("all")
    by_agent = [{"agent": r["agent"], "count": r["n"], "open": r["open_n"],
                 "avg_resolution_hours": R1(r["res_hours_sum"] / r["res_n"]) if r["res_n"] else None} for r in named_all]

    def abreak(view):
        rs, named = agents(view)
        t = sum(r["n"] for r in rs)
        top = named[:top_n]
        un = sum(r["n"] for r in rs if r["agent"] == "Unassigned")
        other = t - sum(r["n"] for r in top) - un
        out = [{"agent": r["agent"], "count": r["n"], "pct": PCT(r["n"], t)} for r in top]
        return out + [{"agent": "Unassigned", "count": un, "pct": PCT(un, t)}, {"agent": "Other", "count": other, "pct": PCT(other, t)}]

    # ---- Needs Attention --------------------------------------------------------------------
    na = cfg["needs_attention"]
    tickets = []
    for r in s10:
        created = dt.datetime.fromisoformat(r["created_at"])
        tickets.append({"ticket_id": r["ticket_number"], "subject": r["subject"], "category": r["category"],
                        "priority": r["priority"], "status": r["status"], "agent": r["agent"],
                        "account_name": r["account_name"], "created_at": created.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "age": (anchor - created.date()).days, "is_tes": bool(r["is_tes"]),
                        "user_type_segment": r["segment"], "url": na["ticket_url"].format(number=r["ticket_number"])})
    waiting = [r for r in s11 if r["status"] in na["waiting_on_findigs_statuses"] and r["segment"] in reported]
    in_window = sum(r["n"] for r in waiting if r["age_band"] != "c_over_90d")
    stale = sum(r["n"] for r in waiting if r["age_band"] == "c_over_90d")
    g.check(len(tickets) == min(in_window, na["limit"]), f"Needs Attention list {len(tickets)} = min({in_window} waiting, {na['limit']})")

    record = {
        "computed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "kpis": kpis, "by_channel": by_channel, "by_category": by_category, "friction_themes": friction,
        "trend_12wk": trend, "by_priority": by_priority, "by_agent": by_agent,
        "priority_breakdown": pbreak("all"), "agent_breakdown": abreak("all"),
        "priority_breakdown_by_segment": {s: pbreak(s) for s in reported},
        "agent_breakdown_by_segment": {s: abreak(s) for s in reported},
        "by_category_by_segment": by_cat_seg,
        "by_category_by_segment_methodology": (
            f"Exact 30-day census from Sigma Support Cases BI, refreshed {run.iso}, pet-excluded. Segment = Pylon "
            "requester type bucketed by shared/sql/support_segment.sql; tickets with no requester type are left out of "
            "both lists. Shares are of each segment's own total (spam included here, as in By Category)."),
        "tickets": tickets,
    }
    backlog = {}
    for r in s11:
        backlog.setdefault(r["status"], [0, 0, 0])[["a_0_30d", "b_30_90d", "c_over_90d"].index(r["age_band"])] += r["n"]
    summary = {"run_date": run.iso, "gates": g.notes + g.fails, "failed": bool(g.fails),
               "needs_attention": {"listed": len(tickets), "waiting_within_90d": in_window, "stale_over_90d": stale},
               "open_backlog_by_status_0_30_30_90_over_90": backlog,
               "unclassified_requester_types": {r["user_type"]: r["n_d30"] for r in s13},
               "applicants": {"d7": apps7, "d30": apps30}}
    return record, summary, g


if __name__ == "__main__":
    run, ns = sm_common.get_run("Build the SupportCache record", [
        (("--live",), {"required": True, "help": "live SupportCache record JSON (GET before the run)"})])
    live = json.load(open(ns.live, encoding="utf-8"))
    live = live[0] if isinstance(live, list) else live
    fcr = run.load(f"fcr_{run.mmdd}.json")
    record, summary, g = build(run, live, fcr)
    print("\n".join(summary["gates"]))
    if g.fails:
        print(f"\nSTOP: {len(g.fails)} gate(s) failed; no record written.")
        sys.exit(1)
    json.dump(record, open(run.path(f"support_record_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(summary, open(run.path(f"build_summary_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nwrote support_record_{run.mmdd}.json and build_summary_{run.mmdd}.json")
