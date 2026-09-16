WITH source AS (
    SELECT * FROM raw_sales_reps
)
SELECT 
    rep_id,
    full_name AS rep_name,
    email,
    role AS rep_role,
    territory,
    CAST(annual_quota AS DECIMAL(14, 2)) AS annual_quota,
    CAST(quarterly_quota AS DECIMAL(14, 2)) AS quarterly_quota,
    is_active,
    CAST(hire_date AS DATE) AS hire_date
FROM source
