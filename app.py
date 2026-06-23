"""
E-Commerce Sales Analytics Dashboard
Entry point — sets global page config and renders the landing / home shell.
"""

import streamlit as st
from utils.data_loader import load_data, apply_filters

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcommerceAnalytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "E-Commerce Analytics Dashboard — built with Streamlit & Plotly"},
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #0F172A; }
[data-testid="stSidebar"]          { background: #1E293B; border-right: 1px solid #334155; }
h1, h2, h3, h4 { color: #F1F5F9; }
p, li, span    { color: #CBD5E1; }

/* ── KPI Cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 8px;
    transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); border-color: #2563EB; }
.kpi-label { font-size: 13px; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 28px; font-weight: 700; color: #F1F5F9; margin: 4px 0; }
.kpi-delta-pos { font-size: 13px; color: #10B981; }
.kpi-delta-neg { font-size: 13px; color: #EF4444; }

/* ── Insight Cards ── */
.insight-card {
    background: #1E293B;
    border-left: 4px solid #2563EB;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
}
.insight-card.green  { border-left-color: #10B981; }
.insight-card.amber  { border-left-color: #F59E0B; }
.insight-card.red    { border-left-color: #EF4444; }
.insight-title { font-size: 13px; font-weight: 700; color: #94A3B8; text-transform: uppercase; }
.insight-body  { font-size: 15px; color: #F1F5F9; margin-top: 4px; }

/* ── Section headers ── */
.section-header {
    font-size: 18px; font-weight: 700; color: #F1F5F9;
    border-bottom: 1px solid #334155; padding-bottom: 8px; margin: 24px 0 16px;
}

/* ── Sidebar brand ── */
.sidebar-brand {
    text-align: center; padding: 12px 0 24px;
    font-size: 20px; font-weight: 800; color: #F1F5F9;
    letter-spacing: 0.02em;
}
.sidebar-brand span { color: #2563EB; }

/* ── Data table ── */
[data-testid="stDataFrame"] { border-radius: 8px; }

/* ── Metric delta colors ── */
[data-testid="stMetricDelta"] svg { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Session state: data ───────────────────────────────────────────────────────
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">📊 <span>Ecommerce</span>Analytics</div>',
                unsafe_allow_html=True)

    # CSV upload
    uploaded = st.file_uploader("Upload your own CSV", type=["csv"],
                                 help="Must contain: Order ID, Sales, Profit, Order Date, etc.")

    # Load / reload
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.session_state.df_raw = None

    # Load data
    if st.session_state.df_raw is None:
        st.session_state.df_raw = load_data(uploaded)

    df_raw = st.session_state.df_raw

    st.divider()
    st.markdown("**🔍 Global Filters**")

    # ── Date range
    min_date = df_raw["Order Date"].min().date()
    max_date = df_raw["Order Date"].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # ── Category
    all_cats = sorted(df_raw["Category"].unique())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats)

    # ── Region
    all_regions = sorted(df_raw["Region"].unique())
    sel_regions = st.multiselect("Region", all_regions, default=all_regions)

    # ── State
    all_states = sorted(df_raw["State"].unique())
    sel_states = st.multiselect("State", all_states, default=all_states)

    # ── Customer (search)
    st.markdown("**Customer Filter**")
    customer_search = st.text_input("Search customer name", "")
    if customer_search:
        matching = [c for c in df_raw["Customer Name"].unique()
                    if customer_search.lower() in c.lower()]
        sel_customers = st.multiselect("Customers", matching, default=matching)
    else:
        sel_customers = []

    # ── Product (search)
    product_search = st.text_input("Search product name", "")
    if product_search:
        matching_p = [p for p in df_raw["Product Name"].unique()
                      if product_search.lower() in p.lower()]
        sel_products = st.multiselect("Products", matching_p, default=matching_p)
    else:
        sel_products = []

    st.divider()
    st.caption(f"Dataset: **{len(df_raw):,}** rows  |  "
               f"{df_raw['Order Date'].dt.year.min()}–{df_raw['Order Date'].dt.year.max()}")


# ── Apply filters globally ────────────────────────────────────────────────────
df_filtered = apply_filters(
    df_raw,
    date_range=date_range if len(date_range) == 2 else None,
    categories=sel_cats   if sel_cats   else None,
    regions=sel_regions   if sel_regions else None,
    states=sel_states     if sel_states  else None,
    customers=sel_customers if sel_customers else None,
    products=sel_products   if sel_products  else None,
)
st.session_state.df_filtered = df_filtered


# ── Home page content ─────────────────────────────────────────────────────────
st.markdown("## 📊 E-Commerce Analytics Dashboard")
st.markdown("Use the **sidebar** to navigate between pages and apply global filters.")

customer_col = next(
    (
        c for c in df_filtered.columns
        if c.strip().lower() in [
            "customer id",
            "customer_id",
            "customer id"
        ]
    ),
    None
)

c1, c2, c3 = st.columns(3)

c1.info(f"**{len(df_filtered):,}** orders after filters")

if customer_col:
    c2.info(
        f"**{df_filtered[customer_col].nunique():,}** unique customers"
    )
else:
    c2.info("Customer count unavailable")

c3.info(f"**${df_filtered['Sales'].sum():,.0f}** total revenue")

st.markdown("""
---
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
