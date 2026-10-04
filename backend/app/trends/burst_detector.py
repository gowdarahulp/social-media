"""Burst detection, velocity, acceleration, and trend score ranking."""
from collections import defaultdict
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from backend.app.schemas.trends import TrendTopic
from backend.app.db.database import db

class BurstDetector:
    @staticmethod
    def detect_rising_trends() -> List[TrendTopic]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT timestamp, topics, user_hash, sentiment FROM posts WHERE topics IS NOT NULL ORDER BY timestamp ASC")
        rows = cursor.fetchall()
        if not rows:
            return []

        cursor.execute("SELECT count(DISTINCT user_hash) as total_users FROM posts")
        total_unique_users = max(cursor.fetchone()["total_users"], 1)

        # Topic -> hourly counts: {topic: {hour_bucket: count}}
        topic_hourly_counts = defaultdict(lambda: defaultdict(int))
        topic_users = defaultdict(set)
        topic_sentiments = defaultdict(list)
        topic_time_bounds = defaultdict(lambda: {"first": None, "last": None})

        for r in rows:
            dt = datetime.fromisoformat(r["timestamp"])
            hour_bucket = dt.strftime("%Y-%m-%d %H:00:00")
            t_list = json.loads(r["topics"] or "[]")
            user = r["user_hash"]
            sent = json.loads(r["sentiment"]) if r["sentiment"] else None

            for t in t_list:
                topic_hourly_counts[t][hour_bucket] += 1
                topic_users[t].add(user)
                if sent:
                    topic_sentiments[t].append(sent.get("emotion", "neutral"))

                tb = topic_time_bounds[t]
                if tb["first"] is None or dt < tb["first"]:
                    tb["first"] = dt
                if tb["last"] is None or dt > tb["last"]:
                    tb["last"] = dt

        trend_results = []
        for topic_name, hourly_map in topic_hourly_counts.items():
            sorted_hours = sorted(hourly_map.keys())
            counts_series = [hourly_map[h] for h in sorted_hours]
            total_vol = sum(counts_series)

            # Velocity: latest window volume / hours in window
            recent_window = counts_series[-4:] if len(counts_series) >= 4 else counts_series
            velocity = round(sum(recent_window) / max(len(recent_window), 1), 2)

            # Acceleration: change between the two most recent periods
            if len(counts_series) >= 2:
                prev_vel = sum(counts_series[-8:-4]) / max(len(counts_series[-8:-4]), 1) if len(counts_series) >= 8 else counts_series[0]
                accel = round(velocity - prev_vel, 2)
            else:
                accel = 0.0

            # Unique user spread: fraction of total active users who posted in this topic
            user_spread = round(len(topic_users[topic_name]) / total_unique_users, 3)

            # Trend score = Velocity * max(0.1, (1.0 + accel)) * UniqueUserSpread * 10.0
            accel_factor = max(0.1, 1.0 + accel * 0.2)
            trend_score = round(velocity * accel_factor * user_spread * 10.0, 2)

            # Dominant sentiment
            emotions = topic_sentiments[topic_name]
            from collections import Counter
            dom_emotion = Counter(emotions).most_common(1)[0][0] if emotions else "neutral"

            # Status determination
            if accel > 0.5 and velocity > 2.0:
                status = "rising"
            elif velocity > 10.0 and accel <= 0.0:
                status = "peaked"
            elif accel < -0.5:
                status = "decaying"
            else:
                status = "stable"

            tb = topic_time_bounds[topic_name]
            trend_results.append(TrendTopic(
                topic_id=f"top_{abs(hash(topic_name)) % 100000}",
                name=topic_name,
                hashtags=[topic_name] if topic_name.startswith("#") else [f"#{topic_name}"],
                keywords=[topic_name.replace("#", "")],
                total_volume=total_vol,
                velocity=velocity,
                acceleration=accel,
                unique_users=len(topic_users[topic_name]),
                trend_score=trend_score,
                status=status,
                dominant_sentiment=dom_emotion,
                first_seen=tb["first"] or datetime.now(timezone.utc),
                last_seen=tb["last"] or datetime.now(timezone.utc)
            ))

        # Sort descending by trend_score
        trend_results.sort(key=lambda x: x.trend_score, reverse=True)
        return trend_results
