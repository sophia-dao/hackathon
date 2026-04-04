from fastapi import APIRouter, HTTPException
import pandas as pd

from app.data_sources import build_features
from app.preprocessing import preprocess_pipeline
from app.index_builder import build_gssi_pipeline
from app.sequence_builder import build_sequences
from app.forecasting import forecast_next_week
from app.alerts import generate_alerts
from app.analytics import get_summary, get_drivers

router = APIRouter()


def execute_pipeline():
    features = build_features()
    if features.empty:
        raise HTTPException(status_code=500, detail="No data fetched")

    clean_data, _ = preprocess_pipeline([features])
    if clean_data.empty:
        raise HTTPException(status_code=500, detail="Preprocessing failed")

    gssi_df = build_gssi_pipeline(clean_data)
    if gssi_df.empty:
        raise HTTPException(status_code=500, detail="GSSI build failed")

    # Merge feature columns back so driver analysis has data to correlate
    date_col = "week" if "week" in gssi_df.columns else "date"
    feature_cols = [c for c in clean_data.columns if c != date_col]
    gssi_df = gssi_df.merge(clean_data[[date_col] + feature_cols], on=date_col, how="left")
    X, y, _ = build_sequences(gssi_df, drop_cols=[date_col])
    if len(X) == 0 or len(y) == 0:
        raise HTTPException(status_code=500, detail="Sequence building failed")

    forecast = forecast_next_week(gssi_df)

    alerts = generate_alerts(gssi_df, forecast)
    if isinstance(alerts, pd.DataFrame):
        gssi_df = alerts

    return gssi_df, forecast


@router.get("/run")
def run_pipeline():
    try:
        gssi_df, forecast = execute_pipeline()

        date_col = "week" if "week" in gssi_df.columns else "date"

        alert_output = []
        if "alert" in gssi_df.columns:
            alert_output = gssi_df.tail(5)[[date_col, "gssi", "alert"]].to_dict(orient="records")

        return {
            "message": "GSSI pipeline executed successfully",
            "latest_gssi": gssi_df.tail(5).to_dict(orient="records"),
            "forecast": forecast,
            "alerts": alert_output,
            "drivers": get_drivers(gssi_df),
            "summary": get_summary(gssi_df, forecast),
            "date_column_used": date_col,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
def current_endpoint():
    try:
        gssi_df, forecast = execute_pipeline()
        date_col = "week" if "week" in gssi_df.columns else "date"
        latest = gssi_df.sort_values(date_col).iloc[-1]
        alert = latest["alert"] if "alert" in gssi_df.columns else None
        return {
            "week": str(latest[date_col]),
            "gssi": round(float(latest["gssi"]), 4),
            "alert": alert,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def history_endpoint():
    try:
        gssi_df, _ = execute_pipeline()
        date_col = "week" if "week" in gssi_df.columns else "date"
        gssi_df = gssi_df.sort_values(date_col)
        cols = [date_col, "gssi"] + (["alert"] if "alert" in gssi_df.columns else [])
        return {"history": gssi_df[cols].to_dict(orient="records")}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
def forecast_endpoint():
    try:
        _, forecast = execute_pipeline()
        return forecast

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def summary_endpoint():
    try:
        gssi_df, forecast = execute_pipeline()
        return get_summary(gssi_df, forecast)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drivers")
def drivers_endpoint():
    try:
        gssi_df, _ = execute_pipeline()
        return {"drivers": get_drivers(gssi_df)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))