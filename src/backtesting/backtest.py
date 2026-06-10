import pandas as pd
import numpy as np
from src.ingestion.price_fetcher import fetch_stock_data
from src.signals.technical import calculate_indicators, get_technical_signal
from src.database.db import save_backtest_result

def run_backtest(ticker, days_back=180):
    print(f"Running backtest for {ticker} over {days_back} days...")

    df = fetch_stock_data(ticker, days_back=days_back)
    if df is None or len(df) < 30:
        print(f"Not enough data for {ticker}")
        return None

    df = calculate_indicators(df)
    df = df.dropna()

    trades = []
    position = None

    for i in range(20, len(df)):
        window = df.iloc[:i]
        signal = get_technical_signal(window)

        current_price = df.iloc[i]["close"]
        current_date = str(df.iloc[i]["date"])
        atr = df.iloc[i]["atr"]

        if position is None and signal["signal"] == "bullish" and signal["confidence"] >= 0.65:
            position = {
                "entry_price": current_price,
                "entry_date": current_date,
                "stop_loss": current_price - (1.5 * atr),
                "profit_target": current_price + (2.5 * atr),
                "sessions": 0,
            }

        elif position is not None:
            position["sessions"] += 1

            if current_price >= position["profit_target"]:
                trades.append({
                    "entry": position["entry_price"],
                    "exit": current_price,
                    "entry_date": position["entry_date"],
                    "exit_date": current_date,
                    "result": "win",
                    "return_pct": ((current_price - position["entry_price"]) / position["entry_price"]) * 100,
                })
                position = None

            elif current_price <= position["stop_loss"]:
                trades.append({
                    "entry": position["entry_price"],
                    "exit": current_price,
                    "entry_date": position["entry_date"],
                    "exit_date": current_date,
                    "result": "loss",
                    "return_pct": ((current_price - position["entry_price"]) / position["entry_price"]) * 100,
                })
                position = None

            elif position["sessions"] >= 3:
                result = "win" if current_price > position["entry_price"] else "loss"
                trades.append({
                    "entry": position["entry_price"],
                    "exit": current_price,
                    "entry_date": position["entry_date"],
                    "exit_date": current_date,
                    "result": result,
                    "return_pct": ((current_price - position["entry_price"]) / position["entry_price"]) * 100,
                })
                position = None

    if not trades:
        print(f"No trades generated for {ticker}")
        return None

    trades_df = pd.DataFrame(trades)
    total_trades = len(trades_df)
    wins = len(trades_df[trades_df["result"] == "win"])
    win_rate = wins / total_trades if total_trades > 0 else 0

    returns = trades_df["return_pct"].values
    total_return = returns.sum()

    if len(returns) > 1 and returns.std() > 0:
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)
    else:
        sharpe_ratio = 0

    cumulative = np.cumsum(returns)
    peak = np.maximum.accumulate(cumulative)
    drawdown = cumulative - peak
    max_drawdown = drawdown.min()

    result = {
        "ticker": ticker,
        "start_date": str(df.iloc[0]["date"]),
        "end_date": str(df.iloc[-1]["date"]),
        "total_signals": total_trades,
        "buy_signals": total_trades,
        "sell_signals": 0,
        "hold_signals": 0,
        "win_rate": round(win_rate, 4),
        "total_return": round(total_return, 4),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown": round(max_drawdown, 4),
    }

    save_backtest_result(result)

    print(f"\nBacktest Results for {ticker}:")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate*100:.1f}%")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2f}%")

    return result


if __name__ == "__main__":
    tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    for ticker in tickers:
        run_backtest(ticker, days_back=180)
        print()