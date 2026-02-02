
import sys
import os
import pandas as pd

# Ensure path is correct
sys.path.append(os.getcwd())

try:
    from quant_core.data import market_data as md
    print("Module imported.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

ticker = "BTC-USD" # Crypto is always live
print(f"Fetching live quote for {ticker}...")

try:
    price, vol, df = md.get_realtime_quote(ticker)
    
    if price:
        print(f"SUCCESS: Price=${price}, Vol={vol}")
        print("Tail of DF:")
        print(df.tail(1))
    else:
        print("FAILURE: No data returned (price is None).")
        
except Exception as e:
    print(f"CRASH: {e}")
