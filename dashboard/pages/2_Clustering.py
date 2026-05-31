import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import get_clustering_features, get_available_years
from utils.charts import make_cluster_scatter, make_elbow_silhouette
from utils import colors

FEATURE_LABELS = {
    "IKP": "IKP",
    "PRODUKSI_TON": "Produksi Ton",
    "HARGA_BERAS_AVG": "Harga Beras Rata-Rata",
    "HARGA_BERAS": "Harga Beras",
    "MPP_TOTAL_PCT": "MPP Total (%)",
    "MPP_TOTAL": "MPP Total",
    "GINI": "Gini Ratio",
}


def feature_label(feature: str) -> str:
    return FEATURE_LABELS.get(feature, feature.replace("_", " ").title())

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page config, MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Klaster Wilayah | Ketahanan Pangan",
    page_icon="🔍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
with open(Path(__file__).parent.parent / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Sidebar controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='color:#065f46; font-weight:700; font-size:16px; letter-spacing:1px;'>KLASTER WILAYAH</div>
      <div style='color:#6f7973; font-size:12px;'>K-Means Clustering</div>
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:8px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='font-size:0.7rem; color:rgba(255,255,255,0.5); text-transform:uppercase;
                letter-spacing:0.07em; margin-bottom:4px;'>Konten</div>
    <div style='font-size:0.82rem; color:rgba(255,255,255,0.85); line-height:2;'>
      Evaluasi Jumlah Klaster Optimal<br>
      Ringkasan Per Klaster
    </div>
    <hr style='border-color:rgba(255,255,255,0.15); margin:10px 0;'>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Pengaturan Klaster**")

    _available_years = get_available_years()
    year = st.selectbox(
        "Tahun Data",
        _available_years,
        index=len(_available_years) - 2,
    )
    k = st.slider("Jumlah Klaster (K)", min_value=2, max_value=6, value=3)
    x_feature = st.selectbox(
        "Sumbu X",
        ["HARGA_BERAS_AVG", "MPP_TOTAL_PCT", "PRODUKSI_TON", "IKP"],
        index=0,
    )
    y_feature = st.selectbox(
        "Sumbu Y",
        ["IKP", "HARGA_BERAS_AVG", "MPP_TOTAL_PCT", "PRODUKSI_TON"],
        index=0,
    )

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
# 4. Section 1: Headline card
# ---------------------------------------------------------------------------
st.markdown("""
<div style='
    background: linear-gradient(135deg, #004532 0%, #065f46 100%);
    border-radius: 12px;
    padding: 32px 48px 24px 48px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0px 4px 20px rgba(0, 69, 50, 0.2);
'>
  <h1 style='
    color: #ffffff;
    font-size: 1.9rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0 0 10px 0;
  '>Klaster Wilayah Berdasarkan Kondisi Ketahanan Pangan</h1>
  <p style='
    color: rgba(255,255,255,0.7);
    font-size: 0.95rem;
    font-style: italic;
    margin: 0;
  '>"Tidak semua provinsi rawan memiliki masalah yang sama, K-Means mengungkap polanya"</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. Section 3: K-Means computation (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def compute_kmeans(year: int, k: int):
    df = get_clustering_features(year)
    if df.empty or len(df) < k:
        return df, [], []

    feature_cols = ["HARGA_BERAS_AVG", "MPP_TOTAL_PCT", "PRODUKSI_TON", "IKP"]
    X = df[feature_cols].dropna()
    df_clean = df.loc[X.index].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit K-Means
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    df_clean["CLUSTER"] = km.fit_predict(X_scaled).astype(str)
    df_clean["CLUSTER"] = "Klaster " + df_clean["CLUSTER"].astype(str)

    # Compute elbow + silhouette for k=2..6
    k_range = range(2, 7)
    inertias = []
    silhouettes = []
    for ki in k_range:
        km_i = KMeans(n_clusters=ki, random_state=42, n_init=10)
        labels = km_i.fit_predict(X_scaled)
        inertias.append(km_i.inertia_)
        if ki > 1:
            silhouettes.append(silhouette_score(X_scaled, labels))
        else:
            silhouettes.append(0)

    return df_clean, inertias, silhouettes


df_clean, inertias, silhouettes = compute_kmeans(year, k)

# ---------------------------------------------------------------------------
# 6. Section 4: Main layout, info panel + scatter plot
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(
        f"""
        <div style='
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 16px;
        '>
          <div style='color:#065f46; font-weight:700; font-size:0.85rem;
                      letter-spacing:1px; text-transform:uppercase; margin-bottom:12px;'>
            Parameter Analisis
          </div>
          <div style='color:#181c1a; font-size:0.9rem; line-height:2;'>
            <span style='color:#6f7973;'>Tahun:</span>
            <span style='color:#904d00; font-weight:700;'> {year}</span><br>
            <span style='color:#6f7973;'>Jumlah Klaster:</span>
            <span style='color:#904d00; font-weight:700;'> K = {k}</span><br>
            <span style='color:#6f7973;'>Sumbu X:</span>
            <span style='color:#181c1a;'> {feature_label(x_feature)}</span><br>
            <span style='color:#6f7973;'>Sumbu Y:</span>
            <span style='color:#181c1a;'> {feature_label(y_feature)}</span><br>
            <span style='color:#6f7973;'>Provinsi:</span>
            <span style='color:#181c1a;'> {len(df_clean) if not df_clean.empty else 0}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
        '>
          <div style='color:#065f46; font-weight:700; font-size:0.85rem;
                      letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;'>
            Tentang K-Means
          </div>
          <div style='color:#6f7973; font-size:0.85rem; line-height:1.7;'>
            <b style='color:#181c1a;'>K-Means</b> adalah algoritma pengelompokan yang membagi
            provinsi ke dalam <b style='color:#904d00;'>K klaster</b> berdasarkan kemiripan
            indikator ketahanan pangan.<br><br>
            Setiap klaster merepresentasikan kelompok provinsi dengan karakteristik serupa,
            sehingga kebijakan dapat dirancang lebih <b style='color:#065f46;'>tertarget</b>
            sesuai kebutuhan masing-masing klaster.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("**Fitur yang digunakan:** Harga Beras, MPP, Produksi Padi, IKP")

with col_right:
    if df_clean.empty:
        st.warning("Tidak ada data klaster untuk tahun yang dipilih.")
    else:
        fig_scatter = make_cluster_scatter(df_clean, x_col=x_feature, y_col=y_feature)
        st.plotly_chart(fig_scatter, width="stretch")

# ---------------------------------------------------------------------------
# 7. Section 5: Elbow and Silhouette
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#004532; font-size:1rem; font-weight:700; letter-spacing:0.04em; "
    "text-transform:uppercase; margin-bottom:4px;'>Evaluasi Jumlah Klaster Optimal</h3>",
    unsafe_allow_html=True,
)

col_elbow, col_sil = st.columns(2)

if inertias and silhouettes:
    fig_elbow, fig_sil = make_elbow_silhouette(inertias, silhouettes, list(range(2, 7)))
    with col_elbow:
        st.markdown("**Elbow Method**")
        st.plotly_chart(fig_elbow, width="stretch")
    with col_sil:
        st.markdown("**Silhouette Score**")
        st.plotly_chart(fig_sil, width="stretch")
else:
    with col_elbow:
        st.warning("Data elbow tidak tersedia.")
    with col_sil:
        st.warning("Data silhouette tidak tersedia.")

# ---------------------------------------------------------------------------
# 8. Section 6: Cluster summary table + expanders
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#004532; font-size:1rem; font-weight:700; letter-spacing:0.04em; "
    "text-transform:uppercase; margin-bottom:8px;'>Ringkasan Per Klaster</h3>",
    unsafe_allow_html=True,
)

if not df_clean.empty:
    # Build summary DataFrame
    summary_rows = []
    for cluster_label in sorted(df_clean["CLUSTER"].unique()):
        sub = df_clean[df_clean["CLUSTER"] == cluster_label]
        summary_rows.append({
            "Klaster": cluster_label,
            "Jumlah Provinsi": len(sub),
            "Rata-rata IKP": round(sub["IKP"].mean(), 2),
            "Rata-rata Harga Beras": round(sub["HARGA_BERAS_AVG"].mean(), 0),
            "Rata-rata MPP (%)": round(sub["MPP_TOTAL_PCT"].mean(), 2),
        })

    summary_df = pd.DataFrame(summary_rows)

    # Identify worst cluster (lowest avg IKP)
    worst_cluster_label = summary_df.loc[summary_df["Rata-rata IKP"].idxmin(), "Klaster"]

    # Render as plain HTML table (bypasses GlideDataGrid CSS issues)
    rows_html = ""
    for _, row in summary_df.iterrows():
        is_worst = row["Klaster"] == worst_cluster_label
        row_style = f"color:{colors.ACCENT_RED}; font-weight:700;" if is_worst else f"color:{colors.TEXT_PRIMARY};"
        badge = f" <span style='background:{colors.ACCENT_RED};color:#fff;font-size:0.65rem;padding:1px 6px;border-radius:4px;vertical-align:middle;'>Kritis</span>" if is_worst else ""
        rows_html += f"""
        <tr style='border-bottom:1px solid #e2e8f0;'>
          <td style='padding:10px 14px; {row_style}'>{row['Klaster']}{badge}</td>
          <td style='padding:10px 14px; text-align:center; {row_style}'>{int(row['Jumlah Provinsi'])}</td>
          <td style='padding:10px 14px; text-align:right; {row_style}'>{row['Rata-rata IKP']:.2f}</td>
          <td style='padding:10px 14px; text-align:right; {row_style}'>Rp {row['Rata-rata Harga Beras']:,.0f}</td>
          <td style='padding:10px 14px; text-align:right; {row_style}'>{row['Rata-rata MPP (%)']:.2f}%</td>
        </tr>"""

    th = "padding:10px 14px; background:#f1f4f0; color:#3f4944; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.04em; font-weight:600; border-bottom:2px solid #e2e8f0;"
    html_table = f"""
    <div style='background:#fff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0px 4px 20px rgba(0,0,0,0.06);'>
    <table style='width:100%; border-collapse:collapse; font-family:Plus Jakarta Sans,sans-serif; font-size:0.88rem;'>
      <thead>
        <tr>
          <th style='{th} text-align:left;'>Klaster</th>
          <th style='{th} text-align:center;'>Jumlah Provinsi</th>
          <th style='{th} text-align:right;'>Rata-rata IKP</th>
          <th style='{th} text-align:right;'>Rata-rata Harga Beras</th>
          <th style='{th} text-align:right;'>Rata-rata MPP (%)</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    </div>"""
    st.markdown(html_table, unsafe_allow_html=True)

    # Expanders per cluster showing province list
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    for cluster_label in sorted(df_clean["CLUSTER"].unique()):
        sub = df_clean[df_clean["CLUSTER"] == cluster_label]
        provinces_in_cluster = sub["PROVINSI"].sort_values().tolist()
        is_worst = cluster_label == worst_cluster_label
        label_suffix = ", Klaster Kritis" if is_worst else ""

        with st.expander(f"{cluster_label}{label_suffix}, {len(provinces_in_cluster)} Provinsi"):
            prov_cols = st.columns(3)
            for idx, prov in enumerate(provinces_in_cluster):
                with prov_cols[idx % 3]:
                    ikp_val = sub.loc[sub["PROVINSI"] == prov, "IKP"].values[0]
                    color_text = colors.ACCENT_RED if is_worst else colors.TEXT_PRIMARY
                    st.markdown(
                        f"<span style='color:{color_text}; font-size:0.85rem;'>"
                        f"• {prov.title()} <span style='color:{colors.TEXT_MUTED};'>"
                        f"(IKP: {ikp_val:.1f})</span></span>",
                        unsafe_allow_html=True,
                    )

    # Additional context
    st.markdown(
        f"""
        <div style='
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px 20px;
            margin-top: 12px;
            font-size: 0.85rem;
            color: #6f7973;
            line-height: 1.7;
        '>
          <b style='color:#065f46;'>Catatan Metodologi:</b>
          Pengelompokan menggunakan <b style='color:#181c1a;'>K-Means</b> dengan
          <b style='color:#904d00;'>K={k}</b> klaster dan fitur yang telah dinormalisasi
          (StandardScaler). Analisis dijalankan pada data tahun
          <b style='color:#904d00;'>{year}</b> mencakup
          <b style='color:#181c1a;'>{len(df_clean)}</b> provinsi.
          Silakan ubah nilai K di sidebar untuk mengeksplorasi konfigurasi klaster yang berbeda.
          <br><br>
          <b style='color:#065f46;'>Cara membaca:</b>
          klaster dengan IKP lebih rendah, harga beras lebih tinggi, atau MPP lebih besar
          dapat diprioritaskan untuk analisis lanjutan.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.error(
        "Data clustering tidak tersedia untuk tahun yang dipilih. "
        "Silakan pilih tahun lain di sidebar.",
    )

# ---------------------------------------------------------------------------
# 10. Footer
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
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
