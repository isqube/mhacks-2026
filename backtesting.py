import numpy as np
import pandas as pd

def run_backtest(
    market: pd.DataFrame,
    sentiment_score: float,
    threshold: float = 0.2,
    benchmark_returns: pd.Series | None = None,
) -> tuple[pd.DataFrame, dict[str, str | float]]:
    """Apply a sentiment-based position and calculate performance metrics."""
    required_columns = {'Relative Return'}
    if market.empty or not required_columns.issubset(market.columns):
        raise ValueError("Market data must contain a non-empty 'Relative Return' column.")

    df = market.copy()
    if benchmark_returns is None:
        benchmark_returns = df['Relative Return']
    else:
        benchmark_returns = benchmark_returns.rename('Benchmark Return')
        df = df.join(benchmark_returns, how='inner')
        if df.empty:
            raise ValueError("Strategy and benchmark data have no overlapping dates.")

    if sentiment_score > threshold:
        signal = 1.0
    elif sentiment_score < -threshold:
        signal = 0.0
    else:
        signal = 0.5
    df['Strategy Return'] = df['Relative Return'] * signal
    df['Cumulative Benchmark'] = (1 + df['Benchmark Return']).cumprod() - 1
    df['Cumulative Strategy'] = (1 + df['Strategy Return']).cumprod() - 1

    trading_days = 252

    strategy_std = df['Strategy Return'].std(ddof=0) * np.sqrt(trading_days)
    strategy_mean = df['Strategy Return'].mean() * trading_days
    sharpe_ratio = (strategy_mean/strategy_std) if strategy_std != 0.0 else 0.0

    strategy_value = (1 + df['Strategy Return']).cumprod()
    peak = strategy_value.cummax()
    drawdown = strategy_value / peak - 1
    max_drawdown = drawdown.min()

    metrics = {
        "Total Return (Strategy)": f"{df['Cumulative Strategy'].iloc[-1] * 100:.2f}%",
        "Total Return (Benchmark)": f"{df['Cumulative Benchmark'].iloc[-1] * 100:.2f}%",
        "Sharpe Ratio": float(round(sharpe_ratio, 2)),
        "Max Drawdown": f"{max_drawdown * 100:.2f}%"
    }

    return df, metrics
