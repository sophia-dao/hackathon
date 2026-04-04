import pandas as pd

FEATURE_COLUMNS = [
    "freight_cost",
    "supplier_delay",
    "oil_price",
    "market_volatility",
    "inventory_stress",
]


def build_gssi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Global Supply Chain Stress Index (GSSI) from standardized features.
    Returns the original feature table plus a computed gssi column.
    """
    df = df.copy()

    features = [col for col in FEATURE_COLUMNS if col in df.columns]
    if not features:
        raise ValueError("No valid feature columns found for GSSI computation.")

    df_norm = df[features].copy()
    df_norm = (df_norm - df_norm.mean()) / df_norm.std(ddof=0)

    df["gssi"] = df_norm.mean(axis=1)

    return df