"""
Color constants and theme definitions for the Indonesian Food Security Dashboard.
Light Corporate / Modern theme — aligned with DESIGN-2.md.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Base background palette
# ---------------------------------------------------------------------------
BG_MAIN: str = "#f7faf6"
BG_PANEL: str = "#f1f4f0"
BG_CARD: str = "#ffffff"

# ---------------------------------------------------------------------------
# Border
# ---------------------------------------------------------------------------
BORDER_CARD: str = "#e2e8f0"

# ---------------------------------------------------------------------------
# Accent colors
# ---------------------------------------------------------------------------
ACCENT_GREEN: str = "#065f46"    # deep emerald (primary-dark)
ACCENT_GOLD: str = "#904d00"     # amber (secondary)
ACCENT_RED: str = "#be123c"      # crimson (error)
ACCENT_ORANGE: str = "#c2410c"   # orange

# ---------------------------------------------------------------------------
# Text colors
# ---------------------------------------------------------------------------
TEXT_PRIMARY: str = "#181c1a"
TEXT_MUTED: str = "#6f7973"
TEXT_DIM: str = "#3f4944"

# ---------------------------------------------------------------------------
# Choropleth map scale colors
# ---------------------------------------------------------------------------
MAP_LOW: str = "#fef2f2"
MAP_MID: str = "#15803d"
MAP_HIGH: str = "#14532d"
MAP_CRITICAL: str = "#be123c"

# ---------------------------------------------------------------------------
# K-Means cluster colors (6 visually distinct, works on light bg)
# ---------------------------------------------------------------------------
CLUSTER_COLORS: list[str] = [
    "#065f46",  # 0 – deep emerald
    "#904d00",  # 1 – amber
    "#1e6ba8",  # 2 – blue
    "#be123c",  # 3 – crimson
    "#7c3aed",  # 4 – purple
    "#c2410c",  # 5 – orange
]

# ---------------------------------------------------------------------------
# Island-group colors (for regional breakdown charts)
# ---------------------------------------------------------------------------
ISLAND_COLORS: dict[str, str] = {
    "Sumatera": "#1e6ba8",
    "Jawa": "#065f46",
    "Kalimantan": "#904d00",
    "Sulawesi": "#c2410c",
    "Nusa Tenggara & Bali": "#7c3aed",
    "Maluku": "#0891b2",
    "Papua": "#be123c",
}

# ---------------------------------------------------------------------------
# Custom Plotly layout template — light theme
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE: dict = {
    "layout": {
        "paper_bgcolor": "#ffffff",
        "plot_bgcolor": "#f7faf6",
        "font": {
            "color": TEXT_PRIMARY,
            "family": "Plus Jakarta Sans, Segoe UI, sans-serif",
        },
        "title": {
            "font": {"color": TEXT_PRIMARY, "size": 15},
            "x": 0.04,
            "xanchor": "left",
            "yanchor": "top",
            "pad": {"t": 12, "l": 8},
        },
        "xaxis": {
            "gridcolor": BORDER_CARD,
            "zerolinecolor": BORDER_CARD,
            "tickcolor": TEXT_MUTED,
            "linecolor": BORDER_CARD,
            "tickfont": {"color": TEXT_MUTED},
        },
        "yaxis": {
            "gridcolor": BORDER_CARD,
            "zerolinecolor": BORDER_CARD,
            "tickcolor": TEXT_MUTED,
            "linecolor": BORDER_CARD,
            "tickfont": {"color": TEXT_MUTED},
        },
        "legend": {
            "bgcolor": "#ffffff",
            "bordercolor": BORDER_CARD,
            "borderwidth": 1,
            "font": {"color": TEXT_PRIMARY},
        },
        "coloraxis": {
            "colorbar": {
                "tickfont": {"color": TEXT_MUTED},
                "title": {"font": {"color": TEXT_MUTED}},
                "bgcolor": "#ffffff",
                "bordercolor": BORDER_CARD,
            }
        },
        "hoverlabel": {
            "bgcolor": "#ffffff",
            "bordercolor": BORDER_CARD,
            "font": {"color": TEXT_PRIMARY},
        },
        "margin": {"l": 60, "r": 36, "t": 72, "b": 52},
    }
}

# ---------------------------------------------------------------------------
# Food-security category colors
# ---------------------------------------------------------------------------
KERENTANAN_COLORS: dict[str, str] = {
    "Sangat Tahan": "#15803d",
    "Tahan": "#16a34a",
    "Agak Tahan": "#ca8a04",
    "Agak Rentan": "#ea580c",
    "Rentan": "#dc2626",
    "Sangat Rentan": "#be123c",
}

# ---------------------------------------------------------------------------
# Continuous colorscale for IKP choropleth
# 0.0 = most food-insecure (crimson) → 1.0 = secure (dark green)
# ---------------------------------------------------------------------------
IKP_COLORSCALE: list[list] = [
    [0.00, MAP_CRITICAL],   # #be123c
    [0.25, ACCENT_ORANGE],  # #c2410c
    [0.50, "#ca8a04"],      # amber
    [0.75, "#16a34a"],      # green
    [1.00, MAP_HIGH],       # #14532d
]

# ---------------------------------------------------------------------------
# Island groups → province name lists
# Province names are stored in UPPER CASE to match typical data sources.
# ---------------------------------------------------------------------------
ISLAND_GROUPS: dict[str, list[str]] = {
    "Sumatera": [
        "ACEH",
        "SUMATERA UTARA",
        "SUMATERA BARAT",
        "RIAU",
        "JAMBI",
        "SUMATERA SELATAN",
        "BENGKULU",
        "LAMPUNG",
        "KEPULAUAN BANGKA BELITUNG",
        "KEPULAUAN RIAU",
    ],
    "Jawa": [
        "DKI JAKARTA",
        "JAWA BARAT",
        "JAWA TENGAH",
        "DAERAH ISTIMEWA YOGYAKARTA",
        "JAWA TIMUR",
        "BANTEN",
    ],
    "Kalimantan": [
        "KALIMANTAN BARAT",
        "KALIMANTAN TENGAH",
        "KALIMANTAN SELATAN",
        "KALIMANTAN TIMUR",
        "KALIMANTAN UTARA",
    ],
    "Sulawesi": [
        "SULAWESI UTARA",
        "SULAWESI TENGAH",
        "SULAWESI SELATAN",
        "SULAWESI TENGGARA",
        "GORONTALO",
        "SULAWESI BARAT",
    ],
    "Nusa Tenggara & Bali": [
        "BALI",
        "NUSA TENGGARA BARAT",
        "NUSA TENGGARA TIMUR",
    ],
    "Maluku": [
        "MALUKU",
        "MALUKU UTARA",
    ],
    "Papua": [
        "PAPUA",
        "PAPUA BARAT",
        "PAPUA SELATAN",
        "PAPUA TENGAH",
        "PAPUA PEGUNUNGAN",
        "PAPUA BARAT DAYA",
    ],
}

# Pre-build reverse lookup: province (upper) → island group name
_PROVINCE_TO_ISLAND: dict[str, str] = {
    province: island
    for island, provinces in ISLAND_GROUPS.items()
    for province in provinces
}


def get_province_island(province_name: str) -> str | None:
    """Return the island-group name for *province_name* (case-insensitive)."""
    return _PROVINCE_TO_ISLAND.get(province_name.upper().strip())
