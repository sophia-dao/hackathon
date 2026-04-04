import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.index_builder import build_gssi_pipeline


def test_gssi_pipeline():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5, freq="W"),
        "oil": [0.1, 0.2, 0.3, 0.4, 0.5],
        "freight": [0.5, 0.4, 0.3, 0.2, 0.1],
    })

    gssi_df = build_gssi_pipeline(df)

    assert "gssi" in gssi_df.columns
    assert len(gssi_df) == 5
    assert gssi_df["gssi"].between(0, 100).all()