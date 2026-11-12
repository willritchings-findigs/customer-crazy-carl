SELECT
  COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", 'uncategorized') AS category,
  COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_ORIGIN", 'unknown') AS channel,
  COUNT(*) AS n_d30,
  COUNT(CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d7_start}' THEN 1 END) AS n_d7
FROM "datamodel"."Gz0-jqrI1V"
WHERE {pylon_base}
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
  AND NOT ({pet_ticket})
GROUP BY 1, 2
