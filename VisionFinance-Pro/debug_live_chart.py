
import pandas as pd
import sys
import os
import yfinance as yf

# Ensure path is correct
sys.path.append(os.getcwd())

try:
    from quant_core.data import market_data as md
    print("Module imported.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

ticker = "BTC-USD"

# 1. Simulate Historical Data (yesterday)
print("Generating mock historical data...")
hist_df = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)
hist_df = hist_df.iloc[:-1] # Remove today so we can simulate "old file"
print(f"Historical Last Date: {hist_df.index[-1]}")

# 2. Fetch Live Daily Candle (today)
print("Fetching live daily candle...")
live_day_df = md.get_latest_daily_candle(ticker)

if live_day_df is not None:
    print(f"Live Day Date: {live_day_df.index[-1]}")
    
    # 3. Test Merge Logic
    try:
       if hist_df.index.tz is not None:
           hist_df.index = hist_df.index.tz_localize(None)
       if live_day_df.index.tz is not None:
           live_day_df.index = live_day_df.index.tz_localize(None)
           
       combined_df = pd.concat([hist_df, live_day_df])
       # Dedup logic
       final_df = combined_df[~combined_df.index.duplicated(keep='last')]
       final_df = final_df.sort_index()
       
       print("\n--- FINAL DATAFRAME TAIL ---")
       print(final_df.tail(3))
       
       if final_df.index[-1] == live_day_df.index[-1]:
           print("\nSUCCESS: Chart is effectively updated to Today!")
       else:
           print("\nFAIL: Merge did not append today's date.")
           
    except Exception as e:
        print(f"Merge Failed: {e}")
else:
    print("FAIL: Could not fetch live candle.")
