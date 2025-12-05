import pandas as pd
import numpy as np
import datetime as dt

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except Exception:
    YFINANCE_AVAILABLE = False


def fetch_minute_data_yf(ticker, period_days=7):
    """Fetch minute data via yfinance. Returns DataFrame with OHLCV indexed by Timestamp."""
    if not YFINANCE_AVAILABLE:
        raise RuntimeError("yfinance not installed in environment")
    period_str = f"{period_days}d"
    df = yf.download(ticker, period=period_str, interval='1m', progress=False, threads=False)
    if df is None or df.empty:
        return None
    df.index = df.index.tz_convert(None)
    return df[['Open','High','Low','Close','Volume']]


def generate_synthetic_minute_data(days=7):
    """Generate synthetic minute OHLCV data for testing. Useful when yfinance is unavailable."""
    minutes = days * 24 * 60
    end = dt.datetime.now()
    idx = pd.date_range(end=end, periods=minutes, freq='T')
    price = 3500 + np.cumsum(np.random.randn(minutes).clip(-3,3)) * 0.5
    df = pd.DataFrame(index=idx)
    df['Open'] = price
    df['High'] = df['Open'] + np.abs(np.random.rand(minutes))
    df['Low'] = df['Open'] - np.abs(np.random.rand(minutes))
    df['Close'] = df['Open'] + np.random.randn(minutes) * 0.2
    df['Volume'] = (np.random.rand(minutes) * 1000).astype(int)
    return df
