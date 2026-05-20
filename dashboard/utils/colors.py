"""
Color constants and theme definitions for the Indonesian Food Security Dashboard.
Dark green / gold / red agricultural theme derived from the original infographic.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Base background palette
# ---------------------------------------------------------------------------
BG_MAIN: str = "#0d1a0e"
BG_PANEL: str = "#152818"
BG_CARD: str = "#1c3319"

# ---------------------------------------------------------------------------
# Border
# ---------------------------------------------------------------------------
BORDER_CARD: str = "#3d7a3d"

# ---------------------------------------------------------------------------
# Accent colors
# ---------------------------------------------------------------------------
ACCENT_GREEN: str = "#7ab528"
ACCENT_GOLD: str = "#d4a520"
ACCENT_RED: str = "#c53030"
ACCENT_ORANGE: str = "#e07820"

# ---------------------------------------------------------------------------
# Text colors
# ---------------------------------------------------------------------------
TEXT_PRIMARY: str = "#f2f7ec"
TEXT_MUTED: str = "#a8c878"
TEXT_DIM: str = "#7a9060"

# ---------------------------------------------------------------------------
# Choropleth map scale colors
# ---------------------------------------------------------------------------
MAP_LOW: str = "#f5e6a3"
MAP_MID: str = "#7ab528"
MAP_HIGH: str = "#1a4a0a"
MAP_CRITICAL: str = "#c53030"

# ---------------------------------------------------------------------------
# K-Means cluster colors (6 visually distinct, accessible on dark bg)
# ---------------------------------------------------------------------------
CLUSTER_COLORS: list[str] = [
    "#7ab528",  # 0 – green
    "#d4a520",  # 1 – gold
    "#4a90d9",  # 2 – blue
    "#c53030",  # 3 – red
    "#b05ec0",  # 4 – purple
    "#e07820",  # 5 – orange
]

# ---------------------------------------------------------------------------
# Island-group colors (for regional breakdown charts)
# ---------------------------------------------------------------------------
ISLAND_COLORS: dict[str, str] = {
    "Sumatera": "#4a90d9",
    "Jawa": "#7ab528",
    "Kalimantan": "#d4a520",
    "Sulawesi": "#e07820",
    "Nusa Tenggara & Bali": "#b05ec0",
    "Maluku": "#4ac9b0",
    "Papua": "#c53030",
}

# ---------------------------------------------------------------------------
# Custom Plotly layout template
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE: dict = {
    "layout": {
        "paper_bgcolor": BG_PANEL,
        "plot_bgcolor": BG_CARD,
        "font": {
            "color": TEXT_PRIMARY,
            "family": "Inter, Segoe UI, sans-serif",
        },
        "title": {
            "font": {"color": TEXT_PRIMARY, "size": 16},
            "x": 0.05,
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
            "bgcolor": BG_PANEL,
            "bordercolor": BORDER_CARD,
            "borderwidth": 1,
            "font": {"color": TEXT_PRIMARY},
        },
        "coloraxis": {
            "colorbar": {
                "tickfont": {"color": TEXT_MUTED},
                "title": {"font": {"color": TEXT_MUTED}},
                "bgcolor": BG_PANEL,
                "bordercolor": BORDER_CARD,
            }
        },
        "hoverlabel": {
            "bgcolor": BG_PANEL,
            "bordercolor": BORDER_CARD,
            "font": {"color": TEXT_PRIMARY},
        },
        "margin": {"l": 40, "r": 20, "t": 50, "b": 40},
    }
}

# ---------------------------------------------------------------------------
# Food-security category colors (IKP / Kerentanan Pangan categories)
# ---------------------------------------------------------------------------
KERENTANAN_COLORS: dict[str, str] = {
    "Sangat Tahan": ACCENT_GREEN,   # #7ab528
    "Tahan": "#4a8a18",
    "Agak Tahan": ACCENT_GOLD,      # #d4a520
    "Agak Rentan": ACCENT_ORANGE,   # #e07820
    "Rentan": "#c07030",
    "Sangat Rentan": ACCENT_RED,    # #c53030
}

# ---------------------------------------------------------------------------
# Continuous colorscale for IKP choropleth
# 0.0 = most food-insecure (red) → 0.5 = moderate (gold) → 1.0 = secure (dark green)
# ---------------------------------------------------------------------------
IKP_COLORSCALE: list[list] = [
    [0.00, MAP_CRITICAL],   # #c53030
    [0.25, ACCENT_ORANGE],  # #e07820
    [0.50, ACCENT_GOLD],    # #d4a520
    [0.75, ACCENT_GREEN],   # #7ab528
    [1.00, MAP_HIGH],       # #1a4a0a
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
    """Return the island-group name for *province_name* (case-insensitive).

    Parameters
    ----------
    province_name:
        Province name as it appears in the dataset (any case).

    Returns
    -------
    str | None
        The island group string (e.g. ``"Jawa"``), or ``None`` if not found.
    """
    return _PROVINCE_TO_ISLAND.get(province_name.upper().strip())
