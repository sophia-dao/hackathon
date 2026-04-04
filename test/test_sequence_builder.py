import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from app.sequence_builder import build_sequences

df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=6, freq="W"),
    "gssi": [10, 11, 12, 13, 14, 15],
    "oil": [70, 72, 71, 73, 74, 75],
    "freight": [100, 101, 102, 103, 104, 105]
})

X, y, feature_cols = build_sequences(
    df,
    target_col="gssi",
    lookback=3,
    drop_cols=["date"]
)

print(feature_cols)
print(X.shape)
print(y.shape)
print(X[0])
print(y[0])