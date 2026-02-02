import yfinance as yf
import pandas as pd
import os

# Inspecting raw fetch for Gold
ticker = "GC=F"
print(f"--- Debugging {ticker} ---")

try:
    print("Attempt 1: Standard Download (start='2024-01-01', auto_adjust=True)")
    df = yf.download(ticker, start="2024-01-01", progress=False, auto_adjust=True)
    print(f"Shape: {df.shape}")
    print(df.head())
    print("Columns:", df.columns)
    
    if df.empty:
        print("\nAttempt 2: Period='1y', auto_adjust=True")
        df = yf.download(ticker, period="1y", progress=False, auto_adjust=True)
        print(f"Shape: {df.shape}")
    
    if not df.empty:
        # Check for MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            print("\nIs MultiIndex: YES")
            print("Levels:", df.columns.nlevels)
            print("Level 1 Values:", df.columns.get_level_values(1))
            
            # Simulate cleaning logic in market_data.py
            print("\nSimulating market_data.py cleaning...")
            if df.columns.nlevels > 1:
                 df = df.droplevel(1, axis=1)
            print("Columns after droplevel:", df.columns)
            
            # Check for NaN handling
            print("\nChecking NaNs before dropna:")
            print(df.isna().sum())
            df_dropped = df.dropna()
            print(f"Shape after dropna: {df_dropped.shape}")
            
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
