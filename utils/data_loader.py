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

    categories = {
        "Technology": {
            "sub": ["Phones", "Computers", "Accessories", "Copiers"],
            "price_range": (50, 2500),
            "margin": (0.05, 0.35),
        },
        "Furniture": {
            "sub": ["Chairs", "Tables", "Bookcases", "Furnishings"],
            "price_range": (30, 1800),
            "margin": (-0.05, 0.25),
        },
        "Office Supplies": {
            "sub": ["Storage", "Binders", "Art", "Labels", "Paper", "Fasteners", "Supplies", "Envelopes"],
            "price_range": (5, 300),
            "margin": (0.10, 0.45),
        },
    }

    regions = {
        "West":     {"states": ["California", "Washington", "Oregon", "Nevada", "Utah", "Colorado", "Arizona"],
                     "cities": ["Los Angeles", "Seattle", "Portland", "Las Vegas", "Salt Lake City", "Denver", "Phoenix"]},
        "East":     {"states": ["New York", "Pennsylvania", "New Jersey", "Massachusetts", "Connecticut", "Maryland", "Virginia"],
                     "cities": ["New York City", "Philadelphia", "Newark", "Boston", "Hartford", "Baltimore", "Richmond"]},
        "Central":  {"states": ["Texas", "Illinois", "Ohio", "Michigan", "Minnesota", "Missouri", "Wisconsin"],
                     "cities": ["Houston", "Chicago", "Columbus", "Detroit", "Minneapolis", "St. Louis", "Milwaukee"]},
        "South":    {"states": ["Florida", "Georgia", "North Carolina", "Tennessee", "Alabama", "South Carolina", "Louisiana"],
                     "cities": ["Miami", "Atlanta", "Charlotte", "Nashville", "Birmingham", "Charleston", "New Orleans"]},
    }

    product_templates = {
        "Phones":      ["iPhone 14 Pro", "Samsung Galaxy S23", "Google Pixel 7", "OnePlus 11", "Motorola Edge 40"],
        "Computers":   ["Dell XPS 15", "MacBook Pro 16", "HP EliteBook 840", "Lenovo ThinkPad X1", "Surface Laptop 5"],
        "Accessories": ["Logitech MX Keys", "Apple AirPods Pro", "Samsung Buds Pro", "USB-C Hub 7-Port", "Webcam HD 1080p"],
        "Copiers":     ["Canon ImageRunner", "HP LaserJet MFP", "Xerox WorkCentre", "Brother MFC-L8900", "Ricoh IM C3000"],
        "Chairs":      ["Herman Miller Aeron", "Steelcase Leap V2", "HM Embody Chair", "IKEA Markus", "HON Ignition 2.0"],
        "Tables":      ["IKEA Bekant Desk", "Uplift V2 Standing", "Flexispot E7 Pro", "Fully Jarvis Desk", "Autonomous SmartDesk"],
        "Bookcases":   ["IKEA Billy Bookcase", "Sauder Select Bookcase", "Bush Cabot 5-Shelf", "Realspace Pro 5-Shelf", "Better Homes 4-Shelf"],
        "Furnishings": ["Lamp Set Modern", "Office Rug 5x7", "Whiteboard Magnetic", "Cork Board 36x24", "Desk Organizer Set"],
        "Storage":     ["Bankers Box", "Eldon Jumbo Portable", "Rubbermaid Bento", "Storex Portable Locker", "Sterilite 6-Drawer"],
        "Binders":     ["Avery Heavy Duty", "Cardinal XtraLife", "Wilson Jones Ultra", "Samsill Earth", "Five Star Flex"],
        "Art":         ["Crayola Business Markers", "Pilot G2 Pens 12pk", "Sharpie Fine Point", "Post-it Super Sticky", "3M Pop-up Notes"],
        "Labels":      ["Avery 5160 Address", "Avery 8160 Inkjet", "Avery 5163 Shipping", "Dymo LabelWriter 450", "Brother P-Touch Labels"],
        "Paper":       ["HP Office Paper Ream", "Hammermill Copy Plus", "Staples Multipurpose", "Georgia Pacific Copy", "Boise X-9 Multipurpose"],
        "Fasteners":   ["Swingline Stapler", "Acme Staple Remover", "Boston Pencil Sharpener", "Universal Binder Clips", "Acco Brands Paper Clips"],
        "Supplies":    ["Avery Shipping Tags", "TOPS Business Forms", "Mead Composition Book", "Ampad Recycled Legal", "Lorell Laminate Panel"],
        "Envelopes":   ["Columbian Poly-Klear", "Quality Park Redi-Seal", "Mead Plain Wove", "Universal Security Tint", "Columbian Business Envelopes"],
    }

    # ... rest of synthetic generation logic ...
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

    import streamlit as st
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
