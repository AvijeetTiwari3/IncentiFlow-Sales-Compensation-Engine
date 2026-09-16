WITH source AS (
    SELECT * FROM raw_deals
)
SELECT 
    deal_id,
    deal_name,
    account_name,
    deal_type,
    CAST(booking_amount AS DECIMAL(14, 2)) AS booking_amount,
    stage,
    CAST(close_date AS DATE) AS close_date,
    currency
FROM source
