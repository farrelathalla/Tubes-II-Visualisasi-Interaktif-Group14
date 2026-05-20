"""
preprocess.py — Standalone script to preprocess raw data into clean CSVs.

Run from any directory:
    python dashboard/data/preprocess.py

Outputs (written to dashboard/data/processed/):
    ikp_all.csv
    harga_beras.csv
    mpp_all.csv
    produksi_padi.csv
    konsumsi_pangan.csv
"""

import os
import re
import sys
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# dashboard/data/  -> go up two levels to project root, then into Sumber Data
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_BASE = os.path.join(PROJECT_ROOT, "Sumber Data")
OUT_DIR = os.path.join(SCRIPT_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Province name normalisation
# ---------------------------------------------------------------------------
_PROV_OVERRIDES = {
    "DI YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    "D.I. YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    "DI_YOGYAKARTA": "DAERAH ISTIMEWA YOGYAKARTA",
    "DI. ACEH": "ACEH",
    "D.I. ACEH": "ACEH",
    "BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "KEP. BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "KEPULAUAN BANGKA BELITUNG": "KEPULAUAN BANGKA BELITUNG",
    "KEP. RIAU": "KEPULAUAN RIAU",
    "KEPULAUAN RIAU": "KEPULAUAN RIAU",
    "DKI JAKARTA": "DKI JAKARTA",
}


def normalise_province(name: str) -> str:
    """Uppercase and apply standard name overrides."""
    if not isinstance(name, str):
        return name
    cleaned = name.strip().upper()
    return _PROV_OVERRIDES.get(cleaned, cleaned)


def filename_to_province(stem: str) -> str:
    """
    Convert an xlsx stem like 'DI_Yogyakarta' -> 'DAERAH ISTIMEWA YOGYAKARTA'.
    General rule: replace underscores with spaces, uppercase, then apply overrides.
    """
    raw = stem.replace("_", " ").upper()
    return _PROV_OVERRIDES.get(raw, raw)


# ---------------------------------------------------------------------------
# IKP group derivation for 2025 data
# ---------------------------------------------------------------------------
def derive_ikp_group(ikp: float):
    """Return (kelompok_int, kerentanan_str) from IKP score."""
    if ikp >= 80:
        return 6, "Sangat Tahan"
    elif ikp >= 70:
        return 5, "Tahan"
    elif ikp >= 60:
        return 4, "Agak Tahan"
    elif ikp >= 50:
        return 3, "Agak Rentan"
    elif ikp >= 40:
        return 2, "Rentan"
    else:
        return 1, "Sangat Rentan"


# ---------------------------------------------------------------------------
# A) ikp_all.csv
# ---------------------------------------------------------------------------
def process_ikp():
    print("\n[IKP] Processing IKP data...")

    # --- 2019-2024 from Pareto Analysis file ---
    path_2024 = os.path.join(RAW_BASE, "[5] Pareto Analysis", "IKP", "data_ikp_provinsi_2024.csv")
    # Also check if [1] has older years as fallback
    path_2025 = os.path.join(RAW_BASE, "[1] Indeks Ketahanan Pangan", "data_ikp_provinsi_2025.csv")

    frames = []

    if os.path.exists(path_2024):
        df24 = pd.read_csv(path_2024)
        # Rename columns to standard names
        df24 = df24.rename(columns={
            "KODE PROV": "KODE_PROV",
            "Kelompok IKP": "KELOMPOK_IKP",
            "Kerentanan Area": "KERENTANAN",
        })
        # Drop NO column if present
        df24 = df24.drop(columns=["NO"], errors="ignore")
        df24["PROVINSI"] = df24["PROVINSI"].apply(normalise_province)
        frames.append(df24[["KODE_PROV", "PROVINSI", "TAHUN", "IKP", "PERINGKAT", "KELOMPOK_IKP", "KERENTANAN"]])
        print(f"  Loaded 2019-2024 data: {len(df24)} rows, years {sorted(df24['TAHUN'].unique())}")
    else:
        print(f"  WARNING: {path_2024} not found, skipping 2019-2024 IKP data")

    if os.path.exists(path_2025):
        df25 = pd.read_csv(path_2025)
        df25 = df25.rename(columns={"KODE PROV": "KODE_PROV"})
        df25["PROVINSI"] = df25["PROVINSI"].apply(normalise_province)
        # Derive group and kerentanan for 2025
        groups = df25["IKP"].apply(derive_ikp_group)
        df25["KELOMPOK_IKP"] = [g[0] for g in groups]
        df25["KERENTANAN"] = [g[1] for g in groups]
        frames.append(df25[["KODE_PROV", "PROVINSI", "TAHUN", "IKP", "PERINGKAT", "KELOMPOK_IKP", "KERENTANAN"]])
        print(f"  Loaded 2025 data: {len(df25)} rows")
    else:
        print(f"  WARNING: {path_2025} not found, skipping 2025 IKP data")

    if not frames:
        print("  ERROR: No IKP data found, skipping ikp_all.csv")
        return

    ikp_all = pd.concat(frames, ignore_index=True)
    ikp_all = ikp_all.sort_values(["PROVINSI", "TAHUN"]).reset_index(drop=True)

    out_path = os.path.join(OUT_DIR, "ikp_all.csv")
    ikp_all.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(ikp_all)} rows)")


# ---------------------------------------------------------------------------
# B) harga_beras.csv
# ---------------------------------------------------------------------------
_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def parse_price(val):
    """Parse '12,550' -> 12550.0; handle NaN / non-numeric."""
    if pd.isna(val):
        return np.nan
    s = str(val).replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def parse_col_to_date(col_name: str):
    """Parse 'Jan  2019' -> pd.Timestamp('2019-01-01') or None."""
    parts = col_name.strip().split()
    if len(parts) < 2:
        return None
    month_str = parts[0].lower()
    year_str = parts[-1]
    month = _MONTH_MAP.get(month_str)
    if month is None:
        return None
    try:
        year = int(year_str)
    except ValueError:
        return None
    return pd.Timestamp(year=year, month=month, day=1)


def process_harga_beras():
    print("\n[Harga Beras] Processing rice price data...")

    beras_dir = os.path.join(RAW_BASE, "[2] K-Means Clustering", "Harga Beras Provinsi 2019-2025")
    if not os.path.exists(beras_dir):
        print(f"  WARNING: {beras_dir} not found, skipping harga_beras.csv")
        return

    all_rows = []
    xlsx_files = [f for f in os.listdir(beras_dir) if f.endswith(".xlsx")]
    print(f"  Found {len(xlsx_files)} province files")

    for fname in sorted(xlsx_files):
        stem = os.path.splitext(fname)[0]
        province = filename_to_province(stem)
        fpath = os.path.join(beras_dir, fname)
        try:
            df = pd.read_excel(fpath)
        except Exception as e:
            print(f"  WARNING: Could not read {fname}: {e}")
            continue

        # Filter to the aggregate 'Beras' row (index I, not the sub-types)
        # It's the row where 'Komoditas (Rp)' == 'Beras'
        komoditas_col = "Komoditas (Rp)"
        if komoditas_col not in df.columns:
            print(f"  WARNING: '{komoditas_col}' column not found in {fname}, skipping")
            continue

        beras_row = df[df[komoditas_col].astype(str).str.strip() == "Beras"]
        if beras_row.empty:
            print(f"  WARNING: No 'Beras' row found in {fname}, skipping")
            continue
        beras_row = beras_row.iloc[0]

        # Iterate over month columns
        for col in df.columns:
            date = parse_col_to_date(str(col))
            if date is None:
                continue
            price = parse_price(beras_row[col])
            if not np.isnan(price):
                all_rows.append({
                    "PROVINSI": province,
                    "TANGGAL": date.strftime("%Y-%m-%d"),
                    "HARGA_BERAS": price,
                })

    if not all_rows:
        print("  ERROR: No rice price rows parsed")
        return

    harga_beras = pd.DataFrame(all_rows)
    harga_beras = harga_beras.sort_values(["PROVINSI", "TANGGAL"]).reset_index(drop=True)

    out_path = os.path.join(OUT_DIR, "harga_beras.csv")
    harga_beras.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(harga_beras)} rows, {harga_beras['PROVINSI'].nunique()} provinces)")


# ---------------------------------------------------------------------------
# C) mpp_all.csv
# ---------------------------------------------------------------------------
def _load_mpp_file(fpath: str, year: int) -> pd.DataFrame | None:
    """
    Load a single MPP CSV file. The file has a 3-row header preamble:
      row 0: NaN, long title, NaN
      row 1: NaN, 'Margin Perdagangan.../MPP Total (%)', 'Jumlah Rantai Utama'
      row 2: NaN, <year>, <year>
      row 3+: PROVINCE, value, value
    """
    try:
        df = pd.read_csv(fpath, header=None)
    except Exception as e:
        print(f"  WARNING: Could not read {fpath}: {e}")
        return None

    # Skip the first 3 header rows (rows 0,1,2)
    data = df.iloc[3:].copy()
    data.columns = ["PROVINSI", "MPP_TOTAL_PCT", "JUMLAH_RANTAI"]
    data = data.dropna(subset=["PROVINSI"])

    # Remove INDONESIA aggregate row
    data = data[data["PROVINSI"].str.strip().str.upper() != "INDONESIA"]

    # Normalise province names
    data["PROVINSI"] = data["PROVINSI"].apply(normalise_province)

    # Convert numeric columns
    def to_numeric_safe(val):
        if pd.isna(val) or str(val).strip() in ("-", ""):
            return np.nan
        try:
            return float(str(val).replace(",", "").strip())
        except ValueError:
            return np.nan

    data["MPP_TOTAL_PCT"] = data["MPP_TOTAL_PCT"].apply(to_numeric_safe)
    data["JUMLAH_RANTAI"] = data["JUMLAH_RANTAI"].apply(to_numeric_safe)
    data["TAHUN"] = year

    return data[["PROVINSI", "TAHUN", "MPP_TOTAL_PCT", "JUMLAH_RANTAI"]].reset_index(drop=True)


def process_mpp():
    print("\n[MPP] Processing MPP data...")

    # 2024 from K-Means Clustering folder
    sources = [
        (os.path.join(RAW_BASE, "[2] K-Means Clustering", "MPP",
                      "Margin Perdagangan dan Pengangkutan (MPP) Komoditas Beras Menurut Provinsi, 2024.csv"), 2024),
        (os.path.join(RAW_BASE, "[6] Indeks GINI", "MPP",
                      "Margin Perdagangan dan Pengangkutan (MPP) Komoditas Beras Menurut Provinsi, 2019.csv"), 2019),
        (os.path.join(RAW_BASE, "[6] Indeks GINI", "MPP",
                      "Margin Perdagangan dan Pengangkutan (MPP) Komoditas Beras Menurut Provinsi, 2020.csv"), 2020),
        (os.path.join(RAW_BASE, "[6] Indeks GINI", "MPP",
                      "Margin Perdagangan dan Pengangkutan (MPP) Komoditas Beras Menurut Provinsi, 2021.csv"), 2021),
    ]

    frames = []
    for fpath, year in sources:
        if not os.path.exists(fpath):
            print(f"  WARNING: {os.path.basename(fpath)} not found, skipping year {year}")
            continue
        df = _load_mpp_file(fpath, year)
        if df is not None and not df.empty:
            frames.append(df)
            print(f"  Loaded MPP {year}: {len(df)} provinces")

    if not frames:
        print("  ERROR: No MPP data loaded, skipping mpp_all.csv")
        return

    mpp_all = pd.concat(frames, ignore_index=True)
    mpp_all = mpp_all.sort_values(["TAHUN", "PROVINSI"]).reset_index(drop=True)

    out_path = os.path.join(OUT_DIR, "mpp_all.csv")
    mpp_all.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(mpp_all)} rows)")


# ---------------------------------------------------------------------------
# D) produksi_padi.csv
# ---------------------------------------------------------------------------
def process_produksi_padi():
    print("\n[Produksi Padi] Processing paddy production data...")

    fpath = os.path.join(
        RAW_BASE,
        "[2] K-Means Clustering",
        "Panen, Produksi, Produktivitas Padi",
        "Luas Panen, Produksi, dan Produktivitas Padi Menurut Provinsi, 2024.csv",
    )
    if not os.path.exists(fpath):
        print(f"  WARNING: {fpath} not found, skipping produksi_padi.csv")
        return

    # The file has 4 rows of header preamble before data starts:
    #   row 0: "38 Provinsi", NaN, NaN, NaN
    #   row 1: NaN, title, NaN, NaN
    #   row 2: NaN, "Luas Panen (ha)", "Produktivitas (ku/ha)", "Produksi (ton)"
    #   row 3: NaN, 2024, 2024, 2024
    #   row 4+: data
    df = pd.read_csv(fpath, header=None, skiprows=4)
    df.columns = ["PROVINSI", "LUAS_PANEN_HA", "PRODUKTIVITAS_KUINTAL_HA", "PRODUKSI_TON"]

    # Drop NaN province rows and INDONESIA aggregate
    df = df.dropna(subset=["PROVINSI"])
    df = df[df["PROVINSI"].str.strip().str.upper() != "INDONESIA"]

    df["PROVINSI"] = df["PROVINSI"].apply(normalise_province)

    # Ensure numeric
    for col in ["LUAS_PANEN_HA", "PRODUKSI_TON", "PRODUKTIVITAS_KUINTAL_HA"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[["PROVINSI", "LUAS_PANEN_HA", "PRODUKSI_TON", "PRODUKTIVITAS_KUINTAL_HA"]].reset_index(drop=True)

    out_path = os.path.join(OUT_DIR, "produksi_padi.csv")
    df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(df)} rows)")


# ---------------------------------------------------------------------------
# E) konsumsi_pangan.csv
# ---------------------------------------------------------------------------
def process_konsumsi_pangan():
    print("\n[Konsumsi Pangan] Processing food consumption data...")

    fpath = os.path.join(
        RAW_BASE,
        "[5] Pareto Analysis",
        "Konsumsi Pangan 2019-2024",
        "Konsumi Pangan 2019-2025.csv",
    )
    if not os.path.exists(fpath):
        print(f"  WARNING: {fpath} not found, skipping konsumsi_pangan.csv")
        return

    df = pd.read_csv(fpath)
    # Rename columns to standard names
    df = df.rename(columns={
        "No": "NO",
        "Kelompok Bahan Pangan": "KELOMPOK",
        "Komoditas": "KOMODITAS",
        "konsumsi_pangan": "KONSUMSI",
        "Satuan": "SATUAN",
        "Tahun": "TAHUN",
    })
    df = df[["NO", "KELOMPOK", "KOMODITAS", "KONSUMSI", "SATUAN", "TAHUN"]]

    out_path = os.path.join(OUT_DIR, "konsumsi_pangan.csv")
    df.to_csv(out_path, index=False)
    print(f"  Saved: {out_path}  ({len(df)} rows)")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def preprocess():
    print("=" * 60)
    print("Preprocessing Ketahanan Pangan raw data")
    print(f"  Raw base : {RAW_BASE}")
    print(f"  Output   : {OUT_DIR}")
    print("=" * 60)

    process_ikp()
    process_harga_beras()
    process_mpp()
    process_produksi_padi()
    process_konsumsi_pangan()

    print("\n" + "=" * 60)
    print("Done. Files written to:", OUT_DIR)
    generated = os.listdir(OUT_DIR)
    for f in sorted(generated):
        fpath = os.path.join(OUT_DIR, f)
        size_kb = os.path.getsize(fpath) // 1024
        print(f"  {f}  ({size_kb} KB)")
    print("=" * 60)


if __name__ == "__main__":
    preprocess()
