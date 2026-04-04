import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.forecasting import get_forecast, reset_model


def make_df(n=20, gssi_values=None):
    weeks = pd.date_range("2024-01-07", periods=n, freq="W").strftime("%Y-%m-%d")
    gssi = gssi_values if gssi_values is not None else np.linspace(0.0, 1.0, n)
    return pd.DataFrame({
        "week": weeks,
        "freight_cost": np.random.rand(n),
        "supplier_delay": np.random.rand(n),
        "oil_price": np.random.rand(n),
        "market_volatility": np.random.rand(n),
        "inventory_stress": np.random.rand(n),
        "gssi": gssi,
        "alert": ["Moderate"] * n,
    })


# Reset cached model before each test so they stay independent.
@pytest.fixture(autouse=True)
def clear_model():
    reset_model()
    yield
    reset_model()


def test_returns_expected_keys():
    result = get_forecast(make_df(20))
    assert set(result.keys()) == {"forecast_week", "predicted_gssi", "predicted_alert"}


def test_forecast_week_is_one_week_after_last_row():
    df = make_df(20)
    result = get_forecast(df)
    last_week = pd.to_datetime(df["week"].iloc[-1])
    expected = (last_week + pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
    assert result["forecast_week"] == expected


def test_predicted_gssi_is_float():
    result = get_forecast(make_df(20))
    assert isinstance(result["predicted_gssi"], float)


def test_predicted_alert_valid_label():
    result = get_forecast(make_df(20))
    assert result["predicted_alert"] in {"Low", "Moderate", "High", "Critical"}


def test_alert_thresholds():
    from app.forecasting import _gssi_to_alert
    assert _gssi_to_alert(-1.0) == "Low"
    assert _gssi_to_alert(-0.5) == "Moderate"
    assert _gssi_to_alert(0.0) == "Moderate"
    assert _gssi_to_alert(0.5) == "High"
    assert _gssi_to_alert(1.5) == "Critical"
    assert _gssi_to_alert(2.0) == "Critical"


def test_raises_with_too_few_rows():
    df = make_df(8)  # need >= 9
    with pytest.raises(ValueError, match="at least 9 weeks"):
        get_forecast(df)


def test_exactly_minimum_rows_works():
    # 9 rows is the minimum that should succeed (8 for window + 1 for target)
    result = get_forecast(make_df(9))
    assert "predicted_gssi" in result


def test_unsorted_input_still_works():
    df = make_df(20)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    result = get_forecast(df_shuffled)
    # forecast_week should still be relative to the chronologically last week
    expected_last = pd.to_datetime(df["week"].iloc[-1])
    expected_fw = (expected_last + pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
    assert result["forecast_week"] == expected_fw
