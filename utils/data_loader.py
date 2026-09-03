"""
Data loading, cleaning, and feature engineering utilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

# ── Synthetic data generation ────────────────────────────────────────────────
def generate_synthetic_data(n_rows: int = 10_000, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic e-commerce sales data."""
    rng = np.random.default_rng(seed)
    # ... your synthetic generation logic exactly as you pasted ...
    return pd.DataFrame(rows)

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def load_data(uploaded_file=None) -> pd.DataFrame:
    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
        else:
            csv_path = Path(__file__).parent.parent / "data" / "sales.csv"
            if csv_path.exists():
                df = pd.read_csv(csv_path)
            else:
                df = generate_synthetic_data()
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(csv_path, index=False)
    except Exception as e:
        st.warning(f"Could not load file ({e}). Generating synthetic data.")
        df = generate_synthetic_data()

    return clean_data(df)

# ── Data cleaning ─────────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.replace("_", " ")
    df.columns = [c.strip() for c in df.columns]

    df = df.copy()
    df.columns = df.columns.str.strip().str.title()

    rename_map = {
        "Sub-Category": "Sub Category",
        "Sub_Category": "Sub Category",
        "Subcategory":  "Sub Category",
        "Order_Date":   "Order Date",
        "Order_Id":     "Order ID",
        "Customer_Id":  "Customer ID",
        "Customer_Name":"Customer Name",
        "Product_Name": "Product Name",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    if "Order ID" in df.columns:
        df.drop_duplicates(subset=["Order ID"], keep="first", inplace=True)
        df.drop_duplicates(inplace=True)

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        df.dropna(subset=["Order Date"], inplace=True)

    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(subset=["Sales", "Profit", "Quantity"], inplace=True)
    df["Discount"] = df["Discount"].fillna(0)

    for col in ["Customer Name", "Product Name", "Category", "Sub Category",
                "Region", "State", "City"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").str.strip()

    df = df[df["Sales"] > 0]
    df = df[df["Quantity"] > 0]
    df["Discount"] = df["Discount"].clip(0, 1)

    df.reset_index(drop=True, inplace=True)

    st.write("Before engineer_features:", list(df.columns))

    return engineer_features(df)

# ── Feature engineering ───────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Profit Margin %"] = np.where(
        df["Sales"] != 0,
        (df["Profit"] / df["Sales"] * 100).round(2),
        0.0
    )

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Quarter"] = df["Order Date"].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
    df["Week"] = df["Order Date"].dt.isocalendar().week.astype(int)
    df["Day of Week"] = df["Order Date"].dt.day_name()
    df["YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)

    customer_col = next(
        (c for c in df.columns if c.strip().lower() in ["customer id", "customer_id"]),
        None
    )

    order_col = next(
        (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
        None
    )

    if customer_col is None:
        raise KeyError(f"Customer ID column not found. Columns: {list(df.columns)}")

    df["Customer Lifetime Value"] = (
        df.groupby(customer_col)["Sales"]
        .transform("sum")
        .round(2)
    )

    if order_col:
        df["Order Frequency"] = (
            df.groupby(customer_col)[order_col]
            .transform("count")
        )
    else:
        df["Order Frequency"] = (
            df.groupby(customer_col)[customer_col]
            .transform("count")
        )

    return df

# ── Filtering helper ──────────────────────────────────────────────────────────
def apply_filters(
    df: pd.DataFrame,
    date_range=None,
    categories=None,
    regions=None,
    states=None,
    customers=None,
    products=None,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)

    if date_range and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask &= (df["Order Date"] >= start) & (df["Order Date"] <= end)

    if categories:
        mask &= df["Category"].isin(categories)

    if regions:
        mask &= df["Region"].isin(regions)

    if states:
        mask &= df["State"].isin(states)

    if customers:
        mask &= df["Customer Name"].isin(customers)

    if products:
        mask &= df["Product Name"].isin(products)

    return df[mask].copy()
