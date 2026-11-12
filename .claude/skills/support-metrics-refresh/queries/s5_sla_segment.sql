WITH base AS (
  SELECT
    "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" AS created_at,
    {segment} AS segment,
    COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_ORIGIN", 'unknown') AS channel,
    CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/TICKET_TIME_TO_ASSIGNED_HOURS" <= ({sla_target_hours}) THEN 1 ELSE 0 END AS hit
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
    AND COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", '') <> 'spam'
)
SELECT
  segment AS segment,
  channel AS channel,
  COUNT(*) AS n_d30,
  SUM(hit) AS hit_d30,
  COUNT(CASE WHEN created_at >= '{d7_start}' THEN 1 END) AS n_d7,
  SUM(CASE WHEN created_at >= '{d7_start}' THEN hit ELSE 0 END) AS hit_d7
FROM base
GROUP BY segment, channel
