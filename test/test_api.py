import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
import pandas as pd
import pytest

from app.main import app
from app.routes import gssi as gssi_routes

client = TestClient(app)


@pytest.fixture
def sample_gssi_df():
    return pd.DataFrame({
        "week": pd.to_datetime([
            "2024-01-07",
            "2024-01-14",
            "2024-01-21",
            "2024-01-28",
            "2024-02-04",
        ]),
        "gssi": [0.1, 0.2, 0.15, 0.3, 0.25],
        "alert": ["Low", "Low", "Medium", "High", "Medium"],
    })


@pytest.fixture
def sample_forecast():
    return {"next_week_gssi": 0.35, "trend": "increasing"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"] == "GSSI backend is running"
    assert "docs" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_pipeline_success(monkeypatch, sample_gssi_df, sample_forecast):
    def mock_get_gssi_data():
        return sample_gssi_df.copy()

    def mock_get_forecast(gssi_df):
        return sample_forecast

    def mock_apply_alerts_if_needed(gssi_df, forecast):
        return gssi_df.copy()

    monkeypatch.setattr(gssi_routes, "get_gssi_data", mock_get_gssi_data)
    monkeypatch.setattr(gssi_routes, "get_forecast", mock_get_forecast)
    monkeypatch.setattr(gssi_routes, "apply_alerts_if_needed", mock_apply_alerts_if_needed)

    response = client.get("/gssi/run")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "GSSI pipeline executed successfully"
    assert "latest_gssi" in data
    assert len(data["latest_gssi"]) > 0


def test_forecast_endpoint_uses_cache(sample_gssi_df, sample_forecast):
    gssi_routes.pipeline_cache["gssi_df"] = sample_gssi_df.copy()
    gssi_routes.pipeline_cache["forecast"] = sample_forecast
    gssi_routes.pipeline_cache["last_updated"] = "2026-04-04T12:00:00"

    response = client.get("/gssi/forecast")
    assert response.status_code == 200

    data = response.json()
    assert "forecast" in data
    assert data["forecast"] == sample_forecast


def test_summary_endpoint_uses_cache(monkeypatch, sample_gssi_df, sample_forecast):
    gssi_routes.pipeline_cache["gssi_df"] = sample_gssi_df.copy()
    gssi_routes.pipeline_cache["forecast"] = sample_forecast
    gssi_routes.pipeline_cache["last_updated"] = "2026-04-04T12:00:00"

    def mock_get_summary(gssi_df, forecast):
        return "GSSI is stable with moderate upward pressure."

    monkeypatch.setattr(gssi_routes, "get_summary", mock_get_summary)

    response = client.get("/gssi/summary")
    assert response.status_code == 200

    data = response.json()
    assert "summary" in data
    assert data["summary"] == "GSSI is stable with moderate upward pressure."


def test_drivers_endpoint_uses_cache(monkeypatch, sample_gssi_df):
    gssi_routes.pipeline_cache["gssi_df"] = sample_gssi_df.copy()
    gssi_routes.pipeline_cache["forecast"] = {"next_week_gssi": 0.35}
    gssi_routes.pipeline_cache["last_updated"] = "2026-04-04T12:00:00"

    def mock_get_drivers(gssi_df):
        return ["oil", "freight", "inventory_stress_total"]

    monkeypatch.setattr(gssi_routes, "get_drivers", mock_get_drivers)

    response = client.get("/gssi/drivers")
    assert response.status_code == 200

    data = response.json()
    assert "drivers" in data
    assert "oil" in data["drivers"]


def test_alerts_endpoint_uses_cache(sample_gssi_df):
    gssi_routes.pipeline_cache["gssi_df"] = sample_gssi_df.copy()
    gssi_routes.pipeline_cache["forecast"] = {"next_week_gssi": 0.35}
    gssi_routes.pipeline_cache["last_updated"] = "2026-04-04T12:00:00"

    response = client.get("/gssi/alerts")
    assert response.status_code == 200

    data = response.json()
    assert "alerts" in data
    assert len(data["alerts"]) > 0
    assert "alert" in data["alerts"][0]


def test_cached_endpoints_fail_if_run_not_called():
    gssi_routes.pipeline_cache["gssi_df"] = None
    gssi_routes.pipeline_cache["forecast"] = None
    gssi_routes.pipeline_cache["last_updated"] = None

    endpoints = [
        "/gssi/forecast",
        "/gssi/summary",
        "/gssi/drivers",
        "/gssi/alerts",
    ]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 400
        assert "Call /run first" in response.json()["detail"]