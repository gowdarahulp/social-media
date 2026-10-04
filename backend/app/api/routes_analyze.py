"""API routes for Account/Handle Analysis across the 4 Pillars & Feedback."""
from fastapi import APIRouter, Query, Body
from backend.app.schemas.profile_analysis import ProfileAnalysisRequest, ProfileAnalysisResponse
from backend.app.services.profile_analyzer import ProfileIntelligenceService

router = APIRouter(prefix="/api/analyze", tags=["Account & Handle Intelligence"])

@router.post("/profile", response_model=ProfileAnalysisResponse)
def analyze_profile_post(request: ProfileAnalysisRequest):
    """Analyze any social media ID/handle across Sentiment, Demographics, Trends, and Network with Feedback."""
    return ProfileIntelligenceService.analyze_handle(
        platform=request.platform,
        raw_handle=request.handle,
        sample_size=request.sample_size
    )

@router.get("/profile", response_model=ProfileAnalysisResponse)
def analyze_profile_get(
    handle: str = Query(..., description="Social handle or channel ID, e.g. @tech_lead_arjun or @elonmusk"),
    platform: str = Query(default="x", description="Social platform: x, telegram, reddit, youtube, instagram"),
    sample_size: int = Query(default=50, ge=10, le=200)
):
    """GET endpoint to analyze any social media ID/handle."""
    return ProfileIntelligenceService.analyze_handle(
        platform=platform,
        raw_handle=handle,
        sample_size=sample_size
    )
