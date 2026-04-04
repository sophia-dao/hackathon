import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.gssi import router


app = FastAPI()
app.include_router(router, prefix="/gssi")
client = TestClient(app)


def mock_prepare_pipeline():
    df = pd.DataFrame({
        "week": pd.to_datetime([
            "2024-01-07",
            "2024-01-14",
            "2024-01-21",
            "2024-01-28",
            "2024-02-04",
        ]),
        "gssi": [0.10, 0.20, 0.35, 0.50, 0.70],
        "alert": ["low", "low", "medium", "medium", "high"],
        "freight_cost": [1.0, 1.2, 1.5, 1.8, 2.0],
        "supplier_delay": [2.0, 2.2, 2.3, 2.7, 3.0],
        "oil_price": [70, 72, 74, 78, 81],
        "market_volatility": [15, 17, 19, 21, 24],
        "inventory_stress": [0.3, 0.4, 0.5, 0.7, 0.9],
    })

    forecast = {
        "forecast_week": "2024-02-11",
        "predicted_gssi": 0.82,
        "predicted_alert": "high",
    }

    return df, forecast


def mock_get_drivers(df):
    return [
        {
            "feature": "freight_cost",
            "correlation": 0.92,
            "impact": "positive",
            "source": "fred",
        },
        {
            "feature": "supplier_delay",
            "correlation": 0.88,
            "impact": "positive",
            "source": "fred",
        },
    ]


def mock_get_summary(df, forecast):
    return {
        "rule_based_summary": "Rule-based summary text",
        "ai_summary": "AI summary text",
        "ai_explanation": "AI explanation text",
        "ai_recommendation": "AI recommendation text",
    }


def test_health():
    response = client.get("/gssi/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_overview():
    response = client.get("/gssi/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["project"] == "Global Supply Chain Stress Index"
    assert data["model"] == "LSTM"


def test_current(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)

    response = client.get("/gssi/current")
    assert response.status_code == 200
    data = response.json()

    assert data["week"] == "2024-02-04"
    assert data["gssi"] == 0.7
    assert data["alert"] == "high"


def test_history(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)

    response = client.get("/gssi/history")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 5
    assert data[-1]["week"] == "2024-02-04"
    assert data[-1]["gssi"] == 0.7


def test_forecast(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)

    response = client.get("/gssi/forecast")
    assert response.status_code == 200
    data = response.json()

    assert data["week"] == "2024-02-11"
    assert data["predicted_gssi"] == 0.82
    assert data["alert"] == "high"


def test_drivers(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)
    monkeypatch.setattr("app.routes.gssi.get_drivers", mock_get_drivers)

    response = client.get("/gssi/drivers")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert data[0]["name"] == "freight_cost"
    assert data[0]["correlation"] == 0.92
    assert data[0]["impact"] == "positive"
    assert data[0]["source"] == "fred"


def test_summary(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)
    monkeypatch.setattr("app.routes.gssi.get_summary", mock_get_summary)

    response = client.get("/gssi/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["rule_based_summary"] == "Rule-based summary text"
    assert data["ai_summary"] == "AI summary text"
    assert data["ai_explanation"] == "AI explanation text"
    assert data["ai_recommendation"] == "AI recommendation text"


def test_components(monkeypatch):
    monkeypatch.setattr("app.routes.gssi.prepare_pipeline", mock_prepare_pipeline)

    response = client.get("/gssi/components")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 5
    assert data[-1]["week"] == "2024-02-04"
    assert data[-1]["oil"] == 81.0
    assert data[-1]["volatility"] == 24.0
    assert data[-1]["freight"] == 2.0
    assert data[-1]["supplier"] == 3.0
    assert data[-1]["inventory"] == 0.9