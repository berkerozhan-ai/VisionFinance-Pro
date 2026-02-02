import yfinance as yf
import pandas as pd
from datetime import datetime

print("--- YFINANCE DEBUG TEST ---")
tickers = ["NVDA", "THYAO.IS", "AAPL"]
start_date = "2024-01-01"

for t in tickers:
    print(f"\nFetching {t}...")
    try:
        df = yf.download(t, start=start_date, progress=False, auto_adjust=True)
        if df.empty:
            print(f"FAILED: Empty DataFrame for {t}")
        else:
            print(f"SUCCESS: Got {len(df)} rows.")
            print(f"Last Date: {df.index[-1]}")
            print(f"Last Close: {df['Close'].iloc[-1]}")
    except Exception as e:
        print(f"ERROR: {e}")

print("\n---------------------------")
