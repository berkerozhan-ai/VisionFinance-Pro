import pandas as pd
import numpy as np

class PatternScorer:
    def __init__(self):
        # Weights definition from User Report
        self.WEIGHTS = {
            'PATTERN': 30,
            'TREND': 25,
            'VOLATILITY': 15,
            'MOMENTUM': 15,
            'LOCATION': 15 
        }

    def score_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates a 'signal_score' (0-100) for each day based on the User's Rulebook.
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # --- 1. PRE-CALCULATIONS ---
        df['body'] = (df['Close'] - df['Open']).abs()
        df['range_'] = df['High'] - df['Low']
        df['upper_wick'] = df['High'] - df[['Open', 'Close']].max(axis=1)
        df['lower_wick'] = df[['Open', 'Close']].min(axis=1) - df['Low']
        
        # Avoid zero division
        safe_range = df['range_'].replace(0, 0.0001)
        df['body_ratio'] = df['body'] / safe_range
        
        # Previous Candles
        df['prev_close'] = df['Close'].shift(1)
        df['prev_open'] = df['Open'].shift(1)
        df['prev_body'] = df['body'].shift(1)
        
        # --- 2. COMPONENT SCORES ---
        
        # A. PATTERN SCORE (Max 30)
        # -------------------------
        # Bullish Engulfing (Weight: 0.20 -> 20 pts)
        cond_engulf = (
            (df['prev_close'] < df['prev_open']) & # Prev Red
            (df['Close'] > df['Open']) &           # Curr Green
            (df['Open'] <= df['prev_close']) & 
            (df['Close'] >= df['prev_open']) &
            (df['body'] > df['prev_body'])
        )
        
        # Hammer / Pinbar (Weight: 0.25 -> 25 pts)
        cond_hammer = (
            (df['lower_wick'] >= (df['body'] * 2)) &
            (df['upper_wick'] <= (df['body'] * 0.5))
        )
        
        # Assign Pattern Points
        # We take the MAX of found patterns (e.g. if both somehow true, take higher)
        pattern_pts = np.zeros(len(df))
        
        # We use numpy where for vectorized scoring
        pattern_pts = np.where(cond_hammer, 25, pattern_pts)
        pattern_pts = np.where(cond_engulf, 20, pattern_pts) # Engulf overwrites Hammer if overlap? Unlikely.
        
        # B. TREND SCORE (Max 25)
        # -----------------------
        # Rule: Price > EMA20 (Short term trend) AND Price > SMA50 (Med term)
        # Let's assume SMA_50 exists from indicators.py.
        # If not calculates, we default to 0.
        trend_pts = np.zeros(len(df))
        if 'SMA_50' in df.columns:
            trend_pts = np.where(df['Close'] > df['SMA_50'], 25, 0)
            
        # C. VOLATILITY SCORE (Max 15)
        # ----------------------------
        # Rule: Range > ATR * 0.5 (Not a tiny doji noise)
        vol_pts = np.zeros(len(df))
        if 'ATR_14' in df.columns:
            # If candle range is significant
            vol_show = df['range_'] > (df['ATR_14'] * 0.5)
            vol_pts = np.where(vol_show, 15, 0)
            
        # D. MOMENTUM / RSI FILTER (Max 15)
        # ---------------------------------
        # For Bullish: We want RSI NOT Overbought (<70). Better if Oversold (<30).
        mom_pts = np.zeros(len(df))
        if 'RSI_14' in df.columns:
            # Ideal: RSI < 50 (Room to grow) -> 15 pts
            # Okay: 50 < RSI < 70 -> 10 pts
            # Bad: RSI > 70 -> 0 pts
            mom_pts = np.where(df['RSI_14'] < 50, 15, mom_pts)
            mom_pts = np.where((df['RSI_14'] >= 50) & (df['RSI_14'] < 70), 10, mom_pts)
            
        # E. SUPPORT/RESISTANCE (Proximity) (Max 15)
        # ------------------------------------------
        # Simplified: Is Low close to 20-day Low? (Liquidity Sweep Logic)
        loc_pts = np.zeros(len(df))
        if 'Low' in df.columns:
            roll_low = df['Low'].rolling(20).min().shift(1)
            # If Low poked near 20-day low?
            # Let's say if Close is within 2% of roll_low or actually swept it
            # Sweep logic: Low < RollLow but Close > RollLow
            sweep = (df['Low'] <= roll_low) & (df['Close'] >= roll_low)
            loc_pts = np.where(sweep, 15, 0)
            
        # --- 3. TOTAL SCORE ---
        df['signal_score'] = pattern_pts + trend_pts + vol_pts + mom_pts + loc_pts
        
        # Log Logic for Debug
        df['score_breakdown'] = (
            "Pat:" + pd.Series(pattern_pts).astype(int).astype(str) + 
            " Trd:" + pd.Series(trend_pts).astype(int).astype(str) + 
            " Vol:" + pd.Series(vol_pts).astype(int).astype(str) +
            " Mom:" + pd.Series(mom_pts).astype(int).astype(str) +
            " Loc:" + pd.Series(loc_pts).astype(int).astype(str)
        )
        
        return df

if __name__ == "__main__":
    import os
    from quant_core.data.indicators import add_features
    
    print("--- TESTING SIGNAL SCORES ---")
    raw_path = os.path.join("quant_core", "data", "raw", "SPY.parquet")
    if os.path.exists(raw_path):
        df = pd.read_parquet(raw_path)
        df = add_features(df)
        
        scorer = PatternScorer()
        df = scorer.score_patterns(df)
        
        # Filter for High Scores (>50)
        high_score = df[df['signal_score'] >= 50]
        print(f"Found {len(high_score)} potential signals.")
        print(high_score[['Close', 'signal_score', 'score_breakdown']].tail(10))
    else:
        print("Data not found.")
