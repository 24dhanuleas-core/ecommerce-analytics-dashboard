"""
Page 3 — Product Analysis
Top/bottom products, categories, subcategories, treemap.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.metrics import top_products, bottom_products
from utils.charts  import horizontal_bar, donut, treemap, LAYOUT_DEFAULTS, PALETTE

st.set_page_config(page_title="Product Analysis", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0F172A;}
.insight-card{background:#1E293B;border-left:4px solid #2563EB;border-radius:8px;padding:14px 18px;margin:6px 0;}
.insight-card.green{border-left-color:#10B981;}.insight-card.red{border-left-color:#EF4444;}
.insight-title{font-size:12px;font-weight:700;color:#94A3B8;text-transform:uppercase;}
.insight-body{font-size:15px;color:#F1F5F9;margin-top:4px;}
</style>""", unsafe_allow_html=True)

df = st.session_state.get("df_filtered")
if df is None or df.empty:
    st.warning("No data. Return to Home page.")
    st.stop()

st.markdown("## 📦 Product Analysis")

n = st.slider("Number of products to display", 5, 30, 10)

# ── Top & Bottom ──────────────────────────────────────────────────────────────
top_df  = top_products(df, n)
bot_df  = bottom_products(df, n)

c1, c2 = st.columns(2)
with c1:
    st.markdown(f"### 🏆 Top {n} Products by Revenue")
    fig = horizontal_bar(top_df, x="Revenue", y="Product Name",
                         title=f"Top {n} Products")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown(f"### ⬇️ Bottom {n} Products by Revenue")
    fig2 = horizontal_bar(bot_df, x="Revenue", y="Product Name",
                          title=f"Bottom {n} Products", color="#EF4444")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Category bar ─────────────────────────────────────────────────────────────
st.markdown("### 🗂️ Revenue by Category & Subcategory")
cat_df = df.groupby("Category", as_index=False).agg(
    Revenue=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum"))

sub_df = df.groupby(["Category","Sub Category"], as_index=False).agg(
    Revenue=("Sales","sum"), Profit=("Profit","sum"))

c3, c4 = st.columns(2)
with c3:
    fig_cat = px.bar(cat_df, x="Category", y="Revenue",
                     color="Category", color_discrete_sequence=PALETTE,
                     title="Revenue by Category", text_auto=".2s")
    fig_cat.update_layout(**LAYOUT_DEFAULTS)
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    fig_sub = px.bar(sub_df, x="Sub Category", y="Revenue",
                     color="Category", color_discrete_sequence=PALETTE,
                     title="Revenue by Sub-Category", text_auto=".2s")
    fig_sub.update_layout(**LAYOUT_DEFAULTS, xaxis_tickangle=-35)
    st.plotly_chart(fig_sub, use_container_width=True)

st.divider()

# ── Treemap ───────────────────────────────────────────────────────────────────
st.markdown("### 🌳 Product Treemap")
treemap_df = df.groupby(["Category","Sub Category","Product Name"], as_index=False).agg(
    Revenue=("Sales","sum"))
fig_tm = treemap(treemap_df, path=["Category","Sub Category","Product Name"],
                 values="Revenue", title="Revenue Treemap — Category → Subcategory → Product")
st.plotly_chart(fig_tm, use_container_width=True)

st.divider()

# ── Pie ───────────────────────────────────────────────────────────────────────
c5, c6 = st.columns(2)
with c5:
    fig_pie_cat = donut(cat_df, names="Category", values="Revenue",
                        title="Revenue Share by Category")
    st.plotly_chart(fig_pie_cat, use_container_width=True)
with c6:
    fig_pie_sub = donut(sub_df, names="Sub Category", values="Revenue",
                        title="Revenue Share by Sub-Category")
    st.plotly_chart(fig_pie_sub, use_container_width=True)

st.divider()

# ── Insights ──────────────────────────────────────────────────────────────────
st.markdown("### 💡 Insights")
best_cat    = cat_df.sort_values("Revenue", ascending=False).iloc[0]
best_prod   = top_df.iloc[0]
worst_prod  = bot_df.iloc[0]
best_sub    = sub_df.sort_values("Revenue", ascending=False).iloc[0]

def ins(title, body, color=""):
    st.markdown(f'<div class="insight-card {color}"><div class="insight-title">{title}</div>'
                f'<div class="insight-body">{body}</div></div>', unsafe_allow_html=True)

c7, c8 = st.columns(2)
with c7:
    ins("Best Category",  f"<b>{best_cat['Category']}</b> leads with <b>${best_cat['Revenue']:,.0f}</b> revenue.", "green")
    ins("Best Product",   f"<b>{best_prod['Product Name']}</b> — <b>${best_prod['Revenue']:,.0f}</b>.", "green")
with c8:
    ins("Top Sub-Category", f"<b>{best_sub['Sub Category']}</b> ({best_sub['Category']}) — <b>${best_sub['Revenue']:,.0f}</b>.")
    ins("Lowest Revenue Product", f"<b>{worst_prod['Product Name']}</b> — only <b>${worst_prod['Revenue']:,.0f}</b>. Consider review.", "red")
