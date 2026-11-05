"""Render the Sigma query templates in ../queries/ for one run.

Usage: python3 render_queries.py --run-date YYYY-MM-DD --scratch <dir>
Writes <scratch>/<name>_<MMDD>.sql for every query in config.sigma.queries. Send each file's
SQL to Sigma exactly as written (query type "datamodel", config.sigma.data_model_id) and save
the result as the JSON named in that query's "output".

Placeholders: {window_start} {window_end}  = trailing window ending on the run date
              {prior_start} {prior_end}    = the equal-length window immediately before it
              {revenue_year}               = the run date's year
"""
import datetime as dt, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, SKILL_DIR

QUERY_DIR = os.path.join(SKILL_DIR, "queries")


def placeholders(run):
    days = run.cfg["window"]["trailing_days"]
    prior_end = run.window_start - dt.timedelta(days=1)
    return {
        "window_start": run.window_start_iso,
        "window_end": run.iso,
        "prior_start": (prior_end - dt.timedelta(days=days)).isoformat(),
        "prior_end": prior_end.isoformat(),
        "revenue_year": str(run.date.year),
    }


def render(name, run):
    sql = open(os.path.join(QUERY_DIR, name + ".sql"), encoding="utf-8").read()
    out = sql
    for k, v in placeholders(run).items():
        out = out.replace("{" + k + "}", v)
    left = re.findall(r"\{[a-z_]+\}", out)
    if left:
        raise SystemExit(f"{name}: unfilled placeholders {left}")
    return out


if __name__ == "__main__":
    run, _ = parse_run("Render Sigma queries for a run")
    for name in run.cfg["sigma"]["queries"]:
        path = run.path(f"{name}_{run.mmdd}.sql")
        open(path, "w", encoding="utf-8").write(render(name, run))
        print(f"{name}: {path}")
    print("window:", placeholders(run))
