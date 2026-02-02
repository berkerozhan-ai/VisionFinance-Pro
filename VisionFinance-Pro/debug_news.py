import feedparser
import ssl
import requests

# Force SSL fix
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def test_feed(url):
    print(f"Testing URL: {url}")
    try:
        # Method 1: Direct Feedparser
        d = feedparser.parse(url)
        print(f"Status: {d.get('status', 'Unknown')}")
        if d.entries:
            print(f"✅ Success! Found {len(d.entries)} entries.")
            print(f"Title: {d.entries[0].title}")
            return True
        else:
            print(f"❌ No entries found. Feed might be empty or blocked.")
            if 'bozo_exception' in d:
                print(f"Exception: {d.bozo_exception}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_google_news(ticker):
    # Google News RSS usually works better
    url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    print(f"\nTesting Google News for {ticker}...")
    return test_feed(url)

if __name__ == "__main__":
    print("--- DIAGNOSTIC START ---")
    
    # 1. Test Yahoo (Existing)
    print("\n[1] Testing Yahoo Finance (AAPL)...")
    test_feed("https://finance.yahoo.com/rss/headline?s=AAPL")
    
    # 2. Test Google News (Alternative)
    print("\n[2] Testing Google News (AAPL)...")
    test_google_news("AAPL")
    
    # 3. Test General Crypto
    print("\n[3] Testing Cointelegraph...")
    test_feed("https://cointelegraph.com/rss")
