import pandas as pd
import yfinance as yf
import json

def get_market_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(ticker, start = start_date, end = end_date)
    for entry in df:
        print(entry)
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Adj Close'] if 'Adj Close' in df else df['Close']
        #outputs all the closing and adjusted closing prices

    returns = df.pct_change().dropna()
    return pd.DataFrame({'price' : df, 'returns': returns}) #makes dataframe with two

df1 = yf.download(['GOOG', 'NVDA', 'MSFT'],period='2mo')
for entry in df1:
    print(entry)