# PROJECT CONTRACT - Financial-Gemi-Analyst

**Objective:** Build a robust, regime-aware financial analysis system. "Don't lose money" > "Make money".

## 🚧 CRITICAL CONSTRAINTS (DO NOT BREAK)

1.  **NO Reinforcement Learning (RL):** We are not building a black box.
2.  **NO Tick/Minute Data:** Daily (OHLCV) timeframe only. Avoid microstructure noise.
3.  **NO LLM Signals:** Gemini DOES NOT predict price. It only explains context.
4.  **NO "Accuracy" Obsession:** We optimize for Sharpe Ratio and Max Drawdown, not directional accuracy.
5.  **Risk First:** The Risk Layer has veto power over the Signal Layer.
6.  **Action = Null:** "No Trade" is a valid and often preferred action.

## ✅ REQUIRED FEATURES

*   **Regime Detection:** Must clearly output `TREND`, `RANGE`, or `HIGH_VOL`.
*   **Volatility Guard:** System must shut down (size=0) during volatility spikes.
*   **Explanation:** Every trade must have a "Why" (even if simple).

Signed,
*The Architecture Team*
