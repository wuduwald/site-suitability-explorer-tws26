"""
transforms.py

Pure data transformations only.

Responsibilities:
- Filter data by week
- Aggregate across years (if needed)
- Build site × week matrices
- Normalize values per week
- Compute ranks (optional)
- Compute mean value per site (planning / prioritisation)
- Classify suitability values (for maps / alerts)

NO visualization logic
NO thresholds hardcoded (config-driven)
NO Streamlit / Plotly imports
"""

import pandas as pd
from app.config import SUITABILITY_CLASSES


# -----------------------------
# Filtering
# -----------------------------
def filter_weeks(
    df: pd.DataFrame,
    weeks: list[int] | None = None
) -> pd.DataFrame:
    """
    Filter dataframe to a subset of weeks.
    """
    if weeks is None:
        return df

    return df[df["week_bin"].isin(weeks)].copy()


# -----------------------------
# Aggregation
# -----------------------------
def aggregate_site_week(
    df: pd.DataFrame,
    value_col: str,
    agg: str = "mean"
) -> pd.DataFrame:
    """
    Aggregate values by site and week.

    Parameters
    ----------
    value_col : column to aggregate
    agg : aggregation method ("mean", "median", "max", etc.)
    """
    if value_col not in df.columns:
        raise ValueError(f"Column '{value_col}' not found")

    return (
        df
        .groupby(["site_name", "week_bin"], as_index=False)
        .agg({value_col: agg})
    )


# -----------------------------
# Matrix construction
# -----------------------------
def build_site_week_matrix(
    df: pd.DataFrame,
    value_col: str
) -> pd.DataFrame:
    """
    Build a site × week matrix WITHOUT dropping sparse sites.

    Preserves:
    - all sites present in df
    - all weeks present in df
    - rows that are entirely NaN
    """
    required = {"site_name", "week_bin", value_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for matrix build: {missing}")

    # Explicit axes
    sites = (
        df[["site_name"]]
        .drop_duplicates()
        .sort_values("site_name")
        ["site_name"]
    )

    weeks = (
        df[["week_bin"]]
        .drop_duplicates()
        .sort_values("week_bin")
        ["week_bin"]
    )

    matrix = df.pivot(
        index="site_name",
        columns="week_bin",
        values=value_col
    )

    # Reindex to prevent silent row/column loss
    matrix = matrix.reindex(index=sites, columns=weeks)

    return matrix


# -----------------------------
# Normalization
# -----------------------------
def normalize_per_week(
    matrix: pd.DataFrame,
    method: str = "minmax"
) -> pd.DataFrame:
    """
    Normalize values column-wise (per week).

    Methods:
    - minmax : scale to [0, 1]
    - zscore : standard score
    """
    if method == "minmax":
        return (matrix - matrix.min()) / (matrix.max() - matrix.min())

    if method == "zscore":
        return (matrix - matrix.mean()) / matrix.std()

    raise ValueError(f"Unknown normalization method '{method}'")


# -----------------------------
# Ranking
# -----------------------------
def rank_per_week(
    matrix: pd.DataFrame,
    ascending: bool = False
) -> pd.DataFrame:
    """
    Rank sites per week.

    ascending=False → best = rank 1
    """
    return matrix.rank(
        axis=0,
        method="min",
        ascending=ascending
    )


# -----------------------------
# Planning / prioritisation
# -----------------------------
def mean_per_site(
    df: pd.DataFrame,
    value_col: str,
    weeks: set[int] | None = None
) -> pd.Series:
    """
    Compute mean value per site across selected weeks.

    Intended for:
    - prioritising sites over a season
    - selecting top-N sites
    """
    data = df

    if weeks is not None:
        data = data[data["week_bin"].isin(weeks)]

    if value_col not in data.columns:
        raise ValueError(f"Column '{value_col}' not found")

    return (
        data
        .groupby("site_name")[value_col]
        .mean()
        .sort_values(ascending=False)
    )


# -----------------------------
# Suitability classification
# -----------------------------
def classify_suitability(value: float) -> dict | None:
    """
    Return suitability class config for a value.

    Returns None if unsuitable.
    """
    if value is None or value <= 0:
        return None

    for cls in SUITABILITY_CLASSES:
        if cls["min"] <= value < cls["max"]:
            return cls

    return None
