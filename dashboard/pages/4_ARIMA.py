"""
dashboard/pages/4_ARIMA.py, Proyeksi Harga ARIMA 2026–2027
Model ARIMA untuk proyeksi harga beras per provinsi Indonesia
IF4061 Visualisasi Data | Semester 2 2025/2026 | VSC26101 Group 14
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

# ---------------------------------------------------------------------------
# 1. Page config, MUST be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Proyeksi ARIMA | Ketahanan Pangan",
    page_icon="🔮",
    layout="wide",
)

# ---------------------------------------------------------------------------
# 2. Inject custom CSS
# ---------------------------------------------------------------------------
css_path = Path(__file__).parent.parent / "assets" / "style.css"
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. Imports (after sys.path is set)
# ---------------------------------------------------------------------------
from utils.data_loader import get_arima_data, get_provinces_list
from utils.charts import make_arima_forecast
from utils import colors
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
import warnings

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# 4. ARIMA computation (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def run_arima(provinsi: str, p: int = 1, d: int = 1, q: int = 1, ci_alpha: float = 0.05):
    """Fit ARIMA and return 24-month forecast with confidence intervals."""
    df = get_arima_data(provinsi)
    if df.empty:
        return None, None, None, None

    series = df.set_index("TANGGAL")["HARGA_BERAS"].asfreq("MS")  # Monthly start
    series = series.ffill()  # Fill any gaps

    try:
        model = ARIMA(series, order=(p, d, q))
        result = model.fit()

        # Forecast 24 months (2026-2027)
        forecast_obj = result.get_forecast(steps=24)
        forecast_mean = forecast_obj.predicted_mean
        conf_int = forecast_obj.conf_int(alpha=ci_alpha)

        df_forecast = pd.DataFrame({
            "TANGGAL": forecast_mean.index,
            "FORECAST": forecast_mean.values,
            "CI_LOWER": conf_int.iloc[:, 0].values,
            "CI_UPPER": conf_int.iloc[:, 1].values,
        })

        # Compute RMSE on in-sample fit
        fitted = result.fittedvalues
        residuals = series - fitted
        rmse = np.sqrt((residuals**2).mean())

        # AIC
        aic = result.aic

        return df, df_forecast, rmse, aic
    except Exception as e:
        st.error(f"ARIMA gagal: {e}")
        return df, None, None, None


# ---------------------------------------------------------------------------
# 5. Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 8px 0;'>
      <div style='color:#065f46; font-weight:700; font-size:16px; letter-spacing:1px;'>KETAHANAN PANGAN</div>
      <div style='color:#6f7973; font-size:12px;'>Indonesia Dashboard</div>
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

    st.markdown("---")
    st.markdown("**Pengaturan ARIMA**")

    # Province selection, focus on Papua region which has most dramatic prices
    arima_provinces = ["PAPUA", "PAPUA BARAT", "MALUKU", "NUSA TENGGARA TIMUR", "LAMPUNG", "DKI JAKARTA"]
    all_provs = get_provinces_list()
    arima_provinces = [p for p in arima_provinces if p in all_provs]

    selected_prov = st.selectbox("Provinsi", arima_provinces, index=0)
    compare_mode = st.checkbox("Bandingkan dua provinsi", value=False)
    if compare_mode:
        selected_prov2 = st.selectbox("Provinsi Kedua", arima_provinces, index=1)

    st.markdown("**Parameter ARIMA (p, d, q)**")
    p_val = st.slider("p (AR order)", 0, 3, 1)
    d_val = st.slider("d (differencing)", 0, 2, 1)
    q_val = st.slider("q (MA order)", 0, 3, 1)

    ci_level = st.radio("Confidence Interval", ["95%", "80%"], index=0)
    ci_alpha = 0.05 if ci_level == "95%" else 0.20
    show_hist = st.checkbox("Tampilkan Data Historis", value=True)


# ---------------------------------------------------------------------------
# 6. Section 1: Headline card
# ---------------------------------------------------------------------------
st.markdown("""
<div class='headline-card'>
  <h1 style='color:#904d00; margin:0;'>Proyeksi Harga Beras 2026–2027</h1>
  <p style='color:#6f7973; margin:4px 0 0;'>"Harga Tidak Akan Turun Sendiri, Model ARIMA Memproyeksikan Kenaikan Berlanjut"</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. Section 4: Run ARIMA and show chart
# ---------------------------------------------------------------------------
df_hist, df_fc, rmse, aic = run_arima(selected_prov, p_val, d_val, q_val, ci_alpha)

if df_fc is not None:
    # Build CI df for chart function
    df_ci = df_fc[["TANGGAL", "CI_LOWER", "CI_UPPER"]].copy()
    df_fc_chart = df_fc[["TANGGAL", "FORECAST"]].copy()

    if not show_hist:
        df_hist_chart = pd.DataFrame(columns=["TANGGAL", "HARGA_BERAS"])
    else:
        df_hist_chart = df_hist

    fig = make_arima_forecast(df_hist_chart, df_fc_chart, df_ci, selected_prov)

    # Compare mode: add second province forecast as additional trace
    if compare_mode and "selected_prov2" in dir():
        df_hist2, df_fc2, _rmse2, _aic2 = run_arima(selected_prov2, p_val, d_val, q_val, ci_alpha)

        if df_fc2 is not None:
            df_fc2_chart = df_fc2[["TANGGAL", "FORECAST"]].copy()
            df_fc2_chart["TANGGAL"] = pd.to_datetime(df_fc2_chart["TANGGAL"], errors="coerce")
            df_fc2_chart = df_fc2_chart.sort_values("TANGGAL")

            # Add historical line for second province
            if show_hist and df_hist2 is not None and not df_hist2.empty:
                df_hist2_sorted = df_hist2.copy()
                df_hist2_sorted["TANGGAL"] = pd.to_datetime(df_hist2_sorted["TANGGAL"], errors="coerce")
                df_hist2_sorted = df_hist2_sorted.sort_values("TANGGAL")
                fig.add_trace(
                    go.Scatter(
                        x=df_hist2_sorted["TANGGAL"],
                        y=df_hist2_sorted["HARGA_BERAS"],
                        mode="lines",
                        name=f"Historis ({selected_prov2})",
                        line=dict(color=colors.ACCENT_GOLD, width=2, dash="dot"),
                        hovertemplate=f"Historis {selected_prov2}: Rp %{{y:,.0f}}<extra></extra>",
                    )
                )

            # Forecast line for second province
            fig.add_trace(
                go.Scatter(
                    x=df_fc2_chart["TANGGAL"],
                    y=df_fc2_chart["FORECAST"],
                    mode="lines",
                    name=f"Proyeksi ({selected_prov2})",
                    line=dict(color=colors.ACCENT_GOLD, width=2, dash="dashdot"),
                    hovertemplate=f"Proyeksi {selected_prov2}: Rp %{{y:,.0f}}<extra></extra>",
                )
            )

            # CI shading for second province
            df_ci2 = df_fc2[["TANGGAL", "CI_LOWER", "CI_UPPER"]].copy()
            df_ci2["TANGGAL"] = pd.to_datetime(df_ci2["TANGGAL"], errors="coerce")
            df_ci2 = df_ci2.sort_values("TANGGAL")

            fig.add_trace(
                go.Scatter(
                    x=df_ci2["TANGGAL"],
                    y=df_ci2["CI_LOWER"],
                    mode="lines",
                    line=dict(width=0),
                    showlegend=False,
                    hoverinfo="skip",
                    name=f"CI Lower ({selected_prov2})",
                )
            )
            gold_rgba2 = "rgba(212, 165, 32, 0.08)"
            fig.add_trace(
                go.Scatter(
                    x=df_ci2["TANGGAL"],
                    y=df_ci2["CI_UPPER"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=gold_rgba2,
                    showlegend=True,
                    name=f"{ci_level} CI ({selected_prov2})",
                    hoverinfo="skip",
                )
            )

    st.plotly_chart(fig, use_container_width=True, height=480)

elif df_hist is not None and not df_hist.empty:
    st.warning("Model ARIMA tidak dapat menghasilkan proyeksi. Coba ubah parameter (p, d, q).")
else:
    st.error(f"Tidak ada data historis untuk provinsi {selected_prov}.")

st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. Section 5: Metrics row (4 columns)
# ---------------------------------------------------------------------------
last_hist_price = df_hist["HARGA_BERAS"].iloc[-1] if df_hist is not None and not df_hist.empty else None
last_fc_price = df_fc["FORECAST"].iloc[-1] if df_fc is not None else None
delta_pct = ((last_fc_price - last_hist_price) / last_hist_price * 100) if (last_fc_price and last_hist_price) else None

col1, col2, col3, col4 = st.columns(4)
with col1:
    if last_hist_price:
        st.metric("Harga Terakhir (Des 2025)", f"Rp {last_hist_price:,.0f}")
with col2:
    if last_fc_price:
        st.metric(
            "Proyeksi Des 2027",
            f"Rp {last_fc_price:,.0f}",
            f"{delta_pct:+.1f}%" if delta_pct is not None else None,
        )
with col3:
    if rmse:
        st.metric("RMSE Model", f"Rp {rmse:,.0f}")
with col4:
    if aic:
        st.metric("AIC", f"{aic:.1f}")

st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 9. Section 7: Model interpretation note
# ---------------------------------------------------------------------------
if df_fc is not None and last_hist_price is not None and last_fc_price is not None and delta_pct is not None:
    direction = "naik" if last_fc_price > last_hist_price else "turun" if last_fc_price < last_hist_price else "berubah"
    st.info(f"""
**Interpretasi Model ARIMA({p_val},{d_val},{q_val})**: Model ini menganalisis pola historis harga beras {selected_prov} \
(Jan 2019, Des 2025) untuk memproyeksikan pergerakan harga 24 bulan ke depan. \
Area berbayang menunjukkan rentang ketidakpastian {ci_level}. \
Tanpa intervensi kebijakan, harga diperkirakan {direction} \
sebesar {abs(delta_pct):.1f}% hingga akhir 2027.
""")

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
  Dashboard ini dibuat untuk keperluan akademik, IF4061 Visualisasi Data,
  Institut Teknologi Bandung, Semester 2 2025/2026.
</div>
""", unsafe_allow_html=True)
