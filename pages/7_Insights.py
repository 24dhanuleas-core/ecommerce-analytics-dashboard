"""
Page 7 — AI Insights (Rule-based automatic analytics)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.metrics import (kpi_summary, monthly_revenue, category_revenue,
                            region_revenue, top_products, customer_summary)
from utils.charts  import LAYOUT_DEFAULTS, PALETTE, GREEN, AMBER, RED, BLUE

st.set_page_config(page_title="AI Insights", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:16px 20px;margin:8px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.amber{border-left-color:#F59E0B;}.insight-card.red{border-left-color:#EF4444;}
.insight-title{font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:.08em;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:6px;line-height:1.5;}
.insight-metric{font-size:24px;font-weight:700;color:#F1F5F9;margin:6px 0;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Return to Home page.")
    st.stop()

st.markdown("## 🤖 Automatic Business Insights")
st.caption("Rule-based analytics engine — insights update with every filter change.")

# ── Compute all needed metrics ────────────────────────────────────────────────
kpis       = kpi_summary(df)
monthly    = monthly_revenue(df)
cat_df     = category_revenue(df)
reg_df     = region_revenue(df)
top_prods  = top_products(df, 5)
cust_df    = customer_summary(df)

# ── Monthly growth trend ──────────────────────────────────────────────────────
if len(monthly) >= 3:
    monthly["Growth %"] = monthly["Revenue"].pct_change().mul(100)
    avg_growth = monthly["Growth %"].dropna().mean()
    last_growth = monthly["Growth %"].dropna().iloc[-1]
    growth_trend = "accelerating" if last_growth > avg_growth else "decelerating"
else:
    avg_growth = last_growth = 0
    growth_trend = "stable"

# ── Discount analysis ─────────────────────────────────────────────────────────
heavy_disc = df[df["Discount"] >= 0.30]
heavy_disc_rev    = heavy_disc["Sales"].sum()
heavy_disc_profit = heavy_disc["Profit"].sum()
heavy_disc_pct    = heavy_disc_rev / df["Sales"].sum() * 100 if df["Sales"].sum() else 0

# ── Category metrics ──────────────────────────────────────────────────────────
top_cat    = cat_df.iloc[0]
top_cat_pct = top_cat["Revenue"] / cat_df["Revenue"].sum() * 100

# ── Customer metrics ──────────────────────────────────────────────────────────
repeat_pct = (cust_df["Orders"] > 1).sum() / len(cust_df) * 100 if len(cust_df) else 0
top_customer = cust_df.iloc[0]

# ── Region ────────────────────────────────────────────────────────────────────
top_region = reg_df.iloc[0]
low_region = reg_df.iloc[-1]

# ── Loss-making ───────────────────────────────────────────────────────────────
loss_count = (df.groupby("Product Name")["Profit"].sum() < 0).sum()

# ── Helper ────────────────────────────────────────────────────────────────────
def card(title, metric, body, color="", icon=""):
    return f"""
    <div class="insight-card {color}">
        <div class="insight-title">{icon} {title}</div>
        <div class="insight-metric">{metric}</div>
        <div class="insight-body">{body}</div>
    </div>"""


# ── Render insight grid ───────────────────────────────────────────────────────
st.markdown("### 📈 Revenue Performance")
r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    color = "green" if last_growth >= 0 else "red"
    st.markdown(card(
        "Latest MoM Growth",
        f"{last_growth:+.1f}%",
        f"Revenue growth is <b>{growth_trend}</b>. Average MoM growth across the period: <b>{avg_growth:+.1f}%</b>.",
        color, "📊"
    ), unsafe_allow_html=True)

with r1c2:
    st.markdown(card(
        "Total Revenue",
        f"${kpis['Total Revenue']:,.0f}",
        f"Across <b>{kpis['Total Orders']:,}</b> orders from <b>{kpis['Total Customers']:,}</b> unique customers.",
        "", "💵"
    ), unsafe_allow_html=True)

with r1c3:
    color = "green" if kpis["Profit Margin %"] > 10 else "amber" if kpis["Profit Margin %"] > 0 else "red"
    st.markdown(card(
        "Profit Margin",
        f"{kpis['Profit Margin %']:.1f}%",
        ("Strong margin above 10%. Maintain current pricing strategy."
         if kpis["Profit Margin %"] > 10
         else "Margin under 10%. Review discount and cost structure."),
        color, "💰"
    ), unsafe_allow_html=True)

st.divider()
st.markdown("### 🏆 Product & Category Intelligence")
r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    st.markdown(card(
        "Dominant Category",
        top_cat["Category"],
        f"Contributes <b>{top_cat_pct:.1f}%</b> of total revenue "
        f"(<b>${top_cat['Revenue']:,.0f}</b>). Focus marketing here.",
        "green", "🏅"
    ), unsafe_allow_html=True)

with r2c2:
    best_prod = top_prods.iloc[0]
    st.markdown(card(
        "Best-Selling Product",
        best_prod["Product Name"][:25] + "…" if len(best_prod["Product Name"]) > 25 else best_prod["Product Name"],
        f"Revenue: <b>${best_prod['Revenue']:,.0f}</b>. "
        f"Profit: <b>${best_prod['Profit']:,.0f}</b>. "
        f"Units sold: <b>{best_prod['Quantity']:,}</b>.",
        "green", "🥇"
    ), unsafe_allow_html=True)

with r2c3:
    color = "red" if loss_count > 5 else "amber" if loss_count > 0 else "green"
    st.markdown(card(
        "Loss-Making Products",
        f"{loss_count}",
        (f"<b>{loss_count}</b> products have negative cumulative profit. "
         "Recommend price review or discontinuation." if loss_count > 0
         else "No loss-making products detected. Healthy product portfolio."),
        color, "⚠️"
    ), unsafe_allow_html=True)

st.divider()
st.markdown("### 👥 Customer Intelligence")
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    color = "green" if repeat_pct > 40 else "amber"
    st.markdown(card(
        "Customer Retention",
        f"{repeat_pct:.1f}%",
        ("Strong retention rate. Invest in loyalty programs to maintain." if repeat_pct > 40
         else "Retention below 40%. Introduce post-purchase follow-up and loyalty incentives."),
        color, "🔄"
    ), unsafe_allow_html=True)

with r3c2:
    st.markdown(card(
        "Top Customer",
        top_customer["Customer Name"],
        f"Lifetime value: <b>${top_customer['Revenue']:,.0f}</b> across "
        f"<b>{top_customer['Orders']}</b> orders. Offer VIP treatment.",
        "green", "⭐"
    ), unsafe_allow_html=True)

with r3c3:
    st.markdown(card(
        "Avg Order Value",
        f"${kpis['Avg Order Value']:,.2f}",
        "Consider upsell and bundle strategies to lift average order value above "
        f"${kpis['Avg Order Value']*1.15:,.0f}.",
        "", "🛒"
    ), unsafe_allow_html=True)

st.divider()
st.markdown("### 🗺️ Regional & Discount Intelligence")
r4c1, r4c2, r4c3 = st.columns(3)

with r4c1:
    st.markdown(card(
        "Top Performing Region",
        top_region["Region"],
        f"Revenue: <b>${top_region['Revenue']:,.0f}</b>. "
        f"Profit: <b>${top_region['Profit']:,.0f}</b>. "
        f"Margin: <b>{top_region['Profit']/top_region['Revenue']*100:.1f}%</b>.",
        "green", "🌟"
    ), unsafe_allow_html=True)

with r4c2:
    st.markdown(card(
        "Growth Opportunity Region",
        low_region["Region"],
        f"Lowest revenue region at <b>${low_region['Revenue']:,.0f}</b>. "
        "Targeted campaigns or distribution expansion recommended.",
        "amber", "📍"
    ), unsafe_allow_html=True)

with r4c3:
    color = "red" if heavy_disc_profit < 0 else "amber"
    st.markdown(card(
        "Heavy Discount Impact",
        f"{heavy_disc_pct:.1f}% of revenue",
        f"Orders with ≥30% discount represent <b>{heavy_disc_pct:.1f}%</b> of revenue "
        f"but generate <b>${heavy_disc_profit:,.0f}</b> in profit. "
        + ("Heavy discounting is hurting profitability." if heavy_disc_profit < 0
           else "Discount strategy is marginally profitable."),
        color, "🏷️"
    ), unsafe_allow_html=True)

st.divider()

# ── Summary scorecard ─────────────────────────────────────────────────────────
st.markdown("### 📋 Executive Summary")
summary_items = [
    ("Revenue", f"${kpis['Total Revenue']:,.0f}", "green"),
    ("Profit Margin", f"{kpis['Profit Margin %']:.1f}%", "green" if kpis["Profit Margin %"] > 10 else "amber"),
    ("MoM Growth", f"{last_growth:+.1f}%", "green" if last_growth >= 0 else "red"),
    ("Retention Rate", f"{repeat_pct:.1f}%", "green" if repeat_pct > 40 else "amber"),
    ("Loss Products", str(loss_count), "green" if loss_count == 0 else "red"),
    ("Top Region", top_region["Region"], "green"),
]

cols = st.columns(6)
for col, (label, val, color) in zip(cols, summary_items):
    bg = {"green": "#064E3B", "amber": "#78350F", "red": "#7F1D1D"}.get(color, "#1E293B")
    col.markdown(f"""
    <div style="background:{bg};border-radius:10px;padding:14px;text-align:center;">
        <div style="font-size:11px;color:#94A3B8;font-weight:700;text-transform:uppercase;">{label}</div>
        <div style="font-size:22px;font-weight:700;color:#F1F5F9;margin-top:4px;">{val}</div>
    </div>""", unsafe_allow_html=True)

# ── Download filtered data ────────────────────────────────────────────────────
st.divider()
st.download_button(
    label="⬇️ Download Filtered Dataset (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_data_export.csv",
    mime="text/csv",
)
