"""Normalized post schema with privacy-by-design user hashing."""
import hashlib
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

def hash_user_id(raw_id: str, salt: str = "social-pulse-secret-salt-2026") -> str:
    """Deterministically hash raw user handles/IDs using salted SHA-256."""
    if not raw_id:
        return "anon_" + hashlib.sha256(b"anonymous").hexdigest()[:12]
    clean_id = raw_id.strip().lower()
    return "usr_" + hashlib.sha256(f"{salt}:{clean_id}".encode("utf-8")).hexdigest()[:16]

class EngagementMetrics(BaseModel):
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    quotes: int = 0
    views: int = 0

class NormalizedPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    post_id: str = Field(..., description="Unique post ID across platforms")
    platform: str = Field(..., description="Platform identifier: x, telegram, reddit, youtube, etc.")
    user_hash: str = Field(..., description="Salted SHA-256 hash of the author ID/handle")
    text: str = Field(..., description="Raw text content of the post")
    lang: str = Field(default="en", description="Detected language code, e.g. en, hi, hinglish")
    timestamp: datetime = Field(..., description="Timestamp of post creation (UTC)")
    parent_id: Optional[str] = Field(default=None, description="ID of thread root or parent post")
    reply_to: Optional[str] = Field(default=None, description="Hashed user ID replied to")
    mentions: List[str] = Field(default_factory=list, description="Hashed user IDs mentioned")
    retweets: Optional[str] = Field(default=None, description="Hashed user ID or parent ID retweeted")
    engagement: EngagementMetrics = Field(default_factory=EngagementMetrics)
    bio_text: Optional[str] = Field(default=None, description="Public bio text of author (hashed user only)")
    topics: List[str] = Field(default_factory=list, description="Associated topic labels/tags")
