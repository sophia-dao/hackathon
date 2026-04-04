import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.data_sources import (
    fetch_fred_features,
    fetch_market_data,
    compute_market_features,
    fetch_news,
    fetch_trends,
    build_features,
)

print("\n===== 2. TEST FRED FEATURES =====")
try:
    fred_features = fetch_fred_features()
    for i, df in enumerate(fred_features, start=1):
        print(f"\nFRED feature {i}")
        print(df.head())
        print("Shape:", df.shape)
except Exception as e:
    print("FRED failed:", e)

print("\n===== 3. TEST MARKET RAW DATA =====")
try:
    market_raw = fetch_market_data()
    print(market_raw.head())
    print("Market raw shape:", market_raw.shape)
    print("Market raw columns:")
    print(market_raw.columns)
except Exception as e:
    print("Market raw failed:", e)

print("\n===== 4. TEST MARKET FEATURES =====")
try:
    market_raw = fetch_market_data()
    market_features = compute_market_features(market_raw)
    print(market_features.head())
    print("Market features shape:", market_features.shape)
except Exception as e:
    print("Market features failed:", e)

print("\n===== 5. TEST NEWS =====")
try:
    news = fetch_news()
    print(news.head())
    print("News shape:", news.shape)
except Exception as e:
    print("News failed:", e)

print("\n===== 6. TEST TRENDS =====")
try:
    trends = fetch_trends()
    print(trends.head())
    print("Trends shape:", trends.shape)
except Exception as e:
    print("Trends failed:", e)

print("\n===== 7. TEST BUILD FEATURES =====")
try:
    features = build_features()
    print(features.head())
    print("Features shape:", features.shape)
    print("Feature columns:")
    print(features.columns.tolist())
except Exception as e:
    print("Build features failed:", e)
