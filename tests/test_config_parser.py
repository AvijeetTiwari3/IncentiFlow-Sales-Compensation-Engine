import pytest
from engine.config_parser import IncentivePlan, AttainmentTier, PlanRules, PlanMetadata


def test_load_valid_plan():
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    assert plan.plan_metadata.plan_id == "ENTERPRISE_AE_FY26"
    assert plan.rules.base_commission_rate == 0.05
    assert len(plan.rules.attainment_tiers) == 4


def test_tier_lookup_logic():
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    
    # 50% attainment -> Tier 1 (multiplier 1.0)
    tier1 = plan.get_tier_for_attainment(0.50)
    assert tier1.multiplier == 1.0
    
    # 90% attainment -> Tier 2 (multiplier 1.25)
    tier2 = plan.get_tier_for_attainment(0.90)
    assert tier2.multiplier == 1.25

    # 120% attainment -> Tier 3 (multiplier 2.0)
    tier3 = plan.get_tier_for_attainment(1.20)
    assert tier3.multiplier == 2.0
    assert tier3.flat_bonus == 2500.0

    # 180% attainment -> Tier 4 (multiplier 2.5)
    tier4 = plan.get_tier_for_attainment(1.80)
    assert tier4.multiplier == 2.5
    assert tier4.flat_bonus == 7500.0


def test_invalid_tier_bounds():
    with pytest.raises(Exception):
        AttainmentTier(
            tier_name="Invalid Tier",
            min_attainment_pct=1.0,
            max_attainment_pct=0.5, # invalid: max < min
            multiplier=1.5
        )
