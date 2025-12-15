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
    """
    Normalize column names to snake_case lowercase.
    """
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
    """
    path = DIMENSIONS_DIR / "sites_fixed.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    sites = pd.read_csv(path)
    sites = _normalize_columns(sites)

    required = {"site_id", "site_name", "state"}
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
    """
    Load raw weekly environmental metrics for a given time window.
    """
    if window not in _METRIC_DATASETS:
        raise ValueError(
            f"Unknown window '{window}'. Choose from {list(_METRIC_DATASETS)}"
        )

    path = METRICS_DIR / _METRIC_DATASETS[window]
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)
    df = _normalize_columns(df)

    # ---- Normalize week column name ----
    if "week_bin" not in df.columns and "week_index" in df.columns:
        df = df.rename(columns={"week_index": "week_bin"})

    required = {"site_id", "week_bin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Metrics dataset missing columns: {missing}")

    return df


# -----------------------------
# Load spatial / suitability data
# -----------------------------
def load_weekly_spatial(window: str) -> pd.DataFrame:
    """
    Load derived weekly spatial suitability data for a given time window.
    """
    if window not in _SPATIAL_DATASETS:
        raise ValueError(
            f"Unknown window '{window}'. Choose from {list(_SPATIAL_DATASETS)}"
        )

    path = DERIVED_DIR / _SPATIAL_DATASETS[window]
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)
    df = _normalize_columns(df)

    required = {"site_id", "week_bin"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Spatial dataset missing columns: {missing}")

    return df


# -----------------------------
# Unified loader (most common entry point)
# -----------------------------
def load_with_sites(
    kind: str,
    window: str
) -> pd.DataFrame:
    """
    Load a dataset and join site metadata.

    Parameters
    ----------
    kind : "metrics" or "spatial"
    window : "2024", "last4y", or "full"
    """
    sites = load_sites()

    if kind == "metrics":
        df = load_weekly_metrics(window)
    elif kind == "spatial":
        df = load_weekly_spatial(window)
    else:
        raise ValueError("kind must be 'metrics' or 'spatial'")

    # -------------------------------------------------
    # Enforce authoritative site metadata
    # -------------------------------------------------
    for col in ["site_name", "state"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df = df.merge(
        sites[["site_id", "site_name", "state"]],
        on="site_id",
        how="left",
        validate="many_to_one",
    )

    if df[["site_name", "state"]].isna().any().any():
        raise ValueError(
            "Some site_id values could not be mapped to sites_fixed.csv"
        )

    return df
