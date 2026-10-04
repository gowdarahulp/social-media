import os
from pathlib import Path

BASE = Path("C:/Users/HP/.gemini/antigravity/scratch/social-pulse")

files = {}

files["backend/app/__init__.py"] = '"""Social Media Analytics Framework Backend."""\n__version__ = "1.0.0"\n'

files["backend/app/config.py"] = '''"""Application configuration and settings."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Social Media Analytics Framework"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Security & Privacy
    HASH_SALT: str = Field(default="social-pulse-secret-salt-2026", description="Salt used for deterministic SHA-256 user anonymization")
    K_ANONYMITY_THRESHOLD: int = Field(default=20, description="Minimum cohort size for reporting demographics")
    
    # Storage
    DATABASE_PATH: str = "social_pulse.db"
    DATABASE_URL: str = "sqlite:///./social_pulse.db"
    
    # Ingestion & Connectors
    REPLAY_DATASET_PATH: str = "backend/app/data/sample_dataset.jsonl"
    REPLAY_SPEED_MULTIPLIER: float = 1.0
    
    # External APIs (Optional - defaults to mock/replay if absent)
    TWITTER_BEARER_TOKEN: str = ""
    TELEGRAM_API_ID: str = ""
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_PHONE: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
'''

files["backend/app/schemas/__init__.py"] = '''"""Pydantic schemas package."""
from .post import NormalizedPost, EngagementMetrics, hash_user_id
from .sentiment import EmotionType, SentimentResult, SentimentTimelinePoint, StanceType
from .demographics import DemographicsSummary, DemographicDistribution, CohortDistribution
from .trends import TrendTopic, TrendForecast, ForecastPoint
from .network import GraphNode, GraphLink, NetworkGraph, CascadeStep, InfluencerProfile

__all__ = [
    "NormalizedPost",
    "EngagementMetrics",
    "hash_user_id",
    "EmotionType",
    "SentimentResult",
    "SentimentTimelinePoint",
    "StanceType",
    "DemographicsSummary",
    "DemographicDistribution",
    "CohortDistribution",
    "TrendTopic",
    "TrendForecast",
    "ForecastPoint",
    "GraphNode",
    "GraphLink",
    "NetworkGraph",
    "CascadeStep",
    "InfluencerProfile",
]
'''

files["backend/app/schemas/post.py"] = '''"""Normalized post schema with privacy-by-design user hashing."""
import hashlib
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

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

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
'''

files["backend/app/schemas/sentiment.py"] = '''"""Sentiment and emotion schemas."""
from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field

EmotionType = Literal[
    "anger",
    "anxiety",
    "excitement",
    "joy",
    "sadness",
    "support",
    "opposition",
    "neutral"
]

StanceType = Literal["favorable", "against", "neutral", "none"]

class SentimentResult(BaseModel):
    polarity: float = Field(..., ge=-1.0, le=1.0, description="Polarity score from -1.0 (negative) to +1.0 (positive)")
    emotion: EmotionType = Field(..., description="Dominant emotion classification")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="Probabilities for each emotion")
    sarcasm: bool = Field(default=False, description="Flag indicating detected sarcasm or irony")
    sarcasm_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Sarcasm confidence score")
    stance: StanceType = Field(default="none", description="Stance towards extracted topic")
    language: str = Field(default="en", description="Identified language or code-mix mode")

class SentimentTimelinePoint(BaseModel):
    timestamp: datetime
    post_count: int
    avg_polarity: float
    emotions: Dict[str, int]
    sarcasm_rate: float
    topics: List[str] = Field(default_factory=list)
'''

files["backend/app/schemas/demographics.py"] = '''"""Demographic profiling schemas with k-anonymity guarantee."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class DemographicDistribution(BaseModel):
    category: str
    count: int
    percentage: float
    confidence: float

class CohortDistribution(BaseModel):
    name: str
    is_suppressed: bool = False
    distribution: List[DemographicDistribution] = Field(default_factory=list)
    k_threshold: int = 20

class DemographicsSummary(BaseModel):
    total_analyzed_users: int
    k_threshold: int = 20
    privacy_guarantee: str = "k-anonymity strictly enforced; sub-threshold cohorts are suppressed"
    age_groups: List[DemographicDistribution]
    geography: List[DemographicDistribution]
    languages: List[DemographicDistribution]
    professional_interests: List[DemographicDistribution]
    confidence_overall: float
    limitations: List[str] = Field(default_factory=list)
'''

files["backend/app/schemas/trends.py"] = '''"""Trending topics and forecasting schemas."""
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class TrendTopic(BaseModel):
    topic_id: str
    name: str
    hashtags: List[str]
    keywords: List[str]
    total_volume: int
    velocity: float = Field(description="Posts per hour rate")
    acceleration: float = Field(description="Rate of velocity change")
    unique_users: int
    trend_score: float = Field(description="Velocity * Acceleration * UniqueUserSpread")
    status: Literal["rising", "peaked", "decaying", "stable"]
    dominant_sentiment: str = "neutral"
    first_seen: datetime
    last_seen: datetime

class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_volume: float
    lower_bound_80: float
    upper_bound_80: float
    lower_bound_95: float
    upper_bound_95: float

class TrendForecast(BaseModel):
    topic_id: str
    name: str
    method: str = "Holt-Winters Exponential Smoothing + Burst Detection"
    history: List[dict]
    forecast: List[ForecastPoint]
'''

files["backend/app/schemas/network.py"] = '''"""Network graph, link analysis and cascade schemas."""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: str = Field(..., description="Hashed user ID")
    label: str
    community_id: int
    pagerank: float
    betweenness: float
    degree: int
    is_bridge: bool = False
    is_influencer: bool = False
    dominant_sentiment: str = "neutral"
    inferred_interest: Optional[str] = None

class GraphLink(BaseModel):
    source: str
    target: str
    type: Literal["reply", "mention", "retweet", "coengagement"]
    weight: float = 1.0
    timestamp: Optional[datetime] = None

class NetworkGraph(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]
    timestamp_from: Optional[datetime] = None
    timestamp_to: Optional[datetime] = None
    communities_count: int = 0
    echo_chamber_count: int = 0

class CascadeStep(BaseModel):
    step_index: int
    timestamp: datetime
    active_nodes: List[str]
    new_infections: List[str]
    active_communities: Dict[int, int]
    dominant_sentiment: str
    cumulative_reach: int

class InfluencerProfile(BaseModel):
    user_hash: str
    kol_score: float
    pagerank: float
    betweenness: float
    community_id: int
    total_engagements: int
    top_topics: List[str]
    inferred_profile: str
'''

for rel_path, content in files.items():
    target = BASE / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(content)
print(f"Successfully generated {len(files)} scaffold & schema files.")
