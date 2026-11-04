# Client Health Weekly Refresh — 2026-09-21

**Pushed live 14:18 UTC** (overview PUT + GET verified; weekly snapshot record `health_snapshot_2026-09-21` created; history archived). Window: 2026-06-23 → 2026-09-21, prior window 2026-03-25 → 2026-06-23.

## Band distribution

| Band | 9/14 | 9/21 | Δ |
|------|------|------|---|
| Green | 132 | 130 | −2 |
| Yellow | 107 | 108 | +1 |
| Red | 19 | 20 | +1 |
| Churned | 8 | 8 | — |
| Unscored | 1 | 1 | — (PF Holdings, parked rollup) |

267 accounts. 3 composite flips, all **data-driven** (zero methodology changes this week). 0 CSM flag changes, 0 new churn flags. Freshness: platform metrics 249 touched, sentiment 125, Pylon 122/122 DA accounts fresh, units switched 227 / carried 16, 32 carry-forward notes (mostly no-HubSpot-match units).

## Flips

**🔴 Beztak Properties Parent — Yellow → Red.** Platform Red (45.6): TTD worsened to 144.6h, QA 19%, ticket ratio red. Sentiment Red (0.0): Slack Negative — leadership escalations over decisioning errors — and Pylon Negative with 136 open issues, 7 verified frictions (incl. an URGENT property-down escalation). Strategic still Green (81.8).

**🟡 Hudson Homes Management LLC — Green → Yellow.** Pylon slipped Positive → Neutral, which broke unanimous-green; Sentiment banded Yellow (50). Platform is fine (Green 92, TTD healthy) — this is a sentiment-only wobble.

**🟡 White Property Management – Ridgewood Apartments — Green → Yellow.** Platform Yellow (75.4): declined-side TTD blew out to 297.4h (red row), ticket ratio yellow. Sentiment and Strategic both Green.

## Verification log (verify-every-Negative rule)

- **Pylon**: 12 agent-reported Negatives → **11 confirmed** by direct re-pull (Beztak 136 open/7 frictions; Brick & Timber 24/5; Evernest 23/7; Harbor Group 43/3; Highmark 93/13; Kairos 66/21; Maymont 37/5; McKinley 62/12; Sentral 68/7; Standard Management 24/6; Western Wealth 26/3 — a genuine new flip, all September incidents), **1 overturned** (Imagine → Neutral: only the two "Decision Assist Processing Delays" tickets are real friction; the criminal-BG ticket was an individual applicant case).
- **New standing rule (Emma, 9/21): Pet Verification / pet-screening tickets don't count as PM friction** and never appear in alert cards (tags "Pets Inbound"/"Pets General", pet SOP/ESA/PetV titles). Applied to Highmark (14→13 frictions); written into the skill.
- **Willowdale (WPM)**: agent "not found" was a shortname search miss — full-name search returned exactly one Pylon account; 1 open issue is coordination, not friction → Positive, fresh.
- **Slack**: 123 accounts scanned, **zero overrides needed**. All 32 window flags were benign "no in-window activity" Neutrals (3 oldest spot-checked directly: Blue Oak, Niguel Point, Soniat — all empty in-window). Yancey Positive and Capital PM Positive both adjudicated correct.

## Pipeline fixes this run (now in the skill)

1. **Batch inputs must key by `resolved_name_sigma`**: 9/21 batches were keyed by input_name and 6 accounts' scan results silently failed to join (carried stale sentiment) — caught via suspiciously-quiet diff, fixed, re-merged.
2. **Sigma renamed 3 rollups** (Beztak, Kairos, Hudson) — their q-file joins silently missed until keys were translated; this was masking the Beztak flip. Detection + translation step added to the skill.
3. **`ts.txt` location bug**: archive wrote `computed_at: null` into wow_history + snapshot because ts.txt landed at project root; patched and record re-PUT with the correct timestamp.

## Client intel from the scans

- **Bridge Homes** — churn-by-acquisition: portfolio bought by a non-Findigs buyer, deactivated 9/18.
- **Harbor Group** — sentiment pillar worsened to Red inside its Yellow composite: offboarding signals, MRI integration dark.
- **Kairos** — "would opt out if given the option" re: Task Service on a Gong call; 21 verified open frictions.
- **McKinley** — platform is stellar (TTD 2.5h, submissions 4,985 vs 3,015) but 12 stuck-underwriting frictions keep Pylon Negative → Yellow composite.
- **Highmark** — pilot ramp is real: submissions 3,589 vs 293 prior (+1,125%), 6,348 decisions, Q3 revenue ≈ $284k.
- **Evernest** — still Red; Q3 revenue ≈ $101k, down from $182k in Q1; volume −28%.
- **Bryten** — client asked to pause (Slack Negative); TTD 352h on thin volume.
- **Metropolitan Holdings** — volume collapse (6 submissions vs 333 prior; Q3 revenue ≈ $78).
- **Willowdale** — Slack Negative with churn flavor: wants FullScreen, not the DA product they have.
- **Out Fast** — standing contradiction: FS composite Green 100 (flag-anchored) while Slack reads churned/negative and volume is −100%. Needs a truth-pick.
- Slack Negatives also on Modern City, Windsor, Legacy Invest, Cooper Zadeh, Equity, Elda.

## Not scored (asked 9/21): decrease in decisioned groups

The scored **volume row tracks submitted groups** (t90 vs p90, `GROUP_IS_SUBMITTED=true`; <20% drop G / 20–40 Y / >40 R). Decisioned-group counts are pulled (they're the denominator for approval/override/QA/ticket rows, kept as `n_decisioned_this_quarter`) but **no row scores a decisioning-count decline**. A "submissions steady, decisions stalling" account only trips TTD — and only for groups that DID get decided; groups parked undecided (the McKinley pattern) are invisible to both rows. Adding a decisioned-t90-vs-p90 row would be cheap (same Groups BI query shape as q2); thresholds would need Emma/Alex sign-off like the volume ones.

## Slack alerts

- The stale **9/14 batch was scrapped unposted** (Emma 9/21), ledger marked SCRAPPED.
- **9/21 batch built and held**: 1 header + 3 alert cards (Beztak Y→R, Hudson G→Y, White PM–Ridgewood G→Y) + still-Red digest (19 accounts). **0 kudos** — no improvement flips this week. No pet-ticket titles anywhere (verified). Ledger: `history/2026-09-21/alerts_2026-09-21.json`, all `posted: false` — **awaiting Emma's go**, then future weeks auto-post.
- Thomas McCarthy's Slack ID verified against his profile (thomas.mccarthy@findigs.com) — he's tagged on the Beztak card and is currently marked "Out sick".

## Addendum 2026-09-22: PM-only Pylon rule + deterministic re-audit

Per Emma: only property-manager-filed tickets feed Pylon sentiment (ticket `user_type` field: "property manager" | "applicant"). Verified: applicant tickets route to the internal catch-all "Applicant Account (DO NOT DELETE)", and pet-team traffic lives on internal "Pet Reviewer <> Support" — neither ever scanned; Kairos (0/69) and Highmark (0/93) had zero applicant-filed tickets on their accounts. Re-audited all 8 scanned accounts holding pet-tagged open tickets against their counted frictions: **zero counted frictions were pet tickets, zero classifications change — the 9/21 record, snapshot, and alert batch stand unchanged.** Field trap caught and documented: `is_pet_verification` is a portfolio *product* flag (true on every ticket from pet-enabled clients), not a ticket classifier — pet tickets are identified by category/sub-category/Pets tags/titles instead. Rules live in the skill and runbook; scan results carry a PM/applicant split from the 9/28 run on.

## Still with humans

- **PF Holdings**: the one unscored account — parked multi-entity rollup ("Churned, Green" flag from one dead 2023 child while the rest is live, 5,531 units sold). Needs a split-or-score call.
- **Out Fast**: Green-vs-churned contradiction (above).
- **6 ownerless accounts** in the alert map: Capital PM Parent, Ebner, FBM, MS Coast, TPG, Weiss.
- **RPM Rental Solutions**: HubSpot churn-record cleanup still open.
- **Volume thresholds**: Alex's replacement cuts still pending (current ones flagged too generous 9/2).
