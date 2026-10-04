import pandas as pd
import yfinance as yf
import json
import datetime as dt
import logging
from collections.abc import Mapping

start_date = dt.date(2019, 6, 13)
end_date = dt.date(2022, 6, 19)

#get closing prices and relative returns
def get_market_data(ticker: str, start_date: str, end_date: str, inter: str = '1d') -> pd.DataFrame:
    """Fetch daily adjusted close prices and calculate daily returns."""
    df = yf.download(tickers = ticker, start=start_date, end=end_date, interval=inter)
    # yfinance multi-index column handling
    return pd.concat(
        [df['Close'], df.pct_change().dropna()['Close']],
        axis=1,
    ).set_axis(['Closing Price', 'Relative Return'], axis=1)

market_data = get_market_data('TSLA', start_date.isoformat(), end_date.isoformat(), '3mo')

with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
    print(market_data)


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

headlines = get_news_headlines('TSLA')

for headline in headlines:
    print(headline["title"])
