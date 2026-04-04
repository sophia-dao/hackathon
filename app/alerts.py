"""
alerts.py — Assigns alert levels to each row in the GSSI DataFrame
and flags whether the forecast crosses a threshold change.

Exposes:
    generate_alerts(df, forecast) -> pd.DataFrame
"""

import pandas as pd

# Thresholds match the normalized 0-100 GSSI scale
ALERT_THRESHOLDS = [
    (-float("inf"), 25,  "Low"),
    (25,            50,  "Moderate"),
    (50,            75,  "High"),
    (75,  float("inf"),  "Critical"),
]

ALERT_ORDER = {"Low": 0, "Moderate": 1, "High": 2, "Critical": 3}


def _gssi_to_alert(value: float) -> str:
    for lo, hi, label in ALERT_THRESHOLDS:
        if lo <= value < hi:
            return label
    return "Critical"


def generate_alerts(df: pd.DataFrame, forecast: dict) -> pd.DataFrame:
    """
    Adds an 'alert' column to df based on each row's gssi value,
    and appends a one-row forecast entry with its predicted alert.

    Parameters:
        df:       DataFrame with at least ['date' or 'week', 'gssi'] columns
        forecast: dict with keys 'forecast_week', 'predicted_gssi', 'predicted_alert'

    Returns:
        DataFrame with original rows + alert column + one forecast row appended.
    """
    df = df.copy()

    date_col = "week" if "week" in df.columns else "date"

    df["alert"] = df["gssi"].apply(_gssi_to_alert)

    # Append the forecast as a new row
    forecast_row = pd.DataFrame([{
        date_col: pd.to_datetime(forecast["forecast_week"]),
        "gssi": forecast["predicted_gssi"],
        "alert": forecast["predicted_alert"],
    }])

    result = pd.concat([df, forecast_row], ignore_index=True)
    return result


def get_alert_summary(df: pd.DataFrame) -> dict:
    """
    Returns counts of each alert level in the DataFrame.

    Example: {"Low": 3, "Moderate": 5, "High": 2, "Critical": 1}
    """
    if "alert" not in df.columns:
        df = df.copy()
        df["alert"] = df["gssi"].apply(_gssi_to_alert)

    counts = df["alert"].value_counts().to_dict()
    return {level: counts.get(level, 0) for level in ALERT_ORDER}


def get_latest_alert(df: pd.DataFrame) -> str:
    """Returns the alert level for the most recent row."""
    date_col = "week" if "week" in df.columns else "date"
    df = df.sort_values(date_col)
    latest_gssi = df["gssi"].iloc[-1]
    return _gssi_to_alert(latest_gssi)
