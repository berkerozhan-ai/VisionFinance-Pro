import feedparser
import pandas as pd
from datetime import datetime
import os

class NewsScraper:
    def __init__(self):
        # Expanded Sources: Finance + Geopolitics + Military + TR Local
        self.feeds = {
            # --- GLOBAL FINANCE ---
            "Yahoo Finance": {"url": "https://finance.yahoo.com/news/rssindex", "category": "FINANCE"},
            "CNBC Finance": {"url": "https://www.cnbc.com/id/10000664/device/rss/rss.html", "category": "FINANCE"},
            "Reuters Business": {"url": "https://rss.reutersagency.com/public/us/businessnews", "category": "FINANCE"},
            
            # --- GLOBAL GEOPOLITICS ---
            "Reuters World": {"url": "https://rss.reutersagency.com/public/us/world", "category": "GEOPOLITICS"},
            "BBC World": {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "GEOPOLITICS"},
            "Defense News": {"url": "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml", "category": "MILITARY"},
            
            # --- TURKEY LOCAL (TR) ---
            "Bloomberg HT": {"url": "https://www.bloomberght.com/rss", "category": "TR_MARKET"},
            "Anadolu Ajansı (Eko)": {"url": "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", "category": "TR_ECONOMY"},
            "Investing TR": {"url": "https://tr.investing.com/rss/news.rss", "category": "TR_MARKET"}
        }
        
    def fetch_news(self, limit_per_source=5) -> pd.DataFrame:
        """
        Fetches latest news from all configured RSS feeds.
        Returns a DataFrame with columns: [Date, Title, Summary, Source, Category, Link]
        """
        all_news = []
        
        print("--- FETCHING NEWS (Finance & Geopolitics) ---")
        
        for source, info in self.feeds.items():
            url = info['url']
            category = info['category']
            
            try:
                print(f"Reading {source} ({category})...")
                feed = feedparser.parse(url)
                
                count = 0
                for entry in feed.entries:
                    if count >= limit_per_source:
                        break
                        
                    # Parse Date
                    try:
                        pub_date = entry.published
                    except:
                        pub_date = str(datetime.now())
                        
                    news_item = {
                        "Date": pub_date,
                        "Title": entry.title,
                        "Summary": getattr(entry, 'summary', ''),
                        "Source": source,
                        "Category": category,
                        "Link": entry.link
                    }
                    all_news.append(news_item)
                    count += 1

                    
            except Exception as e:
                print(f"Error fetching {source}: {e}")
                
        df = pd.DataFrame(all_news)
        print(f"Successfully fetched {len(df)} articles.")
        return df

    def save_to_parquet(self, df):
        if df.empty:
            return
            
        # Create news directory
        save_dir = os.path.join("quant_core", "data", "news")
        os.makedirs(save_dir, exist_ok=True)
        
        # Save with timestamp to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_snapshot_{timestamp}.parquet"
        path = os.path.join(save_dir, filename)
        
        df.to_parquet(path)
        print(f"Saved news to {path}")

if __name__ == "__main__":
    scraper = NewsScraper()
    df = scraper.fetch_news(limit_per_source=3)
    
    if not df.empty:
        print("\n--- LATEST HEADLINES ---")
        for i, row in df.iterrows():
            print(f"[{row['Source']}] {row['Title']}")
        
        # Save for later use by RAG
        scraper.save_to_parquet(df)
