#!/usr/bin/env python3
"""Archive a client-health run into O-output history.

Usage: python3 archive_history.py --run-date YYYY-MM-DD --scratch <dir>
- Appends this run to history/wow_history.json (slim per-account rows incl. why fields).
- Regenerates history/wow_history.csv (one row per account per run).
- Writes history/<run-date>/: baseline, pushed record, wow_diff, overrides, matches, Gong rows,
  plus the exact config.json and scripts that produced the run.
- Emits snapshot_payload_<MMDD>.json (slim Base44 snapshot body) to the scratch dir.
Stops if ts.txt is missing (computed_at would silently be null).
"""
import json, csv, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, HIST, SKILL_DIR

RUN_CTX, _ = parse_run("Archive a client-health run")
SCRATCH = RUN_CTX.scratch
RUN = RUN_CTX.iso
MMDD = RUN_CTX.mmdd

def aname(a): return a.get("resolved_name_sigma") or a.get("input_name")

def g(d, *path):
    for p in path:
        d = (d or {}).get(p)
    return d

def slim_row(a):
    comp = a.get("composite_score_partial") or {}
    ps = a.get("pillar_scores") or {}
    m = a.get("metrics") or {}
    qp = a.get("qualitative_pillars") or {}
    flag = g(qp, "strategic_alignment_governance", "csm_qualitative_risk_flag") or {}
    cs = qp.get("client_sentiment") or {}

    def pv(k, f): return g(ps, k, f)
    def mv(k, f): return g(m, k, f)

    row = {
        "account": aname(a),
        "is_da": bool(a.get("is_decision_assist_enabled")),
        "segment": a.get("rubric_segment_column"),
        "band": comp.get("band"),
        "composite_value": comp.get("value"),
        "platform_value": pv("platform_product_metrics", "value"),
        "platform_band": pv("platform_product_metrics", "band"),
        "strategic_value": pv("strategic_alignment_governance", "value"),
        "strategic_band": pv("strategic_alignment_governance", "band"),
        "sentiment_value": pv("client_sentiment", "value"),
        "sentiment_band": pv("client_sentiment", "band"),
        "csm_flag_value": flag.get("value"),
        "csm_flag_band": flag.get("band"),
        "ttd_worse": mv("median_ttd_hours", "worse_of_two") if mv("median_ttd_hours", "worse_of_two") is not None else mv("median_ttd_hours", "value"),
        "ttd_band": mv("median_ttd_hours", "band"),
        "approval_value": mv("approval_rate_pct", "value"),
        "approval_band": mv("approval_rate_pct", "band"),
        "override_value": mv("override_rate_pct", "value"),
        "override_band": mv("override_rate_pct", "band"),
        "qa_value": mv("qa_pct", "value"),
        "qa_band": mv("qa_pct", "band"),
        "ticket_value": mv("support_ticket_ratio_per_100", "value"),
        "ticket_band": mv("support_ticket_ratio_per_100", "band"),
        "tes_value": mv("tes_pct", "value"),
        "tes_band": mv("tes_pct", "band"),
        "volume_value": mv("volume_trend_pct", "value"),
        "volume_band": mv("volume_trend_pct", "band"),
        "ccs_class": g(cs, "client_communication_sentiment", "classification"),
        "pylon_class": g(cs, "pylon_ticket_tone", "classification"),
        "units_sold": a.get("total_units_sold_hubspot"),
        "units_live": a.get("unit_count_live_current_month"),
        "sold_vs_live_pct": a.get("sold_vs_live_units_pct"),
    }
    row.update(why_fields(a))
    return row

def why_fields(a):
    """The why extension (Emma 2026-09-14): overall why + per-pillar whys + gating reasons."""
    comp = a.get("composite_score_partial") or {}
    ps = a.get("pillar_scores") or {}
    band = comp.get("band")
    out = {
        "why": comp.get("why"),
        "platform_why": g(ps, "platform_product_metrics", "why"),
        "strategic_why": g(ps, "strategic_alignment_governance", "why"),
        "sentiment_why": g(ps, "client_sentiment", "why"),
        "red_reasons": [{"label": r.get("label"), "detail": r.get("detail")}
                        for r in (comp.get("red_reasons") or [])],
    }
    if band == "Churned":
        out["why"] = (f"Churned {comp.get('churn_date') or '(date unknown)'} -- "
                      f"{comp.get('churn_reason') or 'no reason recorded'}")
    elif band is None and comp.get("methodology"):
        out["why"] = comp["methodology"]
    return out

def band_counts(rows):
    c = {}
    for r in rows:
        b = r.get("band") or "None"
        c[b] = c.get(b, 0) + 1
    return c

# ---- load current history ----
wow_path = os.path.join(HIST, "wow_history.json")
wow = json.load(open(wow_path))

# ---- append this run ----
new_rec = json.load(open(os.path.join(SCRATCH, f"new_record_{MMDD}.json")))
accounts = new_rec["accounts"]
ts_path = os.path.join(SCRATCH, "ts.txt")
if not os.path.exists(ts_path) or not open(ts_path).read().strip():
    raise SystemExit(f"ABORT: {ts_path} missing or empty; computed_at would be null")
ts = open(ts_path).read().strip()
rows = [slim_row(a) for a in accounts]
wow[RUN] = {"computed_at": ts, "accounts": rows, "band_counts": band_counts(rows)}
json.dump(wow, open(wow_path, "w"), indent=1)
print(f"wow_history.json: runs={list(wow.keys())}, {RUN} bands={wow[RUN]['band_counts']}")

# ---- regenerate CSV ----
cols = ["run_date"] + list(rows[0].keys())
with open(os.path.join(HIST, "wow_history.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for run_key in sorted(wow.keys()):
        for r in wow[run_key]["accounts"]:
            rr = dict(r)
            rr["run_date"] = run_key
            rr["red_reasons"] = " || ".join(f"{x.get('label')}: {x.get('detail')}"
                                            for x in (r.get("red_reasons") or [])) or None
            w.writerow(rr)
print("wow_history.csv regenerated")

# ---- full run folder ----
run_dir = os.path.join(HIST, RUN)
os.makedirs(run_dir, exist_ok=True)
for fn in (f"baseline_{MMDD}.json", f"new_record_{MMDD}.json", f"wow_diff_{MMDD}.json",
           "slack_overrides.json", "pylon_overrides.json",
           "hs_account_match.json", "gong_strategic_rows.json"):
    src = os.path.join(SCRATCH, fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(run_dir, fn))
shutil.copy(os.path.join(SKILL_DIR, "config.json"), os.path.join(run_dir, "config.json"))
shutil.copytree(os.path.join(SKILL_DIR, "scripts"), os.path.join(run_dir, "scripts"),
                dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
print(f"archived full run to {run_dir}")

# ---- Base44 snapshot payload (slim) ----
diff = json.load(open(os.path.join(SCRATCH, f"wow_diff_{MMDD}.json")))
snap = {
    "cache_key": f"health_snapshot_{RUN}",
    "computed_at": ts,
    "band_counts": wow[RUN]["band_counts"],
    "band_flips": diff.get("band_flips"),
    "accounts": rows,
}
snap_path = os.path.join(SCRATCH, f"snapshot_payload_{MMDD}.json")
json.dump(snap, open(snap_path, "w"))
print(f"snapshot payload written ({os.path.getsize(snap_path)//1024} KB)")
