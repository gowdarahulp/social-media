"""X (Twitter) API v2 Connector with retry and exponential backoff."""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx
from backend.app.connectors.base import BaseConnector
from backend.app.schemas.post import NormalizedPost, EngagementMetrics, hash_user_id
from backend.app.config import settings

logger = logging.getLogger(__name__)

class XConnector(BaseConnector):
    def __init__(self, bearer_token: Optional[str] = None):
        super().__init__(name="XConnector_v2", platform="x")
        self.bearer_token = bearer_token or settings.TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"

    async def fetch(self, query: str = "#AI OR #Tech", limit: int = 50) -> List[NormalizedPost]:
        if not self.bearer_token:
            logger.info("XConnector: No TWITTER_BEARER_TOKEN configured, returning empty/mock batch.")
            return []

        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        params = {
            "query": query,
            "max_results": min(max(limit, 10), 100),
            "tweet.fields": "created_at,public_metrics,lang,conversation_id,in_reply_to_user_id,entities",
            "expansions": "author_id",
            "user.fields": "username,description"
        }

        # Exponential backoff loop
        max_retries = 3
        delay = 1.0
        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(max_retries):
                try:
                    res = await client.get(f"{self.base_url}/tweets/search/recent", headers=headers, params=params)
                    if res.status_code == 200:
                        data = res.json()
                        posts = self._parse_tweets(data)
                        self.total_ingested += len(posts)
                        if posts:
                            self.last_ingested_at = posts[-1].timestamp
                        return posts
                    elif res.status_code == 429: # Rate limited
                        reset_header = res.headers.get("x-rate-limit-reset")
                        wait_time = max(int(reset_header) - int(datetime.now().timestamp()), delay) if reset_header else delay
                        logger.warning(f"Rate limited by X API. Backing off for {wait_time}s (attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(min(wait_time, 15))
                        delay *= 2
                    else:
                        logger.error(f"X API returned status {res.status_code}: {res.text}")
                        self.error_count += 1
                        break
                except Exception as e:
                    logger.error(f"X API request error: {e}")
                    self.error_count += 1
                    await asyncio.sleep(delay)
                    delay *= 2

        return []

    def _parse_tweets(self, data: Dict[str, Any]) -> List[NormalizedPost]:
        posts = []
        user_map = {}
        for u in data.get("includes", {}).get("users", []):
            user_map[u["id"]] = {
                "handle": u.get("username", "anon"),
                "bio": u.get("description", "")
            }

        for tweet in data.get("data", []):
            author_info = user_map.get(tweet.get("author_id"), {})
            metrics = tweet.get("public_metrics", {})
            user_h = hash_user_id(author_info.get("handle", tweet.get("author_id", "anon")), salt=settings.HASH_SALT)
            
            created_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))
            
            mentions = []
            for m in tweet.get("entities", {}).get("mentions", []):
                mentions.append(hash_user_id(m.get("username", "anon"), salt=settings.HASH_SALT))
                
            hashtags = [f"#{h.get('tag')}" for h in tweet.get("entities", {}).get("hashtags", [])]

            post = NormalizedPost(
                post_id=f"x_{tweet['id']}",
                platform="x",
                user_hash=user_h,
                text=tweet.get("text", ""),
                lang=tweet.get("lang", "en"),
                timestamp=created_at,
                parent_id=f"x_{tweet.get('conversation_id')}" if tweet.get("conversation_id") != tweet["id"] else None,
                reply_to=hash_user_id(tweet.get("in_reply_to_user_id", ""), salt=settings.HASH_SALT) if tweet.get("in_reply_to_user_id") else None,
                mentions=mentions,
                engagement=EngagementMetrics(
                    likes=metrics.get("like_count", 0),
                    retweets=metrics.get("retweet_count", 0),
                    replies=metrics.get("reply_count", 0),
                    quotes=metrics.get("quote_count", 0),
                    views=metrics.get("impression_count", 0)
                ),
                bio_text=author_info.get("bio"),
                topics=hashtags
            )
            posts.append(post)
        return posts

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        self.is_active = True
        try:
            while self.is_active:
                batch = await self.fetch(limit=25)
                for post in batch:
                    yield post
                await asyncio.sleep(60.0) # Polling interval for live stream
        finally:
            self.is_active = False
