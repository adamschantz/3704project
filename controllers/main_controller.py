# from flask import Blueprint, render_template, request

# main_blueprint = Blueprint('main', __name__)

from models.recommender import RecommenderContext, SurveyRecommender

def handle_user_input(user_data):
    recommender = RecommenderContext(SurveyRecommender())
    recs = recommender.get_recommendations(user_data)
    print("Recommended Clubs:", recs)

#simulate user input
if __name__ == "__main__":
    handle_user_input({"interests": "engineering"})