"""Asynchronous in-process ingestion worker queue."""
import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from backend.app.schemas.post import NormalizedPost
from backend.app.schemas.sentiment import SentimentResult
from backend.app.db.repository import PostRepository

logger = logging.getLogger(__name__)

class IngestionQueue:
    def __init__(self, maxsize: int = 10000):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self.is_running = False
        self._worker_task: Optional[asyncio.Task] = None
        self.total_enqueued = 0
        self.total_processed = 0
        self.started_at: Optional[float] = None
        self._nlp_analyzer: Optional[Callable] = None

    def set_nlp_analyzer(self, analyzer: Callable):
        self._nlp_analyzer = analyzer

    async def enqueue(self, post: NormalizedPost):
        await self._queue.put(post)
        self.total_enqueued += 1

    async def enqueue_batch(self, posts: List[NormalizedPost]):
        for p in posts:
            await self._queue.put(p)
            self.total_enqueued += 1

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.started_at = time.time()
        self._worker_task = asyncio.create_task(self._process_loop())
        logger.info("Ingestion worker queue started.")

    async def stop(self):
        self.is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Ingestion worker queue stopped.")

    async def _process_loop(self):
        batch: List[NormalizedPost] = []
        batch_size = 50
        last_flush = time.time()

        while self.is_running:
            try:
                # Fetch next item or timeout to flush
                try:
                    item = await asyncio.wait_for(self._queue.get(), timeout=0.2)
                    batch.append(item)
                    self._queue.task_done()
                except asyncio.TimeoutError:
                    pass

                now = time.time()
                # Flush batch if threshold reached or timed out with items
                if len(batch) >= batch_size or (batch and (now - last_flush) > 0.5):
                    await self._flush_batch(batch)
                    batch.clear()
                    last_flush = now

            except asyncio.CancelledError:
                if batch:
                    await self._flush_batch(batch)
                break
            except Exception as e:
                logger.error(f"Error in ingestion worker loop: {e}", exc_info=True)
                await asyncio.sleep(0.5)

    async def _flush_batch(self, batch: List[NormalizedPost]):
        items_to_insert = []
        for post in batch:
            sentiment = None
            if self._nlp_analyzer:
                sentiment = self._nlp_analyzer(post.text, post.lang)
            items_to_insert.append((post, sentiment))

        PostRepository.insert_posts_batch(items_to_insert)
        self.total_processed += len(batch)

    def get_metrics(self) -> Dict[str, Any]:
        elapsed = time.time() - (self.started_at or time.time())
        rate = round(self.total_processed / elapsed, 2) if elapsed > 0 else 0.0
        return {
            "is_running": self.is_running,
            "queue_size": self._queue.qsize(),
            "total_enqueued": self.total_enqueued,
            "total_processed": self.total_processed,
            "throughput_posts_per_sec": rate,
            "uptime_seconds": round(elapsed, 1) if self.started_at else 0.0
        }

ingestion_queue = IngestionQueue()
