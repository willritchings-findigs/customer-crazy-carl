"""Run context for support-metrics-refresh.

Reuses the client-health-refresh helpers (run date, config, query rendering, Sigma fingerprint
checks, credentials) pointed at THIS skill's folder via CX_SKILL_DIR, and adds the SQL pieces that
are generated from config.json rather than written by hand:
  {sla_target_hours}    CASE on channel -> first-response target in hours (config.channels)
  {friction_case}       CASE on columns cat + subj (lowercased subject) -> theme (config.friction_themes)
  {friction_categories} the categories that have themes
  {na_statuses}         Needs Attention statuses (config.needs_attention)
  {na_limit}            Needs Attention list length
  {top_agents}          named agents ranked per view in s8_agents (config.breakdowns.by_agent_rows)
Every script imports this module first.
"""
import json, os, sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["CX_SKILL_DIR"] = SKILL_DIR
SHARED = os.path.join(os.path.dirname(SKILL_DIR), "client-health-refresh", "scripts")
sys.path.insert(0, SHARED)

import ch_common  # noqa: E402  (after CX_SKILL_DIR is set)
from ch_common import parse_run, REPO_ROOT  # noqa: E402,F401

HIST = os.path.join(REPO_ROOT, "O-output", "cx-support-metrics", "history")
REPORTS = os.path.join(REPO_ROOT, "O-output", "cx-support-metrics")
CASE_CAT = '"inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY"'
CASE_SUBJ = '"inode-1dBuhhkgQkWXslu27HE64N/CASE_SUBJECT"'
CASE_ORIGIN = '"inode-1dBuhhkgQkWXslu27HE64N/CASE_ORIGIN"'


def q(s):
    return "'" + str(s).replace("'", "''") + "'"


def generated_fragments(cfg):
    ch = cfg["channels"]
    sla = "CASE " + " ".join(f"WHEN {CASE_ORIGIN} = {q(k)} THEN {float(v['target_hours'])}" for k, v in ch.items()) + " ELSE NULL END"
    ft = {k: v for k, v in cfg["friction_themes"].items() if not k.startswith("_")}
    whens = []
    for catg, themes in ft.items():
        for theme, pats in themes:
            likes = " OR ".join(f"subj LIKE {q(p)}" for p in pats)
            whens.append(f"WHEN cat = {q(catg)} AND ({likes}) THEN {q(theme)}")
    friction = "CASE " + " ".join(whens) + " ELSE 'Other' END"
    na = cfg["needs_attention"]
    return {
        "sla_target_hours": sla,
        "friction_case": friction,
        "friction_categories": ", ".join(q(c) for c in ft),
        "na_statuses": ", ".join(q(s) for s in na["waiting_on_findigs_statuses"]),
        "na_limit": str(int(na["limit"])),
        "top_agents": str(int(cfg["breakdowns"]["by_agent_rows"])),
    }


def prepare(run):
    """Write generated fragments into the scratch dir and register them as sql_fragments."""
    os.makedirs(run.scratch, exist_ok=True)
    for name, sql in generated_fragments(run.cfg).items():
        p = run.path(f"_fragment_{name}.sql")
        open(p, "w", encoding="utf-8").write(sql + "\n")
        run.cfg.setdefault("sql_fragments", {})[name] = p  # absolute path wins in os.path.join
    return run


def get_run(description, extra_args=None):
    run, ns = parse_run(description, extra_args)
    return prepare(run), ns
