from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ProviderResultStatus(str, Enum):
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_PERMITTED = "NOT_PERMITTED"
    ERROR = "ERROR"

class ProviderResult(BaseModel):
    status: ProviderResultStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str

class LeetCodeDataProvider(ABC):
    """
    Abstract interface for LeetCode data access.
    Enforces strict provider abstraction, pluggability, and safety rules.
    Prevents unauthorized web scraping, private endpoint reverse engineering, or mock data fabrication.
    """

    @abstractmethod
    async def check_profile_exists(self, username: str) -> ProviderResult:
        """
        Checks whether a LeetCode profile username legitimately exists.
        Returns ProviderResult with status SUCCESS, NOT_FOUND, UNAVAILABLE, NOT_PERMITTED, or ERROR.
        """
        pass

    @abstractmethod
    async def get_profile_data(self, username: str) -> ProviderResult:
        """
        Retrieves permitted public LeetCode profile metadata (e.g. public bio, handle).
        Returns ProviderResult with status SUCCESS, NOT_FOUND, UNAVAILABLE, NOT_PERMITTED, or ERROR.
        """
        pass

    @abstractmethod
    async def get_profile_statistics(self, username: str) -> ProviderResult:
        """
        Retrieves permitted public problem-solving statistics (e.g. solved counts, topic tags).
        Returns ProviderResult with status SUCCESS, NOT_FOUND, UNAVAILABLE, NOT_PERMITTED, or ERROR.
        """
        pass

    @abstractmethod
    async def get_provider_status(self) -> Dict[str, Any]:
        """
        Reports operational health status, configuration status, and provider capabilities.
        """
        pass

class UnconfiguredLeetCodeProvider(LeetCodeDataProvider):
    """
    Default safe provider returned when no authorized/permitted API provider is configured.
    Strictly returns UNAVAILABLE status and never fabricates mock or placeholder data.
    """

    def __init__(self, reason: str = "No authorized LeetCode API provider configured."):
        self.reason = reason

    async def check_profile_exists(self, username: str) -> ProviderResult:
        return ProviderResult(
            status=ProviderResultStatus.UNAVAILABLE,
            message=self.reason,
            data=None,
            error=self.reason,
            timestamp=datetime.utcnow().isoformat()
        )

    async def get_profile_data(self, username: str) -> ProviderResult:
        return ProviderResult(
            status=ProviderResultStatus.UNAVAILABLE,
            message=self.reason,
            data=None,
            error=self.reason,
            timestamp=datetime.utcnow().isoformat()
        )

    async def get_profile_statistics(self, username: str) -> ProviderResult:
        return ProviderResult(
            status=ProviderResultStatus.UNAVAILABLE,
            message=self.reason,
            data=None,
            error=self.reason,
            timestamp=datetime.utcnow().isoformat()
        )

    async def get_provider_status(self) -> Dict[str, Any]:
        return {
            "provider_name": "UnconfiguredLeetCodeProvider",
            "is_configured": False,
            "is_permitted": False,
            "status": "UNAVAILABLE",
            "message": self.reason,
            "timestamp": datetime.utcnow().isoformat()
        }

class LeetCodeProviderRegistry:
    """
    Registry manager for configuring and retrieving the active LeetCodeDataProvider instance.
    Defaults to UnconfiguredLeetCodeProvider for safety until configured.
    """
    _instance: Optional[LeetCodeDataProvider] = None

    @classmethod
    def get_provider(cls) -> LeetCodeDataProvider:
        if cls._instance is None:
            cls._instance = UnconfiguredLeetCodeProvider()
        return cls._instance

    @classmethod
    def set_provider(cls, provider: LeetCodeDataProvider) -> None:
        cls._instance = provider

    @classmethod
    def reset(cls) -> None:
        cls._instance = UnconfiguredLeetCodeProvider()
