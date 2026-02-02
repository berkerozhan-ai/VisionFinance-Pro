import pandas as pd
import numpy as np
from quant_core.engine.state import StateEngine
from quant_core.signals.strategy import SignalStrategy
from quant_core.risk.filters.risk import RiskManager
from quant_core.regimes.detectors.regime import MarketRegime

class Backtester:
    def __init__(self, initial_capital=10000.0, commission=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.strategy = SignalStrategy()
        # Allows for a simplified risk manager or the full one.
        # For backtesting to be fast, we might simplify risk if needed, 
        # but using the real one is better for "Trust".
        self.risk_manager = RiskManager(target_vol=0.15)
        self.state_engine = StateEngine()

    def run(self, df: pd.DataFrame, signal_threshold: int = 50, stop_loss_pct: float = 0.05):
        """
        Runs the simulation on the provided DataFrame.
        
        Args:
            df (pd.DataFrame): Data with features pre-calculated.
            signal_threshold (int): Minimum score to trigger a BUY.
            stop_loss_pct (float): Percentage to cut losses.
            
        Returns:
            dict: Simulation results (metrics, equity_curve, trades)
        """
        df = df.copy()
        
        # Initialize
        cash = self.initial_capital
        inventory = 0 # Number of shares
        equity_curve = []
        trades = []
        
        # State tracking
        in_position = False
        entry_price = 0.0
        
        # Reset Logic State
        self.state_engine = StateEngine()
        
        for i in range(len(df)):
            if i < 50: # Warmup
                equity_curve.append(cash)
                continue
                
            row = df.iloc[i]
            date = df.index[i]
            price = row['Close']
            
            # 1. Update Engine State
            regime = row.get('regime', MarketRegime.RANGING)
            self.state_engine.update(str(date), regime)
            
            # 2. Check Exits (SL / TP / Signal)
            action = None
            
            if in_position:
                # Stop Loss
                if price < entry_price * (1 - stop_loss_pct):
                    action = 'SELL'
                    reason = 'Stop Loss'
                # Take Profit / Signal Exit
                # For simplicity, we use the Strategy's signal logic (if it says HOLD or weak, we usually hold, 
                # but if we want to secure profit we might need logic. 
                # Current Strategy class mostly handles Entries. 
                # Let's add simple exit detection: If signal score drops drastically? 
                # Or just trailing stop? Let's use Trailing Stop logic implicitly via "Sell if High Volatility".
                
                # Check Strategy for Sell signal
                # Note: original strategy mainly returns BUY/HOLD. 
                # If regime becomes Volatile -> Sell.
                elif regime == MarketRegime.VOLATILE and row.get('signal_score', 0) < 80:
                    action = 'SELL'
                    reason = 'Volatile Regime Exit'
                
                if action == 'SELL':
                    # Execute Sell
                    cash += inventory * price * (1 - self.commission)
                    trades.append({
                        'Date': date, 'Type': 'SELL', 'Price': price, 
                        'Shares': inventory, 'Reason': reason, 'Balance': cash
                    })
                    inventory = 0
                    in_position = False

            # 3. Check Entries
            if not in_position:
                # Use Strategy Logic (Modified by thresholds)
                # We reuse the generated features.
                score = row.get('signal_score', 0)
                
                # Custom Threshold Logic overrides standard strategy for sensitivity testing
                buy_signal = score >= signal_threshold
                
                # Also check standard rules (Regime filter etc)
                # If user sets threshold low, we trust them, but maybe minimal regime check?
                # Let's use the standard strategy.generate_signal BUT allow score override in our logic
                # Actually, better to just look at Score for this interactive backtest.
                
                if buy_signal and regime != MarketRegime.VOLATILE:
                    # Calculate Size (Simplified Kelly or Fixed % for readability)
                    # Let's use 25% of capital for simplicity in single-asset tests, 
                    # or the Risk Manager if we want "Realism".
                    # Let's use Risk Manager.
                    # We need 'confidence'. Map score to confidence 0.5 - 1.0
                    confidence = min(1.0, max(0.5, score / 100.0))
                    
                    size_pct = self.risk_manager.calculate_size(
                        confidence, row.get('volatility_21', 0.15), True
                    )
                    
                    # Cap size at 100% (since we are backtesting 1 asset portfolio)
                    # In a portfolio runner, size is small. Here, "Portfolio" is just this asset.
                    # So we scale up. if size was 0.05 (5%), that means 5% of TOTAL portfolio. 
                    # If this is the only asset, we might want to go heavier. 
                    # Let's assume this is a pure "Strategy Test" -> 100% active capital max.
                    position_value = cash * min(0.95, size_pct * 5) # 5x leverage on the small risk? No.
                    # Let's just use fixed 100% for straightforward "Does the signal work?" test
                    position_value = cash * 0.98 # Leave dust
                    
                    shares = int(position_value / price)
                    
                    if shares > 0:
                        inventory = shares
                        cash -= shares * price * (1 + self.commission)
                        entry_price = price
                        in_position = True
                        trades.append({
                            'Date': date, 'Type': 'BUY', 'Price': price, 
                            'Shares': shares, 'Score': score, 'Balance': cash
                        })

            # Calculate Daily Equity
            current_val = cash + (inventory * price)
            equity_curve.append(current_val)
            
        # Post-Process Results
        equity_series = pd.Series(equity_curve, index=df.index)
        
        # Calculate Metrics
        total_ret = (equity_series.iloc[-1] / self.initial_capital) - 1
        
        # Drawdown
        roll_max = equity_series.cummax()
        drawdown = (equity_series - roll_max) / roll_max
        max_dd = drawdown.min()
        
        results = {
            'equity_curve': equity_series,
            'trades': pd.DataFrame(trades),
            'metrics': {
                'Total Return': f"%{total_ret*100:.2f}",
                'Max Drawdown': f"%{max_dd*100:.2f}",
                'Final Balance': f"${equity_series.iloc[-1]:,.2f}",
                'Trade Count': len(trades)
            }
        }
        
        return results
