import os
import time
import random
from typing import Dict, List

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


# =============================
# UTIL
# =============================
def _to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def merge_data(dfs: List[pd.DataFrame]):
    dfs = [df for df in dfs if not df.empty]

    if not dfs:
        return pd.DataFrame()

    for df in dfs:
        df["date"] = pd.to_datetime(df["date"])

    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="date", how="outer")

    return merged.sort_values("date")


def to_monthly(df, method="mean"):
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")

    if method == "sum":
        df = df.resample("MS").sum()
    elif method == "last":
        df = df.resample("MS").last()
    else:
        df = df.resample("MS").mean()

    return df.reset_index()


# =============================
# FRED DATA
# =============================
def fetch_fred(series_id, start="2018-01-01"):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
    }

    r = requests.get(FRED_URL, params=params)
    r.raise_for_status()

    data = r.json()["observations"]

    df = pd.DataFrame(data)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = _to_numeric(df["value"])

    return df.drop(columns=["value"])


def fetch_fred_features():
    oil = fetch_fred("DCOILWTICO").rename(columns={"DCOILWTICO": "oil"})
    freight = fetch_fred("FRGEXPUSM649NCIS").rename(columns={"FRGEXPUSM649NCIS": "freight"})
    delivery = fetch_fred("DTCDFNA066MNFRBPHI").rename(columns={"DTCDFNA066MNFRBPHI": "delivery_time"})

    return [
        to_monthly(oil),
        to_monthly(freight),
        to_monthly(delivery),
    ]


# =============================
# MARKET DATA
# =============================
def fetch_market_data():
    tickers = ["^GSPC", "^DJI", "^IXIC"]

    df = yf.download(
        tickers,
        period="5y",
        interval="1d",
        group_by="column",
        progress=False,
    )

    return df


def compute_market_features(df):
    close_df = df["Close"]  # works with group_by="column"

    features = []

    for ticker in close_df.columns:
        temp = pd.DataFrame({
            "date": close_df.index,
            f"{ticker}_close": close_df[ticker],
        })

        temp[f"{ticker}_return"] = temp[f"{ticker}_close"].pct_change()
        temp[f"{ticker}_vol"] = temp[f"{ticker}_return"].rolling(5).std()

        temp = to_monthly(temp)

        features.append(temp)

    merged = merge_data(features)

    # rename for clarity
    return merged.rename(columns={
        "^GSPC_close": "sp500_close",
        "^GSPC_return": "sp500_return",
        "^GSPC_vol": "sp500_vol",
        "^DJI_close": "dow_close",
        "^DJI_return": "dow_return",
        "^DJI_vol": "dow_vol",
        "^IXIC_close": "nasdaq_close",
        "^IXIC_return": "nasdaq_return",
        "^IXIC_vol": "nasdaq_vol",
    })


# =============================
# NEWS (GDELT)
# =============================
def fetch_news():
    params = {
        "query": "supply chain",
        "mode": "ArtList",
        "maxrecords": 30,
        "format": "json",
    }

    for i in range(3):
        r = requests.get(GDELT_URL, params=params)

        if r.status_code == 429:
            time.sleep(2 ** i)
            continue

        try:
            data = r.json()["articles"]
            df = pd.DataFrame(data)

            df["date"] = pd.to_datetime(df["seendate"])

            daily = df.groupby(df["date"].dt.date).size().reset_index(name="news_count")
            daily.columns = ["date", "news_count"]

            return to_monthly(daily, method="sum")

        except:
            time.sleep(1)

    return pd.DataFrame()


# =============================
# GOOGLE TRENDS
# =============================
def fetch_trends():
    try:
        pytrends = TrendReq()
        pytrends.build_payload(["trend_supply_chain", "trend_shipping_delays"])

        df = pytrends.interest_over_time().reset_index()
        df = df.drop(columns=["isPartial"])

        return to_monthly(df)

    except:
        print("Trends failed")
        return pd.DataFrame()


# =============================
# BUILD FEATURE MATRIX
# =============================
def build_features():
    fred = fetch_fred_features()
    market = compute_market_features(fetch_market_data())
    news = fetch_news()
    trends = fetch_trends()

    return merge_data(fred + [market, news, trends])

