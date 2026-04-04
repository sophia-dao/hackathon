import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

LOOKBACK = 8


def _build_model(lookback: int) -> Sequential:
    model = Sequential([
        LSTM(64, input_shape=(lookback, 1), return_sequences=False),
        Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


def train_lstm_model(df: pd.DataFrame, lookback: int = LOOKBACK):
    """
    Train LSTM on the GSSI column of Sophia's DataFrame.

    Args:
        df: DataFrame with columns [week, gssi, ...]
        lookback: number of past weeks per sequence (default 8)

    Returns:
        (model, scaler) — trained Keras model and fitted MinMaxScaler
    """
    values = df["gssi"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(values)

    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i - lookback:i])
        y.append(scaled[i])

    X = np.array(X)  # (samples, lookback, 1)
    y = np.array(y)  # (samples,)

    model = _build_model(lookback)
    model.fit(X, y, epochs=50, batch_size=16, verbose=0)

    return model, scaler


def forecast_next_week(
    df: pd.DataFrame,
    model,
    scaler: MinMaxScaler,
    lookback: int = LOOKBACK,
) -> dict:
    """
    Predict next week's GSSI from the last `lookback` weeks.

    Args:
        df: DataFrame with columns [week, gssi, ...]; must have >= lookback rows
        model: trained Keras LSTM model
        scaler: fitted MinMaxScaler from train_lstm_model
        lookback: must match the value used during training

    Returns:
        {"forecast_week": "YYYY-MM-DD", "predicted_gssi": float, "predicted_alert": str}
    """
    values = df["gssi"].values.reshape(-1, 1)
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
