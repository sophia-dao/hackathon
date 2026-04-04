"""
forecasting.py — LSTM-based GSSI next-week forecaster.

Expects a pandas DataFrame with columns:
    week, freight_cost, supplier_delay, oil_price,
    market_volatility, inventory_stress, gssi, alert

Exposes:
    get_forecast(df) -> dict  (used by /gssi/forecast endpoint)
"""

import numpy as np
import pandas as pd
from datetime import timedelta

# Lazy-import TensorFlow so the module can be imported without GPU drivers.
_model = None  # cached model


LOOKBACK = 8  # weeks of history required

ALERT_THRESHOLDS = [
    (-np.inf, 25, "Low"),
    (25,      50, "Moderate"),
    (50,      75, "High"),
    (75,  np.inf, "Critical"),
]


def _gssi_to_alert(value: float) -> str:
    for lo, hi, label in ALERT_THRESHOLDS:
        if lo <= value < hi:
            return label
    return "Critical"


# ---------------------------------------------------------------------------
# Model building / loading
# ---------------------------------------------------------------------------

def _build_model(lookback: int = LOOKBACK) -> "tf.keras.Model":
    from tensorflow import keras

    model = keras.Sequential([
        keras.layers.Input(shape=(lookback, 1)),
        keras.layers.LSTM(64, return_sequences=False),
        keras.layers.Dense(32, activation="relu"),
        keras.layers.Dense(1),
    ], name="gssi_lstm")

    model.compile(optimizer="adam", loss="mse")
    return model


def _get_or_train_model(df: pd.DataFrame) -> "tf.keras.Model":
    """Return the cached model, or train a fresh one on df."""
    global _model
    if _model is not None:
        return _model

    gssi_values = df["gssi"].values.astype(np.float32)

    X, y = [], []
    for i in range(len(gssi_values) - LOOKBACK):
        X.append(gssi_values[i : i + LOOKBACK])
        y.append(gssi_values[i + LOOKBACK])

    if len(X) == 0:
        raise ValueError(
            f"Need at least {LOOKBACK + 1} rows of historical data to train; "
            f"got {len(gssi_values)}."
        )

    X = np.array(X)[..., np.newaxis]  # (samples, lookback, 1)
    y = np.array(y)

    model = _build_model(LOOKBACK)
    model.fit(X, y, epochs=50, batch_size=8, verbose=0)
    _model = model
    return model


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def forecast_next_week(df: pd.DataFrame) -> dict:
    """
    Given  DataFrame, predict next week's GSSI.

    Accepts either a 'week' or 'date' column as the time column.

    Returns:
        {
            "forecast_week": "YYYY-MM-DD",
            "predicted_gssi": float,
            "predicted_alert": str,
        }
    """
    # Normalise the date column name — preprocessing pipeline uses 'date'
    if "date" in df.columns and "week" not in df.columns:
        df = df.rename(columns={"date": "week"})

    df = df.sort_values("week").reset_index(drop=True)

    if len(df) < LOOKBACK + 1:
        raise ValueError(
            f"Need at least {LOOKBACK + 1} weeks of data; got {len(df)}."
        )

    model = _get_or_train_model(df)

    # Use the most recent LOOKBACK weeks as the input window.
    recent_gssi = df["gssi"].values[-LOOKBACK:].astype(np.float32)
    X_input = recent_gssi[np.newaxis, :, np.newaxis]  # (1, lookback, 1)

    predicted_gssi = float(model.predict(X_input, verbose=0)[0, 0])

    # Determine forecast week from last known week + 7 days.
    last_week = pd.to_datetime(df["week"].iloc[-1])
    forecast_week = (last_week + timedelta(weeks=1)).strftime("%Y-%m-%d")

    return {
        "forecast_week": forecast_week,
        "predicted_gssi": round(predicted_gssi, 4),
        "predicted_alert": _gssi_to_alert(predicted_gssi),
    }


# Alias kept for backward compatibility with existing tests
get_forecast = forecast_next_week


def reset_model() -> None:
    """Clear the cached model (useful between test runs or retraining)."""
    global _model
    _model = None
