SELECT
  "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" AS rollup_name,
  BOOL_OR("inode-5OpIcdVfNb9CgO6UIt6Cbk/IS_DECISION_ASSIST_ENABLED") AS is_da,
  SUM("fYbMjAl9NA") AS units_latest,
  SUM("6pSljhsuv9") AS units_cur_month,
  STRING_AGG(DISTINCT "inode-5OpIcdVfNb9CgO6UIt6Cbk/SALES_ACCOUNT_STATUS", ', ') AS statuses,
  STRING_AGG(DISTINCT "raG5zMHzeS", ', ') AS churn_risk,
  BOOL_OR("inode-5OpIcdVfNb9CgO6UIt6Cbk/IS_COMPANY_CHURNED") AS any_churned
FROM "datamodel"."VWI1PYJyy-"
WHERE "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" IS NOT NULL
GROUP BY rollup_name
