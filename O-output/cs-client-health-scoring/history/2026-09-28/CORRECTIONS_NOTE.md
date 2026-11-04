# 2026-09-28 run — corrected twice post-hoc, 2026-09-29

The files in this folder are the FINAL, corrected state of the 2026-09-28 run, not exactly
what was live at the original 14:27:18 UTC push. Two same-day-logical fixes were applied
after the fact, both on 2026-09-29, both re-verified against the live Base44 record with zero
new composite band flips beyond the 2 already known (Cooper Zadeh, Group Fox):

1. **Unit-count fix** (q4 Companies BI multi-portfolio undercount — 44/267 accounts affected,
   e.g. Beztak 1,361 -> 21,539). See `project_client_health_weekly_refresh.md` memory,
   addendum dated 2026-09-28, and `2026-09-28_weekly-refresh-report.md`'s own addendum.
2. **Pet-ticket exclusion + a SQL NULL-propagation bug fix** (q3 Support Cases BI — pet
   verification tickets were inflating `support_ticket_ratio_per_100`/`tes_pct`; the first
   attempt at excluding them had a NULL-handling bug that additionally, wrongly excluded
   ~1,200-2,600 ordinary non-pet tickets across the account base). See
   `project_cx_support_scorecard.md` and `project_client_health_weekly_refresh.md` memory,
   both dated 2026-09-29.

`new_record_0928_PRE_CORRECTIONS.json` is kept as the original, uncorrected snapshot for
reference. `new_record_0928.json`, `wow_diff_0928.json`, and `merge_refresh.py` in this folder
are now the corrected versions (matching what went live 2026-09-29 14:16:52 UTC).
`baseline_0928.json`, `hs_account_match.json`, `gong_strategic_rows.json`,
`pylon_overrides.json`, `slack_overrides.json`, and `alerts_2026-09-28.json` are unaffected by
either fix and were not touched.
