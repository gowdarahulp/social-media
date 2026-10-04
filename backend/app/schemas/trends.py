"""Trending topics and forecasting schemas."""
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class TrendTopic(BaseModel):
    topic_id: str
    name: str
    hashtags: List[str]
    keywords: List[str]
    total_volume: int
    velocity: float = Field(description="Posts per hour rate")
    acceleration: float = Field(description="Rate of velocity change")
    unique_users: int
    trend_score: float = Field(description="Velocity * Acceleration * UniqueUserSpread")
    status: Literal["rising", "peaked", "decaying", "stable"]
    dominant_sentiment: str = "neutral"
    first_seen: datetime
    last_seen: datetime

class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_volume: float
    lower_bound_80: float
    upper_bound_80: float
    lower_bound_95: float
    upper_bound_95: float

class TrendForecast(BaseModel):
    topic_id: str
    name: str
    method: str = "Holt-Winters Exponential Smoothing + Burst Detection"
    history: List[dict]
    forecast: List[ForecastPoint]
