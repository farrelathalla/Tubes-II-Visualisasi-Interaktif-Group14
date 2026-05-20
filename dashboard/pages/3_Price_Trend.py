"""
dashboard/pages/3_Price_Trend.py — Tren & Gap Harga Beras
Interactive rice price trend and gap analysis across Indonesian provinces.
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import load_harga_beras, get_provinces_list
from utils.charts import make_line_harga, make_slopegraph
from utils import colors
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page config — MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Tren & Gap Harga | Ketahanan Pangan",
    page_icon="📈",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Load data
# ---------------------------------------------------------------------------
df_harga = load_harga_beras()

# ---------------------------------------------------------------------------
# 4. Dynamic headline card — Papua vs Lampung gap for 2025
# ---------------------------------------------------------------------------
papua_2025 = df_harga[
    (df_harga.PROVINSI == "PAPUA") & (df_harga.TANGGAL.dt.year == 2025)
].HARGA_BERAS.mean()

lampung_2025 = df_harga[
    (df_harga.PROVINSI == "LAMPUNG") & (df_harga.TANGGAL.dt.year == 2025)
].HARGA_BERAS.mean()

gap = papua_2025 - lampung_2025

st.markdown(f"""
<div class='headline-card'>
  <h1 style='color:#7ab528; margin:0;'>Tren & Gap Harga Beras</h1>
  <p style='color:#e8f0e0; margin:4px 0 2px;'>Papua membayar beras
    <b style='color:#c53030;'>Rp {gap:,.0f}/kg lebih mahal</b>
    dari Lampung pada 2025 — gap ini tidak pernah mengecil sejak 2019.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. Sidebar filters
# ---------------------------------------------------------------------------
all_provinces = get_provinces_list()

with st.sidebar:
    st.markdown("---")
    st.markdown("**Filter Harga Beras**")

    default_provs = ["PAPUA", "PAPUA BARAT", "MALUKU", "LAMPUNG", "JAWA TENGAH", "DKI JAKARTA"]
    default_provs = [p for p in default_provs if p in all_provinces]

    selected_provinces = st.multiselect(
        "Pilih Provinsi",
        options=all_provinces,
        default=default_provs,
    )

    year_range = st.slider(
        "Rentang Tahun",
        min_value=2019,
        max_value=2025,
        value=(2019, 2025),
    )

# ---------------------------------------------------------------------------
# 6. Main line chart (full width)
# ---------------------------------------------------------------------------
if selected_provinces:
    fig_line = make_line_harga(df_harga, selected_provinces, year_range=year_range)
    st.plotly_chart(fig_line, use_container_width=True, height=450)
else:
    st.warning("Pilih minimal satu provinsi untuk menampilkan grafik.")

# ---------------------------------------------------------------------------
# 7. Slope graph + Gap Calculator (two columns)
# ---------------------------------------------------------------------------
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("#### Perubahan Harga: 2019 vs 2025")
    st.caption("Garis merah = kenaikan >15% | Garis hijau = stabil/turun")
    fig_slope = make_slopegraph(df_harga, selected_provinces, year_start=2019, year_end=2025)
    st.plotly_chart(fig_slope, use_container_width=True, height=400)

with col2:
    st.markdown("#### Kalkulator Gap Harga")

    prov_a = st.selectbox(
        "Provinsi A",
        all_provinces,
        index=all_provinces.index("PAPUA") if "PAPUA" in all_provinces else 0,
        key="gap_a",
    )
    prov_b = st.selectbox(
        "Provinsi B",
        all_provinces,
        index=all_provinces.index("LAMPUNG") if "LAMPUNG" in all_provinces else 1,
        key="gap_b",
    )
    gap_year = st.selectbox(
        "Tahun",
        list(range(2019, 2026)),
        index=6,
        key="gap_year",
    )

    def get_avg_price(provinsi: str, year: int):
        mask = (df_harga.PROVINSI == provinsi) & (df_harga.TANGGAL.dt.year == year)
        vals = df_harga[mask].HARGA_BERAS
        return vals.mean() if len(vals) > 0 else None

    price_a = get_avg_price(prov_a, gap_year)
    price_b = get_avg_price(prov_b, gap_year)

    if price_a and price_b:
        gap_val = price_a - price_b
        pct_diff = (gap_val / price_b) * 100

        st.metric(f"Harga {prov_a} ({gap_year})", f"Rp {price_a:,.0f}/kg")
        st.metric(f"Harga {prov_b} ({gap_year})", f"Rp {price_b:,.0f}/kg")

        color = "#c53030" if gap_val > 0 else "#7ab528"
        card_class = "danger" if gap_val > 0 else "success"
        st.markdown(f"""
        <div class='kpi-card {card_class}' style='margin-top:12px;'>
          <div style='font-size:12px; color:#8aaa70;'>Selisih Harga</div>
          <div style='font-size:28px; font-weight:700; color:{color};'>
            Rp {abs(gap_val):,.0f}/kg
          </div>
          <div style='font-size:13px; color:#e8f0e0;'>
            {prov_a} {'lebih mahal' if gap_val > 0 else 'lebih murah'} {abs(pct_diff):.1f}% dari {prov_b}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. National average trend (smaller chart)
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("#### Rata-rata Harga Beras Nasional (Bulanan)")

# Compute national average per month
df_national = (
    df_harga.groupby("TANGGAL")["HARGA_BERAS"]
    .mean()
    .reset_index()
)
df_national.columns = ["TANGGAL", "HARGA_NASIONAL"]

# Filter by year range
df_national = df_national[
    (df_national.TANGGAL.dt.year >= year_range[0])
    & (df_national.TANGGAL.dt.year <= year_range[1])
]

fig_nat = make_line_harga(
    df_harga.groupby(["TANGGAL"])
    .agg(HARGA_BERAS=("HARGA_BERAS", "mean"))
    .reset_index()
    .assign(PROVINSI="Nasional"),
    ["Nasional"],
    year_range=year_range,
)
st.plotly_chart(fig_nat, use_container_width=True, height=300)
