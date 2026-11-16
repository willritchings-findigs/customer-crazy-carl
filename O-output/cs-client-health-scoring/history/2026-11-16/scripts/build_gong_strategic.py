"""Build gong_strategic_rows.json: which client accounts Findigs met with on Gong, and who attended.

Usage: python3 build_gong_strategic.py --run-date YYYY-MM-DD --scratch <dir>
Reads  <scratch>/gong_calls_p*.json (gong_pull.py), <scratch>/baseline_<MMDD>.json,
       <scratch>/hs_account_match.json (match_hs_accounts.py), and the prior run's
       gong_strategic_rows.json from history/ (for the safety stop).
Writes <scratch>/gong_strategic_rows.json, one entry per matched account:
  calls_90d            calls in the window with at least one attendee from the account
  review_call_titles   titles matching config.gong.review_call_title_regex (first 5)
  exec_titles_seen     distinct titles of CLIENT attendees matching config.gong.exec_title_regex
  sample_titles        first 5 call titles
  client_attendees     distinct client attendees across those calls (informational)
  exec_attendees       distinct client attendees with an exec-level title (informational)

Rules (all values in config.gong):
- Findigs employees never count. An attendee is internal if Gong labels them "Internal" or
  their email domain is in internal_email_domains. Internal attendees are ignored for matching
  and for exec titles (decided by Will and Alex Schaper, 2026-11-12: the score measures whether
  Findigs' account team is engaging the client's decision-makers).
- An attendee counts as the account's client attendee only if they are not internal AND either
  their email domain is one of the account's domains, or they have no email and Gong labels them
  "External" (typically a dial-in). Other external attendees (PMS vendors, consultants, other
  companies on the call) and no-email attendees labelled "Unknown" get no credit.
- Matching is by email domain only: the attendee's domain must be one of the account's HubSpot
  company domains (hs_account_match.json) or an extra domain listed for it in
  account_domain_aliases (e.g. a parent company's domain). Free-mail domains never match. Gong's "affiliation"
  field holds Internal/External/Unknown, not a company name, so name matching is not possible
  from Gong data; accounts without a HubSpot domain cannot match.
- Safety stop: exit 1 (stop the run, post the failure to #gtm-automation-log) if no account matches, or fewer than
  min_matched_ratio_vs_prior x the prior run's matched accounts.
"""
import glob, json, os, re, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ch_common import parse_run, HIST


def domain_of(email):
    return (email or "").rsplit("@", 1)[-1].strip().lower() if "@" in (email or "") else ""


def prior_rows(run):
    """gong_strategic_rows.json from the latest archived run before this run date, or None."""
    dirs = sorted(d for d in os.listdir(HIST) if re.match(r"\d{4}-\d{2}-\d{2}$", d) and d < run.iso)
    for d in reversed(dirs):
        p = os.path.join(HIST, d, "gong_strategic_rows.json")
        if os.path.exists(p):
            return d, json.load(open(p, encoding="utf-8"))
    return None, None


def build(cfg, calls, accounts_names, hs_match):
    g = cfg["gong"]
    internal = {d.lower() for d in g["internal_email_domains"]}
    free = {d.lower() for d in g["free_email_domains"]}
    review_re = re.compile(g["review_call_title_regex"], re.I)
    exec_re = re.compile(g["exec_title_regex"], re.I)

    aliases = {k: v for k, v in g.get("account_domain_aliases", {}).items() if not k.startswith("_")}
    dom_to_accts = defaultdict(set)
    for nm in accounts_names:
        for d in ((hs_match.get(nm) or {}).get("domains") or []) + aliases.get(nm, []):
            d = (d or "").strip().lower()
            if d and d not in free and d not in internal:
                dom_to_accts[d].add(nm)

    def is_internal(p):
        return p.get("affiliation") == "Internal" or domain_of(p.get("email")) in internal

    acct_calls = defaultdict(list)
    acct_people = defaultdict(dict)  # account -> {person key: title}
    other_domains = defaultdict(set)  # outside domain -> accounts whose calls it appeared on
    for c in calls:
        parties = [p for p in (c.get("parties") or []) if not is_internal(p)]
        matched = set()
        for p in parties:
            matched |= dom_to_accts.get(domain_of(p.get("email")), set())
        for p in parties:
            d = domain_of(p.get("email"))
            if matched and d and d not in dom_to_accts and d not in free:
                other_domains[d] |= matched
        for nm in matched:
            acct_calls[nm].append(c)
            acct_doms = {d for d, a in dom_to_accts.items() if nm in a}
            for p in parties:
                dom = domain_of(p.get("email"))
                client = dom in acct_doms or (not dom and p.get("affiliation") == "External")
                if not client:
                    continue
                key = (p.get("email") or p.get("name") or "").strip().lower()
                if key:
                    acct_people[nm].setdefault(key, p.get("title") or "")

    out = {}
    for nm in sorted(acct_calls):
        clist = acct_calls[nm]
        titles = [c.get("title") or "" for c in clist]
        people = acct_people[nm]
        execs = {k: t for k, t in people.items() if t and exec_re.search(t)}
        out[nm] = {
            "calls_90d": len(clist),
            "review_call_titles": [t for t in titles if review_re.search(t)][:5],
            "exec_titles_seen": sorted(set(execs.values())),
            "sample_titles": titles[:5],
            "client_attendees": len(people),
            "exec_attendees": len(execs),
        }
    return out, other_domains


if __name__ == "__main__":
    run, _ = parse_run("Build Gong strategic rows")
    cfg = run.cfg
    calls = []
    for fn in sorted(glob.glob(run.path("gong_calls_p*.json"))):
        calls.extend(json.load(open(fn, encoding="utf-8")))
    if not calls:
        raise SystemExit("STOP: no gong_calls_p*.json in scratch; run gong_pull.py first")
    base = run.load(f"baseline_{run.mmdd}.json")
    names = [a.get("resolved_name_sigma") or a.get("input_name") for a in base["accounts"]]
    hs_match = run.load("hs_account_match.json")

    out, other = build(cfg, calls, names, hs_match)
    json.dump(out, open(run.path("gong_strategic_rows.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    n_calls = sum(v["calls_90d"] for v in out.values())
    print(f"calls loaded {len(calls)}; accounts matched {len(out)}; calls assigned {n_calls}; "
          f"accounts with a review call {sum(1 for v in out.values() if v['review_call_titles'])}; "
          f"with a client exec {sum(1 for v in out.values() if v['exec_attendees'])}")

    top = sorted(other.items(), key=lambda kv: -len(kv[1]))[:10]
    if top:
        print("outside domains on client calls (no credit; add to config.gong.account_domain_aliases "
              "if one is really the client, e.g. a parent company):")
        for d, accts in top:
            print(f"  {d}: on calls for {sorted(accts)[:4]}")

    pdate, prev = prior_rows(run)
    ratio = cfg["gong"]["min_matched_ratio_vs_prior"]
    if not out:
        raise SystemExit("STOP: Gong matched 0 accounts. Post the failure to #gtm-automation-log; do not merge.")
    if prev and len(out) < ratio * len(prev):
        raise SystemExit(f"STOP: Gong matched {len(out)} accounts vs {len(prev)} on {pdate} "
                         f"(below {ratio:.0%}). Post the failure to #gtm-automation-log; do not merge.")
    if prev:
        gained, lost = sorted(set(out) - set(prev)), sorted(set(prev) - set(out))
        print(f"vs {pdate}: {len(prev)} -> {len(out)} accounts; new {gained}; dropped {lost}")
