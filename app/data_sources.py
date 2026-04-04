import os
import time
import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def _to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def merge_data(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    dfs = [df for df in dfs if not df.empty]

    if not dfs:
        return pd.DataFrame()

    for df in dfs:
        df["week"] = pd.to_datetime(df["week"])

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="week", how="outer")

    return merged.sort_values("week").reset_index(drop=True)


def to_weekly(df: pd.DataFrame, method="mean") -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    if method == "sum":
        df = df.resample("W-SUN").sum()
    elif method == "last":
        df = df.resample("W-SUN").last()
    else:
        df = df.resample("W-SUN").mean()

    df = df.reset_index().rename(columns={"date": "week"})
    return df


def fetch_fred(series_id: str, start="2018-01-01") -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
    }

    r = requests.get(FRED_URL, params=params, timeout=30)
    r.raise_for_status()

    data = r.json()["observations"]

    df = pd.DataFrame(data)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = _to_numeric(df["value"])

    return df.drop(columns=["value"])


def fetch_fred_features() -> list[pd.DataFrame]:
    oil = fetch_fred("DCOILWTICO").rename(columns={"DCOILWTICO": "oil_price"})
    freight = fetch_fred("FRGEXPUSM649NCIS").rename(columns={"FRGEXPUSM649NCIS": "freight_cost"})
    supplier_delay = fetch_fred("DTCDFNA066MNFRBPHI").rename(
        columns={"DTCDFNA066MNFRBPHI": "supplier_delay"}
    )

    return [
        to_weekly(oil),
        to_weekly(freight),
        to_weekly(supplier_delay),
    ]


def fetch_market_data() -> pd.DataFrame:
    tickers = ["^GSPC", "^DJI", "^IXIC"]

    df = yf.download(
        tickers,
        period="5y",
        interval="1d",
        group_by="column",
        progress=False,
    )

    return df


def compute_market_features(df: pd.DataFrame) -> pd.DataFrame:
    close_df = df["Close"]

    features = []

    for ticker in close_df.columns:
        temp = pd.DataFrame({
            "date": close_df.index,
            f"{ticker}_close": close_df[ticker],
        })

        temp[f"{ticker}_return"] = temp[f"{ticker}_close"].pct_change()
        temp[f"{ticker}_vol"] = temp[f"{ticker}_return"].rolling(5).std()

        temp = to_weekly(temp, method="mean")
        features.append(temp)

    merged = merge_data(features)

    merged = merged.rename(columns={
        "^GSPC_vol": "sp500_vol",
        "^DJI_vol": "dow_vol",
        "^IXIC_vol": "nasdaq_vol",
    })

    # collapse into one market_volatility feature
    vol_cols = [c for c in ["sp500_vol", "dow_vol", "nasdaq_vol"] if c in merged.columns]
    if vol_cols:
        merged["market_volatility"] = merged[vol_cols].mean(axis=1)

    return merged[["week", "market_volatility"]]


def fetch_news():
    params = {
        "query": "supply chain",
        "mode": "ArtList",
        "maxrecords": 30,
        "format": "json",
    }

    try:
        r = requests.get(GDELT_URL, params=params, timeout=5)

        if r.status_code != 200:
            print("GDELT failed with status:", r.status_code)
            return pd.DataFrame()

        data = r.json().get("articles", [])
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        df["date"] = pd.to_datetime(df["seendate"])
        daily = df.groupby(df["date"].dt.date).size().reset_index(name="news_count")
        daily.columns = ["date", "news_count"]

        return to_weekly(daily, method="sum")

    except Exception as e:
        print("GDELT ERROR:", e)
        return pd.DataFrame()


def fetch_trends() -> pd.DataFrame:
    try:
        pytrends = TrendReq()
        pytrends.build_payload(["trend_supply_chain", "trend_shipping_delays"])

        df = pytrends.interest_over_time().reset_index()
        df = df.drop(columns=["isPartial"])

        df = to_weekly(df, method="mean")

        # turn trends into a single inventory_stress proxy
        trend_cols = [c for c in ["trend_supply_chain", "trend_shipping_delays"] if c in df.columns]
        if trend_cols:
            df["inventory_stress"] = df[trend_cols].mean(axis=1)

        return df[["week", "inventory_stress"]]
    except Exception:
        print("Trends failed")
        return pd.DataFrame()


def build_features() -> pd.DataFrame:
    fred = fetch_fred_features()
    market = compute_market_features(fetch_market_data())
    news = fetch_news()
    trends = fetch_trends()

    df = merge_data(fred + [market, news, trends])

    if df.empty:
        return df

    # fallback if trends/news are missing
    if "inventory_stress" not in df.columns:
        if "news_count" in df.columns:
            df["inventory_stress"] = df["news_count"]
        else:
            df["inventory_stress"] = 0.0

    required = [
        "week",
        "freight_cost",
        "supplier_delay",
        "oil_price",
        "market_volatility",
        "inventory_stress",
    ]

    for col in required:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[required].sort_values("week").reset_index(drop=True)
    df = df.ffill().bfill()

    return df