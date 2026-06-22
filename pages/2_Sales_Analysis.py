"""
Page 2 — Sales Analysis
Daily, weekly, monthly, quarterly, yearly trends + simple forecasting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from utils.charts import revenue_trend, grouped_bar, multi_line, LAYOUT_DEFAULTS, BLUE, GREEN, AMBER

st.set_page_config(page_title="Sales Analysis", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.amber{border-left-color:#F59E0B;}
.insight-card.red{border-left-color:#EF4444;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data available. Return to Home page.")
    st.stop()

st.markdown("## 📅 Sales Analysis")

granularity = st.radio(
    "Time Granularity",
    ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
    horizontal=True,
)

# ── Aggregate ─────────────────────────────────────────────────────────────────
def aggregate(df: pd.DataFrame, gran: str) -> pd.DataFrame:
    if gran == "Daily":
        grp = df.groupby("Order Date").agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")).reset_index()
        grp.rename(columns={"Order Date":"Period"}, inplace=True)
        grp["Period"] = grp["Period"].astype(str)
    elif gran == "Weekly":
        df2 = df.copy(); df2["Period"] = df2["Order Date"].dt.strftime("%Y-W%U")
        grp = df2.groupby("Period").agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")).reset_index()
    elif gran == "Monthly":
        grp = df.groupby("YearMonth").agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")).reset_index()
        grp.rename(columns={"YearMonth":"Period"}, inplace=True)
    elif gran == "Quarterly":
        df2 = df.copy(); df2["Period"] = df2["Year"].astype(str) + "-" + df2["Quarter"]
        grp = df2.groupby("Period").agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")).reset_index()
    else:  # Yearly
        df2 = df.copy(); df2["Period"] = df2["Year"].astype(str)
        grp = df2.groupby("Period").agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique")).reset_index()
    grp = grp.sort_values("Period")
    grp["Growth %"] = grp["Revenue"].pct_change().mul(100).round(2)
    return grp

agg_df = aggregate(df, granularity)

# ── Revenue + Growth rate chart ────────────────────────────────────────────────
fig = go.Figure()
fig.add_trace(go.Bar(x=agg_df["Period"], y=agg_df["Revenue"],
                     name="Revenue", marker_color=BLUE, opacity=0.85))
fig.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Growth %"],
                          name="Growth %", yaxis="y2",
                          line=dict(color=AMBER, width=2), mode="lines+markers"))
fig.update_layout(
    yaxis=dict(title="Revenue ($)"),
    yaxis2=dict(title="Growth %", overlaying="y", side="right", zeroline=True,
                zerolinecolor="rgba(200,200,200,0.3)"),
    title=f"{granularity} Revenue with Growth Rate",
    **LAYOUT_DEFAULTS,
)
st.plotly_chart(fig, use_container_width=True)

# ── Revenue vs Profit ─────────────────────────────────────────────────────────
fig2 = multi_line(agg_df, x="Period", ys=["Revenue","Profit"],
                  title=f"{granularity} Revenue vs Profit")
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Forecasting section ────────────────────────────────────────────────────────
st.markdown("### 🔮 Revenue Forecasting (Linear Trend)")
if granularity == "Monthly" and len(agg_df) >= 6:
    n_forecast = st.slider("Months to forecast", 1, 12, 3)
    x_vals = np.arange(len(agg_df))
    y_vals = agg_df["Revenue"].values
    coeffs = np.polyfit(x_vals, y_vals, 1)
    poly   = np.poly1d(coeffs)

    x_fc   = np.arange(len(agg_df), len(agg_df) + n_forecast)
    y_fc   = poly(x_fc)

    # Build period labels for forecast
    last_period = pd.Period(agg_df["Period"].iloc[-1], freq="M")
    fc_periods  = [(last_period + i + 1).strftime("%Y-%m") for i in range(n_forecast)]

    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(x=agg_df["Period"], y=agg_df["Revenue"],
                                mode="lines+markers", name="Actual", line=dict(color=BLUE)))
    fig_fc.add_trace(go.Scatter(x=fc_periods, y=y_fc,
                                mode="lines+markers", name="Forecast",
                                line=dict(color=AMBER, dash="dot")))
    fig_fc.update_layout(title="Revenue Forecast", **LAYOUT_DEFAULTS)
    st.plotly_chart(fig_fc, use_container_width=True)
else:
    st.info("Switch to **Monthly** granularity with at least 6 data points to enable forecasting.")

st.divider()

# ── Day-of-week heatmap ────────────────────────────────────────────────────────
st.markdown("### 📅 Revenue Heatmap by Day of Week × Month")
df2 = df.copy()
df2["Month Name"] = df2["Order Date"].dt.strftime("%b")
df2["Month Num"]  = df2["Order Date"].dt.month
pivot = df2.groupby(["Day of Week","Month Name"])["Sales"].sum().unstack(fill_value=0)
month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
day_order   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
pivot = pivot.reindex(index=[d for d in day_order if d in pivot.index],
                      columns=[m for m in month_order if m in pivot.columns])

fig_hm = go.Figure(go.Heatmap(
    z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
    colorscale="Blues", hoverongaps=False,
))
fig_hm.update_layout(title="Revenue by Day of Week & Month", **LAYOUT_DEFAULTS)
st.plotly_chart(fig_hm, use_container_width=True)

# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Insights")
best_period = agg_df.loc[agg_df["Revenue"].idxmax(), "Period"]
best_rev    = agg_df["Revenue"].max()
avg_rev     = agg_df["Revenue"].mean()
positive_growth = (agg_df["Growth %"].dropna() > 0).sum()
total_periods   = len(agg_df["Growth %"].dropna())

def ins(title, body, color=""):
    st.markdown(f'<div class="insight-card {color}"><div class="insight-title">{title}</div>'
                f'<div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

ins("Peak Period",
    f"Highest revenue in <b>{best_period}</b>: <b>${best_rev:,.0f}</b>.")
ins("Consistency",
    f"<b>{positive_growth}/{total_periods}</b> periods showed positive growth "
    f"({positive_growth/total_periods*100:.0f}%).",
    "green" if positive_growth/total_periods > 0.5 else "amber")
ins("Average Revenue",
    f"Average {granularity.lower()} revenue: <b>${avg_rev:,.0f}</b>.")
