import time
import threading
from src.database.db import init_db
from src.ingestion.news_fetcher import fetch_market_news
from src.signals.fusion import process_articles
from src.database.db import save_signal

def run_pipeline():
    print("Running market intelligence pipeline...")
    try:
        articles = fetch_market_news(max_articles=20)
        print(f"Fetched {len(articles)} articles")

        signals = process_articles(articles)
        print(f"Generated {len(signals)} signals")

        saved = 0
        for signal in signals:
            signal_id = save_signal(signal)
            if signal_id:
                saved += 1

        print(f"Saved {saved} signals to database")
        return signals

    except Exception as e:
        print(f"Pipeline error: {e}")
        return []

def run_continuous(interval_minutes=15):
    print(f"Starting continuous pipeline — running every {interval_minutes} minutes")
    while True:
        run_pipeline()
        print(f"Sleeping for {interval_minutes} minutes...")
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import sys

    init_db()

    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        run_continuous(interval_minutes=15)
    else:
        signals = run_pipeline()
        print("\nGenerated Signals:")
        for signal in signals:
            print(f"  {signal['ticker']} — {signal['action']} (confidence: {signal['confidence']})")