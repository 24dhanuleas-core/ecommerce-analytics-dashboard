"""
KPI and metric computation helpers.
"""

import pandas as pd
import numpy as np


def kpi_summary(df: pd.DataFrame) -> dict:
    """Return a dict of top-level KPIs from a filtered DataFrame."""

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    customer_col = next(
        (c for c in df.columns if c.strip().lower() in ["customer id", "customer_id"]),
        None
    )

    total_orders = (
        df[order_col].nunique()
        if order_col
        else len(df)
    )

    total_customers = (
        df[customer_col].nunique()
        if customer_col
        else df["Customer Name"].nunique()
    )

    total_revenue = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    aov = total_revenue / total_orders if total_orders else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    return {
        "Total Revenue": round(total_revenue, 2),
        "Total Profit": round(total_profit, 2),
        "Total Orders": total_orders,
        "Total Customers": total_customers,
        "Avg Order Value": round(aov, 2),
        "Profit Margin %": round(profit_margin, 2),
    }


def growth_rate(current: float, previous: float) -> float:
    """Percent change from previous to current period."""
    if previous == 0:
        return 0.0
    return round((current - previous) / abs(previous) * 100, 2)


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue, profit and order trends."""

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    if order_col:
        monthly = (
            df.groupby("YearMonth", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Orders=(order_col, "nunique")
            )
            .sort_values("YearMonth")
        )
    else:
        monthly = (
            df.groupby("YearMonth", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("YearMonth")
        )
        monthly["Orders"] = 0

    return monthly


def category_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue by category."""

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    if order_col:
        cat_df = (
            df.groupby("Category", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Orders=(order_col, "nunique")
            )
            .sort_values("Revenue", ascending=False)
        )
    else:
        cat_df = (
            df.groupby("Category", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("Revenue", ascending=False)
        )
        cat_df["Orders"] = 0

    return cat_df


def region_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue by region."""

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    if order_col:
        reg_df = (
            df.groupby("Region", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Orders=(order_col, "nunique")
            )
            .sort_values("Revenue", ascending=False)
        )
    else:
        reg_df = (
            df.groupby("Region", as_index=False)
            .agg(
                Revenue=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("Revenue", ascending=False)
        )
        reg_df["Orders"] = 0

    return reg_df


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
    """Customer-level metrics."""

    customer_col = next(
        (c for c in df.columns if c.strip().lower() in ["customer id", "customer_id"]),
        None
    )

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    group_cols = ["Customer Name"]
    if customer_col:
        group_cols.insert(0, customer_col)

    cust_df = (
        df.groupby(group_cols, as_index=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=(order_col, "nunique") if order_col else ("Sales", "count")
        )
    )

    # CLV
    cust_df["CLV"] = cust_df["Revenue"]

    # Avg Order Value
    cust_df["Avg Order Value"] = (
        cust_df["Revenue"] / cust_df["Orders"]
    ).fillna(0)

    # Customer Segments
    q1 = cust_df["Revenue"].quantile(0.25)
    q3 = cust_df["Revenue"].quantile(0.75)

    def segment_customer(revenue):
        if revenue >= q3:
            return "High Value"
        elif revenue >= q1:
            return "Medium Value"
        return "Low Value"

    cust_df["Segment"] = cust_df["Revenue"].apply(segment_customer)

    return cust_df.sort_values("Revenue", ascending=False)


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
