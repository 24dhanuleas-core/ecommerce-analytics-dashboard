# ── Data cleaning ─────────────────────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize a raw sales DataFrame.

    Steps:
      1. Normalize column names
      2. Remove duplicates
      3. Parse dates
      4. Cast numeric columns
      5. Drop / fill nulls
      6. Remove invalid rows
      7. Validate schema
    """
    df = df.copy()

    # ── 1. Normalize column names
    df.columns = df.columns.str.replace("_", " ")
    df.columns = df.columns.str.strip().str.title()

    # Alias common variant names
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

    # ── 2. Remove duplicates
    if "Order ID" in df.columns:
        df.drop_duplicates(subset=["Order ID"], keep="first", inplace=True)
    df.drop_duplicates(inplace=True)

    # ── 3. Parse dates
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
        df.dropna(subset=["Order Date"], inplace=True)

    # ── 4. Numeric columns
    numeric_cols = ["Sales", "Profit", "Quantity", "Discount"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── 5. Fill / drop nulls safely
    required_cols = ["Sales", "Profit", "Quantity"]
    existing_required = [c for c in required_cols if c in df.columns]

    if existing_required:
        df.dropna(subset=existing_required, inplace=True)
    else:
        import streamlit as st
        st.warning(f"Missing required columns: {required_cols}. Found: {list(df.columns)}")

    if "Discount" in df.columns:
        df["Discount"] = df["Discount"].fillna(0)

    for col in ["Customer Name", "Product Name", "Category", "Sub Category",
                "Region", "State", "City"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").str.strip()

    # ── 6. Remove invalid rows
    if "Sales" in df.columns:
        df = df[df["Sales"] > 0]
    if "Quantity" in df.columns:
        df = df[df["Quantity"] > 0]
    if "Discount" in df.columns:
        df["Discount"] = df["Discount"].clip(0, 1)

    df.reset_index(drop=True, inplace=True)

    import streamlit as st
    st.write("Columns before feature engineering:", list(df.columns))

    # ── 7. Validate schema before feature engineering
    missing = [c for c in ["Sales", "Profit", "Quantity", "Order Date", "Customer ID"] if c not in df.columns]
    if missing:
        raise KeyError(f"Missing critical columns: {missing}. Available: {list(df.columns)}")

    return engineer_features(df)
