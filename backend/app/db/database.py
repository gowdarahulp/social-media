"""SQLite Database connection manager with thread safety and indexing."""
import sqlite3
import threading
from pathlib import Path
from backend.app.config import settings

class Database:
    _instance = None
    _lock = threading.Lock()
    _local = threading.local()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Database, cls).__new__(cls)
                cls._instance._db_path = Path(settings.DATABASE_PATH)
                cls._instance._init_sqlite()
            return cls._instance

    def _init_sqlite(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Posts table with time-series indexing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                user_hash TEXT NOT NULL,
                text TEXT NOT NULL,
                lang TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parent_id TEXT,
                reply_to TEXT,
                mentions TEXT,
                retweets TEXT,
                engagement TEXT,
                bio_text TEXT,
                topics TEXT,
                sentiment TEXT
            )
        ''')
        
        # Indices for rapid range queries, thread reconstruction, and user lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_parent ON posts(parent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)")
        
        # User profiles for demographic aggregation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_hash TEXT PRIMARY KEY,
                bio_text TEXT,
                lang TEXT,
                post_count INTEGER DEFAULT 1,
                posting_hours TEXT,
                inferred_age TEXT,
                inferred_geo TEXT,
                inferred_interest TEXT,
                last_active TEXT
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_geo ON users(inferred_geo)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_interest ON users(inferred_interest)")
        
        # Topics catalog
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                topic_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hashtags TEXT,
                keywords TEXT,
                first_seen TEXT,
                last_seen TEXT
            )
        ''')
        conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                str(self._db_path),
                timeout=30.0,
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

db = Database()
