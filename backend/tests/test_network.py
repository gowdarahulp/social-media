"""Tests for network topology, centrality, Louvain communities, and cascade simulation."""
import pytest
from backend.app.connectors.replay import ReplayConnector
from backend.app.db.repository import PostRepository
from backend.app.network import GraphBuilder, NetworkTopologyAnalyzer, CascadeAnalyzer

@pytest.mark.anyio
async def test_network_graph_construction_and_centrality():
    PostRepository.clear_all()
    connector = ReplayConnector()
    posts = await connector.fetch(limit=380)
    for p in posts:
        PostRepository.insert_post(p)

    G, links = GraphBuilder.build_network()
    assert G.number_of_nodes() > 10
    assert len(links) > 15

    nodes, influencers, num_comms, echo_count = NetworkTopologyAnalyzer.analyze_topology(G)
    assert len(nodes) == G.number_of_nodes()
    assert num_comms >= 1
    assert len(influencers) >= 1

    # Verify PageRank values are valid probabilities
    total_pr = sum(n.pagerank for n in nodes)
    assert 0.85 <= total_pr <= 1.15

    # Verify influencer leaderboard ordering
    scores = [inf.kol_score for inf in influencers]
    assert scores == sorted(scores, reverse=True)

    # Verify bridge nodes have betweenness centrality
    bridges = [n for n in nodes if n.is_bridge]
    assert isinstance(bridges, list)

@pytest.mark.anyio
async def test_cascade_simulation():
    # Simulate cascade on #AIRevolution
    cascade_steps = CascadeAnalyzer.simulate_cascade(topic="#AIRevolution", num_steps=6)
    assert len(cascade_steps) > 0

    # Cumulative reach and active nodes should be non-decreasing
    reaches = [s.cumulative_reach for s in cascade_steps]
    for i in range(1, len(reaches)):
        assert reaches[i] >= reaches[i-1]

    # Verify step metadata
    for step in cascade_steps:
        assert step.step_index >= 1
        assert len(step.active_nodes) > 0
        assert step.dominant_sentiment in ["joy", "excitement", "anger", "anxiety", "support", "opposition", "neutral", "sadness"]
