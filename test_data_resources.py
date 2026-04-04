from app.data_sources import (
    fetch_supply_chain_fred_data,
    fetch_yfinance_indices,
    compute_market_features,
    fetch_news_signal,
)

fred_data = fetch_supply_chain_fred_data(start_date="2022-01-01")
print("FRED keys:", fred_data.keys())
for name, df in fred_data.items():
    print(f"\n{name}")
    print(df.head())

market_raw = fetch_yfinance_indices()
market_features = compute_market_features(market_raw)
print("\nMarket features:")
print(market_features.head())

news_df = fetch_news_signal()
print("\nNews signal:")
print(news_df.head())