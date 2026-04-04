import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.analytics import get_drivers, get_summary


def test_get_drivers():
    df = pd.DataFrame({
        "gssi": [1, 2, 3, 4, 5],
        "freight_cost": [2, 4, 6, 8, 10],
        "supplier_delay": [5, 4, 3, 2, 1],
        "oil_price": [1, 2, 2, 3, 3],
        "market_volatility": [1, 1, 2, 2, 3],
        "inventory_stress": [5, 5, 6, 6, 7],
    })

    drivers = get_drivers(df)
    assert isinstance(drivers, list)
    assert len(drivers) > 0
    assert "feature" in drivers[0]
    assert "correlation" in drivers[0]
    assert "impact" in drivers[0]


def test_get_summary():
    df = pd.DataFrame({
        "week": pd.date_range("2024-01-07", periods=5, freq="W"),
        "gssi": [0.1, 0.2, 0.3, 0.4, 0.5],
        "alert": ["low", "low", "medium", "medium", "high"],
        "freight_cost": [1, 2, 3, 4, 5],
        "supplier_delay": [2, 3, 4, 5, 6],
        "oil_price": [10, 11, 12, 13, 14],
        "market_volatility": [0.1, 0.2, 0.3, 0.4, 0.5],
        "inventory_stress": [5, 5.2, 5.4, 5.6, 5.8],
    })

    forecast = {
        "forecast_week": "2024-02-11",
        "predicted_gssi": 0.6,
        "predicted_alert": "high",
    }

    summary = get_summary(df, forecast)

    assert summary["current_gssi"] == 0.5
    assert summary["forecast_week"] == "2024-02-11"
    assert summary["predicted_alert"] == "high"
    assert "summary" in summary