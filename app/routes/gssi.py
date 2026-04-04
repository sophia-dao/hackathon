from fastapi import APIRouter, HTTPException

from app.data_sources import build_features
from app.preprocessing import preprocess_pipeline
from app.index_builder import build_gssi_pipeline
from app.sequence_builder import build_sequences
from app.forecasting import forecast_next_week
from app.alerts import generate_alerts
from app.analytics import get_summary, get_drivers

router = APIRouter()


@router.get("/run")
def run_pipeline():
    try:
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

        forecast = forecast_next_week(X, y)

        alerts = generate_alerts(gssi_df, forecast)

        # In case generate_alerts returns an updated dataframe,
        # use it. Otherwise keep original gssi_df.
        if hasattr(alerts, "columns"):
            gssi_df = alerts
            alert_output = gssi_df.tail(5)[["week", "gssi", "alert"]].to_dict(orient="records") if "week" in gssi_df.columns else gssi_df.tail(5)[["date", "gssi", "alert"]].to_dict(orient="records")
        else:
            alert_output = alerts

        summary = get_summary(gssi_df, forecast)
        drivers = get_drivers(gssi_df)

        date_col = "week" if "week" in gssi_df.columns else "date"

        return {
            "message": "GSSI pipeline executed successfully",
            "latest_gssi": gssi_df.tail(5).to_dict(orient="records"),
            "forecast": forecast,
            "alerts": alert_output,
            "drivers": drivers,
            "summary": summary,
            "date_column_used": date_col,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def summary_endpoint():
    try:
        features = build_features()
        clean_data = preprocess_pipeline(features)
        gssi_df = build_gssi_pipeline(clean_data)
        X, y = build_sequences(gssi_df)
        forecast = forecast_next_week(X, y)
        alerts = generate_alerts(gssi_df, forecast)

        if hasattr(alerts, "columns"):
            gssi_df = alerts

        return get_summary(gssi_df, forecast)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drivers")
def drivers_endpoint():
    try:
        features = build_features()
        clean_data = preprocess_pipeline(features)
        gssi_df = build_gssi_pipeline(clean_data)
        X, y = build_sequences(gssi_df)
        forecast = forecast_next_week(X, y)
        alerts = generate_alerts(gssi_df, forecast)

        if hasattr(alerts, "columns"):
            gssi_df = alerts

        return {"drivers": get_drivers(gssi_df)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))