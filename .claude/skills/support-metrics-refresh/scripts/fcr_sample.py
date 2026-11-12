"""First-contact resolution (FCR) from a sample of closed Pylon tickets.

Pylon has no bulk touch count, so each run pulls a few pages of closed tickets with their message
history and this script counts agent replies.

Usage:
  python3 fcr_sample.py plan  --run-date YYYY-MM-DD --scratch <dir>
      Prints the Pylon search_issues calls to make (one per sampled day). Make each call exactly as
      printed; the result is large and is saved to a tool-results file: copy that file (never retype
      it) to the printed name, fcr_page_<k>_<MMDD>.json.
  python3 fcr_sample.py build --run-date YYYY-MM-DD --scratch <dir>
      Reads the pages, writes fcr_<MMDD>.json for build_record.py. Exits 1 if a page is missing or
      a page is not the call that was planned.

Rules (config.fcr and the shared SQL, so the sample matches the Sigma numbers):
  - pet tickets excluded with the same rule as shared/sql/pet_ticket.sql; spam excluded (category
    'spam' or a tag in config.fcr.exclude_tags)
  - agent reply = public message from a Findigs user (from_customer false, author_type not
    'system', is_private false)
  - tickets with no agent reply at all (closed without an answer) are left out of the rate
  - FCR = share of the rest answered in <= config.fcr.max_agent_replies agent replies
  - segment = the shared requester-type rule (shared/sql/support_segment.sql), parsed from that file
  - d7 = days inside the last 7; d30 = all sampled days, each day weighted equally
"""
import datetime as dt, json, os, re, sys
import sm_common

PLAN_KEYS = ("created_after", "created_before")


def sample_days(run):
    f = run.cfg["fcr"]
    out = []
    for k, ago in enumerate(f["sample_days_ago"]):
        start = dt.datetime.combine(run.date - dt.timedelta(days=ago), dt.time(f["start_hour_utc"]))
        out.append({"k": k, "days_ago": ago, "in_d7": ago <= 7,
                    "call": {"states": ["closed"], "created_after": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "created_before": (start + dt.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "limit": f["page_size"], "sort_by": "created_at", "sort_order": "asc",
                             "include_messages": True, "max_message_chars": 1, "include_total": True},
                    "file": f"fcr_page_{k}_{run.mmdd}.json"})
    return out


def shared_sql(name):
    return open(os.path.join(sm_common.REPO_ROOT, "shared", "sql", name), encoding="utf-8").read()


def segment_rule():
    """Parse support_segment.sql into [(segment, like_patterns, exact_values)]."""
    sql = shared_sql("support_segment.sql")
    rules = []
    for body, seg in re.findall(r"WHEN (.+?) THEN '(\w+)'", sql):
        if "IS NULL" in body:
            continue
        likes = [p.replace("%", ".*") for p in re.findall(r"LIKE '([^']+)'", body)]
        exact = re.findall(r"'([^']+)'", " ".join(re.findall(r"IN \(([^)]*)\)", body)))
        rules.append((seg, [re.compile("^" + p + "$") for p in likes], set(exact)))
    if [r[0] for r in rules] != ["property_manager", "applicant"]:
        sys.exit("STOP: support_segment.sql no longer has the expected shape; update fcr_sample.py")
    return rules


def segment(value, rules):
    if value is None:
        return "unset"
    v = value.strip().lower()
    for seg, likes, exact in rules:
        if v in exact or any(p.match(v) for p in likes):
            return seg
    return "other"


def pet_rule():
    sql = shared_sql("pet_ticket.sql")
    subs = set(re.findall(r"'([^']+)'", re.search(r"CASE_SUB_CATEGORY\" IN \(([^)]*)\)", sql).group(1)))
    cat = re.search(r"CASE_CATEGORY\" = '([^']+)'", sql).group(1)
    word = re.search(r"ILIKE '%([^%']+)%'", sql).group(1).lower()

    def is_pet(i):
        cf = i.get("custom_fields") or {}
        sub = (cf.get("issue_sub_category") or {}).get("value") or None
        c = (cf.get("issue_category") or {}).get("value") or None
        return sub in subs or (c == cat and sub is None) or word in (i.get("title") or "").lower()
    return is_pet


def build(run):
    f = run.cfg["fcr"]
    rules, is_pet = segment_rule(), pet_rule()
    excl_tags = {t.lower() for t in f["exclude_tags"]}
    spam = run.cfg["spam_category"]
    days, seg_tot = [], {}
    for s in sample_days(run):
        p = run.path(s["file"])
        if not os.path.exists(p):
            sys.exit(f"STOP: missing {s['file']} (make the planned call and copy its result file)")
        d = json.load(open(p, encoding="utf-8"))
        iss = d["issues"]
        lo, hi = s["call"]["created_after"], s["call"]["created_before"]
        bad = [i["number"] for i in iss if not (lo <= i["created_at"] < hi) or i.get("state") != "closed"]
        if bad or not iss:
            sys.exit(f"STOP: {s['file']} is not the planned call (window {lo} to {hi}, closed): {bad[:5] or 'empty'}")
        n = fcr_n = no_reply = excluded = 0
        for i in iss:
            cf = i.get("custom_fields") or {}
            if is_pet(i) or (cf.get("issue_category") or {}).get("value") == spam or \
                    excl_tags & {t.strip().lower() for t in i.get("tags") or []}:
                excluded += 1
                continue
            if i.get("messages_truncated"):
                sys.exit(f"STOP: {s['file']} has truncated message history (do not set max_messages_per_issue)")
            replies = sum(1 for m in i.get("messages") or []
                          if not m["from_customer"] and m.get("author_type") != "system" and not m["is_private"])
            if replies == 0:
                no_reply += 1
                continue
            ok = replies <= f["max_agent_replies"]
            n += 1; fcr_n += ok
            sg = seg_tot.setdefault(segment((cf.get("user_type") or {}).get("value"), rules), [0, 0])
            sg[0] += 1; sg[1] += ok
        days.append({**{k: s[k] for k in ("k", "days_ago", "in_d7")}, "window": [lo, hi], "pulled": len(iss),
                     "closed_that_day": d.get("total"), "excluded_pet_or_spam": excluded,
                     "no_agent_reply": no_reply, "closed_n": n, "fcr_n": fcr_n,
                     "rate": fcr_n / n if n else None})

    def pooled(ds):
        rated = [x for x in ds if x["closed_n"]]
        if not rated:
            return {"closed_n": 0, "fcr_n": 0}
        rate = sum(x["rate"] for x in rated) / len(rated)  # each sampled day weighted equally
        n = sum(x["closed_n"] for x in rated)
        return {"closed_n": n, "fcr_n": round(rate * n)}
    d7, d30 = pooled([x for x in days if x["in_d7"]]), pooled(days)
    out = {"d7": d7, "d30": d30,
           "by_segment": {s: {"closed_n": seg_tot.get(s, [0, 0])[0], "fcr_n": seg_tot.get(s, [0, 0])[1]}
                          for s in run.cfg["segments"]["reported"]},
           "days": days,
           "note": (f"Scripted sample of closed Pylon tickets, refreshed {run.iso}: {len(days)} sampled days "
                    f"({', '.join(str(x['days_ago']) for x in days)} days before the run), up to {f['page_size']} "
                    f"tickets each from {f['start_hour_utc']:02d}:00 UTC, {d30['closed_n']} tickets rated. FCR = "
                    f"share answered in {f['max_agent_replies']} or fewer public agent replies (Emma's 2026-09-22 "
                    "definition); pet and spam excluded; tickets closed with no agent reply are left out. d7 uses "
                    "the sampled days inside the last 7; each day counts equally.")}
    json.dump(out, open(run.path(f"fcr_{run.mmdd}.json"), "w", encoding="utf-8"), indent=1)
    for x in days:
        print(f"day -{x['days_ago']}: pulled {x['pulled']} of {x['closed_that_day']} closed, excluded {x['excluded_pet_or_spam']}, "
              f"no reply {x['no_agent_reply']}, rated {x['closed_n']}, FCR {x['fcr_n']}")
    print("d7", d7, "d30", d30, "by_segment", out["by_segment"])


if __name__ == "__main__":
    run, ns = sm_common.get_run("FCR sample", [(("mode",), {"choices": ["plan", "build"]})])
    if ns.mode == "plan":
        for s in sample_days(run):
            print(f"{s['file']}: search_issues {json.dumps(s['call'])}")
    else:
        build(run)
