"""Tests for normalized schemas, hashing, and database persistence."""
import pytest
from datetime import datetime, timezone
from backend.app.schemas.post import NormalizedPost, EngagementMetrics, hash_user_id
from backend.app.schemas.sentiment import SentimentResult
from backend.app.db.repository import PostRepository

def test_hash_user_id_determinism_and_privacy():
    raw_user = "@TechGuru_99"
    hash1 = hash_user_id(raw_user, salt="test-salt")
    hash2 = hash_user_id(raw_user, salt="test-salt")
    different_salt_hash = hash_user_id(raw_user, salt="other-salt")
    
    # Deterministic with same salt
    assert hash1 == hash2
    assert hash1.startswith("usr_")
    # Raw handle must not appear in hash
    assert "TechGuru" not in hash1
    assert "99" not in hash1
    # Different salt yields different hash
    assert hash1 != different_salt_hash

def test_normalized_post_schema():
    post = NormalizedPost(
        post_id="post_test_001",
        platform="x",
        user_hash=hash_user_id("user1"),
        text="Exploring generative AI architectures today! #AI",
        lang="en",
        timestamp=datetime.now(timezone.utc),
        engagement=EngagementMetrics(likes=45, retweets=12, replies=4, views=1200),
        topics=["#AI", "generative AI"]
    )
    assert post.post_id == "post_test_001"
    assert post.engagement.likes == 45
    assert len(post.topics) == 2

def test_database_insert_and_retrieve():
    PostRepository.clear_all()
    user_hash = hash_user_id("analyst_alpha")
    post = NormalizedPost(
        post_id="p_101",
        platform="telegram",
        user_hash=user_hash,
        text="Breaking: Market rally continues as tech earnings beat expectations.",
        lang="en",
        timestamp=datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc),
        engagement=EngagementMetrics(likes=150, retweets=30, replies=15),
        bio_text="Financial Markets & Tech Analyst",
        topics=["tech", "finance"]
    )
    sentiment = SentimentResult(
        polarity=0.75,
        emotion="excitement",
        sarcasm=False,
        stance="favorable",
        language="en"
    )
    
    PostRepository.insert_post(post, sentiment)
    retrieved = PostRepository.get_post_by_id("p_101")
    
    assert retrieved is not None
    assert retrieved["post_id"] == "p_101"
    assert retrieved["platform"] == "telegram"
    assert retrieved["user_hash"] == user_hash
    assert retrieved["sentiment"]["emotion"] == "excitement"
    assert retrieved["sentiment"]["polarity"] == 0.75
    
    # Thread test
    reply_user = hash_user_id("trader_beta")
    reply = NormalizedPost(
        post_id="p_102",
        platform="telegram",
        user_hash=reply_user,
        text="Agreed, bull momentum looks solid!",
        lang="en",
        timestamp=datetime(2026, 10, 1, 10, 35, tzinfo=timezone.utc),
        parent_id="p_101",
        reply_to=user_hash,
        engagement=EngagementMetrics(likes=10)
    )
    PostRepository.insert_post(reply)
    thread = PostRepository.get_thread("p_102")
    assert thread["root"]["post_id"] == "p_101"
    assert len(thread["replies"]) == 1
    assert thread["replies"][0]["post_id"] == "p_102"
