"""Kaggle Social Media Dataset Connector.

Supports loading standard Kaggle benchmark datasets (CSV/JSON) and custom
user-uploaded Kaggle datasets with intelligent column auto-detection and
privacy-preserving salted SHA-256 user pseudonymization.
"""
import csv
import io
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
import dateutil.parser

from backend.app.connectors.base import BaseConnector
from backend.app.schemas.post import NormalizedPost, EngagementMetrics, hash_user_id


class KaggleConnector(BaseConnector):
    """Ingests Kaggle social media datasets with adaptive schema mapping."""

    def __init__(self, dataset_path: str = "backend/app/data/kaggle_social_dataset.csv"):
        super().__init__(name="KaggleSocialConnector", platform="kaggle_benchmark")
        self.dataset_path = Path(dataset_path)
        self.cursor = 0
        self._posts_cache: List[NormalizedPost] = []
        self._load_cache()

    def _load_cache(self):
        """Load and normalize posts from the local Kaggle CSV benchmark."""
        if not self.dataset_path.exists():
            return
        try:
            with open(self.dataset_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self._posts_cache = self.parse_rows(rows)
        except Exception as e:
            self.error_count += 1
            print(f"[KaggleConnector] Failed to load CSV {self.dataset_path}: {e}")

    @classmethod
    def parse_csv_content(cls, csv_text: str) -> List[NormalizedPost]:
        """Parse raw CSV string (e.g. from file upload) into NormalizedPosts."""
        f = io.StringIO(csv_text)
        reader = csv.DictReader(f)
        rows = list(reader)
        return cls.parse_rows(rows)

    @classmethod
    def parse_rows(cls, rows: List[Dict[str, str]]) -> List[NormalizedPost]:
        """Adaptively maps arbitrary Kaggle CSV columns into NormalizedPost schemas."""
        posts: List[NormalizedPost] = []
        if not rows:
            return posts

        # Identify headers
        sample_keys = list(rows[0].keys())

        def find_col(candidates: List[str]) -> Optional[str]:
            for cand in candidates:
                for k in sample_keys:
                    if k and cand.lower() == k.strip().lower():
                        return k
            for cand in candidates:
                for k in sample_keys:
                    if k and cand.lower() in k.strip().lower():
                        return k
            return None

        col_id = find_col(["post_id", "id", "tweet_id", "status_id", "index"])
        col_text = find_col(["clean_text", "text", "tweet", "content", "post_text", "body", "message"])
        col_user = find_col(["username", "user", "author", "user_id", "screen_name", "handle", "user_name"])
        col_platform = find_col(["platform", "source", "channel", "network"])
        col_lang = find_col(["language", "lang", "detected_lang"])
        col_time = find_col(["timestamp", "created_at", "date", "datetime", "time", "posted_at"])
        col_likes = find_col(["likes", "like_count", "favorite_count", "favs", "upvotes", "score"])
        col_retweets = find_col(["retweets", "retweet_count", "shares", "reposts"])
        col_replies = find_col(["replies", "reply_count", "comments", "comment_count"])
        col_hashtags = find_col(["hashtags", "tags", "topic", "topics", "category"])
        col_bio = find_col(["bio", "user_bio", "description", "user_description"])
        col_geo = find_col(["geo", "location", "country", "place"])

        for idx, row in enumerate(rows):
            # 1. Post ID
            post_id = str(row.get(col_id, "")).strip() if col_id else ""
            if not post_id:
                post_id = f"kg_{idx:05d}"

            # 2. Text
            text = str(row.get(col_text, "")).strip() if col_text else ""
            if not text:
                continue

            # 3. User & Salted Hash
            raw_user = str(row.get(col_user, "")).strip() if col_user else ""
            if not raw_user:
                raw_user = f"kaggle_user_{idx % 40 + 1}"
            user_hash = hash_user_id(raw_user)

            # 4. Platform
            platform = str(row.get(col_platform, "x")).strip().lower() if col_platform else "x"
            if platform not in ["x", "reddit", "telegram", "youtube", "instagram", "facebook"]:
                platform = "x"

            # 5. Language
            lang = str(row.get(col_lang, "en")).strip().lower() if col_lang else "en"
            if not lang:
                lang = "en"

            # 6. Timestamp parsing
            raw_ts = str(row.get(col_time, "")).strip() if col_time else ""
            parsed_dt = None
            if raw_ts:
                try:
                    parsed_dt = dateutil.parser.parse(raw_ts)
                    if parsed_dt.tzinfo is None:
                        parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                except Exception:
                    pass
            if not parsed_dt:
                parsed_dt = datetime.now(timezone.utc)

            # 7. Engagement Metrics
            def _to_int(val: Any) -> int:
                try:
                    if val is None or val == "":
                        return 0
                    return int(float(str(val).replace(",", "").strip()))
                except (ValueError, TypeError):
                    return 0

            likes = _to_int(row.get(col_likes, 0)) if col_likes else 0
            retweets = _to_int(row.get(col_retweets, 0)) if col_retweets else 0
            replies = _to_int(row.get(col_replies, 0)) if col_replies else 0

            # 8. Topics & Hashtags
            topics: List[str] = []
            if col_hashtags and row.get(col_hashtags):
                raw_tags = str(row.get(col_hashtags, ""))
                extracted = re.findall(r"#\w+", raw_tags)
                if extracted:
                    topics.extend(extracted)
                else:
                    topics.extend([f"#{t.strip()}" for t in re.split(r"[,; ]+", raw_tags) if t.strip()])
            
            # Also extract inline hashtags from text if none found
            if not topics:
                topics = re.findall(r"#\w+", text)

            # 9. Mentions
            mentions_raw = re.findall(r"@(\w+)", text)
            mentions = [hash_user_id(m) for m in mentions_raw]

            # 10. Bio & Geo
            bio_text = str(row.get(col_bio, "")).strip() if col_bio else None
            if not bio_text and col_geo and row.get(col_geo):
                bio_text = f"Location: {row.get(col_geo)}"

            post = NormalizedPost(
                post_id=post_id,
                platform=platform,
                user_hash=user_hash,
                text=text,
                lang=lang,
                timestamp=parsed_dt,
                parent_id=None,
                reply_to=None,
                mentions=mentions,
                retweets=None,
                engagement=EngagementMetrics(
                    likes=likes,
                    retweets=retweets,
                    replies=replies,
                    quotes=0,
                    views=likes * 4 + retweets * 8
                ),
                bio_text=bio_text,
                topics=topics
            )
            posts.append(post)

        return posts

    async def fetch(self, limit: int = 100) -> List[NormalizedPost]:
        if not self._posts_cache:
            self._load_cache()

        end = min(self.cursor + limit, len(self._posts_cache))
        chunk = self._posts_cache[self.cursor:end]
        self.cursor = end

        self.total_ingested += len(chunk)
        if chunk:
            self.last_ingested_at = chunk[-1].timestamp
        return chunk

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        if not self._posts_cache:
            self._load_cache()

        self.is_active = True
        try:
            for post in self._posts_cache:
                self.total_ingested += 1
                self.last_ingested_at = post.timestamp
                yield post
        finally:
            self.is_active = False

    def reset(self):
        self.cursor = 0
        self.total_ingested = 0
        self.last_ingested_at = None

    def get_status(self) -> Dict[str, Any]:
        status = super().get_status()
        status.update({
            "total_available": len(self._posts_cache),
            "cursor_position": self.cursor,
            "progress_percent": round((self.cursor / len(self._posts_cache) * 100), 1) if self._posts_cache else 0.0,
            "dataset_path": str(self.dataset_path)
        })
        return status
