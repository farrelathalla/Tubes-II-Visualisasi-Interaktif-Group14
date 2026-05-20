import streamlit as st
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Path anchor
_ROOT = Path(__file__).parent.parent  # = dashboard/
_PROCESSED = _ROOT / "data" / "processed"
_ASSETS = _ROOT / "assets"


# ---------------------------------------------------------------------------
# Raw loaders (cached)
# ---------------------------------------------------------------------------

@st.cache_data
def load_ikp() -> pd.DataFrame:
    """Load ikp_all.csv with TAHUN parsed as int."""
    try:
        df = pd.read_csv(_PROCESSED / "ikp_all.csv")
        df["TAHUN"] = df["TAHUN"].astype(int)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load ikp_all.csv: {e}") from e


@st.cache_data
def load_harga_beras() -> pd.DataFrame:
    """Load harga_beras.csv with TANGGAL parsed as datetime, sorted by PROVINSI and TANGGAL."""
    try:
        df = pd.read_csv(_PROCESSED / "harga_beras.csv")
        df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])
        df = df.sort_values(["PROVINSI", "TANGGAL"]).reset_index(drop=True)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load harga_beras.csv: {e}") from e


@st.cache_data
def load_mpp() -> pd.DataFrame:
    """Load mpp_all.csv with TAHUN as int and MPP_TOTAL_PCT as float."""
    try:
        df = pd.read_csv(_PROCESSED / "mpp_all.csv")
        df["TAHUN"] = df["TAHUN"].astype(int)
        df["MPP_TOTAL_PCT"] = df["MPP_TOTAL_PCT"].astype(float)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load mpp_all.csv: {e}") from e


@st.cache_data
def load_produksi() -> pd.DataFrame:
    """Load produksi_padi.csv with numeric columns parsed."""
    try:
        df = pd.read_csv(_PROCESSED / "produksi_padi.csv")
        for col in ["LUAS_PANEN_HA", "PRODUKSI_TON", "PRODUKTIVITAS_KUINTAL_HA"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load produksi_padi.csv: {e}") from e


@st.cache_data
def load_konsumsi() -> pd.DataFrame:
    """Load konsumsi_pangan.csv."""
    try:
        df = pd.read_csv(_PROCESSED / "konsumsi_pangan.csv")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to load konsumsi_pangan.csv: {e}") from e


@st.cache_data
def load_geojson() -> dict:
    """Load indonesia.geojson as a Python dict."""
    try:
        with open(_ASSETS / "indonesia.geojson", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load indonesia.geojson: {e}") from e


# ---------------------------------------------------------------------------
# Derived helpers (no extra cache — underlying data already cached)
# ---------------------------------------------------------------------------

def get_ikp_for_year(year: int) -> pd.DataFrame:
    """Return IKP rows for the given year, sorted by PERINGKAT."""
    df = load_ikp()
    filtered = df[df["TAHUN"] == year].copy()
    return filtered.sort_values("PERINGKAT").reset_index(drop=True)


def get_harga_provinsi(provinsi: str) -> pd.DataFrame:
    """Return harga beras rows for the given province, sorted by TANGGAL."""
    df = load_harga_beras()
    filtered = df[df["PROVINSI"] == provinsi].copy()
    return filtered.sort_values("TANGGAL").reset_index(drop=True)


def get_clustering_features(year: int = 2024) -> pd.DataFrame:
    """
    Join IKP, average harga beras, MPP, and produksi for the given year.

    Result columns: PROVINSI, KODE_PROV, IKP, HARGA_BERAS_AVG,
                    MPP_TOTAL_PCT, JUMLAH_RANTAI, PRODUKSI_TON
    """
    # IKP for the year
    ikp = get_ikp_for_year(year)[["PROVINSI", "KODE_PROV", "IKP"]]

    # Average harga beras for the year
    harga = load_harga_beras().copy()
    harga = harga[harga["TANGGAL"].dt.year == year]
    harga_avg = (
        harga.groupby("PROVINSI", as_index=False)["HARGA_BERAS"]
        .mean()
        .rename(columns={"HARGA_BERAS": "HARGA_BERAS_AVG"})
    )

    # MPP for the year
    mpp = load_mpp()
    mpp_year = mpp[mpp["TAHUN"] == year][["PROVINSI", "MPP_TOTAL_PCT", "JUMLAH_RANTAI"]].copy()

    # Produksi (no year column — single snapshot)
    produksi = load_produksi()[["PROVINSI", "PRODUKSI_TON"]].copy()

    # Inner joins on PROVINSI
    df = ikp.merge(harga_avg, on="PROVINSI", how="inner")
    df = df.merge(mpp_year, on="PROVINSI", how="inner")
    df = df.merge(produksi, on="PROVINSI", how="inner")

    # Drop rows with NaN in key columns
    key_cols = ["IKP", "HARGA_BERAS_AVG", "MPP_TOTAL_PCT", "JUMLAH_RANTAI", "PRODUKSI_TON"]
    df = df.dropna(subset=key_cols).reset_index(drop=True)

    return df[["PROVINSI", "KODE_PROV", "IKP", "HARGA_BERAS_AVG",
               "MPP_TOTAL_PCT", "JUMLAH_RANTAI", "PRODUKSI_TON"]]


def get_mpp_trend() -> pd.DataFrame:
    """
    Pivot mpp_all on TAHUN.

    Returns one row per province with columns:
    PROVINSI, MPP_2019, MPP_2020, MPP_2021, MPP_2024
    """
    mpp = load_mpp()[["PROVINSI", "TAHUN", "MPP_TOTAL_PCT"]].copy()
    pivot = mpp.pivot_table(
        index="PROVINSI", columns="TAHUN", values="MPP_TOTAL_PCT", aggfunc="first"
    ).reset_index()

    # Rename year columns to MPP_<year>
    pivot.columns.name = None
    rename_map = {}
    for col in pivot.columns:
        if col != "PROVINSI":
            rename_map[col] = f"MPP_{col}"
    pivot = pivot.rename(columns=rename_map)

    return pivot


def get_available_years() -> list:
    """Return sorted unique years present in ikp_all."""
    df = load_ikp()
    return sorted(df["TAHUN"].unique().tolist())


def get_provinces_list() -> list:
    """Return sorted unique province names from harga_beras."""
    df = load_harga_beras()
    return sorted(df["PROVINSI"].unique().tolist())


def get_arima_data(provinsi: str) -> pd.DataFrame:
    """
    Return a DataFrame with TANGGAL and HARGA_BERAS columns for the given
    province, suitable for ARIMA fitting.
    """
    df = get_harga_provinsi(provinsi)
    return df[["TANGGAL", "HARGA_BERAS"]].copy()
