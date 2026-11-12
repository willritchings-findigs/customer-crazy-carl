"""Render this skill's Sigma queries for a run.

Usage: python3 render.py --run-date YYYY-MM-DD --scratch <dir>
Writes <scratch>/<name>_<MMDD>.sql for every query in config.sigma.queries. Send each file's SQL to
Sigma exactly as written and save the result under the query's output name.
"""
import sm_common  # sets CX_SKILL_DIR first
import render_queries

if __name__ == "__main__":
    run, _ = sm_common.get_run("Render Support Metrics queries")
    for name in run.cfg["sigma"]["queries"]:
        path = run.path(f"{name}_{run.mmdd}.sql")
        open(path, "w", encoding="utf-8").write(render_queries.render(name, run))
        print(f"{name}: {path}")
    print("window:", {k: v for k, v in render_queries.placeholders(run).items() if k.endswith("start") or k == "anchor"})
