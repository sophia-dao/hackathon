import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.alerts import generate_alerts, get_alert_summary, get_latest_alert


def make_df(gssi_values, use_date_col=False):
    col = "date" if use_date_col else "week"
    weeks = pd.date_range("2024-01-07", periods=len(gssi_values), freq="W").strftime("%Y-%m-%d")
    return pd.DataFrame({col: weeks, "gssi": gssi_values})


FORECAST = {
    "forecast_week": "2024-06-02",
    "predicted_gssi": 1.2,
    "predicted_alert": "High",
}


# ---------------------------------------------------------------------------
# generate_alerts
# ---------------------------------------------------------------------------

def test_alert_column_added():
    df = make_df([0.0, 0.6, 1.6, -0.6])
    result = generate_alerts(df, FORECAST)
    assert "alert" in result.columns


def test_alert_values_are_correct():
    df = make_df([-1.0, 0.0, 0.6, 1.6])
    result = generate_alerts(df, FORECAST)
    alerts = result["alert"].tolist()
    assert alerts[0] == "Low"
    assert alerts[1] == "Moderate"
    assert alerts[2] == "High"
    assert alerts[3] == "Critical"


def test_forecast_row_appended():
    df = make_df([0.0, 0.5, 1.0])
    result = generate_alerts(df, FORECAST)
    assert len(result) == len(df) + 1
    last = result.iloc[-1]
    assert last["gssi"] == FORECAST["predicted_gssi"]
    assert last["alert"] == FORECAST["predicted_alert"]


def test_forecast_week_stored_in_last_row():
    df = make_df([0.0, 0.5])
    result = generate_alerts(df, FORECAST)
    assert result.iloc[-1]["week"] == FORECAST["forecast_week"]


def test_accepts_date_column():
    df = make_df([0.0, 0.5, 1.0], use_date_col=True)
    result = generate_alerts(df, FORECAST)
    assert "alert" in result.columns
    assert "date" in result.columns


def test_original_df_not_mutated():
    df = make_df([0.0, 0.5])
    generate_alerts(df, FORECAST)
    assert "alert" not in df.columns


# ---------------------------------------------------------------------------
# Alert threshold boundaries
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("gssi,expected", [
    (-1.0, "Low"),
    (-0.5, "Moderate"),   # boundary: -0.5 is Moderate
    (0.0,  "Moderate"),
    (0.5,  "High"),       # boundary: 0.5 is High
    (1.5,  "Critical"),   # boundary: 1.5 is Critical
    (2.0,  "Critical"),
])
def test_threshold_boundaries(gssi, expected):
    df = make_df([gssi])
    result = generate_alerts(df, FORECAST)
    assert result.iloc[0]["alert"] == expected


# ---------------------------------------------------------------------------
# get_alert_summary
# ---------------------------------------------------------------------------

def test_summary_returns_all_levels():
    df = make_df([-1.0, 0.0, 0.6, 1.6])
    result = generate_alerts(df, FORECAST)
    summary = get_alert_summary(result)
    assert set(summary.keys()) == {"Low", "Moderate", "High", "Critical"}


def test_summary_counts_are_correct():
    df = make_df([-1.0, -0.8, 0.0, 0.6, 1.6])
    result = generate_alerts(df, FORECAST)
    summary = get_alert_summary(result)
    assert summary["Low"] == 2
    assert summary["Moderate"] == 1


def test_summary_missing_levels_are_zero():
    df = make_df([0.0, 0.1])  # all Moderate
    result = generate_alerts(df, FORECAST)
    summary = get_alert_summary(result)
    assert summary["Low"] == 0
    assert summary["Critical"] == 0


# ---------------------------------------------------------------------------
# get_latest_alert
# ---------------------------------------------------------------------------

def test_latest_alert_from_most_recent_row():
    df = make_df([0.0, 0.3, 1.8])  # last is Critical
    assert get_latest_alert(df) == "Critical"


def test_latest_alert_unsorted_input():
    df = make_df([1.8, 0.3, 0.0])  # unsorted — last chronologically is 0.0 → Moderate
    assert get_latest_alert(df) == "Moderate"
