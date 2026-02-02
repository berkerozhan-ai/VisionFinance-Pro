import yfinance as yf

tickers = ["GC=F", "SI=F", "CL=F", "NG=F", "BZ=F", "PL=F", "PA=F"]

print("Testing Commodity Tickers...")
for t in tickers:
    try:
        df = yf.download(t, period="5d", progress=False)
        if not df.empty:
            print(f"[OK] {t}: {len(df)} rows")
        else:
            print(f"[FAIL] {t}: Empty")
    except Exception as e:
        print(f"[ERROR] {t}: {e}")
