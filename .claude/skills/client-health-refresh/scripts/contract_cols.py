"""Sigma columns each element must have: everything config.json documents plus every quoted
column identifier the query files use. Shared by contract_check.py and sigma_verify.py."""
import os, re
from ch_common import SKILL_DIR


def query_columns(cfg):
    """{element_key: set of '"ident"'} used by queries/*.sql."""
    out = {}
    for name, q in cfg["sigma"]["queries"].items():
        el = cfg["sigma"]["elements"][q["element"]]
        sql = open(os.path.join(SKILL_DIR, "queries", name + ".sql"), encoding="utf-8").read()
        ids = {f'"{i}"' for i in re.findall(r'"([^"]+)"', sql) if i not in ("datamodel", el["id"])}
        out.setdefault(q["element"], set()).update(ids)
    return out


def documented(el):
    prefix = el.get("column_prefix", "")
    return {f'"{cid}"' for cid in el.get("columns", {}).values()} | {f'"{prefix}{c}"' for c in el.get("named_columns", [])}


def wanted(cfg):
    """{element_key: sorted list of '"ident"'}: documented plus query-used columns."""
    q = query_columns(cfg)
    return {k: sorted(documented(el) | q.get(k, set())) for k, el in cfg["sigma"]["elements"].items()}
