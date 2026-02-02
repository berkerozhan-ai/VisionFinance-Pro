import yfinance as yf
import pandas as pd
import os

# Configuration
# --- TICKER UNIVERSE (CATEGORIZED) ---
TICKER_UNIVERSE = {
    "ABD (USA)": {
        "Teknoloji (Mag 7+)": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "AVGO", "ORCL", "IBM", "INTC", "QCOM", "MU", "TSM", "ARM", "PLTR", "CRM", "ADBE", "NFLX"],
        "Finans": ["JPM", "BAC", "C", "WFC", "GS", "MS", "V", "MA", "AXP", "BLK", "SPGI", "MCO", "PYPL", "SQ", "COIN", "HOOD"],
        "Sanayi & Enerji": ["XOM", "CVX", "COP", "SLB", "EOG", "CAT", "DE", "GE", "BA", "LMT", "RTX", "HON", "MMM", "UNP", "UPS", "FDX"],
        "Tüketim & Sağlık": ["WMT", "TGT", "COST", "HD", "LOW", "MCD", "SBUX", "KO", "PEP", "PG", "CL", "LLY", "JNJ", "PFE", "MRK", "ABBV", "UNH", "TMO", "DHR"],
        "ETFs (Fonlar)": ["SPY", "QQQ", "DIA", "IWM", "VTI", "VEA", "EEM", "TLT", "USO", "UNG", "SMH", "XLK", "XLF", "XLE", "ARKK"]
    },
    "Türkiye (BIST)": {
        "BIST 30 & Devler": ["THYAO.IS", "KCHOL.IS", "SAHOL.IS", "SISE.IS", "TUPRS.IS", "EREGL.IS", "ASELS.IS", "BIMAS.IS", "ENKAI.IS", "FROTO.IS", "GARAN.IS", "AKBNK.IS", "ISCTR.IS", "YKBNK.IS"],
        "Bankacılık": ["VAKBN.IS", "HALKB.IS", "SKBNK.IS", "TSKB.IS", "ALBRK.IS"],
        "Sanayi & Enerji": ["ENJSA.IS", "ASTOR.IS", "SASA.IS", "HEKTS.IS", "TUKAS.IS", "PETKM.IS", "KRDMD.IS", "TTRAK.IS", "TOASO.IS", "OTKAR.IS", "AKSA.IS", "ALARK.IS", "SMRTG.IS", "EUPWR.IS", "GESAN.IS"],
        "Teknoloji & Büyüme": ["KONTR.IS", "MIATK.IS", "REEDR.IS", "YEOTK.IS", "SDTTR.IS", "PATEK.IS", "VBTYZ.IS", "ASELS.IS", "LOGO.IS"],
        "Gıda & Perakende": ["MGROS.IS", "SOKM.IS", "AEFES.IS", "CCOLA.IS", "ULKER.IS", "DOHOL.IS"]
    },
    "Avrupa & Global": {
        "Almanya (DAX)": ["SAP", "SIE.DE", "ALV.DE", "DTE.DE", "VOW3.DE", "BMW.DE", "BAS.DE", "BAYN.DE", "ADS.DE", "AIR.DE"],
        "İngiltere (FTSE)": ["HSBA.L", "SHEL.L", "BP.L", "AZN.L", "GSK.L", "ULVR.L", "BATS.L", "RIO.L", "GLEN.L", "VOD.L"],
        "Fransa & Diğer": ["MC.PA", "OR.PA", "TTE.PA", "SAN.PA", "KER.PA", "ASML", "NVO", "SONY", "TM", "BABA", "JD", "TSM"]
    },
    "Emtia (Commodities)": {
        "Değerli Madenler": ["GC=F", "SI=F", "PL=F", "PA=F"],
        "Enerji": ["CL=F", "NG=F", "BZ=F"]
    },
    "Kripto (7/24)": {
        "Majör": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD"],
        "Meme & Altcoin": ["DOGE-USD", "SHIB-USD", "AVAX-USD", "DOT-USD", "LINK-USD", "POL-USD", "UNI7083-USD", "LTC-USD", "ATOM-USD"]
    }
}

# --- TICKER NAMES (FRIENDLY DISPLAY) ---
TICKER_NAMES = {
    # Commodities
    "GC=F": "Altın (Gold)",
    "SI=F": "Gümüş (Silver)",
    "PL=F": "Platin",
    "PA=F": "Paladyum",
    "CL=F": "Ham Petrol (Crude Oil)",
    "NG=F": "Doğalgaz (Natural Gas)",
    "BZ=F": "Brent Petrol",
    # Crypto
    "BTC-USD": "Bitcoin (BTC)",
    "ETH-USD": "Ethereum (ETH)",
    "SOL-USD": "Solana (SOL)",
    "XRP-USD": "Ripple (XRP)",
    "AVAX-USD": "Avalanche (AVAX)",
    # Major Indices/ETFs
    "SPY": "S&P 500 (SPY)",
    "QQQ": "Nasdaq 100 (QQQ)",
    "GLD": "Altın Fonu (GLD)",
    # BIST
    "THYAO.IS": "Türk Hava Yolları",
    "KCHOL.IS": "Koç Holding",
    "GARAN.IS": "Garanti BBVA",
    "AKBNK.IS": "Akbank",
    "ASELS.IS": "Aselsan",
    "SISE.IS": "Şişecam",
    "BIMAS.IS": "BİM Mağazalar",
    "TUPRS.IS": "Tüpraş",
    "EREGL.IS": "Erdemir"
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "raw")
START_DATE = "2024-01-01" # Extend history for SMA200

def get_display_name(ticker):
    """Returns friendly name if available, else ticker."""
    return TICKER_NAMES.get(ticker, ticker)

def get_all_tickers():
    """Flattens the universe dict into a single list for data fetching."""
    all_tickers = []
    for region, sectors in TICKER_UNIVERSE.items():
        for sector, tickers in sectors.items():
            all_tickers.extend(tickers)
    return list(set(all_tickers)) # Remove duplicates if any

def fetch_single_ticker(ticker):
    """
    Fetches and saves data for a single ticker.
    Returns: (Success Boolean, Message String)
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    try:
       path = os.path.join(DATA_DIR, f"{ticker}.parquet")
       
       # Use threads=False for safety in UI loops
       # Added retries and different period fallback
       df = yf.download(ticker, start=START_DATE, progress=False, auto_adjust=True, interval="1d")
       
       if df.empty:
            # Try fetching without start date (max) if specific date fails
            df = yf.download(ticker, period="1y", progress=False, auto_adjust=True, interval="1d")
       
       if df.empty:
           return False, "No data found (Empty DataFrame)"
       
       if not df.empty:
           df = df.dropna()
           if isinstance(df.columns, pd.MultiIndex):
              if df.columns.nlevels > 1:
                   df = df.droplevel(1, axis=1)
           
           # Ensure index is datetime
           if not isinstance(df.index, pd.DatetimeIndex):
               df.index = pd.to_datetime(df.index)

           if len(df) < 5:
               return False, "Data found but too short (<5 rows)"

           df.to_parquet(path)
           return True, f"Saved {len(df)} rows"
           
    except Exception as e:
        return False, str(e)

def fetch_data():
    """
    Fetches daily OHLCV data for defined tickers.
    """
    all_tickers = get_all_tickers()
    print(f"Fetching data for {len(all_tickers)} assets starting from {START_DATE}...")
    
    import time
    success_count = 0
    
    for ticker in all_tickers:
        success, msg = fetch_single_ticker(ticker)
        if success:
            success_count += 1
        else:
            print(f"Err {ticker}: {msg}")
        time.sleep(0.1) # Polite delay
            
    print(f"Completed. {success_count}/{len(all_tickers)} updated.")

def get_realtime_quote(ticker):
    """
    Fetches the absolute latest 1-minute candle for live monitoring.
    Returns: (price, volume, change_pct) or None
    """
    try:
        # Fetch last 1 day, 1m interval, INCLUDE PREPOST (for morning sessions)
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True, prepost=True)
        if not df.empty:
            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                # Try to find the level with the ticker or just drop level 1
                if df.columns.nlevels > 1:
                    df = df.droplevel(1, axis=1)

            last_row = df.iloc[-1]
            price = float(last_row['Close'])
            volume = float(last_row['Volume'])
            
            # Simple change calc (vs open of valid session or previous close if available)
            # For 1m data, getting "daily change" is tricky without prev close. 
            # We will approximate with (Close - Open) of the minute for volatility or use session info if available.
            # Ideally yfinance Ticker info is better for "Change", but it's slow.
            # We stick to candle data for speed.
            return price, volume, df
        return None, None, None
    except Exception as e:
        print(f"Live fetch error: {e}")
        return None, None, None

def get_latest_daily_candle(ticker):
    """
    Fetches the single latest 'Daily' candle (today).
    Useful for appending to historical data to bridge the gap.
    """
    try:
        df = yf.download(ticker, period="1d", interval="1d", progress=False, auto_adjust=True)
        if not df.empty:
            # Flatten MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                if df.columns.nlevels > 1:
                    df = df.droplevel(1, axis=1)

            # Ensure index is datetime and normalized if needed (though typically YF returns date)
            return df
        return None
    except Exception:
        return None

def smart_load_ticker(ticker, strict=True):
    """
    Loads ticker data and auto-heals gaps if the data is stale.
    strict=True (Default): Checks freshness and fetches from web if needed.
    strict=False (Fast): Returns local data if exists, returns None if missing (no web call).
    
    Returns DataFrame or None.
    """
    path = os.path.join(DATA_DIR, f"{ticker}.parquet")
    
    # 1. If file missing
    if not os.path.exists(path):
        if not strict: return None # Fast mode: Skip fetch
        
        success, _ = fetch_single_ticker(ticker)
        if not success: return None
        if not os.path.exists(path): return None # Still missing
    
    try:
        df = pd.read_parquet(path)
        if df.empty: return None
        
        # 2. Check Latency (Only in Strict Mode)
        if strict:
            last_date = df.index[-1]
            if last_date.tz is not None: last_date = last_date.tz_localize(None)
            
            now = pd.Timestamp.now()
            days_diff = (now - last_date).days
            
            # If gap exists (e.g. yesterday's close is missing, or older)
            if days_diff >= 1:
                start_date = (last_date + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
                
                new_data = yf.download(ticker, start=start_date, progress=False, auto_adjust=True)
                
                # Fallback: If date-based fetch return empty (common on weekends or timezone mismatch),
                # try fetching valid recent history (last 5d) to ensure we have the latest Friday/Weekend candle.
                if new_data.empty:
                     new_data = yf.download(ticker, period="5d", progress=False, auto_adjust=True)

                if not new_data.empty:
                     # Flatten MultiIndex if present
                    if isinstance(new_data.columns, pd.MultiIndex):
                        new_data.columns = new_data.columns.droplevel(1)
                    
                    # Normalize Timezones
                    if new_data.index.tz is not None: new_data.index = new_data.index.tz_localize(None)
                    if df.index.tz is not None: df.index = df.index.tz_localize(None)
                    
                    # Combine
                    combined = pd.concat([df, new_data])
                    # Dedup (Keep last)
                    combined = combined[~combined.index.duplicated(keep='last')]
                    combined = combined.sort_index()
                    
                    # Auto-Save (Cache Update)
                    combined.to_parquet(path)
                    return combined
                
        return df
        
    except Exception as e:
        print(f"Smart Load Warning for {ticker}: {e}")
        # If read fails (corrupt file), delete it so next run fixes it
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f"Deleted corrupt file: {path}")
            except:
                pass
        return None

if __name__ == "__main__":
    fetch_data()
