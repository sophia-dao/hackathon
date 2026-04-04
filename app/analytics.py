"""
analytics.py — Driver analysis and macro summary for the GSSI.

Exposes:
    get_drivers(df)          -> list of dicts
    get_summary(df, forecast) -> dict
"""

import pandas as pd


def get_drivers(df: pd.DataFrame) -> list:
    """
    Returns the top contributing indicators ranked by absolute correlation
    with the gssi column.

    Each entry:
        {"feature": str, "correlation": float, "impact": str}
    where impact is "positive" or "negative".
    """
    exclude = {"gssi", "date", "week", "alert"}
    available = [
        c for c in df.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(df[c])
    ]

    results = []
    for col in available:
        corr = df[col].corr(df["gssi"])
        if pd.isna(corr):
            continue
        results.append({
            "feature": col,
            "correlation": round(corr, 4),
            "impact": "positive" if corr >= 0 else "negative",
        })

    results.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return results


def get_summary(df: pd.DataFrame, forecast: dict) -> dict:
    """
    Returns a macro-financial summary of the current GSSI state and forecast.

    Returns:
        {
            "current_gssi": float,
            "current_alert": str,
            "forecast_week": str,
            "predicted_gssi": float,
            "predicted_alert": str,
            "trend": str,          # "improving", "stable", or "worsening"
            "summary": str,        # human-readable one-liner
        }
    """
    date_col = "week" if "week" in df.columns else "date"
    df = df.sort_values(date_col).reset_index(drop=True)

    current_gssi = round(float(df["gssi"].iloc[-1]), 4)
    current_alert = df["alert"].iloc[-1] if "alert" in df.columns else _gssi_to_alert(current_gssi)

    predicted_gssi = forecast["predicted_gssi"]
    delta = predicted_gssi - current_gssi

    if delta > 0.1:
        trend = "worsening"
    elif delta < -0.1:
        trend = "improving"
    else:
        trend = "stable"

    summary_text = (
        f"GSSI is currently {current_gssi:.2f} ({current_alert}). "
        f"Next week is forecast at {predicted_gssi:.2f} ({forecast['predicted_alert']}), "
        f"indicating a {trend} supply chain outlook."
    )

    return {
        "current_gssi": current_gssi,
        "current_alert": current_alert,
        "forecast_week": forecast["forecast_week"],
        "predicted_gssi": predicted_gssi,
        "predicted_alert": forecast["predicted_alert"],
        "trend": trend,
        "summary": summary_text,
    }


def _gssi_to_alert(value: float) -> str:
    if value < 25:
        return "Low"
    elif value < 50:
        return "Moderate"
    elif value < 75:
        return "High"
    return "Critical"
