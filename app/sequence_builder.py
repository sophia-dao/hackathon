import numpy as np
import pandas as pd


def build_sequences(
    df: pd.DataFrame,
    target_col: str = "gssi",
    lookback: int = 8,
    drop_cols: list[str] | None = None,
    include_target_in_features: bool = True
):
    if df.empty:
        raise ValueError("Input dataframe is empty.")

    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataframe.")

    if lookback <= 0:
        raise ValueError("lookback must be greater than 0.")

    drop_cols = drop_cols or []

    feature_cols = [col for col in df.columns if col not in drop_cols]

    if not include_target_in_features and target_col in feature_cols:
        feature_cols.remove(target_col)

    X = []
    y = []

    for i in range(len(df) - lookback):
        x_seq = df.iloc[i:i + lookback][feature_cols].values
        y_target = df.iloc[i + lookback][target_col]

        X.append(x_seq)
        y.append(y_target)

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    return X, y, feature_cols