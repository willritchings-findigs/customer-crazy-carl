SELECT
  "inode-1dBuhhkgQkWXslu27HE64N/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(*) AS pm_cases,
  COUNT(CASE WHEN "aXcJxyR08B" THEN 1 END) AS tes_cases
FROM "datamodel"."Gz0-jqrI1V"
WHERE "inode-1dBuhhkgQkWXslu27HE64N/CASE_IS_DELETED" = FALSE
  AND "EqUUI_mZyt" IS NOT NULL
  AND "EqUUI_mZyt" NOT ILIKE '%applic%'
  AND "EqUUI_mZyt" NOT ILIKE '%guarant%'
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{window_start}'
  AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" <= '{window_end}'
  AND NOT (COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_SUB_CATEGORY" IN ('pet_verification_dispute','pet_policy_question','pet_fee_refund_request'), FALSE) OR COALESCE(("inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY" = 'pets_disputes_consumer_requests' AND "inode-1dBuhhkgQkWXslu27HE64N/CASE_SUB_CATEGORY" IS NULL), FALSE) OR COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_SUBJECT" ILIKE '%pet%', FALSE))
GROUP BY rollup_name
