"""Regenerate the config-driven sections of the Client Health docs.

Usage: python3 docs/client-health/build_docs.py
Rewrites every block between
  <!-- BEGIN GENERATED: <name> -->  and  <!-- END GENERATED: <name> -->
in design.md and am-guide.md, using .claude/skills/client-health-refresh/config.json (numbers)
and metrics_catalog.json (definitions). Run it after any config change and republish. Never edit
a generated block by hand: the next run overwrites it.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CFG = json.load(open(os.path.join(ROOT, ".claude", "skills", "client-health-refresh", "config.json"), encoding="utf-8"))
CAT = json.load(open(os.path.join(HERE, "metrics_catalog.json"), encoding="utf-8"))
SC = CFG["scoring"]
SEGS = ["ENT", "MM", "SMB"]
OPS = {">": ">", ">=": "≥", "<": "<", "<=": "≤"}
PILLAR = {"platform": ("platform_product_metrics", "Platform & Product Metrics", "row_weights_platform"),
          "strategic": ("strategic_alignment_governance", "Strategic Alignment, Governance & Relationship", "row_weights_strategic"),
          "sentiment": ("client_sentiment", "Client Sentiment", "row_weights_sentiment")}


def fmt_rule(r):
    """{'green': ['>', 50], 'yellow': ['>=', 35]} -> 'Green > 50 · Yellow ≥ 35 · else Red'"""
    if "always" in r:
        return f"Always {r['always']} (not gated)"
    g, y = r.get("green"), r.get("yellow")
    s = f"Green {OPS[g[0]]} {g[1]:g} · Yellow {OPS[y[0]]} {y[1]:g} · else Red"
    if r.get("provisional"):
        s += " (provisional)"
    return s


def thresholds(key, unit):
    mb = SC["metric_bands"].get(key)
    if not mb:
        return "—"
    if any(s in mb for s in SEGS):
        parts = [f"{s}: {fmt_rule(mb[s])}" for s in SEGS if s in mb]
        return "<br>".join(parts)
    s = fmt_rule(mb)
    if "fs_accounts_always" in mb:
        s += f"<br>Full-Screen accounts: always {mb['fs_accounts_always']}"
    if "pending" in mb:
        s += f"<br>Pending: {mb['pending']}"
    return s


def rows_for(pillar):
    return [r for r in CAT["rows"] if r["pillar"] == pillar]


def block_metrics_library():
    out = ["| Metric | Definition | Calculation | Unit | Source | Refreshed | Green / Yellow / Red |",
           "|---|---|---|---|---|---|---|"]
    for r in CAT["rows"]:
        out.append(f"| **{r['label']}** | {r['definition']} | {r['calculation']} | {r['unit']} | {r['source']} | "
                   f"{r['refresh']} | {thresholds(r.get('threshold_key', ''), r['unit']) if r.get('threshold_key') else ('Band set directly' if r['refresh'] != 'No data' else '—')} |")
    out += ["", "**Context fields (shown on the dashboard, never scored)**", "",
            "| Field | Definition | Unit | Source | Refreshed |", "|---|---|---|---|---|"]
    for r in CAT["context"]:
        out.append(f"| **{r['label']}** | {r['definition']} | {r['unit']} | {r['source']} | {r['refresh']} |")
    return "\n".join(out)


def block_scoring_rows():
    out = []
    for p, (pk, plabel, wkey) in PILLAR.items():
        W = SC[wkey]
        out += [f"#### {plabel} ({SC['pillar_weights'][pk]}% of the overall score)", "",
                "| Row | What it measures | Source | Refreshed | Weight ENT | Weight MM | Weight SMB |",
                "|---|---|---|---|---|---|---|"]
        for r in rows_for(p):
            ws = [str(W[s].get(r["key"], "—")) for s in SEGS]
            out.append(f"| {r['label']} | {r['definition']} | {r['source']} | {r['refresh']} | " + " | ".join(ws) + " |")
        out.append("")
    return "\n".join(out).rstrip()


def block_rollup_rules():
    b2s = SC["band_to_score"]; pvb = SC["pillar_value_bands"]; pw = SC["pillar_weights"]
    return "\n".join([
        f"1. **Each row gets a band** (rules in the metrics library). Rows with no data are skipped, not counted as Red.",
        f"2. **Pillar value** = weighted average of row scores, where Green = {b2s['Green']}, Yellow = {b2s['Yellow']}, Red = {b2s['Red']}, using the segment's row weights above.",
        f"3. **Pillar band:** two or more Red rows → Red. Exactly one Red row → Yellow. Otherwise value ≥ {pvb['green_min']} → Green, ≥ {pvb['yellow_min']} → Yellow, and below {pvb['yellow_min']} is capped at Yellow (a pillar can't be Red without two Red rows).",
        f"4. **Overall value** = pillar values weighted {pw['platform_product_metrics']} / {pw['strategic_alignment_governance']} / {pw['client_sentiment']} (Platform / Strategic / Sentiment), re-weighted over the pillars that have data. Shown for context; the band below does not use it.",
        "5. **Overall band:** two or more Red pillars → Red. One Red pillar → Yellow. All pillars Green → Green. Anything else → Yellow.",
        "6. **Overrides, in order:** a Red CSM churn-risk flag forces Red; then a HubSpot client-health override, if set, replaces the result entirely.",
        f"7. **Segments:** weights differ by segment (ENT, MM, SMB). {', '.join(f'{k} is scored as {v}' for k, v in SC['segment_map'].items() if k != v)}.",
    ])


def block_validation():
    v = CFG["validation"]
    floors = ", ".join(f"{k} ≥ {n} accounts" for k, n in v["join_coverage_floors"].items())
    return "\n".join([
        "Every run must pass all of these before anything is pushed. Any failure stops the run and DMs Will; nothing reaches the dashboard or the channel.",
        "",
        "| Check | What it proves |", "|---|---|",
        "| Pre-flight contract check | Credentials resolve; the Base44 record has the expected fields and account count; every Sigma column the queries use exists; every HubSpot property exists. |",
        "| Sigma fingerprint check | Every saved Sigma result matches what Sigma returned (row counts, sums, text fingerprints, each value tied to its account). |",
        "| Threshold reproduction | Re-banding last week's values with the config reproduces last week's bands exactly (catches a changed threshold). |",
        f"| Algorithm unit test | {len(v['pilot_accounts_unit_test'])} pilot accounts' pillars and overall bands reproduce exactly from last week's inputs. |",
        f"| Join coverage | Fresh data joins to enough accounts: {floors}. |",
        f"| Structural diff | No band (Green / Yellow / Red / Churned) gains or loses more than {v['structural_diff_max_band_move']} accounts in one week; every flip is explained. |",
        "| No all-zero metrics | No metric is zero for every account (a sign of a broken query). |",
        "| Unit cross-check | Every account's live units match an independent source (Unit Counts BI). |",
        f"| Gong safety stop | Gong matches at least one account and at least {CFG['gong']['min_matched_ratio_vs_prior']:.0%} of the prior run's matched accounts. |",
        "| Read-back verify | After the push, the record is read back and compared field by field with what was sent. |",
    ])


def block_alert_rules():
    a = CFG["alerts"]
    return "\n".join([
        f"- **Individual alert** (pings the owner) when an account moves: {', '.join(t.replace('->', ' → ') for t in a['negative_transitions'])}.",
        f"- **Kudos card** when an account improves: {', '.join(t.replace('->', ' → ') for t in a['kudos_transitions'])}.",
        "- **Still Red:** one grouped digest listing every account that stayed Red, with how many weeks; nobody is re-pinged individually.",
        f"- Everything posts to {a['slack_channel_name']}, and only after a successful run.",
    ])


def _words(regex):
    return [w.replace("\\b", "").strip() for w in regex.split("|")]


def block_gong_tips():
    g = CFG["gong"]
    review = ", ".join(f"“{w}”" for w in _words(g["review_call_title_regex"]))
    execs = ", ".join(w.upper() if len(w) <= 3 else w.title() for w in _words(g["exec_title_regex"]))
    return "\n".join([
        f"- **Business reviews count when the Gong call title says so.** A call counts as a review if its title contains one of: {review}. A great QBR titled “Weekly sync” doesn't count.",
        f"- **Exec titles that count** (client attendees only, as written in Gong): {execs}. Coordinators, managers and specialists don't count.",
        "- **Invite client attendees with their work email.** Calls are matched to your account by the client's company email domain. A client on a personal Gmail address, or a dial-in with no email, may not be credited.",
        "- **Findigs attendees never count**, including our own executives.",
    ])


BLOCKS = {"gong_tips": block_gong_tips, "metrics_library": block_metrics_library, "scoring_rows": block_scoring_rows,
          "rollup_rules": block_rollup_rules, "validation": block_validation, "alert_rules": block_alert_rules}


def render(path):
    s = open(path, encoding="utf-8").read()
    for name, fn in BLOCKS.items():
        pat = re.compile(rf"(<!-- BEGIN GENERATED: {name} -->\n).*?(<!-- END GENERATED: {name} -->)", re.S)
        s = pat.sub(lambda m: m.group(1) + fn() + "\n" + m.group(2), s)
    open(path, "w", encoding="utf-8", newline="\n").write(s)
    print(f"rendered {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    for f in ("design.md", "am-guide.md"):
        p = os.path.join(HERE, f)
        if os.path.exists(p):
            render(p)
