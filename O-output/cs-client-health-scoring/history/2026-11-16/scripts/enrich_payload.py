#!/usr/bin/env python3
"""Enrich the overview payload with dashboard convenience fields, post-merge / pre-push.

Adds per account (RECOMPUTED every run — never carried forward from baseline):
  account_manager, csa           <- owner_map.json (xlsx-derived SOT, not HubSpot csm_owner)
  prior_band                     <- previous run's band from wow_history.json
  weeks_red                      <- consecutive-Red streak ending at the current run
  band_history                   <- [{run, band, composite_value}] across all runs (popout graph)

Usage: python3 enrich_payload.py <payload.json> <wow_history.json> <owner_map.json>
Rewrites payload.json in place. Run AFTER archive_history.py (wow_history must contain the
current run) and BEFORE the overview PUT.
"""
import json
import sys


def aname(a):
    return a.get("resolved_name_sigma") or a.get("input_name")


def main(payload_path, wow_path, owner_path):
    payload = json.load(open(payload_path))
    wow = json.load(open(wow_path))
    owners = json.load(open(owner_path)).get("accounts", {})

    runs = sorted(wow.keys())  # ISO dates sort correctly
    cur_run, prior_run = runs[-1], (runs[-2] if len(runs) > 1 else None)

    # per-run band/composite lookup keyed by account name
    per_run = {}
    for r in runs:
        per_run[r] = {row["account"]: row for row in wow[r].get("accounts", [])}

    n_owner, n_hist = 0, 0
    for a in payload["accounts"]:
        nm = aname(a)
        o = owners.get(nm) or {}
        a["account_manager"] = o.get("am")
        a["csa"] = o.get("csa")
        if o.get("am"):
            n_owner += 1

        hist = []
        for r in runs:
            row = per_run[r].get(nm)
            if row:
                hist.append({"run": r, "band": row.get("band"),
                             "composite_value": row.get("composite_value")})
        a["band_history"] = hist
        if hist:
            n_hist += 1

        a["prior_band"] = (per_run.get(prior_run, {}).get(nm) or {}).get("band") if prior_run else None

        weeks_red = 0
        for r in reversed(runs):
            row = per_run[r].get(nm)
            if row and row.get("band") == "Red":
                weeks_red += 1
            else:
                break
        a["weeks_red"] = weeks_red

    json.dump(payload, open(payload_path, "w"))
    print(f"enriched {len(payload['accounts'])} accounts: owners {n_owner}, "
          f"band_history {n_hist}, runs {runs}, prior_run {prior_run}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
