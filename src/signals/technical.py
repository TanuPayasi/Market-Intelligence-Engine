import pandas as pd
import ta
import yfinance as yf
from datetime import datetime, timedelta

def calculate_indicators(df):
    if df is None or len(df) < 20:
        return None

    df = df.copy()
    close = df["close"]
    high = df["high"]
    low = df["low"]

    df["rsi"] = ta.momentum.RSIIndicator(close=close, window=14).rsi()

    macd = ta.trend.MACD(close=close)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    bb = ta.volatility.BollingerBands(close=close, window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_mid"] = bb.bollinger_mavg()

    df["atr"] = ta.volatility.AverageTrueRange(
        high=high, low=low, close=close, window=14
    ).average_true_range()

    return df

def get_technical_signal(df):
    if df is None or len(df) < 20:
        return {"signal": "neutral", "confidence": 0.0, "details": {}}

    latest = df.iloc[-1]
    signals = []

    rsi = latest.get("rsi")
    if pd.notna(rsi):
        if rsi < 30:
            signals.append(("bullish", 0.8))
        elif rsi > 70:
            signals.append(("bearish", 0.8))
        else:
            signals.append(("neutral", 0.4))

    macd_diff = latest.get("macd_diff")
    if pd.notna(macd_diff):
        if macd_diff > 0:
            signals.append(("bullish", 0.7))
        else:
            signals.append(("bearish", 0.7))

    close = latest.get("close")
    bb_lower = latest.get("bb_lower")
    bb_upper = latest.get("bb_upper")
    if pd.notna(close) and pd.notna(bb_lower) and pd.notna(bb_upper):
        if close <= bb_lower:
            signals.append(("bullish", 0.75))
        elif close >= bb_upper:
            signals.append(("bearish", 0.75))
        else:
            signals.append(("neutral", 0.3))

    bullish_score = sum(conf for sig, conf in signals if sig == "bullish")
    bearish_score = sum(conf for sig, conf in signals if sig == "bearish")
    total = bullish_score + bearish_score

    if total == 0:
        return {"signal": "neutral", "confidence": 0.5, "details": {}}

    if bullish_score > bearish_score:
        confidence = bullish_score / (bullish_score + bearish_score)
        signal = "bullish"
    elif bearish_score > bullish_score:
        confidence = bearish_score / (bullish_score + bearish_score)
        signal = "bearish"
    else:
        signal = "neutral"
        confidence = 0.5

    return {
        "signal": signal,
        "confidence": round(confidence, 4),
        "details": {
            "rsi": round(float(rsi), 2) if pd.notna(rsi) else None,
            "macd_diff": round(float(macd_diff), 4) if pd.notna(macd_diff) else None,
            "close": round(float(close), 2) if pd.notna(close) else None,
            "bb_upper": round(float(bb_upper), 2) if pd.notna(bb_upper) else None,
            "bb_lower": round(float(bb_lower), 2) if pd.notna(bb_lower) else None,
            "atr": round(float(latest.get("atr")), 2) if pd.notna(latest.get("atr")) else None,
        }
    }


if __name__ == "__main__":
    from src.ingestion.price_fetcher import fetch_stock_data

    ticker = "RELIANCE.NS"
    df = fetch_stock_data(ticker, days_back=60)
    df_with_indicators = calculate_indicators(df)
    signal = get_technical_signal(df_with_indicators)

    print(f"Technical signal for {ticker}:")
    print(f"Signal: {signal['signal']}")
    print(f"Confidence: {signal['confidence']}")
    print(f"Details: {signal['details']}")