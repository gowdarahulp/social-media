"""Tests for BaseConnector and ReplayConnector."""
import pytest
import asyncio
from pathlib import Path
from backend.app.connectors.replay import ReplayConnector
from backend.app.schemas.post import NormalizedPost

@pytest.mark.anyio
async def test_replay_connector_fetch_and_reset():
    dataset_path = "backend/app/data/sample_dataset.jsonl"
    connector = ReplayConnector(dataset_path=dataset_path)
    status = connector.get_status()
    
    assert status["total_available"] >= 300
    assert status["cursor_position"] == 0
    
    batch = await connector.fetch(limit=50)
    assert len(batch) == 50
    assert isinstance(batch[0], NormalizedPost)
    assert batch[0].user_hash.startswith("usr_")
    
    updated_status = connector.get_status()
    assert updated_status["cursor_position"] == 50
    assert updated_status["total_ingested"] == 50
    
    connector.reset()
    assert connector.get_status()["cursor_position"] == 0

@pytest.mark.anyio
async def test_replay_dataset_contains_planted_signals():
    connector = ReplayConnector(dataset_path="backend/app/data/sample_dataset.jsonl")
    all_posts = await connector.fetch(limit=500)
    
    # Verify languages include hinglish
    langs = {p.lang for p in all_posts}
    assert "hinglish" in langs or "hi" in langs
    assert "en" in langs
    
    # Verify planted topics exist
    topics = {t for p in all_posts for t in p.topics}
    assert "#AIRevolution" in topics
    assert "#SustainableTech" in topics
    assert "#CryptoRally" in topics
    assert "#BrandCrisis" in topics
    
    # Verify presence of threads (replies)
    replies = [p for p in all_posts if p.parent_id is not None]
    assert len(replies) > 20
    
    # Verify presence of interactions (mentions or retweets)
    interactions = [p for p in all_posts if p.mentions or p.retweets]
    assert len(interactions) > 20
