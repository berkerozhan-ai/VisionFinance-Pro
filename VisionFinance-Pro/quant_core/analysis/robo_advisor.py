import pandas as pd
import numpy as np
import os
from quant_core.data.market_data import get_all_tickers, DATA_DIR

class RoboAdvisor:
    def __init__(self):
        self.tickers = get_all_tickers()
    
    def generate_portfolio(self, capital, risk_profile="Balanced", focus_sectors=None):
        """
        Constructs a portfolio recommendation.
        
        Args:
            capital (float): Total investment amount.
            risk_profile (str): 'Conservative', 'Balanced', 'Aggressive'.
            focus_sectors (list): List of sectors to focus on (e.g. ['Technology', 'Metals']).
            
        Returns:
            dict: Portfolio allocation details.
        """
        candidates = []
        
        # 1. Screen Assets
        # Build Sector Map on fail (simple lookup)
        ticker_sector_map = {}
        # We need to import TICKER_UNIVERSE inside or pass it. 
        # Ideally import at top, but to avoid circular imports if any, we can do it here or pass it.
        from quant_core.data.market_data import TICKER_UNIVERSE
        
        for reg, secs in TICKER_UNIVERSE.items():
            for sec, t_list in secs.items():
                for t in t_list:
                    ticker_sector_map[t] = sec

        from quant_core.signals.strategy import SignalStrategy
        from quant_core.data.indicators import add_features
        
        # Initialize Strategy for Sanity Check
        strategy_engine = SignalStrategy()
        
        for ticker in self.tickers:
            # Filter by Sector if requested
            if focus_sectors:
                sec = ticker_sector_map.get(ticker, "Unknown")
                if sec not in focus_sectors:
                    continue

            # Read Data
            path = os.path.join(DATA_DIR, f"{ticker}.parquet")
            if not os.path.exists(path):
                continue
                
            df = pd.read_parquet(path)
            if df.empty or len(df) < 50:
                continue
            
            # --- SANITY CHECK (Don't buy if Core Strategy says SELL) ---
            # We need indicators for the strategy
            try:
                # Minimal feature gen for speed (SMA, RSI, BB)
                # Just calling add_features is safest
                df_check = df.copy()
                df_check = add_features(df_check)
                
                last_row = df_check.iloc[-1]
                sig = strategy_engine.generate_signal(last_row)
                
                if sig['action'] == 'SELL':
                    # Skip this asset strictly
                    continue
            except:
                # If indicators fail, skip for safety
                continue
                
            # 2. Calculate Metrics (Score)
            last_close = df['Close'].iloc[-1]
            
            # Momentum (Returns)
            ret_3m = df['Close'].pct_change(60).iloc[-1] # 3 month return
            
            # Volatility (Risk)
            volatility = df['Close'].pct_change().std() * np.sqrt(252)
            
            # Trend (SMA) - Simple Logic
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) > 50 else last_close
            trend_score = 1 if last_close > sma_50 else 0
            
            # Assign Score based on Risk Profile
            score = 0
            if risk_profile == "Aggressive":
                # High Risk, High Reward
                score = (ret_3m * 0.7) + (trend_score * 0.3)
            elif risk_profile == "Conservative":
                # Low Volatility, Positive Trend
                score = (trend_score * 0.5) - (volatility * 0.5)
            else: # Balanced
                score = (ret_3m * 0.4) - (volatility * 0.2) + (trend_score * 0.4)
            
            candidates.append({
                "Ticker": ticker,
                "Price": last_close,
                "Score": score,
                "Volatility": volatility,
                "Return_3M": ret_3m
            })
            
        # 3. Select Top Assets
        df_cand = pd.DataFrame(candidates)
        if df_cand.empty:
            return None
            
        # Pick top 5-7 assets
        top_picks = df_cand.sort_values(by="Score", ascending=False).head(5)
        
        # 4. Allocate Capital
        # Simplified: Weight by Score (normalized)
        # Ensure non-negative scores for weights
        min_score = top_picks['Score'].min()
        if min_score < 0:
            top_picks['Score'] = top_picks['Score'] + abs(min_score) + 0.1
            
        total_score = top_picks['Score'].sum()
        top_picks['Weight'] = top_picks['Score'] / total_score
        top_picks['Allocation ($)'] = top_picks['Weight'] * capital
        top_picks['Shares'] = (top_picks['Allocation ($)'] / top_picks['Price']).astype(int)
        
        return {
            "portfolio": top_picks[['Ticker', 'Weight', 'Allocation ($)', 'Shares', 'Price']],
            "risk_profile": risk_profile,
            "total_capital": capital
        }

if __name__ == "__main__":
    advisor = RoboAdvisor()
    port = advisor.generate_portfolio(100000, "Aggressive")
    if port:
        print(port['portfolio'])
    else:
        print("No valid portfolio found.")
