"""Abstract Base Connector for data ingestion."""
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from backend.app.schemas.post import NormalizedPost

class BaseConnector(ABC):
    def __init__(self, name: str, platform: str):
        self.name = name
        self.platform = platform
        self.is_active = False
        self.total_ingested = 0
        self.error_count = 0
        self.last_ingested_at = None

    @abstractmethod
    async def fetch(self, limit: int = 100) -> List[NormalizedPost]:
        """Fetch a batch of posts synchronously/asynchronously."""
        pass

    @abstractmethod
    async def stream(self) -> AsyncIterator[NormalizedPost]:
        """Stream posts in real-time or replay mode."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Return operational health and ingestion metrics."""
        return {
            "connector_name": self.name,
            "platform": self.platform,
            "is_active": self.is_active,
            "total_ingested": self.total_ingested,
            "error_count": self.error_count,
            "last_ingested_at": self.last_ingested_at.isoformat() if self.last_ingested_at else None
        }
