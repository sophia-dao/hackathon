import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def standardize_date_column(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """
    Ensure the date column exists and is converted to datetime.
    """
    df = df.copy()

    if date_col not in df.columns:
        raise ValueError(f"Expected '{date_col}' column in dataframe.")

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col])
    df = df.sort_values(date_col)

    return df


def resample_to_weekly(
    df: pd.DataFrame,
    date_col: str = "date",
    method: str = "mean"
) -> pd.DataFrame:
    """
    Resample a dataframe to weekly frequency.

    Parameters:
        method:
            - 'mean' for averaging within each week
            - 'last' for taking the last available value of the week
            - 'sum' for weekly totals
    """
    df = standardize_date_column(df, date_col)
    df = df.set_index(date_col)

    if method == "mean":
        weekly_df = df.resample("W").mean(numeric_only=True)
    elif method == "last":
        weekly_df = df.resample("W").last()
    elif method == "sum":
        weekly_df = df.resample("W").sum(numeric_only=True)
    else:
        raise ValueError("method must be one of: 'mean', 'last', 'sum'")

    weekly_df = weekly_df.reset_index()
    return weekly_df


def merge_dataframes_on_date(dataframes: list[pd.DataFrame], date_col: str = "date") -> pd.DataFrame:
    """
    Merge multiple weekly dataframes on the date column using outer join.
    This keeps all weeks and lets us fill missing values later.
    """
    if not dataframes:
        raise ValueError("No dataframes provided for merging.")

    merged_df = standardize_date_column(dataframes[0], date_col)

    for df in dataframes[1:]:
        df = standardize_date_column(df, date_col)
        merged_df = pd.merge(merged_df, df, on=date_col, how="outer")

    merged_df = merged_df.sort_values(date_col).reset_index(drop=True)
    return merged_df


def handle_missing_values(
    df: pd.DataFrame,
    date_col: str = "date",
    fill_method: str = "ffill_bfill"
) -> pd.DataFrame:
    """
    Fill missing values after merging all sources.

    Options:
        - 'ffill': forward fill only
        - 'bfill': backward fill only
        - 'ffill_bfill': forward fill then backward fill
        - 'interpolate': time-based interpolation + fallback fill
        - 'drop': drop rows with missing values
    """
    df = df.copy()
    df = standardize_date_column(df, date_col)

    if fill_method == "ffill":
        df = df.ffill()
    elif fill_method == "bfill":
        df = df.bfill()
    elif fill_method == "ffill_bfill":
        df = df.ffill().bfill()
    elif fill_method == "interpolate":
        df = df.set_index(date_col)
        df = df.interpolate(method="time").ffill().bfill().reset_index()
    elif fill_method == "drop":
        df = df.dropna()
    else:
        raise ValueError("Invalid fill_method.")

    return df


def remove_outliers_zscore(
    df: pd.DataFrame,
    threshold: float = 3.0,
    date_col: str = "date"
) -> pd.DataFrame:
    """
    Clip extreme outliers using z-score threshold.
    Instead of dropping rows, this caps values at threshold boundaries.
    """
    df = df.copy()

    numeric_cols = [col for col in df.columns if col != date_col and pd.api.types.is_numeric_dtype(df[col])]

    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()

        if std == 0 or pd.isna(std):
            continue

        lower = mean - threshold * std
        upper = mean + threshold * std
        df[col] = df[col].clip(lower=lower, upper=upper)

    return df


def scale_features(
    df: pd.DataFrame,
    date_col: str = "date"
) -> tuple[pd.DataFrame, StandardScaler]:
    """
    Standardize numeric features so they are centered around 0
    with unit variance. This is important before index construction
    and especially before LSTM training.
    """
    df = df.copy()

    numeric_cols = [col for col in df.columns if col != date_col and pd.api.types.is_numeric_dtype(df[col])]
    scaler = StandardScaler()

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    return df, scaler


def preprocess_pipeline(
    raw_dataframes: list[pd.DataFrame],
    date_col: str = "date",
    weekly_method: str = "mean",
    fill_method: str = "ffill_bfill",
    apply_outlier_clipping: bool = True,
) -> tuple[pd.DataFrame, StandardScaler]:
    """
    Full preprocessing pipeline:
    1. Standardize dates
    2. Resample each source to weekly
    3. Merge all sources
    4. Handle missing values
    5. Clip outliers
    6. Scale numeric features
    """
    weekly_dfs = [
        resample_to_weekly(df, date_col=date_col, method=weekly_method)
        for df in raw_dataframes
    ]

    merged_df = merge_dataframes_on_date(weekly_dfs, date_col=date_col)
    clean_df = handle_missing_values(merged_df, date_col=date_col, fill_method=fill_method)

    if apply_outlier_clipping:
        clean_df = remove_outliers_zscore(clean_df, date_col=date_col)

    scaled_df, scaler = scale_features(clean_df, date_col=date_col)

    return scaled_df, scaler