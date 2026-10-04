"""Tests for Account/Handle Analysis across the 4 Pillars & Feedback."""
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_analyze_profile_get_existing_handle():
    res = client.get("/api/analyze/profile?handle=@tech_lead_arjun&platform=x")
    assert res.status_code == 200
    data = res.json()

    assert data["handle"] == "@tech_lead_arjun"
    assert data["user_hash"].startswith("usr_")
    
    # 1. What are people feeling? (Sentiment)
    assert "sentiment" in data
    assert "overall_sentiment" in data["sentiment"]
    assert "avg_polarity" in data["sentiment"]
    assert "dominant_emotion" in data["sentiment"]
    assert "audience_feeling_summary" in data["sentiment"]
    assert -1.0 <= data["sentiment"]["avg_polarity"] <= 1.0

    # 2. Who are the people? (Demographics)
    assert "demographics" in data
    assert "audience_archetype" in data["demographics"]
    assert data["demographics"]["k_anonymity_verified"] is True
    assert len(data["demographics"]["top_geographies"]) > 0
    assert "who_they_are_summary" in data["demographics"]

    # 3. What are they talking about? (Trends)
    assert "trends" in data
    assert len(data["trends"]["key_topics"]) > 0
    assert data["trends"]["viral_velocity_score"] > 0
    assert "what_they_talk_about_summary" in data["trends"]

    # 4. How does information spread? (Network Analysis)
    assert "network" in data
    assert "reach_tier" in data["network"]
    assert "community_role" in data["network"]
    assert "cascade_spread_rate" in data["network"]
    assert "how_info_spreads_summary" in data["network"]

    # 5. Feedback Report
    assert "feedback" in data
    assert 0 <= data["feedback"]["health_score"] <= 100
    assert len(data["feedback"]["strengths"]) >= 2
    assert len(data["feedback"]["actionable_recommendations"]) >= 2
    assert len(data["feedback"]["executive_summary"]) > 20

def test_analyze_profile_post_new_handle():
    payload = {
        "platform": "x",
        "handle": "@elonmusk",
        "sample_size": 40
    }
    res = client.post("/api/analyze/profile", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["handle"] == "@elonmusk"
    assert "sentiment" in data
    assert "demographics" in data
    assert "trends" in data
    assert "network" in data
    assert "feedback" in data
    assert data["feedback"]["health_score"] > 0
