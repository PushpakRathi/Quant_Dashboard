import pandas as pd
import numpy as np

from ta.momentum import RSIIndicator

MA_SHORT = 5
MA_LONG = 50
RSI_PERIOD = 14
RSI_LOW = 30
RSI_HIGH = 70


def resample_to_1h(min_df):
    ohlc = {'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}
    hourly = min_df.resample('60T', closed='right', label='right').apply(ohlc).dropna()
    return hourly


def compute_indicators(df_hourly):
    df = df_hourly.copy()
    df['ma5'] = df['Close'].rolling(MA_SHORT).mean()
    df['ma50'] = df['Close'].rolling(MA_LONG).mean()
    rsi = RSIIndicator(close=df['Close'], window=RSI_PERIOD)
    df['rsi'] = rsi.rsi()
    df['ema_fast'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['ema_slow'] = df['Close'].ewm(span=26, adjust=False).mean()
    df['macd'] = df['ema_fast'] - df['ema_slow']
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df


def generate_signals(df):
    df = df.copy()
    df['ma_cross_up'] = (df['ma5'] > df['ma50']) & (df['ma5'].shift(1) <= df['ma50'].shift(1))
    df['ma_cross_down'] = (df['ma5'] < df['ma50']) & (df['ma5'].shift(1) >= df['ma50'].shift(1))
    signals = []
    for ts, row in df.iterrows():
        if row['ma_cross_up']:
            if (row['rsi'] > RSI_LOW) and (row['macd_hist'] > 0):
                signals.append((ts, 'BUY', row['Close']))
        if row['ma_cross_down']:
            if (row['rsi'] < RSI_HIGH) and (row['macd_hist'] < 0):
                signals.append((ts, 'SELL', row['Close']))
    last_signal = signals[-1] if signals else None
    return last_signal, signals

