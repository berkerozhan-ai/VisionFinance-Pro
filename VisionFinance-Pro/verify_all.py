import yfinance as yf
import pandas as pd

def safe_print(msg):
    try:
        print(msg)
    except:
        pass

def check_price(ticker, name):
    try:
        df = yf.download(ticker, period="1d", progress=False, auto_adjust=True)
        if not df.empty:
            price = df['Close'].iloc[-1]
            safe_print(f"{name} ({ticker}): {price:,.2f}")
        else:
            safe_print(f"{name} ({ticker}): NO DATA")
    except Exception as e:
        safe_print(f"{name} ({ticker}): ERROR {e}")

safe_print("--- PRICE VERIFICATION CHECK ---")

# 1. Commodities (User focus)
check_price("GC=F", "Gold (Altın)")
check_price("SI=F", "Silver (Gümüş)")
check_price("HG=F", "Copper (Bakır)")
check_price("CL=F", "Crude Oil (Petrol)")

# 2. BIST (Check for ~300-400 TL)
check_price("THYAO.IS", "THYAO")
check_price("GARAN.IS", "GARAN")

# 3. US Tech (Check for ~$230 etc)
check_price("AAPL", "Apple")
check_price("NVDA", "Nvidia")

# 4. Crypto (Check for ~$100k)
check_price("BTC-USD", "Bitcoin")

# 5. UK (Potential Pence vs Pound issue)
# LSE stocks often quoted in pence (GBp) instead of pounds (GBP)
check_price("HSBA.L", "HSBC (UK)")
check_price("SHEL.L", "Shell (UK)")
