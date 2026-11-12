WITH base AS (
  SELECT
    "inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY" AS cat,
    LOWER(COALESCE("inode-1dBuhhkgQkWXslu27HE64N/CASE_SUBJECT", '')) AS subj
  FROM "datamodel"."Gz0-jqrI1V"
  WHERE {pylon_base}
    AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" >= '{d30_start}' AND "inode-1dBuhhkgQkWXslu27HE64N/CREATED_AT" < '{anchor}'
    AND "inode-1dBuhhkgQkWXslu27HE64N/CASE_CATEGORY" IN ({friction_categories})
),
themed AS (
  SELECT cat AS category, ({friction_case}) AS theme FROM base
)
SELECT
  category AS category,
  theme AS theme,
  COUNT(*) AS n_d30
FROM themed
GROUP BY category, theme
