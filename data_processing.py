import pandas as pd
import yfinance as yf
import json
import datetime as dt

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

market_data = get_market_data('GOOG', start_date.isoformat(), end_date.isoformat(), '3mo')

with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
    print(market_data)


def get_news_headlines(ticker: str) -> list[dict]:
    try:
        tick = yf.Ticker(ticker)
        news = tick.news
        if news:
            return [{'title': n['title'],'publisher': n['publisher']} for n in news]
    except Exception:
        print("No news for this ticker. Defaulting to the failsafe news headlines.")
        return [
        {"title": f"{ticker} beats Q3 earnings expectations with record revenue growth", "publisher": "Reuters"},
        {"title": f"Regulatory scrutiny tightens around {ticker} supply chain", "publisher": "Bloomberg"},
        {"title": f"Analysts upgrade {ticker} rating citing strong AI margin expansion", "publisher": "CNBC"}
    ]

print(headline['title'] for headline in get_news_headlines('AAPL'))
