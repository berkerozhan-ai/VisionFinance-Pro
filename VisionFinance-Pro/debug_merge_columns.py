
import pandas as pd
import sys
import os
import yfinance as yf

# Ensure path to imports
sys.path.append(os.getcwd())

try:
    import quant_core.data.market_data as md
    print("Module imported.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

ticker = "BTC-USD"

# 1. Simulate Historical Data (Flat columns)
print("--- Generating Mock Historical Data ---")
cols = ['Open', 'High', 'Low', 'Close', 'Volume']
dates = pd.date_range(end=pd.Timestamp.now(), periods=5)
data = [[100, 110, 90, 105, 1000] for _ in range(5)]
hist_df = pd.DataFrame(data, columns=cols, index=dates)
print("Historical Columns:", hist_df.columns.tolist())

# 2. Fetch Live Candle
print("\n--- Fetching Live Data ---")
live_day_df = md.get_latest_daily_candle(ticker)

if live_day_df is not None:
    print("Live DF Columns (Raw):", live_day_df.columns.tolist())
    
    # Check if MultiIndex
    if isinstance(live_day_df.columns, pd.MultiIndex):
        print("ALERT: Live DF has MultiIndex columns!")
    
    # 3. Simulate Merge
    print("\n--- Simulating Merge ---")
    try:
        # Mimic dashboard logic
        if hist_df.index.tz is not None:
             hist_df.index = hist_df.index.tz_localize(None)
        if live_day_df.index.tz is not None:
             live_day_df.index = live_day_df.index.tz_localize(None)

        combined_df = pd.concat([hist_df, live_day_df])
        print("Combined DF Columns:", combined_df.columns.tolist())
        
        # Check for tuples
        has_tuple = any(isinstance(c, tuple) for c in combined_df.columns)
        print(f"Has Tuple in Columns? {has_tuple}")
        
    except Exception as e:
        print(f"Merge Error: {e}")

else:
    print("Could not fetch live data.")
