import pandas as pd

def rank_by_week(
    df: pd.DataFrame,
    value_col: str,
    rank_col: str,
    ascending: bool
) -> pd.DataFrame:
    """
    Dense rank sites per week for a given variable.
    """
    df = df.copy()

    df[rank_col] = (
        df.groupby("week_bin")[value_col]
          .rank(method="dense", ascending=ascending)
          .astype(int)
    )

    return df
