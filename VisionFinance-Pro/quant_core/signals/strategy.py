import pandas as pd
import numpy as np
from quant_core.regimes.detectors.regime import MarketRegime
from quant_core.regimes.detectors.patterns import PatternScorer

class SignalStrategy:
    def __init__(self):
        # Initialize the Scorer we built in Step 10
        self.scorer = PatternScorer()
        
    def generate_signal(self, row: pd.Series, full_df: pd.DataFrame = None, current_idx: int = None) -> dict:
        """
        Decides on the action based on Regime AND Pattern Score.
        
        Args:
            row: The current single row of data.
            full_df: The entire dataframe (needed for pattern lookback).
            current_idx: The index of the current row in full_df.
        """
        
        regime = row.get('regime', MarketRegime.RANGING)
        score = row.get('signal_score', 0)
        
        # --- 0. SAFETY FIRST ---
        if regime == MarketRegime.VOLATILE:
            # EXCEPTION: "Sniper Mode"
            # If the technical pattern is PERFECT (Score >= 85), we take a small stab even in high vol.
            if score >= 85:
                 return {
                    'action': 'BUY', 
                    'confidence': 0.3, # Low stakes (30%)
                    'rule': 'Sniper Entry in Volatile Market (Score 85+)'
                }
            
            return {
                'action': 'SELL', 
                'confidence': 1.0, 
                'rule': 'Regime is Volatile. Cash is King.'
            }

        # --- 1. GET PATTERN SCORE ---
        # We need to run the scorer on the history up to this point to be safe,
        # or if we pre-calculated it, we just read it.
        # For efficiency in a loop, we assume 'signal_score' is already in 'row' 
        # or we calculate it on the fly if needed.
        # Let's assume the BacktestEngine pre-calculates scores for the whole DF to save speed.
        
        # score is already calculated above
        
        # If score is missing (e.g. live trade), we might need to calc it here.
        # But for this architecture, we will update BacktestEngine to add scores first.
        
        # --- 2. VOLUME CHECK (Pump Hunter) ---
        # "Trap Check": If price is dropping on huge volume, it's a 'High Vol Sell' (Panic/Dump). 
        # We should NOT buy into this knife.
        vol_signal = row.get('Vol_Signal', 'NORMAL')
        
        if vol_signal == 'HIGH_VOL_SELL':
            return {
                'action': 'HOLD', # Block the Buy
                'confidence': 0.0,
                'rule': 'Volume Trap Detected (High Vol + Price Drop). Stay away.'
            }

        # --- 3. DECISION LOGIC (The "Fusion") ---
        
        # A. STRONG SIGNAL (Score >= 50) - LOWERED FOR ACTIVE TRADING
        # ------------------------------
        if score >= 50:
            return {
                'action': 'BUY',
                'confidence': 0.9,
                'rule': f'Active Setup! Score: {score}/100 exceeds new threshold (50)'
            }
            
        # B. MEDIUM SIGNAL (40 <= Score < 50)
        # -----------------------------------
        # Only take these if the Regime helps us.
        if score >= 40:
            if regime == MarketRegime.TRENDING:
                return {
                    'action': 'BUY',
                    'confidence': 0.6,
                    'rule': f'Trend Following w/ Decent Score: {score}'
                }
            elif regime == MarketRegime.RANGING:
                 # RELAXED: Allow trades in Range if score > 45 (was 60)
                 if score >= 45:
                     return {
                        'action': 'BUY',
                        'confidence': 0.5,
                        'rule': f'Range Play. Score {score} passes active threshold (45).'
                    }
                 else:
                     return {
                        'action': 'HOLD',
                        'confidence': 0.0,
                        'rule': f'Range requires decent setup (60+). Score {score} too low.'
                    }
        
        # C. WEAK SIGNAL
        # --------------
        return {
            'action': 'HOLD',
            'confidence': 0.0,
            'rule': 'No significant signal.'
        }

if __name__ == "__main__":
    # Test Driver
    import os
    from quant_core.data.indicators import add_features
    from quant_core.regimes.detectors.regime import detect_regime
    
    # Load Data
    raw_path = os.path.join("quant_core", "data", "raw", "SPY.parquet")
    if os.path.exists(raw_path):
        df = pd.read_parquet(raw_path)
        df = add_features(df)
        df = detect_regime(df)
        
        # CRITICAL: Calculate Scores first!
        scorer = PatternScorer()
        df = scorer.score_patterns(df)
        
        strat = SignalStrategy()
        
        print(f"{'DATE':<12} | {'REGIME':<10} | {'SCORE':<5} | {'ACTION':<6} | {'RULE'}")
        print("-" * 100)
        
        # Test on profitable days
        interesting_days = df[df['signal_score'] > 40].tail(10)
        
        for index, row in interesting_days.iterrows():
            result = strat.generate_signal(row)
            date_str = str(index).split(" ")[0]
            print(f"{date_str:<12} | {row['regime']:<10} | {int(row['signal_score']):<5} | {result['action']:<6} | {result['rule']}")
    else:
        print("Data not found.")
