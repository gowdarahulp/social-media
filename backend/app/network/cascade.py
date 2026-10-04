"""Information cascade simulation: tracks topic/sentiment propagation across communities."""
import json
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
from backend.app.schemas.network import CascadeStep
from backend.app.db.database import db

class CascadeAnalyzer:
    @staticmethod
    def simulate_cascade(topic: str, num_steps: int = 8, community_map: Optional[Dict[str, int]] = None) -> List[CascadeStep]:
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT post_id, user_hash, timestamp, engagement, sentiment 
            FROM posts 
            WHERE topics LIKE ? 
            ORDER BY timestamp ASC
        ''', (f"%{topic}%",))
        rows = cursor.fetchall()
        if not rows:
            return []

        total_posts = len(rows)
        chunk_size = max(1, total_posts // num_steps)

        steps: List[CascadeStep] = []
        cumulative_nodes = set()
        cumulative_reach = 0

        for step_idx in range(num_steps):
            start_i = step_idx * chunk_size
            end_i = total_posts if step_idx == num_steps - 1 else min((step_idx + 1) * chunk_size, total_posts)
            slice_rows = rows[start_i:end_i]

            if not slice_rows:
                break

            new_infections = set()
            slice_emotions = []
            slice_timestamp = datetime.fromisoformat(slice_rows[-1]["timestamp"])

            for r in slice_rows:
                u = r["user_hash"]
                if u not in cumulative_nodes:
                    new_infections.add(u)
                    cumulative_nodes.add(u)

                eng = json.loads(r["engagement"] or "{}")
                cumulative_reach += eng.get("views", 100)

                sent = json.loads(r["sentiment"]) if r["sentiment"] else None
                if sent:
                    slice_emotions.append(sent.get("emotion", "neutral"))

            # Communities breakdown for cumulative nodes
            comm_counts = defaultdict(int)
            if community_map:
                for node in cumulative_nodes:
                    cid = community_map.get(node, 0)
                    comm_counts[cid] += 1
            else:
                comm_counts[0] = len(cumulative_nodes)

            dom_emotion = Counter(slice_emotions).most_common(1)[0][0] if slice_emotions else "neutral"

            steps.append(CascadeStep(
                step_index=step_idx + 1,
                timestamp=slice_timestamp,
                active_nodes=list(cumulative_nodes),
                new_infections=list(new_infections),
                active_communities=dict(comm_counts),
                dominant_sentiment=dom_emotion,
                cumulative_reach=cumulative_reach
            ))

        return steps
