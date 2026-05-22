"""
dashboard/app.py, Landing / Home page
Ketahanan Pangan Indonesia, Dashboard Analitik Spasial-Temporal Distribusi Beras
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path: allow `from utils.xxx import ...` without installing as package
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Page config, MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Ketahanan Pangan Indonesia",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
_CSS_PATH = Path(__file__).parent / "assets" / "style.css"
with open(_CSS_PATH) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Data imports (after sys.path is set)
# ---------------------------------------------------------------------------
from utils.data_loader import load_ikp, load_harga_beras, load_produksi
from utils import colors

# ---------------------------------------------------------------------------
# 4. Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='color:#065f46; font-weight:700; font-size:18px; letter-spacing:0.5px;'>Home</div>
      <div style='color:#6f7973; font-size:12px;'>Ketahanan Pangan Indonesia</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div style='color:#6f7973; font-size:11px; padding: 4px 0 8px 0; "
        "text-transform:uppercase; letter-spacing:1px;'>Navigasi</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style='font-size:13px; color:#181c1a; line-height:2;'>
    <b>Gambaran Umum</b>, Peta IKP<br>
    <b>Klaster Wilayah</b>, K-Means<br>
    <b>Tren &amp; Gap Harga</b>, Slope<br>
    <b>Proyeksi ARIMA</b>, Forecast<br>
    <b>Analisis Pareto</b>, 80/20<br>
    <b>Distribusi MPP</b>, Ketimpangan
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,0.15); margin:12px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:11px; color:#6f7973; line-height:1.6;'>
    <b style='color:#6f7973;'>IF4061 Visualisasi Data</b><br>
    Semester 2 2025/2026<br>
    VSC26101, Group 14<br><br>
    Sumber: BPS, Badan Pangan Nasional
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. Load data & compute quick stats
# ---------------------------------------------------------------------------
@st.cache_data
def _get_landing_stats():
    ikp_df = load_ikp()
    latest_year = int(ikp_df["TAHUN"].max())
    earliest_year = int(ikp_df["TAHUN"].min())
    df_latest = ikp_df[ikp_df["TAHUN"] == latest_year]

    n_provinces = df_latest["PROVINSI"].nunique()
    year_range = f"{earliest_year}–{latest_year}"
    sangat_rentan = int((df_latest["IKP"] < 50).sum())
    avg_ikp = round(df_latest["IKP"].mean(), 1)

    # Lowest IKP province (most vulnerable)
    worst_idx = df_latest["IKP"].idxmin()
    worst_province = df_latest.loc[worst_idx, "PROVINSI"].title()
    worst_ikp = round(df_latest.loc[worst_idx, "IKP"], 1)

    # Price gap, West (Jawa) vs East (Papua+Maluku)
    harga_df = load_harga_beras()
    harga_latest = harga_df[harga_df["TANGGAL"].dt.year == latest_year]
    west_provs = ["JAWA BARAT", "JAWA TENGAH", "JAWA TIMUR", "DKI JAKARTA", "BANTEN",
                  "DAERAH ISTIMEWA YOGYAKARTA"]
    east_provs = ["PAPUA", "PAPUA BARAT", "PAPUA PEGUNUNGAN", "PAPUA TENGAH",
                  "PAPUA SELATAN", "PAPUA BARAT DAYA", "MALUKU", "MALUKU UTARA"]
    west_avg = harga_latest[harga_latest["PROVINSI"].isin(west_provs)]["HARGA_BERAS"].mean()
    east_avg = harga_latest[harga_latest["PROVINSI"].isin(east_provs)]["HARGA_BERAS"].mean()
    price_gap_pct = round((east_avg - west_avg) / west_avg * 100, 0) if west_avg > 0 else 0

    # Total production (all provinces, latest snapshot in produksi_padi.csv)
    prod_df = load_produksi()
    total_prod_juta_ton = round(prod_df["PRODUKSI_TON"].sum() / 1_000_000, 1)

    return {
        "latest_year": latest_year,
        "year_range": year_range,
        "n_provinces": n_provinces,
        "sangat_rentan": sangat_rentan,
        "avg_ikp": avg_ikp,
        "worst_province": worst_province,
        "worst_ikp": worst_ikp,
        "price_gap_pct": int(price_gap_pct),
        "west_avg": round(west_avg / 1000, 1),
        "east_avg": round(east_avg / 1000, 1),
        "total_prod_juta_ton": total_prod_juta_ton,
    }


stats = _get_landing_stats()

# ---------------------------------------------------------------------------
# 6. Hero section
# ---------------------------------------------------------------------------
st.markdown(f"""
<div style='
    background: linear-gradient(135deg, #004532 0%, #065f46 100%);
    border-radius: 12px;
    padding: 40px 48px 32px 48px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0px 4px 20px rgba(0, 69, 50, 0.2);
'>
  <h1 style='
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    margin: 0 0 8px 0;
    text-transform: uppercase;
  '>KETAHANAN PANGAN INDONESIA</h1>
  <p style='
    color: rgba(255,255,255,0.8);
    font-size: 1rem;
    margin: 0 0 6px 0;
    font-weight: 400;
  '>Dashboard Analitik Spasial-Temporal Distribusi Beras</p>
  <p style='
    color: rgba(255,255,255,0.55);
    font-size: 0.82rem;
    margin: 0;
    letter-spacing: 0.04em;
  '>Data {stats['year_range']} &nbsp;·&nbsp; {stats['n_provinces']} Provinsi &nbsp;·&nbsp;
     IF4061 Visualisasi Data, Group 14</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. Quick-stat KPI row
# ---------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Provinsi Dianalisis",
        value=str(stats["n_provinces"]),
        help="Jumlah provinsi yang tercakup dalam dataset IKP",
    )

with kpi2:
    st.metric(
        label="Rentang Tahun Data",
        value=stats["year_range"],
        help="Tahun pertama hingga terakhir dalam dataset IKP",
    )

with kpi3:
    st.metric(
        label=f"Sangat Rentan ({stats['latest_year']})",
        value=str(stats["sangat_rentan"]),
        help="Jumlah provinsi dengan IKP < 50 pada tahun terbaru",
        delta=f"IKP < 50",
        delta_color="inverse",
    )

with kpi4:
    st.metric(
        label=f"Rata-rata IKP Nasional ({stats['latest_year']})",
        value=f"{stats['avg_ikp']}",
        help="Rata-rata Indeks Ketahanan Pangan seluruh provinsi",
    )

st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. Narrative cards
# ---------------------------------------------------------------------------
st.markdown(
    "<h3 style='color:#004532; font-size:1rem; font-weight:700; letter-spacing:0.04em; "
    "text-transform:uppercase; margin-bottom:12px;'>Temuan Utama</h3>",
    unsafe_allow_html=True,
)

card1, card2, card3 = st.columns(3)

with card1:
    st.markdown(f"""
    <div style='
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        height: 170px;
    '>
      <div style='display:flex; align-items:center; gap:7px; margin-bottom:10px;'>
        <span style='width:7px;height:7px;border-radius:50%;background:#065f46;flex-shrink:0;display:inline-block;'></span>
        <span style='color:#065f46; font-weight:700; font-size:0.82rem; letter-spacing:0.6px;'>PRODUKSI BERAS NASIONAL</span>
      </div>
      <div style='color:#181c1a; font-size:0.9rem; line-height:1.6;'>
        Total produksi padi nasional mencapai
        <span style='color:#904d00; font-weight:700; font-size:1.1rem;'>
          {stats['total_prod_juta_ton']} juta ton
        </span>
       , namun distribusinya masih timpang antara Jawa dan wilayah timur.
      </div>
    </div>
    """, unsafe_allow_html=True)

with card2:
    st.markdown(f"""
    <div style='
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        height: 170px;
    '>
      <div style='display:flex; align-items:center; gap:7px; margin-bottom:10px;'>
        <span style='width:7px;height:7px;border-radius:50%;background:#be123c;flex-shrink:0;display:inline-block;'></span>
        <span style='color:#be123c; font-weight:700; font-size:0.82rem; letter-spacing:0.6px;'>ZONA KRITIS PANGAN</span>
      </div>
      <div style='color:#181c1a; font-size:0.9rem; line-height:1.6;'>
        <span style='color:#be123c; font-weight:700;'>{stats['worst_province']}</span>
        memiliki IKP terendah
        <span style='color:#be123c; font-weight:700;'>{stats['worst_ikp']}</span>
       , jauh di bawah ambang ketahanan nasional.
        {stats['sangat_rentan']} provinsi masuk kategori Sangat Rentan.
      </div>
    </div>
    """, unsafe_allow_html=True)

with card3:
    st.markdown(f"""
    <div style='
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        height: 170px;
    '>
      <div style='display:flex; align-items:center; gap:7px; margin-bottom:10px;'>
        <span style='width:7px;height:7px;border-radius:50%;background:#904d00;flex-shrink:0;display:inline-block;'></span>
        <span style='color:#904d00; font-weight:700; font-size:0.82rem; letter-spacing:0.6px;'>GAP HARGA BARAT–TIMUR</span>
      </div>
      <div style='color:#181c1a; font-size:0.9rem; line-height:1.6;'>
        Harga beras di Papua &amp; Maluku rata-rata
        <span style='color:#904d00; font-weight:700;'>Rp {stats['east_avg']}rb/kg</span>
        vs Jawa
        <span style='color:#065f46; font-weight:700;'>Rp {stats['west_avg']}rb/kg</span>
       , selisih
        <span style='color:#904d00; font-weight:700;'>{stats['price_gap_pct']}%</span>.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:28px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 9. Navigation cards, 6 pages
# ---------------------------------------------------------------------------
st.markdown(
    "<h3 style='color:#004532; font-size:1rem; font-weight:700; letter-spacing:0.04em; "
    "text-transform:uppercase; margin-bottom:12px;'>Jelajahi Dashboard</h3>",
    unsafe_allow_html=True,
)

NAV_PAGES = [
    {
        "icon": "🗺️",
        "title": "Gambaran Umum",
        "desc": "Peta IKP interaktif seluruh provinsi dengan choropleth dan tabel peringkat.",
        "href": "/Overview",
        "color": "#1e6ba8",
    },
    {
        "icon": "🔍",
        "title": "Klaster Wilayah",
        "desc": "Segmentasi provinsi menggunakan K-Means clustering berdasarkan 5 indikator.",
        "href": "/Clustering",
        "color": "#065f46",
    },
    {
        "icon": "📈",
        "title": "Tren & Gap Harga",
        "desc": "Slope chart harga beras antar provinsi dan gap wilayah barat–timur.",
        "href": "/Price_Trend",
        "color": "#904d00",
    },
    {
        "icon": "🔮",
        "title": "Proyeksi ARIMA",
        "desc": "Forecast harga beras 12 bulan ke depan per provinsi menggunakan ARIMA.",
        "href": "/ARIMA",
        "color": "#7c3aed",
    },
    {
        "icon": "📊",
        "title": "Analisis Pareto",
        "desc": "Identifikasi 20% provinsi yang menyumbang 60%+ beban kerentanan pangan.",
        "href": "/Pareto",
        "color": "#c2410c",
    },
    {
        "icon": "🔗",
        "title": "Distribusi MPP",
        "desc": "Analisis ketimpangan margin perdagangan dan penyaluran beras antar wilayah.",
        "href": "/MPP_GINI",
        "color": "#0891b2",
    },
]

nav_cols = st.columns(6)
for col, page in zip(nav_cols, NAV_PAGES):
    with col:
        st.markdown(f"""
        <a href="{page['href']}" target="_self" style="text-decoration:none;">
          <div style='
              background: #ffffff;
              border: 1px solid #e2e8f0;
              border-radius: 10px;
              padding: 18px 12px;
              text-align: center;
              cursor: pointer;
              height: 150px;
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-start;
          '>
            <div style='font-size:1.4rem; margin-bottom:8px; line-height:1;'>{page['icon']}</div>
            <div style='color:{page['color']}; font-weight:700; font-size:0.78rem;
                        margin-bottom:6px; line-height:1.2;'>{page['title']}</div>
            <div style='color:#6f7973; font-size:0.67rem; line-height:1.4;'>
              {page['desc']}
            </div>
          </div>
        </a>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:28px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 10. Footer
# ---------------------------------------------------------------------------
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
  Dashboard ini dibuat untuk keperluan akademik, IF4061 Visualisasi Data,
  Institut Teknologi Bandung, Semester 2 2025/2026.
</div>
""", unsafe_allow_html=True)
