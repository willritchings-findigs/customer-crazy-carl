SELECT
  "inode-1dBuhhkgQkWXslu27HE64N/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(*) AS pm_cases,
  COUNT(CASE WHEN "aXcJxyR08B" THEN 1 END) AS tes_cases
FROM "datamodel"."Gz0-jqrI1V"
WHERE "inode-1dBuhhkgQkWXslu27HE64N/CASE_IS_DELETED" = FALSE
  AND "dyE5lEXjiZ" = 'pylon'
  AND "EqUUI_mZyt" IS NOT NULL
  AND "EqUUI_mZyt" NOT ILIKE '%applic%'
  AND "EqUUI_mZyt" NOT ILIKE '%guarant%'
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{window_start}'
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" <= '{window_end}'
  AND NOT ({pet_ticket})
GROUP BY rollup_name
