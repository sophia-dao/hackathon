from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "GSSI backend is running", "docs": "/docs"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.routes.gssi.get_drivers")
@patch("app.routes.gssi.get_summary")
@patch("app.routes.gssi.generate_alerts")
@patch("app.routes.gssi.forecast_next_week")
@patch("app.routes.gssi.build_sequences")
@patch("app.routes.gssi.build_gssi_pipeline")
@patch("app.routes.gssi.preprocess_pipeline")
@patch("app.routes.gssi.build_features")
def test_gssi_run(
    mock_build_features,
    mock_preprocess_pipeline,
    mock_build_gssi_pipeline,
    mock_build_sequences,
    mock_forecast_next_week,
    mock_generate_alerts,
    mock_get_summary,
    mock_get_drivers,
):
    features_df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=8, freq="W"),
        "oil_price": [70, 71, 69, 73, 75, 74, 76, 77],
        "freight_cost": [1.1, 1.2, 1.15, 1.3, 1.35, 1.33, 1.4, 1.45],
    })

    gssi_df = pd.DataFrame({
        "week": pd.date_range("2024-01-07", periods=8, freq="W"),
        "gssi": [-0.2, -0.1, 0.0, 0.1, 0.15, 0.2, 0.35, 0.5],
        "alert": ["low", "low", "low", "medium", "medium", "medium", "high", "high"],
        "freight_cost": [1.1, 1.2, 1.15, 1.3, 1.35, 1.33, 1.4, 1.45],
        "supplier_delay": [2, 2.1, 2.2, 2.4, 2.5, 2.7, 2.8, 3.0],
        "oil_price": [70, 71, 69, 73, 75, 74, 76, 77],
        "market_volatility": [0.10, 0.11, 0.09, 0.13, 0.14, 0.15, 0.18, 0.20],
        "inventory_stress": [0.3, 0.31, 0.32, 0.36, 0.37, 0.39, 0.42, 0.45],
    })

    mock_build_features.return_value = features_df
    mock_preprocess_pipeline.return_value = features_df.copy()
    mock_build_gssi_pipeline.return_value = gssi_df
    mock_build_sequences.return_value = (
        np.array([[[0.1], [0.2], [0.3], [0.4]]]),
        np.array([0.5]),
    )
    mock_forecast_next_week.return_value = {
        "forecast_week": "2024-03-10",
        "predicted_gssi": 0.62,
        "predicted_alert": "high",
    }
    mock_generate_alerts.return_value = gssi_df
    mock_get_summary.return_value = {
        "current_gssi": 0.5,
        "trend": "rising",
        "forecast_week": "2024-03-10",
        "predicted_gssi": 0.62,
        "predicted_alert": "high",
        "summary": "Stress is rising.",
    }
    mock_get_drivers.return_value = [
        {"feature": "freight_cost", "correlation": 0.81, "impact": "positive"},
        {"feature": "market_volatility", "correlation": 0.67, "impact": "positive"},
    ]

    response = client.get("/gssi/run")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "GSSI pipeline executed successfully"
    assert "latest_gssi" in data
    assert "forecast" in data
    assert "alerts" in data
    assert "drivers" in data
    assert "summary" in data
    assert data["forecast"]["predicted_gssi"] == 0.62


@patch("app.routes.gssi.get_summary")
@patch("app.routes.gssi.generate_alerts")
@patch("app.routes.gssi.forecast_next_week")
@patch("app.routes.gssi.build_sequences")
@patch("app.routes.gssi.build_gssi_pipeline")
@patch("app.routes.gssi.preprocess_pipeline")
@patch("app.routes.gssi.build_features")
def test_gssi_summary(
    mock_build_features,
    mock_preprocess_pipeline,
    mock_build_gssi_pipeline,
    mock_build_sequences,
    mock_forecast_next_week,
    mock_generate_alerts,
    mock_get_summary,
):
    df = pd.DataFrame({
        "week": pd.date_range("2024-01-07", periods=6, freq="W"),
        "gssi": [0.1, 0.2, 0.15, 0.3, 0.35, 0.4],
        "alert": ["low", "low", "low", "medium", "medium", "high"],
    })

    mock_build_features.return_value = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=6, freq="W")})
    mock_preprocess_pipeline.return_value = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=6, freq="W")})
    mock_build_gssi_pipeline.return_value = df
    mock_build_sequences.return_value = (np.array([[[0.1]]]), np.array([0.2]))
    mock_forecast_next_week.return_value = {
        "forecast_week": "2024-03-10",
        "predicted_gssi": 0.55,
        "predicted_alert": "high",
    }
    mock_generate_alerts.return_value = df
    mock_get_summary.return_value = {
        "current_gssi": 0.4,
        "trend": "rising",
        "forecast_week": "2024-03-10",
        "predicted_gssi": 0.55,
        "predicted_alert": "high",
        "summary": "Summary text",
    }

    response = client.get("/gssi/summary")
    assert response.status_code == 200
    assert response.json()["trend"] == "rising"


@patch("app.routes.gssi.get_drivers")
@patch("app.routes.gssi.generate_alerts")
@patch("app.routes.gssi.forecast_next_week")
@patch("app.routes.gssi.build_sequences")
@patch("app.routes.gssi.build_gssi_pipeline")
@patch("app.routes.gssi.preprocess_pipeline")
@patch("app.routes.gssi.build_features")
def test_gssi_drivers(
    mock_build_features,
    mock_preprocess_pipeline,
    mock_build_gssi_pipeline,
    mock_build_sequences,
    mock_forecast_next_week,
    mock_generate_alerts,
    mock_get_drivers,
):
    df = pd.DataFrame({
        "week": pd.date_range("2024-01-07", periods=6, freq="W"),
        "gssi": [0.1, 0.2, 0.15, 0.3, 0.35, 0.4],
        "alert": ["low", "low", "low", "medium", "medium", "high"],
    })

    mock_build_features.return_value = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=6, freq="W")})
    mock_preprocess_pipeline.return_value = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=6, freq="W")})
    mock_build_gssi_pipeline.return_value = df
    mock_build_sequences.return_value = (np.array([[[0.1]]]), np.array([0.2]))
    mock_forecast_next_week.return_value = {
        "forecast_week": "2024-03-10",
        "predicted_gssi": 0.55,
        "predicted_alert": "high",
    }
    mock_generate_alerts.return_value = df
    mock_get_drivers.return_value = [
        {"feature": "freight_cost", "correlation": 0.81, "impact": "positive"}
    ]

    response = client.get("/gssi/drivers")
    assert response.status_code == 200
    assert "drivers" in response.json()
    assert response.json()["drivers"][0]["feature"] == "freight_cost"