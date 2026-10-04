"""Application configuration and settings."""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "Social Media Analytics Framework"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Security & Privacy
    HASH_SALT: str = Field(default="social-pulse-secret-salt-2026", description="Salt used for deterministic SHA-256 user anonymization")
    K_ANONYMITY_THRESHOLD: int = Field(default=20, description="Minimum cohort size for reporting demographics")
    
    # Storage
    DATABASE_PATH: str = "social_pulse.db"
    DATABASE_URL: str = "sqlite:///./social_pulse.db"
    
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
