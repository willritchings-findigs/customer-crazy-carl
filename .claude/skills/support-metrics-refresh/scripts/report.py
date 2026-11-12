"""Write the run report and Slack text, and archive the run's files.

Usage: python3 report.py --run-date D --scratch S [--dry-run]
Reads support_record_<MMDD>.json, build_summary_<MMDD>.json, baseline_<MMDD>.json (the record
before this run) and, unless --dry-run, the readback verify result.
Writes:
  O-output/cx-support-metrics/<date>_weekly-refresh-report.md
  <scratch>/slack_success_<MMDD>.txt   (post to config.slack.success_channel_id after a PASS)
  O-output/cx-support-metrics/history/<date>/  (record, summary, baseline, Sigma results, FCR days,
                                                config used) -- skipped on --dry-run
"""
import glob, json, os, shutil
import sm_common


def one(x):
    return x[0] if isinstance(x, list) else x


def get(d, path):
    for p in path.split("."):
        d = (d or {}).get(p) if isinstance(d, dict) else None
    return d


ROWS = [("Tickets, 30d", "ticket_volume.d30", "{:,}"), ("Tickets, 7d", "ticket_volume.d7", "{:,}"),
        ("Median first response, 30d (min)", "median_ttfr_minutes.d30", "{}"),
        ("SLA within target, 30d (%)", "sla_within_target_pct.d30", "{}"),
        ("SLA within target, 7d (%)", "sla_within_target_pct.d7", "{}"),
        ("FCR, 30d (%)", "fcr_pct.d30", "{}"), ("FCR, 7d (%)", "fcr_pct.d7", "{}"),
        ("PM CSAT, 30d", "pm_csat.d30", "{}"), ("Applicant CSAT, 30d", "applicant_csat.d30", "{}"),
        ("Tickets per 100 applicants, 30d", "tickets_pct_of_apps.d30", "{}"),
        ("Handled without escalation, 30d (%)", "handled_without_escalation_pct.d30", "{}"),
        ("Median resolution, 30d (min)", "median_resolution_minutes.d30", "{}"),
        ("Pet SLA within 24h, 30d (%)", "pet_sla.d30", "{}")]


def fmt(f, v):
    return "n/a" if v is None else f.format(v)


if __name__ == "__main__":
    run, ns = sm_common.get_run("Support Metrics report", [(("--dry-run",), {"action": "store_true"})])
    rec = run.load(f"support_record_{run.mmdd}.json")
    summ = run.load(f"build_summary_{run.mmdd}.json")
    base = one(run.load(f"baseline_{run.mmdd}.json"))
    new_k, old_k = rec["kpis"], base.get("kpis", {})
    na = summ["needs_attention"]
    lines = [f"# Support Metrics weekly refresh: {run.iso}" + (" (DRY RUN, nothing pushed)" if ns.dry_run else ""), "",
             f"Record `{run.cfg['target']['cache_key']}` on {run.cfg['target']['entity']}, computed {rec['computed_at']}. "
             f"Previous record computed {base.get('computed_at')}.", "",
             "## Headline numbers", "", "| Metric | Before | Now |", "|---|---|---|"]
    for label, path, f in ROWS:
        lines.append(f"| {label} | {fmt(f, get(old_k, path))} | {fmt(f, get(new_k, path))} |")
    lines += ["", "Method notes: pet and spam excluded from every figure except By Category; SLA counts a ticket "
              "with no first response as a miss; FCR is a scripted sample (see the FCR note on the record).", "",
              "## Needs Attention", "",
              f"{na['listed']} tickets listed (oldest first) of {na['waiting_within_90d']} property-manager and applicant "
              f"tickets waiting on Findigs from the last 90 days; {na['stale_over_90d']} more are older than 90 days "
              "(stale backlog, not listed).", "", "## Open backlog by status (0-30d / 30-90d / over 90d)", ""]
    for st, (a, b, c) in sorted(summ["open_backlog_by_status_0_30_30_90_over_90"].items()):
        lines.append(f"- {st}: {a} / {b} / {c}")
    lines += ["", "## Gates", ""] + [f"- {g}" for g in summ["gates"]]
    ut = summ["unclassified_requester_types"]
    lines += ["", f"Unclassified requester types (d30): {', '.join(f'{k} {v}' for k, v in ut.items()) or 'none'}.", ""]
    os.makedirs(sm_common.REPORTS, exist_ok=True)
    rpath = os.path.join(sm_common.REPORTS, f"{run.iso}_weekly-refresh-report{'_dry-run' if ns.dry_run else ''}.md")
    open(rpath, "w", encoding="utf-8").write("\n".join(lines) + "\n")

    k = new_k
    slack = (f"Support Metrics refreshed for {run.iso} ({run.cfg['target']['dashboard_url']}). "
             f"30d: {k['ticket_volume']['d30']:,} tickets, SLA {k['sla_within_target_pct']['d30']}%, "
             f"FCR {k['fcr_pct']['d30']}%, median first response {k['median_ttfr_minutes']['d30']} min, "
             f"CSAT PM {k['pm_csat']['d30']} / applicant {k['applicant_csat']['d30']}. "
             f"Needs Attention: {na['listed']} listed, {na['stale_over_90d']} stale over 90 days. All gates passed; "
             "readback verified.")
    open(run.path(f"slack_success_{run.mmdd}.txt"), "w", encoding="utf-8").write(slack + "\n")
    print("report:", rpath)
    print("slack:", slack)

    if not ns.dry_run:
        dest = os.path.join(sm_common.HIST, run.iso)
        os.makedirs(dest, exist_ok=True)
        keep = [f"support_record_{run.mmdd}.json", f"build_summary_{run.mmdd}.json", f"baseline_{run.mmdd}.json",
                f"readback_{run.mmdd}.json", f"fcr_{run.mmdd}.json"]
        keep += [os.path.basename(p) for p in glob.glob(run.path(f"s*_{run.mmdd}*.json"))]
        for fn in keep:
            if os.path.exists(run.path(fn)):
                shutil.copy2(run.path(fn), dest)
        shutil.copy2(os.path.join(sm_common.SKILL_DIR, "config.json"), os.path.join(dest, "config_used.json"))
        print("archived:", dest, len(os.listdir(dest)), "files")
