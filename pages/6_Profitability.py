"""
Page 6 — Profitability Analysis
Margins, discount impact, loss-makers, scatter/box plots.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.charts import scatter, box_plot, horizontal_bar, heatmap, LAYOUT_DEFAULTS, PALETTE, RED, GREEN, AMBER, BLUE

st.set_page_config(page_title="Profitability", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.red{border-left-color:#EF4444;}.insight-card.amber{border-left-color:#F59E0B;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Return to Home page.")
    st.stop()

st.markdown("## 💰 Profitability Analysis")

# ── Category / Subcategory profitability ──────────────────────────────────────
cat_prof = (df.groupby("Category", as_index=False)
              .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"))
              .assign(**{"Margin %": lambda x: (x["Profit"]/x["Revenue"]*100).round(2)})
              .sort_values("Profit", ascending=False))

sub_prof = (df.groupby(["Category","Sub Category"], as_index=False)
              .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"))
              .assign(**{"Margin %": lambda x: (x["Profit"]/x["Revenue"]*100).round(2)})
              .sort_values("Profit", ascending=False))

c1, c2 = st.columns(2)
with c1:
    fig_cat = px.bar(cat_prof, x="Category", y=["Revenue","Profit"],
                     barmode="group", color_discrete_sequence=[BLUE, GREEN],
                     title="Revenue vs Profit by Category")
    fig_cat.update_layout(**LAYOUT_DEFAULTS)
    st.plotly_chart(fig_cat, use_container_width=True)

with c2:
    fig_margin = px.bar(cat_prof, x="Category", y="Margin %",
                        color="Margin %", color_continuous_scale="RdYlGn",
                        title="Profit Margin % by Category")
    fig_margin.update_layout(**LAYOUT_DEFAULTS)
    st.plotly_chart(fig_margin, use_container_width=True)

st.divider()

# ── Subcategory margin ────────────────────────────────────────────────────────
st.markdown("### 📊 Subcategory Profitability")
fig_sub = px.bar(sub_prof, x="Sub Category", y="Margin %",
                 color="Category", color_discrete_sequence=PALETTE,
                 title="Profit Margin % by Subcategory", text_auto=".1f")
fig_sub.add_hline(y=0, line_dash="dash", line_color=RED, annotation_text="Break-even")
fig_sub.update_layout(**LAYOUT_DEFAULTS, xaxis_tickangle=-35)
st.plotly_chart(fig_sub, use_container_width=True)

st.divider()

# ── Discount impact ───────────────────────────────────────────────────────────
st.markdown("### 🏷️ Discount Impact on Profit Margin")
disc_bins = [0, 0.01, 0.1, 0.2, 0.3, 0.5, 1.0]
disc_labels = ["0%", "1-10%", "10-20%", "20-30%", "30-50%", "50%+"]
df_disc = df.copy()
df_disc["Discount Tier"] = pd.cut(df_disc["Discount"], bins=disc_bins,
                                   labels=disc_labels, include_lowest=True)
disc_agg = (df_disc.groupby("Discount Tier", as_index=False, observed=True)
            order_col = next(
    (c for c in df.columns if c.strip().lower() in ["order id", "order_id"]),
    None
)

.agg(
    Revenue=("Sales", "sum"),
    Profit=("Profit", "sum"),
    Orders=(order_col, "nunique") if order_col else ("Sales", "count")
)

              .assign(**{"Margin %": lambda x: (x["Profit"]/x["Revenue"]*100).round(2)}))

fig_disc = px.bar(disc_agg, x="Discount Tier", y="Margin %",
                  color="Margin %", color_continuous_scale="RdYlGn",
                  title="Profit Margin % by Discount Tier", text_auto=".1f")
fig_disc.add_hline(y=0, line_dash="dash", line_color=RED)
fig_disc.update_layout(**LAYOUT_DEFAULTS)
st.plotly_chart(fig_disc, use_container_width=True)

# ── Scatter: Sales vs Profit ──────────────────────────────────────────────────
st.divider()
st.markdown("### 🔵 Sales vs Profit (by Category)")
prod_agg = (df.groupby(["Product Name","Category"], as_index=False)
              .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum")))

fig_sc = scatter(prod_agg, x="Revenue", y="Profit", color="Category",
                 size="Quantity", title="Sales vs Profit — Product Level")
fig_sc.add_hline(y=0, line_dash="dash", line_color=RED,
                 annotation_text="Break-even", annotation_position="bottom right")
st.plotly_chart(fig_sc, use_container_width=True)

# ── Box plot: Profit margin distribution ──────────────────────────────────────
st.divider()
st.markdown("### 📦 Profit Margin Distribution by Category")
fig_box = box_plot(df, x="Category", y="Profit Margin %",
                   title="Profit Margin % Distribution by Category")
st.plotly_chart(fig_box, use_container_width=True)

# ── Loss-making products ──────────────────────────────────────────────────────
st.divider()
st.markdown("### ⚠️ Loss-Making Products")
prod_loss = (df.groupby(["Product Name","Category"], as_index=False)
               .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
               .query("Profit < 0")
               .sort_values("Profit"))

if prod_loss.empty:
    st.success("No loss-making products in the current selection.")
else:
    st.error(f"**{len(prod_loss)} products** are generating a loss.")
    prod_loss_disp = prod_loss.copy()
    prod_loss_disp["Revenue"] = prod_loss_disp["Revenue"].map("${:,.2f}".format)
    prod_loss_disp["Profit"]  = prod_loss_disp["Profit"].map("${:,.2f}".format)
    st.dataframe(prod_loss_disp, use_container_width=True)
    fig_loss = horizontal_bar(prod_loss.head(10), x="Profit", y="Product Name",
                               title="Top 10 Loss-Making Products", color=RED)
    st.plotly_chart(fig_loss, use_container_width=True)

# ── State profitability heatmap ───────────────────────────────────────────────
st.divider()
st.markdown("### 🔥 Profitability Heatmap — State × Category")
try:
    pivot = df.pivot_table(values="Profit Margin %", index="State",
                           columns="Category", aggfunc="mean", fill_value=0).round(1)
    pivot = pivot.head(20)  # top 20 states for readability
    fig_hm = heatmap(pivot, "Avg Profit Margin % — Top 20 States × Category")
    st.plotly_chart(fig_hm, use_container_width=True)
except Exception:
    pass

# ── Insights ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 💡 Insights")

best_margin_cat = cat_prof.sort_values("Margin %", ascending=False).iloc[0]
worst_margin_cat = cat_prof.sort_values("Margin %").iloc[0]
high_disc_margin = disc_agg.sort_values("Discount Tier").iloc[-1]["Margin %"]

def ins(title, body, color=""):
    st.markdown(f'<div class="insight-card {color}"><div class="insight-title">{title}</div>'
                f'<div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

ca, cb = st.columns(2)
with ca:
    ins("Best Margin Category",  f"<b>{best_margin_cat['Category']}</b> has the highest margin at <b>{best_margin_cat['Margin %']:.1f}%</b>.", "green")
    ins("Loss-Making Products",  f"<b>{len(prod_loss)}</b> products are currently generating losses.", "red" if len(prod_loss) > 0 else "green")
with cb:
    ins("Worst Margin Category", f"<b>{worst_margin_cat['Category']}</b> has the lowest margin at <b>{worst_margin_cat['Margin %']:.1f}%</b>.", "amber")
    ins("Discount Risk",         f"Orders with 50%+ discounts yield a margin of <b>{high_disc_margin:.1f}%</b>. Review heavy discounting.", "red" if high_disc_margin < 0 else "amber")
