WITH base AS (
  SELECT
    COALESCE(LOWER("inode-1dBuhhkgQkWXslu27HE64N/CASE_PRIORITY"), 'none') AS priority,
    {segment} AS segment,
    CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" <> 'Closed' THEN 1 ELSE 0 END AS is_open
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
)
SELECT 'all' AS view, priority AS priority, COUNT(*) AS n, SUM(is_open) AS open_n FROM base GROUP BY priority
UNION ALL
SELECT segment AS view, priority AS priority, COUNT(*) AS n, SUM(is_open) AS open_n FROM base WHERE segment IN ('property_manager', 'applicant') GROUP BY segment, priority
