import pandas as pd
import os
from quant_core.data.market_data import get_all_tickers, DATA_DIR, smart_load_ticker

class MarketScanner:
    def __init__(self):
        self.tickers = get_all_tickers()
        
    def scan_for_whales(self, threshold=1.5):
        """
        Scans ALL tickers for Volume Anomalies (RVOL > threshold).
        Returns a DataFrame of results sorted by RVOL.
        """
        results = []
        
        for ticker in self.tickers:
            try:
                # Fast Parquet Read (Only columns we need?)
                # We use smart_load_ticker in FAST mode (strict=False) to avoid network calls in loop
                df = smart_load_ticker(ticker, strict=False)
                
                if df is None or df.empty or len(df) < 20: 
                    continue
                
                # Check Last Row
                df_tail = df.tail(21) # 20 for MA + 1 for current
                last_row = df_tail.iloc[-1]
                
                # Calculate RVOL on the fly (Fast)
                vol_ma = df_tail['Volume'].iloc[:-1].mean() # Previous 20 days
                
                # Minimum Volume Threshold to avoid 1300x artifacts on illiquid/gap data
                if vol_ma < 1000: # Lowered to 1k to keep Silver/Gold futures visible
                    continue
                    
                curr_vol = last_row['Volume']
                rvol = curr_vol / vol_ma
                
                if rvol >= threshold:
                    # Determine intent
                    open_p = last_row['Open']
                    close_p = last_row['Close']
                    pct_change = (close_p - open_p) / open_p
                    
                    signal = "BUY" if close_p > open_p else "SELL"
                    
                    from quant_core.data.market_data import get_display_name # Lazy import
                    friendly_name = get_display_name(ticker)
                    
                    results.append({
                        "Ticker": friendly_name, # Display Name for UI
                        "RawTicker": ticker,     # Keep for sorting/logic if needed
                        "RVOL": round(rvol, 2),
                        "Volume": f"{curr_vol/1000:.1f}K",
                        "Signal": signal,
                        "Change": f"%{pct_change*100:.1f}"
                    })
            except Exception:
                continue
                
        # Return sorted by RVOL descending
        if results:
            df_res = pd.DataFrame(results)
            return df_res.sort_values(by="RVOL", ascending=False)
        return pd.DataFrame()

if __name__ == "__main__":
    scanner = MarketScanner()
    print("Scanning...")
    df = scanner.scan_for_whales()
    print(df)
