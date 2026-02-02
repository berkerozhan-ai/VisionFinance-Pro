
import pandas as pd
import sys
import os
import yfinance as yf
from datetime import timedelta

# Ensure path is correct
sys.path.append(os.getcwd())

try:
    from quant_core.data import market_data as md
    print("Module imported.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

ticker = "BTC-USD"
path = os.path.join(md.DATA_DIR, f"{ticker}.parquet")

# 1. Create Stale File (5 days ago)
print("Creating stale parquet file...")
end_date = pd.Timestamp.now() - timedelta(days=5)
# Ensure end_date is normalized for clean comparison
end_date = end_date.normalize()

stale_df = yf.download(ticker, end=end_date, period="1mo", progress=False, auto_adjust=True)
if stale_df.empty:
    print("Failed to download initial stale data.")
    sys.exit(1)

# Ensure no MultiIndex for the mock file to be clean
if isinstance(stale_df.columns, pd.MultiIndex):
    stale_df.columns = stale_df.columns.droplevel(1)
    
stale_df.to_parquet(path)
print(f"Saved stale file with last date: {stale_df.index[-1]}")

# 2. Trigger Smart Load
print("\n--- TRIGGERING SMART SYNC ---")
try:
    updated_df = md.smart_load_ticker(ticker)
    
    if updated_df is not None:
        new_last_date = updated_df.index[-1]
        print(f"Updated Last Date: {new_last_date}")
        
        if new_last_date > stale_df.index[-1]:
            print("SUCCESS: Data was auto-healed and updated!")
        else:
            print("FAIL: Date did not advance.")
    else:
        print("FAIL: Returned None.")
        
except Exception as e:
    print(f"Smart Sync Failed: {e}")
