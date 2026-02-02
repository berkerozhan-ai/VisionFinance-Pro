import pandas as pd
import os
import random
from quant_core.data.market_data import get_all_tickers, DATA_DIR

class MarketPulse:
    def __init__(self):
        self.tickers = get_all_tickers()
        
    def get_daily_movers(self, top_n=5):
        """
        Scans all local data to find Top Gainers and Losers for the latest available date.
        """
        updates = []
        
        for ticker in self.tickers:
            path = os.path.join(DATA_DIR, f"{ticker}.parquet")
            if not os.path.exists(path):
                continue
            
            try:
                # Read only needed columns (last 2 rows to calc change if not present)
                df = pd.read_parquet(path)
                if len(df) < 2:
                    continue
                
                last_row = df.iloc[-1]
                prev_row = df.iloc[-2]
                
                # Calculate % Change
                if 'Close' in last_row and prev_row['Close'] > 0:
                    change = (last_row['Close'] - prev_row['Close']) / prev_row['Close']
                    updates.append({
                        "Ticker": ticker,
                        "Price": last_row['Close'],
                        "Change": change * 100, # In percentage
                        "Volume": last_row.get('Volume', 0)
                    })
            except:
                continue
                
        if not updates:
            return pd.DataFrame(), pd.DataFrame()
            
        df_all = pd.DataFrame(updates)
        
        # Sort
        gainers = df_all.sort_values(by="Change", ascending=False).head(top_n)
        losers = df_all.sort_values(by="Change", ascending=True).head(top_n)
        
        return gainers, losers

    def get_social_feed(self):
        """
        Generates simulated 'Social Trading' updates.
        In a real app, this would fetch from a DB of user portfolios.
        """
        names = ["Ahmet'in Tekno Fonu", "Ayşe'nin Temettü Sepeti", "Kripto Kralı (Mehmet)", "Global Makro (Ali)", "Devrim'in Yapay Zekası"]
        
        feed = []
        for name in names:
            # Simulate daily return between -2% and +5%
            daily_ret = random.uniform(-2.0, 5.0)
            
            feed.append({
                "User/Fund": name,
                "Daily Return": daily_ret,
                "Copiers": random.randint(50, 5000),
                "Top Holding": random.choice(self.tickers) if self.tickers else "CASH"
            })
            
        df_feed = pd.DataFrame(feed).sort_values(by="Daily Return", ascending=False)
        return df_feed

if __name__ == "__main__":
    pulse = MarketPulse()
    g, l = pulse.get_daily_movers()
    print("Gainers:", g)
    print("Social:", pulse.get_social_feed())
