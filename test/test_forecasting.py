import pandas as pd
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.forecasting import train_lstm_model, forecast_next_week, LOOKBACK


@pytest.fixture
def sample_gssi_df():
    """
    Small weekly dataset with enough rows for LSTM sequence creation.
    """
    weeks = pd.date_range(start="2024-01-07", periods=20, freq="W")
    gssi_values = [
        -0.8, -0.6, -0.4, -0.2,
         0.0,  0.1,  0.3,  0.5,
         0.7,  0.8,  1.0,  1.2,
         1.1,  0.9,  0.6,  0.4,
         0.2,  0.0, -0.1, -0.2
    ]

    return pd.DataFrame({
        "week": weeks,
        "gssi": gssi_values
    })


def test_train_lstm_model_returns_model_and_scaler(sample_gssi_df):
    model, scaler = train_lstm_model(sample_gssi_df)

    assert model is not None
    assert scaler is not None


def test_forecast_next_week_returns_expected_structure(sample_gssi_df):
    model, scaler = train_lstm_model(sample_gssi_df)
    result = forecast_next_week(sample_gssi_df, model, scaler)

    assert isinstance(result, dict)
    assert "forecast_week" in result
    assert "predicted_gssi" in result
    assert "predicted_alert" in result


def test_forecast_week_is_one_week_after_last_date(sample_gssi_df):
    model, scaler = train_lstm_model(sample_gssi_df)
    result = forecast_next_week(sample_gssi_df, model, scaler)

    expected_week = (
        pd.to_datetime(sample_gssi_df["week"].iloc[-1]) + pd.Timedelta(weeks=1)
    ).strftime("%Y-%m-%d")

    assert result["forecast_week"] == expected_week


def test_predicted_gssi_is_float(sample_gssi_df):
    model, scaler = train_lstm_model(sample_gssi_df)
    result = forecast_next_week(sample_gssi_df, model, scaler)

    assert isinstance(result["predicted_gssi"], float)


def test_predicted_alert_is_valid_label(sample_gssi_df):
    model, scaler = train_lstm_model(sample_gssi_df)
    result = forecast_next_week(sample_gssi_df, model, scaler)

    assert result["predicted_alert"] in {"Low", "Moderate", "High", "Critical"}


def test_forecast_next_week_raises_with_too_few_rows():
    short_df = pd.DataFrame({
        "week": pd.date_range(start="2024-01-07", periods=LOOKBACK - 1, freq="W"),
        "gssi": [0.1] * (LOOKBACK - 1)
    })

    with pytest.raises(Exception):
        model, scaler = train_lstm_model(short_df)
        forecast_next_week(short_df, model, scaler)