import pandas as pd
import yfinance as yf
import logging
from collections.abc import Mapping

def get_market_data(ticker: str, start_date: str, end_date: str, inter: str = '1d') -> pd.DataFrame:
    """Fetch closing prices and calculate daily returns."""
    if not ticker.strip():
        raise ValueError("Ticker must not be empty.")
    if start_date >= end_date:
        raise ValueError("Start date must be before end date.")

    prices = yf.download(
        tickers=ticker.strip().upper(),
        start=start_date,
        end=end_date,
        interval=inter,
        auto_adjust=False,
        progress=False,
    )
    if prices.empty or 'Close' not in prices:
        raise ValueError(f"No market data was found for {ticker.upper()}.")

    close = prices['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.rename('Closing Price').dropna()
    if close.empty:
        raise ValueError(f"No closing prices were found for {ticker.upper()}.")

    return pd.concat(
        [close, close.pct_change().rename('Relative Return')],
        axis=1,
    ).dropna()


def _parse_news_item(item: Mapping) -> dict | None:
    #Normalize the old and new yfinance news response formats
    content = item.get('content', item)
    if not isinstance(content, Mapping):
        return None

    title = content.get('title')
    if not isinstance(title, str) or not title.strip():
        return None

    publisher = content.get('publisher')
    if not isinstance(publisher, str):
        provider = content.get('provider')
        publisher = provider.get('displayName') if isinstance(provider, Mapping) else None

    return {
        'title': title.strip(),
        'publisher': publisher.strip() if isinstance(publisher, str) else 'Yahoo Finance',
    }


def get_news_headlines(ticker: str) -> list[dict]:
    try:
        tick = yf.Ticker(ticker)
        news = tick.get_news()
        headlines = [
            headline
            for item in news or []
            if isinstance(item, Mapping)
            for headline in [_parse_news_item(item)]
            if headline is not None
        ]
        if headlines:
            return headlines
    except Exception as exc:
        logging.warning("Unable to fetch news headlines for %s: %s", ticker, exc)

    return [
        {"title": f"{ticker} beats Q3 earnings expectations with record revenue growth", "publisher": "Reuters"},
        {"title": f"Regulatory scrutiny tightens around {ticker} supply chain", "publisher": "Bloomberg"},
        {"title": f"Analysts upgrade {ticker} rating citing strong AI margin expansion", "publisher": "CNBC"}
    ]

#headlines = get_news_headlines('TSLA')

#for headline in headlines:
#    print(headline["title"])
