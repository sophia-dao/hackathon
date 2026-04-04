import os
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
EIA_BASE_URL = "https://api.eia.gov/v2"
GDELT_DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"


class DataSourceError(Exception):
    """Raised when an upstream data source fails."""
    pass


def _safe_numeric(series: pd.Series) -> pd.Series:
    """Convert values to numeric, coercing bad strings like '.' to NaN."""
    return pd.to_numeric(series, errors="coerce")


def fetch_fred_series(
    series_id: str,
    observation_start: Optional[str] = None,
    observation_end: Optional[str] = None,
    frequency: Optional[str] = None,
    aggregation_method: str = "avg",
) -> pd.DataFrame:
    """
    Fetch one FRED time series as a DataFrame with columns:
    ['date', '<series_id>']
    """
    if not FRED_API_KEY:
        raise DataSourceError("Missing FRED_API_KEY in environment.")

    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
    }

    if observation_start:
        params["observation_start"] = observation_start
    if observation_end:
        params["observation_end"] = observation_end
    if frequency:
        params["frequency"] = frequency
        params["aggregation_method"] = aggregation_method

    response = requests.get(FRED_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    observations = payload.get("observations", [])
    if not observations:
        raise DataSourceError(f"No FRED observations returned for {series_id}")

    df = pd.DataFrame(observations)[["date", "value"]].copy()
    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = _safe_numeric(df["value"])
    df = df.drop(columns=["value"]).sort_values("date").reset_index(drop=True)

    return df


def fetch_supply_chain_fred_data(
    start_date: str = "2018-01-01",
    end_date: Optional[str] = None,
) -> Dict[str, pd.DataFrame]:
    """
    Suggested FRED series:
    - DCOILWTICO: WTI crude oil
    - FRGEXPUSM649NCIS: Cass Freight Expenditures
    - DTCDFNA066MNFRBPHI: Current Delivery Time
    """
    series_map = {
        "oil_wti": "DCOILWTICO",
        "cass_freight_expenditures": "FRGEXPUSM649NCIS",
        "supplier_delivery_time": "DTCDFNA066MNFRBPHI",
    }

    results = {}
    for name, series_id in series_map.items():
        results[name] = fetch_fred_series(
            series_id=series_id,
            observation_start=start_date,
            observation_end=end_date,
        )

    return results


def fetch_yfinance_indices(
    tickers: Optional[List[str]] = None,
    period: str = "5y",
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Fetch market index data from yfinance.
    Default tickers:
    - ^GSPC : S&P 500
    - ^DJI  : Dow Jones
    - ^IXIC : Nasdaq Composite
    """
    if tickers is None:
        tickers = ["^GSPC", "^DJI", "^IXIC"]

    df = yf.download(
        tickers=tickers,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        group_by="ticker",
        threads=True,
    )

    if df.empty:
        raise DataSourceError("No data returned from yfinance.")

    return df


def compute_market_features(price_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert yfinance OHLC data into a compact feature table:
    - daily close
    - daily return
    - 5-day rolling volatility
    """
    records = []

    # MultiIndex columns expected when downloading multiple tickers
    tickers = sorted(set(col[0] for col in price_df.columns))

    for ticker in tickers:
        ticker_df = price_df[ticker].copy()
        if "Close" not in ticker_df.columns:
            continue

        tmp = ticker_df[["Close"]].copy()
        tmp = tmp.rename(columns={"Close": "close"})
        tmp["return"] = tmp["close"].pct_change()
        tmp["volatility_5d"] = tmp["return"].rolling(5).std()
        tmp["ticker"] = ticker
        tmp["date"] = tmp.index
        records.append(tmp.reset_index(drop=True))

    if not records:
        raise DataSourceError("Could not compute market features from yfinance output.")

    return pd.concat(records, ignore_index=True)


import time
import random


def fetch_gdelt_article_list(
    query: str,
    max_records: int = 100,
    retries: int = 3,
    backoff_factor: float = 1.5,
) -> pd.DataFrame:
    """
    Fetch GDELT articles with retry + backoff to handle rate limits.
    """

    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": max_records,
        "format": "json",
    }

    for attempt in range(retries):
        try:
            response = requests.get(GDELT_DOC_URL, params=params, timeout=30)

            # Handle rate limit manually
            if response.status_code == 429:
                wait_time = backoff_factor ** attempt + random.uniform(0, 1)
                print(f"[GDELT] Rate limited. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            payload = response.json()

            articles = payload.get("articles", [])
            if not articles:
                return pd.DataFrame()

            df = pd.DataFrame(articles)

            keep_cols = [
                c for c in [
                    "url",
                    "title",
                    "seendate",
                    "domain",
                    "language",
                    "sourcecountry"
                ] if c in df.columns
            ]

            return df[keep_cols].copy()

        except Exception as e:
            if attempt == retries - 1:
                print(f"[GDELT] Failed after retries: {e}")
                return pd.DataFrame()
            else:
                wait_time = backoff_factor ** attempt
                time.sleep(wait_time)

    return pd.DataFrame()

def fetch_news_signal(
    query: str = '"supply chain disruption" OR "shipping delays" OR "port congestion"',
    max_records: int = 100,
) -> pd.DataFrame:
    """
    Create a simple daily/weekly news-volume signal from GDELT article results.
    """
    df = fetch_gdelt_article_list(query=query, max_records=max_records)

    if df.empty:
        return pd.DataFrame(columns=["date", "article_count"])

    df["date"] = pd.to_datetime(df["seendate"], errors="coerce").dt.date
    volume = (
        df.groupby("date")
        .size()
        .reset_index(name="article_count")
        .sort_values("date")
    )
    volume["date"] = pd.to_datetime(volume["date"])

    return volume


def fetch_google_trends(
    keywords: List[str],
    timeframe: str = "today 5-y",
    geo: str = "",
) -> pd.DataFrame:
    """
    Fetch Google Trends interest-over-time data.
    Note: pytrends is unofficial and may break.
    """
    if not keywords:
        raise ValueError("keywords must not be empty")

    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
    df = pytrends.interest_over_time()

    if df.empty:
        return pd.DataFrame()

    df = df.reset_index()
    if "isPartial" in df.columns:
        df = df.drop(columns=["isPartial"])

    return df


def fetch_eia_series(
    route: str,
    facets: Optional[Dict[str, List[str]]] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    frequency: str = "daily",
    data_fields: Optional[List[str]] = None,
    sort_column: str = "period",
    sort_direction: str = "asc",
    offset: int = 0,
    length: int = 5000,
) -> pd.DataFrame:
    """
    Generic EIA v2 fetcher.

    Example route:
    /petroleum/pri/spt/data
    """
    if not EIA_API_KEY:
        raise DataSourceError("Missing EIA_API_KEY in environment.")

    if data_fields is None:
        data_fields = ["value"]

    url = f"{EIA_BASE_URL}{route}"

    params = {
        "api_key": EIA_API_KEY,
        "frequency": frequency,
        "data[0]": data_fields[0],
        "sort[0][column]": sort_column,
        "sort[0][direction]": sort_direction,
        "offset": offset,
        "length": length,
    }

    # support multiple requested fields
    for i, field in enumerate(data_fields):
        params[f"data[{i}]"] = field

    if start:
        params["start"] = start
    if end:
        params["end"] = end

    if facets:
        facet_index = 0
        for facet_name, facet_values in facets.items():
            for value in facet_values:
                params[f"facets[{facet_name}][{facet_index}]"] = value
                facet_index += 1

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    records = payload.get("response", {}).get("data", [])
    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def fetch_energy_data_example() -> pd.DataFrame:
    """
    Example EIA pull for spot petroleum price data.
    You may need to adjust route/facets after testing in EIA's API browser.
    """
    return fetch_eia_series(
        route="/petroleum/pri/spt/data",
        facets={
            "product": ["EPCWTI"],   # WTI spot-style identifier in some EIA datasets
        },
        frequency="daily",
        data_fields=["value"],
        start="2020-01-01",
    )


def merge_on_date(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Outer-join a list of DataFrames on 'date'.
    """
    valid = [df.copy() for df in dataframes if df is not None and not df.empty]
    if not valid:
        return pd.DataFrame()

    for df in valid:
        df["date"] = pd.to_datetime(df["date"])

    merged = valid[0]
    for df in valid[1:]:
        merged = merged.merge(df, on="date", how="outer")

    return merged.sort_values("date").reset_index(drop=True)