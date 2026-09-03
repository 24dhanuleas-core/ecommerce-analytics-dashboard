"""
Data loading, cleaning, and feature engineering utilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import streamlit as st

# ── Synthetic data generation ────────────────────────────────────────────────
def generate_synthetic_data(n_rows: int = 10_000, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic e-commerce sales data for testing."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_rows):
        qty = int(rng.integers(1, 11))
        unit_price = float(rng.uniform(10, 500))
        discount = float(rng.choice([0, 0.1, 0.2]))
        sales = round(unit_price * qty * (1 - discount), 2)
        profit = round(sales * rng.uniform(0.05, 0.3), 2)
        rows.append({
            "Order ID": f"ORD-{100000+i}",
            "Customer ID": f"CUST-{i%1000}",
            "Customer Name": f"Customer {i%1000}",
            "Product Name": f"Product {i%50}",
            "Category": "Technology",
            "Sub Category": "Phones",
            "Region": "West",
            "State": "California",
            "City": "Los Angeles",
            "Order Date": pd.Timestamp("2023-01-01") + pd.Timedelta(days=i%365),
            "Quantity": qty,
            "Sales": sales,
            "Profit": profit,
            "Discount": discount,
        })
    return pd.DataFrame(rows)

# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading data…")
def load_data(uploaded_file=None) -> pd.DataFrame:
    """
    Load data from uploaded file, local CSV, or generate synthetic data.
    Priority: uploaded_file > local CSV > synthetic generation
    """
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
    """
    Clean and standardize the raw sales DataFrame.
    """
    df = df.copy()
    df.columns = df.columns.str.replace("_", " ").str.strip().str.title()

    # Rename common variants
    rename_map = {
        "Sub-Category": "Sub Category",
        "Order_Date": "Order Date",
        "Order_Id": "Order ID",
        "Customer_Id": "Customer ID",
        "Customer_Name": "Customer Name",
        "Product_Name": "Product Name",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # Remove duplicates
    if "Order ID" in df.columns:
        df.drop_duplicates(subset=["Order ID"], keep="first", inplace=True)

    # Parse dates
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        df.dropna(subset=["Order Date"], inplace=True)

    # Convert numeric columns
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with missing key values
    df.dropna(subset=["Sales", "Profit", "Quantity"], inplace=True)

    # Fill missing discount values
    if "Discount" in df.columns:
        df["Discount"] = df["Discount"].fillna(0).clip(0, 1)

    # Fill missing text values
    for col in ["Customer Name", "Product Name", "Category", "Sub Category",
                "Region", "State", "City"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").str.strip()

    # Remove invalid rows
    if "Sales" in df.columns:
        df = df[df["Sales"] > 0]
    if "Quantity" in df.columns:
        df = df[df["Quantity"] > 0]

    df.reset_index(drop=True, inplace=True)

    return engineer_features(df)

# ── Feature engineering ───────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used throughout the dashboard."""
    df = df.copy()

    # Profit margin percentage
    if "Sales" in df.columns and "Profit" in df.columns:
        df["Profit Margin %"] = np.where(
            df["Sales"] != 0,
            (df["Profit"] / df["Sales"] * 100).round(2),
            0.0
        )

    # Date-based features
    if "Order Date" in df.columns:
        df["Year"] = df["Order Date"].dt.year
        df["Month"] = df["Order Date"].dt.month
        df["Month Name"] = df["Order Date"].dt.strftime("%b")
        df["Quarter"] = df["Order Date"].dt.quarter.map({1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4"})
        df["Week"] = df["Order Date"].dt.isocalendar().week.astype(int)
        df["Day of Week"] = df["Order Date"].dt.day_name()
        df["YearMonth"] = df["Order Date"].dt.to_period("M").astype(str)

    # Customer lifetime value
    if "Customer ID" in df.columns and "Sales" in df.columns:
        df["Customer Lifetime Value"] = df.groupby("Customer ID")["Sales"].transform("sum").round(2)

    # Order frequency
    if "Customer ID" in df.columns and "Order ID" in df.columns:
        df["Order Frequency"] = df.groupby("Customer ID")["Order ID"].transform("count")
    elif "Customer ID" in df.columns:
        df["Order Frequency"] = df.groupby("Customer ID")["Customer ID"].transform("count")

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
    """Return a filtered copy of the DataFrame based on sidebar selections."""
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
