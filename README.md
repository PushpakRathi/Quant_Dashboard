# Quant Dashboard (Streamlit)

This repository contains a Streamlit-based quant dashboard that calculates MA(5/50), RSI and MACD on 1-hour bars derived from minute-level data. It supports live fetch via `yfinance` or falls back to synthetic data.

## Run locally

1. Create virtualenv and install requirements:

'''bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
