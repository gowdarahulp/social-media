"""Graph construction from multi-platform interactions using NetworkX."""
import networkx as nx
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from backend.app.db.repository import PostRepository
from backend.app.schemas.network import GraphLink

class GraphBuilder:
    @staticmethod
    def build_network(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Tuple[nx.DiGraph, List[GraphLink]]:
        edges = PostRepository.get_user_network_edges(start_time, end_time)
        G = nx.DiGraph()

        link_objects: List[GraphLink] = []
        edge_weights = {}

        for e in edges:
            src = e["source"]
            tgt = e["target"]
            if not src or not tgt or src == tgt:
                continue

            pair = (src, tgt)
            edge_weights[pair] = edge_weights.get(pair, 0.0) + 1.0

            ts = datetime.fromisoformat(e["timestamp"]) if e.get("timestamp") else None
            link_objects.append(GraphLink(
                source=src,
                target=tgt,
                type=e.get("type", "mention"),
                weight=1.0,
                timestamp=ts
            ))

        for (src, tgt), w in edge_weights.items():
            G.add_edge(src, tgt, weight=w)

        return G, link_objects
