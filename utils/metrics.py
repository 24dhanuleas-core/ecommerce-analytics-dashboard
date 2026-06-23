"""
KPI and metric computation helpers.
"""

import pandas as pd
import numpy as np


def kpi_summary(df: pd.DataFrame) -> dict:
    """Return a dict of top-level KPIs from a filtered DataFrame."""
    total_orders    = df["Order ID"].nunique()
    total_customers = df["Customer ID"].nunique() if "Customer ID" in df.columns else df["Customer Name"].nunique()
    total_revenue   = df["Sales"].sum()
    total_profit    = df["Profit"].sum()
    aov             = total_revenue / total_orders if total_orders else 0
    profit_margin   = (total_profit / total_revenue * 100) if total_revenue else 0

    return {
        "Total Revenue":    round(total_revenue, 2),
        "Total Profit":     round(total_profit, 2),
        "Total Orders":     total_orders,
        "Total Customers":  total_customers,
        "Avg Order Value":  round(aov, 2),
        "Profit Margin %":  round(profit_margin, 2),
    }


def growth_rate(current: float, previous: float) -> float:
    """Percent change from previous to current period."""
    if previous == 0:
        return 0.0
    return round((current - previous) / abs(previous) * 100, 2)


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregated revenue & profit."""
    return (
        df.groupby("YearMonth", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("YearMonth")
    )


def category_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Revenue", ascending=False)
    )


def region_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Region", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Revenue", ascending=False)
    )


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Product Name", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .sort_values("Revenue", ascending=False)
        .head(n)
    )


def bottom_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Product Name", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .sort_values("Revenue", ascending=True)
        .head(n)
    )


def customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["Customer ID", "Customer Name"], as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            CLV=("Customer Lifetime Value", "first"),
        )
        .sort_values("Revenue", ascending=False)
    )
    summary["Avg Order Value"] = (summary["Revenue"] / summary["Orders"]).round(2)
    return summary


def state_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("State", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Revenue", ascending=False)
    )


def profit_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Category", as_index=False)
        .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"))
        .assign(**{"Margin %": lambda x: (x["Profit"] / x["Revenue"] * 100).round(2)})
        .sort_values("Profit", ascending=False)
    )
