# Support Metrics weekly refresh: 2026-11-12 (DRY RUN, nothing pushed)

Record `support_overview` on SupportCache, computed 2026-11-12T17:15:30.000Z. Previous record computed 2026-10-29T21:13:17.000Z.

## Headline numbers

| Metric | Before | Now |
|---|---|---|
| Tickets, 30d | 16,143 | 15,325 |
| Tickets, 7d | 3,716 | 3,609 |
| Median first response, 30d (min) | 2.0 | 1.0 |
| SLA within target, 30d (%) | 83.1 | 85.3 |
| SLA within target, 7d (%) | 85.3 | 85.8 |
| FCR, 30d (%) | 15.8 | 14.5 |
| FCR, 7d (%) | 16.9 | 8.2 |
| PM CSAT, 30d | 4.41 | 4.49 |
| Applicant CSAT, 30d | 3.41 | 3.64 |
| Tickets per 100 applicants, 30d | 27.7 | 25.7 |
| Handled without escalation, 30d (%) | 99.17 | 99.23 |
| Median resolution, 30d (min) | 46.0 | 69.0 |
| Pet SLA within 24h, 30d (%) | 65.1 | 63.6 |

Method notes: pet and spam excluded from every figure except By Category; SLA counts a ticket with no first response as a miss; FCR is a scripted sample (see the FCR note on the record).

## Needs Attention

50 tickets listed (oldest first) of 179 property-manager and applicant tickets waiting on Findigs from the last 90 days; 79 more are older than 90 days (stale backlog, not listed).

## Open backlog by status (0-30d / 30-90d / over 90d)

- New: 108 / 85 / 31
- On Customer Success Team: 15 / 20 / 42
- On Engineering: 14 / 16 / 31
- On Hold: 50 / 30 / 51
- Waiting on Customer: 487 / 160 / 123
- Waiting on You: 95 / 68 / 41

## Gates

- ok   segments sum to headline (15325 / 3609)
- ok   category x channel minus spam (390 / 60) = headline
- ok   category x segment = category x channel
- ok   SLA base = headline
- ok   priority rows (all) = 15325
- ok   agent rows (all) = 15325
- ok   priority rows (property_manager) = 5243
- ok   agent rows (property_manager) = 5243
- ok   priority rows (applicant) = 8731
- ok   agent rows (applicant) = 8731
- ok   trend week 0 = d7 volume
- ok   funnel week 0 = d7 applicants
- ok   trend has weeks w0-w11
- ok   funnel has weeks w0-w11
- ok   no unlabelled categories 
- ok   no unknown channels 
- ok   unclassified requester types 0.05% <= 1.0% (values: agent 1, employer 2, other 3, pr 1)
- ok   d30 volume 15325 >= 5000
- ok   d30 volume vs live 16143: -5.1% (limit +/-40%)
- ok   FCR sample has d7 and d30 tickets
- ok   Needs Attention list 50 = min(179 waiting, 50)

Unclassified requester types (d30): agent 1, employer 2, other 3, pr 1.

