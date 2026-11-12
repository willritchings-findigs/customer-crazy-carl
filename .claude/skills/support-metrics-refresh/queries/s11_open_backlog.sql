WITH base AS (
  SELECT
    "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" AS status,
    CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' THEN 'a_0_30d' WHEN "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d90_start}' THEN 'b_30_90d' ELSE 'c_over_90d' END AS age_band,
    {segment} AS segment,
    CASE WHEN "aXcJxyR08B" THEN 1 ELSE 0 END AS tes
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" NOT IN ('Closed', 'TEST')
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND NOT ({pet_ticket})
    AND COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", '') <> 'spam'
)
SELECT
  status AS status,
  age_band AS age_band,
  segment AS segment,
  COUNT(*) AS n,
  SUM(tes) AS n_tes
FROM base
GROUP BY status, age_band, segment
