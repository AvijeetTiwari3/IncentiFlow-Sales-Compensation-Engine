import pytest
import pandas as pd
from engine.config_parser import IncentivePlan
from engine.calculation_engine import CommissionEngine
from engine.data_generator import generate_benchmark_datasets


def test_commission_calculation_pipeline():
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    engine = CommissionEngine(plan)
    
    df_reps, df_deals, df_splits, df_adjustments = generate_benchmark_datasets(num_reps=5, num_deals=50, random_seed=123)
    engine.load_data(df_reps, df_deals, df_splits, df_adjustments)
    
    df_payouts = engine.execute_pipeline()
    assert len(df_payouts) > 0
    assert "net_commission_payout" in df_payouts.columns
    assert "audit_signature" in df_payouts.columns
    
    # Assert every payout has a valid SHA-256 signature (64 hex characters)
    for sig in df_payouts["audit_signature"]:
        assert len(sig) == 64


def test_split_deal_attribution():
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    engine = CommissionEngine(plan)
    
    df_reps = pd.DataFrame([{
        "rep_id": "REP_001", "full_name": "Alice", "role": "Enterprise AE",
        "territory": "East", "annual_quota": 400000.0, "quarterly_quota": 100000.0,
        "is_active": True, "hire_date": "2024-01-01"
    }, {
        "rep_id": "REP_002", "full_name": "Bob", "role": "Enterprise AE",
        "territory": "East", "annual_quota": 400000.0, "quarterly_quota": 100000.0,
        "is_active": True, "hire_date": "2024-01-01"
    }])
    
    df_deals = pd.DataFrame([{
        "deal_id": "OPP_SPLIT_1", "deal_name": "Mega Deal", "account_name": "BigCo",
        "deal_type": "New Business", "booking_amount": 100000.0, "stage": "Closed Won",
        "close_date": "2026-01-15", "currency": "USD"
    }])
    
    df_splits = pd.DataFrame([{
        "split_id": "S1", "deal_id": "OPP_SPLIT_1", "rep_id": "REP_001",
        "split_percentage": 0.70, "attributed_booking": 70000.0, "is_primary": True
    }, {
        "split_id": "S2", "deal_id": "OPP_SPLIT_1", "rep_id": "REP_002",
        "split_percentage": 0.30, "attributed_booking": 30000.0, "is_primary": False
    }])
    
    df_adjustments = pd.DataFrame(columns=["adjustment_id", "deal_id", "adjustment_type", "adjustment_amount", "reason", "adjustment_date"])
    
    engine.load_data(df_reps, df_deals, df_splits, df_adjustments)
    df_payouts = engine.execute_pipeline()
    
    # Total credited booking must equal deal total $100k
    assert df_payouts["attributed_booking"].sum() == 100000.0
    
    # Alice earned on $70k (70% quota -> Tier 1: 5%) = $3,500
    p_alice = df_payouts[df_payouts["rep_id"] == "REP_001"].iloc[0]
    assert p_alice["gross_commission"] == 3500.0
    
    # Bob earned on $30k (30% quota -> Tier 1: 5%) = $1,500
    p_bob = df_payouts[df_payouts["rep_id"] == "REP_002"].iloc[0]
    assert p_bob["gross_commission"] == 1500.0
