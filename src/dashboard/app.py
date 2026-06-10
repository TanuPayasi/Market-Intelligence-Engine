import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Market Intelligence Engine",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Market Intelligence Engine")
st.caption("AI-powered trading signals from financial news")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Generate New Signals", type="primary"):
        with st.spinner("Fetching news and generating signals..."):
            try:
                response = requests.post(f"{API_URL}/generate")
                data = response.json()
                st.success(f"Generated {data['signals_generated']} signals from {data['articles_processed']} articles")
            except Exception as e:
                st.error(f"Error: {e}")

try:
    response = requests.get(f"{API_URL}/signals?limit=50")
    signals_data = response.json()
    signals = signals_data.get("signals", [])
except Exception as e:
    st.error(f"Cannot connect to API. Make sure the API server is running on port 8000")
    st.stop()

if not signals:
    st.info("No signals yet. Click 'Generate New Signals' to start.")
    st.stop()

df = pd.DataFrame(signals)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Signals", len(df))
with col2:
    buy_count = len(df[df["action"] == "BUY"])
    st.metric("BUY Signals", buy_count)
with col3:
    sell_count = len(df[df["action"] == "SELL"])
    st.metric("SELL Signals", sell_count)
with col4:
    avg_confidence = df["confidence"].mean()
    st.metric("Avg Confidence", f"{avg_confidence:.1%}")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Signal Distribution")
    action_counts = df["action"].value_counts()
    fig = px.pie(
        values=action_counts.values,
        names=action_counts.index,
        color=action_counts.index,
        color_discrete_map={"BUY": "#00cc44", "SELL": "#ff4444", "HOLD": "#ffaa00"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Confidence by Ticker")
    fig = px.bar(
        df,
        x="ticker",
        y="confidence",
        color="action",
        color_discrete_map={"BUY": "#00cc44", "SELL": "#ff4444", "HOLD": "#ffaa00"},
    )
    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Latest Signals")

for _, signal in df.iterrows():
    action = signal["action"]
    color = "🟢" if action == "BUY" else "🔴" if action == "SELL" else "🟡"

    with st.expander(f"{color} {signal['ticker']} — {action} (confidence: {signal['confidence']:.1%})"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Action", action)
            st.metric("Confidence", f"{signal['confidence']:.1%}")
            st.metric("Sentiment", signal["sentiment"].upper())

        with col2:
            st.metric("Close Price", f"₹{signal['close_price']}")
            if signal["stop_loss"]:
                st.metric("Stop Loss", f"₹{signal['stop_loss']}")
            if signal["profit_target"]:
                st.metric("Profit Target", f"₹{signal['profit_target']}")

        with col3:
            st.metric("Technical Signal", signal["technical_signal"].upper())
            if signal["rsi"]:
                st.metric("RSI", f"{signal['rsi']:.1f}")

        st.caption(f"📰 {signal['article_title']}")
        st.caption(f"Source: {signal['source']} | Published: {signal['published_at']}")

st.divider()
st.subheader("Backtesting")

ticker_input = st.text_input("Enter ticker for backtest (e.g. RELIANCE.NS)", value="RELIANCE.NS")
days_input = st.slider("Days of history", min_value=30, max_value=365, value=180)

if st.button("Run Backtest"):
    with st.spinner(f"Running backtest for {ticker_input}..."):
        try:
            response = requests.post(f"{API_URL}/backtest/{ticker_input}?days={days_input}")
            result = response.json()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Trades", result["total_signals"])
            with col2:
                st.metric("Win Rate", f"{result['win_rate']:.1%}")
            with col3:
                st.metric("Total Return", f"{result['total_return']:.2f}%")
            with col4:
                st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")

            st.metric("Max Drawdown", f"{result['max_drawdown']:.2f}%")
        except Exception as e:
            st.error(f"Backtest failed: {e}")