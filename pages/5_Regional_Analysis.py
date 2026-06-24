"""
Page 5 — Regional Analysis
Choropleth map, state/city rankings, regional heatmap.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.metrics import state_revenue, region_revenue
from utils.charts  import choropleth_us, horizontal_bar, heatmap, LAYOUT_DEFAULTS, PALETTE

st.set_page_config(page_title="Regional Analysis", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.amber{border-left-color:#F59E0B;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Return to Home page.")
    st.stop()

st.markdown("## 🗺️ Regional Analysis")

# ── Choropleth ────────────────────────────────────────────────────────────────
state_df = state_revenue(df)

metric_choice = st.radio("Map metric", ["Revenue","Profit","Orders"], horizontal=True)
fig_map = choropleth_us(state_df, state_col="State", value_col=metric_choice,
                         title=f"US State {metric_choice}")
st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# ── State & Region bars ───────────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🏙️ Top States by Revenue")
    fig_state = horizontal_bar(state_df.head(15), x="Revenue", y="State",
                               title="Top 15 States — Revenue")
    st.plotly_chart(fig_state, use_container_width=True)
with c2:
    st.markdown("### 🌍 Revenue by Region")
    reg_df = region_revenue(df)
    fig_reg = px.bar(reg_df, x="Region", y="Revenue",
                     color="Region", color_discrete_sequence=PALETTE,
                     title="Revenue by Region", text_auto=".2s")
    fig_reg.update_layout(**LAYOUT_DEFAULTS)
    st.plotly_chart(fig_reg, use_container_width=True)

st.divider()

# ── City ranking ──────────────────────────────────────────────────────────────
st.markdown("### 🏙️ Top Cities by Revenue")
order_col = next(
    (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
    None
)

city_df = (
    df.groupby("City", as_index=False)
      .agg(
          Revenue=("Sales", "sum"),
          Profit=("Profit", "sum"),
          Orders=(order_col, "nunique") if order_col else ("Sales", "count")
      )
)

fig_city = horizontal_bar(city_df, x="Revenue", y="City",
                           title="Top 20 Cities — Revenue")
st.plotly_chart(fig_city, use_container_width=True)

st.divider()

# ── Region × Category heatmap ─────────────────────────────────────────────────
st.markdown("### 🔥 Revenue Heatmap — Region × Category")
pivot = df.pivot_table(values="Sales", index="Region",
                       columns="Category", aggfunc="sum", fill_value=0)
fig_hm = heatmap(pivot, "Revenue Heatmap: Region × Category")
st.plotly_chart(fig_hm, use_container_width=True)

st.divider()

# ── Profitability by region ───────────────────────────────────────────────────
st.markdown("### 💰 Regional Profitability")
reg_prof = reg_df.copy()
reg_prof["Margin %"] = (reg_prof["Profit"] / reg_prof["Revenue"] * 100).round(2)

fig_prof = go.Figure()
fig_prof.add_trace(go.Bar(x=reg_prof["Region"], y=reg_prof["Revenue"],
                           name="Revenue", marker_color="#2563EB"))
fig_prof.add_trace(go.Bar(x=reg_prof["Region"], y=reg_prof["Profit"],
                           name="Profit", marker_color="#10B981"))
fig_prof.update_layout(barmode="group", title="Revenue vs Profit by Region", **LAYOUT_DEFAULTS)
st.plotly_chart(fig_prof, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Insights")
top_state  = state_df.iloc[0]
top_region = reg_df.iloc[0]
top_city   = city_df.iloc[0]

def ins(title, body, color=""):
    st.markdown(f'<div class="insight-card {color}"><div class="insight-title">{title}</div>'
                f'<div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

ca, cb = st.columns(2)
with ca:
    ins("Top State",  f"<b>{top_state['State']}</b> generates <b>${top_state['Revenue']:,.0f}</b> in revenue.", "green")
    ins("Top Region", f"<b>{top_region['Region']}</b> is the highest-performing region with <b>${top_region['Revenue']:,.0f}</b>.")
with cb:
    ins(
    "Top City",
    f"<b>{top_city['City']}</b> leads city-level revenue at <b>${top_city['Revenue']:,.0f}</b>.",
    "green"
)
    low_region = reg_df.iloc[-1]
    ins("Growth Opportunity",
        f"<b>{low_region['Region']}</b> has the lowest revenue (<b>${low_region['Revenue']:,.0f}</b>). Consider targeted campaigns.")
