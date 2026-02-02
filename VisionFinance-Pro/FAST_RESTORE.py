import yfinance as yf
import pandas as pd
import os
import time

# Critical Tickers to make the app usable immediately
CRITICAL_TICKERS = [
    "NVDA", "AAPL", "MSFT", "TSLA", # US Tech
    "THYAO.IS", "KCHOL.IS", "GARAN.IS", # TR
    "BTC-USD", "ETH-USD", # Crypto
    "SPY", "QQQ" # ETFs
]

DATA_DIR = os.path.join("quant_core", "data", "raw")
START_DATE = "2024-01-01"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print("--- EMERGENCY DATA RESTORE ---")

for ticker in CRITICAL_TICKERS:
    try:
        print(f"Restoring {ticker}...", end=" ")
        df = yf.download(ticker, start=START_DATE, progress=False, auto_adjust=True)
        
        if not df.empty:
            df = df.dropna()
            if isinstance(df.columns, pd.MultiIndex):
                if df.columns.nlevels > 1:
                    df = df.droplevel(1, axis=1)
            
            # Ensure index is datetime
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)

            path = os.path.join(DATA_DIR, f"{ticker}.parquet")
            df.to_parquet(path)
            print("OK")
        else:
            print("FAILED (Empty)")
            
    except Exception as e:
        print(f"ERROR: {e}")

print("\nCore assets restored. You can open the app now.")
