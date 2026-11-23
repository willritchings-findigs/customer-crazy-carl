"""Apply this week's plan to the ChurnCache accounts and recompute every aggregate.

Usage: python3 build_record.py --run-date D --scratch S
Reads baseline_<MMDD>.json and plan_<MMDD>.json. Writes churn_record_<MMDD>.json (managed fields)
and build_summary_<MMDD>.json, only if every gate passes; otherwise exits 1 and writes nothing.
Gates:
  - the recompute reproduces the baseline's own numbers from the baseline's accounts (proves the
    logic and the live record agree before anything changes)
  - no churned account is removed; churned count grows by exactly the planned additions (new churns
    plus At Risk rows converted to Churned)
  - every planned churn-date update lands on a churned row
  - At Risk ends up equal to Client Health's Red list (less any Red account already churned, including
    the rows converted this run)
  - At Risk moves by no more than config.validation.max_at_risk_change
  - no duplicate HubSpot company IDs
  - every planned Account Status FTL update lands on a churned row
Then every churned-population row is labelled Churned or Failure to Launch from is_ftl (cr_common.normalize_status).
"""
import datetime as dt, json, sys
from copy import deepcopy
import cr_common as C


def numeric_diffs(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += numeric_diffs(a.get(k, "<missing>"), b.get(k, "<missing>"), f"{path}.{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += numeric_diffs(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, str) and isinstance(b, str) and ("caveat" in path or "resolved_of_total" in path):
        return []  # generated caption text
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        return [] if abs(a - b) <= 0.005 else [f"{path}: {a} vs {b}"]
    return [] if a == b else [f"{path}: {str(a)[:60]!r} vs {str(b)[:60]!r}"]


if __name__ == "__main__":
    run, _ = C.parse_run("Build the ChurnCache record")
    cfg, st = run.cfg, run.cfg["taxonomy"]["statuses"]
    base = C.one(run.load(f"baseline_{run.mmdd}.json"))
    plan = run.load(f"plan_{run.mmdd}.json")
    gates, fails = [], []

    def check(ok, msg):
        (gates if ok else fails).append(("ok   " if ok else "FAIL ") + msg)

    # The baseline's own run date is its computed_at date or the day before (late-night UTC runs).
    bdate = C.pdate(base["computed_at"])
    d = None
    for day in (bdate, bdate - dt.timedelta(days=1)):
        repro, _ = C.recompute(base["accounts"], cfg, day)
        dd = [x for f in repro for x in numeric_diffs(base.get(f), repro[f], f)]
        d = dd if d is None or len(dd) < len(d) else d
    check(not d, "recompute reproduces the live record from its own accounts" + (f": {d[:5]}" if d else ""))

    accts = deepcopy(base["accounts"])
    n_churned_before = sum(C.is_churned_row(a, cfg) for a in accts)
    converted = plan.get("at_risk_to_churned", [])
    drop = set(plan["remove_at_risk"]) | {x["replaces_at_risk"] for x in converted}
    accts = [a for a in accts if not (a["status"] == st["at_risk"] and a["name"] in drop)]
    accts += [x["entry"] for x in plan["add_at_risk"]] + [x["entry"] for x in plan["add_churned"]] + [x["entry"] for x in converted]
    dates = {d["hubspot_company_id"]: d["to"] for d in plan.get("date_updates", [])}
    applied = 0
    for a in accts:
        if C.is_churned_row(a, cfg) and a.get("hubspot_company_id") in dates:
            a["effective_churn_date"], applied = dates[a["hubspot_company_id"]], applied + 1
    flips = {u["hubspot_company_id"]: u["to_ftl"] for u in plan.get("ftl_updates", [])}
    flipped = 0
    for a in accts:
        if C.is_churned_row(a, cfg) and a.get("hubspot_company_id") in flips:
            a["is_ftl"] = flips[a["hubspot_company_id"]]
            a["status"] = st["ftl"] if a["is_ftl"] else st["churned"]
            flipped += 1
    relabelled = C.normalize_status(accts, cfg)
    # Base44 added churn_date and account_status to the stored row schema on 2026-11-20 (the in-app writer) and
    # stores null when a row omits them; the page reads churn_date. Fill both on every row, every run.
    hs_status = plan.get("account_status_by_id", {})
    for a in accts:
        a["churn_date"] = a.get("effective_churn_date") if C.is_churned_row(a, cfg) else None
        a["account_status"] = hs_status.get(a.get("hubspot_company_id"), a.get("account_status"))
    churned = [a for a in accts if C.is_churned_row(a, cfg)]
    at_risk = [a for a in accts if a["status"] == st["at_risk"]]
    check(len(churned) == n_churned_before + len(plan["add_churned"]) + len(converted),
          f"churned {n_churned_before} -> {len(churned)} (+{len(plan['add_churned'])} added, +{len(converted)} from At Risk, none removed)")
    check(flipped == len(flips), f"Account Status FTL updates applied to churned rows: {flipped} of {len(flips)}"
          + (f"; {relabelled} rows relabelled Churned / Failure to Launch from is_ftl" if relabelled else ""))
    check(applied == len(dates), f"churn date updates applied to churned rows: {applied} of {len(dates)}")
    skipped = sum("already on the page as Churned" in f for f in plan["flags"]) + len(converted)
    check(len(at_risk) == plan["red_count"] - skipped,
          f"At Risk {len(at_risk)} = Client Health Red {plan['red_count']}" + (f" less {skipped} already churned" if skipped else ""))
    moved = len(plan["remove_at_risk"]) + len(plan["add_at_risk"]) + len(converted)
    check(moved <= cfg["validation"]["max_at_risk_change"],
          f"At Risk moved by {moved} (limit {cfg['validation']['max_at_risk_change']})")
    ids = [a["hubspot_company_id"] for a in accts if a.get("hubspot_company_id")]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    check(not dups, f"no duplicate HubSpot company IDs {dups or ''}")

    fields, ro = C.recompute(accts, cfg, run.date)
    record = {"computed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"), "accounts": accts, **fields}
    summary = {"run_date": run.iso, "gates": gates + fails, "failed": bool(fails), "report_only": ro,
               "before": {k: base["kpis"].get(k) for k in ("accounts_churned_count", "churned_acv_total", "churned_acv_ytd",
                                                           "at_risk_count", "at_risk_acv_best_effort", "total_acv_tracked")},
               "after": {k: fields["kpis"][k] for k in ("accounts_churned_count", "churned_acv_total", "churned_acv_ytd",
                                                        "at_risk_count", "at_risk_acv_best_effort", "total_acv_tracked")}}
    print("\n".join(summary["gates"]))
    if fails:
        print(f"\nSTOP: {len(fails)} gate(s) failed; no record written.")
        sys.exit(1)
    json.dump(record, open(run.path(f"churn_record_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(summary, open(run.path(f"build_summary_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\nwrote churn_record_{run.mmdd}.json; before {summary['before']}\nafter {summary['after']}")
