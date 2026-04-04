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

    clean_data = preprocess_pipeline(features)
    if clean_data.empty:
        raise HTTPException(status_code=500, detail="Preprocessing failed")

    gssi_df = build_gssi_pipeline(clean_data)
    if gssi_df.empty:
        raise HTTPException(status_code=500, detail="GSSI build failed")

    X, y = build_sequences(gssi_df)
    if len(X) == 0 or len(y) == 0:
        raise HTTPException(status_code=500, detail="Sequence building failed")

    forecast = forecast_next_week(X, y)

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