import pytest
import pandas as pd
from engine.config_parser import IncentivePlan
from engine.calculation_engine import CommissionEngine
from engine.audit_runner import FinancialAuditRunner
from engine.data_generator import generate_benchmark_datasets


def test_clawback_deduction_and_zero_leakage():
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    engine = CommissionEngine(plan)
    
    df_reps, df_deals, df_splits, df_adjustments = generate_benchmark_datasets(num_reps=10, num_deals=200, random_seed=42)
    engine.load_data(df_reps, df_deals, df_splits, df_adjustments)
    
    df_payouts = engine.execute_pipeline()
    
    auditor = FinancialAuditRunner(df_deals, df_splits, df_payouts, df_reps)
    results = auditor.run_all_checks()
    
    for r in results:
        assert r.status == "PASS", f"Audit check failed: {r.check_name} - {r.details}"
