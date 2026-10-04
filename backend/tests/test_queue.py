"""Tests for async IngestionQueue and ConnectorManager."""
import pytest
import asyncio
from datetime import datetime, timezone
from backend.app.schemas.post import NormalizedPost, EngagementMetrics, hash_user_id
from backend.app.queue.worker import IngestionQueue
from backend.app.connectors import connector_manager
from backend.app.db.repository import PostRepository

@pytest.mark.anyio
async def test_ingestion_queue_processing():
    PostRepository.clear_all()
    queue = IngestionQueue()
    await queue.start()

    posts = [
        NormalizedPost(
            post_id=f"queue_test_{i}",
            platform="x",
            user_hash=hash_user_id(f"worker_user_{i}"),
            text=f"Testing high throughput async queue item {i}",
            lang="en",
            timestamp=datetime.now(timezone.utc),
            engagement=EngagementMetrics(likes=i*2)
        )
        for i in range(15)
    ]

    await queue.enqueue_batch(posts)
    # Wait briefly for batch worker flush
    await asyncio.sleep(0.8)
    
    metrics = queue.get_metrics()
    assert metrics["total_enqueued"] == 15
    assert metrics["total_processed"] == 15
    
    # Verify in DB
    stats = PostRepository.get_total_stats()
    assert stats["total_posts"] == 15
    
    await queue.stop()
    assert not queue.is_running

def test_connector_manager_registry():
    statuses = connector_manager.get_all_statuses()
    assert len(statuses) >= 6
    platforms = {s["platform"] for s in statuses}
    assert "replay_multi" in platforms
    assert "x" in platforms
    assert "telegram" in platforms
    assert "reddit" in platforms
