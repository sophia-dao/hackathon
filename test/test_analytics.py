import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import pytest

from app.analytics import get_drivers, get_summary


@pytest.fixture
def sample_df():
    return pd.DataFrame({
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


@pytest.fixture
def sample_forecast():
    return {
        "forecast_week": "2024-02-11",
        "predicted_gssi": 0.82,
        "predicted_alert": "high",
    }


def test_get_drivers_returns_ranked_driver_list(sample_df):
    drivers = get_drivers(sample_df)

    assert isinstance(drivers, list)
    assert len(drivers) > 0

    for d in drivers:
        assert "feature" in d
        assert "source" in d
        assert "correlation" in d
        assert "impact" in d

    corrs = [abs(d["correlation"]) for d in drivers]
    assert corrs == sorted(corrs, reverse=True)


def test_get_drivers_skips_missing_columns(sample_df):
    df = sample_df.drop(columns=["oil_price", "inventory_stress"])
    drivers = get_drivers(df)

    features = [d["feature"] for d in drivers]
    assert "oil_price" not in features
    assert "inventory_stress" not in features


def test_get_summary_with_mocked_ai(monkeypatch, sample_df, sample_forecast):
    mock_ai_output = {
        "inflation_risk_summary": "Inflation risk remains elevated due to ongoing supply pressure.",
        "main_drivers_explanation": "Freight costs and supplier delays are the dominant contributors.",
        "recommendation": "Monitor logistics-sensitive sectors closely.",
    }

    def mock_generate_ai_summary(df, forecast, current_gssi, trend, top_drivers):
        return mock_ai_output

    monkeypatch.setattr("app.analytics._generate_ai_summary", mock_generate_ai_summary)

    result = get_summary(sample_df, sample_forecast)

    assert "rule_based_summary" in result
    assert "ai_summary" in result
    assert "ai_explanation" in result
    assert "ai_recommendation" in result
    assert "top_drivers" in result
    assert "driver_source_groups" in result

    assert result["ai_summary"] == mock_ai_output["inflation_risk_summary"]
    assert result["ai_explanation"] == mock_ai_output["main_drivers_explanation"]
    assert result["ai_recommendation"] == mock_ai_output["recommendation"]


def test_get_summary_fallback_when_ai_fails(monkeypatch, sample_df, sample_forecast):
    def mock_generate_ai_summary(df, forecast, current_gssi, trend, top_drivers):
        raise RuntimeError("OpenAI failed")

    monkeypatch.setattr("app.analytics._generate_ai_summary", mock_generate_ai_summary)

    result = get_summary(sample_df, sample_forecast)

    assert isinstance(result["ai_summary"], str)
    assert isinstance(result["ai_explanation"], str)
    assert isinstance(result["ai_recommendation"], str)
    assert len(result["ai_summary"]) > 0


def test_get_summary_contains_expected_core_fields(monkeypatch, sample_df, sample_forecast):
    def mock_generate_ai_summary(df, forecast, current_gssi, trend, top_drivers):
        return {
            "inflation_risk_summary": "AI summary text",
            "main_drivers_explanation": "AI explanation text",
            "recommendation": "AI recommendation text",
        }

    monkeypatch.setattr("app.analytics._generate_ai_summary", mock_generate_ai_summary)

    result = get_summary(sample_df, sample_forecast)

    assert result["current_gssi"] == 0.7
    assert result["current_alert"] == "high"
    assert result["forecast_week"] == "2024-02-11"
    assert result["predicted_gssi"] == 0.82
    assert result["predicted_alert"] == "high"
    assert result["trend_past_4_weeks"] in {"rising", "falling", "stable"}
    assert result["active_feature_sources"] == ["fred", "inventory", "market"]
    assert result["future_feature_sources"] == ["news", "trends"]