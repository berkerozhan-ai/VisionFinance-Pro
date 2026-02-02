
import yfinance as yf

tickers = ["SMRTG.IS", "MATIC-USD", "SQ"]
for t in tickers:
    print(f"Testing {t}...")
    try:
        dat = yf.Ticker(t)
        hist = dat.history(period="5d")
        if not hist.empty:
            print(f"SUCCESS: {t} - {len(hist)} rows")
        else:
            print(f"FAIL: {t} - Empty")
    except Exception as e:
        print(f"ERROR: {t} - {e}")
