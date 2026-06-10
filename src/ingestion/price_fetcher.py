import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

STOCK_MAPPING = {
    "reliance": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "wipro": "WIPRO.NS",
    "sbi": "SBIN.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "hul": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "indigo": "INDIGO.NS",
    "nifty": "^NSEI",
    "sensex": "^BSESN",
    "nifty 50": "^NSEI",
}

def get_ticker_for_entity(entity_name):
    entity_lower = entity_name.lower().strip()
    for key, ticker in STOCK_MAPPING.items():
        if key in entity_lower or entity_lower in key:
            return ticker
    return None

def fetch_stock_data(ticker, days_back=30):
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        df = stock.history(start=start_date, end=end_date)

        if df.empty:
            return None

        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        df = df[["date", "open", "high", "low", "close", "volume"]]
        df["ticker"] = ticker

        return df

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def fetch_multiple_stocks(tickers, days_back=30):
    results = {}
    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back)
        if df is not None:
            results[ticker] = df
            print(f"Fetched {len(df)} days of data for {ticker}")
    return results

if __name__ == "__main__":
    tickers = ["RELIANCE.NS", "TCS.NS", "^NSEI"]
    data = fetch_multiple_stocks(tickers, days_back=30)

    for ticker, df in data.items():
        print(f"\n{ticker}:")
        print(df.tail(3).to_string())