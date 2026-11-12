"""Prepare the ImplementationsCache PUT body and prove the write landed.

Usage:
  python3 push_verify.py payload --run-date D --scratch S
      Writes put_body_<MMDD>.json: cache_key plus every config.target.managed_fields value from
      impl_record_<MMDD>.json. Send it with curl PUT (see SKILL.md).
  python3 push_verify.py verify  --run-date D --scratch S
      Compares readback_<MMDD>.json (a fresh curl GET after the PUT) with what was sent and with
      baseline_<MMDD>.json (the GET before the run). PASS needs: every managed field equals what
      was sent, value for value; every other field unchanged except updated_date. Exit 1 on FAIL.
Base44 answers 200 even when it silently drops a field, so the readback is the only proof.
"""
import json, sys
import im_common as C

IGNORE = {"updated_date"}


def one(x):
    return x[0] if isinstance(x, list) else x


def diffs(a, b, path=""):
    """Paths where a and b differ (numbers compared to 1e-9)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += diffs(a.get(k, "<missing>"), b.get(k, "<missing>"), f"{path}.{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diffs(x, y, f"{path}[{i}]")
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return [] if abs(a - b) <= 1e-9 * max(1, abs(a)) else [f"{path}: {a!r} vs {b!r}"]
    return [] if a == b else [f"{path}: {str(a)[:80]!r} vs {str(b)[:80]!r}"]


if __name__ == "__main__":
    run, ns = C.parse_run("ImplementationsCache push body and readback verify",
                                [(("mode",), {"choices": ["payload", "verify"]})])
    t = run.cfg["target"]
    if ns.mode == "payload":
        rec = run.load(f"impl_record_{run.mmdd}.json")
        missing = [f for f in t["managed_fields"] if f not in rec]
        if missing:
            sys.exit(f"STOP: record lacks managed fields {missing}")
        body = {"cache_key": t["cache_key"], **{f: rec[f] for f in t["managed_fields"]}}
        json.dump(body, open(run.path(f"put_body_{run.mmdd}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        print(f"wrote put_body_{run.mmdd}.json ({len(body)} fields)")
        sys.exit(0)
    sent = run.load(f"put_body_{run.mmdd}.json")
    back = one(run.load(f"readback_{run.mmdd}.json"))
    base = one(run.load(f"baseline_{run.mmdd}.json"))
    fails = []
    if back.get("id") != t["record_id"] or back.get("cache_key") != t["cache_key"]:
        fails.append(f"readback is not record {t['record_id']} / {t['cache_key']}")
    for f in t["managed_fields"]:
        fails += [f"managed {d}" for d in diffs(sent[f], back.get(f, "<missing>"), f)]
    for f in sorted((set(base) | set(back)) - set(t["managed_fields"]) - IGNORE - {"cache_key"}):
        fails += [f"unmanaged {d}" for d in diffs(base.get(f, "<missing>"), back.get(f, "<missing>"), f)]
    if fails:
        print(f"FAIL: {len(fails)} difference(s)")
        print("\n".join(fails[:40]))
        sys.exit(1)
    print(f"PASS: all {len(t['managed_fields'])} managed fields read back exactly as sent; nothing else changed")
