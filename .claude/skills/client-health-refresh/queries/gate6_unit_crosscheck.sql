SELECT
  "inode-2XlQwTlI1rVsFvZQ8sG6SG/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(*) AS n_children,
  SUM("inode-2XlQwTlI1rVsFvZQ8sG6SG/UNIT_COUNT") AS sum_units_cur_month
FROM "datamodel"."Y4dN5LDwns"
WHERE "inode-2XlQwTlI1rVsFvZQ8sG6SG/UNIT_COUNT_AT" >= '{month_start}'
  AND "inode-2XlQwTlI1rVsFvZQ8sG6SG/UNIT_COUNT_AT" < '{next_month_start}'
  AND "inode-2XlQwTlI1rVsFvZQ8sG6SG/ROLLUP_COMPANY_NAME" IS NOT NULL
GROUP BY rollup_name
