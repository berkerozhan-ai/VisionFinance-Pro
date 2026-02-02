import pandas as pd
import os
import glob
import sys
from datetime import timedelta

# Mock path setup
sys.path.append(os.getcwd())
import quant_core.data.market_data as md

DATA_DIR = md.DATA_DIR
print(f"Auditing Data Directory: {DATA_DIR}")

files = glob.glob(os.path.join(DATA_DIR, "*.parquet"))
print(f"Found {len(files)} files.")

corrupt_files = []
suspicious_files = []

for f in files:
    fname = os.path.basename(f)
    try:
        df = pd.read_parquet(f)
        
        # Check 1: Empty
        if df.empty:
            print(f"[EMPTY] {fname}")
            corrupt_files.append(f)
            continue
            
        # Check 2: Row Count (Too short for analysis)
        if len(df) < 50:
            print(f"[SHORT] {fname}: Only {len(df)} rows")
            suspicious_files.append(f)
            
        # Check 3: Frequency / Time Span
        # If we have 200 rows but they span only 1 day, it's intraday trash data
        start_date = df.index[0]
        end_date = df.index[-1]
        
        if start_date.tz is not None: start_date = start_date.tz_localize(None)
        if end_date.tz is not None: end_date = end_date.tz_localize(None)
        
        days_span = (end_date - start_date).days
        rows = len(df)
        
        # Logic: If rows > 20 but days_span < 5 => It's likely minutes data
        if rows > 20 and days_span < 5:
            print(f"[INTRADAY DETECTED] {fname}: {rows} rows span {days_span} days")
            corrupt_files.append(f)
            continue
            
        # Check 4: Stale Data (Older than 10 days)
        now = pd.Timestamp.now()
        days_since_update = (now - end_date).days
        if days_since_update > 10:
             print(f"[STALE] {fname}: Last data from {end_date.date()} ({days_since_update} days ago)")
             # Stale is not 'corrupt' per se, smart_load handles it, but good to know
        
    except Exception as e:
        print(f"[ERROR] {fname}: {e}")
        corrupt_files.append(f)

print("-" * 30)
print(f"Audit Complete.")
print(f"Corrupt Files (To Delete): {len(corrupt_files)}")
print(f"Suspicious Files (Manual Check): {len(suspicious_files)}")

if corrupt_files:
    print("Deleting corrupt files...")
    for cf in corrupt_files:
        try:
            os.remove(cf)
            print(f"Deleted: {os.path.basename(cf)}")
        except Exception as e:
            print(f"Failed to delete {cf}: {e}")
else:
    print("No corrupt files found!")
