import pandas as pd


def generate_alerts(gssi_value: float) -> dict:
    """
    Return alert level for a single GSSI value.

    Thresholds:
        < -0.5   → Low
        -0.5–0.5 → Moderate
        0.5–1.5  → High
        > 1.5    → Critical
    """
    return {
        "gssi_value": round(gssi_value, 4),
        "alert_level": _alert_label(gssi_value),
    }


def label_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add an 'alert' column to Sophia's DataFrame based on GSSI values.

    Args:
        df: DataFrame with a 'gssi' column

    Returns:
        DataFrame with an added 'alert' column (does not modify in place)
    """
    df = df.copy()
    df["alert"] = df["gssi"].apply(_alert_label)
    return df


def _alert_label(gssi_value: float) -> str:
    if gssi_value < -0.5:
        return "Low"
    elif gssi_value < 0.5:
        return "Moderate"
    elif gssi_value < 1.5:
        return "High"
    else:
        return "Critical"
