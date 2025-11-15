from abc import ABC, abstractmethod
import json
import os
from typing import List, Dict, Any

class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, user_data):
        pass

class SurveyRecommender(RecommendationStrategy):
    def __init__(self):
        # Load club data on initialization
        self.clubs = self._load_clubs()
    
    def _load_clubs(self) -> Dict[str, Any]:
        """Load club data from JSON file."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data_collection',
            'gobblerconnect_clubs.json'
        )
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading clubs: {e}")
            return {}
    
    def _calculate_match_score(self, club: Dict[str, Any], keywords: List[str]) -> int:
        """Calculate how well a club matches the user's interests."""
        score = 0
        searchable_text = (
            f"{club.get('name', '')} "
            f"{club.get('summary', '')} "
            f"{club.get('description_html', '')}"
        ).lower()
        
        for keyword in keywords:
            if keyword in searchable_text:
                score += searchable_text.count(keyword)
        
        return score
    
    def recommend(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match user interests with clubs using keyword matching."""
        interests = user_data.get('interests', '')
        if not interests:
            return []
        
        # Parse interests into keywords
        keywords = [k.strip().lower() for k in interests.split(',')]
        
        # Score each club
        scored_clubs = []
        for club_id, club in self.clubs.items():
            score = self._calculate_match_score(club, keywords)
            if score > 0:
                scored_clubs.append((score, club))
        
        # Sort by score (highest first) and return top 10
        scored_clubs.sort(reverse=True, key=lambda x: x[0])
        
        return [
            {
                'name': club.get('name'),
                'shortName': club.get('shortName'),
                'summary': club.get('summary')
            }
            for _, club in scored_clubs[:10]
        ]

class RecommenderContext:
    def __init__(self, strategy: RecommendationStrategy):
        self.strategy = strategy

    def get_recommendations(self, user_data):
        return self.strategy.recommend(user_data)