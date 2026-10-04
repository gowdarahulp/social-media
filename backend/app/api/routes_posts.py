"""API routes for exploring normalized posts and conversation threads."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.db.repository import PostRepository

router = APIRouter(prefix="/api/posts", tags=["Posts & Threads"])

@router.get("")
def list_posts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    topic: Optional[str] = Query(default=None, description="Filter by topic keyword or hashtag"),
    emotion: Optional[str] = Query(default=None, description="Filter by dominant emotion classification"),
    platform: Optional[str] = Query(default=None, description="Filter by platform: x, telegram, reddit, etc."),
    from_date: Optional[datetime] = Query(default=None, alias="from"),
    to_date: Optional[datetime] = Query(default=None, alias="to")
) -> List[Dict[str, Any]]:
    return PostRepository.get_posts(
        limit=limit,
        offset=offset,
        topic=topic,
        emotion=emotion,
        platform=platform,
        start_time=from_date,
        end_time=to_date
    )

@router.get("/{post_id}")
def get_single_post(post_id: str) -> Dict[str, Any]:
    post = PostRepository.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post '{post_id}' not found.")
    return post

@router.get("/{post_id}/thread")
def get_post_thread(post_id: str) -> Dict[str, Any]:
    thread = PostRepository.get_thread(post_id)
    if not thread["root"]:
        raise HTTPException(status_code=404, detail=f"Thread for post '{post_id}' not found.")
    return thread
