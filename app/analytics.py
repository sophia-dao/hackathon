import os
import json
import pandas as pd
from openai import OpenAI

FEATURE_COLUMNS = [
    "freight_cost",
    "supplier_delay",
    "oil_price",
    "market_volatility",
    "inventory_stress",
]

FEATURE_SOURCE_MAP = {
    "freight_cost": "fred",
    "supplier_delay": "fred",
    "oil_price": "fred",
    "market_volatility": "market",
    "inventory_stress": "inventory",
}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_drivers(df: pd.DataFrame) -> list[dict]:
    results = []

    for col in FEATURE_COLUMNS:
        if col not in df.columns:
            continue

        corr = df[col].corr(df["gssi"])
        if pd.isna(corr):
            continue

        corr = float(corr)
        results.append({
            "feature": col,
            "source": FEATURE_SOURCE_MAP.get(col, "unknown"),
            "correlation": round(corr, 4),
            "impact": "positive" if corr >= 0 else "negative",
        })

    results.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return results

def summarize_driver_sources(top_drivers: list[dict]) -> dict:
    """
    Aggregate top drivers by source group.
    """
    grouped = {}

    for driver in top_drivers:
        source = driver.get("source", "unknown")
        grouped[source] = grouped.get(source, 0) + 1

    return grouped

def get_summary(df: pd.DataFrame, forecast: dict) -> dict:
    current_gssi = round(float(df["gssi"].iloc[-1]), 4)
    trend = _trend_label(df.tail(4)["gssi"].values)
    top_drivers = get_drivers(df)

    rule_based_summary = _build_rule_based_summary(df, forecast, current_gssi, trend, top_drivers)

    ai_summary = None
    try:
        ai_summary = _generate_ai_summary(
            df=df,
            forecast=forecast,
            current_gssi=current_gssi,
            trend=trend,
            top_drivers=top_drivers,
        )
    except Exception:
        ai_summary = {
            "inflation_risk_summary": (
                f"Current supply chain stress is {df['alert'].iloc[-1]} and the short-term trend is {trend}, "
                f"suggesting continued inflation risk if disruptions persist."
            ),
            "main_drivers_explanation": (
                f"The strongest associated drivers are "
                f"{', '.join([d['feature'] for d in top_drivers[:3]]) or 'multiple factors'}, "
                f"which can raise input, transport, and inventory costs across the economy."
            ),
            "recommendation": (
                "Monitor cost-sensitive inputs closely and prepare contingency plans for continued supply pressure."
            ),
        }

    return {
        "current_gssi": current_gssi,
        "current_alert": df["alert"].iloc[-1],
        "trend_past_4_weeks": trend,
        "forecast_week": str(forecast["forecast_week"]),
        "predicted_gssi": float(forecast["predicted_gssi"]),
        "predicted_alert": forecast["predicted_alert"],

        "summary": rule_based_summary,            
        "rule_based_summary": rule_based_summary,
        "ai_summary": ai_summary,

        "top_drivers": top_drivers[:3],
        "driver_source_groups": summarize_driver_sources(top_drivers[:5]),

        "feature_sources_used": [
            "fred",
            "inventory",
            "market",
            "news",
            "trends",
        ],
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


def _build_rule_based_summary(
    df: pd.DataFrame,
    forecast: dict,
    current_gssi: float,
    trend: str,
    top_drivers: list[dict],
) -> str:
    """
    Deterministic fallback summary.
    """
    top_driver_names = [d["feature"] for d in top_drivers[:2]]
    driver_str = " and ".join(top_driver_names) if top_driver_names else "multiple factors"

    return (
        f"The Global Supply Chain Stress Index is currently {current_gssi:.2f} "
        f"({df['alert'].iloc[-1]} stress), with a {trend} trend over the past 4 weeks. "
        f"The primary drivers are {driver_str}. "
        f"The model forecasts a GSSI of {forecast['predicted_gssi']:.2f} "
        f"({forecast['predicted_alert']} stress) for the week of {forecast['forecast_week']}."
    )


def _generate_ai_summary(
    df: pd.DataFrame,
    forecast: dict,
    current_gssi: float,
    trend: str,
    top_drivers: list[dict],
) -> dict:
    """
    Generate structured AI summary using OpenAI.
    Returns:
        {
            "inflation_risk_summary": str,
            "main_drivers_explanation": str,
            "recommendation": str
        }
    """
    payload = {
        "current_gssi": current_gssi,
        "current_alert": df["alert"].iloc[-1],
        "trend_past_4_weeks": trend,
        "forecast_week": str(forecast["forecast_week"]),
        "predicted_gssi": float(forecast["predicted_gssi"]),
        "predicted_alert": forecast["predicted_alert"],
        "top_drivers": top_drivers[:3],
        "driver_source_groups": summarize_driver_sources(top_drivers[:5]),
    }

    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a macro-financial analyst. "
                    "The system integrates multiple signal groups: "
                    "macro indicators (FRED), inventory data, market signals, news signals, and search trends. "
                    "Use both the top drivers and the driver source groups to explain results. "
                    "Return valid JSON only with exactly these keys: "
                    "inflation_risk_summary, main_drivers_explanation, recommendation. "
                    "Keep responses concise, professional, and grounded in the provided data."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this Global Supply Chain Stress Index data:\n"
                    f"{json.dumps(payload, indent=2)}\n\n"
                    "Requirements:\n"
                    "- inflation_risk_summary: explain what this implies for inflation risk\n"
                    "- main_drivers_explanation: explain why the top drivers matter\n"
                    "- recommendation: give a short action-oriented note for decision-makers"
                ),
            },
        ],
    )

    text = response.output_text.strip()
    return json.loads(text)


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