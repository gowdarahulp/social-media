"""Sentiment and emotion schemas."""
from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

EmotionType = Literal[
    "anger",
    "anxiety",
    "excitement",
    "joy",
    "sadness",
    "support",
    "opposition",
    "neutral"
]

StanceType = Literal["favorable", "against", "neutral", "none"]

class SentimentResult(BaseModel):
    polarity: float = Field(..., ge=-1.0, le=1.0, description="Polarity score from -1.0 (negative) to +1.0 (positive)")
    emotion: EmotionType = Field(..., description="Dominant emotion classification")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="Probabilities for each emotion")
    sarcasm: bool = Field(default=False, description="Flag indicating detected sarcasm or irony")
    sarcasm_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Sarcasm confidence score")
    stance: StanceType = Field(default="none", description="Stance towards extracted topic")
    language: str = Field(default="en", description="Identified language or code-mix mode")

class SentimentTimelinePoint(BaseModel):
    timestamp: datetime
    post_count: int
    avg_polarity: float
    emotions: Dict[str, int]
    sarcasm_rate: float
    topics: List[str] = Field(default_factory=list)
