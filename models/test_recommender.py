import pytest
from unittest.mock import patch, mock_open
from recommender import SurveyRecommender, RecommenderContext

MOCK_CLUB_DATA = {
    "1": {
        "name": "Robotics Club",
        "shortName": "Robotics",
        "summary": "We build cool robots.",
        "description_html": "Engineering, robotics, AI."
    },
    "2": {
        "name": "Art Club",
        "shortName": "Art",
        "summary": "Painting and sculpting.",
        "description_html": "We draw, paint, and create art."
    },
    "3": {
        "name": "Chess Club",
        "shortName": "Chess",
        "summary": "Competitive chess.",
        "description_html": "Strategy games and tournaments."
    }
}


def test_load_clubs_success():
    mock_json = '{"1": {"name": "Test Club"}}'
    with patch("builtins.open", mock_open(read_data=mock_json)):
        rec = SurveyRecommender()
        assert rec.clubs == {"1": {"name": "Test Club"}}


def test_load_clubs_failure():
    with patch("builtins.open", side_effect=Exception("File error")):
        rec = SurveyRecommender()
        assert rec.clubs == {}  # Should return empty dict on failure


def test_calculate_match_score_basic():
    rec = SurveyRecommender()
    rec.clubs = MOCK_CLUB_DATA  # bypass file loading

    club = MOCK_CLUB_DATA["1"]
    score = rec._calculate_match_score(club, ["robot"])
    assert score > 0
    assert score == club["description_html"].lower().count("robot") + \
        club["summary"].lower().count("robot") + \
        club["name"].lower().count("robot")


def test_calculate_match_score_no_matches():
    rec = SurveyRecommender()
    rec.clubs = MOCK_CLUB_DATA

    club = MOCK_CLUB_DATA["2"]
    score = rec._calculate_match_score(club, ["engineering"])
    assert score == 0


def test_recommend_no_interests():
    rec = SurveyRecommender()
    rec.clubs = MOCK_CLUB_DATA

    results = rec.recommend({"interests": ""})
    assert results == []


def test_recommend_matching():
    rec = SurveyRecommender()
    rec.clubs = MOCK_CLUB_DATA

    results = rec.recommend({"interests": "robotics, art"})

    names = [c["name"] for c in results]

    assert "Robotics Club" in names
    assert "Art Club" in names
    assert len(results) >= 2


def test_recommend_sorted_by_score():
    rec = SurveyRecommender()
    rec.clubs = MOCK_CLUB_DATA

    results = rec.recommend({"interests": "art"})

    assert results[0]["name"] == "Art Club"


def test_recommend_limit_to_top_10():
    rec = SurveyRecommender()

    # Create 20 mock clubs that all match
    rec.clubs = {
        str(i): {
            "name": f"Club {i}",
            "shortName": f"C{i}",
            "summary": "test",
            "description_html": "keyword"
        }
        for i in range(20)
    }

    results = rec.recommend({"interests": "keyword"})
    assert len(results) == 10  # Should return top 10 only


def test_recommender_context_calls_strategy():
    class MockStrategy:
        def recommend(self, data):
            return ["OK"]

    context = RecommenderContext(MockStrategy())
    assert context.get_recommendations({"x": 1}) == ["OK"]
