WITH payouts AS (
    SELECT * FROM {{ ref('fct_commission_payouts') }}
)
SELECT 
    rep_id,
    rep_name,
    territory,
    quarterly_quota,
    COUNT(DISTINCT deal_id) AS total_deals_won,
    SUM(attributed_booking) AS total_attributed_bookings,
    ROUND((SUM(attributed_booking) / quarterly_quota) * 100, 2) AS final_quota_attainment_pct,
    SUM(gross_commission) AS total_gross_commission,
    SUM(clawback_deduction) AS total_clawbacks,
    SUM(net_commission_payout) AS total_net_payout
FROM payouts
GROUP BY rep_id, rep_name, territory, quarterly_quota
ORDER BY total_attributed_bookings DESC
