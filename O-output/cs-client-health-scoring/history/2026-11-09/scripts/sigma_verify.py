"""Prove that every saved Sigma result file matches what Sigma returned, without trusting
whoever wrote the file.

Why: the Sigma connector returns small results inline, so the agent has to write them to disk
itself. That copy can be wrong (a dropped row, a mistyped number, a value shifted to another
account). This script has Sigma compute a one-row fingerprint of each query's result and
compares it with the same fingerprint computed locally from the saved file. A copying mistake
can only cause a false stop, never a false pass.

Usage (all take --run-date YYYY-MM-DD --scratch <dir>):
  python3 sigma_verify.py checks   # after saving <name>_<MMDD>.json for every query:
                                   #   writes <name>_<MMDD>_check.sql (run each in Sigma, save
                                   #   the one-row result as <name>_<MMDD>_check.json)
  python3 sigma_verify.py compare  # PASS/FAIL per query; exit 1 on any FAIL or missing file
  python3 sigma_verify.py probes   # writes sigma_probe_<key>_<MMDD>.sql per element: selects
                                   #   every documented and query-used column, LIMIT 0 (no data
                                   #   returned). Sigma rejects it, naming the column, if any is
                                   #   missing. Save each successful result (it is
                                   #   {"columns":[],"rows":[]}) as sigma_probe_<key>_<MMDD>.json;
                                   #   on an error save nothing. contract_check.py reads those.

Fingerprint per query: row count, then per column:
  text:    non-null count, distinct count, total length, total character weight, and character
           weight times the key's character weight (ties the text to its row's account)
  numeric: non-null count, sum, and sum of value times the key's character weight
  boolean: true count, and the key's character weight summed over true rows
"Character weight" = for the lowercased value, sum over the characters 0-9 a-z of (position in
that list) x (times it appears). Sigma has no character-code function, so it is computed with
LENGTH/REPLACE, once per text column in a nested subquery. It changes when any one letter or
digit changes. The key is the query's first column.
"""
import json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run
import render_queries
from contract_cols import wanted


ONLY = []
CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"


def cw(x):
    x = x.lower()
    return sum((i + 1) * x.count(ch) for i, ch in enumerate(CHARS))


def cw_sql(c):
    return "(" + "+".join(f"(LENGTH({c})-LENGTH(REPLACE({c},'{ch}','')))*{i + 1}" for i, ch in enumerate(CHARS)) + ")"


def split_top(s):
    """Split on commas outside parentheses and quotes."""
    out, depth, cur, q = [], 0, "", None
    for ch in s:
        if q:
            cur += ch
            if ch == q:
                q = None
            continue
        if ch in "'\"":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    out.append(cur)
    return out


def aliases(sql):
    """Output column aliases of the top-level SELECT, in order."""
    m = re.search(r"^\s*SELECT\s+(.*?)\n\s*FROM\s", sql, re.S | re.I)
    if not m:
        raise SystemExit("cannot find the top-level SELECT ... FROM")
    names = []
    for item in split_top(m.group(1)):
        a = re.search(r'\bAS\s+"?(\w+)"?\s*$', item.strip(), re.I)
        if not a:
            raise SystemExit(f"select item has no AS alias: {item.strip()[:80]}")
        names.append(a.group(1))
    return names


def col_kind(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return "empty"
    if all(isinstance(v, bool) for v in vals):
        return "bool"
    if all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
        return "num"
    return "text"


def spec_for(names, rows):
    """List of (out_name, kind, col_index) fingerprint terms."""
    key_text = col_kind([r[0] for r in rows]) == "text"
    spec = [("n_rows", "count_rows", None)]
    for i, a in enumerate(names):
        k = col_kind([r[i] for r in rows])
        spec.append((f"c{i}", "count_nonnull", i))
        if k == "text":
            spec += [(f"d{i}", "count_distinct", i), (f"l{i}", "sum_length", i), (f"h{i}", "sum_cw", i)]
            if key_text and i:
                spec.append((f"k{i}", "sum_cw_keyed", i))
        elif k == "num":
            spec.append((f"s{i}", "sum", i))
            if key_text and i:
                spec.append((f"w{i}", "sum_weighted", i))
        elif k == "bool":
            spec.append((f"b{i}", "count_true", i))
            if key_text and i:
                spec.append((f"t{i}", "true_keyed", i))
    return spec


def sql_term(kind, i, names):
    """One aggregate over the nested subquery; "_h<i>" holds column i's character weight."""
    c = f'"{names[i]}"' if i is not None else None
    h, kh = f'"_h{i}"', '"_h0"'
    return {
        "count_rows": "COUNT(*)",
        "count_nonnull": f"COUNT({c})",
        "count_distinct": f"COUNT(DISTINCT {c})",
        "sum_length": f"SUM(LENGTH({c}))",
        "sum": f"SUM({c})",
        "sum_weighted": f"SUM({c} * {kh})",
        "count_true": f"SUM(CASE WHEN {c} THEN 1 ELSE 0 END)",
        "sum_cw": f"SUM({h})",
        "sum_cw_keyed": f"SUM({h} * {kh})",
        "true_keyed": f"SUM(CASE WHEN {c} THEN {kh} ELSE 0 END)",
    }[kind]


def check_sql(sql, names, rows):
    """The one-row fingerprint query: query -> lowercase text columns -> character weights -> aggregates."""
    spec = spec_for(names, rows)
    need = {i for _, k, i in spec if k in ("sum_cw", "sum_cw_keyed")}
    if any(k in ("sum_weighted", "sum_cw_keyed", "true_keyed") for _, k, _ in spec):
        need.add(0)
    need = sorted(need)
    inner = "SELECT t.* FROM (\n" + sql.strip() + "\n) t"
    if need:
        lower = ", ".join(f'LOWER("{names[i]}") AS "_l{i}"' for i in need)
        weights = ", ".join(cw_sql(f'"_l{i}"') + f' AS "_h{i}"' for i in need)
        inner = f"SELECT u.*, {weights} FROM (SELECT t.*, {lower} FROM (\n" + sql.strip() + "\n) t) u"
    terms = ", ".join(f"{sql_term(k, i, names)} AS {o}" for o, k, i in spec)
    return f"SELECT {terms} FROM ({inner}) v", spec


def local_term(kind, i, rows):
    col = [r[i] for r in rows] if i is not None else None
    if kind == "count_rows":
        return len(rows)
    if kind == "count_nonnull":
        return sum(v is not None for v in col)
    if kind == "count_distinct":
        return len({v for v in col if v is not None})
    if kind == "sum_length":
        return sum(len(v) for v in col if v is not None)
    if kind == "sum":
        vals = [v for v in col if v is not None]
        return sum(vals) if vals else None
    if kind == "sum_weighted":
        vals = [v * cw(r[0]) for v, r in zip(col, rows) if v is not None and r[0] is not None]
        return sum(vals) if vals else None
    if kind == "count_true":
        return sum(v is True for v in col)
    if kind == "sum_cw":
        vals = [cw(v) for v in col if v is not None]
        return sum(vals) if vals else None
    if kind == "sum_cw_keyed":
        vals = [cw(v) * cw(r[0]) for v, r in zip(col, rows) if v is not None and r[0] is not None]
        return sum(vals) if vals else None
    if kind == "true_keyed":
        return sum(cw(r[0]) for v, r in zip(col, rows) if v is True and r[0] is not None)


def same(a, b):
    if a is None or b is None:
        return a is None and b is None or (a in (None, 0) and b in (None, 0))
    a, b = float(a), float(b)
    return math.isclose(a, b, rel_tol=1e-6, abs_tol=1e-6)


def load_rows(path):
    d = json.load(open(path, encoding="utf-8"))
    return d["columns"], d["rows"]


def selected(run):
    names = list(run.cfg["sigma"]["queries"])
    return [n for n in names if n in ONLY] if ONLY else names


def cmd_checks(run):
    for name in selected(run):
        sql = render_queries.render(name, run)
        names = aliases(sql)
        res = run.path(f"{name}_{run.mmdd}.json")
        if not os.path.exists(res):
            raise SystemExit(f"{name}: result file not saved ({res})")
        cols, rows = load_rows(res)
        if len(cols) != len(names):
            raise SystemExit(f"{name}: file has {len(cols)} columns, query selects {len(names)}")
        check, spec = check_sql(sql, names, rows)
        open(run.path(f"{name}_{run.mmdd}_check.sql"), "w", encoding="utf-8").write(check)
        json.dump(spec, open(run.path(f"{name}_{run.mmdd}_check_spec.json"), "w"))
        print(f"{name}: {run.path(name + '_' + run.mmdd + '_check.sql')}")


def cmd_compare(run):
    bad = 0
    for name in selected(run):
        try:
            _, rows = load_rows(run.path(f"{name}_{run.mmdd}.json"))
            spec = json.load(open(run.path(f"{name}_{run.mmdd}_check_spec.json")))
            ccols, crow = load_rows(run.path(f"{name}_{run.mmdd}_check.json"))
        except FileNotFoundError as e:
            print(f"FAIL {name}: missing {e.filename}")
            bad += 1
            continue
        got = dict(zip([c.lower() for c in ccols], crow[0]))
        diffs = []
        for o, k, i in spec:
            mine, theirs = local_term(k, i, rows), got.get(o)
            if o not in got:
                diffs.append(f"{o} missing from check result")
            elif not same(mine, theirs):
                diffs.append(f"{o} ({k}, col {i}): file {mine} vs Sigma {theirs}")
        if diffs:
            bad += 1
            print(f"FAIL {name}: " + "; ".join(diffs))
        else:
            print(f"PASS {name}: {len(rows)} rows, {len(spec)} fingerprint terms match")
    sys.exit(1 if bad else 0)


def cmd_probes(run):
    for key, cols in wanted(run.cfg).items():
        el = run.cfg["sigma"]["elements"][key]
        sql = "SELECT " + ", ".join(cols) + f' FROM "datamodel"."{el["id"]}" LIMIT 0'
        p = run.path(f"sigma_probe_{key}_{run.mmdd}.sql")
        open(p, "w", encoding="utf-8").write(sql)
        print(f"{key}: {len(cols)} columns -> {p}")


if __name__ == "__main__":
    run, ns = parse_run("Verify saved Sigma results", [(("mode",), {"choices": ["checks", "compare", "probes"]}),
                                                       (("--only",), {"default": "", "help": "comma-separated query names"})])
    ONLY = [x for x in ns.only.split(",") if x]
    {"checks": cmd_checks, "compare": cmd_compare, "probes": cmd_probes}[ns.mode](run)
