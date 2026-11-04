# Base44 builder prompt — fix Units Live mismatch between Rating Detail and the account popout (2026-09-29)

Paste this into the Findigs Hub AI builder. This is a display/binding fix only — no data is
wrong, two different fields are just both labeled "units live" in different places.

---

On the Client Health page's **Rating Detail** tab, the account list's "Units Live" column
(and the "Flat (Units Live ↓)" sort, and each band's summary line like "106 accounts, 175,584
units live") currently reads from the account field `unit_count_live_latest`.

The account detail popout's "Units Sold vs. Live" line reads from a different field,
`unit_count_live_current_month`, for the live-units half of that ratio.

These are two distinct, both-correct Sigma metrics (latest reported month vs. current
month), but showing them under the same "Units Live" label in two places on the same page
makes them look like a data error when someone compares the list to the popout for the same
account.

**Fix**: change the Rating Detail tab's "Units Live" column, its sort key, and every band-level
"units live" total on that tab to read from `unit_count_live_current_month` instead of
`unit_count_live_latest`, so it matches what the popout already shows. Do not change the
popout (it's already correct) or the Segment Detail tab (that one shows a "volume" metric,
unrelated to units live, and isn't affected by this).
