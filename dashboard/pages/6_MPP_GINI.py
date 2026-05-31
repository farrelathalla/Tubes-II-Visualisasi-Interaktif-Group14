import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path: allow `from utils.xxx import ...` without installing as package
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------
# 1. Page config, MUST be the first Streamlit call
# ---------------------------------------------------------------------------
import streamlit as st

st.set_page_config(
    page_title="Distribusi MPP | Ketahanan Pangan",
    page_icon="🔗",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Imports
# ---------------------------------------------------------------------------
from utils.data_loader import load_mpp, load_ikp, load_produksi, get_mpp_trend, get_available_years
from utils.charts import make_mpp_scatter, make_mpp_bar
from utils import colors
from utils.colors import get_province_island

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats

# ---------------------------------------------------------------------------
# 4. Load data & compute correlation (2024 baseline)
# ---------------------------------------------------------------------------
df_mpp = load_mpp()
df_ikp = load_ikp()
df_prod = load_produksi()

mpp_2024 = df_mpp[df_mpp.TAHUN == 2024][["PROVINSI", "MPP_TOTAL_PCT", "JUMLAH_RANTAI"]].copy()
ikp_2024 = df_ikp[df_ikp.TAHUN == 2024][["PROVINSI", "IKP", "KODE_PROV"]].copy()

df_merged = mpp_2024.merge(ikp_2024, on="PROVINSI", how="inner")
df_merged = df_merged.merge(df_prod, on="PROVINSI", how="left")

# Add island column
df_merged["ISLAND"] = df_merged["PROVINSI"].apply(get_province_island).fillna("Lainnya")

# Compute Pearson correlation
_valid = df_merged[["MPP_TOTAL_PCT", "IKP"]].dropna()
r, p_val = stats.pearsonr(_valid["MPP_TOTAL_PCT"], _valid["IKP"])

# ---------------------------------------------------------------------------
# 5. Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='color:#065f46; font-weight:700; font-size:16px; letter-spacing:1px;'>Distribusi MPP</div>
      <div style='color:#6f7973; font-size:12px;'>Margin Perdagangan & Pengangkutan</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:0.7rem; color:rgba(255,255,255,0.5); text-transform:uppercase;
                letter-spacing:0.07em; margin-bottom:4px;'>Konten</div>
    <div style='font-size:0.82rem; color:rgba(255,255,255,0.85); line-height:2;'>
      Hubungan MPP vs IKP<br>
      MPP Per Provinsi<br>
      Tren MPP Multi-Tahun
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:10px 0;'>
    """, unsafe_allow_html=True)

    # Page-specific filters
    st.markdown("---")
    st.markdown("**Filter MPP**")
    selected_island = st.selectbox("Pulau/Wilayah", ["Semua"] + list(colors.ISLAND_GROUPS.keys()))
    mpp_year = st.selectbox("Tahun MPP", [2019, 2020, 2021, 2024], index=3)
    show_regression = st.checkbox("Tampilkan Regresi Linear", value=True)
    highlight_threshold = st.slider("Highlight MPP > (%)", min_value=10, max_value=30, value=20)

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
# 6. Section 1: Headline card
# ---------------------------------------------------------------------------
_corr_color = "c53030" if r < -0.3 else "d4a520"
_corr_label = "negatif" if r < 0 else "positif"

st.markdown(f"""
<div class='headline-card'>
  <h1 style='color:#065f46; margin:0;'>Ketimpangan Distribusi Beras</h1>
  <p style='color:#181c1a; margin:4px 0 2px;'>
    Margin Perdagangan &amp; Pengangkutan (MPP) berkorelasi
    <b style='color:#{_corr_color};'>{_corr_label} (r = {r:.3f})</b>
    dengan IKP, provinsi dengan margin distribusi tinggi cenderung memiliki ketahanan pangan lebih rendah.
  </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. Section 2: KPI metrics (4 columns)
# ---------------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

avg_mpp = df_merged["MPP_TOTAL_PCT"].mean()
n_high_mpp = int((df_merged["MPP_TOTAL_PCT"] > highlight_threshold).sum())
avg_chains = df_merged["JUMLAH_RANTAI"].mean()

with col1:
    st.metric("Rata-rata MPP Nasional", f"{avg_mpp:.1f}%")
with col2:
    st.metric(f"Provinsi MPP > {highlight_threshold}%", f"{n_high_mpp} provinsi")
with col3:
    st.metric("Korelasi MPP–IKP", f"r = {r:.3f}", "negatif = buruk" if r < 0 else "positif",
              delta_color="inverse")
with col4:
    st.metric("Rata-rata Rantai Distribusi", f"{avg_chains:.1f} rantai")

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. Section 3: Scatter plot MPP vs IKP (full width)
# ---------------------------------------------------------------------------
if selected_island != "Semua":
    df_scatter = df_merged[df_merged["ISLAND"] == selected_island].copy()
else:
    df_scatter = df_merged.copy()

st.markdown(
    "<h3 style='color:#004532; font-size:1rem; font-weight:700; letter-spacing:0.04em; "
    "text-transform:uppercase; margin-bottom:8px;'>Hubungan MPP vs IKP</h3>",
    unsafe_allow_html=True,
)

fig_scatter = make_mpp_scatter(df_scatter, show_regression=show_regression)
st.plotly_chart(fig_scatter, width="stretch", height=480)

st.caption(
    f"Ukuran titik = volume produksi padi. Data MPP 2024, IKP 2024. "
    f"r² = {r**2:.3f}, p = {p_val:.4f}"
)

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 9. Section 4: Two-column, MPP bar + MPP trend
# ---------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### MPP per Provinsi ({mpp_year})")
    df_mpp_year = df_mpp[df_mpp.TAHUN == mpp_year].copy()
    if selected_island != "Semua":
        island_provs = colors.ISLAND_GROUPS.get(selected_island, [])
        df_mpp_year = df_mpp_year[df_mpp_year.PROVINSI.isin(island_provs)]
    fig_bar = make_mpp_bar(df_mpp_year, year=mpp_year)
    st.plotly_chart(fig_bar, width="stretch", height=450)

with col2:
    st.markdown("#### Tren MPP Multi-Tahun")

    # Allow province selection for trend
    all_mpp_provs = sorted(df_mpp["PROVINSI"].unique().tolist())
    trend_provinces = st.multiselect(
        "Pilih Provinsi untuk Tren",
        all_mpp_provs,
        default=["PAPUA", "PAPUA BARAT", "NUSA TENGGARA TIMUR", "JAWA TENGAH", "KALIMANTAN SELATAN"],
        key="mpp_trend_select",
    )

    # Build multi-year trend line chart
    df_mpp_trend = df_mpp[df_mpp.PROVINSI.isin(trend_provinces)].copy()

    fig_trend = go.Figure()
    palette = colors.CLUSTER_COLORS + ["#ffffff", "#aaaaaa", "#ffaaaa"]

    for i, prov in enumerate(trend_provinces):
        df_p = df_mpp_trend[df_mpp_trend.PROVINSI == prov].sort_values("TAHUN")
        color = palette[i % len(palette)]
        fig_trend.add_trace(go.Scatter(
            x=df_p["TAHUN"].astype(str),
            y=df_p["MPP_TOTAL_PCT"],
            mode="lines+markers",
            name=prov,
            line=dict(color=color, width=2),
            marker=dict(size=8),
            hovertemplate=f"<b>{prov}</b><br>Tahun: %{{x}}<br>MPP: %{{y:.1f}}%<extra></extra>",
        ))

    # Add threshold line
    fig_trend.add_hline(
        y=highlight_threshold,
        line_dash="dash",
        line_color=colors.ACCENT_RED,
        annotation_text=f"Threshold {highlight_threshold}%",
        annotation_font_color=colors.ACCENT_RED,
    )

    fig_trend.update_layout(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f7faf6",
        font=dict(color=colors.TEXT_PRIMARY),
        xaxis=dict(gridcolor=colors.BORDER_CARD, tickfont=dict(color=colors.TEXT_MUTED)),
        yaxis=dict(
            gridcolor=colors.BORDER_CARD,
            tickfont=dict(color=colors.TEXT_MUTED),
            title="MPP Total (%)",
        ),
        legend=dict(bgcolor=colors.BG_PANEL, bordercolor=colors.BORDER_CARD, borderwidth=1),
        margin=dict(l=40, r=200, t=30, b=40),
        hoverlabel=dict(
            bgcolor=colors.BG_PANEL,
            bordercolor=colors.BORDER_CARD,
            font=dict(color=colors.TEXT_PRIMARY),
        ),
    )

    st.plotly_chart(fig_trend, width="stretch", height=450)

# ---------------------------------------------------------------------------
# 11. Footer
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
