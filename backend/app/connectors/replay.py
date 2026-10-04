"""Mock/Replay Connector for offline, demo-ready data ingestion."""
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional
from backend.app.connectors.base import BaseConnector
from backend.app.schemas.post import NormalizedPost, EngagementMetrics
from backend.app.schemas.sentiment import SentimentResult

class ReplayConnector(BaseConnector):
    def __init__(self, dataset_path: str = "backend/app/data/sample_dataset.jsonl"):
        super().__init__(name="MockReplayConnector", platform="replay_multi")
        self.dataset_path = Path(dataset_path)
        self.cursor = 0
        self._raw_cache: List[Dict[str, Any]] = []
        self._load_cache()

    def _load_cache(self):
        if not self.dataset_path.exists():
            return
        self._raw_cache.clear()
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self._raw_cache.append(json.loads(line))

    def _to_normalized_post(self, data: Dict[str, Any]) -> NormalizedPost:
        eng = data.get("engagement", {})
        return NormalizedPost(
            post_id=data["post_id"],
            platform=data.get("platform", "x"),
            user_hash=data["user_hash"],
            text=data["text"],
            lang=data.get("lang", "en"),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            parent_id=data.get("parent_id"),
            reply_to=data.get("reply_to"),
            mentions=data.get("mentions", []),
            retweets=data.get("retweets"),
            engagement=EngagementMetrics(
                likes=eng.get("likes", 0),
                retweets=eng.get("retweets", 0),
                replies=eng.get("replies", 0),
                quotes=eng.get("quotes", 0),
                views=eng.get("views", 0)
            ),
            bio_text=data.get("bio_text"),
            topics=data.get("topics", [])
        )

    def _to_sentiment(self, data: Dict[str, Any]) -> Optional[SentimentResult]:
        sent = data.get("sentiment")
        if not sent:
            return None
        return SentimentResult(
            polarity=sent["polarity"],
            emotion=sent["emotion"],
            emotion_scores=sent.get("emotion_scores", {}),
            sarcasm=sent.get("sarcasm", False),
            sarcasm_score=sent.get("sarcasm_score", 0.0),
            stance=sent.get("stance", "none"),
            language=sent.get("language", "en")
        )

    async def fetch(self, limit: int = 100) -> List[NormalizedPost]:
        if not self._raw_cache:
            self._load_cache()
            
        end = min(self.cursor + limit, len(self._raw_cache))
        chunk = self._raw_cache[self.cursor:end]
        self.cursor = end
        
        posts = [self._to_normalized_post(item) for item in chunk]
        self.total_ingested += len(posts)
        if posts:
            self.last_ingested_at = posts[-1].timestamp
        return posts

    async def stream(self, delay_seconds: float = 0.0) -> AsyncIterator[NormalizedPost]:
        if not self._raw_cache:
            self._load_cache()
            
        self.is_active = True
        try:
            for item in self._raw_cache:
                post = self._to_normalized_post(item)
                self.total_ingested += 1
                self.last_ingested_at = post.timestamp
                yield post
                if delay_seconds > 0:
                    await asyncio.sleep(delay_seconds)
        finally:
            self.is_active = False

    def reset(self):
        self.cursor = 0
        self.total_ingested = 0
        self.last_ingested_at = None

    def get_status(self) -> Dict[str, Any]:
        status = super().get_status()
        status.update({
            "total_available": len(self._raw_cache),
            "cursor_position": self.cursor,
            "progress_percent": round((self.cursor / len(self._raw_cache) * 100), 1) if self._raw_cache else 0.0,
            "dataset_path": str(self.dataset_path)
        })
        return status
