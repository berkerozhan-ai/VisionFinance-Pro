import sys
import os
import pandas as pd
import yfinance as yf

# Mock environment
sys.path.append(os.getcwd())
import quant_core.data.market_data as md

ticker = "GC=F"
print(f"--- Debugging {ticker} History ---")

# 1. Check File on Disk
path = os.path.join(md.DATA_DIR, f"{ticker}.parquet")
if os.path.exists(path):
    print(f"File exists: {path}")
    try:
        df_disk = pd.read_parquet(path)
        print(f"Rows on disk: {len(df_disk)}")
        print("Tail on disk:")
        print(df_disk.tail(3))
        print("Columns on disk:", df_disk.columns)
    except Exception as e:
        print(f"Error reading disk file: {e}")
else:
    print("File DOES NOT EXIST on disk.")

# 2. Simulate smart_load_ticker (Strict=True)
print("\n--- Simulating smart_load_ticker(strict=True) ---")
df_smart = md.smart_load_ticker(ticker, strict=True)
if df_smart is not None:
    print(f"Smart Load Rows: {len(df_smart)}")
    print("Smart Load Tail:")
    print(df_smart.tail(3))
else:
    print("Smart Load returned None!")

# 3. Simulate Live Merge (Dashboard Logic)
print("\n--- Simulating Dashboard Merge ---")
if df_smart is not None and not df_smart.empty:
    df = df_smart.copy()
    
    # CRITICAL FIX REPLICATION
    if isinstance(df.columns, pd.MultiIndex):
        print("Is MultiIndex: YES -> Flattening")
        df.columns = df.columns.droplevel(1)
    else:
        print("Is MultiIndex: NO")
        
    print(f"Columns before merge: {df.columns}")
    
    # Synthetic Candle
    live_date = pd.Timestamp.now().normalize()
    # Mock candle
    synthetic_candle = pd.DataFrame([{
        'Open': 2000, 'High': 2010, 'Low': 1990, 'Close': 2005, 'Volume': 1000
    }], index=[live_date])
    
    print("Merging...")
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    combined = pd.concat([df, synthetic_candle])
    combined = combined[~combined.index.duplicated(keep='last')]
    
    print(f"Final Merged Rows: {len(combined)}")
    print("Final Tail:")
    print(combined.tail(3))
