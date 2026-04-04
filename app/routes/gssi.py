from fastapi import APIRouter, HTTPException
import pandas as pd
import time

from app.data_sources import build_features
from app.preprocessing import preprocess_pipeline
from app.index_builder import build_gssi_pipeline
from app.sequence_builder import build_sequences
from app.forecasting import forecast_next_week
from app.alerts import generate_alerts
from app.analytics import get_summary, get_drivers, ai_summarize, ai_recommendations

router = APIRouter()

# In-memory cache: holds last pipeline result for CACHE_TTL seconds
_cache: dict = {}
CACHE_TTL = 3600  # 1 hour


def _run_pipeline():
    features = build_features()
    if features.empty:
        raise HTTPException(status_code=500, detail="No data fetched")

    clean_data, _ = preprocess_pipeline([features])
    if clean_data.empty:
        raise HTTPException(status_code=500, detail="Preprocessing failed")

    gssi_df = build_gssi_pipeline(clean_data)
    if gssi_df.empty:
        raise HTTPException(status_code=500, detail="GSSI build failed")

    date_col = "week" if "week" in gssi_df.columns else "date"
    feature_cols = [c for c in clean_data.columns if c != date_col]
    gssi_df = gssi_df.merge(clean_data[[date_col] + feature_cols], on=date_col, how="left")
    X, y, _ = build_sequences(gssi_df, drop_cols=[date_col])
    if len(X) == 0 or len(y) == 0:
        raise HTTPException(status_code=500, detail="Sequence building failed")

    forecast = forecast_next_week(gssi_df)

    alerts = generate_alerts(gssi_df, forecast)
    if isinstance(alerts, pd.DataFrame):
        # generate_alerts appends the forecast as a new row — strip it so
        # gssi_df only contains real historical data. The forecast row would
        # make iloc[-1] return the predicted value instead of the current one.
        gssi_df = alerts.iloc[:-1].reset_index(drop=True)

    return gssi_df, forecast, features


def execute_pipeline(force_refresh: bool = False):
    now = time.time()
    if not force_refresh and "result" in _cache and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["result"]

    result = _run_pipeline()
    _cache["result"] = result
    _cache["ts"] = now
    return result


@router.post("/refresh")
def refresh_cache():
    """Force a full pipeline re-run and update the cache."""
    try:
        execute_pipeline(force_refresh=True)
        return {"message": "Cache refreshed successfully", "cached_until": time.time() + CACHE_TTL}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache-status")
def cache_status():
    if "ts" not in _cache:
        return {"cached": False}
    age = int(time.time() - _cache["ts"])
    return {"cached": True, "age_seconds": age, "expires_in_seconds": max(0, CACHE_TTL - age)}


@router.get("/run")
def run_pipeline():
    try:
        gssi_df, forecast, raw_features = execute_pipeline()

        date_col = "week" if "week" in gssi_df.columns else "date"

        alert_output = []
        if "alert" in gssi_df.columns:
            alert_output = gssi_df.tail(5)[[date_col, "gssi", "alert"]].to_dict(orient="records")

        return {
            "message": "GSSI pipeline executed successfully",
            "latest_gssi": gssi_df.tail(5).to_dict(orient="records"),
            "forecast": forecast,
            "alerts": alert_output,
            "drivers": get_drivers(gssi_df, raw_df=raw_features),
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
        gssi_df, forecast, _ = execute_pipeline()
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
        gssi_df, _, __ = execute_pipeline()
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
        _, forecast, __ = execute_pipeline()
        return forecast

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
def summary_endpoint():
    try:
        gssi_df, forecast, _ = execute_pipeline()
        return get_summary(gssi_df, forecast)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai-summary")
def ai_summary_endpoint():
    try:
        gssi_df, forecast, raw_features = execute_pipeline()
        summary = get_summary(gssi_df, forecast)
        drivers = get_drivers(gssi_df, raw_df=raw_features)
        try:
            narrative = ai_summarize(summary, drivers)
        except Exception:
            narrative = None
        try:
            recs = ai_recommendations(summary, drivers)
        except Exception:
            recs = None
        return {"ai_summary": narrative, "ai_recommendations": recs, **summary}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drivers")
def drivers_endpoint():
    try:
        gssi_df, _, raw_features = execute_pipeline()
        return {"drivers": get_drivers(gssi_df, raw_df=raw_features)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))