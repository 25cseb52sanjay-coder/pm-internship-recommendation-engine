from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseSearchProvider(ABC):
    def __init__(self, provider_name: str, daily_quota: int = 1000):
        self.provider_name = provider_name
        self.daily_quota = daily_quota
        self.used_quota = 0

    @abstractmethod
    async def execute_search(self, query_text: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Executes authorized web search query and returns candidate URLs and snippets."""
        pass

    def check_quota(self) -> bool:
        if self.used_quota >= self.daily_quota:
            logger.warning(f"Search Provider '{self.provider_name}' daily quota ({self.daily_quota}) exhausted.")
            return False
        return True

    def increment_quota_use(self, count: int = 1):
        self.used_quota += count
