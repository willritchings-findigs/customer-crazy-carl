SELECT
  "inode-3t4SuoA2pU267qM43Rx4jl/ROLLUP_COMPANY_NAME" AS rollup_name,
  COUNT(CASE WHEN "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_IS_SUBMITTED" AND "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_SUBMITTED_AT" >= '{window_start}' AND "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_SUBMITTED_AT" <= '{window_end}' THEN 1 END) AS sub_t90,
  COUNT(CASE WHEN "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_IS_SUBMITTED" AND "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_SUBMITTED_AT" >= '{prior_start}' AND "inode-3t4SuoA2pU267qM43Rx4jl/GROUP_SUBMITTED_AT" <= '{prior_end}' THEN 1 END) AS sub_p90
FROM "datamodel"."xv3TuuWX8Z"
GROUP BY rollup_name
