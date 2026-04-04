import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.preprocessing import preprocess_pipeline

df1 = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=14, freq="D"),
    "oil": range(70, 84)
})

df2 = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=14, freq="D"),
    "freight": range(1000, 1014)
})

processed_df, scaler = preprocess_pipeline([df1, df2])

print(processed_df)
print(processed_df.isnull().sum())