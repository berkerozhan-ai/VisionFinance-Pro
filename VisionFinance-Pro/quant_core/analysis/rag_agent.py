import pandas as pd
import os
import json
from datetime import datetime
from textblob import TextBlob
from quant_core.data.news_fetcher import RSSFetcher
from quant_core.utils.localization import get_text

class RAGAgent:
    def __init__(self, api_key=None):
        self.rss = RSSFetcher()
        self.api_key = api_key

    def analyze_context(self, ticker, lang="Türkçe") -> dict:
        """
        Fetches REAL news and uses NLP (TextBlob) to calculate Sentiment Score.
        """
        print(f"--- AI ANALYST READING NEWS FOR {ticker} ---")
        
        # 1. Fetch Real News
        articles = self.rss.fetch_news(ticker)
        
        # 2. Semantic Analysis (NLP)
        polarities = []
        hits = []
        
        for art in articles:
            text = f"{art['title']} {art.get('summary', '')}"
            blob = TextBlob(text)
            
            # Polarity: -1.0 (Negative) to 1.0 (Positive)
            score = blob.sentiment.polarity
            polarities.append(score)
            
            # Annotate significant news
            if abs(score) > 0.1:
                label = f"🟢 {get_text('rag_bull', lang)}" if score > 0 else f"🔴 {get_text('rag_bear', lang)}"
                hits.append(f"{label} ({score:.2f}): {art['title']}")
            else:
                hits.append(f"⚪ {get_text('rag_neutr', lang)}: {art['title']}")
        
        # 3. Aggregate Score
        if polarities:
            avg_score = sum(polarities) / len(polarities)
            # Normalize to -1.0 to 1.0 range (TextBlob is already there, but let's amplify slightly)
            final_sentiment = max(min(avg_score * 2.0, 1.0), -1.0) # Amplify weak signals
        else:
            final_sentiment = 0.0
            hits.append(get_text('rag_no_data', lang))
        
        sent_label = get_text('rag_neutral', lang)
        if final_sentiment > 0.05: sent_label = get_text('rag_pos', lang)
        elif final_sentiment < -0.05: sent_label = get_text('rag_neg', lang)
        
        summary = get_text('rag_summary', lang).format(len(articles), sent_label)
        
        result = {
            "sentiment_score": final_sentiment,
            "summary": summary,
            "details": hits[:5], # Top 5 relevant headline strings (formatted)
            "articles": articles[:10], # Raw article objects for UI (Title, Link)
            "timestamp": str(datetime.now())
        }
        
        print(f"AI Sentiment: {final_sentiment:.2f}")
        return result

if __name__ == "__main__":
    agent = RAGAgent()
    analysis = agent.analyze_context("NVDA")
    print(json.dumps(analysis, indent=2))
