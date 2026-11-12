# Support Metrics weekly refresh: why, decisions, incident log

Skill: `.claude/skills/support-metrics-refresh/` (procedure in `SKILL.md`, logic in `config.json`,
`queries/`, `scripts/`, shared SQL rules in `shared/sql/`). Dashboard:
https://findigs-growth-hub.base44.app/cx/support-metrics, record `SupportCache / support_overview`.
Owner: Will Ritchings. Taken over from Emma Kyber's handoff.

## What the run does

1. Sigma: 14 queries over Support Cases BI (Pylon rows) and the User Application Funnel, each
   result proven against Sigma with the shared fingerprint check (`sigma_verify.py`).
2. Pylon: six sampled days of closed tickets with message history, for FCR.
3. `build_record.py` maps everything onto the existing SupportCache schema (no new fields: Base44
   drops unknown ones) and refuses to write if any view fails to reconcile to the headline.
4. PUT the managed fields, GET them back, diff value for value.

## Decisions (2026-11-12, Will)

| Topic | Decision |
|---|---|
| Needs Attention | Open tickets "waiting on Findigs" (New, Waiting on You, On Engineering, On Customer Success Team) created in the last 90 days, oldest first, 50 rows. Older ones are reported as a stale count, not listed. |
| Needs Attention requesters | Property managers and applicants only. Tickets with no requester type were mostly automated or internal email. |
| Spam | Excluded from every figure except the By Category list (where it is its own row). The headline therefore equals the sum of By Channel, priority, agent and segment views. |
| FCR, SLA, tickets per 100 apps | Rebuilt now rather than carried forward. |
| SLA | "Honest version": pet and spam excluded; a ticket with no first response counts as a miss. |
| Success post | `#gtm-automation-log` (`C0CJ1P9D0HE`). Failures DM Will. |

## Method notes

- **Windows.** `[run date - N days, run date)`: the run date's partial day is excluded. Trend
  weeks are trailing 7-day blocks ending the day before the run (so a Monday run gives
  Monday-start weeks). Week index uses `FLOOR((DATE_DIFF('day', ts, anchor) - 1) / 7)` because
  Sigma's DATE_DIFF counts day boundaries.
- **Pet rule** (`shared/sql/pet_ticket.sql`) and **segment rule** (`shared/sql/support_segment.sql`)
  are shared with Client Health. `fcr_sample.py` parses both files so the Pylon sample uses the
  same rules.
- **Segment rule** restores Emma's pattern match (lost on 10/29): property_manager includes
  Landlord / Portfolio Admin variants and typos; applicant includes Guarantor and typos; NULL =
  unset; anything else = other (stop if over 1% of d30).
- **FCR** (Emma, 2026-09-22): closed tickets answered in 2 or fewer agent replies. Agent reply =
  public message from a Findigs user. Tickets closed with no agent reply are left out of the rate
  (they were never answered). Six days sampled (2, 5, 10, 16, 22, 28 days back), up to 100
  tickets each from 13:00 UTC; d7 = days 2 and 5; each day weighted equally. Applicant chat
  tickets often get several short agent messages in a row, which counts as several replies:
  applicant FCR runs much lower than PM FCR for that reason.
- **Tickets per 100 applicants** = pet- and spam-excluded tickets / people whose first funnel
  event falls in the same window, x100. Reproduced the 9/28 value to within a point.
- **Friction themes** keyword rules were lost with the original build and were rebuilt under the
  9/24 theme names (`config.friction_themes`). They include pet tickets on purpose (the pets
  panel is about pet verification).
- **Sigma alias quirk.** A first-column alias that renames a column (`cat AS category`, or a
  plain column with GROUP BY 1) sometimes comes back under the source name. Every query that hit
  it now selects from a CTE with the final name. The run stops rather than renaming by hand.

## First automated run, 2026-11-12 (dry run)

All 14 Sigma results fingerprint-verified, all build gates passed. Against the 10/29 record:
tickets 30d 16,143 -> 15,325 (spam now excluded: 390), SLA 30d 83.1 -> 85.3 (new method),
FCR 30d 15.8 -> 14.5 and 7d 16.9 -> 8.2 (new scripted sample), applicant CSAT 3.41 -> 3.64,
tickets per 100 applicants 27.7 -> 25.7. Needs Attention: 50 listed of 179 waiting, 79 stale.

Open points for Will:
- Email SLA 7d reads 76.5% (was 95.9%) because unset-requester email (automated and internal
  mail) mostly never gets a first response and now counts as a miss. PM and applicant SLA are
  87.8% and 89.8%. Option: exclude unset requesters from the SLA, as Needs Attention does.
- The By Channel caption on the page says spam is included; the builder prompt to fix the
  caption is still to be written (display change, Base44 builder, Will runs it).

## Incident log

- 2026-11-12: the 10/29 values had been hand-typed into a push script; queries recovered from
  the transcript and rebuilt here. Needs Attention was a frozen June-July snapshot; replaced.
