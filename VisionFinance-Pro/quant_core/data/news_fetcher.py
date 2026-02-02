import feedparser
import ssl
import urllib.parse
from datetime import datetime

# Fix SSL issue for some feeds
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

class RSSFetcher:
    """
    Fetches REAL-TIME news from Google News RSS (Most reliable aggregagor).
    """
    
    def __init__(self):
        # Google News RSS Search URL
        # hl=en-US&gl=US&ceid=US:en -> English/US
        # hl=tr-TR&gl=TR&ceid=TR:tr -> Turkish/TR
        self.base_url = "https://news.google.com/rss/search?q={query}&hl={lang}&gl={country}&ceid={country}:{lang}"
        
    def fetch_news(self, ticker, lang="en"):
        """
        Parses RSS feed and returns a list of dictionaries.
        """
        try:
            # 1. Construct Query
            # Clean ticker (remove -USD etc for better search)
            clean_ticker = ticker.replace("-USD", "").replace(".IS", "")
            
            query = f"{clean_ticker} stock"
            if "-USD" in ticker:
                query = f"{clean_ticker} crypto"
            elif ".IS" in ticker:
                query = f"{clean_ticker} hisse"
                lang = "tr" # Force TR for BIST
            
            # Encode URL
            encoded_query = urllib.parse.quote(query)
            
            # Params
            if lang == "tr":
                url = self.base_url.format(query=encoded_query, lang="tr-TR", country="TR")
            else:
                url = self.base_url.format(query=encoded_query, lang="en-US", country="US")
                
            print(f"Fetching News: {url}")
            
            # 2. Fetch with User-Agent (Critical for Google/Yahoo)
            import requests
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"RSS Request Failed: {resp.status_code}")
                return [{"title": f"News Fetch Failed ({resp.status_code})", "link": "#", "summary": "Connection blocked."}]
                
            # 3. Parse Content
            feed = feedparser.parse(resp.content)
            articles = []
            
            if not feed.entries:
                # Fallback: Maybe no "stock" keyword needed
                pass
            
            for entry in feed.entries[:10]: # Top 10 items
                # Google News puts the source in the title usually "Title - Source"
                # And the summary is often HTML.
                
                title = entry.title
                link = entry.link
                pubDate = entry.published if 'published' in entry else str(datetime.now())
                
                # HTML Summary cleaning (very basic)
                summary = ""
                if 'summary' in entry:
                    # Strip HTML tags
                    import re
                    clean = re.compile('<.*?>')
                    summary = re.sub(clean, '', entry.summary)
                
                articles.append({
                    'title': title,
                    'link': link,
                    'published': pubDate,
                    'summary': summary
                })
                
            if not articles:
                 return [{"title": f"No recent news found for {ticker}", "link": "#", "summary": "Try checking manual sources."}]
            
            return articles
            
        except Exception as e:
            print(f"News Fetch Error: {e}")
            return [{"title": "News Feed Error", "link": "#", "summary": str(e)}]

if __name__ == "__main__":
    fetcher = RSSFetcher()
    # Test
    for t in ["THYAO.IS", "BTC-USD", "NVDA"]:
        print(f"\n--- {t} ---")
        news = fetcher.fetch_news(t)
        for n in news[:2]:
            print(f"- {n['title']}")
