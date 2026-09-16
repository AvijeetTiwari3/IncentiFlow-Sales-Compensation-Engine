WITH splits AS (
    SELECT * FROM {{ ref('int_deal_credit_splits') }}
)
SELECT 
    *,
    SUM(attributed_booking) OVER (
        PARTITION BY rep_id 
        ORDER BY close_date ASC, split_id ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_ptd_booking,
    (SUM(attributed_booking) OVER (
        PARTITION BY rep_id 
        ORDER BY close_date ASC, split_id ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) / quarterly_quota) AS current_attainment_pct
FROM splits
