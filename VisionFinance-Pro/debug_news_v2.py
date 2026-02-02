import requests
import feedparser
import urllib.parse
from datetime import datetime

t = "NVDA"
clean_ticker = t.replace("-USD", "").replace(".IS", "")
query = f"{clean_ticker} stock"
encoded_query = urllib.parse.quote(query)
url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

print(f"Testing URL: {url}")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {resp.status_code}")
    print(f"Content Type: {resp.headers.get('Content-Type')}")
    print(f"Raw Content (First 500 chars):\n{resp.text[:500]}")
    
    feed = feedparser.parse(resp.content)
    print(f"\nFeed Entries: {len(feed.entries)}")
    if feed.entries:
        print(f"First Entry: {feed.entries[0].title}")
    else:
        print("No entries found.")
        if hasattr(feed, 'bozo_exception'):
            print(f"Bozo Exception: {feed.bozo_exception}")
            
except Exception as e:
    print(f"Request Error: {e}")
