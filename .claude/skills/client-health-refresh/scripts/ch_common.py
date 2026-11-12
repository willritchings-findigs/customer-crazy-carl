"""Shared run context for the client-health-refresh scripts: config, run date, window, paths.

Every script takes the same two flags:
  --run-date YYYY-MM-DD   (default: today, UTC)
  --scratch DIR           (default: current directory) where this run's pulls and outputs live
"""
import argparse, datetime as dt, json, operator, os

# Other CS/CX skills reuse these helpers by setting CX_SKILL_DIR to their own skill folder.
SKILL_DIR = os.environ.get("CX_SKILL_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.environ.get("REPO_ROOT") or os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR)))
CH_DIR = os.path.join(REPO_ROOT, "O-output", "cs-client-health-scoring")
HIST = os.path.join(CH_DIR, "history")
CONFIG_PATH = os.path.join(SKILL_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


class Run:
    def __init__(self, run_date, scratch, cfg):
        self.cfg = cfg
        self.date = run_date
        self.iso = run_date.isoformat()
        self.mmdd = run_date.strftime("%m%d")
        days = cfg["window"]["trailing_days"]
        self.window_start = run_date - dt.timedelta(days=days)
        self.window_start_iso = self.window_start.isoformat()
        self.window = f"{self.window_start_iso} to {self.iso} (rolling trailing {days}d)"
        self.scratch = os.path.abspath(scratch)

    def path(self, fn):
        return os.path.join(self.scratch, fn)

    def load(self, fn):
        with open(self.path(fn), encoding="utf-8") as f:
            return json.load(f)


def parse_run(description="", extra_args=None):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--run-date", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    ap.add_argument("--scratch", default=os.getcwd())
    for args, kwargs in (extra_args or []):
        ap.add_argument(*args, **kwargs)
    ns = ap.parse_args()
    run = Run(dt.date.fromisoformat(ns.run_date), ns.scratch, load_config())
    return run, ns


_OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt, "<=": operator.le}


def band_from_rule(rule, v):
    """Green if rule['green'] passes, else Yellow if rule['yellow'] passes, else Red."""
    if "always" in rule:
        return rule["always"]
    op, cut = rule["green"]
    if _OPS[op](v, cut):
        return "Green"
    op, cut = rule["yellow"]
    if _OPS[op](v, cut):
        return "Yellow"
    return "Red"
