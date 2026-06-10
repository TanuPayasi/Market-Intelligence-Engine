from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.database.db import get_db, save_signal, get_recent_signals, init_db
from src.database.models import Signal
from src.signals.fusion import process_articles
from src.ingestion.news_fetcher import fetch_market_news
from src.backtesting.backtest import run_backtest

app = FastAPI(
    title="Market Intelligence Engine API",
    description="AI-powered trading signals from financial news",
    version="1.0.0",
)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"message": "Market Intelligence Engine API is running"}

@app.get("/signals")
def get_signals(limit: int = 50, db: Session = Depends(get_db)):
    signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(limit).all()
    return {
        "count": len(signals),
        "signals": [
            {
                "id": s.id,
                "ticker": s.ticker,
                "action": s.action,
                "confidence": s.confidence,
                "sentiment": s.sentiment,
                "technical_signal": s.technical_signal,
                "close_price": s.close_price,
                "stop_loss": s.stop_loss,
                "profit_target": s.profit_target,
                "rsi": s.rsi,
                "article_title": s.article_title,
                "source": s.source,
                "published_at": s.published_at,
                "created_at": str(s.created_at),
            }
            for s in signals
        ],
    }

@app.get("/signals/{ticker}")
def get_signals_by_ticker(ticker: str, db: Session = Depends(get_db)):
    signals = (
        db.query(Signal)
        .filter(Signal.ticker == ticker.upper())
        .order_by(Signal.created_at.desc())
        .limit(20)
        .all()
    )
    if not signals:
        raise HTTPException(status_code=404, detail=f"No signals found for {ticker}")
    return {"ticker": ticker, "count": len(signals), "signals": signals}

@app.post("/generate")
def generate_signals():
    try:
        articles = fetch_market_news(max_articles=10)
        signals = process_articles(articles)

        saved_count = 0
        for signal in signals:
            signal_id = save_signal(signal)
            if signal_id:
                saved_count += 1

        return {
            "message": "Signals generated successfully",
            "articles_processed": len(articles),
            "signals_generated": len(signals),
            "signals_saved": saved_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/backtest/{ticker}")
def backtest_ticker(ticker: str, days: int = 180):
    result = run_backtest(ticker, days_back=days)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Could not run backtest for {ticker}")
    return result

@app.get("/health")
def health():
    return {"status": "healthy"}