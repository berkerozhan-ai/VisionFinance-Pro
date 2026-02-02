import re

class SemanticAnalyzer:
    """
    A rule-based semantic engine that simulates 'reading' financial news.
    It understands the RELATIONSHIP between an ENTITY (Inflation, Profit) 
    and an ACTION (Rose, Fell) to determine sentiment.
    
    It does NOT just count words. It parses logic.
    """
    
    def __init__(self):
        # 1. Define Entities and their "Desired Direction" (1 = UP is Good, -1 = UP is Bad)
        self.ENTITIES = {
            'profit': 1, 'revenue': 1, 'growth': 1, 'dividends': 1, 'earnings': 1, 'guidance': 1,
            'employment': 1, 'jobs': 1, 'demand': 1, 'sales': 1, 
            'inflation': -1, 'unemployment': -1, 'tax': -1, 'debt': -1, 'rates': -1, 'fed hike': -1,
            'volatility': -1, 'loss': -1, 'risk': -1, 'tension': -1, 'war': -1
        }
        
        # 2. Define Actions and their Direction (1 = UP, -1 = DOWN)
        self.ACTIONS = {
            'rose': 1, 'increased': 1, 'soared': 1, 'jumped': 1, 'surged': 1, 'grew': 1, 'climb': 1, 'high': 1, 'record': 1,
            'fell': -1, 'dropped': -1, 'plunged': -1, 'decreased': -1, 'slid': -1, 'crash': -1, 'low': -1, 'cut': -1, 'missed': -1, 'loss': -1
        }
        
        # 3. Context Modifiers
        self.MODIFIERS = {
            'not': -1, 'despite': 0.5, 'but': 0.5, 'although': 0.5
        }

    def analyze_news_bundle(self, ticker: str, news_list: list) -> dict:
        """
        Reads a list of news and builds a 'Mental Model' of the market.
        """
        total_score = 0
        thoughts = []
        
        for news in news_list:
            score, reasoning = self._parse_sentence(news)
            if score != 0:
                total_score += score
                thoughts.append(reasoning)
                
        # Final "Thought Process"
        if total_score > 0:
            conclusion = "Pozitif veri akisi baskin."
            sentiment = "BULLISH"
        elif total_score < 0:
            conclusion = "Negatif veri akisi baskin."
            sentiment = "BEARISH"
        else:
            conclusion = "Veriler celiskili veya notr."
            sentiment = "NEUTRAL"
            
        return {
            "sentiment": sentiment,
            "score": total_score,
            "thoughts": thoughts,
            "conclusion": conclusion
        }

    def _parse_sentence(self, text: str) -> tuple:
        """
        Parses a single sentence to find (Entity + Action).
        Returns (Score, Reasoning String)
        """
        text = text.lower()
        score = 0
        found_entity = None
        found_action = None
        
        # 1. Find Entity
        for entity in self.ENTITIES:
            if entity in text:
                found_entity = entity
                break
                
        if not found_entity:
            return 0, ""
            
        # 2. Find Action
        for action, direction in self.ACTIONS.items():
            if action in text:
                found_action = action
                action_dir = direction
                break
        
        if not found_action:
            # Maybe the entity itself carries sentiment (e.g. "War detected")
            # If no action, we assume the entity's mere presence checking against a default context? 
            # For now, simplistic:
             return 0, ""

        # 3. Calculate Logic
        # Result = Entity_Preference * Action_Direction
        # Example: Inflation (-1) * Dropped (-1) = +1 (GOOD)
        # Example: Profit (+1) * Dropped (-1) = -1 (BAD)
        
        logic_score = self.ENTITIES[found_entity] * action_dir * 10 
        
        # 4. Construct "Thought"
        if logic_score > 0:
            reason = f"Olumlu: '{found_entity}' ({found_action}) -> Piyasa icin IYI."
        else:
            reason = f"Olumsuz: '{found_entity}' ({found_action}) -> Piyasa icin KOTU."
            
        return logic_score, reason
