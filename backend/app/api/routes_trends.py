"""API routes for trending topics, burst velocity, and 24-72h forecasting."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.trends import TrendTopic, TrendForecast
from backend.app.trends import BurstDetector, TrendForecaster

router = APIRouter(prefix="/api/trends", tags=["Trends & Forecasting"])

@router.get("/rising", response_model=List[TrendTopic])
def get_rising_trends():
    return BurstDetector.detect_rising_trends()

@router.get("/forecast", response_model=TrendForecast)
def get_trend_forecast(
    topic: str = Query(..., description="Topic name or hashtag to forecast, e.g. #AIRevolution"),
    hours: int = Query(default=48, ge=12, le=72, description="Forecast horizon in hours (24-72h)")
):
    fcst = TrendForecaster.forecast_topic(topic_name=topic, forecast_hours=hours)
    if not fcst:
        raise HTTPException(status_code=404, detail=f"Insufficient history to forecast topic '{topic}'.")
    return fcst
