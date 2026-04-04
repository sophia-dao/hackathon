import pandas as pd
import numpy as np


def compute_gssi(
    df: pd.DataFrame,
    date_col: str = "date",
    weights: dict | None = None
) -> pd.DataFrame:
    """
    Compute Global Supply Chain Stress Index (GSSI).

    Parameters:
        df: preprocessed dataframe (already scaled)
        weights: optional dictionary of feature weights
                 e.g. {"oil": 0.3, "freight": 0.4, ...}

    Returns:
        DataFrame with [date, gssi]
    """
    df = df.copy()

    feature_cols = [col for col in df.columns if col != date_col]

    if not feature_cols:
        raise ValueError("No features available to compute GSSI.")

    # Default: equal weights
    if weights is None:
        weights = {col: 1 / len(feature_cols) for col in feature_cols}

    # Ensure weights match features
    for col in feature_cols:
        if col not in weights:
            raise ValueError(f"Missing weight for feature: {col}")

    # Compute weighted sum
    gssi_values = np.zeros(len(df))

    for col in feature_cols:
        gssi_values += df[col] * weights[col]

    result = pd.DataFrame({
        date_col: df[date_col],
        "gssi": gssi_values
    })

    return result


def normalize_gssi(
    df: pd.DataFrame,
    gssi_col: str = "gssi"
) -> pd.DataFrame:
    """
    Normalize GSSI to 0–100 scale for interpretability.
    """
    df = df.copy()

    min_val = df[gssi_col].min()
    max_val = df[gssi_col].max()

    if max_val - min_val == 0:
        df[gssi_col] = 50  # fallback
    else:
        df[gssi_col] = 100 * (df[gssi_col] - min_val) / (max_val - min_val)

    return df


def build_gssi_pipeline(
    processed_df: pd.DataFrame,
    date_col: str = "date",
    weights: dict | None = None,
    normalize: bool = True
) -> pd.DataFrame:
    """
    Full pipeline:
    1. Compute GSSI
    2. Normalize (optional)
    """
    gssi_df = compute_gssi(processed_df, date_col=date_col, weights=weights)

    if normalize:
        gssi_df = normalize_gssi(gssi_df)

    return gssi_df