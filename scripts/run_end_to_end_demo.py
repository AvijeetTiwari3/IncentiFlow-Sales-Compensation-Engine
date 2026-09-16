"""
IncentiFlow End-to-End Enterprise Demonstration Script.
Simulates real-world sales compensation workflow from raw ingestion to dbt compilation,
vectorized calculation, SOX audit verification, and executive reporting.
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from engine.config_parser import IncentivePlan
from engine.data_generator import generate_benchmark_datasets
from engine.calculation_engine import CommissionEngine
from engine.audit_runner import FinancialAuditRunner


def main():
    console = Console(force_terminal=True, legacy_windows=False)
    console.print(Panel.fit(
        "[bold cyan]IncentiFlow[/bold cyan] [bold white]-- Multi-Tenant Sales Incentive Compensation & Auditing Engine[/bold white]\n"
        "[dim]Enterprise-grade Analytics Engineering & Financial Lineage Suite[/dim]",
        border_style="cyan"
    ))

    # Step 1: Load Plan Configuration
    console.print("[bold yellow]>> Step 1:[/bold yellow] Parsing & Validating Declarative Incentive Plan (YAML)...")
    plan = IncentivePlan.from_yaml("configs/plans/enterprise_ae_plan.yaml")
    console.print(f"[bold green][OK][/bold green] Successfully loaded plan: [bold white]{plan.plan_metadata.plan_name}[/bold white] (Base Rate: {plan.rules.base_commission_rate*100}%, Tiers: {len(plan.rules.attainment_tiers)})")

    # Step 2: Synthetic Data Ingestion
    console.print("\n[bold yellow]>> Step 2:[/bold yellow] Synthesizing Enterprise Benchmark CRM & Billing Data...")
    df_reps, df_deals, df_splits, df_adjustments = generate_benchmark_datasets(num_reps=20, num_deals=600, random_seed=42)
    console.print(f"[bold green][OK][/bold green] Ingested [bold cyan]{len(df_reps)}[/bold cyan] Reps, [bold cyan]{len(df_deals)}[/bold cyan] Deals, [bold cyan]{len(df_splits)}[/bold cyan] Split Credits, [bold cyan]{len(df_adjustments)}[/bold cyan] Clawback Adjustments.")

    # Step 3: Commission Engine Execution
    console.print("\n[bold yellow]>> Step 3:[/bold yellow] Executing Vectorized Calculation Engine (DuckDB OLAP)...")
    engine = CommissionEngine(plan)
    engine.load_data(df_reps, df_deals, df_splits, df_adjustments)
    df_payouts = engine.execute_pipeline()
    df_rep_summary = engine.get_rep_summary_mart()
    console.print(f"[bold green][OK][/bold green] Successfully processed [bold cyan]{len(df_payouts)}[/bold cyan] payout transactions with cryptographic SHA-256 signatures.")

    # Step 4: Financial Auditing & SOX Validation
    console.print("\n[bold magenta]>> Step 4: Running Automated Financial Audit & Compliance Suite[/bold magenta]")
    auditor = FinancialAuditRunner(df_deals, df_splits, df_payouts, df_reps)
    audit_results = auditor.run_all_checks()

    audit_table = Table(title="Financial Audit & Compliance Verification Ledger", title_style="bold magenta", border_style="magenta")
    audit_table.add_column("Audit Check Name", style="bold white", width=45)
    audit_table.add_column("Status", justify="center", width=12)
    audit_table.add_column("Details & Metrics", style="dim", width=45)

    all_passed = True
    for res in audit_results:
        status_str = "[bold green]PASS[/bold green]" if res.status == "PASS" else "[bold red]FAIL[/bold red]"
        if res.status != "PASS":
            all_passed = False
        audit_table.add_row(res.check_name, status_str, f"{res.details} ({res.metrics})")
    
    console.print(audit_table)

    # Step 5: Executive Performance Rollup Mart
    console.print("\n[bold blue]>> Step 5: Executive Sales Rep Performance & Payout Mart[/bold blue]")
    summary_table = Table(title="Top Performing Sales Executives (Quarterly Rollup)", title_style="bold blue", border_style="blue")
    summary_table.add_column("Rep ID", justify="center", style="cyan")
    summary_table.add_column("Full Name", style="bold white")
    summary_table.add_column("Territory", style="dim")
    summary_table.add_column("Attributed Bookings", justify="right", style="green")
    summary_table.add_column("Quota Attainment", justify="right", style="bold yellow")
    summary_table.add_column("Gross Commission", justify="right", style="white")
    summary_table.add_column("Clawbacks", justify="right", style="red")
    summary_table.add_column("Net Payout", justify="right", style="bold green")

    for _, row in df_rep_summary.head(8).iterrows():
        summary_table.add_row(
            str(row["rep_id"]),
            str(row["rep_name"]),
            str(row["territory"]),
            f"${row['total_attributed_bookings']:,.2f}",
            f"{row['final_quota_attainment_pct']:.1f}%",
            f"${row['total_gross_commission']:,.2f}",
            f"${row['total_clawbacks']:,.2f}",
            f"${row['total_net_payout']:,.2f}"
        )
    console.print(summary_table)

    # Total Summary Panel
    total_deal_vol = df_payouts['attributed_booking'].sum()
    total_payout = df_payouts['net_commission_payout'].sum()
    effective_org_rate = (total_payout / total_deal_vol) * 100 if total_deal_vol > 0 else 0.0

    compliance_badge = "[bold green]CERTIFIED (100% Zero Leakage)[/bold green]" if all_passed else "[bold red]FAILED[/bold red]"

    console.print(Panel(
        f"[bold white]Total Bookings Managed:[/bold white] [bold green]${total_deal_vol:,.2f}[/bold green] | "
        f"[bold white]Total Net Commissions Paid:[/bold white] [bold green]${total_payout:,.2f}[/bold green] | "
        f"[bold white]Effective Org Commission Cost:[/bold white] [bold yellow]{effective_org_rate:.2f}%[/bold yellow]\n"
        f"[bold cyan]SOX Compliance Status:[/bold cyan] {compliance_badge}",
        title="[bold]Enterprise Financial Summary[/bold]",
        border_style="green" if all_passed else "red"
    ))


if __name__ == "__main__":
    main()
