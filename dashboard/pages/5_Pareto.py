import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page config, MUST be the first Streamlit call
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
      <div style='color:#065f46; font-weight:700; font-size:16px; letter-spacing:1px;'>Analisis Pareto</div>
      <div style='color:#6f7973; font-size:12px;'>Prioritas 80/20</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:0.7rem; color:rgba(255,255,255,0.5); text-transform:uppercase;
                letter-spacing:0.07em; margin-bottom:4px;'>Konten</div>
    <div style='font-size:0.82rem; color:rgba(255,255,255,0.85); line-height:2;'>
      Distribusi Kategori Ketahanan<br>
      Pareto Chart IKP Defisit<br>
      Tren Konsumsi Pangan Indonesia
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:10px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Filter Pareto**")
    _years = get_available_years()
    selected_year = st.selectbox("Tahun", _years, index=len(_years) - 2)
    pareto_threshold = st.slider(
        "Threshold Kumulatif (%)", min_value=60, max_value=95, value=80, step=5
    )
    show_by = st.radio("Tampilkan berdasarkan", ["Skor IKP (terendah)", "Defisit IKP"])

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15); margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#6f7973; line-height:1.6;'>
    <b style='color:#6f7973;'>IF4061 Visualisasi Data</b><br>
    Semester 2 2025/2026<br>
    Group 14<br><br>
    Sumber: BPS, Badan Pangan Nasional
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. Load & prepare Pareto data
# ---------------------------------------------------------------------------
df_year = get_ikp_for_year(selected_year)

MAX_IKP = 100.0
df_pareto = df_year.copy()
df_pareto["DEFICIT"] = MAX_IKP - df_pareto["IKP"]

# Sort based on user selection
if show_by == "Skor IKP (terendah)":
    df_pareto = df_pareto.sort_values("IKP", ascending=True).reset_index(drop=True)
else:  # "Defisit IKP"
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
headline_text = (
    f"<b style='color:#904d00;'>{n_80pct} provinsi ({pct_provinces:.0f}%)</b> dari total {n_total} provinsi "
    f"menyumbang <b style='color:#be123c;'>80% dari total defisit ketahanan pangan</b> pada {selected_year}."
)

if show_by == "Skor IKP (terendah)":
    headline_title = "Prioritas: Provinsi dengan Skor IKP Terendah"
    headline_context = "Intervensi pada provinsi dengan skor IKP paling rendah dapat memberikan dampak terbesar untuk meningkatkan ketahanan pangan."
else:
    headline_title = "Prioritas: Provinsi dengan Defisit Ketahanan Pangan"
    headline_context = "Intervensi tepat sasaran pada kelompok ini dapat memberikan dampak terbesar untuk mengatasi kekurangan ketahanan pangan."

st.markdown(f"""
<div class='headline-card'>
  <h1 style='color:#065f46; margin:0;'>{headline_title}</h1>
  <p style='color:#181c1a; margin:4px 0 2px;'>{headline_text}</p>
  <p style='color:#6f7973; margin:4px 0; font-size:0.95rem;'>{headline_context}</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. Section 3: Top row, KPI + priority list | Donut chart
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    fig_donut = make_donut_kerentanan(df_year)
    st.plotly_chart(fig_donut, width="stretch", height=390)

with col2:
    kpi_label = (
        "Provinsi dengan IKP Terendah" if show_by == "Skor IKP (terendah)"
        else "Provinsi Perlu Prioritas"
    )
    st.markdown(f"""
    <div class='kpi-card danger'>
      <div style='font-size:12px; color:#6f7973;'>{kpi_label} ({pareto_threshold}% threshold)</div>
      <div style='font-size:36px; font-weight:700; color:#904d00;'>{n_threshold} Provinsi</div>
      <div style='font-size:13px; color:#181c1a;'>dari total {n_total} provinsi ({n_threshold / n_total * 100:.0f}%)</div>
    </div>
    """, unsafe_allow_html=True)

    # Build priority province list
    priority_provs = df_pareto[df_pareto["CUM_PCT"] <= pareto_threshold]["PROVINSI"].tolist()
    # Ensure we include the province that crosses the threshold
    if len(priority_provs) < n_threshold and len(priority_provs) < n_total:
        priority_provs.append(df_pareto["PROVINSI"].iloc[len(priority_provs)])

    items_html = ""
    for i, prov in enumerate(priority_provs[:10], 1):
        mask = df_pareto["PROVINSI"] == prov
        ikp_val = float(df_pareto.loc[mask, "IKP"].values[0]) if mask.any() else 0.0
        items_html += (
            f"<div style='display:grid; grid-template-columns:28px 1fr; align-items:baseline;"
            f" padding:3px 0; border-bottom:1px solid #f1f4f0;'>"
            f"<span style='color:#be123c; font-weight:700; text-align:right; padding-right:6px;'>{i}.</span>"
            f"<span style='color:#181c1a; font-size:0.86rem;'>{prov.title()}"
            f" <span style='color:#6f7973;'>IKP:</span>"
            f" <b style='color:#904d00;'>{ikp_val:.1f}</b></span>"
            f"</div>"
        )
    st.markdown(
        f"<div style='margin-top:10px;'>"
        f"<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase;"
        f" letter-spacing:0.05em; color:#6f7973; margin-bottom:6px;'>Provinsi Prioritas</div>"
        f"{items_html}</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 8. Section 4: Full-width Pareto chart
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"#### Pareto Chart: IKP {show_by} per Provinsi ({selected_year})")

fig_pareto = make_pareto_chart(df_pareto, show_by=show_by)
st.plotly_chart(fig_pareto, width="stretch", height=500)

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
    st.plotly_chart(fig_kons, width="stretch", height=380)

# ---------------------------------------------------------------------------
# 10. Footer
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='
    border-top: 1px solid #e2e8f0;
    padding-top: 16px;
    text-align: center;
    color: #6f7973;
    font-size: 0.78rem;
    line-height: 1.8;
'>
  <span style='color:#6f7973; font-weight:600;'>Sumber Data:</span>
  Badan Pusat Statistik (BPS) &nbsp;·&nbsp;
  Badan Pangan Nasional (NFA) &nbsp;·&nbsp;
  Panel Harga Pangan Kementerian Pertanian<br>
  IF4061 Visualisasi Data,
  Institut Teknologi Bandung, Semester 2 2025/2026.
</div>
""", unsafe_allow_html=True)
