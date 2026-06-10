from src.nlp.sentiment import analyze_sentiment
from src.nlp.ner import extract_entities, map_to_ticker
from src.signals.technical import calculate_indicators, get_technical_signal
from src.ingestion.price_fetcher import fetch_stock_data

CONFIDENCE_THRESHOLD = 0.65

def generate_signal(article):
    text = article.get("full_text", "")

    sentiment = analyze_sentiment(text)
    entities = extract_entities(text)

    tickers = entities.get("tickers", [])
    if not tickers:
        return None

    results = []

    for ticker in tickers:
        df = fetch_stock_data(ticker, days_back=60)
        if df is None:
            continue

        df_indicators = calculate_indicators(df)
        technical = get_technical_signal(df_indicators)

        sentiment_score = sentiment["confidence"]
        sentiment_label = sentiment["label"]
        tech_signal = technical["signal"]
        tech_confidence = technical["confidence"]

        if sentiment_label == "positive" and tech_signal == "bullish":
            action = "BUY"
            confidence = (sentiment_score + tech_confidence) / 2
        elif sentiment_label == "negative" and tech_signal == "bearish":
            action = "SELL"
            confidence = (sentiment_score + tech_confidence) / 2
        elif sentiment_label == "positive" and tech_signal == "bearish":
            action = "HOLD"
            confidence = abs(sentiment_score - tech_confidence) / 2
        elif sentiment_label == "negative" and tech_signal == "bullish":
            action = "HOLD"
            confidence = abs(sentiment_score - tech_confidence) / 2
        else:
            action = "HOLD"
            confidence = 0.5

        if confidence < CONFIDENCE_THRESHOLD:
            action = "HOLD"

        latest = df_indicators.iloc[-1]
        atr = latest.get("atr", 0)
        close = latest.get("close", 0)

        stop_loss = round(close - (1.5 * atr), 2) if action == "BUY" else None
        profit_target = round(close + (2.5 * atr), 2) if action == "BUY" else None

        results.append({
            "ticker": ticker,
            "action": action,
            "confidence": round(confidence, 4),
            "sentiment": sentiment_label,
            "sentiment_confidence": sentiment_score,
            "technical_signal": tech_signal,
            "technical_confidence": tech_confidence,
            "close_price": round(float(close), 2),
            "stop_loss": stop_loss,
            "profit_target": profit_target,
            "atr": round(float(atr), 2),
            "article_title": article.get("title", ""),
            "source": article.get("source", ""),
            "published_at": article.get("published_at", ""),
            "technical_details": technical["details"],
        })

    return results


def process_articles(articles):
    all_signals = []
    for article in articles:
        signals = generate_signal(article)
        if signals:
            all_signals.extend(signals)
    return all_signals


if __name__ == "__main__":
    test_articles = [
        {
            "full_text": "Reliance Industries shares rose 3% after strong quarterly results beating analyst estimates",
            "title": "Reliance Q4 results beat estimates",
            "source": "Economic Times",
            "published_at": "2026-06-10T10:00:00Z",
        },
        {
            "full_text": "TCS misses revenue targets amid global slowdown, shares fall sharply",
            "title": "TCS misses Q4 targets",
            "source": "BusinessLine",
            "published_at": "2026-06-10T09:00:00Z",
        },
    ]

    print("Testing signal fusion...\n")
    signals = process_articles(test_articles)

    for signal in signals:
        print(f"Ticker: {signal['ticker']}")
        print(f"Action: {signal['action']} (confidence: {signal['confidence']})")
        print(f"Sentiment: {signal['sentiment']} ({signal['sentiment_confidence']})")
        print(f"Technical: {signal['technical_signal']} ({signal['technical_confidence']})")
        print(f"Close: ₹{signal['close_price']}")
        print(f"Stop Loss: ₹{signal['stop_loss']}")
        print(f"Profit Target: ₹{signal['profit_target']}")
        print()