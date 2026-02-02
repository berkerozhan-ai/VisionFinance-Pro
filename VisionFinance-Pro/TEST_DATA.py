import yfinance as yf
import pandas as pd
import shutil
import os

# 1. Setup
TICKER = "NVDA"
START = "2025-12-01" # Very recent
DATA_DIR = os.path.join("quant_core", "data", "raw")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

print(f"--- FETCHING {TICKER} ---")

# 2. Fetch
try:
    df = yf.download(TICKER, start=START, progress=False, auto_adjust=True)
    
    # 3. Inspect
    if df.empty:
        print("!!! EMPTY DATAFRAME !!!")
    else:
        print(f"Rows: {len(df)}")
        print("Last 5 Rows:")
        print(df.tail(5))
        
        # Check Date
        last_date = df.index[-1]
        print(f"\nLAST DATE FOUND: {last_date}")
        
        # 4. Save
        path = os.path.join(DATA_DIR, f"{TICKER}.parquet")
        df.to_parquet(path)
        print(f"Saved to {path}")

except Exception as e:
    print(f"CRASH: {e}")
