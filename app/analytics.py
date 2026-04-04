import pandas as pd

FEATURE_COLUMNS = [
    "freight_cost",
    "supplier_delay",
    "oil_price",
    "market_volatility",
    "inventory_stress",
]


def get_drivers(df: pd.DataFrame) -> list[dict]:
    """
    Rank supply chain features by their correlation with GSSI.
    Used by the /gssi/drivers endpoint.

    Args:
        df: DataFrame with columns [gssi, freight_cost, supplier_delay,
            oil_price, market_volatility, inventory_stress]

    Returns:
        List of {"feature": str, "correlation": float, "impact": str},
        sorted by absolute correlation descending.
    """
    results = []
    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            continue
        corr = float(df[col].corr(df["gssi"]))
        results.append({
            "feature": col,
            "correlation": round(corr, 4),
            "impact": "positive" if corr >= 0 else "negative",
        })

    results.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return results


def get_summary(df: pd.DataFrame, forecast: dict) -> dict:
    """
    Generate a macro-financial summary of current GSSI trend and forecast.
    Used by the /gssi/summary endpoint.

    Args:
        df: DataFrame with columns [week, gssi, alert]
        forecast: output of forecast_next_week()
            {"forecast_week", "predicted_gssi", "predicted_alert"}

    Returns:
        {"current_gssi", "trend", "forecast_week", "predicted_gssi",
         "predicted_alert", "summary"}
    """
    current_gssi = round(float(df["gssi"].iloc[-1]), 4)
    trend = _trend_label(df.tail(4)["gssi"].values)
    top_drivers = get_drivers(df)

    top_driver_names = [d["feature"] for d in top_drivers[:2]]
    driver_str = " and ".join(top_driver_names) if top_driver_names else "multiple factors"

    summary = (
        f"The Global Supply Chain Stress Index is currently {current_gssi:.2f} "
        f"({df['alert'].iloc[-1]} stress), with a {trend} trend over the past 4 weeks. "
        f"The primary drivers are {driver_str}. "
        f"The model forecasts a GSSI of {forecast['predicted_gssi']:.2f} "
        f"({forecast['predicted_alert']} stress) for the week of {forecast['forecast_week']}."
    )

    return {
        "current_gssi": current_gssi,
        "trend": trend,
        "forecast_week": forecast["forecast_week"],
        "predicted_gssi": forecast["predicted_gssi"],
        "predicted_alert": forecast["predicted_alert"],
        "summary": summary,
    }


def summarize_trends(df: pd.DataFrame) -> dict:
    """
    Lightweight trend summary over the full DataFrame.
    Kept for backward compatibility with any existing callers.
    """
    return {
        "latest_gssi": round(float(df["gssi"].iloc[-1]), 4),
        "trend": _trend_label(df.tail(4)["gssi"].values),
        "weeks_covered": len(df),
    }


def _trend_label(recent_gssi_values) -> str:
    if len(recent_gssi_values) < 2:
        return "stable"
    delta = float(recent_gssi_values[-1]) - float(recent_gssi_values[0])
    if delta > 0.2:
        return "rising"
    elif delta < -0.2:
        return "falling"
    else:
        return "stable"
