"""Run context and shared logic for churn-analysis-refresh.

Reuses the client-health-refresh helpers (run date, config, credentials) pointed at THIS skill's
folder via CX_SKILL_DIR. recompute() rebuilds every aggregate on the ChurnCache record from the
accounts list (ported from the 2026-10-29 script, which reproduced the live record exactly).
"""
import datetime as dt, glob, json, os, sys
from collections import Counter

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["CX_SKILL_DIR"] = SKILL_DIR
sys.path.insert(0, os.path.join(os.path.dirname(SKILL_DIR), "client-health-refresh", "scripts"))

import ch_common  # noqa: E402
from ch_common import parse_run, REPO_ROOT  # noqa: E402,F401

HIST = os.path.join(REPO_ROOT, "O-output", "cx-churn-analysis", "history")
REPORTS = os.path.join(REPO_ROOT, "O-output", "cx-churn-analysis")


def one(x):
    return x[0] if isinstance(x, list) else x


def r1(x):
    return round(float(x), 1)


def r2(x):
    return round(float(x), 2)


def pdate(d):
    return dt.date.fromisoformat(d[:10]) if d else None


def hs_url(cid):
    return f"https://app-na2.hubspot.com/contacts/243635806/record/0-2/{cid}" if cid else None


def latest_match_file(cfg):
    files = sorted(glob.glob(os.path.join(REPO_ROOT, cfg["health_source"]["match_file_glob"])))
    if not files:
        sys.exit("STOP: no Client Health hs_account_match.json found in history")
    return files[-1]


def recompute(accts, cfg, today):
    """Every aggregate field, rebuilt from accts. Returns (fields, report_only)."""
    tx = cfg["taxonomy"]
    st_churned, st_risk = tx["statuses"]["churned"], tx["statuses"]["at_risk"]
    churned = [a for a in accts if a["status"] == st_churned]
    at_risk = [a for a in accts if a["status"] == st_risk]
    if len(churned) + len(at_risk) != len(accts):
        raise SystemExit("STOP: an account has a status other than Churned / At Risk")
    true_churn = [a for a in churned if not a.get("is_ftl")]
    ftl = [a for a in churned if a.get("is_ftl")]
    ytd_start, month_start = dt.date(today.year, 1, 1), today.replace(day=1)

    def acv_sum(lst):
        return r2(sum(a.get("acv") or 0 for a in lst))

    def window(lst, start):
        tot, fwd = 0.0, []
        for a in lst:
            d = pdate(a.get("effective_churn_date"))
            if d and d > today:
                fwd.append(a)
            elif d and start <= d <= today:
                tot += a.get("acv") or 0
        return r2(tot), fwd

    true_total, ftl_total = acv_sum(true_churn), acv_sum(ftl)
    ytd_true, fwd = window(true_churn, ytd_start)
    month_true, _ = window(true_churn, month_start)
    _, fwd_ftl = window(ftl, ytd_start)
    fwd_all = fwd + fwd_ftl
    at_risk_acv = acv_sum(at_risk)
    unresolved = [a for a in at_risk if not a.get("acv_resolved")]
    resolved_caveat = f"{len(at_risk) - len(unresolved)}/{len(at_risk)} confirmed via closed-won deal match."
    if unresolved:
        resolved_caveat += " Not resolved (ACV shown as found, needs a check): " + ", ".join(
            f"{a['name']} (${(a.get('acv') or 0):,.2f})" for a in unresolved) + "."
    if fwd_all:
        month_caveat = (f"Excludes {len(fwd_all)} pending contract-end date(s) not yet realized: " + ", ".join(
            f"{a['name']} (${(a.get('acv') or 0):,.2f}, ends {a['effective_churn_date']})" for a in fwd_all) + ". ")
    else:
        month_caveat = "No pending contract-end dates. "
    month_caveat += ("This field (and churned_acv_total/ytd/accounts_churned_count) represent true churn only, "
                     "excluding Failure-to-Launch (is_ftl=true) accounts -- see the FTL card on the dashboard "
                     "for that population's own totals, derived live from is_ftl.")
    kpis = {
        "total_acv_tracked": r2(true_total + ftl_total + at_risk_acv),
        "churned_acv_total": true_total, "churned_acv_ytd": ytd_true, "churned_acv_month": month_true,
        "churned_acv_month_caveat": month_caveat,
        "accounts_churned_count": len(true_churn), "at_risk_count": len(at_risk),
        "at_risk_acv_best_effort": at_risk_acv, "at_risk_acv_resolved_of_total": resolved_caveat,
    }

    def mini(a):
        return {"name": a["name"], "acv": a["acv"], "churn_date": a["effective_churn_date"], "hubspot_url": a["hubspot_url"]}

    rows_by_reason = {r: [] for r in tx["reason_order"]}
    for a in churned:
        r = a.get("reason") or "Uncategorized"
        if r not in rows_by_reason:
            raise SystemExit(f"STOP: reason {r!r} is not in config.taxonomy.reason_order")
        rows_by_reason[r].append(a)
    combined = r2(true_total + ftl_total)
    churn_by_reason = []
    for r in tx["reason_order"]:
        rows = rows_by_reason[r]
        subs = {}
        for a in rows:
            for s in a.get("sub_reasons") or []:
                subs.setdefault(s, []).append(a)
        acv = acv_sum(rows)
        churn_by_reason.append({
            "reason": r, "count": len(rows), "acv": acv,
            "pct_of_total_acv": r1(100.0 * acv / combined) if combined else 0.0,
            "accounts": [mini(a) for a in rows],
            "sub_reasons": [{"sub_reason": s, "count": len(sr), "acv": acv_sum(sr), "accounts": [mini(a) for a in sr]}
                            for s, sr in subs.items()]})

    labels = tx["product_labels"]
    by_prod = {"DecisionAssist": [], "Full-Screen": [], "Unclassified": []}
    for a in churned:
        by_prod[labels.get(a.get("product_segment"), "Unclassified")].append(a)
    by_product_breakdown = [{"segment": s, "count": len(rs), "acv": acv_sum(rs), "accounts": [mini(a) for a in rs]}
                            for s, rs in by_prod.items()]

    by_segment_size = {}
    for a in churned:
        e = by_segment_size.setdefault(a.get("segment") or "Unknown", {"count": 0, "acv": 0.0})
        e["count"] += 1
        e["acv"] += a.get("acv") or 0
    for e in by_segment_size.values():
        e["acv"] = r2(e["acv"])

    da, fs, un = (next(r for r in by_product_breakdown if r["segment"] == s) for s in ("DecisionAssist", "Full-Screen", "Unclassified"))
    res_n = da["count"] + fs["count"]
    by_segment_product = {"note": (
        f"DA (DecisionAssist): {da['count']} accounts, ${da['acv']/1e6:.2f}M ACV | "
        f"Full-Screen: {fs['count']} accounts, ${fs['acv']/1e6:.2f}M ACV | "
        f"{un['count']} accounts (${un['acv']/1e6:.2f}M ACV) still unclassified -- "
        f"{r1(100.0*res_n/len(churned)) if churned else 0.0}% of churned accounts ({res_n} of {len(churned)}) resolved, primarily via HubSpot's Findigs "
        "Products field (DecisionAssist/Screening), Sigma Companies BI fallback for the "
        "rest. This breakdown includes FTL accounts (full churned population, combined) -- "
        "it does NOT sum to the new true-churn-only kpis.accounts_churned_count; it sums to "
        "accounts_churned_count + ftl_count. Click into any reason/sub-reason row above or "
        "any product bar below to see the actual account list behind each number.")}

    ytd_rows = {s: [] for s in tx["segment_order"]}
    for a in churned:
        d = pdate(a.get("effective_churn_date"))
        if not d or d > today or d < ytd_start:
            continue
        s = a.get("segment") or "Unknown"
        if s not in ytd_rows:
            raise SystemExit(f"STOP: segment {s!r} is not in config.taxonomy.segment_order")
        ytd_rows[s].append(a)
    churn_by_segment_ytd = []
    for s in tx["segment_order"]:
        rs = ytd_rows[s]
        d_ = [a for a in rs if a.get("product_segment") == "DA"]
        f_ = [a for a in rs if a.get("product_segment") == "FS"]
        u_ = [a for a in rs if a.get("product_segment") not in ("DA", "FS")]
        churn_by_segment_ytd.append({
            "segment": s, "count_total": float(len(rs)), "acv_total": acv_sum(rs),
            "count_da_fs": float(len(d_) + len(f_)), "acv_da_fs": acv_sum(d_ + f_),
            "count_da": float(len(d_)), "acv_da": acv_sum(d_), "count_fs": float(len(f_)), "acv_fs": acv_sum(f_),
            "count_unclassified": float(len(u_)), "acv_unclassified": acv_sum(u_)})

    keys = tx["reason_source_coverage_keys"]
    cov = Counter((a.get("reason_source") or "none") if (a.get("reason_source") or "none") in keys else "none" for a in true_churn)
    reason_source_coverage = {k: cov.get(k, 0) for k in keys}

    fields = {"kpis": kpis, "by_segment_size": by_segment_size, "by_segment_product": by_segment_product,
              "by_product_breakdown": by_product_breakdown, "churn_by_segment_ytd": churn_by_segment_ytd,
              "churn_by_reason": churn_by_reason, "reason_source_coverage": reason_source_coverage}
    report_only = {"ftl_count": len(ftl), "ftl_acv_total": ftl_total, "forward_dated": [a["name"] for a in fwd_all]}
    return fields, report_only
