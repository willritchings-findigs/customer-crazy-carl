WITH base AS (
  SELECT
    COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_OWNER", 'Unassigned') AS agent,
    {segment} AS segment,
    CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" <> 'Closed' THEN 1 ELSE 0 END AS is_open,
    "inode-1dBuhhkgQkWXslu27HE64N/TICKET_RESOLUTION_HOURS" AS res_hours
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
),
agg AS (
  SELECT 'all' AS view, agent, COUNT(*) AS n, SUM(is_open) AS open_n, SUM(res_hours) AS res_sum, COUNT(res_hours) AS res_n FROM base GROUP BY agent
  UNION ALL
  SELECT segment AS view, agent, COUNT(*) AS n, SUM(is_open) AS open_n, SUM(res_hours) AS res_sum, COUNT(res_hours) AS res_n FROM base WHERE segment IN ('property_manager', 'applicant') GROUP BY segment, agent
),
ranked AS (
  SELECT view, agent, n, open_n, res_sum, res_n,
    ROW_NUMBER() OVER (PARTITION BY view ORDER BY CASE WHEN agent = 'Unassigned' THEN 1 ELSE 0 END, n DESC, agent) AS rk
  FROM agg
)
SELECT
  view AS view,
  CASE WHEN agent = 'Unassigned' OR rk <= {top_agents} THEN agent ELSE 'Other' END AS agent,
  SUM(n) AS n,
  SUM(open_n) AS open_n,
  SUM(res_sum) AS res_hours_sum,
  SUM(res_n) AS res_n
FROM ranked
GROUP BY 1, 2
