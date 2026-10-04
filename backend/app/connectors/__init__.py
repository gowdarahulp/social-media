"""Connector registry and manager."""
from typing import Dict, List, Optional
from backend.app.connectors.base import BaseConnector
from backend.app.connectors.replay import ReplayConnector
from backend.app.connectors.kaggle import KaggleConnector
from backend.app.connectors.twitter import XConnector
from backend.app.connectors.telegram import TelegramConnector
from backend.app.connectors.stubs import (
    RedditConnectorStub,
    YouTubeConnectorStub,
    InstagramConnectorStub,
    FacebookConnectorStub
)

class ConnectorManager:
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {
            "replay": ReplayConnector(),
            "kaggle": KaggleConnector(),
            "x": XConnector(),
            "telegram": TelegramConnector(),
            "reddit": RedditConnectorStub(),
            "youtube": YouTubeConnectorStub(),
            "instagram": InstagramConnectorStub(),
            "facebook": FacebookConnectorStub()
        }

    def get_connector(self, name: str) -> Optional[BaseConnector]:
        return self.connectors.get(name)

    def get_all_statuses(self) -> List[Dict]:
        return [conn.get_status() for conn in self.connectors.values()]

connector_manager = ConnectorManager()

__all__ = [
    "BaseConnector",
    "ReplayConnector",
    "KaggleConnector",
    "XConnector",
    "TelegramConnector",
    "RedditConnectorStub",
    "YouTubeConnectorStub",
    "InstagramConnectorStub",
    "FacebookConnectorStub",
    "connector_manager"
]
