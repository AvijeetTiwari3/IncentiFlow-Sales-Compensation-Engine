WITH attainment AS (
    SELECT * FROM {{ ref('int_cumulative_quota_attainment') }}
)
SELECT 
    *,
    CASE 
        WHEN current_attainment_pct < 0.80 THEN 'Tier 1 (0% to 80% Quota)'
        WHEN current_attainment_pct >= 0.80 AND current_attainment_pct < 1.00 THEN 'Tier 2 (80% to 100% Target)'
        WHEN current_attainment_pct >= 1.00 AND current_attainment_pct < 1.50 THEN 'Tier 3 (100% to 150% Accelerator)'
        ELSE 'Tier 4 (150%+ President Club Super-Accelerator)'
    END AS applied_tier,
    CASE 
        WHEN current_attainment_pct < 0.80 THEN 1.00
        WHEN current_attainment_pct >= 0.80 AND current_attainment_pct < 1.00 THEN 1.25
        WHEN current_attainment_pct >= 1.00 AND current_attainment_pct < 1.50 THEN 2.00
        ELSE 2.50
    END AS tier_multiplier,
    CAST(0.05 * (
        CASE 
            WHEN current_attainment_pct < 0.80 THEN 1.00
            WHEN current_attainment_pct >= 0.80 AND current_attainment_pct < 1.00 THEN 1.25
            WHEN current_attainment_pct >= 1.00 AND current_attainment_pct < 1.50 THEN 2.00
            ELSE 2.50
        END
    ) AS DECIMAL(6, 4)) AS effective_rate
FROM attainment
