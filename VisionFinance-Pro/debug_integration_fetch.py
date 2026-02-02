import sys
import os
sys.path.append(os.getcwd())

import quant_core.data.market_data as md

print(f"DATA_DIR: {md.DATA_DIR}")

ticker = "GC=F"
print(f"Fetching {ticker}...")
ok, msg = md.fetch_single_ticker(ticker)
print(f"Result: {ok}, {msg}")

path = os.path.join(md.DATA_DIR, f"{ticker}.parquet")
if os.path.exists(path):
    print(f"File exists at {path}")
else:
    print(f"File MISSING at {path}")
