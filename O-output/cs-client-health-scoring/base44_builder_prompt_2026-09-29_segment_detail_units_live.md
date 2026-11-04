# Base44 builder prompt — fix Units Live on Segment Detail too (2026-09-29)

Paste this into the Findigs Hub AI builder. Follow-up to the earlier Rating Detail fix — the
same mismatch turned out to affect a second tab that was missed the first time.

---

The **Segment Detail** tab's account-level **"Units Live"** column currently reads from
`unit_count_live_latest`, in both of its views:
- the default "By Segment" grouped view (per-account rows under each segment/band group)
- the "Flat (Volume ↓)" view (the flat sortable table)

This is the same field the account detail popout and the Rating Detail tab used to read
before being fixed to `unit_count_live_current_month` — Segment Detail was believed to only
show a "volume" metric (unrelated, still correct, don't touch it) and was skipped by mistake.

**Fix**: change the "Units Live" column in both Segment Detail views to read from
`unit_count_live_current_month` instead of `unit_count_live_latest`, so it matches the
popout and Rating Detail. Don't change anything labeled "volume" (the group-header totals
like "3 accounts, 49,891 volume", or the "Flat (Volume ↓)" sort toggle/label) — that's a
different, already-correct metric (submitted groups), not units live. Don't change any other
tab or section.
