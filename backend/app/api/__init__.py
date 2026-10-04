"""API router aggregation."""
from fastapi import APIRouter
from .routes_ingest import router as ingest_router
from .routes_posts import router as posts_router
from .routes_sentiment import router as sentiment_router
from .routes_demographics import router as demographics_router
from .routes_trends import router as trends_router
from .routes_network import router as network_router
from .routes_analyze import router as analyze_router

api_router = APIRouter()
api_router.include_router(ingest_router)
api_router.include_router(posts_router)
api_router.include_router(sentiment_router)
api_router.include_router(demographics_router)
api_router.include_router(trends_router)
api_router.include_router(network_router)
api_router.include_router(analyze_router)

__all__ = ["api_router"]
