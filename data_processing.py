import pandas as pd
import yfinance as yf
import json
import datetime as dt

def get_market_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(ticker, start = start_date, end = end_date)
    for entry in df:
        print(entry)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Adj Close'] if 'Adj Close' in df else df['Close']
        #outputs all the closing and adjusted closing prices

    returns = df.pct_change().dropna()
    return pd.DataFrame({'price' : df, 'returns': returns}) 

start_date = dt.date(2019, 6, 13)
end_date = dt.date(2019, 6, 14)

market_data = get_market_data(ticker='AAPL', start_date=start_date.isoformat(), end_date=end_date.isoformat())

with (pd.option_context('display.max_rows', None, 'display.max_columns', None)):
    print(market_data)