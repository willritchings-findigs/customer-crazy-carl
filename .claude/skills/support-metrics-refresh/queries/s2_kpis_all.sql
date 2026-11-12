WITH base AS (
  SELECT
    "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" AS created_at,
    "inode-1dBuhhkgQkWXslu27HE64N/TICKET_TIME_TO_ASSIGNED_HOURS" * 60.0 AS ttfr_min,
    "inode-1dBuhhkgQkWXslu27HE64N/TICKET_RESOLUTION_HOURS" * 60.0 AS res_min,
    CASE WHEN "aXcJxyR08B" THEN 0.0 ELSE 100.0 END AS hwe_pct,
    "00TvMgGarP" AS csat
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
)
SELECT
  COUNT(*) AS n_d30,
  COUNT(CASE WHEN created_at >= '{d7_start}' THEN 1 END) AS n_d7,
  MEDIAN(ttfr_min) AS ttfr_med_d30,
  MEDIAN(CASE WHEN created_at >= '{d7_start}' THEN ttfr_min END) AS ttfr_med_d7,
  MEDIAN(res_min) AS res_med_d30,
  MEDIAN(CASE WHEN created_at >= '{d7_start}' THEN res_min END) AS res_med_d7,
  AVG(hwe_pct) AS hwe_d30,
  AVG(CASE WHEN created_at >= '{d7_start}' THEN hwe_pct END) AS hwe_d7,
  AVG(csat) AS csat_avg_d30,
  COUNT(csat) AS csat_n_d30,
  AVG(CASE WHEN created_at >= '{d7_start}' THEN csat END) AS csat_avg_d7,
  COUNT(CASE WHEN created_at >= '{d7_start}' THEN csat END) AS csat_n_d7
FROM base
