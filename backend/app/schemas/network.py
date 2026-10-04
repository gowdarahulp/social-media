"""Network graph, link analysis and cascade schemas."""
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
