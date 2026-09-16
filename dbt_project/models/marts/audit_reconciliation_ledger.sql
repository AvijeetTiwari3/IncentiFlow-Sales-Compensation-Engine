WITH deals AS (
    SELECT deal_id, booking_amount 
    FROM {{ ref('stg_crm__deals') }}
    WHERE stage = 'Closed Won'
),
splits AS (
    SELECT deal_id, SUM(attributed_booking) AS total_split_booking, SUM(split_percentage) AS total_split_pct
    FROM {{ ref('int_deal_credit_splits') }}
    GROUP BY deal_id
)
SELECT 
    d.deal_id,
    d.booking_amount AS gross_deal_amount,
    s.total_split_booking AS credited_split_amount,
    (d.booking_amount - s.total_split_booking) AS variance_leakage_amount,
    CASE 
        WHEN ABS(d.booking_amount - s.total_split_booking) < 0.01 THEN 'BALANCED_ZERO_LEAKAGE'
        ELSE 'IMBALANCE_DETECTED'
    END AS reconciliation_status
FROM deals d
JOIN splits s ON d.deal_id = s.deal_id
