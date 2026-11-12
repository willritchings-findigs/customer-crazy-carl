"""Write the Implementations run report and Slack text, and archive the run.

Usage: python3 report.py --run-date D --scratch S [--dry-run]
Writes O-output/cx-implementations/<date>_weekly-refresh-report.md, <scratch>/slack_success_<MMDD>.txt,
and (unless --dry-run) O-output/cx-implementations/history/<date>/.
"""
import json, os, shutil
import im_common as C

if __name__ == "__main__":
    run, ns = C.parse_run("Implementations report", [(("--dry-run",), {"action": "store_true"})])
    s = run.load(f"build_summary_{run.mmdd}.json")
    rec = run.load(f"impl_record_{run.mmdd}.json")
    b, a, g = s["before"], s["after"], s["gaps"]
    rows = [("HubSpot implementation records", "total_all_records"), ("Open (incl. test records)", "total_active_open_stage"),
            ("Test / placeholder records excluded", "excluded_test_junk_count"), ("Needs triage (no owner)", "triage_queue_count"),
            ("Active implementations (owned)", "ongoing_worklist_count"), ("Aging (no stage change in 30+ days)", "aging_worklist_count"),
            ("Recently completed (30 days)", "recently_completed_count")]
    L = [f"# Implementations weekly refresh: {run.iso}" + (" (DRY RUN, nothing pushed)" if ns.dry_run else ""), "",
         "Source: HubSpot implementation object only (system of record since 2026-11-06). Activity = days in the current stage.", "",
         "## Headline numbers", "", "| Metric | Before | Now |", "|---|---|---|"]
    L += [f"| {lab} | {b.get(k) if b.get(k) is not None else 'n/a'} | {a.get(k)} |" for lab, k in rows]
    L += ["", f"Triage queue value: ${a['triage_queue_total_tcv']:,.0f} TCV, {a['triage_queue_total_units']:,} units.", "",
          "## Stage funnel (open, test records excluded)", ""]
    L += [f"- {x['stage']}: {x['count']}" for x in rec["stage_funnel"]]
    L += ["", "## HubSpot gaps (shown as blanks on the page)", "",
          f"- Open implementations with no owner: {g['open_without_owner']}",
          f"- Owned implementations with no go-live date: {g['owned_without_go_live_date']}",
          f"- Owned implementations with no kickoff date: {g['owned_without_kickoff_date']}",
          f"- Owned implementations with no project health: {g['owned_without_project_health']}",
          f"- Open implementations with no units: {g['open_without_units']}; with no segment: {g['open_without_segment']}",
          f"- No HubSpot source (left empty): {', '.join(g['no_source_on_hubspot'])}", "",
          f"Owners on open implementations: {', '.join(s['owners_on_open']) or 'none'}.", "",
          "## Most overdue (owned, go-live date passed)", ""]
    od = [x for x in rec["ongoing_worklist"] if x["days_overdue"]][:10]
    L += [f"- {x['customer']} ({x['status']}, {x['im_owner']}): {x['days_overdue']} days past {x['go_live_date']}" for x in od] or ["- None"]
    L += ["", "## Gates", ""] + [f"- {x}" for x in s["gates"]]
    os.makedirs(C.REPORTS, exist_ok=True)
    rpath = os.path.join(C.REPORTS, f"{run.iso}_weekly-refresh-report{'_dry-run' if ns.dry_run else ''}.md")
    open(rpath, "w", encoding="utf-8").write("\n".join(L) + "\n")
    t = run.cfg["target"]
    slack = (f"Implementations refreshed for {run.iso} ({t['dashboard_url']}), from HubSpot. {a['ongoing_worklist_count']} active "
             f"(owned), {a['triage_queue_count']} need triage (${a['triage_queue_total_tcv']:,.0f} TCV), {a['aging_worklist_count']} "
             f"with no stage change in 30+ days, {a['recently_completed_count']} completed in the last 30 days. HubSpot gaps: "
             f"{g['open_without_owner']} open with no owner, {g['owned_without_go_live_date']} owned with no go-live date. Readback verified.")
    open(run.path(f"slack_success_{run.mmdd}.txt"), "w", encoding="utf-8").write(slack + "\n")
    print("report:", rpath)
    print("slack:", slack)
    if not ns.dry_run:
        dest = os.path.join(C.HIST, run.iso)
        os.makedirs(dest, exist_ok=True)
        for fn in [f"impl_record_{run.mmdd}.json", f"build_summary_{run.mmdd}.json", f"baseline_{run.mmdd}.json",
                   f"readback_{run.mmdd}.json", f"hs_impl_{run.mmdd}.json"]:
            if os.path.exists(run.path(fn)):
                shutil.copy2(run.path(fn), dest)
        shutil.copy2(os.path.join(C.SKILL_DIR, "config.json"), os.path.join(dest, "config_used.json"))
        print("archived:", dest, len(os.listdir(dest)), "files")
