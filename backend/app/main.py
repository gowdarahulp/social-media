"""Main FastAPI application entry point with lifespan management and static dashboard hosting."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from backend.app.config import settings
from backend.app.api import api_router
from backend.app.queue.worker import ingestion_queue
from backend.app.db.repository import PostRepository
from backend.app.connectors import connector_manager, ReplayConnector
from backend.app.nlp.sentiment_analyzer import sentiment_engine

# Resolve paths relative to this file's location (works on both local + Vercel)
BASE_DIR = Path(__file__).parent.parent.parent  # project root

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start worker queue
    ingestion_queue.set_nlp_analyzer(sentiment_engine.analyze)
    await ingestion_queue.start()

    # Auto-seed database if empty for instant out-of-the-box demo
    stats = PostRepository.get_total_stats()
    if stats["total_posts"] == 0:
        print("[Startup] Database is empty. Auto-seeding initial dataset from ReplayConnector...")
        replay: ReplayConnector = connector_manager.get_connector("replay") # type: ignore
        if replay:
            batch = await replay.fetch(limit=380)
            items_to_save = []
            for post in batch:
                sent = sentiment_engine.analyze(post.text, target_topic=post.topics[0] if post.topics else None)
                items_to_save.append((post, sent))
            PostRepository.insert_posts_batch(items_to_save)
            print(f"[Startup] Auto-seeded {len(items_to_save)} posts. Ready for demo.")

    yield
    # Shutdown
    await ingestion_queue.stop()

app = FastAPI(
    title="Social Media Analytics Framework (Audience Intelligence Platform)",
    description="Full-stack AI-driven audience intelligence engine with multi-dimensional sentiment, aggregate demographics with k-anonymity, rising trend forecasting, and influence network cascades.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API endpoints
app.include_router(api_router)

def get_dashboard_html() -> str:
    """Bulletproof loader for dashboard HTML across local dev and Vercel serverless."""
    candidates = [
        Path(__file__).parent / "index.html",
        BASE_DIR / "frontend" / "public" / "index.html",
        BASE_DIR / "api" / "index.html",
        BASE_DIR / "backend" / "app" / "index.html",
        Path("frontend/public/index.html"),
        Path("backend/app/index.html"),
        Path("api/index.html"),
        Path("index.html")
    ]
    for p in candidates:
        if p.exists():
            try:
                return p.read_text(encoding="utf-8")
            except Exception:
                continue
    return "<h1>SocialPulse API running. Visit <a href='/docs'>/docs</a></h1>"

# Mount frontend static directory if exists
frontend_public = BASE_DIR / "frontend" / "public"
if frontend_public.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_public)), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index():
    return HTMLResponse(content=get_dashboard_html(), status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

