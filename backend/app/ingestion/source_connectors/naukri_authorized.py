from typing import List, Dict, Any
from app.ingestion.source_connectors.base import BaseConnector
from app.core.config import settings

class NaukriAuthorizedConnector(BaseConnector):
    """
    Naukri Authorized Connector Stub (Google Antigravity Spec Specification).
    Defaults to NOT_CONFIGURED. Activates ONLY when official API key is provided.
    Strictly prohibits unauthorized scraping or anti-bot circumvention.
    """
    def __init__(self):
        auth_status = "AUTHORIZED" if settings.NAUKRI_API_KEY else "NOT_CONFIGURED"
        super().__init__(
            source_name="Naukri Authorized API Connector",
            source_type="AUTHORIZED_API",
            authorization_status=auth_status
        )

    async def fetch(self) -> List[Dict[str, Any]]:
        if not self.check_authorization():
            return []
        return []

    def validate_raw(self, raw_record: Dict[str, Any]) -> bool:
        return bool(raw_record.get("company_name") and raw_record.get("title"))

    def normalize(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        return raw_record
