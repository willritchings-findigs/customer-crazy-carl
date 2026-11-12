WITH base AS (
  SELECT
    FLOOR((DATE_DIFF('day', "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT", CAST('{anchor}' AS TIMESTAMP)) - 1) / 7) AS week_idx,
    "inode-1dBuhhkgQkWXslu27HE64N/TICKET_TIME_TO_ASSIGNED_HOURS" * 60.0 AS ttfr_min,
    "00TvMgGarP" AS csat,
    {segment} AS segment,
    CASE WHEN COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", '') <> 'spam' THEN 1 ELSE 0 END AS nonspam,
    CASE WHEN COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", '') <> 'spam' AND "inode-1dBuhhkgQkWXslu27HE64N/TICKET_TIME_TO_ASSIGNED_HOURS" <= ({sla_target_hours}) THEN 1 ELSE 0 END AS hit
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{trend_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
)
SELECT
  CONCAT('w', CAST(week_idx AS VARCHAR)) AS bucket,
  COUNT(*) AS ticket_volume,
  MEDIAN(ttfr_min) AS median_ttfr_min,
  SUM(nonspam) AS nonspam_n,
  SUM(hit) AS sla_hits,
  AVG(CASE WHEN segment = 'property_manager' THEN csat END) AS pm_csat,
  AVG(CASE WHEN segment = 'applicant' THEN csat END) AS applicant_csat
FROM base
GROUP BY week_idx
