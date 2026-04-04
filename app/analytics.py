"""
analytics.py — Driver analysis and macro summary for the GSSI.

Exposes:
    get_drivers(df)                    -> list of dicts
    get_summary(df, forecast)          -> dict
    ai_summarize(summary, drivers)     -> str
"""

import os

import pandas as pd
from openai import OpenAI


def get_drivers(df: pd.DataFrame, raw_df: pd.DataFrame = None) -> list:
    """
    Returns the top contributing indicators ranked by absolute correlation
    with the gssi column.

    Each entry:
        {"feature": str, "correlation": float, "impact": str, "latest_value": float|None}
    where impact is "positive" or "negative".

    raw_df: optional unscaled dataframe used to show real-world values in the tooltip.
            If omitted, latest_value falls back to whatever is in df (scaled).
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

        # Prefer raw (unscaled) values for the tooltip
        value_series = raw_df[col] if (raw_df is not None and col in raw_df.columns) else df[col]
        cleaned = value_series.dropna()
        latest_value = float(cleaned.iloc[-1]) if not cleaned.empty else None

        results.append({
            "feature": col,
            "correlation": round(corr, 4),
            "impact": "positive" if corr >= 0 else "negative",
            "latest_value": round(latest_value, 4) if latest_value is not None else None,
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


def ai_summarize(summary: dict, drivers: list) -> str:
    """
    Generates a macro-financial early-warning narrative for the GSSI dashboard.
    Covers inflation risk, market volatility, commodity prices, and sector impact.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    top_drivers = drivers[:5]
    driver_lines = "\n".join(
        f"  - {d['feature']}: {d['correlation']:+.4f} ({d['impact']})"
        for d in top_drivers
    )

    prompt = (
        f"You are a macro-financial analyst specialising in supply chain early-warning systems.\n"
        f"The Global Supply Chain Stress Index (GSSI) is a composite index (0-100) that signals "
        f"rising macro-financial disruption risk. Higher values indicate greater stress.\n\n"
        f"Current GSSI: {summary['current_gssi']:.2f} (Alert: {summary['current_alert']})\n"
        f"Next-week forecast: {summary['predicted_gssi']:.2f} (Alert: {summary['predicted_alert']})\n"
        f"Trend: {summary['trend']}\n"
        f"Top stress drivers:\n{driver_lines}\n\n"
        f"Write 3 sentences covering:\n"
        f"1. What the current GSSI level signals about supply chain and macro-financial conditions.\n"
        f"2. How the leading drivers link to inflation risk, market volatility, or commodity prices.\n"
        f"3. What the forecast trend means for investors, policymakers, and corporations.\n"
        f"Be specific, analytical, and avoid generic statements."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=280,
        temperature=0.4,
    )

    return response.choices[0].message.content.strip()


def ai_recommendations(summary: dict, drivers: list) -> dict:
    """
    Generates three sets of recommendations for the GSSI hackathon case:
      - "investors":   portfolio strategy actions
      - "risk":        risk management actions for corporations and financial institutions
      - "policy":      policy responses for regulators and governments

    Returns:
        {"investors": [...], "risk": [...], "policy": [...]}
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    top_drivers = drivers[:5]
    driver_lines = "\n".join(
        f"  - {d['feature']}: {d['correlation']:+.4f} ({d['impact']})"
        for d in top_drivers
    )

    prompt = (
        f"You are a macro-financial strategist advising on supply chain stress impacts.\n"
        f"The GSSI (0-100) is an early-warning index for macro-financial disruptions.\n\n"
        f"Current GSSI: {summary['current_gssi']:.2f} (Alert: {summary['current_alert']})\n"
        f"Next-week forecast: {summary['predicted_gssi']:.2f} (Alert: {summary['predicted_alert']})\n"
        f"Trend: {summary['trend']}\n"
        f"Top stress drivers:\n{driver_lines}\n\n"
        f"Respond in valid JSON only, with exactly this structure:\n"
        f'{{"investors": ["bullet 1", "bullet 2", "bullet 3"], '
        f'"risk": ["bullet 1", "bullet 2", "bullet 3"], '
        f'"policy": ["bullet 1", "bullet 2", "bullet 3"]}}\n\n'
        f'"investors": 3 portfolio strategy actions — cover asset allocation, sector exposure, '
        f'commodity hedging, or volatility positioning given this stress level.\n'
        f'"risk": 3 risk management actions for corporations and financial institutions — '
        f'cover supply chain resilience, counterparty risk, inventory, or liquidity buffers.\n'
        f'"policy": 3 policy responses for regulators or governments — '
        f'cover trade policy, strategic reserves, monetary response, or systemic risk measures.\n'
        f'Each bullet must be one specific, actionable sentence. Return only the JSON.'
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=700,
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    import json
    return json.loads(response.choices[0].message.content)


def _gssi_to_alert(value: float) -> str:
    if value < 25:
        return "Low"
    elif value < 50:
        return "Moderate"
    elif value < 75:
        return "High"
    return "Critical"
