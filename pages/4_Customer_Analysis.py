"""
Page 4 — Customer Analysis
Segmentation, CLV, repeat customers, downloadable table.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.metrics import customer_summary
from utils.charts  import horizontal_bar, LAYOUT_DEFAULTS, PALETTE, BLUE, GREEN, AMBER

st.set_page_config(page_title="Customer Analysis", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.kpi-card{background:linear-gradient(135deg,#1E293B 0%,#0F172A 100%);border:1px solid #334155;
          border-radius:12px;padding:20px 24px;margin-bottom:8px;}
.kpi-label{font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:.05em;}
.kpi-value{font-size:28px;font-weight:700;color:#F1F5F9;margin:4px 0;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Return to Home page.")
    st.stop()

st.markdown("## 👥 Customer Analysis")

cust_df = customer_summary(df)

total_customers  = len(cust_df)
repeat_customers = (cust_df["Orders"] > 1).sum()
new_customers    = total_customers - repeat_customers
avg_clv          = cust_df["Revenue"].mean()

# ── KPI row ───────────────────────────────────────────────────────────────────
def kpi_card(label, val):
    return (f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div></div>')

c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi_card("Total Customers",   f"{total_customers:,}"),   unsafe_allow_html=True)
c2.markdown(kpi_card("Repeat Customers",  f"{repeat_customers:,}"),  unsafe_allow_html=True)
c3.markdown(kpi_card("New Customers",     f"{new_customers:,}"),     unsafe_allow_html=True)
c4.markdown(kpi_card("Avg Revenue / Customer", f"${avg_clv:,.0f}"), unsafe_allow_html=True)

st.divider()

# ── Top customers bar ─────────────────────────────────────────────────────────
n = st.slider("Top N customers", 5, 30, 10)
top_cust = cust_df.head(n)

c5, c6 = st.columns(2)
with c5:
    fig_tc = horizontal_bar(top_cust, x="Revenue", y="Customer Name",
                            title=f"Top {n} Customers by Revenue")
    st.plotly_chart(fig_tc, use_container_width=True)
with c6:
    fig_clv = horizontal_bar(
        top_cust,
        x="CLV",
        y="Customer Name",
        title=f"Top {n} Customers by Lifetime Value",
        color=GREEN
    )
    st.plotly_chart(fig_clv, use_container_width=True)
st.divider()

# ── Revenue distribution ──────────────────────────────────────────────────────
st.markdown("### 📊 Revenue Distribution per Customer")
fig_hist = px.histogram(cust_df, x="Revenue", nbins=50,
                        color_discrete_sequence=[BLUE], title="Customer Revenue Distribution")
fig_hist.update_layout(**LAYOUT_DEFAULTS)
st.plotly_chart(fig_hist, use_container_width=True)

# ── Order frequency ───────────────────────────────────────────────────────────
st.markdown("### 🔄 Order Frequency Distribution")
freq_counts = cust_df["Orders"].value_counts().reset_index()
freq_counts.columns = ["Orders", "Customers"]
fig_freq = px.bar(freq_counts.sort_values("Orders"), x="Orders", y="Customers",
                  color_discrete_sequence=[AMBER], title="Customers by Number of Orders")
fig_freq.update_layout(**LAYOUT_DEFAULTS)
st.plotly_chart(fig_freq, use_container_width=True)

# ── Segmentation ─────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🎯 Customer Segmentation (RFM-Lite)")

# Simple segmentation based on revenue quantiles
q33 = cust_df["Revenue"].quantile(0.33)
q66 = cust_df["Revenue"].quantile(0.66)

def segment(row):
    if row["Revenue"] >= q66:
        return "High Value"
    elif row["Revenue"] >= q33:
        return "Mid Value"
    else:
        return "Low Value"

cust_df["Segment"] = cust_df.apply(segment, axis=1)
seg_counts = cust_df["Segment"].value_counts().reset_index()
seg_counts.columns = ["Segment","Count"]

seg_colors = {"High Value": "#10B981", "Mid Value": AMBER, "Low Value": "#EF4444"}
fig_seg = px.pie(seg_counts, names="Segment", values="Count", hole=0.4,
                 color="Segment", color_discrete_map=seg_colors,
                 title="Customer Segments")
fig_seg.update_layout(**LAYOUT_DEFAULTS)
st.plotly_chart(fig_seg, use_container_width=True)

# ── Full ranking table ────────────────────────────────────────────────────────
st.divider()
st.markdown("### 📋 Customer Ranking Table")

display_df = cust_df[["Customer Name","Revenue","Profit","Orders","Avg Order Value","Segment"]].copy()
display_df["Revenue"]        = display_df["Revenue"].map("${:,.2f}".format)
display_df["Profit"]         = display_df["Profit"].map("${:,.2f}".format)
display_df["Avg Order Value"]= display_df["Avg Order Value"].map("${:,.2f}".format)

st.dataframe(display_df, use_container_width=True, height=400)

# ── CSV Export ────────────────────────────────────────────────────────────────
st.download_button(
    label="⬇️ Download Customer Report (CSV)",
    data=cust_df.to_csv(index=False).encode("utf-8"),
    file_name="customer_analysis.csv",
    mime="text/csv",
)

# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Insights")
top_c = cust_df.iloc[0]
repeat_pct = repeat_customers / total_customers * 100
high_val_pct = (cust_df["Segment"] == "High Value").sum() / total_customers * 100

def ins(title, body, color=""):
    st.markdown(f'<div class="insight-card {color}"><div class="insight-title">{title}</div>'
                f'<div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

ca, cb = st.columns(2)
with ca:
    ins("Top Customer", f"<b>{top_c['Customer Name']}</b> generated <b>${top_c['Revenue']:,.0f}</b> in lifetime value.", "green")
    ins("Repeat Rate",  f"<b>{repeat_pct:.1f}%</b> of customers placed more than one order.")
with cb:
    ins("High-Value Segment", f"<b>{high_val_pct:.1f}%</b> of customers fall in the High Value tier.")
    ins("Acquisition Gap",    f"<b>{new_customers:,}</b> single-order customers represent retention opportunity.", "green")
