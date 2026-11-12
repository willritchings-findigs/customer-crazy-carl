SELECT
  CASE WHEN "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" >= '{d7_start}' THEN 'd7' ELSE 'd30_only' END AS bucket,
  COUNT(*) AS applicants
FROM "datamodel"."apKoPbqWa9"
WHERE "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" >= '{d30_start}' AND "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" < '{anchor}'
GROUP BY 1
UNION ALL
SELECT
  CONCAT('w', CAST(FLOOR((DATE_DIFF('day', "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT", CAST('{anchor}' AS TIMESTAMP)) - 1) / 7) AS VARCHAR)) AS bucket,
  COUNT(*) AS applicants
FROM "datamodel"."apKoPbqWa9"
WHERE "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" >= '{trend_start}' AND "inode-54xB1eUhLxf1EJucb7r8Xk/FIRST_EVENT_AT" < '{anchor}'
GROUP BY 1
