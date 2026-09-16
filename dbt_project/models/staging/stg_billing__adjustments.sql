WITH source AS (
    SELECT * FROM raw_adjustments
)
SELECT 
    adjustment_id,
    deal_id,
    adjustment_type,
    CAST(adjustment_amount AS DECIMAL(14, 2)) AS adjustment_amount,
    reason,
    CAST(adjustment_date AS DATE) AS adjustment_date
FROM source
