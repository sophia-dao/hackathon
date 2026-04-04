import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping

LOOKBACK = 8


def _build_model(lookback: int) -> Sequential:
    model = Sequential([
        Input(shape=(lookback, 1)),
        LSTM(64, return_sequences=False),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


def train_lstm_model(df: pd.DataFrame, lookback: int = LOOKBACK):
    """
    Train LSTM on the gssi column.

    Args:
        df: DataFrame with at least columns ['week', 'gssi']
        lookback: number of past weeks per training sequence

    Returns:
        (model, scaler)
    """
    if "gssi" not in df.columns:
        raise ValueError("DataFrame must contain a 'gssi' column.")

    if len(df) <= lookback:
        raise ValueError(
            f"DataFrame must contain more than {lookback} rows to create training sequences."
        )

    values = df["gssi"].astype(float).values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i - lookback:i])
        y.append(scaled[i])

    X = np.array(X)
    y = np.array(y)

    model = _build_model(lookback)

    early_stopping = EarlyStopping(
        monitor="loss",
        patience=5,
        restore_best_weights=True
    )

    model.fit(
        X,
        y,
        epochs=50,
        batch_size=16,
        verbose=0,
        callbacks=[early_stopping]
    )

    return model, scaler


def forecast_next_week(
    df: pd.DataFrame,
    model,
    scaler: MinMaxScaler,
    lookback: int = LOOKBACK,
) -> dict:
    """
    Forecast next week's GSSI from the last `lookback` weeks.
    """
    if "week" not in df.columns or "gssi" not in df.columns:
        raise ValueError("DataFrame must contain 'week' and 'gssi' columns.")

    if len(df) < lookback:
        raise ValueError(
            f"Need at least {lookback} rows to forecast the next week."
        )

    values = df["gssi"].astype(float).values.reshape(-1, 1)
    scaled = scaler.transform(values)

    sequence = scaled[-lookback:].reshape(1, lookback, 1)
    pred_scaled = model.predict(sequence, verbose=0)
    predicted_gssi = float(scaler.inverse_transform(pred_scaled)[0][0])

    last_week = pd.to_datetime(df["week"].iloc[-1])
    forecast_week = (last_week + timedelta(weeks=1)).strftime("%Y-%m-%d")

    return {
        "forecast_week": forecast_week,
        "predicted_gssi": round(predicted_gssi, 4),
        "predicted_alert": _alert_label(predicted_gssi),
    }


def _alert_label(gssi_value: float) -> str:
    if gssi_value < -0.5:
        return "Low"
    elif gssi_value < 0.5:
        return "Moderate"
    elif gssi_value < 1.5:
        return "High"
    else:
        return "Critical"