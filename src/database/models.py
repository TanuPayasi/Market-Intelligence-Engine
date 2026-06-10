from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)
    confidence = Column(Float, nullable=False)
    sentiment = Column(String(20))
    sentiment_confidence = Column(Float)
    technical_signal = Column(String(20))
    technical_confidence = Column(Float)
    close_price = Column(Float)
    stop_loss = Column(Float)
    profit_target = Column(Float)
    atr = Column(Float)
    rsi = Column(Float)
    macd_diff = Column(Float)
    article_title = Column(Text)
    source = Column(String(100))
    published_at = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20))
    start_date = Column(String(20))
    end_date = Column(String(20))
    total_signals = Column(Integer)
    buy_signals = Column(Integer)
    sell_signals = Column(Integer)
    hold_signals = Column(Integer)
    win_rate = Column(Float)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)