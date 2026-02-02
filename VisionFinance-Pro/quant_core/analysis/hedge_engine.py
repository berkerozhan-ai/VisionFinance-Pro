import pandas as pd
import os
import numpy as np
from quant_core.data.market_data import get_all_tickers, DATA_DIR

class HedgeEngine:
    def __init__(self):
        self.tickers = get_all_tickers()
        
    def _get_master_df(self):
        """
        Reads 'Close' prices for ALL tickers and combines them into one DataFrame.
        This is resource intensive, so it should be cached by the caller (Streamlit).
        """
        closes = {}
        for ticker in self.tickers:
            try:
                path = os.path.join(DATA_DIR, f"{ticker}.parquet")
                if not os.path.exists(path):
                    continue
                
                # Only read Close column to save memory
                df = pd.read_parquet(path, columns=['Close'])
                if len(df) > 60: # Need at least 2 months of overlap
                    closes[ticker] = df['Close']
            except:
                continue
                
        master_df = pd.DataFrame(closes)
        # Forward fill to handle different trading calendars (crypto vs stocks)
        master_df = master_df.fillna(method='ffill').dropna(how='all')
        return master_df

    def find_hedges(self, target_ticker, top_n=3):
        """
        Finds the assets with the strongest NEGATIVE correlation to the target.
        """
        master_df = self._get_master_df()
        
        if target_ticker not in master_df.columns:
            return []
            
        # Calculate Correlations for the target column only (faster than full matrix)
        corrs = master_df.corrwith(master_df[target_ticker])
        
        # Sort by lowest correlation (most negative)
        # We look for correlations between -1.0 and -0.3
        hedges = corrs.sort_values(ascending=True).head(top_n)
        
        results = []
        for ticker, score in hedges.items():
            if score < -0.2: # Must have some meaningful inverse correlation
                results.append({
                    "Ticker": ticker,
                    "Correlation": round(score, 2),
                    "Type": "Inverse (Hedge)"
                })
        
        return results

if __name__ == "__main__":
    engine = HedgeEngine()
    print("Finding hedges for SPY...")
    # This might take a moment without caching
    print(engine.find_hedges("SPY"))
