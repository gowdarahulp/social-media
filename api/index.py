"""
Vercel serverless entry point for the Social Media Analytics Framework.
Wraps the FastAPI app for Vercel's @vercel/python runtime.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Override DATABASE_PATH to /tmp (writable on Vercel serverless)
os.environ.setdefault("DATABASE_PATH", "/tmp/social_pulse.db")
os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/social_pulse.db")
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("REPLAY_DATASET_PATH", str(project_root / "backend" / "app" / "data" / "sample_dataset.jsonl"))

# Import the FastAPI app (this triggers startup/lifespan)
from backend.app.main import app

# Vercel expects the ASGI app exposed as 'app'
