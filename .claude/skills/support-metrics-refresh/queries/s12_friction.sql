SELECT
  "inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY" AS category,
  ({friction_case}) AS theme,
  COUNT(*) AS n_d30
FROM "datamodel"."Gz0-jqrI1V"
WHERE {pylon_base}
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
  AND "inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY" IN ({friction_categories})
GROUP BY 1, 2
