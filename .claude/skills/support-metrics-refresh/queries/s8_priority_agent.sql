SELECT
  COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_OWNER", 'Unassigned') AS agent,
  COALESCE(LOWER("inode-1dBuhhkgQkWXslu27HE64N/CASE_PRIORITY"), 'none') AS priority,
  {segment} AS segment,
  COUNT(*) AS n,
  COUNT(CASE WHEN "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" <> 'Closed' THEN 1 END) AS open_n,
  SUM("inode-1dBuhhkgQkWXslu27HE64N/TICKET_RESOLUTION_HOURS") AS res_hours_sum,
  COUNT("inode-1dBuhhkgQkWXslu27HE64N/TICKET_RESOLUTION_HOURS") AS res_n
FROM "datamodel"."Gz0-jqrI1V"
WHERE {pylon_base}
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
  AND NOT ({pet_ticket})
GROUP BY 1, 2, 3
