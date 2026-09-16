"""
IncentiFlow Vectorized Calculation Engine.
Executes multi-tier commission calculations, accelerator lookups, deal-splits, and cryptographic audit hashing.
"""

import hashlib
import duckdb
import pandas as pd
from engine.config_parser import IncentivePlan


class CommissionEngine:
    def __init__(self, plan: IncentivePlan, db_path: str = ":memory:"):
        self.plan = plan
        self.con = duckdb.connect(db_path)

    def load_data(self, df_reps: pd.DataFrame, df_deals: pd.DataFrame, 
                  df_splits: pd.DataFrame, df_adjustments: pd.DataFrame):
        """Register raw datasets into DuckDB tables."""
        self.con.register("raw_sales_reps", df_reps)
        self.con.register("raw_deals", df_deals)
        self.con.register("raw_deal_splits", df_splits)
        self.con.register("raw_adjustments", df_adjustments)

    def execute_pipeline(self) -> pd.DataFrame:
        """
        Executes end-to-end vectorized commission calculation with running attainment tiers,
        accelerators, and clawbacks.
        """
        self.con.execute("""
            CREATE OR REPLACE TABLE stg_active_splits AS
            SELECT 
                s.split_id,
                s.deal_id,
                s.rep_id,
                r.full_name AS rep_name,
                r.role AS rep_role,
                r.territory,
                r.quarterly_quota,
                d.deal_name,
                d.account_name,
                d.deal_type,
                d.booking_amount AS full_deal_amount,
                s.split_percentage,
                s.attributed_booking,
                d.close_date
            FROM raw_deal_splits s
            JOIN raw_deals d ON s.deal_id = d.deal_id
            JOIN raw_sales_reps r ON s.rep_id = r.rep_id
            WHERE d.stage = 'Closed Won'
            ORDER BY s.rep_id, d.close_date ASC
        """)

        self.con.execute("""
            CREATE OR REPLACE TABLE int_rep_deal_attainment AS
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
            FROM stg_active_splits
        """)

        df_attainment = self.con.execute("SELECT * FROM int_rep_deal_attainment").fetchdf()

        tiers = []
        multipliers = []
        applied_rates = []
        gross_commissions = []
        flat_bonuses = []

        base_rate = self.plan.rules.base_commission_rate

        for _, row in df_attainment.iterrows():
            attainment = row["current_attainment_pct"]
            tier = self.plan.get_tier_for_attainment(attainment)
            
            rate = base_rate * tier.multiplier
            commission = round(row["attributed_booking"] * rate, 2)
            
            tiers.append(tier.tier_name)
            multipliers.append(tier.multiplier)
            applied_rates.append(rate)
            gross_commissions.append(commission)
            flat_bonuses.append(tier.flat_bonus)

        df_attainment["applied_tier"] = tiers
        df_attainment["tier_multiplier"] = multipliers
        df_attainment["effective_rate"] = applied_rates
        df_attainment["gross_commission"] = gross_commissions
        df_attainment["milestone_bonus"] = flat_bonuses

        self.con.register("int_calculated_payouts", df_attainment)

        self.con.execute("""
            CREATE OR REPLACE TABLE fct_final_payouts AS
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
                c.gross_commission,
                c.milestone_bonus,
                CASE 
                    WHEN a.adjustment_id IS NOT NULL THEN (c.gross_commission * -1.0)
                    ELSE 0.0 
                END AS clawback_deduction,
                CASE 
                    WHEN a.adjustment_id IS NOT NULL THEN 'CLAWBACK_APPLIED'
                    ELSE 'STANDARD_PAYOUT'
                END AS payout_status,
                (c.gross_commission + CASE WHEN a.adjustment_id IS NOT NULL THEN (c.gross_commission * -1.0) ELSE 0.0 END) AS net_commission_payout
            FROM int_calculated_payouts c
            LEFT JOIN raw_adjustments a ON c.deal_id = a.deal_id
        """)

        df_final = self.con.execute("SELECT * FROM fct_final_payouts").fetchdf()
        
        audit_hashes = []
        for _, row in df_final.iterrows():
            hash_input = f"{row['payout_id']}|{row['deal_id']}|{row['rep_id']}|{row['attributed_booking']}|{row['effective_rate']}|{row['net_commission_payout']}"
            audit_hashes.append(hashlib.sha256(hash_input.encode("utf-8")).hexdigest())

        df_final["audit_signature"] = audit_hashes
        self.con.register("fct_commission_payouts_audited", df_final)
        
        return df_final

    def get_rep_summary_mart(self) -> pd.DataFrame:
        """Generate executive monthly/quarterly sales performance rollup mart."""
        return self.con.execute("""
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
            FROM fct_commission_payouts_audited
            GROUP BY rep_id, rep_name, territory, quarterly_quota
            ORDER BY total_attributed_bookings DESC
        """).fetchdf()
