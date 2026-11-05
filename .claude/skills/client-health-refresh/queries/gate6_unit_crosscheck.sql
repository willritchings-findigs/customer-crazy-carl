SELECT
  "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(*) AS n_children,
  SUM("6pSljhsuv9") AS sum_units_cur_month,
  SUM("fYbMjAl9NA") AS sum_units_latest
FROM "datamodel"."VWI1PYJyy-"
WHERE "inode-5OpIcdVfNb9CgO6UIt6Cbk/ROLLUP_COMPANY_NAME" IS NOT NULL
GROUP BY rollup_name
