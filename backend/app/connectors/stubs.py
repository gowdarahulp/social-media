"""Connector stubs for Reddit, Instagram, Facebook, and YouTube Comments."""
from typing import Any, AsyncIterator, Dict, List, Optional
from backend.app.connectors.base import BaseConnector
from backend.app.schemas.post import NormalizedPost

class RedditConnectorStub(BaseConnector):
    def __init__(self, client_id: str = "", client_secret: str = ""):
        super().__init__(name="RedditPRAWConnector", platform="reddit")
        self.subreddits = ["technology", "machinelearning", "cryptocurrency", "environment"]

    async def fetch(self, limit: int = 50) -> List[NormalizedPost]:
        return []

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        if False:
            yield

class YouTubeConnectorStub(BaseConnector):
    def __init__(self, api_key: str = ""):
        super().__init__(name="YouTubeCommentsConnector", platform="youtube")

    async def fetch(self, limit: int = 50) -> List[NormalizedPost]:
        return []

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        if False:
            yield

class InstagramConnectorStub(BaseConnector):
    def __init__(self, access_token: str = ""):
        super().__init__(name="InstagramGraphConnector", platform="instagram")

    async def fetch(self, limit: int = 50) -> List[NormalizedPost]:
        return []

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        if False:
            yield

class FacebookConnectorStub(BaseConnector):
    def __init__(self, access_token: str = ""):
        super().__init__(name="FacebookPageConnector", platform="facebook")

    async def fetch(self, limit: int = 50) -> List[NormalizedPost]:
        return []

    async def stream(self) -> AsyncIterator[NormalizedPost]:
        if False:
            yield
