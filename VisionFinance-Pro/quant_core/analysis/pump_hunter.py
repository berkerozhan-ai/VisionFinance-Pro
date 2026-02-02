import pandas as pd
import numpy as np

class VolumeAnalyzer:
    def __init__(self):
        pass
        
    def analyze_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds volume analytics to the DataFrame.
        """
        if df.empty:
            return df
            
        df = df.copy()
        
        # 1. Calculate Average Volume (20-day benchmark)
        df['Vol_Avg_20'] = df['Volume'].rolling(window=20).mean()
        
        # 2. Calculate RVOL (Relative Volume)
        # Avoid division by zero
        safe_avg = df['Vol_Avg_20'].replace(0, 1)
        df['RVOL'] = df['Volume'] / safe_avg
        
        # 3. Volume Trend (Is smart money entering?)
        # Logic: If Volume is increasing for 3 days straight
        df['Vol_Change'] = df['Volume'].pct_change()
        # Check if last 3 days volume change was positive
        # (This is a bit hard to vectorize simply, let's look at slope or simple consecutive checks)
        # Simplified: Is today's volume > yesterday > day before?
        df['Vol_Trending_Up'] = (
            (df['Volume'] > df['Volume'].shift(1)) & 
            (df['Volume'].shift(1) > df['Volume'].shift(2))
        )
        
        # 4. Anomaly Detection (The "Pump/Dump" Alert)
        # If Volume is 3x normal, something BIG is happening.
        df['Vol_Anomaly'] = df['RVOL'] > 3.0
        
        # 5. Interpretive Signal
        # High Volume + Green Candle = Strong Buying (Validation)
        # High Volume + Red Candle = Panic Selling (Capitulation)
        # Low Volume + Green Candle = Fakeout (No Convention)
        
        conditions = [
            (df['RVOL'] > 1.5) & (df['Close'] > df['Open']), # Strong Buy Support
            (df['RVOL'] > 1.5) & (df['Close'] < df['Open']), # Strong Sell Pressure
            (df['RVOL'] < 0.7) # Low Interest (Drying up)
        ]
        choices = ['HIGH_VOL_BUY', 'HIGH_VOL_SELL', 'LOW_VOL']
        
        df['Vol_Signal'] = np.select(conditions, choices, default='NORMAL')
        
        return df

if __name__ == "__main__":
    import os
    # Test Driver
    raw_path = os.path.join("quant_core", "data", "raw", "SPY.parquet")
    if os.path.exists(raw_path):
        print("Testing Volume Analyzer...")
        df = pd.read_parquet(raw_path)
        
        analyzer = VolumeAnalyzer()
        df = analyzer.analyze_volume(df)
        
        # Show days with Abnormal Volume
        anomalies = df[df['RVOL'] > 2.0]
        print(f"\nFound {len(anomalies)} High Volume events (RVOL > 2.0).")
        print(df[['Close', 'Volume', 'Vol_Avg_20', 'RVOL', 'Vol_Signal']].tail(10))
    else:
        print("Data not found.")
