
import os
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

# Import Core Modules
from quant_core.data import market_data
from quant_core.data import market_data
from quant_core.data.market_data import get_all_tickers, DATA_DIR, fetch_data, smart_load_ticker
from quant_core.data.indicators import add_features
from quant_core.regimes.detectors.regime import detect_regime, MarketRegime
from quant_core.regimes.detectors.patterns import PatternScorer
from quant_core.analysis.pump_hunter import VolumeAnalyzer
from quant_core.signals.strategy import SignalStrategy
from quant_core.risk.filters.risk import RiskManager

from quant_core.engine.state import StateEngine
from quant_core.engine.state import StateEngine
from quant_core.analysis.narrative import NarrativeEngine
from quant_core.utils.localization import get_text

class PortfolioRunner:
    def __init__(self, initial_capital=10000.0, tickers=None, lang="Türkçe"):
        self.initial_capital = initial_capital
        self.lang = lang
        
        if tickers:
            self.tickers = tickers
        else:
            self.tickers = get_all_tickers()
        self.strategy = SignalStrategy()
        self.risk_manager = RiskManager(target_vol=0.15)

        self.state_engine = StateEngine()
        self.narrative_engine = NarrativeEngine()
        
    def run_full_analysis(self):
        """
        Runs backtest on ALL tickers and generates a Current Allocation table.
        """
        print(f"--- STARTING PORTFOLIO ANALYSIS (Capital: ${self.initial_capital:,.2f}) ---")
        
        # 1. Ensure Data is Fresh
        # We assume data is reasonably fresh, but let's check existence.
        if not os.path.exists(DATA_DIR):
             print("Data directory not found. Fetching data...")
             fetch_data()
        
        stats = []
        allocations = []
        
        for ticker in self.tickers:
            try:
                # Load Data
                df = self._load_and_prep(ticker)
                if df is None:
                    continue
                
                # Run Backtest
                metrics = self._run_backtest(df, ticker)
                stats.append(metrics)
                
                # Get Current Allocation
                alloc = self._get_current_allocation(df, ticker)
                allocations.append(alloc)
                
            except Exception as e:
                print(f"Error analyzing {ticker}: {e}")
                traceback.print_exc()
                
        return stats, allocations

    def print_report(self, stats, allocations):
        """
        Prints the standard detailed report.
        """
        self._print_backtest_summary(stats)
        self._print_allocation_advice(allocations)
        
    def _load_and_prep(self, ticker):
        # Use smart_load_ticker to auto-heal/fetch if missing
        df = smart_load_ticker(ticker)
        
        if df is None or df.empty:
            print(f"Skipping {ticker}: No data.")
            return None
        
        # Feature Engineering
        df = add_features(df)
        df = detect_regime(df)
        
        # Pattern & Volume Analysis
        scorer = PatternScorer()
        df = scorer.score_patterns(df)
        
        vol = VolumeAnalyzer()
        df = vol.analyze_volume(df)
        
        return df
        
    def _run_backtest(self, df, ticker):
        """
        Vectorized Backtest for detailed stats.
        """
        df = df.copy()
        
        # 1. Sim Loop for Signals/Allocations (Cannot be fully vectorized due to path dependence of some logic, 
        # but here we replicate basic Strategy Logic)
        
        # We need to reconstruct the loop logic simply to get 'allocation' column
        # Or we can blindly apply the strategy row-by-row
        # Speed optimization: Apply simple logic
        
        # For 'allocation':
        # logic: if signal='BUY' -> size = risk_calc(). 
        # But risk_calc depends on 'state' (is_risk_allowed). State updates daily.
        # So we MUST loop.
        
        # allocs = []
        # Reset State for each ticker backtest
        self.state_engine = StateEngine()
        
        allocs = []
        for i in range(len(df)):
            row = df.iloc[i]
            
            # Update State
            # Ensure date is string, regime is string
            date_str = str(df.index[i])
            regime = row.get('regime', MarketRegime.RANGING)
            
            state_snapshot = self.state_engine.update(date_str, regime)
            
            # Generate Signal
            sig = self.strategy.generate_signal(row)
            
            # Calculate Size
            if sig['action'] == 'BUY':
                size = self.risk_manager.calculate_size(
                    sig['confidence'], 
                    row.get('volatility_21', 0.15), 
                    state_snapshot.is_risk_allowed
                )
            else:
                size = 0.0
            
            allocs.append(size)
            
        df['allocation'] = allocs
        df['strategy_ret'] = df['allocation'].shift(1) * df['log_ret']
        df['equity_curve'] = (1 + df['strategy_ret']).cumprod()
        
        # KPIs
        if df['equity_curve'].isnull().all() or len(df) == 0:
             total_ret = 0.0
             max_dd = 0.0
             final_eq = self.initial_capital
        else:
             total_ret = (df['equity_curve'].iloc[-1] - 1) * 100
             roll_max = df['equity_curve'].cummax()
             dd = (df['equity_curve'] - roll_max) / roll_max
             max_dd = dd.min() * 100
             final_eq = df['equity_curve'].iloc[-1] * self.initial_capital
        
        return {
            "Ticker": ticker,
            "Return %": round(total_ret, 2),
            "Max DD %": round(max_dd, 2),
            "Final Equity": round(final_eq, 2)
        }

    def _get_current_allocation(self, df, ticker):
        """
        Analyzes the LAST row to give "Today's Advice".
        """
        last_row = df.iloc[-1]
        
        # Check Risk State manually since we just finished the loop
        is_risk_allowed = (
            self.state_engine.current_regime != MarketRegime.VOLATILE 
            and self.state_engine.cooldown_counter == 0
        )
        
        sig = self.strategy.generate_signal(last_row)
        
        # Recalculate size for TODAY
        size = 0.0
        reason = sig.get('rule', 'N/A')
        
        if sig['action'] == 'BUY':
             size = self.risk_manager.calculate_size(
                sig['confidence'], 
                last_row.get('volatility_21', 0.15), 
                is_risk_allowed
            )
        
        # Monetary Value
        cash_needed = size * self.initial_capital
        
        # Narrative Analysis
        # 1. Prepare Tech State
        tech_state = {
            'trend': 'UP' if last_row['Close'] > last_row.get('SMA_50', 0) else 'DOWN',
            'volume_strength': last_row['Volume'] / last_row.get('Volume_MA', last_row['Volume']) if 'Volume_MA' in last_row else 1.0
        }
        
        # 2. REAL AI Analysis (RAG Agent)
        # We need to instantiate RAGAgent here or in __init__
        # For efficiency, we can do it on the fly or pass it in.
        # Let's import it at top level if needed, but here is fine for prototype.
        from quant_core.analysis.rag_agent import RAGAgent
        rag = RAGAgent()
        
        # If toggled off in UI, we might skip this, but for now we run it.
        # Ideally, we pass 'ai_enabled' flag from Dashboard -> Runner.
        # We will assume enabled for now, or handle empty return.
        
        
        ai_result = rag.analyze_context(ticker, lang=self.lang)
        
        # 3. Narrative Generation with Real Inputs
        analysis = self.narrative_engine.analyze_context(
            ticker=ticker, 
            technical_state=tech_state, 
            news_headlines=[], 
            market_sentiment_score=ai_result['sentiment_score'],
            lang=self.lang
        )
        
        # Merge RAG details into Story
        # We append the AI Headlines to the story manually here
        ai_section = get_text('ai_news_summary_header', self.lang) + ai_result['summary'] + "\n"
        for d in ai_result['details']:
            ai_section += f"- {d}\n"
            
        full_story = analysis['story'] + ai_section

        return {
            "Ticker": ticker,
            "Action": sig['action'],
            "Size": size,
            "Capital ($)": round(cash_needed, 2),
            "Price": round(last_row['Close'], 2),
            "Shares": int(cash_needed / last_row['Close']) if last_row['Close'] > 0 else 0,
            "Reason": reason,
            "Story": full_story,
            "Advice": analysis['advice'],
            # --- NEW METRICS FOR DASHBOARD UI ---
            "Sentiment_Score": ai_result['sentiment_score'],
            "RVOL": last_row.get('RVOL', 0.0),
            "Vol_Signal": last_row.get('Vol_Signal', 'NORMAL'),
            "News_Articles": ai_result.get('articles', [])
        }

    def _print_backtest_summary(self, stats):
        print("\n" + "="*60)
        print(f" PORTFOLIO BACKTEST SUMMARY (Historical Performance)")
        print("="*60)
        print(f"{'TICKER':<8} | {'RETURN %':<10} | {'MAX DD %':<10} | {'FINAL EQUITY ($)':<15}")
        print("-" * 60)
        
        total_equity = 0
        
        for s in stats:
            print(f"{s['Ticker']:<8} | {s['Return %']:<10} | {s['Max DD %']:<10} | ${s['Final Equity']:,.2f}")
            total_equity += s['Final Equity'] # Note: This sums independent 10k runs.
            
        print("-" * 60)
        print(f"AVG RETURN: {np.mean([s['Return %'] for s in stats]):.2f}%")
        
    def _print_allocation_advice(self, allocations):
        print("\n" + "="*80)
        print(f" CURRENT ALLOCATION ADVICE (Based on Last Close)")
        print(f" Total Capital Available: ${self.initial_capital:,.2f} per asset (Theoretical)")
        print("="*80)
        print(f"{'TICKER':<8} | {'ACTION':<6} | {'SIZE':<5} | {'SHARES':<6} | {'VALUE ($)':<10} | {'REASON'}")
        print("-" * 80)
        
        total_invested = 0
        
        for a in allocations:
            if a['Action'] == 'BUY':
                print(f"{a['Ticker']:<8} | {a['Action']:<6} | {a['Size']:<5} | {a['Shares']:<6} | ${a['Capital ($)']:<10,.2f} | {a['Reason']}")
                print(f"   > AI GORUSU: {a['Advice']}")
                print(f"   > KAFA RAPORU: {a['Story']}\n")
                total_invested += a['Capital ($)']
            else:
                 # Show Holds/Sells less prominently
                 print(f"{a['Ticker']:<8} | {a['Action']:<6} | {0.0:<5} | {0:<6} | $0.00       | {a['Reason']}")
                 print(f"   > AI GORUSU: {a['Advice']}")
                 print(f"   > KAFA RAPORU: {a['Story']}\n")

        print("-" * 80)
        print(f"TOTAL CAPITAL DEPLOYED: ${total_invested:,.2f}")
        
if __name__ == "__main__":
    runner = PortfolioRunner(initial_capital=10000)
    runner.run_full_analysis()
