"""
dashboard/pages/1_Overview.py — Gambaran Umum (Overview)
Peta distribusi Indeks Ketahanan Pangan (IKP) 38 provinsi Indonesia
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path: allow `from utils.xxx import ...` without installing as package
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Page config — MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Gambaran Umum IKP | Ketahanan Pangan Indonesia",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
_CSS_PATH = Path(__file__).parent.parent / "assets" / "style.css"
with open(_CSS_PATH) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Data imports (after sys.path is set)
# ---------------------------------------------------------------------------
from utils.data_loader import load_ikp, load_geojson, get_ikp_for_year
from utils.charts import make_choropleth, make_bar_top_bottom
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

    # Page-specific filters
    st.markdown("---")
    st.markdown("**Filter Halaman Ini**")
    selected_year = st.selectbox("Tahun", options=list(range(2019, 2026)), index=6)
    selected_island = st.selectbox(
        "Pulau",
        options=["Semua"] + list(colors.ISLAND_GROUPS.keys()),
    )

# ---------------------------------------------------------------------------
# 5. Section 1: Page header
# ---------------------------------------------------------------------------
st.markdown("""
<div class='headline-card'>
  <h1 style='color:#7ab528; margin:0;'>Gambaran Umum Ketahanan Pangan</h1>
  <p style='color:#8aaa70; margin:4px 0 0;'>Peta distribusi Indeks Ketahanan Pangan (IKP) 38 provinsi Indonesia</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 6. Load data for selected year
# ---------------------------------------------------------------------------
df_year = get_ikp_for_year(selected_year)
geojson = load_geojson()

# Compute delta vs previous year for avg IKP
avg_ikp = df_year["IKP"].mean()
delta_avg = None
if selected_year > 2019:
    df_prev = get_ikp_for_year(selected_year - 1)
    prev_avg = df_prev["IKP"].mean()
    delta_avg = round(avg_ikp - prev_avg, 2)

# KPI computations
count_tahan = int(df_year["KERENTANAN"].isin(["Tahan", "Sangat Tahan"]).sum())
count_kritis = int((df_year["IKP"] < 60).sum())

max_idx = df_year["IKP"].idxmax()
min_idx = df_year["IKP"].idxmin()
max_ikp = df_year.loc[max_idx, "IKP"]
min_ikp = df_year.loc[min_idx, "IKP"]
prov_max = df_year.loc[max_idx, "PROVINSI"].title()
prov_min = df_year.loc[min_idx, "PROVINSI"].title()

# ---------------------------------------------------------------------------
# 7. Section 3: KPI Metrics row (5 columns)
# ---------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(
        label="Rata-rata IKP Nasional",
        value=f"{avg_ikp:.2f}",
        delta=f"{delta_avg:+.2f} vs {selected_year - 1}" if delta_avg is not None else None,
        help="Rata-rata Indeks Ketahanan Pangan seluruh provinsi pada tahun yang dipilih",
    )

with kpi2:
    st.metric(
        label="Provinsi Tahan/Sangat Tahan",
        value=str(count_tahan),
        help="Jumlah provinsi dengan kategori Tahan atau Sangat Tahan",
    )

with kpi3:
    st.metric(
        label="Provinsi Kritis (IKP < 60)",
        value=str(count_kritis),
        delta=f"IKP < 60" if count_kritis > 0 else "Tidak ada",
        delta_color="inverse",
        help="Jumlah provinsi dengan IKP di bawah 60 (kritis)",
    )

with kpi4:
    st.metric(
        label="IKP Tertinggi",
        value=f"{max_ikp:.1f}",
        delta=prov_max,
        delta_color="off",
        help="Nilai IKP tertinggi dan provinsinya",
    )

with kpi5:
    st.metric(
        label="IKP Terendah",
        value=f"{min_ikp:.1f}",
        delta=prov_min,
        delta_color="off",
        help="Nilai IKP terendah dan provinsinya",
    )

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. Section 4: Choropleth map (full width)
# ---------------------------------------------------------------------------

# Apply island filter
if selected_island != "Semua":
    island_provinces = colors.ISLAND_GROUPS[selected_island]
    df_filtered = df_year[df_year["PROVINSI"].isin(island_provinces)].copy()
else:
    df_filtered = df_year.copy()

st.markdown(
    f"<h3 style='color:#7ab528; font-size:1rem; letter-spacing:2px; "
    f"text-transform:uppercase; margin-bottom:8px;'>"
    f"Peta IKP — {selected_year}"
    f"{' · ' + selected_island if selected_island != 'Semua' else ''}"
    f"</h3>",
    unsafe_allow_html=True,
)

map_fig = make_choropleth(df_filtered, geojson)
st.plotly_chart(map_fig, use_container_width=True, height=500)

st.markdown(
    f"<p style='color:#556644; font-size:0.78rem; text-align:center; margin-top:-8px;'>"
    f"Sumber: Badan Pangan Nasional (NFA) &nbsp;·&nbsp; Data IKP Tahun {selected_year} &nbsp;·&nbsp; "
    f"Skala warna: merah (kritis) → kuning (sedang) → hijau (tahan)"
    f"</p>",
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 9. Section 5: Two-column bar charts
# ---------------------------------------------------------------------------
st.markdown(
    "<h3 style='color:#7ab528; font-size:1rem; letter-spacing:2px; "
    "text-transform:uppercase; margin-bottom:8px;'>Peringkat Provinsi</h3>",
    unsafe_allow_html=True,
)

bar_col1, bar_col2 = st.columns(2)

with bar_col1:
    fig_top = make_bar_top_bottom(df_year, top=True, n=10)
    st.plotly_chart(fig_top, use_container_width=True, height=420)

with bar_col2:
    fig_bot = make_bar_top_bottom(df_year, top=False, n=10)
    st.plotly_chart(fig_bot, use_container_width=True, height=420)

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

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
