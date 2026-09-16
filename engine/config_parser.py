"""
Config Parser and Pydantic Validators for Incentive Compensation Plans.
Translates business requirements expressed in YAML into strict, typed rulebooks.
"""

from typing import List, Optional
import yaml
from pydantic import BaseModel, Field, field_validator


class AttainmentTier(BaseModel):
    tier_name: str
    min_attainment_pct: float = Field(ge=0.0)
    max_attainment_pct: float = Field(ge=0.0)
    multiplier: float = Field(gt=0.0, description="Rate multiplier applied to base commission")
    flat_bonus: float = Field(default=0.0, ge=0.0, description="Optional milestone bonus")

    @field_validator("max_attainment_pct")
    def validate_bounds(cls, v, values):
        min_val = values.data.get("min_attainment_pct", 0.0)
        if v <= min_val:
            raise ValueError(f"max_attainment_pct ({v}) must be greater than min_attainment_pct ({min_val})")
        return v


class ClawbackPolicy(BaseModel):
    enabled: bool = True
    clawback_window_days: int = Field(default=90, ge=1)
    reversal_rate: float = Field(default=1.0, ge=0.0, le=1.0)


class PlanRules(BaseModel):
    base_commission_rate: float = Field(gt=0.0, le=1.0)
    split_credit_supported: bool = True
    clawback_policy: ClawbackPolicy
    attainment_tiers: List[AttainmentTier]


class PlanMetadata(BaseModel):
    plan_id: str
    plan_name: str
    effective_period: str
    currency: str = "USD"


class IncentivePlan(BaseModel):
    plan_metadata: PlanMetadata
    rules: PlanRules

    @classmethod
    def from_yaml(cls, file_path: str) -> "IncentivePlan":
        """Load and strictly validate a compensation plan from a YAML file."""
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
        return cls(**raw_data)

    def get_tier_for_attainment(self, attainment_pct: float) -> AttainmentTier:
        """Find the matching accelerator tier for a given attainment percentage."""
        for tier in self.rules.attainment_tiers:
            if tier.min_attainment_pct <= attainment_pct < tier.max_attainment_pct:
                return tier
        return self.rules.attainment_tiers[-1]
