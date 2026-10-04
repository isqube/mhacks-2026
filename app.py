import streamlit as st
import plotly.graph_objects as go
from data_processing import get_news_headlines, get_market_data
from sentiment_engine import analyze_headline_sentiment
from backtesting import run_backtest
import datetime as dt

st.set_page_config(page_title="AlphaVibe: AI-Assisted Sentiment Backtester", layout="wide")

st.title("AlphaVibe")
st.caption("Quantify news sentiment.")

st.sidebar.header("Configure Strategy")
ticker = st.sidebar.text_input("Asset Ticker (Strategy)", value="GOOG").upper()
benchmark = st.sidebar.text_input("Asset Ticker (Benchmark)", value="GOOG").upper()

custom_rule = st.sidebar.text_area(
    "Custom Rule",
    value="Rebalance to long position when news on AI or earnings are positive, otherwise save face and reduce exposure.",
)

start = st.sidebar.date_input("Start Date", value=dt.date(2023, 6, 15))
end = st.sidebar.date_input("End Date", value=dt.date(2025, 9, 10))

if st.sidebar.button("Run Backtest"):
    with st.spinner("Fetching market data and analysing news sentiment..."):
        try:
            df = get_market_data(ticker, start.isoformat(), end.isoformat())
            benchmark_df = get_market_data(benchmark, start.isoformat(), end.isoformat())
            news = get_news_headlines(ticker)
            sentiment_score, rationale = analyze_headline_sentiment(ticker, news, custom_rule)
            results, metrics = run_backtest(
                df,
                sentiment_score,
                benchmark_returns=benchmark_df["Relative Return"],
            )
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            st.session_state.pop("backtest", None)
            st.error(f"Backtest failed: {exc}")
        else:
            st.session_state["backtest"] = {
                "results": results,
                "metrics": metrics,
                "news": news,
                "sentiment_score": sentiment_score,
                "rationale": rationale,
                "ticker": ticker,
                "benchmark": benchmark,
            }
else:
    if "backtest" not in st.session_state:
        st.info("Click the 'Run Backtest' button.")

backtest = st.session_state.get("backtest")
if backtest:
    results = backtest["results"]
    metrics = backtest["metrics"]
    ticker = backtest["ticker"]
    benchmark = backtest["benchmark"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sentiment Score", backtest["sentiment_score"])
    c2.metric("Strategy Return", metrics["Total Return (Strategy)"])
    c3.metric("Sharpe Ratio", metrics["Sharpe Ratio"])
    c4.metric("Max Drawdown", metrics["Max Drawdown"])

    st.info(f"**Rationale:** {backtest['rationale']}")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=results.index,
        y=results['Cumulative Strategy'],
        mode='lines',
        name=f'AlphaVibe ({ticker})',
        line=dict(color="#00ffaa", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=results.index,
        y=results['Cumulative Benchmark'],
        mode='lines',
        name=f'Buy & Hold Benchmark ({benchmark})',
        line=dict(color="#ff5555", dash='dash'),
    ))

    fig.update_layout(
        title="Cumulative Strategy Returns vs. Benchmark",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_dark",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Parsed News Headlines"):
        st.table(backtest["news"])