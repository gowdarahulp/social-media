"""Application configuration and settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# On Vercel (and other serverless), only /tmp is writable
_IS_SERVERLESS = os.environ.get("VERCEL") or os.environ.get("ENVIRONMENT") == "production"
_DEFAULT_DB_PATH = "/tmp/social_pulse.db" if _IS_SERVERLESS else "social_pulse.db"
_DEFAULT_DB_URL = f"sqlite:///{_DEFAULT_DB_PATH}"

class Settings(BaseSettings):
    APP_NAME: str = "Social Media Analytics Framework"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Security & Privacy
    HASH_SALT: str = Field(default="social-pulse-secret-salt-2026", description="Salt used for deterministic SHA-256 user anonymization")
    K_ANONYMITY_THRESHOLD: int = Field(default=20, description="Minimum cohort size for reporting demographics")
    
    # Storage - auto-detect writable path
    DATABASE_PATH: str = Field(default=_DEFAULT_DB_PATH)
    DATABASE_URL: str = Field(default=_DEFAULT_DB_URL)
    
    # Ingestion & Connectors
    REPLAY_DATASET_PATH: str = "backend/app/data/sample_dataset.jsonl"
    REPLAY_SPEED_MULTIPLIER: float = 1.0
    
    # External APIs (Optional - defaults to mock/replay if absent)
    TWITTER_BEARER_TOKEN: str = ""
    TELEGRAM_API_ID: str = ""
    TELEGRAM_API_HASH: str = ""
    TELEGRAM_PHONE: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
