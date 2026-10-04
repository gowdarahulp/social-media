"""API routes for ingestion management, mock replay, and Kaggle dataset loading."""
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Query, UploadFile
from typing import Any, Dict, Optional
from backend.app.connectors import connector_manager, ReplayConnector, KaggleConnector
from backend.app.queue.worker import ingestion_queue
from backend.app.db.repository import PostRepository
from backend.app.nlp.sentiment_analyzer import sentiment_engine

router = APIRouter(prefix="/api/ingest", tags=["Ingestion & Connectors"])

@router.get("/status")
def get_ingestion_status() -> Dict[str, Any]:
    stats = PostRepository.get_total_stats()
    queue_metrics = ingestion_queue.get_metrics()
    connector_statuses = connector_manager.get_all_statuses()
    return {
        "status": "operational",
        "database": stats,
        "worker_queue": queue_metrics,
        "connectors": connector_statuses
    }

async def _run_replay_task(limit: int, reset_db: bool):
    if reset_db:
        PostRepository.clear_all()
    replay: Optional[ReplayConnector] = connector_manager.get_connector("replay") # type: ignore
    if replay:
        if reset_db:
            replay.reset()
        batch = await replay.fetch(limit=limit)
        items_to_save = []
        for post in batch:
            sent = sentiment_engine.analyze(post.text, target_topic=post.topics[0] if post.topics else None)
            items_to_save.append((post, sent))
        PostRepository.insert_posts_batch(items_to_save)

@router.post("/replay")
async def trigger_replay(
    background_tasks: BackgroundTasks,
    limit: int = Query(default=380, ge=1, le=1000, description="Number of posts to ingest"),
    reset_db: bool = Query(default=False, description="Whether to clear existing DB data before replay")
):
    await _run_replay_task(limit=limit, reset_db=reset_db)
    stats = PostRepository.get_total_stats()
    return {
        "message": f"Successfully ingested {limit} posts via ReplayConnector.",
        "current_database_stats": stats
    }

@router.post("/kaggle")
async def trigger_kaggle_ingest(
    limit: int = Query(default=500, ge=1, le=2000, description="Number of Kaggle posts to ingest"),
    reset_db: bool = Query(default=True, description="Whether to reset database before loading Kaggle benchmark")
):
    """Loads Kaggle social media benchmark dataset with NLP analysis and updates all 4 intelligence pillars."""
    if reset_db:
        PostRepository.clear_all()
    
    kaggle: Optional[KaggleConnector] = connector_manager.get_connector("kaggle") # type: ignore
    if not kaggle:
        raise HTTPException(status_code=500, detail="KaggleConnector not initialized")

    if reset_db:
        kaggle.reset()

    batch = await kaggle.fetch(limit=limit)
    items_to_save = []
    for post in batch:
        primary_topic = post.topics[0] if post.topics else None
        sent = sentiment_engine.analyze(post.text, target_topic=primary_topic)
        items_to_save.append((post, sent))

    PostRepository.insert_posts_batch(items_to_save)
    stats = PostRepository.get_total_stats()

    return {
        "message": f"Successfully ingested {len(items_to_save)} posts from Kaggle benchmark dataset.",
        "dataset_name": "kaggle_social_dataset.csv",
        "current_database_stats": stats
    }

@router.post("/kaggle/upload")
async def upload_kaggle_csv(
    file: UploadFile = File(..., description="Kaggle CSV file to upload and analyze"),
    reset_db: bool = Query(default=False, description="Whether to clear DB before ingesting uploaded CSV")
):
    """Upload custom Kaggle CSV, auto-detect columns, analyze with NLP engine, and persist to DB."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv file")

    content_bytes = await file.read()
    try:
        csv_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        csv_text = content_bytes.decode("latin-1", errors="replace")

    posts = KaggleConnector.parse_csv_content(csv_text)
    if not posts:
        raise HTTPException(status_code=400, detail="No valid post records could be parsed from uploaded CSV")

    if reset_db:
        PostRepository.clear_all()

    items_to_save = []
    for post in posts:
        primary_topic = post.topics[0] if post.topics else None
        sent = sentiment_engine.analyze(post.text, target_topic=primary_topic)
        items_to_save.append((post, sent))

    PostRepository.insert_posts_batch(items_to_save)
    stats = PostRepository.get_total_stats()

    return {
        "message": f"Successfully parsed and ingested {len(posts)} posts from uploaded Kaggle dataset '{file.filename}'.",
        "filename": file.filename,
        "posts_ingested": len(posts),
        "current_database_stats": stats
    }
