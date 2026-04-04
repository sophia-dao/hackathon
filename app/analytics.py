import pandas as pd

FEATURE_COLUMNS = [
    "freight_cost",
    "supplier_delay",
    "oil_price",
    "market_volatility",
    "inventory_stress",
]

DISPLAY_NAMES = {
    "freight_cost": "Freight Cost",
    "supplier_delay": "Supplier Delay",
    "oil_price": "Oil Price",
    "market_volatility": "Market Volatility",
    "inventory_stress": "Inventory Stress",
}


def get_drivers(df: pd.DataFrame) -> list[dict]:
    """
    Return ranked driver correlations with GSSI.
    """
    results = []

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            continue

        corr = df[col].corr(df["gssi"])
        if pd.isna(corr):
            corr = 0.0

        results.append({
            "name": DISPLAY_NAMES.get(col, col),
            "feature": col,
            "contribution": round(float(abs(corr)), 4),
            "direction": "positive" if float(corr) >= 0 else "negative",
        })

    results.sort(key=lambda x: x["contribution"], reverse=True)
    return results


def get_summary(df: pd.DataFrame, forecast: dict) -> dict:
    current_gssi = round(float(df["gssi"].iloc[-1]), 4)
    current_alert = df["alert"].iloc[-1]
    trend = _trend_label(df.tail(4)["gssi"].values)

    top_drivers = get_drivers(df)
    top_driver_names = [d["name"] for d in top_drivers[:2]]
    driver_str = " and ".join(top_driver_names) if top_driver_names else "multiple factors"

    summary = (
        f"Current GSSI is {current_gssi:.2f} ({current_alert} stress) with a {trend} trend "
        f"over the last 4 weeks. The strongest drivers are {driver_str}. "
        f"Next week is forecast at {forecast['predicted_gssi']:.2f} "
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


def _trend_label(recent_gssi_values) -> str:
    if len(recent_gssi_values) < 2:
        return "stable"

    delta = float(recent_gssi_values[-1]) - float(recent_gssi_values[0])

    if delta > 0.2:
        return "rising"
    elif delta < -0.2:
        return "falling"
    return "stable"