WITH deals AS (
    SELECT * FROM {{ ref('stg_crm__deals') }}
    WHERE stage = 'Closed Won'
),
splits AS (
    SELECT * FROM raw_deal_splits
),
reps AS (
    SELECT * FROM {{ ref('stg_hr__sales_reps') }}
)
SELECT 
    s.split_id,
    s.deal_id,
    s.rep_id,
    r.rep_name,
    r.rep_role,
    r.territory,
    r.quarterly_quota,
    d.deal_name,
    d.account_name,
    d.deal_type,
    d.booking_amount AS full_deal_amount,
    CAST(s.split_percentage AS DECIMAL(5, 2)) AS split_percentage,
    CAST(s.attributed_booking AS DECIMAL(14, 2)) AS attributed_booking,
    d.close_date
FROM splits s
JOIN deals d ON s.deal_id = d.deal_id
JOIN reps r ON s.rep_id = r.rep_id
