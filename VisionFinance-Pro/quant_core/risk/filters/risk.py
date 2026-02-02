import numpy as np

class RiskManager:
    def __init__(self, target_vol=0.20, max_leverage=1.5):
        self.target_vol = target_vol # Increased to 20% for Equities
        self.max_leverage = max_leverage # Allow 1.5x leverage for high conviction
        
    def calculate_size(self, signal_strength: float, current_volatility: float, is_risk_allowed: bool) -> float:
        """
        Determines the Position Size (0.0 to 1.0).
        
        Args:
            signal_strength: 0.0 to 1.0 (How confident is the signal?)
            current_volatility: Annualized volatility (e.g., 0.20 for 20%)
            is_risk_allowed: Boolean from StateEngine
            
        Returns:
            Float representing the % of capital to deploy.
        """
        
        # 1. Hard Veto (The "Check Engine" Light)
        if not is_risk_allowed:
            return 0.0
            
        if current_volatility <= 0.001: # Avoid division by zero
            return 0.0

        # 2. Volatility Targeting (The "Shock Absorber")
        # Formula: (Target Vol / Current Vol) 
        # If market is calm (10% vol) and we want 20% risk -> Size = 2.0x (Capped at 1.0)
        # If market is crazy (40% vol) and we want 20% risk -> Size = 0.5x
        vol_scalar = self.target_vol / current_volatility
        
        # 3. Kelly Logic (The "Gambler's Math")
        # We assume a fixed Win Rate advantage for now (e.g. 5% edge)
        # In a generic naive model, we just scale by signal confidence.
        # Size = Vol_Scalar * Confidence
        
        raw_size = vol_scalar * signal_strength
        
        # 4. Safety Caps
        # Never exceed Max Leverage
        final_size = min(raw_size, self.max_leverage)
        
        # Round to 2 decimals for clean logging
        return round(max(0.0, final_size), 2)

if __name__ == "__main__":
    # Test Scenarios
    rm = RiskManager(target_vol=0.15) # We want 15% risk profile
    
    scenarios = [
        # (Signal Strength, Volatility, Allowed?)
        (1.0, 0.10, True),  # Strong Signal, Calm Market -> Should be BIG size
        (1.0, 0.30, True),  # Strong Signal, Crazy Market -> Should be SMALL size
        (0.5, 0.10, True),  # Weak Signal, Calm Market -> Medium size
        (1.0, 0.10, False), # Strong Signal, but StateEngine says NO -> ZERO
    ]
    
    print(f"{'SIGNAL':<8} | {'VOL %':<8} | {'ALLOWED?':<8} | {'SIZE (% of Capital)'}")
    print("-" * 50)
    
    for sig, vol, allowed in scenarios:
        size = rm.calculate_size(sig, vol, allowed)
        print(f"{sig:<8} | {int(vol*100):<6}% | {str(allowed):<8} | {int(size*100)}%")
