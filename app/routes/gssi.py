from fastapi import APIRouter, HTTPException
import pandas as pd
from datetime import datetime, UTC

from app.data_sources import build_features
from app.preprocessing import preprocess_pipeline
from app.index_builder import build_gssi_pipeline
from app.sequence_builder import build_sequences
from app.forecasting import forecast_next_week
from app.alerts import generate_alerts
from app.analytics import get_summary, get_drivers

router = APIRouter()

pipeline_cache = {
    "clean_data": None,
    "gssi_df": None,
    "forecast": None,
    "last_updated": None,
}


def get_clean_data():
    features = build_features()

    if not features:
        raise HTTPException(status_code=500, detail="No data fetched")

    weekly_methods = [
        "mean",  # oil
        "last",  # freight
        "last",  # delivery_time
        "last",  # inventory_stress_total
        "last",  # inventory_stress_mfg
        "last",  # inventory_stress_wholesale
        "last",  # inventory_stress_retail
        "mean",  # market
        "sum",   # news_count
        "mean",  # trends
    ]

    if len(features) != len(weekly_methods):
        raise HTTPException(
            status_code=500,
            detail=f"Mismatch: build_features returned {len(features)} dataframes but weekly_methods has {len(weekly_methods)} entries."
        )

    clean_data, _ = preprocess_pipeline(
        raw_dataframes=features,
        weekly_methods=weekly_methods,
        fill_method="ffill_bfill",
        apply_outlier_clipping=True,
        add_inventory_derived_features=True,
    )

    if clean_data.empty:
        raise HTTPException(status_code=500, detail="Preprocessing failed")

    return clean_data


def get_gssi_data():
    clean_data = get_clean_data()
    gssi_df = build_gssi_pipeline(clean_data)

    if gssi_df.empty:
        raise HTTPException(status_code=500, detail="GSSI build failed")

    return gssi_df


def get_forecast(gssi_df):
    X, y = build_sequences(gssi_df)

    if len(X) == 0 or len(y) == 0:
        raise HTTPException(status_code=500, detail="Sequence building failed")

    return forecast_next_week(X, y)


def apply_alerts_if_needed(gssi_df, forecast):
    alerts = generate_alerts(gssi_df, forecast)

    if isinstance(alerts, pd.DataFrame):
        return alerts

    return gssi_df


def require_cache():
    if pipeline_cache["gssi_df"] is None:
        raise HTTPException(
            status_code=400,
            detail="No cached pipeline result found. Call /run first."
        )


@router.get("/run")
def run_pipeline():
    try:
        gssi_df = get_gssi_data()
        forecast = get_forecast(gssi_df)
        gssi_with_alerts = apply_alerts_if_needed(gssi_df, forecast)

        pipeline_cache["clean_data"] = None  # optional
        pipeline_cache["gssi_df"] = gssi_with_alerts
        pipeline_cache["forecast"] = forecast
        pipeline_cache["last_updated"] = datetime.now(UTC).isoformat()

        return {
            "message": "GSSI pipeline executed successfully",
            "last_updated": pipeline_cache["last_updated"],
            "latest_gssi": gssi_with_alerts.tail(5).to_dict(orient="records"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
def forecast_endpoint():
    try:
        require_cache()
        return {
            "last_updated": pipeline_cache["last_updated"],
            "forecast": pipeline_cache["forecast"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
def alerts_endpoint():
    try:
        require_cache()

        gssi_df = pipeline_cache["gssi_df"]
        date_col = "week" if "week" in gssi_df.columns else "date"

        if "alert" not in gssi_df.columns:
            return {
                "last_updated": pipeline_cache["last_updated"],
                "alerts": [],
            }

        return {
            "last_updated": pipeline_cache["last_updated"],
            "alerts": gssi_df.tail(5)[[date_col, "gssi", "alert"]].to_dict(orient="records"),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def summary_endpoint():
    try:
        require_cache()

        gssi_df = pipeline_cache["gssi_df"]
        forecast = pipeline_cache["forecast"]

        return {
            "last_updated": pipeline_cache["last_updated"],
            "summary": get_summary(gssi_df, forecast),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drivers")
def drivers_endpoint():
    try:
        require_cache()

        gssi_df = pipeline_cache["gssi_df"]

        return {
            "last_updated": pipeline_cache["last_updated"],
            "drivers": get_drivers(gssi_df),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))