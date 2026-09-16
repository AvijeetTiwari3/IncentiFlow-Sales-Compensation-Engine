"""
Enterprise Synthetic Data Generator.
Generates realistic B2B sales data: Sales Reps, Opportunities/Deals, Split Credits, and Adjustments/Clawbacks.
"""

import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def generate_benchmark_datasets(num_reps: int = 25, num_deals: int = 1500, random_seed: int = 42):
    """
    Generate deterministic, enterprise-grade synthetic datasets with strict financial conservation.
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    roles = ["Enterprise AE", "Commercial AE", "Mid-Market AE", "Strategic AE"]
    territories = ["North America - East", "North America - West", "EMEA", "APAC", "LATAM"]
    
    reps_data = []
    for i in range(1, num_reps + 1):
        rep_id = f"REP_{i:03d}"
        role = random.choice(roles)
        quota = {
            "Enterprise AE": 1_200_000.0,
            "Strategic AE": 1_800_000.0,
            "Commercial AE": 800_000.0,
            "Mid-Market AE": 600_000.0
        }[role]
        
        reps_data.append({
            "rep_id": rep_id,
            "full_name": f"Sales Exec {i}",
            "email": f"rep{i}@enterprise-corp.com",
            "role": role,
            "territory": random.choice(territories),
            "annual_quota": quota,
            "quarterly_quota": quota / 4.0,
            "is_active": True,
            "hire_date": "2024-01-15"
        })
    df_reps = pd.DataFrame(reps_data)

    base_date = datetime(2026, 1, 1)
    deal_types = ["New Business", "Expansion", "Renewal"]
    deal_stages = ["Closed Won", "Closed Lost", "Negotiation"]
    
    deals_data = []
    splits_data = []
    adjustments_data = []
    
    deal_counter = 1
    for d in range(num_deals):
        deal_id = f"OPP_{deal_counter:05d}"
        deal_counter += 1
        
        close_offset = random.randint(0, 89)
        close_date = base_date + timedelta(days=close_offset)
        
        stage = "Closed Won" if random.random() < 0.85 else random.choice(deal_stages)
        if stage != "Closed Won":
            booking_amount = round(random.uniform(10_000, 150_000), 2)
            deals_data.append({
                "deal_id": deal_id,
                "deal_name": f"Enterprise Deal {deal_id}",
                "account_name": f"Acme Client {random.randint(1, 300)}",
                "deal_type": random.choice(deal_types),
                "booking_amount": booking_amount,
                "stage": stage,
                "close_date": close_date.strftime("%Y-%m-%d"),
                "currency": "USD"
            })
            continue

        booking_amount = round(random.uniform(25_000, 350_000), 2)
        primary_rep = random.choice(df_reps["rep_id"].tolist())
        
        deals_data.append({
            "deal_id": deal_id,
            "deal_name": f"Enterprise Deal {deal_id}",
            "account_name": f"Acme Client {random.randint(1, 300)}",
            "deal_type": random.choice(deal_types),
            "booking_amount": booking_amount,
            "stage": stage,
            "close_date": close_date.strftime("%Y-%m-%d"),
            "currency": "USD"
        })

        is_split = random.random() < 0.25
        if is_split:
            other_reps = [r for r in df_reps["rep_id"].tolist() if r != primary_rep]
            secondary_rep = random.choice(other_reps)
            split_pct_primary = round(random.choice([0.60, 0.70, 0.80]), 2)
            split_pct_sec = round(1.0 - split_pct_primary, 2)
            
            primary_attributed = round(booking_amount * split_pct_primary, 2)
            sec_attributed = round(booking_amount - primary_attributed, 2)
            
            splits_data.append({
                "split_id": f"SPLIT_{deal_id}_1",
                "deal_id": deal_id,
                "rep_id": primary_rep,
                "split_percentage": split_pct_primary,
                "attributed_booking": primary_attributed,
                "is_primary": True
            })
            splits_data.append({
                "split_id": f"SPLIT_{deal_id}_2",
                "deal_id": deal_id,
                "rep_id": secondary_rep,
                "split_percentage": split_pct_sec,
                "attributed_booking": sec_attributed,
                "is_primary": False
            })
        else:
            splits_data.append({
                "split_id": f"SPLIT_{deal_id}_1",
                "deal_id": deal_id,
                "rep_id": primary_rep,
                "split_percentage": 1.0,
                "attributed_booking": booking_amount,
                "is_primary": True
            })

        if random.random() < 0.04:
            adj_offset = close_offset + random.randint(10, 45)
            adj_date = base_date + timedelta(days=adj_offset)
            adjustments_data.append({
                "adjustment_id": f"ADJ_{deal_id}",
                "deal_id": deal_id,
                "adjustment_type": "CLAWBACK_REFUND",
                "adjustment_amount": booking_amount,
                "reason": "Contract dispute and customer churn within 90 days",
                "adjustment_date": adj_date.strftime("%Y-%m-%d")
            })

    df_deals = pd.DataFrame(deals_data)
    df_splits = pd.DataFrame(splits_data)
    df_adjustments = pd.DataFrame(adjustments_data)

    return df_reps, df_deals, df_splits, df_adjustments
