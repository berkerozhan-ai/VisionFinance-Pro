from dataclasses import dataclass
from typing import Optional

# Re-use the Regime logic
# In a real app we might put MarketRegime in a shared 'constants.py'
# For now, we redefine or import. Let's import to be clean.
from quant_core.regimes.detectors.regime import MarketRegime

@dataclass
class SystemState:
    """Snapshot of the system's brain at any given day."""
    date: str
    regime: str
    days_in_regime: int
    is_risk_allowed: bool
    comment: str

class StateEngine:
    def __init__(self):
        self.current_regime = MarketRegime.RANGING # Default start
        self.days_in_regime = 0
        self.cooldown_counter = 0 # Days to wait after a crash
        
    def update(self, date: str, new_regime: str) -> SystemState:
        """
        Updates the state based on today's new regime.
        Implements 'Hysteresis' (Resistance to change) to avoid fake signals.
        """
        
        comment = ""
        
        # 1. State Transition Logic
        if new_regime == self.current_regime:
            self.days_in_regime += 1
            comment = "Regime stable."
        else:
            # Regime Change!
            # Use a simple filter: Don't switch to TRENDING unless we have valid signal
            # But for safety, switch to VOLATILE immediately.
            
            if new_regime == MarketRegime.VOLATILE:
                # IMMEDIATE DANGER -> Switch instantly
                self.current_regime = new_regime
                self.days_in_regime = 1
                self.cooldown_counter = 5 # Penalty: No trading for 5 days after volatility spike
                comment = "Volatile Spike Detected! Engaging Safety Lock."
                
            elif self.current_regime == MarketRegime.VOLATILE:
                # Trying to recover from Crash...
                # Don't switch back instantly. Wait for cooldown.
                if self.cooldown_counter > 0:
                    self.cooldown_counter -= 1
                    comment = f"Recovering from crash... Cooldown: {self.cooldown_counter}"
                    # We stay in VOLATILE state essentially, or a 'RECOVERY' state
                else:
                    self.current_regime = new_regime
                    self.days_in_regime = 1
                    comment = "Coast is clear. Regime Normalized."
            else:
                # Normal Switch (Range <-> Trend)
                self.current_regime = new_regime
                self.days_in_regime = 1
                comment = f"Regime switched to {new_regime}"

        # 2. Risk Evaluation
        # Risk is allowed ONLY if:
        # - Not Volatile
        # - Not in Cooldown
        # - (Optional) Days in regime > 3 (Confirmation)
        
        is_risk_allowed = (
            self.current_regime != MarketRegime.VOLATILE 
            and self.cooldown_counter == 0
        )
        
        return SystemState(
            date=str(date),
            regime=self.current_regime,
            days_in_regime=self.days_in_regime,
            is_risk_allowed=is_risk_allowed,
            comment=comment
        )

if __name__ == "__main__":
    # Test Scenario
    engine = StateEngine()
    
    test_sequence = [
        ("2024-01-01", MarketRegime.TRENDING),
        ("2024-01-02", MarketRegime.TRENDING),
        ("2024-01-03", MarketRegime.VOLATILE), # CRASH!
        ("2024-01-04", MarketRegime.TRENDING), # Fake recovery
        ("2024-01-05", MarketRegime.TRENDING),
        ("2024-01-06", MarketRegime.TRENDING),
        ("2024-01-07", MarketRegime.TRENDING),
        ("2024-01-08", MarketRegime.TRENDING),
        ("2024-01-09", MarketRegime.TRENDING), # Should be safe now
    ]
    
    print(f"{'DATE':<12} | {'INPUT':<10} | {'STATE':<10} | {'RISK?':<6} | {'COMMENT'}")
    print("-" * 70)
    
    for date, input_regime in test_sequence:
        state = engine.update(date, input_regime)
        risk_icon = "✅" if state.is_risk_allowed else "⛔"
        print(f"{state.date:<12} | {input_regime:<10} | {state.regime:<10} | {risk_icon:<6} | {state.comment}")
