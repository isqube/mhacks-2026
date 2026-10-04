import pandas as pd
import yfinance as yf
import logging
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
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
    symbol = ticker.strip().upper()
    if not symbol:
        raise ValueError("Ticker must not be empty.")

    query = urlencode({
        "q": symbol,
        "newsCount": 10,
        "quotesCount": 1,
        "enableFuzzyQuery": "false",
    })
    request = Request(
        f"https://query1.finance.yahoo.com/v1/finance/search?{query}",
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urlopen(request, timeout=15) as response:
            payload = json.load(response)
        news = payload.get("news", []) if isinstance(payload, Mapping) else []
        headlines = [
            headline
            for item in news or []
            if isinstance(item, Mapping)
            for headline in [_parse_news_item(item)]
            if headline is not None
        ]
        if headlines:
            return headlines
        raise RuntimeError(f"No current news headlines were found for {symbol}.")
    except Exception as exc:
        logging.warning("Unable to fetch news headlines for %s: %s", symbol, exc)
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError(f"Unable to fetch news headlines for {symbol}.") from exc

#headlines = get_news_headlines('TSLA')

#for headline in headlines:
#    print(headline["title"])
