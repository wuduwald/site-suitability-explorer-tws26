"""
App configuration for Site Suitability App.
This file is auto-generated from 03_app_config.ipynb.
DO NOT edit manually unless you know what you're doing.
"""

# -----------------------------
# DATASETS
# -----------------------------
DATASETS = {
    "full": {
        "label": "2018–2024 (Full History)",
        "path": "/content/data/derived/weekly_spatial_full_history.csv",
        "description": "All available historical data (2018–2024). Best for long-term patterns.",
    },
    "last4y": {
        "label": "2021–2024 (Last 4 Years)",
        "path": "/content/data/derived/weekly_spatial_last4y.csv",
        "description": "Recent multi-year view. Balances recency and stability.",
    },
    "2024": {
        "label": "2024 Only",
        "path": "/content/data/derived/weekly_spatial_2024.csv",
        "description": "Single-year view. Best for short-term planning and validation.",
    },
}

DEFAULT_DATASET_KEY = "full"


# -----------------------------
# VARIABLES
# -----------------------------
VARIABLES = {

    # --- SUITABILITY (dimensionless, daytime-derived) ---
    "suitability": {
        "column": "pct_viability",
        "rank_column": "suitability_rank",
        "label": "Overall Suitability",
        "description": "Overall weekly suitability (all constraints combined).",
        "time_window": "08:00–18:00",
        "unit": None,
        "value_format": ".2f",
        "colorscale": "rdylgn",
        "vmin": 0.0,
        "vmax": 1.0,
        "allow_rank_overlay": True,
        "allow_value_overlay": False,
        "allow_winner_strip": True,
        "default_overlay": "winner",
    },

    "suitability_temp": {
        "column": "pct_t2m_08_18",
        "rank_column": "suitability_temp_rank",
        "label": "Temperature Suitability",
        "description": "Percentage of workable temperature conditions.",
        "time_window": "08:00–18:00",
        "unit": None,
        "value_format": ".2f",
        "colorscale": "rdylgn",
        "vmin": 0.0,
        "vmax": 1.0,
        "allow_rank_overlay": True,
        "allow_value_overlay": False,
        "allow_winner_strip": True,
        "default_overlay": "rank",
    },

    "suitability_humidity": {
        "column": "pct_rh_08_18",
        "rank_column": "suitability_rh_rank",
        "label": "Humidity Suitability",
        "description": "Percentage of workable humidity conditions.",
        "time_window": "08:00–18:00",
        "unit": None,
        "value_format": ".2f",
        "colorscale": "rdylgn",
        "vmin": 0.0,
        "vmax": 1.0,
        "allow_rank_overlay": True,
        "allow_value_overlay": False,
        "allow_winner_strip": True,
        "default_overlay": "rank",
    },

    "suitability_wind": {
        "column": "pct_wind_max",
        "rank_column": "suitability_wind_rank",
        "label": "Wind Suitability",
        "description": "Percentage of workable wind conditions.",
        "time_window": None,  # derived from 24-hour wind maxima
        "unit": None,
        "value_format": ".2f",
        "colorscale": "rdylgn",
        "vmin": 0.0,
        "vmax": 1.0,
        "allow_rank_overlay": True,
        "allow_value_overlay": False,
        "allow_winner_strip": True,
        "default_overlay": "rank",
    },

    # --- TEMPERATURE (°C) ---
    "temperature_mean": {
        "column": "t2m_mean_08_18",
        "label": "Mean Temperature",
        "description": "Mean daytime temperature.",
        "time_window": "08:00–18:00",
        "unit": "°C",
        "value_format": ".1f",
        "colorscale": "rdylbu_r",
        "vmin": 0,
        "vmax": 35,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    "temperature_absmin": {
        "column": "t2m_absmin_08_18",
        "label": "Absolute Minimum Temperature",
        "description": "Worst-case minimum temperature observed.",
        "time_window": None,
        "unit": "°C",
        "value_format": ".1f",
        "colorscale": "rdylbu_r",
        "vmin": -30,
        "vmax": 20,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    "temperature_absmax": {
        "column": "t2m_absmax_08_18",
        "label": "Absolute Maximum Temperature",
        "description": "Worst-case maximum temperature observed.",
        "time_window": None,
        "unit": "°C",
        "value_format": ".1f",
        "colorscale": "rdylbu_r",
        "vmin": 20,
        "vmax": 45,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    # --- HUMIDITY (%) ---
    "humidity_mean": {
        "column": "rh_mean_08_18",
        "label": "Mean Humidity",
        "description": "Mean daytime relative humidity.",
        "time_window": "08:00–18:00",
        "unit": "%",
        "value_format": ".0f",
        "colorscale": "blues",
        "vmin": 40,
        "vmax": 100,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    "humidity_absmax": {
        "column": "rh_absmax_08_18",
        "label": "Maximum Humidity",
        "description": "Worst-case relative humidity observed.",
        "time_window": None,
        "unit": "%",
        "value_format": ".0f",
        "colorscale": "blues",
        "vmin": 60,
        "vmax": 100,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    # --- WIND (m/s, 24-hour) ---
    "wind_mean": {
        "column": "wind_mean",
        "label": "Mean Wind Speed",
        "description": "Mean wind speed.",
        "time_window": None,  # 24-hour mean
        "unit": "m/s",
        "value_format": ".1f",
        "colorscale": "greens",
        "vmin": 0,
        "vmax": 12,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },

    "wind_absmax": {
        "column": "wind_absmax",
        "label": "Maximum Wind Speed",
        "description": "Worst-case wind speed observed.",
        "time_window": None,  # 24-hour max
        "unit": "m/s",
        "value_format": ".1f",
        "colorscale": "greens",
        "vmin": 0,
        "vmax": 25,
        "allow_rank_overlay": False,
        "allow_value_overlay": True,
        "allow_winner_strip": False,
        "default_overlay": "value",
    },
}

DEFAULT_VARIABLE_KEY = "suitability"


# -----------------------------
# OVERLAY MODES
# -----------------------------
OVERLAY_MODES = {
    "none": {
        "label": "No Overlay",
        "description": "Show heatmap only.",
    },
    "value": {
        "label": "Value",
        "description": "Display the raw value in each cell.",
    },
    "rank": {
        "label": "Rank",
        "description": "Display per-week dense rank (1 = best).",
    },
    "winner": {
        "label": "Winner",
        "description": "Highlight the best site per week.",
    },
}


# -----------------------------
# APP DEFAULTS
# -----------------------------
APP_DEFAULTS = {
    "dataset": "full",
    "variable": "suitability",
    "overlay": "winner",
    "show_colorbar": True,
    "sort_sites_alphabetically": True,
}
