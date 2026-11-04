# Base44 builder prompts — Client Health page

Paste into the Base44 AI builder for the growth-hub app (findigs-growth-hub.base44.app).
Page lives at `/cx/client-health`, backed by `AccountHealthCache` (cache_key
`health_overview`). No data/schema change needed for this one — it's a pure
page-behavior fix.

## Gap from the 2026-09-22 churn/health call: Red tile doesn't drill down

Emma's ask: "the number of accounts at risk should be all red, and then an
option to click down, which is all the reds across all the segments." The
Aggregate tab already shows the right overall count (130/108/20/1/8 as of
9/21) but the tiles aren't clickable — confirmed by testing directly, nothing
happens on click.

```
On the Client Health page's Aggregate tab, make each of the 5 band tiles
(Green accounts, Yellow accounts, Red accounts, Unscored accounts, Churned
accounts — not the "Accounts total" tile) clickable.

Clicking a tile should: switch to the Rating Detail tab, ensure it's in "By
Rating" view mode (not "Flat"), expand that band's group (e.g. clicking "Red
accounts" expands the "Red — N accounts" group), collapse every other band's
group, and scroll the expanded group into view. This should feel like the
tile is a shortcut into the exact same grouped list Rating Detail already
renders, not a new view.

Give the 5 tiles a hover state (cursor pointer, subtle highlight) so it's
clear they're clickable now.
```

Once published, tell Donna — she'll verify by clicking each tile directly in
the browser before calling it done.

## Gap from the same call: dollars-vs-counts toggle on the WoW Movement matrix

Emma floated this as a "maybe" — lower priority than the drill-down above.
**Not ready to prompt for yet**: `AccountHealthCache` doesn't carry an ACV
figure per account anywhere in the payload (checked `merge_refresh.py` and
`enrich_payload.py` directly — no ACV/amount field exists in the accounts
array, only unit counts and the portfolio-level quarterly revenue rollup).
Adding a per-account $ weighting means a real HubSpot ACV pull + join into
the weekly refresh first, similar to what Churn Analysis and Implementations
already do — not a page-only fix. Flagged to Emma, waiting on a priority call
before building the data side.

## Bug: "Unscored accounts" tile drills into the wrong band (2026-09-24 full-page review)

Confirmed reproducible twice, from a fresh Aggregate-tab load each time:
clicking the "Unscored accounts" tile correctly switches to Rating Detail, but
expands the "Red" group instead of "Unscored". The other four tiles (Green,
Yellow, Red, Churned) all expand their own correct group — this looks like an
isolated mix-up in just the Unscored tile's click handler.

```
On the Client Health page's Aggregate tab, fix the "Unscored accounts" tile.
Clicking it currently switches to Rating Detail and expands the "Red" group --
it should expand the "Unscored" group instead: same "By Rating" view mode,
collapse every other band's group, scroll the expanded "Unscored" group into
view. This should match exactly how the Green/Yellow/Red/Churned tiles already
correctly drill into their own bands. Don't change the behavior of those other
four tiles -- only Unscored is wrong.
```

Once published, tell Donna — she'll re-verify by clicking the Unscored tile
directly in the browser (and re-clicking Red/Yellow/Green/Churned too, to make
sure the fix didn't disturb the ones that already work) before calling it done.
