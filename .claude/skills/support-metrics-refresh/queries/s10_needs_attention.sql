SELECT
  CAST(CAST("inode-1dBuhhkgQkWXslu27HE64N/CASE_NUMBER" AS INTEGER) AS VARCHAR) AS ticket_number,
  "inode-1dBuhhkgQkWXslu27HE64N/CASE_SUBJECT" AS subject,
  COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", 'uncategorized') AS category,
  LOWER("inode-1dBuhhkgQkWXslu27HE64N/CASE_PRIORITY") AS priority,
  "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" AS status,
  "inode-1dBuhhkgQkWXslu27HE64N/CASE_OWNER" AS agent,
  "inode-1dBuhhkgQkWXslu27HE64N/ROLLUP_COMPANY_NAME" AS account_name,
  CAST("inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" AS VARCHAR) AS created_at,
  "aXcJxyR08B" AS is_tes,
  {segment} AS segment
FROM "datamodel"."Gz0-jqrI1V"
WHERE {pylon_base}
  AND "inode-1dBuhhkgQkWXslu27HE64N/CASE_STATUS" IN ({na_statuses})
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d90_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
  AND NOT ({pet_ticket})
  AND COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY", '') <> 'spam'
  AND ({segment}) IN ('property_manager', 'applicant')
ORDER BY "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" ASC
LIMIT {na_limit}
