SELECT
  LOWER(TRIM("EqUUI_mZyt")) AS user_type,
  COUNT(*) AS n_d30
FROM "datamodel"."Gz0-jqrI1V"
WHERE {pylon_base}
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
  AND NOT ({pet_ticket})
  AND ({segment}) = 'other'
GROUP BY 1
