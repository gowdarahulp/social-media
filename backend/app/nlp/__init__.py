"""NLP package with sentiment, emotion analysis, and timeline aggregations."""
from datetime import datetime, timezone
from collections import defaultdict
from typing import Any, Dict, List, Optional
from .sentiment_analyzer import sentiment_engine, MultiDimensionalSentimentEngine
from .evaluation import evaluate_sentiment_engine
from backend.app.schemas.sentiment import SentimentTimelinePoint
from backend.app.db.database import db

def get_sentiment_timeline_aggregation(
    topic: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    bucket: str = "hour"
) -> List[SentimentTimelinePoint]:
    conn = db.get_connection()
    cursor = conn.cursor()

    query = "SELECT timestamp, topics, sentiment FROM posts WHERE sentiment IS NOT NULL"
    params = []
    if topic:
        query += " AND topics LIKE ?"
        params.append(f"%{topic}%")
    if start_time:
        query += " AND timestamp >= ?"
        params.append(start_time.isoformat())
    if end_time:
        query += " AND timestamp <= ?"
        params.append(end_time.isoformat())

    query += " ORDER BY timestamp ASC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    import json
    # Group by bucket
    buckets = defaultdict(lambda: {
        "count": 0,
        "polarities": [],
        "emotions": defaultdict(int),
        "sarcasm_count": 0,
        "topics": set()
    })

    for r in rows:
        ts_str = r["timestamp"]
        dt = datetime.fromisoformat(ts_str)
        if bucket == "hour":
            key = dt.strftime("%Y-%m-%d %H:00:00")
        else:
            key = dt.strftime("%Y-%m-%d")

        sent = json.loads(r["sentiment"])
        t_list = json.loads(r["topics"] or "[]")

        b = buckets[key]
        b["count"] += 1
        b["polarities"].append(sent.get("polarity", 0.0))
        em = sent.get("emotion", "neutral")
        b["emotions"][em] += 1
        if sent.get("sarcasm"):
            b["sarcasm_count"] += 1
        for t in t_list:
            b["topics"].add(t)

    result = []
    for bucket_key in sorted(buckets.keys()):
        b = buckets[bucket_key]
        avg_pol = sum(b["polarities"]) / len(b["polarities"]) if b["polarities"] else 0.0
        sarcasm_rate = b["sarcasm_count"] / b["count"] if b["count"] else 0.0
        
        # parse timestamp
        fmt = "%Y-%m-%d %H:%M:%S" if bucket == "hour" else "%Y-%m-%d"
        point_dt = datetime.strptime(bucket_key, fmt).replace(tzinfo=timezone.utc)

        result.append(SentimentTimelinePoint(
            timestamp=point_dt,
            post_count=b["count"],
            avg_polarity=round(avg_pol, 3),
            emotions=dict(b["emotions"]),
            sarcasm_rate=round(sarcasm_rate, 3),
            topics=list(b["topics"])[:5]
        ))

    return result

__all__ = [
    "sentiment_engine",
    "MultiDimensionalSentimentEngine",
    "evaluate_sentiment_engine",
    "get_sentiment_timeline_aggregation"
]
