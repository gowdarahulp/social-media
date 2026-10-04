"""Tests for topic modeling, burst detection, and Holt-Winters forecasting."""
import pytest
from backend.app.trends import TopicModeler, BurstDetector, TrendForecaster
from backend.app.connectors.replay import ReplayConnector
from backend.app.db.repository import PostRepository

def test_topic_modeler_extraction():
    text = "Exciting progress in #AIRevolution and #SustainableTech reported today!"
    tags = TopicModeler.extract_hashtags(text)
    assert "#AIRevolution" in tags
    assert "#SustainableTech" in tags

    docs = {
        "AI": ["transformers attention heads deep neural networks foundation models", "machine learning reasoning benchmark"],
        "Climate": ["solar energy decarbonization grid battery storage circular economy", "wind turbines renewable power"]
    }
    kws = TopicModeler.extract_keywords_ctf_idf(docs, top_k=3)
    assert len(kws["AI"]) > 0
    assert len(kws["Climate"]) > 0

@pytest.mark.anyio
async def test_burst_detection_and_forecasting():
    PostRepository.clear_all()
    # Ingest full replay dataset
    connector = ReplayConnector()
    posts = await connector.fetch(limit=380)
    for p in posts:
        PostRepository.insert_post(p)

    # 1. Burst Detection
    rising = BurstDetector.detect_rising_trends()
    assert len(rising) >= 3
    # Verify ranked by trend_score
    scores = [t.trend_score for t in rising]
    assert scores == sorted(scores, reverse=True)
    assert rising[0].velocity > 0
    assert rising[0].unique_users > 0

    # 2. Forecasting
    top_topic = rising[0].name
    fcst = TrendForecaster.forecast_topic(top_topic, forecast_hours=48)
    assert fcst is not None
    assert len(fcst.forecast) == 48
    assert len(fcst.history) > 0
    
    # Verify confidence intervals
    pt_early = fcst.forecast[0]
    pt_late = fcst.forecast[-1]
    
    # 80% and 95% bounds check
    assert pt_early.lower_bound_80 <= pt_early.predicted_volume <= pt_early.upper_bound_80
    assert pt_early.lower_bound_95 <= pt_early.lower_bound_80
    assert pt_early.upper_bound_95 >= pt_early.upper_bound_80
    assert pt_early.lower_bound_95 >= 0.0
    
    # Confidence interval spreads widen into the future
    spread_early = pt_early.upper_bound_95 - pt_early.lower_bound_95
    spread_late = pt_late.upper_bound_95 - pt_late.lower_bound_95
    assert spread_late >= spread_early
