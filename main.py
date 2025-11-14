from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from controllers.main_controller import get_recommendations_for_request

# Pydantic models (request/response schemas)
class RecommendationRequest(BaseModel):
    interests: str  # e.g., "engineering, robotics, community service, basketball"


class ClubRecommendation(BaseModel):
    name: str | None = None
    shortName: str | None = None
    summary: str | None = None


class RecommendationsResponse(BaseModel):
    recommendations: List[ClubRecommendation]


# FastAPI app setup

app = FastAPI(
    title="Club Match AI API",
    version="0.1.0",
    description="Backend API for recommending clubs and events to VT students.",
)

# Allow localhost frontends to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Checks if endpoints are working
@app.get("/api/v1/health")
def health_check() -> Dict[str, bool]:
    """Simple health endpoint used for quick checks."""
    return {"ok": True}


@app.post("/api/v1/recommend", response_model=RecommendationsResponse)
def recommend(payload: RecommendationRequest) -> RecommendationsResponse:
    """
    Core Club Match AI endpoint.

    Example request JSON:
        { "interests": "engineering, robotics, community service, basketball" }

    Example response JSON:
        {
          "recommendations": [
            { "name": "...", "shortName": "...", "summary": "..." },
            ...
          ]
        }
    """
    user_data: Dict[str, Any] = payload.model_dump()
    recs = get_recommendations_for_request(user_data)
    return RecommendationsResponse(recommendations=recs)
