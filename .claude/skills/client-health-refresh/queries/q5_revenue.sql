SELECT
  "inode-01S9MnIuLWteAJ8QRq5wee/ROLLUP_COMPANY_NAME" AS rollup_name,
  DATE_PART('quarter', "inode-01S9MnIuLWteAJ8QRq5wee/REVENUE_AT") AS q,
  SUM("inode-01S9MnIuLWteAJ8QRq5wee/FINDIGS_REVENUE_AMOUNT") AS rev
FROM "datamodel"."VDO-u_D7p-"
WHERE DATE_PART('year', "inode-01S9MnIuLWteAJ8QRq5wee/REVENUE_AT") = {revenue_year}
GROUP BY rollup_name,
  q
