"""
Reusable Plotly chart factory functions.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Theme constants ────────────────────────────────────────────────────────────

PALETTE = px.colors.qualitative.Set2
BLUE    = "#2563EB"
GREEN   = "#10B981"
RED     = "#EF4444"
AMBER   = "#F59E0B"
GRAY    = "#6B7280"
BG      = "rgba(0,0,0,0)"          # transparent → respects Streamlit theme

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif", size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(orientation="h", y=-0.2),
    hoverlabel=dict(bgcolor="#1E293B", font_color="white"),
)


def _apply(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(title=title, **LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(100,100,100,0.15)", zeroline=False)
    return fig


# ── KPI sparkline ─────────────────────────────────────────────────────────────

def sparkline(series: pd.Series, color: str = BLUE) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=list(range(len(series))), y=series.values,
        mode="lines", line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba"),
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False, height=60,
    )
    return fig


# ── Line / area charts ────────────────────────────────────────────────────────

def revenue_trend(df: pd.DataFrame, x: str, y: str = "Revenue",
                  title: str = "Revenue Trend") -> go.Figure:
    fig = px.area(df, x=x, y=y, color_discrete_sequence=[BLUE], title=title)
    fig.update_traces(line_width=2)
    return _apply(fig)


def multi_line(df: pd.DataFrame, x: str, ys: list[str], title: str) -> go.Figure:
    colors = [BLUE, GREEN, AMBER, RED]
    fig = go.Figure()
    for i, col in enumerate(ys):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], name=col,
            mode="lines+markers", line=dict(color=colors[i % len(colors)], width=2),
        ))
    return _apply(fig, title)


# ── Bar charts ────────────────────────────────────────────────────────────────

def horizontal_bar(df: pd.DataFrame, x: str, y: str, title: str,
                   color: str = BLUE) -> go.Figure:
    fig = px.bar(df, x=x, y=y, orientation="h", color_discrete_sequence=[color], title=title)
    fig.update_layout(yaxis=dict(categoryorder="total ascending"))
    return _apply(fig)


def grouped_bar(df: pd.DataFrame, x: str, ys: list[str], title: str) -> go.Figure:
    colors = [BLUE, GREEN, AMBER]
    fig = go.Figure()
    for i, col in enumerate(ys):
        fig.add_trace(go.Bar(name=col, x=df[x], y=df[col],
                             marker_color=colors[i % len(colors)]))
    fig.update_layout(barmode="group")
    return _apply(fig, title)


# ── Pie / donut ───────────────────────────────────────────────────────────────

def donut(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(df, names=names, values=values, hole=0.45,
                 color_discrete_sequence=PALETTE, title=title)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply(fig)


# ── Treemap ───────────────────────────────────────────────────────────────────

def treemap(df: pd.DataFrame, path: list[str], values: str, title: str) -> go.Figure:
    fig = px.treemap(df, path=path, values=values,
                     color=values, color_continuous_scale="Blues",
                     title=title)
    return _apply(fig)


# ── Scatter ───────────────────────────────────────────────────────────────────

def scatter(df: pd.DataFrame, x: str, y: str, color: str | None,
            size: str | None, title: str) -> go.Figure:
    fig = px.scatter(df, x=x, y=y, color=color, size=size,
                     color_discrete_sequence=PALETTE,
                     hover_data=df.columns.tolist(),
                     title=title, opacity=0.75)
    return _apply(fig)


# ── Choropleth (US states) ────────────────────────────────────────────────────

# Map full state names to abbreviations
_STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY", "District of Columbia": "DC",
}


def choropleth_us(df: pd.DataFrame, state_col: str, value_col: str,
                  title: str) -> go.Figure:
    tmp = df.copy()
    tmp["State Code"] = tmp[state_col].map(_STATE_ABBR)
    tmp = tmp.dropna(subset=["State Code"])

    fig = px.choropleth(
        tmp, locations="State Code", locationmode="USA-states",
        color=value_col, scope="usa",
        color_continuous_scale="Blues", title=title,
        hover_name=state_col, hover_data={value_col: True, "State Code": False},
    )
    fig.update_layout(
        geo=dict(bgcolor=BG, lakecolor=BG, landcolor="rgba(30,41,59,0.6)"),
        **LAYOUT_DEFAULTS,
    )
    return fig


# ── Heatmap ───────────────────────────────────────────────────────────────────

def heatmap(matrix: pd.DataFrame, title: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=matrix.values, x=matrix.columns.tolist(),
        y=matrix.index.tolist(),
        colorscale="Blues", showscale=True,
        hoverongaps=False,
    ))
    return _apply(fig, title)


# ── Box plot ──────────────────────────────────────────────────────────────────

def box_plot(df: pd.DataFrame, x: str, y: str, title: str) -> go.Figure:
    fig = px.box(df, x=x, y=y, color=x, color_discrete_sequence=PALETTE,
                 title=title, points="outliers")
    return _apply(fig)


# ── Funnel chart ──────────────────────────────────────────────────────────────

def funnel(labels: list, values: list, title: str) -> go.Figure:
    fig = go.Figure(go.Funnel(
        y=labels, x=values,
        marker=dict(color=PALETTE[:len(labels)]),
        textinfo="value+percent total",
    ))
    return _apply(fig, title)
