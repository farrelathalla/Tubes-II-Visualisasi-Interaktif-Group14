"""
dashboard/pages/2_Clustering.py — Klaster Wilayah (K-Means Clustering)
Segmentasi provinsi berdasarkan kondisi ketahanan pangan menggunakan K-Means.
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.data_loader import get_clustering_features, get_available_years
from utils.charts import make_cluster_scatter, make_elbow_silhouette
from utils import colors

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# 1. Page config — MUST be the first Streamlit call
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
      <div style='color:#7ab528; font-weight:700; font-size:16px; letter-spacing:1px;'>KLASTER WILAYAH</div>
      <div style='color:#8aaa70; font-size:12px;'>K-Means Clustering</div>
    </div>
    <hr style='border-color:#2d5a2d; margin:8px 0;'>
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

    st.markdown("<hr style='border-color:#2d5a2d; margin:12px 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:11px; color:#7a9060; line-height:1.6;'>
    <b style='color:#a8c878;'>IF4061 Visualisasi Data</b><br>
    Semester 2 2025/2026<br>
    VSC26101 — Group 14<br><br>
    Sumber: BPS, Badan Pangan Nasional
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 4. Section 1: Headline card
# ---------------------------------------------------------------------------
st.markdown("""
<div style='
    background: linear-gradient(135deg, #152818 0%, #1c3319 60%, #0d1a0e 100%);
    border: 1px solid #2d5a2d;
    border-radius: 12px;
    padding: 32px 48px 24px 48px;
    margin-bottom: 28px;
    text-align: center;
'>
  <h1 style='
    color: #7ab528;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: 2px;
    margin: 0 0 10px 0;
  '>Klaster Wilayah Berdasarkan Kondisi Ketahanan Pangan</h1>
  <p style='
    color: #8aaa70;
    font-size: 1rem;
    font-style: italic;
    margin: 0;
  '>"Tidak semua provinsi rawan memiliki masalah yang sama — K-Means mengungkap polanya"</p>
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
# 6. Section 4: Main layout — info panel + scatter plot
# ---------------------------------------------------------------------------
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(
        f"""
        <div style='
            background: #152818;
            border: 1px solid #2d5a2d;
            border-radius: 10px;
            padding: 24px;
            margin-bottom: 16px;
        '>
          <div style='color:#7ab528; font-weight:700; font-size:0.85rem;
                      letter-spacing:1px; text-transform:uppercase; margin-bottom:12px;'>
            Parameter Analisis
          </div>
          <div style='color:#e8f0e0; font-size:0.9rem; line-height:2;'>
            <span style='color:#8aaa70;'>Tahun:</span>
            <span style='color:#d4a520; font-weight:700;'> {year}</span><br>
            <span style='color:#8aaa70;'>Jumlah Klaster:</span>
            <span style='color:#d4a520; font-weight:700;'> K = {k}</span><br>
            <span style='color:#8aaa70;'>Sumbu X:</span>
            <span style='color:#e8f0e0;'> {x_feature}</span><br>
            <span style='color:#8aaa70;'>Sumbu Y:</span>
            <span style='color:#e8f0e0;'> {y_feature}</span><br>
            <span style='color:#8aaa70;'>Provinsi:</span>
            <span style='color:#e8f0e0;'> {len(df_clean) if not df_clean.empty else 0}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='
            background: #152818;
            border: 1px solid #2d5a2d;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
        '>
          <div style='color:#7ab528; font-weight:700; font-size:0.85rem;
                      letter-spacing:1px; text-transform:uppercase; margin-bottom:10px;'>
            Tentang K-Means
          </div>
          <div style='color:#8aaa70; font-size:0.85rem; line-height:1.7;'>
            <b style='color:#e8f0e0;'>K-Means</b> adalah algoritma pengelompokan yang membagi
            provinsi ke dalam <b style='color:#d4a520;'>K klaster</b> berdasarkan kemiripan
            indikator ketahanan pangan.<br><br>
            Setiap klaster merepresentasikan kelompok provinsi dengan karakteristik serupa,
            sehingga kebijakan dapat dirancang lebih <b style='color:#7ab528;'>tertarget</b>
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
        st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------------------------
# 7. Section 5: Elbow and Silhouette
# ---------------------------------------------------------------------------
st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#7ab528; font-size:1rem; letter-spacing:2px; "
    "text-transform:uppercase; margin-bottom:4px;'>Evaluasi Jumlah Klaster Optimal</h3>",
    unsafe_allow_html=True,
)

col_elbow, col_sil = st.columns(2)

if inertias and silhouettes:
    fig_elbow, fig_sil = make_elbow_silhouette(inertias, silhouettes, list(range(2, 7)))
    with col_elbow:
        st.markdown("**Elbow Method**")
        st.plotly_chart(fig_elbow, use_container_width=True)
    with col_sil:
        st.markdown("**Silhouette Score**")
        st.plotly_chart(fig_sil, use_container_width=True)
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
    "<h3 style='color:#7ab528; font-size:1rem; letter-spacing:2px; "
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

    # Highlight worst cluster row using Styler
    def _highlight_worst(row):
        if row["Klaster"] == worst_cluster_label:
            return [f"color: {colors.ACCENT_RED}; font-weight: bold;"] * len(row)
        return [""] * len(row)

    styled_summary = summary_df.style.apply(_highlight_worst, axis=1).format({
        "Rata-rata IKP": "{:.2f}",
        "Rata-rata Harga Beras": "Rp {:,.0f}",
        "Rata-rata MPP (%)": "{:.2f}%",
    })

    st.dataframe(styled_summary, use_container_width=True, hide_index=True)

    # Expanders per cluster showing province list
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    for cluster_label in sorted(df_clean["CLUSTER"].unique()):
        sub = df_clean[df_clean["CLUSTER"] == cluster_label]
        provinces_in_cluster = sub["PROVINSI"].sort_values().tolist()
        is_worst = cluster_label == worst_cluster_label
        label_suffix = " — Klaster Kritis" if is_worst else ""

        with st.expander(f"{cluster_label}{label_suffix} — {len(provinces_in_cluster)} Provinsi"):
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

    # ---------------------------------------------------------------------------
    # 9. Section 7: Insight box
    # ---------------------------------------------------------------------------
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='color:#7ab528; font-size:1rem; letter-spacing:2px; "
        "text-transform:uppercase; margin-bottom:8px;'>Insight Klaster</h3>",
        unsafe_allow_html=True,
    )

    worst_sub = df_clean[df_clean["CLUSTER"] == worst_cluster_label]
    worst_ikp_avg = worst_sub["IKP"].mean()
    worst_provinces = worst_sub["PROVINSI"].sort_values().tolist()
    worst_provinces_str = ", ".join([p.title() for p in worst_provinces])

    best_cluster_label = summary_df.loc[summary_df["Rata-rata IKP"].idxmax(), "Klaster"]
    best_ikp_avg = df_clean[df_clean["CLUSTER"] == best_cluster_label]["IKP"].mean()

    st.warning(
        f"**Klaster Paling Kritis: {worst_cluster_label}**\n\n"
        f"Rata-rata IKP: **{worst_ikp_avg:.2f}** — terendah di antara semua klaster.\n\n"
        f"**Provinsi dalam klaster ini ({len(worst_provinces)}):**\n"
        f"{worst_provinces_str}\n\n"
        f"Klaster ini perlu prioritas intervensi kebijakan — termasuk penguatan distribusi beras, "
        f"subsidi harga, dan peningkatan produksi padi lokal.",
    )

    st.info(
        f"**Klaster Terbaik: {best_cluster_label}** — Rata-rata IKP: **{best_ikp_avg:.2f}**. "
        f"Provinsi di klaster ini dapat dijadikan benchmark praktik ketahanan pangan yang baik "
        f"untuk diadopsi wilayah lain.",
    )

    # Additional context
    st.markdown(
        f"""
        <div style='
            background: #152818;
            border: 1px solid #2d5a2d;
            border-left: 4px solid #7ab528;
            border-radius: 8px;
            padding: 16px 20px;
            margin-top: 12px;
            font-size: 0.85rem;
            color: #8aaa70;
            line-height: 1.7;
        '>
          <b style='color:#7ab528;'>Catatan Metodologi:</b>
          Pengelompokan menggunakan <b style='color:#e8f0e0;'>K-Means</b> dengan
          <b style='color:#d4a520;'>K={k}</b> klaster dan fitur yang telah dinormalisasi
          (StandardScaler). Analisis dijalankan pada data tahun
          <b style='color:#d4a520;'>{year}</b> mencakup
          <b style='color:#e8f0e0;'>{len(df_clean)}</b> provinsi.
          Silakan ubah nilai K di sidebar untuk mengeksplorasi konfigurasi klaster yang berbeda.
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
    border-top: 1px solid #2d5a2d;
    padding-top: 16px;
    text-align: center;
    color: #556644;
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
