
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
hist_df = hist_df.iloc[:-1] # Remove today
if hist_df.index.tz is not None: hist_df.index = hist_df.index.tz_localize(None)
print(f"Historical Last Date: {hist_df.index[-1]}")

# 2. Fetch Intraday Data
print("Fetching intraday 1m data...")
rt_price, rt_vol, intraday_df = md.get_realtime_quote(ticker)

if intraday_df is not None and not intraday_df.empty:
    print(f"Intraday Last Timestamp: {intraday_df.index[-1]}")
    
    # Flatten if needed
    if isinstance(intraday_df.columns, pd.MultiIndex):
        intraday_df.columns = intraday_df.columns.droplevel(1)

    # 3. HTML Synthesis Logic
    live_date = intraday_df.index[-1].normalize()
    if live_date.tz is not None: live_date = live_date.tz_localize(None)
    
    synthetic_candle = pd.DataFrame([{
        'Open': intraday_df['Open'].iloc[0],
        'High': intraday_df['High'].max(),
        'Low': intraday_df['Low'].min(),
        'Close': intraday_df['Close'].iloc[-1],
        'Volume': intraday_df['Volume'].sum()
    }], index=[live_date])
    
    print("\n--- SYNTHETIC CANDLE ---")
    print(synthetic_candle)
    
    # 4. Merge
    combined_df = pd.concat([hist_df, synthetic_candle])
    final_df = combined_df[~combined_df.index.duplicated(keep='last')]
    final_df = final_df.sort_index()
    
    print("\n--- FINAL DF TAIL ---")
    print(final_df.tail(3))
    
    if final_df.index[-1].normalize() == pd.Timestamp.now().normalize():
        print("\nSUCCESS: Final DF has Today's date.")
    else:
        # Note: In simulation/testing env, 'now' might be different, but we check if it matches synthetic
        if final_df.index[-1] == live_date:
             print(f"\nSUCCESS: Final DF matched synthetic date {live_date}")
        else:
             print(f"\nFAIL: Final DF date {final_df.index[-1]} != synthetic {live_date}")

else:
    print("FAIL: No intraday data fetched.")
