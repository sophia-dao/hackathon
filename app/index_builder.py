import pandas as pd
import numpy as np

# Signed weights: positive = raises stress when feature goes up
#                 negative = lowers stress when feature goes up
SIGNED_WEIGHTS = {
    # Stress indicators — rising = more supply chain pressure
    "oil":                    +0.12,
    "freight":                +0.12,
    "transport_ppi":          +0.10,
    "dow_vol":                +0.08,
    "sp500_vol":              +0.08,
    "nasdaq_vol":             +0.08,
    "news_count":             +0.05,
    "trend_supply_chain":     +0.03,
    "trend_shipping_delays":  +0.03,

    # Health indicators — rising = economy healthy = less stress
    "consumer_confidence":    -0.10,
    "sp500_close":            -0.06,
    "dow_close":              -0.06,
    "nasdaq_close":           -0.06,
    "sp500_return":           -0.03,
    "dow_return":             -0.03,
    "nasdaq_return":          -0.03,
}


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

    # Default: use signed weights; unknown features get a small positive weight
    if weights is None:
        unknown = [c for c in feature_cols if c not in SIGNED_WEIGHTS]
        fallback = 0.02 / max(len(unknown), 1)
        weights = {
            col: SIGNED_WEIGHTS.get(col, fallback)
            for col in feature_cols
        }

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