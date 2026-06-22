"""
Page 1 — Overview
KPIs, revenue trend, category & region breakdown, top products.
"""

import streamlit as st
import pandas as pd
from utils.metrics import (kpi_summary, monthly_revenue, category_revenue,
                            region_revenue, top_products)
from utils.charts  import (revenue_trend, donut, horizontal_bar, sparkline)

st.set_page_config(page_title="Overview", layout="wide")

# ── Inject shared CSS (inline mini-version) ───────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background:#0F172A; }
.kpi-card{background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);border:1px solid #334155;
          border-radius:12px;padding:20px 24px;margin-bottom:8px;}
.kpi-label{font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em;}
.kpi-value{font-size:28px;font-weight:700;color:#F1F5F9;margin:4px 0;}
.kpi-delta-pos{font-size:13px;color:#10B981;}
.kpi-delta-neg{font-size:13px;color:#EF4444;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.amber{border-left-color:#F59E0B;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)


def fmt_currency(v: float) -> str:
    if v >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if v >= 1_000:
        return f"${v/1_000:.1f}K"
    return f"${v:.0f}"


def kpi_card(label: str, value: str, delta: float | None = None) -> str:
    delta_html = ""
    if delta is not None:
        arrow = "▲" if delta >= 0 else "▼"
        cls   = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        delta_html = f'<span class="{cls}">{arrow} {abs(delta):.1f}%</span>'
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>"""


def insight_card(title: str, body: str, color: str = "") -> str:
    return f"""
    <div class="insight-card {color}">
        <div class="insight-title">{title}</div>
        <div class="insight-body">{body}</div>
    </div>"""


# ── Load filtered data ────────────────────────────────────────────────────────
df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Go back to the Home page to load data.")
    st.stop()

st.markdown("## 📋 Overview")

# ── KPIs ──────────────────────────────────────────────────────────────────────
kpis = kpi_summary(df)

col1, col2, col3, col4, col5, col6 = st.columns(6)
pairs = [
    ("Total Revenue",   fmt_currency(kpis["Total Revenue"])),
    ("Total Profit",    fmt_currency(kpis["Total Profit"])),
    ("Total Orders",    f"{kpis['Total Orders']:,}"),
    ("Total Customers", f"{kpis['Total Customers']:,}"),
    ("Avg Order Value", fmt_currency(kpis["Avg Order Value"])),
    ("Profit Margin",   f"{kpis['Profit Margin %']:.1f}%"),
]
for col, (label, val) in zip([col1, col2, col3, col4, col5, col6], pairs):
    col.markdown(kpi_card(label, val), unsafe_allow_html=True)

st.divider()

# ── Revenue Trend ─────────────────────────────────────────────────────────────
monthly = monthly_revenue(df)
st.markdown("### 📈 Revenue & Profit Trend")
fig_trend = revenue_trend(monthly, x="YearMonth", y="Revenue", title="Monthly Revenue")
st.plotly_chart(fig_trend, use_container_width=True)

# ── Category + Region ─────────────────────────────────────────────────────────
c_left, c_right = st.columns(2)

with c_left:
    st.markdown("### 🗂️ Revenue by Category")
    cat_df = category_revenue(df)
    fig_cat = donut(cat_df, names="Category", values="Revenue",
                    title="Revenue Share by Category")
    st.plotly_chart(fig_cat, use_container_width=True)

with c_right:
    st.markdown("### 🌍 Revenue by Region")
    reg_df = region_revenue(df)
    fig_reg = donut(reg_df, names="Region", values="Revenue",
                    title="Revenue Share by Region")
    st.plotly_chart(fig_reg, use_container_width=True)

# ── Top 10 Products ───────────────────────────────────────────────────────────
st.markdown("### 🏆 Top 10 Products by Revenue")
top_df = top_products(df, 10)
fig_top = horizontal_bar(top_df, x="Revenue", y="Product Name",
                         title="Top 10 Products — Revenue")
st.plotly_chart(fig_top, use_container_width=True)

# ── Auto Insights ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Automatic Insights")

# Top category
top_cat     = cat_df.iloc[0]
cat_pct     = top_cat["Revenue"] / cat_df["Revenue"].sum() * 100
# Top region
top_reg     = reg_df.iloc[0]
reg_pct     = top_reg["Revenue"] / reg_df["Revenue"].sum() * 100
# Monthly growth
if len(monthly) >= 2:
    last_rev  = monthly.iloc[-1]["Revenue"]
    prev_rev  = monthly.iloc[-2]["Revenue"]
    mom_growth = (last_rev - prev_rev) / prev_rev * 100 if prev_rev else 0
else:
    mom_growth = 0

insights = [
    ("🏆 Top Category",
     f"<b>{top_cat['Category']}</b> leads with "
     f"<b>{fmt_currency(top_cat['Revenue'])}</b> revenue ({cat_pct:.1f}% share).",
     ""),
    ("📍 Top Region",
     f"<b>{top_reg['Region']}</b> generates the most revenue at "
     f"<b>{fmt_currency(top_reg['Revenue'])}</b> ({reg_pct:.1f}% of total).",
     "green"),
    ("📆 Month-over-Month",
     f"Latest month revenue <b>{'grew' if mom_growth >= 0 else 'fell'} by "
     f"{abs(mom_growth):.1f}%</b> compared to the previous month.",
     "green" if mom_growth >= 0 else "red"),
    ("💰 Profit Margin",
     f"Overall profit margin is <b>{kpis['Profit Margin %']:.1f}%</b>. "
     + ("Healthy performance above 10%." if kpis["Profit Margin %"] > 10
        else "Margin below 10% — review discount strategy."),
     "green" if kpis["Profit Margin %"] > 10 else "amber"),
]

cols_i = st.columns(2)
for i, (title, body, color) in enumerate(insights):
    cols_i[i % 2].markdown(insight_card(title, body, color), unsafe_allow_html=True)
