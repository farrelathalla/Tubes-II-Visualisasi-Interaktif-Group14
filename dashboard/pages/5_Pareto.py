"""
dashboard/pages/5_Pareto.py — Analisis Prioritas (Pareto)
Prinsip Pareto untuk identifikasi provinsi prioritas ketahanan pangan
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page config — MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Analisis Pareto | Ketahanan Pangan",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Data imports (after sys.path is set)
# ---------------------------------------------------------------------------
from utils.data_loader import load_ikp, get_ikp_for_year, load_konsumsi, get_available_years
from utils.charts import make_pareto_chart, make_donut_kerentanan, make_konsumsi_area
from utils import colors

# ---------------------------------------------------------------------------
# 4. Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='color:#7ab528; font-weight:700; font-size:16px; letter-spacing:1px;'>KETAHANAN PANGAN</div>
      <div style='color:#a8c878; font-size:12px;'>Indonesia Dashboard</div>
    </div>
    <hr style='border-color:#2d5a2d; margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#a8c878; font-size:11px; padding: 4px 0 8px 0; "
        "text-transform:uppercase; letter-spacing:1px;'>Navigasi</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style='font-size:13px; color:#f2f7ec; line-height:2;'>
    <b>Gambaran Umum</b> — Peta IKP<br>
    <b>Klaster Wilayah</b> — K-Means<br>
    <b>Tren &amp; Gap Harga</b> — Slope<br>
    <b>Proyeksi ARIMA</b> — Forecast<br>
    <b>Analisis Pareto</b> — 80/20<br>
    <b>Distribusi MPP</b> — Ketimpangan
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#2d5a2d; margin:12px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:11px; color:#7a9060; line-height:1.6;'>
    <b style='color:#a8c878;'>IF4061 Visualisasi Data</b><br>
    Semester 2 2025/2026<br>
    VSC26101 — Group 14<br><br>
    Sumber: BPS, Badan Pangan Nasional
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Filter Pareto**")
    _years = get_available_years()
    selected_year = st.selectbox("Tahun", _years, index=len(_years) - 2)
    pareto_threshold = st.slider(
        "Threshold Kumulatif (%)", min_value=60, max_value=95, value=80, step=5
    )
    show_by = st.radio("Tampilkan berdasarkan", ["Skor IKP (terendah)", "Defisit IKP"])

# ---------------------------------------------------------------------------
# 5. Load & prepare Pareto data
# ---------------------------------------------------------------------------
df_year = get_ikp_for_year(selected_year)

MAX_IKP = 100.0
df_pareto = df_year.copy()
df_pareto["DEFICIT"] = MAX_IKP - df_pareto["IKP"]
df_pareto = df_pareto.sort_values("DEFICIT", ascending=False).reset_index(drop=True)
df_pareto["CUM_DEFICIT"] = df_pareto["DEFICIT"].cumsum()
total_deficit = df_pareto["DEFICIT"].sum()
df_pareto["CUM_PCT"] = (df_pareto["CUM_DEFICIT"] / total_deficit * 100) if total_deficit > 0 else 0.0

n_total = len(df_pareto)

# Provinces that account for 80% of deficit (fixed for headline)
n_80pct = int((df_pareto["CUM_PCT"] <= 80).sum()) + 1
n_80pct = min(n_80pct, n_total)
pct_provinces = n_80pct / n_total * 100

# Provinces that account for pareto_threshold% of deficit (variable slider)
n_threshold = int((df_pareto["CUM_PCT"] <= pareto_threshold).sum()) + 1
n_threshold = min(n_threshold, n_total)

# ---------------------------------------------------------------------------
# 6. Section 1: Headline card
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class='headline-card'>
  <h1 style='color:#7ab528; margin:0;'>Analisis Prioritas — Prinsip Pareto</h1>
  <p style='color:#e8f0e0; margin:4px 0 2px;'>
    <b style='color:#d4a520;'>{n_80pct} provinsi ({pct_provinces:.0f}%)</b> dari total {n_total} provinsi
    menyumbang <b style='color:#c53030;'>80% dari total defisit ketahanan pangan</b> pada {selected_year}.
    Intervensi tepat sasaran pada kelompok ini dapat memberikan dampak terbesar.
  </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. Section 3: Top row — KPI + priority list | Donut chart
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    <div class='kpi-card danger'>
      <div style='font-size:12px; color:#8aaa70;'>Provinsi Perlu Prioritas ({pareto_threshold}% threshold)</div>
      <div style='font-size:36px; font-weight:700; color:#d4a520;'>{n_threshold} Provinsi</div>
      <div style='font-size:13px; color:#e8f0e0;'>dari total {n_total} provinsi ({n_threshold / n_total * 100:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

    # Build priority province list
    priority_provs = df_pareto[df_pareto["CUM_PCT"] <= pareto_threshold]["PROVINSI"].tolist()
    # Ensure we include the province that crosses the threshold
    if len(priority_provs) < n_threshold and len(priority_provs) < n_total:
        priority_provs.append(df_pareto["PROVINSI"].iloc[len(priority_provs)])

    st.markdown("**Provinsi Prioritas:**")
    for i, prov in enumerate(priority_provs[:10], 1):
        mask = df_pareto["PROVINSI"] == prov
        ikp_val = float(df_pareto.loc[mask, "IKP"].values[0]) if mask.any() else 0.0
        st.markdown(
            f"<span style='color:#c53030;'>{i}.</span> {prov} — IKP: **{ikp_val:.1f}**",
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("**Distribusi Kategori Ketahanan**")
    fig_donut = make_donut_kerentanan(df_year)
    st.plotly_chart(fig_donut, use_container_width=True, height=320)

# ---------------------------------------------------------------------------
# 8. Section 4: Full-width Pareto chart
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"#### Pareto Chart: IKP Defisit per Provinsi ({selected_year})")

fig_pareto = make_pareto_chart(df_pareto)
st.plotly_chart(fig_pareto, use_container_width=True, height=500)

# ---------------------------------------------------------------------------
# 9. Section 5: Food consumption trend
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("#### Tren Konsumsi Pangan Indonesia")

df_kons = load_konsumsi()
kelompok_list = df_kons["KELOMPOK"].unique().tolist()

kons_col1, kons_col2 = st.columns([1, 3])

with kons_col1:
    selected_groups = st.multiselect(
        "Kelompok Pangan",
        kelompok_list,
        default=kelompok_list[:5],
    )
    view_mode = st.radio("Level Detail", ["Per Kelompok", "Per Komoditas"])

with kons_col2:
    if view_mode == "Per Kelompok":
        # Aggregate to group level; exclude summary rows where KOMODITAS == KELOMPOK
        df_plot = df_kons[df_kons["KOMODITAS"] != df_kons["KELOMPOK"]].copy()
        df_plot = df_plot[df_plot["KELOMPOK"].isin(selected_groups)]
        df_agg = df_plot.groupby(["TAHUN", "KELOMPOK"])["KONSUMSI"].sum().reset_index()
        df_agg.columns = ["TAHUN", "KELOMPOK", "KONSUMSI"]
        df_for_chart = df_agg
    else:
        df_for_chart = df_kons[df_kons["KELOMPOK"].isin(selected_groups)].copy()

    fig_kons = make_konsumsi_area(df_for_chart, selected_groups)
    st.plotly_chart(fig_kons, use_container_width=True, height=380)

# ---------------------------------------------------------------------------
# 10. Footer
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='
    border-top: 1px solid #2d5a2d;
    padding-top: 16px;
    text-align: center;
    color: #7a9060;
    font-size: 0.78rem;
    line-height: 1.8;
'>
  <span style='color:#a8c878; font-weight:600;'>Sumber Data:</span>
  Badan Pusat Statistik (BPS) &nbsp;·&nbsp;
  Badan Pangan Nasional (NFA) &nbsp;·&nbsp;
  Panel Harga Pangan Kementerian Pertanian<br>
  Dashboard ini dibuat untuk keperluan akademik — IF4061 Visualisasi Data,
  Institut Teknologi Bandung, Semester 2 2025/2026.
</div>
""", unsafe_allow_html=True)
