"""
data_loader.py

Responsible ONLY for:
- Loading CSV data
- Normalizing column names
- Joining site metadata (sites_fixed.csv)
- Selecting datasets by time window

NO business logic
NO thresholds
NO suitability rules
"""

from pathlib import Path
import pandas as pd


# -----------------------------
# Project paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
DIMENSIONS_DIR = DATA_DIR / "dimensions"
METRICS_DIR = DATA_DIR / "metrics"
DERIVED_DIR = DATA_DIR / "derived"


# -----------------------------
# Utility helpers
# -----------------------------
def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


# -----------------------------
# Load dimension table
# -----------------------------
def load_sites() -> pd.DataFrame:
    """
    Load sites_fixed.csv (authoritative site dimension table).
    Normalizes latitude / longitude naming.
    """
    path = DIMENSIONS_DIR / "sites_fixed.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    sites = pd.read_csv(path)
    sites = _normalize_columns(sites)

    # -----------------------------
    # Normalize coordinate columns
    # -----------------------------
    rename_map = {}

    if "lat" in sites.columns:
        rename_map["lat"] = "latitude"
    if "latitude_deg" in sites.columns:
        rename_map["latitude_deg"] = "latitude"

    if "lon" in sites.columns:
        rename_map["lon"] = "longitude"
    if "lng" in sites.columns:
        rename_map["lng"] = "longitude"
    if "long" in sites.columns:
        rename_map["long"] = "longitude"
    if "longitude_deg" in sites.columns:
        rename_map["longitude_deg"] = "longitude"

    if rename_map:
        sites = sites.rename(columns=rename_map)

    # -----------------------------
    # Hard validation
    # -----------------------------
    required = {"site_id", "site_name", "state", "latitude", "longitude"}
    missing = required - set(sites.columns)
    if missing:
        raise ValueError(f"sites_fixed.csv missing columns: {missing}")

    return sites


# -----------------------------
# Dataset registry
# -----------------------------
_METRIC_DATASETS = {
    "2024": "Weekly_Master_2024.csv",
    "last4y": "Weekly_Master_4y.csv",
    "full": "Weekly_Master_2018_2024.csv",
}

_SPATIAL_DATASETS = {
    "2024": "weekly_spatial_2024.csv",
    "last4y": "weekly_spatial_last4y.csv",
    "full": "weekly_spatial_full_history.csv",
}


# -----------------------------
# Load metric data
# -----------------------------
def load_weekly_metrics(window: str) -> pd.DataFrame:
    if window not in _METRIC_DATASETS:
        raise ValueError(f"Unknown window '{window}'")

    path = METRICS_DIR / _METRIC_DATASETS[window]
    df = _normalize_columns(pd.read_csv(path))

    if "week_bin" not in df.columns and "week_index" in df.columns:
        df = df.rename(columns={"week_index": "week_bin"})

    return df


# -----------------------------
# Load spatial data
# -----------------------------
def load_weekly_spatial(window: str) -> pd.DataFrame:
    if window not in _SPATIAL_DATASETS:
        raise ValueError(f"Unknown window '{window}'")

    path = DERIVED_DIR / _SPATIAL_DATASETS[window]
    df = _normalize_columns(pd.read_csv(path))

    return df


# -----------------------------
# Unified loader
# -----------------------------
def load_with_sites(kind: str, window: str) -> pd.DataFrame:
    sites = load_sites()

    if kind == "metrics":
        df = load_weekly_metrics(window)
    elif kind == "spatial":
        df = load_weekly_spatial(window)
    else:
        raise ValueError("kind must be 'metrics' or 'spatial'")

    # Drop any stale metadata
    for col in ("site_name", "state", "latitude", "longitude"):
        if col in df.columns:
            df = df.drop(columns=[col])

    # Merge authoritative metadata
    df = df.merge(
        sites[
            ["site_id", "site_name", "state", "latitude", "longitude"]
        ],
        on="site_id",
        how="left",
        validate="many_to_one",
    )

    # Hard validation
    if df[["site_name", "state", "latitude", "longitude"]].isna().any().any():
        raise ValueError(
            "Some site_id values could not be mapped to sites_fixed.csv"
        )

    return df
