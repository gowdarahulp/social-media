"""API routes for multi-dimensional sentiment timeline and evaluation metrics."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query
from backend.app.schemas.sentiment import SentimentTimelinePoint
from backend.app.nlp import get_sentiment_timeline_aggregation, evaluate_sentiment_engine

router = APIRouter(prefix="/api/sentiment", tags=["Sentiment & Emotion"])

@router.get("/timeline", response_model=List[SentimentTimelinePoint])
def get_sentiment_timeline(
    topic: Optional[str] = Query(default=None, description="Filter timeline by topic"),
    bucket: str = Query(default="hour", pattern="^(hour|day)$", description="Aggregation bucket: hour or day"),
    from_date: Optional[datetime] = Query(default=None, alias="from"),
    to_date: Optional[datetime] = Query(default=None, alias="to")
):
    return get_sentiment_timeline_aggregation(
        topic=topic,
        start_time=from_date,
        end_time=to_date,
        bucket=bucket
    )

@router.get("/evaluation")
def get_sentiment_model_evaluation() -> Dict[str, Any]:
    return evaluate_sentiment_engine()
