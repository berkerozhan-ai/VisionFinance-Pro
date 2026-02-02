
import yfinance as yf

tickers = ["ENKAI.IS", "POL-USD", "UNI7083-USD", "SQ"]
for t in tickers:
    print(f"Testing {t}...")
    try:
        dat = yf.Ticker(t)
        hist = dat.history(period="5d")
        if not hist.empty:
            print(f"SUCCESS: {t} - {len(hist)} rows")
        else:
            print(f"FAIL: {t} - Empty")
            # Try finding symbol
    except Exception as e:
        print(f"ERROR: {t} - {e}")
