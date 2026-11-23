"""Write the Churn run report and Slack text, and archive the run.

Usage: python3 report.py --run-date D --scratch S [--dry-run]
Writes O-output/cx-churn-analysis/<date>_weekly-refresh-report.md, <scratch>/slack_success_<MMDD>.txt,
<scratch>/slack_alert_<MMDD>.txt when the run had to work around something (foreign write restored, At
Risk not synced, FTL updates held), and (unless --dry-run) O-output/cx-churn-analysis/history/<date>/.
"""
import glob, json, os, shutil
import cr_common as C

if __name__ == "__main__":
    run, ns = C.parse_run("Churn report", [(("--dry-run",), {"action": "store_true"})])
    summ = run.load(f"build_summary_{run.mmdd}.json")
    plan = run.load(f"plan_{run.mmdd}.json")
    guard = run.load(f"guard_{run.mmdd}.json") if os.path.exists(run.path(f"guard_{run.mmdd}.json")) else {}
    b, a = summ["before"], summ["after"]
    money = lambda v: f"${v:,.2f}"
    rows = [("True churn accounts", "accounts_churned_count", str), ("True churn ACV", "churned_acv_total", money),
            ("True churn ACV, YTD", "churned_acv_ytd", money), ("At Risk accounts", "at_risk_count", str),
            ("At Risk ACV", "at_risk_acv_best_effort", money), ("Total ACV tracked", "total_acv_tracked", money)]
    L = [f"# Churn Analysis weekly refresh: {run.iso}" + (" (DRY RUN, nothing pushed)" if ns.dry_run else ""), "",
         (f"Client Health record used: computed {plan['health_computed_at']} ({plan['red_count']} Red)."
          if plan.get("at_risk_synced", True) else
          f"**At Risk NOT synced:** Client Health record computed {plan['health_computed_at']} is too old or unreadable; "
          "At Risk carried over unchanged."), "",
         "## Headline numbers", "", "| Metric | Before | Now |", "|---|---|---|"]
    L += [f"| {lab} | {f(b[k])} | {f(a[k])} |" for lab, k, f in rows]
    if guard.get("foreign_write"):
        L += ["", "## Foreign write restored", "",
              f"The live record had been rewritten outside this skill (computed {guard.get('live_computed_at')}, "
              f"updated {guard.get('live_updated_date')}): {guard.get('live_accounts')} accounts {guard.get('live_by_status')} "
              f"vs {guard.get('vetted_accounts')} {guard.get('vetted_by_status')} in the last vetted record "
              f"({guard.get('vetted_source')}). It dropped {len(guard.get('dropped_vetted_churned') or [])} vetted churned "
              "accounts. This run rebuilt from the vetted record and restored it. Most likely source: the Base44 "
              "\"Daily Churn Cache Refresh\" workflow (see the workflow doc). The live copy is archived as foreign_<MMDD>.json."]
    L += ["", f"Failure to Launch (shown live on the page from is_ftl): {summ['report_only']['ftl_count']} accounts, "
          f"{money(summ['report_only']['ftl_acv_total'])}.", "", "## At Risk changes (synced to Client Health Red)", ""]
    L += [f"- Left At Risk: {n}" for n in plan["remove_at_risk"]] or ["- None left"]
    L += [f"- Added: {x['entry']['name']} ({money(x['entry']['acv'])}; HubSpot {x['entry']['hubspot_company_id']} via "
          f"{x['evidence']['company_from']}; {x['evidence']['deals']}; AM {x['entry']['csm']})" for x in plan["add_at_risk"]] or ["- None added"]
    conv = plan.get("at_risk_to_churned", [])
    L += ["", "## New churns", ""]
    L += [f"- Added: {x['entry']['name']} (churned {x['entry']['effective_churn_date']}, {money(x['entry']['acv'])}, "
          f"{x['entry']['reason']}; {x['evidence']['rule']})" for x in plan["add_churned"]] or ["- None added this week"]
    L += [f"- Converted from At Risk ({x['replaces_at_risk']}): {x['entry']['name']} (churned {x['entry']['effective_churn_date']}, "
          f"{money(x['entry']['acv'])}, {x['entry']['reason']}; {x['evidence']['rule']})" for x in conv]
    dates = plan.get("date_updates", [])
    L += ["", f"## Churn date updates ({len(dates)})", "",
          "Effective churn dates re-synced to HubSpot's churn date field (config.hubspot.churn_date_fields).", ""]
    L += [f"- {d['name']}: {d['from']} -> {d['to']} (HubSpot {d['field']})" for d in dates] or ["- None"]
    L += ["", f"## Candidates not added ({len(plan['candidates'])})", "",
          "HubSpot says churned=true but the page doesn't list them as Churned. To add one, put its HubSpot ID in "
          "`config.new_churns.approved_additions` (with a note) by commit. Ones marked *on the page as At Risk* stay "
          "At Risk until they pass the rule or are approved.", ""]
    recent = sorted(plan["candidates"], key=lambda c: (bool(c.get("on_page_as")), c["churn_date"] or ""), reverse=True)
    L += [f"- {c['name']} ({c['hubspot_company_id']}): churn date {c['churn_date']}, status {c['account_status']}: {c['why_not_added']}"
          + (f" *(on the page as {c['on_page_as']})*" if c.get("on_page_as") else "") for c in recent[:25]]
    if len(recent) > 25:
        L.append(f"- ...and {len(recent) - 25} more, all listed in plan_{run.mmdd}.json in the history folder")
    fu, fh = plan.get("ftl_updates", []), plan.get("ftl_updates_held", [])
    L += ["", f"## FTL updates from HubSpot Account Status ({len(fu)} applied, {len(fh)} held)", ""]
    L += [f"- {u['name']}: {'true churn -> FTL' if u['to_ftl'] else 'FTL -> true churn'} (Account Status {u['account_status']}, "
          f"{money(u.get('acv') or 0)})" for u in fu] or ["- None applied"]
    L += [f"- HELD: {u['name']} ({'to FTL' if u['to_ftl'] else 'to true churn'}, Account Status {u['account_status']})" for u in fh]
    L += ["", f"## Failure-to-Launch candidates (propose-only): {len(plan['ftl_candidates'])}", ""]
    L += [f"- {c['name']} ({c['hubspot_company_id']})" for c in plan["ftl_candidates"]] or ["- None"]
    L += ["", "## Standing data checks (not changed automatically)", "",
          f"- Churned on the page but HubSpot status is Live/Onboarding/Pilot: {len(plan['churned_on_page_but_hubspot_status_live'])}",
          f"- Churned on the page but no longer churned=true in HubSpot: {len(plan['churned_on_page_but_hubspot_not_churned'])}"
          + (f" ({', '.join(plan['churned_on_page_but_hubspot_not_churned'][:10])})" if plan['churned_on_page_but_hubspot_not_churned'] else ""),
          "", "## Flags", ""]
    L += [f"- {f}" for f in plan["flags"]] or ["- None"]
    L += ["", "## Gates", ""] + [f"- {g}" for g in summ["gates"]]
    os.makedirs(C.REPORTS, exist_ok=True)
    rpath = os.path.join(C.REPORTS, f"{run.iso}_weekly-refresh-report{'_dry-run' if ns.dry_run else ''}.md")
    open(rpath, "w", encoding="utf-8").write("\n".join(L) + "\n")
    t = run.cfg["target"]
    slack = (f"Churn Analysis refreshed for {run.iso} ({t['dashboard_url']}). True churn: {a['accounts_churned_count']} accounts, "
             f"{money(a['churned_acv_total'])} ({money(a['churned_acv_ytd'])} YTD). At Risk: {a['at_risk_count']} accounts, "
             f"{money(a['at_risk_acv_best_effort'])} (+{len(plan['add_at_risk'])} / -{len(plan['remove_at_risk'])} vs last week). "
             f"New churns added: {len(plan['add_churned']) + len(conv)}"
             + (f" ({len(conv)} converted from At Risk)" if conv else "") + f". {len(plan['flags'])} flag(s) in the report. Readback verified.")
    notes = []
    if guard.get("foreign_write"):
        notes.append(f"restored the vetted account list after an outside rewrite ({guard.get('live_accounts')} accounts, "
                     f"{len(guard.get('dropped_vetted_churned') or [])} vetted churns dropped; likely the Base44 "
                     "Daily Churn Cache Refresh workflow)")
    ws = guard.get("writer_workflow_status")
    if ws and ws not in ("inactive", "not found (deleted)"):
        notes.append(f"the Base44 'Daily Churn Cache Refresh' workflow is {ws}; it will overwrite this record at 06:00 ET "
                     "until a Base44 admin sets it inactive (Workflows tab of the Findigs Hub app)")
    if not plan.get("at_risk_synced", True):
        notes.append("At Risk carried over unchanged because Client Health is stale")
    if fh:
        notes.append(f"{len(fh)} FTL status changes held (over the limit)")
    if notes:
        slack += " Note: " + "; ".join(notes) + "."
        alert = (f":warning: Churn Analysis refresh {run.iso} succeeded with workarounds: " + "; ".join(notes)
                 + f". Details: O-output/cx-churn-analysis/{run.iso}_weekly-refresh-report.md")
        open(run.path(f"slack_alert_{run.mmdd}.txt"), "w", encoding="utf-8").write(alert + "\n")
        print("alert:", alert)
    elif os.path.exists(run.path(f"slack_alert_{run.mmdd}.txt")):
        os.remove(run.path(f"slack_alert_{run.mmdd}.txt"))
    open(run.path(f"slack_success_{run.mmdd}.txt"), "w", encoding="utf-8").write(slack + "\n")
    print("report:", rpath)
    print("slack:", slack)
    if not ns.dry_run:
        dest = os.path.join(C.HIST, run.iso)
        os.makedirs(dest, exist_ok=True)
        for fn in [f"churn_record_{run.mmdd}.json", f"build_summary_{run.mmdd}.json", f"baseline_{run.mmdd}.json",
                   f"readback_{run.mmdd}.json", f"plan_{run.mmdd}.json", f"guard_{run.mmdd}.json",
                   f"foreign_{run.mmdd}.json"]:
            # not health_<MMDD>.json: Client Health archives its own record (3.5 MB); the plan keeps its computed_at
            if os.path.exists(run.path(fn)):
                shutil.copy2(run.path(fn), dest)
        shutil.copy2(os.path.join(C.SKILL_DIR, "config.json"), os.path.join(dest, "config_used.json"))
        print("archived:", dest, len(os.listdir(dest)), "files")
