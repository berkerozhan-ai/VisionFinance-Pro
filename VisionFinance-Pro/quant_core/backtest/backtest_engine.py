import pandas as pd
import numpy as np
import os

# Import our modules
from quant_core.data.indicators import add_features
from quant_core.regimes.detectors.regime import detect_regime, MarketRegime
from quant_core.regimes.detectors.patterns import PatternScorer
from quant_core.analysis.pump_hunter import VolumeAnalyzer
from quant_core.engine.state import StateEngine
from quant_core.risk.filters.risk import RiskManager
from quant_core.signals.strategy import SignalStrategy

class BacktestEngine:
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = 0.0 # Value of assets held
        self.cash = initial_capital
        self.equity_curve = []
        
        # Initialize Components
        self.state_engine = StateEngine()
        self.risk_manager = RiskManager(target_vol=0.15)
        self.strategy = SignalStrategy()
        
    def run(self, ticker="SPY"):
        print(f"--- STARTING BACKTEST: {ticker} ---")
        
        # 1. Load & Prep Data
        raw_path = os.path.join("quant_core", "data", "raw", f"{ticker}.parquet")
        if not os.path.exists(raw_path):
            print("Data not found.")
            return

        df = pd.read_parquet(raw_path)
        df = add_features(df)
        df = detect_regime(df)
        
        # [NEW] Calculate Pattern Scores
        print("Scoring Patterns...")
        scorer = PatternScorer()
        df = scorer.score_patterns(df)
        
        # [NEW] Calculate Volume Analytics
        print("Analyzing Volume Traps...")
        vol = VolumeAnalyzer()
        df = vol.analyze_volume(df)
        
        # 2. Simulation Loop
        print(f"Simulating {len(df)} days...")
        
        for date, row in df.iterrows():
            date_str = str(date).split(" ")[0]
            current_price = row['Close']
            
            # A. Update State (Brain)
            regime = row['regime']
            state = self.state_engine.update(date_str, regime)
            
            # B. Generate Signal (Tactics)
            sig_result = self.strategy.generate_signal(row)
            
            # C. Risk Management (Wallet)
            # 1.0 = Buy, -1.0 = Sell, 0.0 = Hold
            # We map 'BUY' to 1.0, 'SELL' to -1.0 for sizing calc
            sig_val = 1.0 if sig_result['action'] == 'BUY' else 0.0
            
            # If Action is SELL, we force size to 0.0 (Cash)
            if sig_result['action'] == 'SELL':
                target_size_pct = 0.0
            else:
                target_size_pct = self.risk_manager.calculate_size(
                    signal_strength=sig_result['confidence'], 
                    current_volatility=row['volatility_21'],
                    is_risk_allowed=state.is_risk_allowed
                )

            # D. Execution (The Trade)
            # Simple Logic: Rebalance to Target Size
            # Target Value = Total Equity * Target %
            total_equity = self.cash + self.positions
            target_value = total_equity * target_size_pct
            
            # We assume we can trade fractional shares and zero cost for this MVP
            diff = target_value - self.positions
            
            if diff != 0:
                # Buying or Selling
                self.positions += diff
                self.cash -= diff
            
            # Update Position Value for next day (Mark to Market)
            # In a real loop we'd track shares, but value-based tracking is simpler for MVP 
            # Note: This is a simplification. For exact tracking we need:
            # shares = self.positions / current_price. 
            # Let's do it slightly better:
            # We held 'positions' amount of dollars in stock at 'current_price'.
            # Next loop, this value changes. We need to handle the daily return.
            # But here we are iterating: Today's decision -> Trade at Close -> Hold overnight.
            
            # Let's fix the logic for properly tracking PnL:
            # 1. Calculate Equity BEFORE trade (from yesterday's holdings moving with today's price)
            # 2. Execute Trade
            # 3. Record Equity
            
            pass # (The logic above is slightly flawed for PnL tracking in a single pass without lookahead)
            
        print("--- RE-RUNNING WITH VECTORIZED PNL FOR SPEED & ACCURACY ---")
        self.run_vectorized(df)

    def run_vectorized(self, df):
        """
        A more robust way to calculate PnL using pandas.
        """
        # We need to simulate the state updates day-by-day because of the StateEngine memory
        # So we create a list of 'Target Allocations'
        
        allocations = []
        
        # Reset Engine for clean run
        self.state_engine = StateEngine()
        
        for date, row in df.iterrows():
            date_str = str(date).split(" ")[0]
            
            # 1. State
            state = self.state_engine.update(date_str, row['regime'])
            
            # 2. Signal
            sig = self.strategy.generate_signal(row)
            
            # 3. Risk
            if sig['action'] == 'SELL':
                size = 0.0
            elif sig['action'] == 'HOLD':
                # Hold previous allocation? Or 0?
                # Simplified: Strategy returns HOLD if no signal. 
                # If we are strictly Trend Following, HOLD usually means "Keep position".
                # But our Strategy returns HOLD when no entry rules met.
                # Let's assume we want to be IN only if BUY signal persists? 
                # No, usually once in, we stay until Exit.
                # FIX: We need a stateful strategy or assume 'BUY' means 'Be Long'.
                # For this MVP, let's assume 'BUY' signal is persistent condition (Price > SMA).
                # Checking strategy.py: It checks (Price > SMA) every day. So if valid, it says BUY.
                # So we can treat BUY as "Stay Long".
                size = 0.0 # Default if HOLD (No signal matched)
            else:
                size = self.risk_manager.calculate_size(
                    sig['confidence'], row['volatility_21'], state.is_risk_allowed
                )
            
            # Strategy.py returns 'BUY' as long as conditions are met. 
            # If conditions fail (e.g. Price < SMA), it returns SELL or HOLD.
            # It returns SELL if Price < SMA200.
            # It returns HOLD if just "No Signal". 
            
            # Let's just append the calculated size.
            allocations.append(size)
            
        df['allocation'] = allocations
        df['strategy_ret'] = df['allocation'].shift(1) * df['log_ret']
        
        # Calculate Equity Curve
        df['equity_curve'] = (1 + df['strategy_ret']).cumprod() * self.initial_capital
        df['benchmark_curve'] = (1 + df['log_ret']).cumprod() * self.initial_capital
        
        # Statistics
        total_ret = (df['equity_curve'].iloc[-1] / self.initial_capital) - 1
        bench_ret = (df['benchmark_curve'].iloc[-1] / self.initial_capital) - 1
        
        # Max Drawdown
        roll_max = df['equity_curve'].cummax()
        drawdown = (df['equity_curve'] - roll_max) / roll_max
        max_dd = drawdown.min()
        
        # Sharpe (Simplified)
        sharpe = (df['strategy_ret'].mean() / df['strategy_ret'].std()) * np.sqrt(252)
        
        print("\n" + "="*40)
        print(f" FINAL RESULTS")
        print("="*40)
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Equity:    ${df['equity_curve'].iloc[-1]:,.2f}")
        print(f"Total Return:    {total_ret*100:.2f}% (Benchmark: {bench_ret*100:.2f}%)")
        print(f"Sharpe Ratio:    {sharpe:.2f}")
        print(f"Max Drawdown:    {max_dd*100:.2f}%")
        print("="*40)
        
        # Show specific events (e.g. Volatility Lock)
        print("\nLog Snapshot (Regime Logic):")
        print(df[['Close', 'regime', 'allocation', 'equity_curve']].tail(10))

if __name__ == "__main__":
    bt = BacktestEngine()
    bt.run("SPY")
