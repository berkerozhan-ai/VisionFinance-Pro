import pandas as pd
import numpy as np

from quant_core.utils.localization import get_text

class NarrativeEngine:
    """
    Ham verileri ve sinyalleri anlamlı, detaylı bir 'Deep Dive' raporuna dönüştüren modül.
    Profesyonel, şeffaf ve eğitici bir dil kullanır.
    """
    
    def __init__(self):
        pass
        
    def analyze_context(self, ticker: str, technical_state: dict, news_headlines: list = None, market_sentiment_score: float = 0.0, lang: str = "Türkçe") -> dict:
        """
        Teknik verileri, haber sentimentini ve risk parametrelerini birleştirerek detaylı rapor oluşturur.
        """
        
        # 1. Executive Summary (Yönetici Özeti)
        trend = technical_state.get('trend', 'NEUTRAL')
        score = technical_state.get('pattern_score', 0) # Assumes passed in tech state
        
        decision = get_text('decision_neutral', lang)
        if trend == "UP": decision = get_text('decision_pos', lang)
        if trend == "DOWN": decision = get_text('decision_neg', lang)
        
        # 2. Detailed Sections
        parts = []
        
        # --- HEADER ---
        parts.append(f"# {get_text('report_title', lang).format(ticker)}")
        parts.append(get_text('decision_label', lang).format(decision, trend))
        parts.append("---")
        
        # --- SECTION 1: Strategic Rationale (Stratejik Mantık) ---
        parts.append(get_text('strategic_logic_header', lang))
        if trend == "UP":
            parts.append(get_text('trend_analysis_up', lang))
        else:
            parts.append(get_text('trend_analysis_down', lang))
            
        vol_str = technical_state.get('volume_strength', 1.0)
        parts.append(get_text('vol_support', lang).format(vol_str) + 
                     (get_text('vol_strong', lang) if vol_str > 1.2 else get_text('vol_weak', lang)))

        # --- SECTION 2: AI & Sentiment (Piyasa Algısı) ---
        parts.append(get_text('ai_sentiment_header', lang))
        normalized_sent = market_sentiment_score # -1 to 1
        
        sentiment_text = get_text('sent_label_neutral', lang)
        if normalized_sent > 0.1: sentiment_text = get_text('sent_label_pos', lang)
        elif normalized_sent < -0.1: sentiment_text = get_text('sent_label_neg', lang)
        
        parts.append(get_text('global_news_score', lang).format(normalized_sent, sentiment_text))
        parts.append(get_text('ai_sent_desc', lang) + 
                     (get_text('ai_sent_bull', lang) if normalized_sent > 0 else get_text('ai_sent_bear', lang)))
        
        # --- SECTION 3: Risk Assessment (Risk Yönetimi) ---
        parts.append(get_text('risk_header', lang))
        parts.append(get_text('risk_desc', lang))
        parts.append(get_text('risk_advice', lang))
        
        # --- FOOTER ---
        advice = get_text('footer_advice', lang).format(trend, sentiment_text)
        if trend == "UP" and normalized_sent > -0.2:
            advice += get_text('advice_buy', lang)
        else:
            advice += get_text('advice_hold', lang)

        return {
            "story": "\n\n".join(parts),
            "advice": advice
        }
