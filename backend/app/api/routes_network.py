"""API routes for network topology, centrality, Louvain communities, and information cascade."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from backend.app.schemas.network import NetworkGraph, InfluencerProfile, CascadeStep
from backend.app.network import GraphBuilder, NetworkTopologyAnalyzer, CascadeAnalyzer

router = APIRouter(prefix="/api/network", tags=["Network Analysis & Cascades"])

@router.get("/graph", response_model=NetworkGraph)
def get_network_graph(
    from_date: Optional[datetime] = Query(default=None, alias="from"),
    to_date: Optional[datetime] = Query(default=None, alias="to"),
    min_weight: float = Query(default=1.0, ge=1.0)
):
    G, links = GraphBuilder.build_network(start_time=from_date, end_time=to_date)
    filtered_links = [l for l in links if l.weight >= min_weight]
    nodes, _, num_comms, echo_count = NetworkTopologyAnalyzer.analyze_topology(G)

    return NetworkGraph(
        nodes=nodes,
        links=filtered_links,
        timestamp_from=from_date,
        timestamp_to=to_date,
        communities_count=num_comms,
        echo_chamber_count=echo_count
    )

@router.get("/influencers", response_model=List[InfluencerProfile])
def get_influencer_kols(
    limit: int = Query(default=20, ge=1, le=100)
):
    G, _ = GraphBuilder.build_network()
    _, influencers, _, _ = NetworkTopologyAnalyzer.analyze_topology(G)
    return influencers[:limit]

@router.get("/cascade", response_model=List[CascadeStep])
def get_information_cascade(
    topic: str = Query(default="#AIRevolution", description="Topic to trace information spread for"),
    steps: int = Query(default=8, ge=3, le=24, description="Number of chronological time-slices")
):
    G, _ = GraphBuilder.build_network()
    nodes, _, _, _ = NetworkTopologyAnalyzer.analyze_topology(G)
    community_map = {n.id: n.community_id for n in nodes}
    return CascadeAnalyzer.simulate_cascade(topic=topic, num_steps=steps, community_map=community_map)
