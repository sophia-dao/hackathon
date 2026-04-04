import os
import time
import random
from typing import Dict, List, Optional

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from pytrends.request import TrendReq

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
EIA_API_KEY = os.getenv("EIA_API_KEY")

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


# -----------------------------
# Utility
# -----------------------------
class DataSourceError(Exception):
    pass


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


# -----------------------------
# FRED (Macro + Supply Chain)
# -----------------------------
def fetch_fred_series(series_id: str, start_date: str) -> pd.DataFrame:
    if not FRED_API_KEY:
        raise DataSourceError("Missing FRED_API_KEY")

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
    }

    response = requests.get(FRED_BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()["observations"]

    df = pd.DataFrame(data)[["date", "value"]]
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = _safe_numeric(df["value"])
    df = df.drop(columns=["value"])

    return df


def fetch_supply_chain_fred_data(start_date="2018-01-01"):
    return {
        "oil": fetch_fred_series("DCOILWTICO", start_date),
        "freight": fetch_fred_series("FRGEXPUSM649NCIS", start_date),
        "delivery_time": fetch_fred_series("DTCDFNA066MNFRBPHI", start_date),
    }


# -----------------------------
# Yahoo Finance (Market Data)
# -----------------------------
def fetch_market_data():
    tickers = ["^GSPC", "^DJI", "^IXIC"]

    df = yf.download(tickers, period="5y", interval="1d", progress=False)

    return df


def compute_market_features(df):
    records = []

    tickers = list(set(col[0] for col in df.columns))

    for ticker in tickers:
        temp = df[ticker][["Close"]].copy()
        temp["return"] = temp["Close"].pct_change()
        temp["volatility"] = temp["return"].rolling(5).std()
        temp["ticker"] = ticker
        temp["date"] = temp.index

        records.append(temp.reset_index(drop=True))

    return pd.concat(records)


# -----------------------------
# GDELT (News Sentiment Proxy)
# -----------------------------
def fetch_gdelt_article_list(query, max_records=50, retries=3):
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": max_records,
        "format": "json",
    }

    for attempt in range(retries):
        response = requests.get(GDELT_DOC_URL, params=params)

        if response.status_code == 429:
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"[GDELT] Rate limited. Waiting {wait:.2f}s")
            time.sleep(wait)
            continue

        try:
            response.raise_for_status()
            data = response.json()["articles"]

            df = pd.DataFrame(data)

            return df[["seendate", "title"]]

        except:
            time.sleep(1)

    return pd.DataFrame()


def fetch_news_signal():
    df = fetch_gdelt_article_list("supply chain", max_records=30)

    if df.empty:
        return pd.DataFrame(columns=["date", "article_count"])

    df["date"] = pd.to_datetime(df["seendate"]).dt.date

    return (
        df.groupby("date")
        .size()
        .reset_index(name="article_count")
    )


# -----------------------------
# Google Trends (Optional)
# -----------------------------
def fetch_google_trends():
    try:
        pytrends = TrendReq()
        pytrends.build_payload(["supply chain", "shipping delays"])

        df = pytrends.interest_over_time().reset_index()

        return df.drop(columns=["isPartial"])

    except:
        print("[Trends] Failed — skipping")
        return pd.DataFrame()


# -----------------------------
# Merge Helper
# -----------------------------
def merge_data(data_dict: Dict[str, pd.DataFrame]):
    dfs = []

    for df in data_dict.values():
        df["date"] = pd.to_datetime(df["date"])
        dfs.append(df)

    merged = dfs[0]

    for df in dfs[1:]:
        merged = merged.merge(df, on="date", how="outer")

    return merged.sort_values("date")