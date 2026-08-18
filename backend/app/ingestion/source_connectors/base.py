from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseConnector(ABC):
    def __init__(self, source_name: str, source_type: str, authorization_status: str = "AUTHORIZED"):
        self.source_name = source_name
        self.source_type = source_type
        self.authorization_status = authorization_status # AUTHORIZED, NOT_CONFIGURED, REVOKED, RATE_LIMITED, UNAVAILABLE

    @abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetch raw internship listing records from external source API or feed."""
        pass

    @abstractmethod
    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        """Validate presence of minimum required fields in raw record."""
        pass

    @abstractmethod
    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw record to standard ingestion model schema."""
        pass

    def check_authorization(self) -> bool:
        """Check if source connector is authorized to execute."""
        if self.authorization_status == "NOT_CONFIGURED":
            logger.info(f"Connector '{self.source_name}' skipped: Authorization status is NOT_CONFIGURED (Stub Mode).")
            return False
        elif self.authorization_status == "REVOKED":
            logger.warning(f"Connector '{self.source_name}' disabled: Authorization status is REVOKED.")
            return False
        elif self.authorization_status in ("RATE_LIMITED", "UNAVAILABLE"):
            logger.warning(f"Connector '{self.source_name}' deferred: Status is {self.authorization_status}.")
            return False
        return True
