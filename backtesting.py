import numpy as np
import pandas as pd

def run_back_test(market: pd.DataFrame, sentiment_score: float, threashold: float = 0.2):
    df = market.copy()

    signal = 1.0 if sentiment_score > threshold else signal = 0.0 if sentiment_score < -threshold else signal = 0.0
    df['Strategy'] =  df['Relative Return']*signal
    df['Cumulative Benchmark'] = 
