SELECT
  "inode-54xB1eUhLxf1EJucb7r8Xk/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(*) AS funnel_total,
  SUM("inode-54xB1eUhLxf1EJucb7r8Xk/HIT_SUBMIT") AS submits
FROM "datamodel"."apKoPbqWa9"
WHERE "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" >= '{window_start}'
  AND "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" <= '{window_end}'
GROUP BY rollup_name
