"""
E-Commerce Sales Analytics Dashboard
Entry point — sets global page config and renders the landing / home shell.
"""

import streamlit as st
import utils.data_loader as dl   # safer import style

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcommerceAnalytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "E-Commerce Analytics Dashboard — built with Streamlit & Plotly"},
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""<style>/* your CSS exactly as you pasted */</style>""", unsafe_allow_html=True)

# ── Session state: data ───────────────────────────────────────────────────────
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">📊 <span>Ecommerce</span>Analytics</div>', unsafe_allow_html=True)

    # CSV upload
    uploaded = st.file_uploader("Upload your own CSV", type=["csv"],
                                 help="Must contain: Order ID, Sales, Profit, Order Date, etc.")

    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_raw = None

    # Load data
    if st.session_state.df_raw is None:
        st.session_state.df_raw = dl.load_data(uploaded)

    df_raw = st.session_state.df_raw

    # Filters (unchanged from your code)
    st.divider()
    st.markdown("**🔍 Global Filters**")

    min_date = df_raw["Order Date"].min().date()
    max_date = df_raw["Order Date"].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    all_cats = sorted(df_raw["Category"].unique())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats)

    all_regions = sorted(df_raw["Region"].unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions)

    all_states = sorted(df_raw["State"].unique())
    sel_states = st.multiselect("State", all_states, default=all_states)

    st.markdown("**Customer Filter**")
    customer_search = st.text_input("Search customer name", "")
    if customer_search:
        matching = [c for c in df_raw["Customer Name"].unique() if customer_search.lower() in c.lower()]
        sel_customers = st.multiselect("Customers", matching, default=matching)
    else:
        sel_customers = []

    product_search = st.text_input("Search product name", "")
    if product_search:
        matching_p = [p for p in df_raw["Product Name"].unique() if product_search.lower() in p.lower()]
        sel_products = st.multiselect("Products", matching_p, default=matching_p)
    else:
        sel_products = []

    st.divider()
    st.caption(f"Dataset: **{len(df_raw):,}** rows  |  "
               f"{df_raw['Order Date'].dt.year.min()}–{df_raw['Order Date'].dt.year.max()}")

# ── Apply filters globally ────────────────────────────────────────────────────
df_filtered = dl.apply_filters(
    df_raw,
    date_range=date_range if len(date_range) == 2 else None,
    categories=sel_cats if sel_cats else None,
    regions=sel_regions if sel_regions else None,
    states=sel_states if sel_states else None,
    customers=sel_customers if sel_customers else None,
    products=sel_products if sel_products else None,
)
st.session_state.df_filtered = df_filtered

# ── Home page content ─────────────────────────────────────────────────────────
st.markdown("## 📊 E-Commerce Analytics Dashboard")
st.markdown("Use the **sidebar** to navigate between pages and apply global filters.")

customer_col = next(
    (c for c in df_filtered.columns if c.strip().lower() in ["customer id", "customer_id"]),
    None
)

c1, c2, c3 = st.columns(3)
c1.info(f"**{len(df_filtered):,}** orders after filters")

if customer_col:
    c2.info(f"**{df_filtered[customer_col].nunique():,}** unique customers")
else:
    c2.info("Customer count unavailable")

c3.info(f"**${df_filtered['Sales'].sum():,.0f}** total revenue")

st.markdown("""--- 
### 🗺️ Dashboard Pages
| Page | Description |
|------|-------------|
| **1 — Overview** | KPIs, revenue trend, category & region breakdown |
| **2 — Sales Analysis** | Daily / weekly / monthly / quarterly trends + forecasting |
| **3 — Product Analysis** | Top/bottom products, treemap, subcategory drill-down |
| **4 — Customer Analysis** | Segmentation, CLV, repeat customers, export |
| **5 — Regional Analysis** | US choropleth, state/city ranking, heatmap |
| **6 — Profitability** | Margins, discount impact, loss-makers |
| **7 — AI Insights** | Rule-based automatic business insights |
---
> Built with **Streamlit · Plotly · Pandas · NumPy**
""")
