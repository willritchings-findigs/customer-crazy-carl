#!/usr/bin/env python3
"""Build AM Slack alert payloads from the week's band transitions (plan confirmed by Emma 2026-09-14).

Negative triggers: Green->Yellow, Yellow->Red, Green->Red, newly-scored Red, scored->Churned.
Kudos triggers (added per Emma 9/14): Red->Yellow, Yellow->Green, Red->Green — celebratory
card tagging the same owner. Unchanged bands never alert. Accounts that stay Red get ONE
grouped "still Red" digest (names + owners + weeks-red), no individual re-pings.

Inputs (paths below): history/wow_history.json (last two runs), the freshly pushed record
(for red_reasons/why), owner_map.json, hs_account_match.json (hs_object_id for record links).
Output: history/<run>/alerts_<run>.json — payloads + resolved tags, reviewable before posting,
and the dedupe ledger (each entry carries posted:false until a send marks it true; a rerun
skips account+transition pairs already marked posted).
"""
# Usage: python3 build_alerts.py --scratch <dir>   (current run = latest run in wow_history)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, HIST, REPO_ROOT

RUN, _ = parse_run("Build AM Slack alert payloads")
CFG = RUN.cfg
OWNER_MAP = os.path.join(REPO_ROOT, CFG["alerts"]["owner_source_of_truth"])
SCRATCH = RUN.scratch
PORTAL = CFG["hubspot"]["portal_id"]
CHANNEL = CFG["alerts"]["slack_channel_id"]
DASH_URL = CFG["target"]["dashboard_url"]
BAND_EMOJI = {"Red": "\U0001F534", "Yellow": "\U0001F7E1", "Green": "\U0001F7E2", "Churned": "⚫"}

def load(p): return json.load(open(p))

wow = load(os.path.join(HIST, "wow_history.json"))
runs = sorted(wow.keys())
prev_run, cur_run = runs[-2], runs[-1]
prev = {r["account"]: r for r in wow[prev_run]["accounts"]}
cur = {r["account"]: r for r in wow[cur_run]["accounts"]}
owners = load(OWNER_MAP)["accounts"]
hs = load(os.path.join(SCRATCH, "hs_account_match.json")) if os.path.exists(os.path.join(SCRATCH, "hs_account_match.json")) else {}

# methodology-driven flips (kind starts with 'methodology' in the run's wow_diff) never ping:
# a scoring-rule change isn't account movement — note them in the weekly report instead.
methodology_flips = set()
if os.path.isdir(SCRATCH):
    for f in os.listdir(SCRATCH):
        if f.startswith("wow_diff"):
            for fl in load(os.path.join(SCRATCH, f)).get("band_flips", []):
                if str(fl.get("kind", "")).startswith("methodology"):
                    methodology_flips.add(fl["account"])
            break

def weeks_red(name):
    n = 0
    for rk in reversed(runs):
        row = next((x for x in wow[rk]["accounts"] if x["account"] == name), None)
        if row and row.get("band") == "Red":
            n += 1
        else:
            break
    return n

ROW_WORDS = {
    "median_ttd_hours": "time-to-decision", "approval_rate_pct": "approval rate",
    "override_rate_pct": "override rate", "qa_pct": "QA rate",
    "support_ticket_ratio_per_100": "support-ticket ratio", "tes_pct": "technical escalations",
    "volume_trend_pct": "volume trend", "pms_integration_depth": "PMS integration",
    "Client communication sentiment": "Slack/Gong sentiment", "Pylon ticket tone": "Pylon ticket tone",
}
PILLAR_SHORT = {"Platform & Product Metrics": "Platform",
                "Strategic Alignment, Governance & Relationship": "Strategic",
                "Client Sentiment": "Sentiment"}

# full record (for pylon friction titles on Negative-pylon accounts) -- optional enrichment
_full = {}
for _cand in (os.path.join(SCRATCH, f) for f in os.listdir(SCRATCH) if f.startswith("new_record_")) if os.path.isdir(SCRATCH) else []:
    try:
        for _a in json.load(open(_cand)).get("accounts", []):
            _full[_a.get("resolved_name_sigma") or _a.get("input_name")] = _a
        break
    except Exception:
        pass

def _signals_from_why(why):
    """'k: Band | k2 (Band): Note' -> 'time-to-decision, support-ticket ratio red / override rate yellow'."""
    import re
    reds, yels, senti = [], [], []
    for piece in (why or "").split("|"):
        piece = piece.strip()
        km = re.match(r"([\w &/,'-]+?)(?:\s*\((Red|Yellow|Green)\))?:\s*(.*)", piece)
        if not km:
            continue
        key, band_in_name, rest = km.group(1).strip(), km.group(2), km.group(3).strip()
        band = band_in_name or (rest if rest in ("Red", "Yellow", "Green") else None)
        word = ROW_WORDS.get(key, key.replace("_", " "))
        if key in ("Client communication sentiment", "Pylon ticket tone"):
            # self-describing phrases ('Slack/Gong negative'), no band-word suffix
            if band in ("Red", "Yellow") and rest and rest not in ("Red", "Yellow", "Green"):
                prefix = "Slack/Gong" if key.startswith("Client") else "Pylon"
                senti.append(f"{prefix} {rest.lower()}")
            continue
        if band == "Red":
            reds.append(word)
        elif band == "Yellow":
            yels.append(word)
    bits = []
    if reds: bits.append(", ".join(reds) + " red")
    if yels: bits.append(", ".join(yels) + " yellow")
    if senti: bits.append(", ".join(senti))
    return " / ".join(bits)

def _pylon_titles(name):
    a = _full.get(name) or {}
    py = ((a.get("qualitative_pillars") or {}).get("client_sentiment") or {}).get("pylon_ticket_tone")
    if isinstance(py, dict) and py.get("classification") == "Negative":
        t = (py.get("pm_friction_titles") or [])[:2]
        n = py.get("pm_friction_count")
        if t:
            return f'{n} Pylon friction issues ("' + '", "'.join(str(x).split(" (")[0] for x in t) + '")'
    return None

def drivers_and_signals(row):
    """Structured-fields lines from the archived history row (Emma's approved format).
    Colors only — no numeric pillar scores in Slack (Emma 9/14)."""
    if not row.get("is_da"):
        return (f"Drivers: CSM churn-risk flag {row.get('csm_flag_value')} — Full-Screen account, flag-anchored score",
                None)
    pillars = [("Platform & Product", row.get("platform_band"), row.get("platform_value"), row.get("platform_why")),
               ("Strategic Alignment", row.get("strategic_band"), row.get("strategic_value"), row.get("strategic_why")),
               ("Client Sentiment", row.get("sentiment_band"), row.get("sentiment_value"), row.get("sentiment_why"))]
    bad = [p for p in pillars if p[1] in ("Red", "Yellow")]
    bad.sort(key=lambda p: (p[1] != "Red", p[2] if p[2] is not None else 999))
    if not bad:
        return (None, None)
    drivers = "Drivers: " + " · ".join(f"{n} {b.lower()}" for n, b, v, w in bad)
    sig_bits = [s for s in (_signals_from_why(w) for n, b, v, w in bad[:2]) if s]
    name_titles = _pylon_titles(row["account"])
    if name_titles:
        sig_bits.append(name_titles)
    signals = "Signals: " + " · ".join(sig_bits) if sig_bits else None
    return (drivers, signals)

def hs_link(name):
    oid = (hs.get(name) or {}).get("hs_object_id")
    # portal is in HubSpot's NA2 region — app-na2 host opens records directly (Emma-confirmed 9/14)
    return f"<https://app-na2.hubspot.com/contacts/{PORTAL}/record/0-2/{oid}|HubSpot ↗>" if oid else None

def owner_line(name):
    o = owners.get(name) or {}
    tags = []
    if o.get("am_slack_id"):
        tags.append(f"<@{o['am_slack_id']}>")
    elif o.get("am"):
        tags.append(f"{o['am']} (Slack ID unresolved)")
    if o.get("csa_slack_id"):
        tags.append(f"CSA: <@{o['csa_slack_id']}>")
    return " · ".join(tags) if tags else None

PILLARS = [("Platform & Product", "platform"), ("Strategic Alignment", "strategic"),
           ("Client Sentiment", "sentiment")]

def kudos_lines(p, c):
    """Middle lines for an improvement card: what moved, what's still open."""
    if not c.get("is_da"):
        was = (p or {}).get("csm_flag_value")
        return [f"CSM churn-risk flag now {c.get('csm_flag_value')}" + (f" (was {was})" if was else "")]
    moved, watching = [], []
    for label, k in PILLARS:
        ob, nb = (p or {}).get(f"{k}_band"), c.get(f"{k}_band")
        rank = {"Red": 0, "Yellow": 1, "Green": 2}
        if ob in rank and nb in rank and rank[nb] > rank[ob]:
            moved.append(f"{label} {ob} → {nb}")
        if nb in ("Red", "Yellow"):
            watching.append(f"{label} still {nb.lower()}")
    lines = []
    if moved:
        lines.append("What moved: " + " · ".join(moved))
    if not watching:
        lines.append("All pillars Green")
    else:
        lines.append("Still watching: " + " · ".join(watching))
    return lines

alerts, kudos, still_red = [], [], []
for name, c in cur.items():
    p = prev.get(name)
    ob, nb = (p or {}).get("band"), c.get("band")
    if nb == "Red" and ob == "Red":
        still_red.append((name, weeks_red(name)))
        continue
    trigger, kind = None, "alert"
    if ob == "Green" and nb == "Yellow": trigger = "Green -> Yellow"
    elif ob == "Yellow" and nb == "Red": trigger = "Yellow -> Red"
    elif ob == "Green" and nb == "Red": trigger = "Green -> Red"
    elif nb == "Red" and ob in (None, "None"): trigger = "newly scored -> Red"
    elif nb == "Churned" and ob in ("Green", "Yellow", "Red"): trigger = f"{ob} -> Churned"
    elif ob == "Red" and nb == "Yellow": trigger, kind = "Red -> Yellow", "kudos"
    elif ob == "Yellow" and nb == "Green": trigger, kind = "Yellow -> Green", "kudos"
    elif ob == "Red" and nb == "Green": trigger, kind = "Red -> Green", "kudos"
    if not trigger or name in methodology_flips:
        continue
    o = owners.get(name) or {}
    arrow = trigger.replace("->", "→")
    if kind == "kudos":
        lead = "🎉" if nb == "Green" else "📈"
        lines = [f"{lead} *{name}* — improved {arrow}, nice work"]
        lines.extend(kudos_lines(p, c))
    else:
        lines = [f"{BAND_EMOJI.get(nb, '')} *{name}* — moved {arrow}"]
        drv, sig = drivers_and_signals(c)
        if drv: lines.append(drv)
        if sig: lines.append(sig)
    tail = ["Owner: " + (owner_line(name) or "_unresolved — not in the ownership sheet_"),
            hs_link(name) or "(no HubSpot record matched)",
            f"<{DASH_URL}|Dashboard ↗>"]
    lines.append(" · ".join(tail))
    (kudos if kind == "kudos" else alerts).append(
        {"account": name, "transition": trigger, "band": nb,
         "am": o.get("am"), "am_slack_id": o.get("am_slack_id"),
         "csa": o.get("csa"), "csa_slack_id": o.get("csa_slack_id"),
         "message": "\n".join(lines), "posted": False})

still_red.sort(key=lambda x: (-x[1], x[0].lower()))
digest = None
if still_red:
    bits = []
    for name, wr in still_red:
        o = owners.get(name) or {}
        who = (o.get("am") or "unassigned").split()[0]
        bits.append(f"{name} ({who}, {wr} wk{'s' if wr != 1 else ''})")
    digest = {"message": (f"⚪ Still Red this week ({len(still_red)}), no change — grouped so no one gets "
                          f"re-pinged: " + " · ".join(bits)),
              "accounts": [n for n, _ in still_red], "posted": False}

run_dir = os.path.join(HIST, cur_run)
os.makedirs(run_dir, exist_ok=True)
out_path = os.path.join(run_dir, f"alerts_{cur_run}.json")
# dedupe: keep posted marks from an earlier build the same week
old = load(out_path) if os.path.exists(out_path) else {}
posted_pairs = {(a["account"], a["transition"])
                for a in old.get("alerts", []) + old.get("kudos", []) if a.get("posted")}
for a in alerts + kudos:
    if (a["account"], a["transition"]) in posted_pairs:
        a["posted"] = True
n_ch = sum(1 for a in alerts if a['band'] == 'Churned')
result = {"run": cur_run, "prev_run": prev_run, "channel": CHANNEL,
          "header": f":stethoscope: *Client health weekly refresh {cur_run}* — {len(alerts)} alert(s): "
                    f"{sum(1 for a in alerts if a['band'] == 'Red')} newly Red, "
                    f"{sum(1 for a in alerts if a['band'] == 'Yellow')} worsened to Yellow"
                    + (f", {n_ch} churned" if n_ch else "")
                    + (f" · {len(kudos)} improved 🎉" if kudos else "")
                    + f" · <{DASH_URL}|Dashboard ↗>",
          "alerts": alerts, "kudos": kudos, "still_red_digest": digest}
json.dump(result, open(out_path, "w"), indent=1)
print(f"{out_path}\n{result['header']}")
for a in alerts:
    print("\n--- ALERT ---")
    print(a["message"])
for a in kudos:
    print("\n--- KUDOS ---")
    print(a["message"])
if digest:
    print("\n--- DIGEST (first 12 lines) ---")
    print("\n".join(digest["message"].splitlines()[:12]))
