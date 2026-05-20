# PLAN.md — Dashboard Interaktif: Ketahanan Pangan Indonesia
## Analisis Spasial-Temporal Distribusi Beras Antar Provinsi

---

## 1. KONSEP & NARASI DASHBOARD

### Judul
**"KETAHANAN PANGAN INDONESIA: Dashboard Analitik Spasial-Temporal Distribusi Beras"**
*Subtitle: Mengungkap Ketimpangan, Memandu Kebijakan*

### Tipe Dashboard
**Dashboard Analitis** — dirancang untuk pengambil kebijakan, peneliti, dan akademisi yang ingin memahami pola ketimpangan ketahanan pangan antar wilayah Indonesia secara mendalam, bukan sekadar memantau angka real-time.

### Pertanyaan Kunci yang Dijawab
1. Bagaimana kondisi ketahanan pangan (IKP) di setiap provinsi, dan ke mana tren-nya?
2. Provinsi mana yang membentuk klaster "rawan" dan apa karakteristiknya?
3. Seberapa besar gap harga beras antara wilayah barat dan timur Indonesia?
4. Ke mana arah harga beras pada 2026–2027 berdasarkan proyeksi ARIMA?
5. 20% wilayah mana yang menyumbang 60%+ masalah ketahanan pangan (Pareto)?
6. Bagaimana hubungan antara MPP (margin distribusi) dan nilai IKP?

### Target Pengguna
- Peneliti & akademisi kebijakan pangan
- Mahasiswa yang mempelajari visualisasi data spasial
- Analis di Badan Pangan Nasional / BPS

---

## 2. TECHNICAL STACK

```
Framework   : Streamlit (Python)
Visualisasi : Plotly Express & Plotly Graph Objects (interaktif utama)
             Folium (choropleth peta Indonesia)
             Streamlit-Folium (embed folium di Streamlit)
Data        : Pandas, NumPy
ML          : Scikit-learn (K-Means, StandardScaler)
Forecasting : Statsmodels (ARIMA)
Peta GeoJSON: Indonesia provinces GeoJSON (publik BPS/naturalearth)
Deployment  : Streamlit Community Cloud (gratis, public URL)
```

---

## 3. SISTEM WARNA & VISUAL

### Palet Warna (diambil dari infografis A4-1)

| Peran | Hex | Digunakan untuk |
|---|---|---|
| Background utama | `#0d1a0e` | Latar seluruh halaman |
| Panel/Card | `#152818` | Container chart, card KPI |
| Border card | `#2d5a2d` | Garis pembatas panel |
| Aksen Hijau Terang | `#7ab528` | Highlight utama, judul, ikon aktif |
| Aksen Emas/Amber | `#d4a520` | Angka KPI, ranking teratas |
| Aksen Merah Kritis | `#c53030` | Zona kritis/rentan, alert |
| Teks Utama | `#e8f0e0` | Body text, label |
| Teks Muted | `#8aaa70` | Subtitle, legend text |
| Peta rendah (IKP) | `#f5e6a3` | Nilai IKP < 50 (kritis) |
| Peta menengah | `#7ab528` | Nilai IKP 60–75 |
| Peta tinggi | `#1a4a0a` | Nilai IKP > 80 (tahan) |

### Tipografi
- **Font utama**: `Inter` atau `Source Sans Pro` (Streamlit default, clean)
- **Judul halaman**: 28px, bold, warna `#7ab528`
- **Judul panel/card**: 16px, semibold, warna `#e8f0e0`
- **Angka KPI**: 36px, bold, warna `#d4a520`
- **Label data**: 12px, regular, warna `#8aaa70`

### Custom CSS (Streamlit)
- Dark background diforce via `st.markdown` dengan CSS injection
- Card menggunakan `border-left: 4px solid #7ab528` untuk aksen
- Metric cards: rounded corners 8px, subtle shadow
- Sidebar dark dengan logo di atas

---

## 4. STRUKTUR HALAMAN (6 HALAMAN)

### Navigasi
Sidebar kiri dengan ikon + label. Active page diberi highlight `#7ab528`. Header tetap di atas dengan nama dashboard dan filter global.

---

### HALAMAN 1: 🌾 Gambaran Umum

**Tujuan**: Memberikan snapshot kondisi IKP nasional dan konteks utama.

#### Layout (F-pattern, top-to-bottom):

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: Judul + Filter Global (Tahun: 2019-2025, Pulau)        │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│ KPI: Avg │ KPI: Min │ KPI: Max │KPI: %    │ KPI: Provinsi      │
│ IKP Nas. │ IKP Prov │ IKP Prov │Sangat    │ Kritis (IKP < 60)  │
│ [angka]  │ [nama]   │ [nama]   │Tahan     │ [jumlah]           │
├──────────┴──────────┴──────────┴──────────┴────────────────────┤
│                                                                 │
│   CHOROPLETH MAP INDONESIA (Plotly + GeoJSON)                   │
│   - Warna gradien dari merah (kritis) → hijau tua (tahan)       │
│   - Hover: nama provinsi, skor IKP, peringkat, kategori         │
│   - Klik provinsi → highlight + detail panel muncul di bawah    │
│   - Zoom & pan enabled                                          │
│                                                                 │
├────────────────────────────┬────────────────────────────────────┤
│  TOP 10 PROVINSI (Bar Hz)  │  BOTTOM 10 PROVINSI (Bar Hz)       │
│  Warna emas (#d4a520)       │  Warna merah (#c53030)             │
│  Sorted desc, label di bar  │  Sorted asc, label di bar          │
└────────────────────────────┴────────────────────────────────────┘
```

**Interaktif:**
- Slider tahun (2019–2025) → peta dan bar berubah dinamis (animasi)
- Dropdown "Pulau" (Sumatera, Jawa, Kalimantan, Sulawesi, Nusa Tenggara, Maluku, Papua) → filter provinsi
- Hover tooltip peta: `{Provinsi} | IKP: {nilai} | Rank: {rank} | Kategori: {label}`
- Click on bar → zoom ke provinsi tersebut di peta

---

### HALAMAN 2: 🔍 Klaster Wilayah (K-Means)

**Tujuan**: Menunjukkan bahwa tidak semua provinsi rawan memiliki masalah yang sama — ada pola klaster.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Intro card: "Masalah Ketahanan Pangan Tidak Sama di Setiap     │
│  Wilayah — K-Means Clustering Mengungkap Polanya"               │
├───────────────────────────┬─────────────────────────────────────┤
│  PANEL KIRI: Kontrol      │  PANEL KANAN: Scatter Plot Klaster  │
│  - Slider K (2–6 klaster) │  - 2D scatter: sumbu X = Harga Beras│
│  - Dropdown: Fitur X, Y   │    sumbu Y = IKP atau MPP           │
│  - Year selector           │  - Titik warna per klaster          │
│  - Multiselect provinsi   │  - Hover: nama provinsi, nilai X, Y │
│                           │  - Legend klaster interaktif         │
├───────────────────────────┴─────────────────────────────────────┤
│  ELBOW METHOD CHART           │  SILHOUETTE SCORE CHART          │
│  - Line chart inertia vs K    │  - Bar chart score per K         │
│  - Annotation di elbow point  │  - Best K highlighted (#d4a520)  │
├───────────────────────────────┴──────────────────────────────────┤
│  TABEL RINGKASAN KLASTER                                         │
│  - Kolom: Klaster | Jumlah Provinsi | Avg IKP | Avg Harga Beras │
│  - Daftar nama provinsi per klaster (expandable)                 │
│  - Row klaster terburuk diberi highlight merah                   │
└──────────────────────────────────────────────────────────────────┘
```

**Interaktif:**
- Slider K → scatter dan tabel otomatis recompute klaster
- Dropdown fitur (Harga Beras, MPP, Produksi Padi, IKP) → ubah sumbu
- Click klaster di legend → isolate klaster (sembunyikan yang lain)
- Hover scatter: nama provinsi + semua nilai fitur

---

### HALAMAN 3: 📈 Tren & Gap Harga Beras

**Tujuan**: Memperlihatkan bahwa gap harga barat-timur tidak pernah mengecil.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Headline card: "Gap harga beras tidak pernah mengecil.         │
│  Papua terus membayar Rp X.XXX lebih mahal dari Lampung."       │
├─────────────────────────────────────────────────────────────────┤
│  FILTER: Multi-select Provinsi │ Year Range Slider              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   LINE CHART MULTI-PROVINSI (Plotly)                            │
│   - Sumbu X: waktu (bulanan 2019–2025)                          │
│   - Sumbu Y: harga beras (Rp/kg)                                │
│   - Tiap provinsi = satu garis, warna dari palet                │
│   - Hover: semua nilai provinsi di titik waktu yang sama         │
│   - Rangeslider di bawah chart untuk zoom temporal              │
│   - Annotation otomatis: puncak kenaikan harga 2022-2023        │
│                                                                  │
├──────────────────────────────────┬──────────────────────────────┤
│  SLOPE GRAPH: Gap Awal vs Akhir  │  GAP CALCULATOR              │
│  - Dua kolom: 2019 | 2025        │  - Dropdown: Provinsi A vs B │
│  - Garis merah = harga naik besar│  - Metric: selisih harga     │
│  - Garis hijau = stabil/turun    │    tahun dipilih             │
│  - Label provinsi di kedua sisi  │  - % lebih mahal vs nasional │
└──────────────────────────────────┴──────────────────────────────┘
```

**Interaktif:**
- Multi-select provinsi (default: 5 provinsi representatif)
- Range slider tahun di atas chart
- Click nama provinsi di slope graph → highlight di line chart
- Hover unified: tooltip menampilkan seluruh provinsi terpilih

---

### HALAMAN 4: 🔮 Proyeksi Harga 2026–2027 (ARIMA)

**Tujuan**: Memperkuat argumen bahwa tanpa intervensi, harga akan terus naik.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Headline: "Harga Tidak Akan Turun Sendiri — ARIMA Membuktikan" │
├────────────────────┬────────────────────────────────────────────┤
│  KONTROL            │  FORECAST CHART (Plotly)                  │
│  - Select Provinsi  │  - Historical line (2019–2025)            │
│    (Papua/Papua Brt)│  - Forecast line (2026–2027) warna emas   │
│  - Confidence level │  - Shaded confidence interval (semi-trans) │
│    (80%, 95%)       │  - Vertical dashed line: batas aktual/fore │
│  - Show/hide CI     │  - Hover: tanggal, harga aktual/prediksi   │
│                     │  - Annotation: "Proyeksi ARIMA (p,d,q)"   │
├────────────────────┴────────────────────────────────────────────┤
│  METRICS ROW:                                                    │
│  [Harga Akhir 2025] [Prediksi Akhir 2027] [Kenaikan %] [RMSE]  │
├─────────────────────────────────────────────────────────────────┤
│  TABEL: Proyeksi Bulanan 2026–2027 (scrollable, download CSV)   │
│  Kolom: Bulan | Prediksi | CI Bawah | CI Atas | Δ vs bulan lalu │
└─────────────────────────────────────────────────────────────────┘
```

**Interaktif:**
- Dropdown provinsi (Papua, Papua Barat) + opsi bandingkan keduanya
- Confidence level slider → CI band melebar/menyempit
- Toggle show/hide historical data
- Download button: ekspor tabel proyeksi ke CSV

---

### HALAMAN 5: 📊 Analisis Prioritas (Pareto)

**Tujuan**: Menunjukkan bahwa intervensi pada ~20% wilayah berdampak >60% perbaikan.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Headline: "Atasi 20% Wilayah → Selesaikan 60% Masalah Pangan" │
├──────────────────────────────────┬──────────────────────────────┤
│  FILTER: Threshold % kumulatif   │  KATEGORI RISIKO (Pie/Donut) │
│  Slider: "Tampilkan hingga X%"   │  - Sangat Tahan, Tahan,      │
│  (default 80%)                   │    Agak Tahan, dst.          │
│                                  │  - Hover: jumlah provinsi    │
├──────────────────────────────────┴──────────────────────────────┤
│                                                                  │
│  PARETO CHART (Bar + Kumulatif Line)                            │
│  - Bar: provinsi terurut dari IKP terendah (most critical first) │
│  - Warna bar: merah (kritis) → kuning → hijau                   │
│  - Line kumulatif: % kontribusi terhadap total "masalah"        │
│  - Dua sumbu Y: IKP (kiri), % kumulatif (kanan)                │
│  - Vertical line: titik 80% threshold                           │
│  - Annotation: "X provinsi ini mewakili 80% total gap IKP"     │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  KONSUMSI PANGAN CHART (Stacked Area / Grouped Bar)             │
│  - Tren kelompok pangan 2018–2024 (Padi-padian, Hewani, dll)   │
│  - Toggle: per komoditas atau per kelompok                      │
│  - Tahun selector                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Interaktif:**
- Slider threshold: ubah garis 80% secara real-time
- Click bar provinsi → highlight di peta (cross-filter ke Halaman 1)
- Toggle: tampilkan berdasarkan skor IKP atau berdasarkan delta IKP (penurunan)
- Hover bar: nama provinsi, IKP, peringkat, kategori kerentanan

---

### HALAMAN 6: 🔗 Ketimpangan Distribusi (MPP & GINI)

**Tujuan**: Menghubungkan ketimpangan distribusi (MPP) dengan nilai IKP provinsi.

#### Layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Headline: "Margin Distribusi Tinggi = Ketahanan Pangan Rendah" │
├───────────────────────────┬─────────────────────────────────────┤
│  KPI: Avg MPP Nasional    │  KPI: Korelasi MPP-IKP (r value)   │
│  KPI: Provinsi MPP > 20%  │  KPI: Jumlah Rantai Distribusi Avg │
├───────────────────────────┴─────────────────────────────────────┤
│  SCATTER PLOT: MPP (X) vs IKP (Y)                               │
│  - Titik = tiap provinsi, ukuran = produksi padi                │
│  - Warna: pulau/wilayah (Sumatera, Jawa, Kalimantan, dll)       │
│  - Regression line dengan annotation r² dan p-value             │
│  - 4 kuadran: MPP rendah+IKP tinggi (ideal) vs sebaliknya       │
│  - Label provinsi outlier (MPP > 25% atau IKP < 60)             │
├───────────────────────────┬─────────────────────────────────────┤
│  BAR CHART: MPP per Prov  │  MULTI-YEAR MPP TREND              │
│  Horizontal, sorted       │  Line chart: 2019, 2020, 2021, 2024 │
│  Color: threshold 20%     │  Select provinsi tertentu           │
│  merah = di atas threshold│  Slope menunjukkan perubahan MPP    │
└───────────────────────────┴─────────────────────────────────────┘
```

**Interaktif:**
- Dropdown: filter per pulau/wilayah → highlight di scatter
- Hover scatter: nama provinsi, MPP %, IKP score, jumlah rantai distribusi
- Click titik scatter → highlight provinsi di peta (link ke halaman 1)
- Year selector untuk bar chart MPP
- Toggle: tampilkan/sembunyikan regression line

---

## 5. KOMPONEN GLOBAL

### Sidebar
```
┌──────────────────┐
│  🌾 [LOGO PADI]  │
│  Ketahanan Pangan│
│  Indonesia       │
├──────────────────┤
│  NAVIGASI:       │
│  ▶ Gambaran Umum │
│    Klaster Prov  │
│    Tren & Gap    │
│    Proyeksi ARIMA│
│    Pareto Prio   │
│    Ketimpangan   │
├──────────────────┤
│  FILTER GLOBAL:  │
│  Tahun: [slider] │
│  Pulau: [select] │
├──────────────────┤
│  TENTANG:        │
│  VSC26101 - IF4061│
│  Group 14        │
└──────────────────┘
```

### Header Global (tiap halaman)
- Breadcrumb: `Dashboard > [Nama Halaman]`
- Tanggal data terakhir diperbarui

### Footer
- Sumber data (BPS, Badan Pangan Nasional, dsb.)
- Link ke GitHub repo

---

## 6. FITUR INTERAKTIF (CHECKLIST SPESIFIKASI)

| Fitur | Implementasi | Halaman |
|---|---|---|
| **Filtering kategori** | Dropdown pulau/provinsi, kategori IKP | Semua |
| **Filtering waktu** | Slider tahun 2019–2025 | 1, 2, 3, 5, 6 |
| **Zooming grafik** | Plotly native zoom + rangeslider | 1, 3, 4 |
| **Zooming peta** | Plotly choropleth zoom + scroll | 1 |
| **Tooltip/Hover** | Custom hover template setiap chart | Semua |
| **Dropdown pilihan** | Provinsi, klaster K, fitur axes | 2, 3, 4, 6 |
| **Slider** | K-Means K value, CI level, threshold Pareto | 2, 4, 5 |
| **Peta interaktif** | Click provinsi, hover info, zoom | 1 |
| **Download data** | CSV export tabel proyeksi ARIMA | 4 |
| **Cross-filter** | Click bar Pareto → highlight peta | 5 → 1 |

---

## 7. DATA PIPELINE

### Preprocessing Steps
1. **IKP data** (`data_ikp_provinsi_2024.csv` + `data_ikp_provinsi_2025.csv`): merge multi-tahun, standardize nama provinsi (UPPERCASE, handle variasi "DI Yogyakarta" dll)
2. **Harga Beras** (per-provinsi xlsx): load semua xlsx, concat ke dataframe tunggal `[Provinsi, Tanggal, Harga_Beras]`, pivot ke wide format untuk slope graph
3. **MPP** (CSV per tahun): merge semua tahun menjadi satu dataframe, tambah kolom `TAHUN`
4. **K-Means**: merge IKP + Harga Beras + MPP + Produksi per provinsi, StandardScaler, run KMeans(k=k)
5. **ARIMA**: load data per provinsi (Papua, Papua Barat), fit ARIMA(p,d,q) via auto_arima atau manual, generate forecast 24 bulan
6. **Konsumsi pangan**: sudah dalam format panjang, filter per kelompok/komoditas/tahun
7. **GeoJSON Indonesia**: download sekali, simpan lokal di `assets/indonesia.geojson`

### File Structure
```
dashboard/
├── app.py                    # Entry point Streamlit
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Clustering.py
│   ├── 3_Price_Trend.py
│   ├── 4_ARIMA.py
│   ├── 5_Pareto.py
│   └── 6_MPP_GINI.py
├── data/
│   ├── processed/            # CSV hasil preprocessing
│   └── raw/ → symlink ke "Sumber Data/"
├── assets/
│   ├── indonesia.geojson
│   ├── logo.png
│   └── style.css
├── utils/
│   ├── data_loader.py        # Semua fungsi load + preprocess
│   ├── charts.py             # Fungsi pembuat chart reusable
│   └── colors.py             # Konstanta warna
└── requirements.txt
```

---

## 8. PRINSIP DESAIN DASHBOARD (HOLISTIK)

| Prinsip | Implementasi |
|---|---|
| **Data-ink ratio tinggi** | Minimise gridlines, no chart junk, background chart gelap semi-transparan |
| **Hierarki visual** | KPI paling besar di atas, detail di bawah, warna utama hanya untuk hal penting |
| **Konsistensi** | Warna klaster konsisten lintas halaman, nama provinsi seragam |
| **Konteks & narasi** | Setiap halaman punya headline card yang menceritakan "temuan utama" |
| **Tidak membingungkan** | Max 3 warna distinktif per chart, label langsung di grafik |
| **Responsif** | Streamlit column layout auto-adjust, cek di layar 1366px dan 1920px |
| **Performa** | `@st.cache_data` untuk semua operasi baca data dan komputasi berat |
| **Aksesibilitas** | Warna dipilih dengan rasio kontras cukup, bukan hanya warna untuk encode klaster |

---

## 9. ESTIMASI FASE PENGERJAAN

### Fase 1 — Data & Environment (1 hari)
- [ ] Setup virtual environment + install dependencies
- [ ] Buat `utils/data_loader.py`: load + clean semua dataset
- [ ] Download GeoJSON Indonesia, simpan ke `assets/`
- [ ] Buat `utils/colors.py` dan inject custom CSS dark theme
- [ ] Test render minimal `app.py` + sidebar

### Fase 2 — Halaman Core (2–3 hari)
- [ ] Halaman 1: Choropleth peta + KPI cards + bar top/bottom
- [ ] Halaman 2: K-Means scatter + elbow + silhouette + tabel
- [ ] Halaman 3: Line chart harga + slope graph + gap calculator

### Fase 3 — Halaman Analitis (1–2 hari)
- [ ] Halaman 4: ARIMA forecast chart + tabel + metrics
- [ ] Halaman 5: Pareto chart + donut kategori + konsumsi area chart
- [ ] Halaman 6: MPP scatter + bar + trend line

### Fase 4 — Polish & Deploy (1 hari)
- [ ] Cross-filter dan integrasi antar halaman
- [ ] Uji coba user (responden target)
- [ ] Fix responsivitas dan performa (`st.cache_data`)
- [ ] Deploy ke Streamlit Community Cloud
- [ ] Test URL publik dapat diakses tanpa login

---

## 10. REFERENSI VISUAL

- **Infografis asli (A4-1.jpg)**: referensi palet warna, tone editorial, section numbering style
- **Dashboard INDEEP (image.png)**: referensi layout dark dashboard, KPI strip, multi-panel grid, navigation tab, numbered section
- **Plotly dark theme**: `template="plotly_dark"` sebagai base, customized dengan warna infografis
