import pandas as pd
import numpy as np

# Define Standard Regimes
class MarketRegime:
    TRENDING = "TRENDING"   # Safe to use Moving Averages
    RANGING = "RANGING"     # Safe to use RSI / Mean Reversion
    VOLATILE = "VOLATILE"   # DANGER ZONE - Reduce Risk!

def detect_regime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes technical features to classify the market state.
    
    Logic:
    1. First, check DANGER (Volatility). If Volatility is in the top 20% of history, 
       we are in VOLATILE regime regardless of trend.
    2. Then, check TREND strength (ADX). If ADX > 20, we are TRENDING.
    3. Otherwise, we are RANGING (Choppy).
    
    Args:
        df: DataFrame with 'volatility_21' and 'ADX_14' columns.
        
    Returns:
        DataFrame with a new column 'regime'.
    """
    if df.empty:
        return df
        
    df = df.copy()
    
    # --- 1. Dynamic Volatility Threshold (The "Fear" Meter) ---
    # We don't use a fixed number like "20%". We look at the last year (252 days).
    # If today's volatility is higher than 80% of the last year, it's HIGH.
    rolling_vol_80pct = df['volatility_21'].rolling(window=252).quantile(0.80)
    
    # --- 2. Trend Threshold (The "Direction" Meter) ---
    # ADX > 20 usually means a trend is forming or active.
    ADX_THRESHOLD = 20.0
    
    def classify_row(row):
        # Safety First: Check Volatility
        # Note: If we don't have enough data for rolling_vol (beginning of chart), default to Safe.
        current_vol_limit = row.get('vol_80_pct', 999.0)
        
        if pd.notna(current_vol_limit) and row['volatility_21'] > current_vol_limit:
            return MarketRegime.VOLATILE
            
        # If safe, check Trend
        if row['ADX_14'] > ADX_THRESHOLD:
            return MarketRegime.TRENDING
        else:
            return MarketRegime.RANGING

    # Create a temporary column for the rolling percentile to make apply easier
    df['vol_80_pct'] = rolling_vol_80pct
    
    # Apply the logic row by row
    df['regime'] = df.apply(classify_row, axis=1)
    
    # Cleanup temp column
    df.drop(columns=['vol_80_pct'], inplace=True)
    
    return df

if __name__ == "__main__":
    # Test Driver
    import os
    from quant_core.data.indicators import add_features
    
    # Load Data
    raw_path = os.path.join("quant_core", "data", "raw", "SPY.parquet")
    if os.path.exists(raw_path):
        print("Loading SPY data...")
        df = pd.read_parquet(raw_path)
        
        print("Adding indicators...")
        df = add_features(df)
        
        print("Detecting Regimes...")
        df = detect_regime(df)
        
        # Show the last 10 days
        print("\n--- RECENT MARKET REGIME ---")
        print(df[['Close', 'volatility_21', 'ADX_14', 'regime']].tail(10))
        
        # Count stats
        counts = df['regime'].value_counts()
        print("\n--- REGIME STATISTICS (Last 5 Years) ---")
        print(counts)
    else:
        print("Error: SPY data not found. Run market_data.py first.")
