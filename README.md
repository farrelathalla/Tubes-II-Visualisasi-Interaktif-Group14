# Ketahanan Pangan Indonesia Dashboard

Dashboard analitik spasial-temporal distribusi beras Indonesia.  
**IF4061 Visualisasi Data** | Semester 2 2025/2026 | VSC26101 Group 14

---

## Fitur

| Halaman | Deskripsi |
|---|---|
| **Gambaran Umum** | Peta choropleth IKP 38 provinsi + tabel peringkat |
| **Klaster Wilayah** | Segmentasi provinsi dengan K-Means (5 indikator) |
| **Tren & Gap Harga** | Slope chart harga beras + kalkulator gap wilayah |
| **Proyeksi ARIMA** | Forecast harga beras 2026–2027 per provinsi |
| **Analisis Pareto** | Identifikasi provinsi prioritas (prinsip 80/20) |
| **Distribusi MPP** | Analisis margin perdagangan & pengangkutan beras |

## Cara Menjalankan

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/Home.py
```

## Struktur Proyek

```
dashboard/
├── Home.py                  # Landing page
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Clustering.py
│   ├── 3_Price_Trend.py
│   ├── 4_ARIMA.py
│   ├── 5_Pareto.py
│   └── 6_MPP_GINI.py
├── utils/
│   ├── charts.py            # Plotly chart factory
│   ├── colors.py            # Design tokens & theme
│   └── data_loader.py       # Data loading & caching
├── assets/
│   ├── style.css            # Global stylesheet
│   └── icons/               # Nav card icons (png/jpg/svg)
└── data/                    # Dataset (CSV)
```

## Sumber Data

- **BPS** — Badan Pusat Statistik
- **Badan Pangan Nasional (NFA)** — Indeks Ketahanan Pangan (IKP)
- **Panel Harga Pangan** — Kementerian Pertanian
