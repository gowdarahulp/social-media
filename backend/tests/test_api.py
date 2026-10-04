"""Comprehensive end-to-end API integration tests."""
import pytest
from urllib.parse import quote_plus
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.repository import PostRepository

client = TestClient(app)

def test_root_serves_html_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "SocialPulse" in response.text

def test_api_ingest_replay_and_status():
    replay_res = client.post("/api/ingest/replay?limit=200&reset_db=true")
    assert replay_res.status_code == 200
    data = replay_res.json()
    assert "current_database_stats" in data
    assert data["current_database_stats"]["total_posts"] == 200

    status_res = client.get("/api/ingest/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["status"] == "operational"
    assert status_data["database"]["total_posts"] == 200
    assert len(status_data["connectors"]) >= 6

def test_api_posts_and_threads():
    posts_res = client.get("/api/posts?limit=10")
    assert posts_res.status_code == 200
    posts = posts_res.json()
    assert len(posts) == 10
    
    first_post_id = posts[0]["post_id"]
    single_res = client.get(f"/api/posts/{first_post_id}")
    assert single_res.status_code == 200
    assert single_res.json()["post_id"] == first_post_id

    thread_res = client.get(f"/api/posts/{first_post_id}/thread")
    assert thread_res.status_code == 200
    assert "root" in thread_res.json()

def test_api_sentiment_timeline_and_evaluation():
    tl_res = client.get("/api/sentiment/timeline?bucket=hour")
    assert tl_res.status_code == 200
    timeline = tl_res.json()
    assert isinstance(timeline, list)
    assert len(timeline) > 0
    assert "avg_polarity" in timeline[0]

    eval_res = client.get("/api/sentiment/evaluation")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["emotion_accuracy"] >= 0.85
    assert eval_data["macro_f1"] >= 0.80

def test_api_demographics_summary():
    demo_res = client.get("/api/demographics/summary?k=20")
    assert demo_res.status_code == 200
    demo = demo_res.json()
    assert demo["k_threshold"] == 20
    assert len(demo["age_groups"]) > 0
    assert len(demo["geography"]) > 0
    assert "k-Anonymity strictly enforced" in demo["privacy_guarantee"]

def test_api_trends_and_forecast():
    trends_res = client.get("/api/trends/rising")
    assert trends_res.status_code == 200
    trends = trends_res.json()
    assert len(trends) > 0
    
    top_topic = trends[0]["name"]
    fcst_res = client.get(f"/api/trends/forecast?topic={quote_plus(top_topic)}&hours=48")
    assert fcst_res.status_code == 200
    fcst = fcst_res.json()
    assert len(fcst["forecast"]) == 48
    assert "upper_bound_95" in fcst["forecast"][0]

def test_api_network_graph_influencers_and_cascade():
    graph_res = client.get("/api/network/graph")
    assert graph_res.status_code == 200
    graph = graph_res.json()
    assert len(graph["nodes"]) > 0
    assert len(graph["links"]) > 0
    assert graph["communities_count"] >= 1

    inf_res = client.get("/api/network/influencers?limit=5")
    assert inf_res.status_code == 200
    influencers = inf_res.json()
    assert len(influencers) > 0
    assert "kol_score" in influencers[0]

    # Information Cascade with encoded topic name
    topic_enc = quote_plus("#AIRevolution")
    cascade_res = client.get(f"/api/network/cascade?topic={topic_enc}&steps=6")
    assert cascade_res.status_code == 200
    cascade = cascade_res.json()
    assert len(cascade) == 6
    assert "cumulative_reach" in cascade[-1]
