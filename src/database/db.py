import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Signal, BacktestResult
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/signals.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    print("Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_signal(signal_data):
    db = SessionLocal()
    try:
        technical_details = signal_data.get("technical_details", {})
        signal = Signal(
            ticker=signal_data["ticker"],
            action=signal_data["action"],
            confidence=signal_data["confidence"],
            sentiment=signal_data["sentiment"],
            sentiment_confidence=signal_data["sentiment_confidence"],
            technical_signal=signal_data["technical_signal"],
            technical_confidence=signal_data["technical_confidence"],
            close_price=signal_data["close_price"],
            stop_loss=signal_data.get("stop_loss"),
            profit_target=signal_data.get("profit_target"),
            atr=signal_data.get("atr"),
            rsi=technical_details.get("rsi"),
            macd_diff=technical_details.get("macd_diff"),
            article_title=signal_data.get("article_title", ""),
            source=signal_data.get("source", ""),
            published_at=signal_data.get("published_at", ""),
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        return signal.id
    except Exception as e:
        db.rollback()
        print(f"Error saving signal: {e}")
        return None
    finally:
        db.close()

def get_recent_signals(limit=50):
    db = SessionLocal()
    try:
        signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(limit).all()
        return signals
    finally:
        db.close()

def save_backtest_result(result_data):
    db = SessionLocal()
    try:
        result = BacktestResult(**result_data)
        db.add(result)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving backtest: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully")
    
    test_signal = {
        "ticker": "RELIANCE.NS",
        "action": "BUY",
        "confidence": 0.74,
        "sentiment": "positive",
        "sentiment_confidence": 0.95,
        "technical_signal": "bullish",
        "technical_confidence": 0.53,
        "close_price": 1258.8,
        "stop_loss": 1219.72,
        "profit_target": 1323.93,
        "atr": 26.05,
        "article_title": "Reliance Q4 results beat estimates",
        "source": "Economic Times",
        "published_at": "2026-06-10T10:00:00Z",
        "technical_details": {"rsi": 27.76, "macd_diff": -7.65},
    }

    signal_id = save_signal(test_signal)
    print(f"Saved signal with ID: {signal_id}")

    signals = get_recent_signals(10)
    print(f"Recent signals count: {len(signals)}")
    for s in signals:
        print(f"  {s.ticker} - {s.action} - confidence: {s.confidence}")