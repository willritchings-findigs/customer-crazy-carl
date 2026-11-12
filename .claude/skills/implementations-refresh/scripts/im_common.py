"""Run context for implementations-refresh: reuses the client-health-refresh helpers (run date,
config, credentials) pointed at this skill's folder via CX_SKILL_DIR."""
import os, sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["CX_SKILL_DIR"] = SKILL_DIR
sys.path.insert(0, os.path.join(os.path.dirname(SKILL_DIR), "client-health-refresh", "scripts"))

import ch_common  # noqa: E402
from ch_common import parse_run, REPO_ROOT  # noqa: E402,F401

HIST = os.path.join(REPO_ROOT, "O-output", "cx-implementations", "history")
REPORTS = os.path.join(REPO_ROOT, "O-output", "cx-implementations")


def one(x):
    return x[0] if isinstance(x, list) else x
