"""Data access repository for timeline queries, threading, and aggregations."""
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from backend.app.db.database import db
from backend.app.schemas.post import NormalizedPost, EngagementMetrics
from backend.app.schemas.sentiment import SentimentResult

class PostRepository:
    @staticmethod
    def insert_post(post: NormalizedPost, sentiment: Optional[SentimentResult] = None):
        conn = db.get_connection()
        cursor = conn.cursor()
        
        mentions_json = json.dumps(post.mentions)
        engagement_json = json.dumps(post.engagement.model_dump())
        topics_json = json.dumps(post.topics)
        sentiment_json = json.dumps(sentiment.model_dump()) if sentiment else None
        ts_str = post.timestamp.isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO posts (
                post_id, platform, user_hash, text, lang, timestamp,
                parent_id, reply_to, mentions, retweets, engagement,
                bio_text, topics, sentiment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.post_id, post.platform, post.user_hash, post.text, post.lang,
            ts_str, post.parent_id, post.reply_to, mentions_json,
            post.retweets, engagement_json, post.bio_text, topics_json, sentiment_json
        ))
        
        post_hour = post.timestamp.hour
        cursor.execute("SELECT bio_text, post_count, posting_hours FROM users WHERE user_hash = ?", (post.user_hash,))
        user_row = cursor.fetchone()
        
        if user_row:
            count = user_row["post_count"] + 1
            bio = post.bio_text or user_row["bio_text"]
            hours = json.loads(user_row["posting_hours"] or "[]")
            hours.append(post_hour)
            cursor.execute('''
                UPDATE users SET 
                    bio_text = ?, 
                    post_count = ?, 
                    posting_hours = ?, 
                    last_active = ?
                WHERE user_hash = ?
            ''', (bio, count, json.dumps(hours), ts_str, post.user_hash))
        else:
            cursor.execute('''
                INSERT INTO users (user_hash, bio_text, lang, post_count, posting_hours, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                post.user_hash, post.bio_text, post.lang, 1, json.dumps([post_hour]), ts_str
            ))
            
        conn.commit()

    @staticmethod
    def insert_posts_batch(items: List[Tuple[NormalizedPost, Optional[SentimentResult]]]):
        conn = db.get_connection()
        cursor = conn.cursor()
        for post, sentiment in items:
            mentions_json = json.dumps(post.mentions)
            engagement_json = json.dumps(post.engagement.model_dump())
            topics_json = json.dumps(post.topics)
            sentiment_json = json.dumps(sentiment.model_dump()) if sentiment else None
            ts_str = post.timestamp.isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO posts (
                    post_id, platform, user_hash, text, lang, timestamp,
                    parent_id, reply_to, mentions, retweets, engagement,
                    bio_text, topics, sentiment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post.post_id, post.platform, post.user_hash, post.text, post.lang,
                ts_str, post.parent_id, post.reply_to, mentions_json,
                post.retweets, engagement_json, post.bio_text, topics_json, sentiment_json
            ))
            cursor.execute('''
                INSERT INTO users (user_hash, bio_text, lang, post_count, posting_hours, last_active)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(user_hash) DO UPDATE SET
                    bio_text = COALESCE(excluded.bio_text, users.bio_text),
                    post_count = users.post_count + 1,
                    last_active = excluded.last_active
            ''', (
                post.user_hash, post.bio_text, post.lang, json.dumps([post.timestamp.hour]), ts_str
            ))
        conn.commit()

    @staticmethod
    def get_posts(
        limit: int = 50,
        offset: int = 0,
        topic: Optional[str] = None,
        emotion: Optional[str] = None,
        platform: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM posts WHERE 1=1"
        params = []
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        if topic:
            query += " AND topics LIKE ?"
            params.append(f"%{topic}%")
        if emotion:
            query += " AND sentiment LIKE ?"
            params.append(f'%\"emotion\": \"{emotion}\"%')
            
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for r in rows:
            item = dict(r)
            item["mentions"] = json.loads(item["mentions"] or "[]")
            item["engagement"] = json.loads(item["engagement"] or "{}")
            item["topics"] = json.loads(item["topics"] or "[]")
            item["sentiment"] = json.loads(item["sentiment"]) if item["sentiment"] else None
            results.append(item)
        return results

    @staticmethod
    def get_post_by_id(post_id: str) -> Optional[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,))
        row = cursor.fetchone()
        if not row:
            return None
        item = dict(row)
        item["mentions"] = json.loads(item["mentions"] or "[]")
        item["engagement"] = json.loads(item["engagement"] or "{}")
        item["topics"] = json.loads(item["topics"] or "[]")
        item["sentiment"] = json.loads(item["sentiment"]) if item["sentiment"] else None
        return item

    @staticmethod
    def get_thread(post_id: str) -> Dict[str, Any]:
        target = PostRepository.get_post_by_id(post_id)
        if not target:
            return {"root": None, "replies": []}
            
        curr = target
        visited = set()
        while curr and curr.get("parent_id") and curr["post_id"] not in visited:
            visited.add(curr["post_id"])
            parent = PostRepository.get_post_by_id(curr["parent_id"])
            if not parent:
                break
            curr = parent
        root = curr
        
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE parent_id = ? ORDER BY timestamp ASC", (root["post_id"],))
        rows = cursor.fetchall()
        
        replies = []
        for r in rows:
            item = dict(r)
            item["mentions"] = json.loads(item["mentions"] or "[]")
            item["engagement"] = json.loads(item["engagement"] or "{}")
            item["topics"] = json.loads(item["topics"] or "[]")
            item["sentiment"] = json.loads(item["sentiment"]) if item["sentiment"] else None
            replies.append(item)
            
        return {"root": root, "replies": replies}

    @staticmethod
    def get_user_network_edges(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT user_hash, reply_to, mentions, retweets, timestamp, platform FROM posts WHERE 1=1"
        params = []
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        edges = []
        for r in rows:
            src = r["user_hash"]
            ts = r["timestamp"]
            
            if r["reply_to"] and r["reply_to"] != src:
                edges.append({"source": src, "target": r["reply_to"], "type": "reply", "timestamp": ts})
                
            if r["retweets"] and r["retweets"] != src:
                edges.append({"source": src, "target": r["retweets"], "type": "retweet", "timestamp": ts})
                
            mentions = json.loads(r["mentions"] or "[]")
            for m in mentions:
                if m != src:
                    edges.append({"source": src, "target": m, "type": "mention", "timestamp": ts})
                    
        return edges

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        users = []
        for r in rows:
            u = dict(r)
            u["posting_hours"] = json.loads(u["posting_hours"] or "[]")
            users.append(u)
        return users

    @staticmethod
    def update_user_demographics(user_hash: str, age: str, geo: str, interest: str):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET inferred_age = ?, inferred_geo = ?, inferred_interest = ?
            WHERE user_hash = ?
        ''', (age, geo, interest, user_hash))
        conn.commit()

    @staticmethod
    def get_total_stats() -> Dict[str, Any]:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) as total_posts FROM posts")
        total_posts = cursor.fetchone()["total_posts"]
        
        cursor.execute("SELECT count(DISTINCT user_hash) as total_users FROM posts")
        total_users = cursor.fetchone()["total_users"]
        
        cursor.execute("SELECT min(timestamp) as min_ts, max(timestamp) as max_ts FROM posts")
        ts_row = cursor.fetchone()
        
        cursor.execute("SELECT count(DISTINCT platform) as platform_count FROM posts")
        p_count = cursor.fetchone()["platform_count"]
        
        return {
            "total_posts": total_posts,
            "total_users": total_users,
            "min_timestamp": ts_row["min_ts"] if ts_row else None,
            "max_timestamp": ts_row["max_ts"] if ts_row else None,
            "platforms_active": p_count
        }

    @staticmethod
    def clear_all():
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts")
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM topics")
        conn.commit()
