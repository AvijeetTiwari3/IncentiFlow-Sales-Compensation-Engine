WITH calculated AS (
    SELECT * FROM {{ ref('int_applied_accelerator_rates') }}
),
adjustments AS (
    SELECT * FROM {{ ref('stg_billing__adjustments') }}
)
SELECT 
    c.split_id AS payout_id,
    c.deal_id,
    c.rep_id,
    c.rep_name,
    c.territory,
    c.close_date,
    c.full_deal_amount,
    c.split_percentage,
    c.attributed_booking,
    c.quarterly_quota,
    c.cumulative_ptd_booking,
    c.current_attainment_pct,
    c.applied_tier,
    c.tier_multiplier,
    c.effective_rate,
    CAST(ROUND(c.attributed_booking * c.effective_rate, 2) AS DECIMAL(14, 2)) AS gross_commission,
    CASE 
        WHEN a.adjustment_id IS NOT NULL THEN CAST(ROUND(c.attributed_booking * c.effective_rate * -1.0, 2) AS DECIMAL(14, 2))
        ELSE CAST(0.0 AS DECIMAL(14, 2))
    END AS clawback_deduction,
    CASE 
        WHEN a.adjustment_id IS NOT NULL THEN 'CLAWBACK_APPLIED'
        ELSE 'STANDARD_PAYOUT'
    END AS payout_status,
    CAST(ROUND(
        (c.attributed_booking * c.effective_rate) + 
        (CASE WHEN a.adjustment_id IS NOT NULL THEN (c.attributed_booking * c.effective_rate * -1.0) ELSE 0.0 END), 2
    ) AS DECIMAL(14, 2)) AS net_commission_payout
FROM calculated c
LEFT JOIN adjustments a ON c.deal_id = a.deal_id
