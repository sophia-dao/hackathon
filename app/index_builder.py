# app/index_builder.py

import pandas as pd


def build_gssi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Global Supply Chain Stress Index (GSSI)
    """

    df = df.copy()

    # Select features
    features = [
        "oil",
        "freight",
        "delivery_time",
        "sp500_vol",
        "dow_vol",
        "nasdaq_vol",
        "news_count",
    ]

    # Keep only existing columns
    features = [f for f in features if f in df.columns]

    # Normalize (z-score)
    df_norm = df[features].copy()

    df_norm = (df_norm - df_norm.mean()) / df_norm.std()

    # Combine into index (equal weights)
    df["gssi"] = df_norm.mean(axis=1)

    return df[["date", "gssi"]]