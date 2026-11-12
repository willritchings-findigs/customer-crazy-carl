# Shared SQL fragments

Pasted into queries by `render_queries.py` through `config.sql_fragments` (`{name}` placeholders), so
every dashboard uses one definition. Change a fragment here, re-render, and re-verify every skill
that uses it: the pet filter has drifted between dashboards before.

| File | Meaning | Used by |
|---|---|---|
| `pet_ticket.sql` | TRUE when a Support Cases BI row is a pet-verification ticket. Every sub-condition is wrapped in `COALESCE(..., FALSE)`: a NULL sub-category must not silently drop ordinary tickets. | client-health-refresh (q3), support-metrics-refresh |
| `pylon_base.sql` | Pylon tickets that are not deleted, archived or test. | support-metrics-refresh |
| `support_segment.sql` | Ticket requester bucket from the free-text Case User Type: `property_manager` / `applicant` / `unset` / `other`. Emma's patterns (2026-09-24) plus known typos. | support-metrics-refresh |
