"""Schemas for Handle/Account Intelligence Analysis across the 4 Pillars & Feedback."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ProfileAnalysisRequest(BaseModel):
    platform: str = Field(default="x", description="Social platform: x, telegram, reddit, youtube, instagram")
    handle: str = Field(..., description="Social media username, handle or channel ID, e.g. @tech_lead_arjun or @elonmusk")
    sample_size: int = Field(default=50, ge=10, le=200)

class ProfileSentimentSummary(BaseModel):
    overall_sentiment: str = Field(description="Net sentiment: Highly Favorable, Moderately Positive, Polarized, Critical")
    avg_polarity: float = Field(description="Polarity score from -1.0 to +1.0")
    dominant_emotion: str = Field(description="Primary emotion: joy, excitement, anger, anxiety, support, etc.")
    emotion_breakdown: Dict[str, float] = Field(description="Percentage distribution across 8 emotions")
    sarcasm_rate: float = Field(description="Percentage of audience discourse flagged as sarcastic/ironic")
    audience_feeling_summary: str = Field(description="What are people feeling? Summary paragraph")

class ProfileDemographicsSummary(BaseModel):
    audience_archetype: str = Field(description="Primary audience persona, e.g. Senior Tech Architects & AI Founders")
    top_geographies: List[Dict[str, Any]] = Field(description="Country/state distribution")
    top_age_groups: List[Dict[str, Any]] = Field(description="Age bracket percentages")
    top_languages: List[Dict[str, Any]] = Field(description="Language distribution including Hinglish")
    primary_interests: List[Dict[str, Any]] = Field(description="Professional interest categories")
    k_anonymity_verified: bool = Field(default=True, description="Strict k >= 20 cohort threshold enforced")
    who_they_are_summary: str = Field(description="Who are the people? Summary paragraph")

class ProfileTrendsSummary(BaseModel):
    key_topics: List[str] = Field(description="Dominant recurring themes")
    top_hashtags: List[str] = Field(description="Frequently co-occurring hashtags")
    viral_velocity_score: float = Field(description="Engagement & viral velocity rate")
    forecast_outlook_48h: str = Field(description="Projected 48-hour volume and engagement trend")
    what_they_talk_about_summary: str = Field(description="What are they talking about? Summary paragraph")

class ProfileNetworkSummary(BaseModel):
    reach_tier: str = Field(description="KOL tier: Macro Authority, Niche Thought Leader, Rising Community Hub")
    pagerank_percentile: float = Field(description="Authority rank compared to total network")
    community_role: str = Field(description="Role: Cluster Core, Inter-community Bridge, Broadcast Node")
    cascade_spread_rate: str = Field(description="Propagation speed: Viral Multiplier, Organic Word-of-Mouth, Echoed")
    how_info_spreads_summary: str = Field(description="How does information spread? Summary paragraph")

class ProfileFeedbackReport(BaseModel):
    health_score: int = Field(ge=0, le=100, description="Overall audience sentiment and engagement health score (0-100)")
    status_label: str = Field(description="e.g. Excellent Audience Affinity, High Controversy Risk, Rapid Organic Growth")
    strengths: List[str] = Field(description="Key competitive strengths and positive audience signals")
    risk_flags: List[str] = Field(description="Identified audience friction points, sarcasm spikes, or churn risks")
    actionable_recommendations: List[str] = Field(description="Concrete strategic recommendations for content & community")
    executive_summary: str = Field(description="Comprehensive strategic feedback report")

class ProfileAnalysisResponse(BaseModel):
    platform: str
    handle: str
    user_hash: str
    analyzed_posts_count: int
    analyzed_at: datetime
    sentiment: ProfileSentimentSummary
    demographics: ProfileDemographicsSummary
    trends: ProfileTrendsSummary
    network: ProfileNetworkSummary
    feedback: ProfileFeedbackReport
    sample_posts: List[Dict[str, Any]] = Field(default_factory=list)
