import yfinance as yf
import sys

# Windows console encoding fix attempt (or just avoid printing)
def safe_print(msg):
    try:
        print(msg)
    except:
        print(msg.encode('ascii', 'ignore').decode('ascii'))

def get_currency_symbol_desc(ticker):
    if ticker.endswith(".IS"): return "TRY (TL)"
    if ticker.endswith(".DE") or ticker.endswith(".PA"): return "EUR"
    if ticker.endswith(".L"): return "GBP"
    return "USD"

print("--- Testing Currency Logic (Descriptions) ---")
print(f"THYAO.IS: {get_currency_symbol_desc('THYAO.IS')}")
print(f"AAPL: {get_currency_symbol_desc('AAPL')}")

print("\n--- Testing Gold Tickers ---")
try:
    print("Fetching GC=F (Gold Futures)...")
    gc = yf.Ticker("GC=F")
    hist_gc = gc.history(period="1d")
    if not hist_gc.empty:
        print(f"GC=F Price: {hist_gc['Close'].iloc[-1]}")
    else:
        print("GC=F: No data")

    print("Fetching XAUUSD=X (Gold Spot)...")
    xau = yf.Ticker("XAUUSD=X")
    hist_xau = xau.history(period="1d")
    if not hist_xau.empty:
        print(f"XAUUSD=X Price: {hist_xau['Close'].iloc[-1]}")
    else:
        print("XAUUSD=X: No data")

except Exception as e:
    print(f"Error: {e}")
