# from flask import Blueprint, render_template, request

# main_blueprint = Blueprint('main', __name__)

from typing import List, Dict, Any
from models.recommender import RecommenderContext, SurveyRecommender

def get_recommendations_for_request(user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get club recommendations based on user interests."""
    recommender = RecommenderContext(SurveyRecommender())
    return recommender.get_recommendations(user_data)

def handle_user_input(user_data):
    recs = get_recommendations_for_request(user_data)
    print("Recommended Clubs:", recs)

#simulate user input
if __name__ == "__main__":
    handle_user_input({"interests": "engineering, robotics"})