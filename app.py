import streamlit as st
from utils.datafetch import fetch_minute_data_yf, generate_synthetic_minute_data
from utils.indicators import resample_to_1h, compute_indicators, generate_signals
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import io

st.set_page_config(page_title="Quant Dashboard", layout="wide")
st.title("Quant Dashboard — MA(5/50) + RSI + MACD")

# Sidebar inputs
ticker = st.sidebar.text_input("Ticker (yfinance format)", value="RELIANCE.NS")
use_live = st.sidebar.checkbox("Use live yfinance data (requires internet)", value=True)
history_days = st.sidebar.slider("History (days)", 3, 30, 7)
refresh_minutes = st.sidebar.number_input("Auto refresh (seconds)", min_value=30, max_value=600, value=60)

st.sidebar.markdown("---")
st.sidebar.write("Data source: yfinance (fallback to synthetic if unavailable)")

# Fetch data
with st.spinner("Fetching minute-level data..."):
    if use_live:
        try:
            minute_df = fetch_minute_data_yf(ticker, period_days=history_days)
            if minute_df is None or minute_df.empty:
                st.warning("yfinance returned no data. Using synthetic data instead.")
                minute_df = generate_synthetic_minute_data(days=history_days)
        except Exception as e:
            st.error(f"Error fetching live data: {e}\nUsing synthetic data.")
            minute_df = generate_synthetic_minute_data(days=history_days)
    else:
        minute_df = generate_synthetic_minute_data(days=history_days)

# Resample and compute indicators
hourly = resample_to_1h(minute_df)
ind = compute_indicators(hourly)
last_signal, all_signals = generate_signals(ind)

# Display key info
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader(f"{ticker} — 1H Chart")
    buf = io.BytesIO()
    # mplfinance plot
    mpf.plot(ind[['Open', 'High', 'Low', 'Close']], type='candle', mav=(5,50), volume=False, style='yahoo', savefig=dict(fname=buf, dpi=100, bbox_inches='tight'))
    buf.seek(0)
    img = buf.read()
    st.image(img, use_column_width=True)
    st.markdown("**Latest indicators (last 3 rows)**")
    st.dataframe(ind.tail(3))

with col2:
    st.subheader("Latest Signal")
    if last_signal:
        ts, sig, price = last_signal
        st.markdown(f"### {sig} @ {price:.2f}")
        st.write(f"Signal time: {ts}")
    else:
        st.write("No BUY/SELL signal detected in the recent bars.")
    st.markdown("---")
    st.write("All Signals (last 10):")
    if all_signals:
        df_s = pd.DataFrame(all_signals, columns=['Datetime', 'Signal', 'Price']).sort_values('Datetime', ascending=False).head(10)
        st.table(df_s)
    else:
        st.write("No signals yet.")

st.markdown("---")

st.subheader("Indicator Plots")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,6), sharex=True)
ax1.plot(ind.index, ind['Close'], label='Close')
ax1.plot(ind.index, ind['ma5'], label='MA5')
ax1.plot(ind.index, ind['ma50'], label='MA50')
ax1.legend()
ax1.set_title('Price with MAs')

ax2.plot(ind.index, ind['rsi'], label='RSI', color='purple')
ax2.axhline(30, color='green', linestyle='--')
ax2.axhline(70, color='red', linestyle='--')
ax2.set_title('RSI')

st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.write("Deployment: Streamlit Cloud recommended")

# Auto-refresh info
st.info(f"This page pulls data on demand. To auto-refresh, reload or set up Streamlit Cloud scheduled jobs.")
