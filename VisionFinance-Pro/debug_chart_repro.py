import pandas as pd
import yfinance as yf
import os
import sys

# Mocking dashboard logic
ticker = "NVDA"
print(f"--- Debugging Chart Data for {ticker} ---")

# 1. Load History (Mocking smart_load_ticker)
# We'll just fetch fresh to be sure what YF gives us vs what we do
print("Fetching 1y history...")
df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
print(f"History Shape: {df.shape}")
print("History Tail:")
print(df.tail(3))
print("History Index Type:", df.index.dtype)

# 2. Simulate Live Data Fetch
print("\nFetching Live 1m data...")
intraday_df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)

if not intraday_df.empty:
    print(f"Intraday Shape: {intraday_df.shape}")
    
    # Logic from dashboard.py
    if isinstance(intraday_df.columns, pd.MultiIndex):
        intraday_df.columns = intraday_df.columns.droplevel(1)
        
    live_date = intraday_df.index[-1].normalize()
    print(f"Live Date (Normalized): {live_date}")
    
    synthetic_candle = pd.DataFrame([{
        'Open': intraday_df['Open'].iloc[0],
        'High': intraday_df['High'].max(),
        'Low': intraday_df['Low'].min(),
        'Close': intraday_df['Close'].iloc[-1],
        'Volume': intraday_df['Volume'].sum()
    }], index=[live_date])
    
    print("\nSynthetic Candle:")
    print(synthetic_candle)
    
    # Merge Logic
    if df.index.tz is not None: df.index = df.index.tz_localize(None)
    if synthetic_candle.index.tz is not None: synthetic_candle.index = synthetic_candle.index.tz_localize(None)
    
    print("\nSimulating FIX: Flattening History Columns...")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    print("History Columns:", df.columns)

    print("\nMerging...")
    combined_df = pd.concat([df, synthetic_candle])
    
    # Check for duplicates BEFORE dedupe
    print("Duplicates mask:", combined_df.index.duplicated(keep='last'))
    
    df_merged = combined_df[~combined_df.index.duplicated(keep='last')]
    df_merged = df_merged.sort_index()
    
    print("\nMerged Tail (Final Chart Data):")
    print(df_merged.tail(5))
    
    # CHECK FOR ANOMALIES
    last_close = df_merged['Close'].iloc[-1]
    prev_close = df_merged['Close'].iloc[-2]
    
    print(f"\nLast Close: {last_close}, Prev Close: {prev_close}")
    if abs(last_close - prev_close) > prev_close * 0.5:
        print("!!! ANOMALY DETECTED: Huge price jump !!!")
        
    # Check Columns Structure
    print("\nFinal Columns:", df_merged.columns)
    if isinstance(df_merged.columns, pd.MultiIndex):
        print("!!! WARNING: MultiIndex Columns Remaining !!!")
else:
    print("No intraday data found.")
