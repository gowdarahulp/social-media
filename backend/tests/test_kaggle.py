"""Unit and integration tests for Kaggle dataset ingestion and analysis."""
import pytest
import io
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.connectors.kaggle import KaggleConnector
from backend.app.schemas.post import NormalizedPost
from backend.app.db.repository import PostRepository

client = TestClient(app)

@pytest.mark.anyio
async def test_kaggle_connector_benchmark_dataset():
    """Verify KaggleConnector loads benchmark CSV and produces valid NormalizedPosts."""
    connector = KaggleConnector(dataset_path="backend/app/data/kaggle_social_dataset.csv")
    status = connector.get_status()
    
    assert status["total_available"] >= 500
    assert status["cursor_position"] == 0
    
    batch = await connector.fetch(limit=100)
    assert len(batch) == 100
    assert isinstance(batch[0], NormalizedPost)
    
    # Check privacy-preserving hashing
    assert batch[0].user_hash.startswith("usr_")
    
    # Check platform diversity
    platforms = {p.platform for p in batch}
    assert "x" in platforms
    assert len(platforms) >= 2
    
    # Check topics
    topics = {t for p in batch for t in p.topics}
    assert any("AI" in t or "Crypto" in t or "Tech" in t or "Brand" in t for t in topics)

    # Check languages (multilingual benchmark)
    langs = {p.lang for p in batch}
    assert "en" in langs

    connector.reset()
    assert connector.get_status()["cursor_position"] == 0

def test_kaggle_connector_adaptive_mapping():
    """Verify adaptive column detection for non-standard Kaggle CSV headers."""
    custom_csv = (
        "tweet_id,author,tweet,Date,like_count,retweet_count,tags,location\n"
        '98765,kaggle_guru,"Open source AI will dominate proprietary models! #AI #Innovation",2026-10-01T12:00:00Z,45,12,#AI #Innovation,San Francisco\n'
        '98766,delhi_dev,"Yeh architecture kitni fast hai yaar, latency near zero! #Cloud",2026-10-01T13:00:00Z,89,20,#Cloud,India\n'
    )
    posts = KaggleConnector.parse_csv_content(custom_csv)
    assert len(posts) == 2
    assert posts[0].post_id == "98765"
    assert posts[0].user_hash.startswith("usr_")
    assert "Open source AI" in posts[0].text
    assert posts[0].engagement.likes == 45
    assert posts[0].engagement.retweets == 12
    assert "#AI" in posts[0].topics
    assert "Location: San Francisco" in posts[0].bio_text
    assert "Location: India" in posts[1].bio_text

def test_api_ingest_kaggle_benchmark_endpoint():
    """Verify POST /api/ingest/kaggle populates database and downstream analytics."""
    res = client.post("/api/ingest/kaggle?limit=150&reset_db=true")
    assert res.status_code == 200
    data = res.json()
    assert "Successfully ingested 150 posts" in data["message"]
    assert data["current_database_stats"]["total_posts"] == 150

    # Verify Sentiment Timeline reflects Kaggle data
    tl_res = client.get("/api/sentiment/timeline?bucket=hour")
    assert tl_res.status_code == 200
    timeline = tl_res.json()
    assert len(timeline) > 0

    # Verify Demographics with k>=20 guardrails
    demo_res = client.get("/api/demographics/summary?k=20")
    assert demo_res.status_code == 200
    demo_data = demo_res.json()
    assert demo_data["k_threshold"] == 20
    assert "k-anonymity" in demo_data["privacy_guarantee"].lower()
    assert demo_data["total_analyzed_users"] > 0

    # Verify Trends endpoint
    trends_res = client.get("/api/trends/rising")
    assert trends_res.status_code == 200
    trends = trends_res.json()
    assert len(trends) > 0

    # Verify Network Graph
    net_res = client.get("/api/network/graph")
    assert net_res.status_code == 200
    net_data = net_res.json()
    assert "nodes" in net_data
    assert "links" in net_data

def test_api_ingest_kaggle_upload_endpoint():
    """Verify custom CSV file upload via /api/ingest/kaggle/upload."""
    csv_bytes = (
        "id,user,text,likes,retweets,category\n"
        "up_1,alice,Excited about the future of autonomous vehicles! #AV #Mobility,12,3,#AV\n"
        "up_2,bob,Battery recycling efficiency reached 98%! #CleanEnergy,45,10,#CleanEnergy\n"
    ).encode("utf-8")

    files = {"file": ("custom_kaggle_feed.csv", io.BytesIO(csv_bytes), "text/csv")}
    res = client.post("/api/ingest/kaggle/upload?reset_db=false", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["posts_ingested"] == 2
    assert "custom_kaggle_feed.csv" in data["message"]
