from fastapi import APIRouter, HTTPException
from app.data_sources import build_features
from app.index_builder import build_gssi
from app.alerts import label_dataframe
from app.analytics import get_drivers, get_summary
from app.forecasting import train_lstm_model, forecast_next_week

router = APIRouter()


def prepare_pipeline():
    """
    Build the full pipeline:
    features -> gssi -> alerts -> forecast
    """
    features = build_features()
    if features.empty:
        raise HTTPException(status_code=500, detail="No feature data available")

    df = build_gssi(features)
    df = label_dataframe(df)

    if len(df) < 10:
        raise HTTPException(
            status_code=500,
            detail="Not enough data points to train forecast model"
        )

    model, scaler = train_lstm_model(df, lookback=8)
    forecast = forecast_next_week(df, model, scaler, lookback=8)

    return df, forecast


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "GSSI route is working"
    }


@router.get("/overview")
def get_overview():
    return {
        "project": "Global Supply Chain Stress Index",
        "frequency": "weekly",
        "model": "LSTM",
        "status": "backend scaffold ready"
    }


@router.get("/current")
def get_current():
    df, _ = prepare_pipeline()
    row = df.iloc[-1]

    return {
        "week": str(row["week"].date()) if hasattr(row["week"], "date") else str(row["week"])[:10],
        "gssi": round(float(row["gssi"]), 4),
        "alert": row["alert"],
    }


@router.get("/history")
def get_history():
    df, _ = prepare_pipeline()

    history = []
    for _, row in df[["week", "gssi"]].iterrows():
        history.append({
            "week": str(row["week"].date()) if hasattr(row["week"], "date") else str(row["week"])[:10],
            "gssi": round(float(row["gssi"]), 4),
        })

    return history


@router.get("/forecast")
def get_forecast():
    _, forecast = prepare_pipeline()

    return {
        "week": forecast["forecast_week"],
        "predicted_gssi": forecast["predicted_gssi"],
        "alert": forecast["predicted_alert"],
    }


@router.get("/drivers")
def get_driver_contributions():
    df, _ = prepare_pipeline()
    drivers = get_drivers(df)

    return [
        {
            "name": d["name"],
            "contribution": d["contribution"],
        }
        for d in drivers
    ]


@router.get("/summary")
def get_macro_summary():
    df, forecast = prepare_pipeline()
    summary_data = get_summary(df, forecast)

    return {
        "summary": summary_data["summary"]
    }


@router.get("/components")
def get_components():
    df, _ = prepare_pipeline()

    components = []
    cols = ["week", "oil_price", "market_volatility", "freight_cost", "supplier_delay", "inventory_stress"]

    for _, row in df[cols].iterrows():
        components.append({
            "week": str(row["week"].date()) if hasattr(row["week"], "date") else str(row["week"])[:10],
            "oil": round(float(row["oil_price"]), 4),
            "volatility": round(float(row["market_volatility"]), 4),
            "freight": round(float(row["freight_cost"]), 4),
            "supplier": round(float(row["supplier_delay"]), 4),
            "inventory": round(float(row["inventory_stress"]), 4),
        })

    return components