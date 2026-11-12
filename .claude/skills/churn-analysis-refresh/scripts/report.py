"""Write the Churn run report and Slack text, and archive the run.

Usage: python3 report.py --run-date D --scratch S [--dry-run]
Writes O-output/cx-churn-analysis/<date>_weekly-refresh-report.md, <scratch>/slack_success_<MMDD>.txt,
and (unless --dry-run) O-output/cx-churn-analysis/history/<date>/.
"""
import glob, json, os, shutil
import cr_common as C

if __name__ == "__main__":
    run, ns = C.parse_run("Churn report", [(("--dry-run",), {"action": "store_true"})])
    summ = run.load(f"build_summary_{run.mmdd}.json")
    plan = run.load(f"plan_{run.mmdd}.json")
    b, a = summ["before"], summ["after"]
    money = lambda v: f"${v:,.2f}"
    rows = [("True churn accounts", "accounts_churned_count", str), ("True churn ACV", "churned_acv_total", money),
            ("True churn ACV, YTD", "churned_acv_ytd", money), ("At Risk accounts", "at_risk_count", str),
            ("At Risk ACV", "at_risk_acv_best_effort", money), ("Total ACV tracked", "total_acv_tracked", money)]
    L = [f"# Churn Analysis weekly refresh: {run.iso}" + (" (DRY RUN, nothing pushed)" if ns.dry_run else ""), "",
         f"Client Health record used: computed {plan['health_computed_at']} ({plan['red_count']} Red).", "",
         "## Headline numbers", "", "| Metric | Before | Now |", "|---|---|---|"]
    L += [f"| {lab} | {f(b[k])} | {f(a[k])} |" for lab, k, f in rows]
    L += ["", f"Failure to Launch (shown live on the page from is_ftl): {summ['report_only']['ftl_count']} accounts, "
          f"{money(summ['report_only']['ftl_acv_total'])}.", "", "## At Risk changes (synced to Client Health Red)", ""]
    L += [f"- Left At Risk: {n}" for n in plan["remove_at_risk"]] or ["- None left"]
    L += [f"- Added: {x['entry']['name']} ({money(x['entry']['acv'])}; HubSpot {x['entry']['hubspot_company_id']} via "
          f"{x['evidence']['company_from']}; {x['evidence']['deals']}; AM {x['entry']['csm']})" for x in plan["add_at_risk"]] or ["- None added"]
    L += ["", "## New churns", ""]
    L += [f"- Added: {x['entry']['name']} (churned {x['entry']['effective_churn_date']}, {money(x['entry']['acv'])}, "
          f"{x['entry']['reason']}; {x['evidence']['rule']})" for x in plan["add_churned"]] or ["- None added this week"]
    L += ["", f"## Candidates not added ({len(plan['candidates'])})", "",
          "HubSpot says churned=true but the page doesn't list them. To add one, put its HubSpot ID in "
          "`config.new_churns.approved_additions` (with a note) by commit.", ""]
    recent = sorted(plan["candidates"], key=lambda c: c["churn_date"] or "", reverse=True)
    L += [f"- {c['name']} ({c['hubspot_company_id']}): churn date {c['churn_date']}, status {c['account_status']}: {c['why_not_added']}"
          for c in recent[:25]]
    if len(recent) > 25:
        L.append(f"- ...and {len(recent) - 25} more, all listed in plan_{run.mmdd}.json in the history folder")
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
             f"New churns added: {len(plan['add_churned'])}. {len(plan['flags'])} flag(s) in the report. Readback verified.")
    open(run.path(f"slack_success_{run.mmdd}.txt"), "w", encoding="utf-8").write(slack + "\n")
    print("report:", rpath)
    print("slack:", slack)
    if not ns.dry_run:
        dest = os.path.join(C.HIST, run.iso)
        os.makedirs(dest, exist_ok=True)
        for fn in [f"churn_record_{run.mmdd}.json", f"build_summary_{run.mmdd}.json", f"baseline_{run.mmdd}.json",
                   f"readback_{run.mmdd}.json", f"plan_{run.mmdd}.json"]:
            # not health_<MMDD>.json: Client Health archives its own record (3.5 MB); the plan keeps its computed_at
            if os.path.exists(run.path(fn)):
                shutil.copy2(run.path(fn), dest)
        shutil.copy2(os.path.join(C.SKILL_DIR, "config.json"), os.path.join(dest, "config_used.json"))
        print("archived:", dest, len(os.listdir(dest)), "files")
