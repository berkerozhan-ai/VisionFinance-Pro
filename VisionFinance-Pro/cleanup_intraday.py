import os
import pandas as pd
import glob

DATA_DIR = "quant_core/data/raw"

print("--- AUDITING FOR INTRADAY CORRUPTION ---")
files = glob.glob(os.path.join(DATA_DIR, "*.parquet"))
count = 0

for f in files:
    try:
        df = pd.read_parquet(f)
        if len(df) < 2: continue
        
        # Check time difference between last two rows
        diff = df.index[-1] - df.index[-2]
        
        # If difference is around 1 minute, it's corrupt (should be >= 1 Day)
        if diff.total_seconds() < 3600: # Less than 1 hour diff implies Intraday
            print(f"CORRUPT FOUND: {f} (Diff: {diff})")
            os.remove(f)
            print(f" -> DELETED {f}")
            count += 1
            
    except Exception as e:
        print(f"Error checking {f}: {e}")

print(f"--- COMPLETE. Deleted {count} files. ---")
