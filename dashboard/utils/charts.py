"""
Reusable Plotly chart factory functions for the Indonesian Food Security Dashboard.
Every function returns a go.Figure with the dark theme applied.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import colors

# ---------------------------------------------------------------------------
# Extended cycling palette (CLUSTER_COLORS + extras for multi-series charts)
# ---------------------------------------------------------------------------
_PALETTE: list[str] = colors.CLUSTER_COLORS + [
    "#4ac9b0",  # teal
    "#e05c9a",  # pink
    "#a0c040",  # lime
    "#60a8e0",  # sky blue
    "#e0b060",  # amber
    "#8060e0",  # indigo
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _empty_fig(message: str = "No data available") -> go.Figure:
    """Return a blank figure with a centred 'No data' annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(color=colors.TEXT_MUTED, size=16),
    )
    return _apply_theme(fig)


def _apply_theme(fig: go.Figure, margin: dict | None = None) -> go.Figure:
    """Apply light theme layout to any figure."""
    fig.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f7faf6",
        font=dict(color=colors.TEXT_PRIMARY, family="Plus Jakarta Sans, Segoe UI, sans-serif"),
        legend=dict(
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            borderwidth=1,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        margin=margin if margin is not None else dict(l=64, r=60, t=72, b=52),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
    )
    fig.update_xaxes(
        gridcolor=colors.BORDER_CARD,
        zerolinecolor=colors.BORDER_CARD,
        color=colors.TEXT_PRIMARY,
        tickfont=dict(color=colors.TEXT_PRIMARY),
        title_font=dict(color=colors.TEXT_PRIMARY),
        linecolor=colors.TEXT_DIM,
    )
    fig.update_yaxes(
        gridcolor=colors.BORDER_CARD,
        zerolinecolor=colors.BORDER_CARD,
        color=colors.TEXT_PRIMARY,
        tickfont=dict(color=colors.TEXT_PRIMARY),
        title_font=dict(color=colors.TEXT_PRIMARY),
        linecolor=colors.TEXT_DIM,
    )
    return fig


# ---------------------------------------------------------------------------
# 1. Choropleth map
# ---------------------------------------------------------------------------

def make_choropleth(df_ikp: pd.DataFrame, geojson: dict, title: str = "") -> go.Figure:
    """Mapbox choropleth of IKP by province."""
    if df_ikp is None or df_ikp.empty:
        return _empty_fig("No IKP data available")

    fig = px.choropleth_mapbox(
        df_ikp,
        geojson=geojson,
        locations="KODE_PROV",
        featureidkey="properties.kode",
        color="IKP",
        color_continuous_scale=colors.IKP_COLORSCALE,
        range_color=[30, 90],
        mapbox_style="carto-darkmatter",
        center={"lat": -2, "lon": 118},
        zoom=3.8,
        custom_data=["PROVINSI", "PERINGKAT", "KERENTANAN"],
        title=title,
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "IKP: %{z:.2f}<br>"
            "Rank: %{customdata[1]}<br>"
            "Kategori: %{customdata[2]}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        paper_bgcolor="#ffffff",
        font=dict(color=colors.TEXT_PRIMARY, family="Plus Jakarta Sans, Segoe UI, sans-serif"),
        margin=dict(l=15, r=150, t=20, b=20),
        coloraxis_colorbar=dict(
            tickfont=dict(color=colors.TEXT_MUTED),
            title=dict(font=dict(color=colors.TEXT_MUTED), text="IKP"),
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# 2. Top / Bottom bar chart
# ---------------------------------------------------------------------------

def make_bar_top_bottom(
    df_ikp: pd.DataFrame, top: bool = True, n: int = 10
) -> go.Figure:
    """Horizontal bar chart of top-n or bottom-n provinces by IKP."""
    if df_ikp is None or df_ikp.empty:
        return _empty_fig("No IKP data available")

    if top:
        df_plot = df_ikp.nlargest(n, "IKP").sort_values("IKP", ascending=True)
        bar_color = colors.ACCENT_GOLD
        title = f"Top {n} Provinsi IKP Tertinggi"
    else:
        df_plot = df_ikp.nsmallest(n, "IKP").sort_values("IKP", ascending=False)
        bar_color = colors.ACCENT_RED
        title = f"{n} Provinsi IKP Terendah"

    fig = go.Figure(
        go.Bar(
            x=df_plot["IKP"],
            y=df_plot["PROVINSI"],
            orientation="h",
            marker_color=bar_color,
            text=df_plot["IKP"].map(lambda v: f"{v:.1f}"),
            textposition="outside",
            textfont=dict(color=colors.TEXT_PRIMARY),
            customdata=df_plot[["PROVINSI", "IKP", "PERINGKAT"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "IKP: %{customdata[1]:.2f}<br>"
                "Peringkat: %{customdata[2]}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(color=colors.TEXT_PRIMARY)),
        xaxis_title="IKP",
        showlegend=False,
    )
    return _apply_theme(fig, margin=dict(l=64, r=60, t=72, b=52))


# ---------------------------------------------------------------------------
# 3. Multi-line rice price chart
# ---------------------------------------------------------------------------

def make_line_harga(
    df_harga: pd.DataFrame,
    selected_provinces: list[str],
    year_range: tuple[int, int] | None = None,
) -> go.Figure:
    """Multi-line chart of rice prices per province over time."""
    if df_harga is None or df_harga.empty or not selected_provinces:
        return _empty_fig("No price data available")

    df = df_harga.copy()
    df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce")

    if year_range is not None:
        start_year, end_year = year_range
        df = df[
            (df["TANGGAL"].dt.year >= start_year)
            & (df["TANGGAL"].dt.year <= end_year)
        ]

    df = df[df["PROVINSI"].isin(selected_provinces)]

    if df.empty:
        return _empty_fig("No data for selected provinces / date range")

    fig = go.Figure()
    for i, province in enumerate(selected_provinces):
        prov_df = df[df["PROVINSI"] == province].sort_values("TANGGAL")
        if prov_df.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=prov_df["TANGGAL"],
                y=prov_df["HARGA_BERAS"],
                mode="lines",
                name=province,
                line=dict(color=_PALETTE[i % len(_PALETTE)], width=2),
                hovertemplate=(
                    f"<b>{province}</b><br>"
                    "Tanggal: %{x|%Y-%m-%d}<br>"
                    "Harga: Rp %{y:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=dict(
            text="Harga Beras per Provinsi",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title="Tanggal",
        yaxis_title="Harga Beras (Rp)",
        hovermode="x unified",
    )
    fig.update_xaxes(rangeslider_visible=False)
    return _apply_theme(fig, margin=dict(l=64, r=170, t=72, b=52))


# ---------------------------------------------------------------------------
# 4. Slope graph
# ---------------------------------------------------------------------------

def make_slopegraph(
    df_harga: pd.DataFrame,
    provinces: list[str],
    year_start: int = 2019,
    year_end: int = 2025,
) -> go.Figure:
    """Two-column slope graph comparing avg rice price between two years."""
    if df_harga is None or df_harga.empty or not provinces:
        return _empty_fig("No data for slope graph")

    df = df_harga.copy()
    df["TANGGAL"] = pd.to_datetime(df["TANGGAL"], errors="coerce")
    df["YEAR"] = df["TANGGAL"].dt.year
    df = df[df["PROVINSI"].isin(provinces)]

    avg = (
        df[df["YEAR"].isin([year_start, year_end])]
        .groupby(["PROVINSI", "YEAR"])["HARGA_BERAS"]
        .mean()
        .reset_index()
    )

    fig = go.Figure()
    x_labels = [str(year_start), str(year_end)]

    for idx, province in enumerate(provinces):
        p_start = avg[(avg["PROVINSI"] == province) & (avg["YEAR"] == year_start)]
        p_end = avg[(avg["PROVINSI"] == province) & (avg["YEAR"] == year_end)]

        if p_start.empty or p_end.empty:
            continue

        val_start = p_start["HARGA_BERAS"].iloc[0]
        val_end = p_end["HARGA_BERAS"].iloc[0]

        pct_change = (val_end - val_start) / val_start if val_start != 0 else 0
        line_color = _PALETTE[idx % len(_PALETTE)]

        fig.add_trace(
            go.Scatter(
                x=x_labels,
                y=[val_start, val_end],
                mode="lines+markers",
                name=province,
                line=dict(color=line_color, width=2),
                marker=dict(size=8, color=line_color),
                hovertemplate=(
                    f"<b>{province}</b><br>"
                    "Tahun: %{x}<br>"
                    "Harga: Rp %{y:,.0f}<br>"
                    f"Perubahan: {pct_change:+.1%}"
                    "<extra></extra>"
                ),
                showlegend=True,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"Perubahan Harga Beras {year_start} → {year_end}",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis=dict(
            tickvals=x_labels,
            ticktext=x_labels,
        ),
        yaxis_title="Rata-rata Harga Beras (Rp)",
        legend=dict(
            orientation="v",
            x=1.02,
            xanchor="left",
            y=1,
            yanchor="top",
            font=dict(size=11),
        ),
    )
    return _apply_theme(fig, margin=dict(l=64, r=160, t=72, b=52))


# ---------------------------------------------------------------------------
# 5. Elbow & Silhouette charts
# ---------------------------------------------------------------------------

def make_elbow_silhouette(
    inertias: list[float],
    silhouettes: list[float],
    k_range: list[int],
) -> tuple[go.Figure, go.Figure]:
    """Return (elbow_fig, silhouette_fig) for K-means evaluation."""
    if not inertias or not silhouettes or not k_range:
        empty = _empty_fig("No clustering data available")
        return empty, empty

    # --- Elbow chart ---
    inertias_arr = np.array(inertias, dtype=float)
    elbow_k = k_range[0]
    if len(inertias_arr) >= 3:
        second_deriv = np.diff(inertias_arr, n=2)
        elbow_idx = int(np.argmax(second_deriv)) + 1  # offset for double diff
        elbow_k = k_range[elbow_idx] if elbow_idx < len(k_range) else k_range[0]

    elbow_fig = go.Figure()
    elbow_fig.add_trace(
        go.Scatter(
            x=k_range,
            y=inertias,
            mode="lines+markers",
            line=dict(color=colors.ACCENT_GREEN, width=2),
            marker=dict(size=8, color=colors.ACCENT_GREEN),
            name="Inertia",
            hovertemplate="K=%{x}<br>Inertia=%{y:,.1f}<extra></extra>",
        )
    )
    elbow_fig.add_annotation(
        x=elbow_k,
        y=inertias[k_range.index(elbow_k)],
        text=f"Elbow K={elbow_k}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=colors.ACCENT_GOLD,
        font=dict(color=colors.ACCENT_GOLD),
        ax=30, ay=-30,
    )
    elbow_fig.update_layout(
        title=dict(text="Elbow Method", font=dict(color=colors.TEXT_PRIMARY)),
        xaxis_title="Jumlah Cluster (K)",
        yaxis_title="Inertia",
    )
    _apply_theme(elbow_fig, margin=dict(l=64, r=44, t=72, b=52))

    # --- Silhouette chart ---
    best_k_idx = int(np.argmax(silhouettes))
    best_k = k_range[best_k_idx]
    bar_colors = [
        colors.ACCENT_GOLD if k == best_k else colors.ACCENT_GREEN
        for k in k_range
    ]

    sil_fig = go.Figure()
    sil_fig.add_trace(
        go.Bar(
            x=k_range,
            y=silhouettes,
            marker_color=bar_colors,
            name="Silhouette",
            hovertemplate="K=%{x}<br>Silhouette=%{y:.4f}<extra></extra>",
        )
    )
    sil_fig.add_annotation(
        x=best_k,
        y=silhouettes[best_k_idx],
        text=f"Best K={best_k}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=colors.ACCENT_GOLD,
        font=dict(color=colors.ACCENT_GOLD),
        ax=30, ay=-30,
    )
    sil_fig.update_layout(
        title=dict(text="Silhouette Score", font=dict(color=colors.TEXT_PRIMARY)),
        xaxis_title="Jumlah Cluster (K)",
        yaxis_title="Silhouette Score",
    )
    _apply_theme(sil_fig, margin=dict(l=64, r=44, t=72, b=52))

    return elbow_fig, sil_fig


# ---------------------------------------------------------------------------
# 6. Cluster scatter plot
# ---------------------------------------------------------------------------

def make_cluster_scatter(
    df_clustered: pd.DataFrame,
    x_col: str,
    y_col: str,
    cluster_col: str = "CLUSTER",
) -> go.Figure:
    """Scatter plot coloured by cluster."""
    if df_clustered is None or df_clustered.empty:
        return _empty_fig("No cluster data available")

    fig = go.Figure()
    clusters = sorted(df_clustered[cluster_col].unique())

    hover_cols = [c for c in df_clustered.columns if c not in [x_col, y_col]]

    for i, cluster_id in enumerate(clusters):
        mask = df_clustered[cluster_col] == cluster_id
        sub = df_clustered[mask]

        # Build hover text
        hover_parts = ["<b>%{customdata[0]}</b>"] if "PROVINSI" in hover_cols else []
        hover_parts += [
            f"{col}: %{{customdata[{idx + (1 if 'PROVINSI' in hover_cols else 0)}]}}"
            for idx, col in enumerate(
                [c for c in hover_cols if c != "PROVINSI" and c != cluster_col]
            )
        ]
        hover_template = "<br>".join(hover_parts) + "<extra></extra>"

        custom_cols = (
            ["PROVINSI"] if "PROVINSI" in hover_cols else []
        ) + [c for c in hover_cols if c != "PROVINSI" and c != cluster_col]
        customdata = sub[custom_cols].values if custom_cols else None

        fig.add_trace(
            go.Scatter(
                x=sub[x_col],
                y=sub[y_col],
                mode="markers",
                name=f"Cluster {cluster_id}",
                marker=dict(
                    color=colors.CLUSTER_COLORS[i % len(colors.CLUSTER_COLORS)],
                    size=10,
                    opacity=0.85,
                    line=dict(color=colors.BG_MAIN, width=1),
                ),
                customdata=customdata,
                hovertemplate=hover_template,
            )
        )

    fig.update_layout(
        title=dict(
            text=f"Cluster Scatter: {x_col} vs {y_col}",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title=x_col,
        yaxis_title=y_col,
    )
    return _apply_theme(fig, margin=dict(l=64, r=180, t=72, b=52))


# ---------------------------------------------------------------------------
# 7. ARIMA forecast chart
# ---------------------------------------------------------------------------

def make_arima_forecast(
    df_historical: pd.DataFrame,
    df_forecast: pd.DataFrame,
    df_ci: pd.DataFrame,
    province_name: str,
) -> go.Figure:
    """Line chart with historical data, ARIMA forecast, and confidence interval."""
    if df_historical is None or df_historical.empty:
        return _empty_fig("No historical data available")

    df_hist = df_historical.copy()
    df_hist["TANGGAL"] = pd.to_datetime(df_hist["TANGGAL"], errors="coerce")
    df_hist = df_hist.sort_values("TANGGAL")

    fig = go.Figure()

    # Historical
    fig.add_trace(
        go.Scatter(
            x=df_hist["TANGGAL"],
            y=df_hist["HARGA_BERAS"],
            mode="lines",
            name="Historis",
            line=dict(color=colors.TEXT_PRIMARY, width=2),
            hovertemplate="Historis: Rp %{y:,.0f}<extra></extra>",
        )
    )

    if df_forecast is not None and not df_forecast.empty:
        df_fc = df_forecast.copy()
        df_fc["TANGGAL"] = pd.to_datetime(df_fc["TANGGAL"], errors="coerce")
        df_fc = df_fc.sort_values("TANGGAL")

        # Confidence interval shading (lower bound, invisible)
        if df_ci is not None and not df_ci.empty:
            df_ci_plot = df_ci.copy()
            df_ci_plot["TANGGAL"] = pd.to_datetime(
                df_ci_plot["TANGGAL"], errors="coerce"
            )
            df_ci_plot = df_ci_plot.sort_values("TANGGAL")

            fig.add_trace(
                go.Scatter(
                    x=df_ci_plot["TANGGAL"],
                    y=df_ci_plot["CI_LOWER"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                    name="CI Lower",
                )
            )
            # Upper bound with fill
            gold_rgba = "rgba(212, 165, 32, 0.15)"
            fig.add_trace(
                go.Scatter(
                    x=df_ci_plot["TANGGAL"],
                    y=df_ci_plot["CI_UPPER"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=gold_rgba,
                    showlegend=True,
                    name="95% CI",
                    hoverinfo="skip",
                )
            )

        # Forecast line
        fig.add_trace(
            go.Scatter(
                x=df_fc["TANGGAL"],
                y=df_fc["FORECAST"],
                mode="lines",
                name="Proyeksi",
                line=dict(color=colors.ACCENT_GOLD, width=2, dash="dash"),
                hovertemplate="Proyeksi: Rp %{y:,.0f}<extra></extra>",
            )
        )

        # Vertical boundary line
        boundary = df_hist["TANGGAL"].max()
        fig.add_vline(
            x=boundary,
            line_dash="dot",
            line_color=colors.TEXT_MUTED,
            line_width=1.5,
        )
        fig.add_annotation(
            x=boundary,
            y=1,
            yref="paper",
            text="Proyeksi ARIMA",
            showarrow=False,
            font=dict(color=colors.ACCENT_GOLD, size=11),
            xanchor="left",
            xshift=6,
        )

    fig.update_layout(
        title=dict(
            text=f"Proyeksi Harga Beras – {province_name}",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title="Tanggal",
        yaxis_title="Harga Beras (Rp)",
    )
    return _apply_theme(fig, margin=dict(l=64, r=150, t=72, b=52))


# ---------------------------------------------------------------------------
# 8. Pareto chart
# ---------------------------------------------------------------------------

def make_pareto_chart(df_ikp_sorted: pd.DataFrame) -> go.Figure:
    """Bar chart of IKP with cumulative deficit line (Pareto)."""
    if df_ikp_sorted is None or df_ikp_sorted.empty:
        return _empty_fig("No IKP data available")

    df = df_ikp_sorted.copy().reset_index(drop=True)
    max_ikp = df["IKP"].max()
    df["DEFICIT"] = max_ikp - df["IKP"]
    total_deficit = df["DEFICIT"].sum()
    df["CUM_PCT"] = (df["DEFICIT"].cumsum() / total_deficit * 100) if total_deficit > 0 else 0

    # Number of provinces that account for 80% of deficit
    threshold_count = int((df["CUM_PCT"] <= 80).sum()) + 1
    threshold_count = min(threshold_count, len(df))

    # Bar colors: red (low IKP) → green (high IKP)
    n = len(df)
    bar_colors = [
        f"rgb({int(197*(1-i/(n-1)) + 122*(i/(n-1)))}, "
        f"{int(48*(1-i/(n-1)) + 181*(i/(n-1)))}, "
        f"{int(48*(1-i/(n-1)) + 40*(i/(n-1)))})"
        for i in range(n)
    ] if n > 1 else [colors.ACCENT_GREEN]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["PROVINSI"],
            y=df["IKP"],
            name="IKP",
            marker_color=bar_colors,
            hovertemplate="<b>%{x}</b><br>IKP: %{y:.2f}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["PROVINSI"],
            y=df["CUM_PCT"],
            mode="lines+markers",
            name="Kumulatif Defisit (%)",
            line=dict(color=colors.ACCENT_GOLD, width=2),
            marker=dict(size=6, color=colors.ACCENT_GOLD),
            hovertemplate="%{x}<br>Kumulatif: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    # 80% threshold vertical line
    if threshold_count <= len(df):
        x_thresh = df["PROVINSI"].iloc[threshold_count - 1]
        fig.add_vline(
            x=x_thresh,
            line_dash="dash",
            line_color=colors.ACCENT_RED,
            line_width=1.5,
        )
        fig.add_annotation(
            x=x_thresh,
            y=1,
            yref="paper",
            text=f"{threshold_count} prov = 80% defisit",
            showarrow=False,
            font=dict(color=colors.ACCENT_RED, size=11),
            xanchor="right",
            xshift=-6,
        )

    fig.update_layout(
        title=dict(
            text="Analisis Pareto – Defisit IKP",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f7faf6",
        font=dict(color=colors.TEXT_PRIMARY, family="Plus Jakarta Sans, Segoe UI, sans-serif"),
        legend=dict(
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            borderwidth=1,
            font=dict(color=colors.TEXT_MUTED),
        ),
        margin=dict(l=64, r=220, t=72, b=120),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=colors.BORDER_CARD,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis=dict(
            tickangle=-45,
            color=colors.TEXT_PRIMARY,
            tickfont=dict(color=colors.TEXT_PRIMARY, size=11),
            title=dict(font=dict(color=colors.TEXT_PRIMARY, size=13)),
            linecolor=colors.TEXT_PRIMARY,
        ),
    )
    fig.update_yaxes(
        title_text="IKP",
        gridcolor=colors.BORDER_CARD,
        zerolinecolor=colors.BORDER_CARD,
        color=colors.TEXT_PRIMARY,
        tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
        title_font=dict(color=colors.TEXT_PRIMARY, size=13),
        linecolor=colors.TEXT_PRIMARY,
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Kumulatif Defisit (%)",
        range=[0, 105],
        gridcolor="rgba(0,0,0,0)",
        color=colors.TEXT_PRIMARY,
        tickfont=dict(color=colors.TEXT_PRIMARY, size=12),
        title_font=dict(color=colors.TEXT_PRIMARY, size=13),
        linecolor=colors.TEXT_PRIMARY,
        secondary_y=True,
    )
    return fig


# ---------------------------------------------------------------------------
# 9. Donut chart – vulnerability categories
# ---------------------------------------------------------------------------

def make_donut_kerentanan(df_ikp: pd.DataFrame) -> go.Figure:
    """Donut chart showing province count per KERENTANAN category."""
    if df_ikp is None or df_ikp.empty:
        return _empty_fig("No vulnerability data available")

    counts = df_ikp["KERENTANAN"].value_counts().reset_index()
    counts.columns = ["KERENTANAN", "JUMLAH"]

    cat_colors = [
        colors.KERENTANAN_COLORS.get(cat, colors.TEXT_MUTED)
        for cat in counts["KERENTANAN"]
    ]

    total = counts["JUMLAH"].sum()
    fig = go.Figure(
        go.Pie(
            labels=counts["KERENTANAN"],
            values=counts["JUMLAH"],
            hole=0.5,
            marker=dict(colors=cat_colors, line=dict(color=colors.BG_MAIN, width=2)),
            textfont=dict(color=colors.TEXT_PRIMARY),
            customdata=counts[["JUMLAH"]].values,
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Jumlah: %{customdata[0]} provinsi<br>"
                "Persentase: %{percent}"
                "<extra></extra>"
            ),
        )
    )
    fig.add_annotation(
        text=f"<b>{total}</b><br>Provinsi",
        x=0.5, y=0.5,
        font=dict(color=colors.TEXT_PRIMARY, size=16),
        showarrow=False,
    )
    fig.update_layout(
        title=dict(
            text="Distribusi Kategori Kerentanan Pangan",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
    )
    return _apply_theme(fig, margin=dict(l=40, r=170, t=72, b=40))


# ---------------------------------------------------------------------------
# 10. Stacked area – food consumption
# ---------------------------------------------------------------------------

def make_konsumsi_area(
    df_konsumsi: pd.DataFrame,
    selected_groups: list[str] | None = None,
) -> go.Figure:
    """Stacked area chart of food consumption by group over years."""
    if df_konsumsi is None or df_konsumsi.empty:
        return _empty_fig("No consumption data available")

    df = df_konsumsi.copy()
    if selected_groups:
        df = df[df["KELOMPOK"].isin(selected_groups)]

    if df.empty:
        return _empty_fig("No data for selected groups")

    groups = df["KELOMPOK"].unique()
    fig = go.Figure()

    for i, group in enumerate(groups):
        grp_df = df[df["KELOMPOK"] == group].sort_values("TAHUN")
        fig.add_trace(
            go.Scatter(
                x=grp_df["TAHUN"],
                y=grp_df["KONSUMSI"],
                name=group,
                mode="lines",
                stackgroup="one",
                line=dict(color=_PALETTE[i % len(_PALETTE)], width=1),
                fillcolor=_PALETTE[i % len(_PALETTE)],
                hovertemplate=(
                    f"<b>{group}</b><br>"
                    "Tahun: %{x}<br>"
                    "Konsumsi: %{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title=dict(
            text="Konsumsi Pangan per Kelompok",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title="Tahun",
        yaxis_title="Konsumsi",
        hovermode="x unified",
    )
    return _apply_theme(fig, margin=dict(l=64, r=200, t=72, b=52))


# ---------------------------------------------------------------------------
# 11. MPP scatter plot
# ---------------------------------------------------------------------------

def make_mpp_scatter(
    df_merged: pd.DataFrame, show_regression: bool = True
) -> go.Figure:
    """Scatter: MPP_TOTAL_PCT vs IKP, sized by production, coloured by island."""
    if df_merged is None or df_merged.empty:
        return _empty_fig("No MPP data available")

    df = df_merged.copy()

    # Scale production to marker size 5–25 px
    prod = df["PRODUKSI_TON"].fillna(0).values.astype(float)
    p_min, p_max = prod.min(), prod.max()
    if p_max > p_min:
        sizes = 5 + (prod - p_min) / (p_max - p_min) * 20
    else:
        sizes = np.full(len(prod), 12.0)

    fig = go.Figure()

    islands = df["ISLAND"].unique()
    for island in islands:
        mask = df["ISLAND"] == island
        sub = df[mask]
        sub_sizes = sizes[mask]

        fig.add_trace(
            go.Scatter(
                x=sub["MPP_TOTAL_PCT"],
                y=sub["IKP"],
                mode="markers",
                name=island,
                marker=dict(
                    color=colors.ISLAND_COLORS.get(island, colors.TEXT_MUTED),
                    size=sub_sizes,
                    opacity=0.85,
                    line=dict(color=colors.BG_MAIN, width=1),
                ),
                customdata=sub[["PROVINSI", "MPP_TOTAL_PCT", "IKP", "PRODUKSI_TON"]].values,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    "MPP: %{customdata[1]:.1f}%<br>"
                    "IKP: %{customdata[2]:.2f}<br>"
                    "Produksi: %{customdata[3]:,.0f} ton"
                    "<extra></extra>"
                ),
            )
        )

    # Linear regression line
    r2_val = None
    if show_regression and len(df) >= 2:
        x_vals = df["MPP_TOTAL_PCT"].values.astype(float)
        y_vals = df["IKP"].values.astype(float)
        valid = ~(np.isnan(x_vals) | np.isnan(y_vals))
        if valid.sum() >= 2:
            x_v, y_v = x_vals[valid], y_vals[valid]
            coeffs = np.polyfit(x_v, y_v, 1)
            x_line = np.linspace(x_v.min(), x_v.max(), 100)
            y_line = np.polyval(coeffs, x_line)
            ss_res = np.sum((y_v - np.polyval(coeffs, x_v)) ** 2)
            ss_tot = np.sum((y_v - y_v.mean()) ** 2)
            r2_val = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    name="Regresi Linear",
                    line=dict(color=colors.ACCENT_GOLD, width=2, dash="dash"),
                    hoverinfo="skip",
                )
            )
            fig.add_annotation(
                x=x_line[-1],
                y=y_line[-1],
                text=f"R² = {r2_val:.3f}",
                showarrow=False,
                font=dict(color=colors.ACCENT_GOLD, size=12),
                xanchor="left",
                xshift=6,
            )

    # Label outliers
    outliers = df[(df["MPP_TOTAL_PCT"] > 25) | (df["IKP"] < 60)]
    for _, row in outliers.iterrows():
        fig.add_annotation(
            x=row["MPP_TOTAL_PCT"],
            y=row["IKP"],
            text=row["PROVINSI"],
            showarrow=True,
            arrowhead=1,
            arrowcolor=colors.TEXT_MUTED,
            font=dict(color=colors.TEXT_MUTED, size=9),
            ax=15, ay=-15,
        )

    fig.update_layout(
        title=dict(
            text="Hubungan MPP vs IKP per Pulau",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title="MPP Total (%)",
        yaxis_title="IKP",
    )
    return _apply_theme(fig, margin=dict(l=64, r=220, t=72, b=52))


# ---------------------------------------------------------------------------
# 12. MPP horizontal bar chart
# ---------------------------------------------------------------------------

def make_mpp_bar(df_mpp: pd.DataFrame, year: int = 2024) -> go.Figure:
    """Horizontal bar chart of MPP_TOTAL_PCT per province for a given year."""
    if df_mpp is None or df_mpp.empty:
        return _empty_fig("No MPP data available")

    df = df_mpp.copy()
    if "TAHUN" in df.columns:
        df = df[df["TAHUN"] == year]

    if df.empty:
        return _empty_fig(f"No MPP data for year {year}")

    df = df.sort_values("MPP_TOTAL_PCT", ascending=False).reset_index(drop=True)

    bar_colors = [
        colors.ACCENT_RED
        if v > 20
        else (colors.ACCENT_GOLD if v >= 10 else colors.ACCENT_GREEN)
        for v in df["MPP_TOTAL_PCT"]
    ]

    fig = go.Figure(
        go.Bar(
            x=df["MPP_TOTAL_PCT"],
            y=df["PROVINSI"],
            orientation="h",
            marker_color=bar_colors,
            text=df["MPP_TOTAL_PCT"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
            textfont=dict(color=colors.TEXT_PRIMARY),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "MPP: %{x:.1f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_vline(
        x=20,
        line_dash="dash",
        line_color=colors.ACCENT_RED,
        line_width=1.5,
        annotation_text="Ambang 20%",
        annotation_font_color=colors.ACCENT_RED,
        annotation_position="top right",
    )

    fig.update_layout(
        title=dict(
            text=f"MPP Total per Provinsi ({year})",
            font=dict(color=colors.TEXT_PRIMARY),
        ),
        xaxis_title="MPP Total (%)",
        showlegend=False,
        height=max(400, len(df) * 22),
    )
    return _apply_theme(fig, margin=dict(l=64, r=60, t=72, b=52))
