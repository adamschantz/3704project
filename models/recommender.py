from abc import ABC, abstractmethod

class RecommendationStrategy(ABC):
    @abstractmethod
    def recommend(self, user_data):
        pass

class SurveyRecommender(RecommendationStrategy):
    def recommend(self, user_data):
        return ["Chess Club", "Robotics Club"]

class RecommenderContext:
    def __init__(self, strategy: RecommendationStrategy):
        self.strategy = strategy

    def get_recommendations(self, user_data):
        return self.strategy.recommend(user_data)