"""
Integration test: verifies that forecast_next_week works with data produced
by the preprocessing and index_builder pipeline (no API calls needed).
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.preprocessing import preprocess_pipeline
from app.index_builder import build_gssi_pipeline
from app.forecasting import forecast_next_week, reset_model


@pytest.fixture(autouse=True)
def clear_model():
    reset_model()
    yield
    reset_model()


def make_raw_dfs(n_days=120):
    """Synthetic daily DataFrames that mimic the raw data pipeline sources."""
    dates = pd.date_range("2023-01-01", periods=n_days, freq="D")
    df1 = pd.DataFrame({"date": dates, "oil": np.linspace(70, 90, n_days)})
    df2 = pd.DataFrame({"date": dates, "freight": np.linspace(1000, 1400, n_days)})
    df3 = pd.DataFrame({"date": dates, "delivery_time": np.linspace(5, 8, n_days)})
    return [df1, df2, df3]


def test_pipeline_output_feeds_into_forecast():
    """Full pipeline: raw dfs → preprocess → build_gssi → forecast_next_week."""
    raw_dfs = make_raw_dfs()

    processed_df, _ = preprocess_pipeline(raw_dfs)
    gssi_df = build_gssi_pipeline(processed_df)

    # gssi_df has columns: date, gssi
    assert "date" in gssi_df.columns
    assert "gssi" in gssi_df.columns

    result = forecast_next_week(gssi_df)

    assert set(result.keys()) == {"forecast_week", "predicted_gssi", "predicted_alert"}
    assert result["predicted_alert"] in {"Low", "Moderate", "High", "Critical"}


def test_forecast_week_is_after_last_date_in_pipeline_output():
    raw_dfs = make_raw_dfs()
    processed_df, _ = preprocess_pipeline(raw_dfs)
    gssi_df = build_gssi_pipeline(processed_df)

    result = forecast_next_week(gssi_df)

    last_date = pd.to_datetime(gssi_df["date"].max())
    forecast_date = pd.to_datetime(result["forecast_week"])
    assert forecast_date > last_date


def test_raises_if_pipeline_output_too_short():
    """Only 5 weeks of data — should fail gracefully."""
    raw_dfs = make_raw_dfs(n_days=30)  # ~4 weeks after resampling
    processed_df, _ = preprocess_pipeline(raw_dfs)
    gssi_df = build_gssi_pipeline(processed_df)

    if len(gssi_df) < 9:
        with pytest.raises(ValueError, match="at least 9 weeks"):
            forecast_next_week(gssi_df)
    else:
        pytest.skip("synthetic data produced enough rows — adjust n_days")
