"""Detect a foreign write to the ChurnCache record and fall back to the last vetted record.

Usage: python3 guard.py --run-date D --scratch S
Reads baseline_<MMDD>.json (the live GET). Compares its accounts with the newest archived readback in
O-output/cx-churn-analysis/history/ (the last record this skill wrote and verified).

- Same accounts: nothing to do (prints OK).
- Different accounts: something other than this skill rewrote the record (on 2026-11-23 the Base44
  "Daily Churn Cache Refresh" workflow did; see the workflow log). The live copy is saved as
  foreign_<MMDD>.json, and baseline_<MMDD>.json is replaced by the archived readback with the live
  record's identity fields, so the rest of the run rebuilds from the vetted list and the page is
  restored at the push. Never a stop: the vetted list is the source of truth by design.
Writes guard_<MMDD>.json (what was found) for report.py. Exit 1 only if no archive exists.
"""
import glob, json, os, sys
import cr_common as C

IDENTITY = ("id", "cache_key", "created_date", "created_by_id", "is_sample", "updated_date")


def newest_readback():
    best = None
    for f in glob.glob(os.path.join(C.HIST, "*", "readback_*.json")):
        r = C.one(json.load(open(f, encoding="utf-8")))
        if best is None or r.get("computed_at", "") > best[1].get("computed_at", ""):
            best = (f, r)
    return best


def key(a):
    return a.get("hubspot_company_id") or ("name:" + (a.get("name") or ""))


def summary(accts):
    out = {}
    for a in accts:
        s = a.get("status")
        out[s] = out.get(s, 0) + 1
    return out


if __name__ == "__main__":
    run, _ = C.parse_run("ChurnCache foreign-write guard")
    live = C.one(run.load(f"baseline_{run.mmdd}.json"))
    found = newest_readback()
    if not found:
        sys.exit("STOP: no archived readback in history; cannot tell the vetted list from a foreign write")
    path, vetted = found
    same = json.dumps(live.get("accounts"), sort_keys=True) == json.dumps(vetted.get("accounts"), sort_keys=True)
    result = {"run_date": run.iso, "foreign_write": not same, "vetted_source": os.path.relpath(path, C.REPO_ROOT).replace("\\", "/"),
              "vetted_computed_at": vetted.get("computed_at"), "live_computed_at": live.get("computed_at"),
              "live_updated_date": live.get("updated_date")}
    if same:
        print(f"OK: live record matches the last vetted readback ({result['vetted_source']}, computed {vetted.get('computed_at')})")
    else:
        lk = {key(a): a for a in live.get("accounts") or []}
        vk = {key(a): a for a in vetted.get("accounts") or []}
        result.update({
            "live_accounts": len(lk), "vetted_accounts": len(vk),
            "live_by_status": summary(live.get("accounts") or []), "vetted_by_status": summary(vetted.get("accounts") or []),
            "only_in_live": len(set(lk) - set(vk)), "only_in_vetted": len(set(vk) - set(lk)),
            "dropped_vetted_churned": sorted(vk[k]["name"] for k in set(vk) - set(lk)
                                             if vk[k].get("status") != run.cfg["taxonomy"]["statuses"]["at_risk"]),
        })
        json.dump(live, open(run.path(f"foreign_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        restored = {k: v for k, v in vetted.items() if k not in IDENTITY}
        restored.update({k: live[k] for k in IDENTITY if k in live})
        json.dump(restored, open(run.path(f"baseline_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(f"FOREIGN WRITE: live record (computed {live.get('computed_at')}, updated {live.get('updated_date')}) "
              f"has {len(lk)} accounts {result['live_by_status']}; last vetted readback has {len(vk)} {result['vetted_by_status']}.")
        print(f"  {result['only_in_live']} accounts only in live, {result['only_in_vetted']} only in vetted "
              f"(vetted churned rows dropped: {len(result['dropped_vetted_churned'])}).")
        print(f"  Saved live copy as foreign_{run.mmdd}.json; baseline now = {result['vetted_source']}. This run restores the vetted list.")
    # Is the Base44 workflow that rewrote the record still switched off? (workflows_<MMDD>.json = curl GET
    # <api_base>/apps/<app_id>/workflows; missing file = not checked.)
    fw = run.cfg["target"].get("foreign_writer") or {}
    wpath = run.path(f"workflows_{run.mmdd}.json")
    if fw and os.path.exists(wpath):
        try:
            wf = next((w for w in json.load(open(wpath, encoding="utf-8")) if w.get("id") == fw["base44_workflow_id"]), None)
            result["writer_workflow_status"] = wf.get("status") if wf else "not found (deleted)"
            result["writer_workflow_last_run_at"] = wf.get("last_run_at") if wf else None
        except (ValueError, TypeError, AttributeError) as e:
            result["writer_workflow_status"] = f"unreadable ({type(e).__name__})"
    else:
        result["writer_workflow_status"] = "not checked"
    print(f"Base44 workflow '{fw.get('base44_workflow_name')}': {result['writer_workflow_status']}")
    json.dump(result, open(run.path(f"guard_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
